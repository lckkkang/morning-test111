 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/main.py b/main.py
index 2847dc67a2d3c66c45f7147e2c46eea7d1d5fa99..69c4378751b7c3b00ac03ceb69afab7b56278b30 100644
--- a/main.py
+++ b/main.py
@@ -1,83 +1,254 @@
-import requests
-from datetime import datetime
-import os
 import base64
 import hashlib
-from playwright.sync_api import sync_playwright
+import html
+import os
+from datetime import date, datetime
+from importlib.util import find_spec
+from pathlib import Path
+from zoneinfo import ZoneInfo
 import xml.etree.ElementTree as ET
 
+
 WEBHOOK = os.getenv("WEBHOOK")
+CHINA_TZ = ZoneInfo("Asia/Shanghai")
+BASE_DIR = Path(__file__).resolve().parent
+HTML_PATH = BASE_DIR / "temp.html"
+IMAGE_PATH = BASE_DIR / "out.png"
+NEWS_URL = "https://news.google.com/rss/search?q=财经&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
+DEFAULT_NEWS = "暂无财经要闻"
+NEWS_FETCH_FAILED = "新闻获取失败"
+LUNAR_BASE_DATE = date(1900, 1, 31)
+LUNAR_INFO = (
+    0x04BD8, 0x04AE0, 0x0A570, 0x054D5, 0x0D260, 0x0D950, 0x16554, 0x056A0,
+    0x09AD0, 0x055D2, 0x04AE0, 0x0A5B6, 0x0A4D0, 0x0D250, 0x1D255, 0x0B540,
+    0x0D6A0, 0x0ADA2, 0x095B0, 0x14977, 0x04970, 0x0A4B0, 0x0B4B5, 0x06A50,
+    0x06D40, 0x1AB54, 0x02B60, 0x09570, 0x052F2, 0x04970, 0x06566, 0x0D4A0,
+    0x0EA50, 0x06E95, 0x05AD0, 0x02B60, 0x186E3, 0x092E0, 0x1C8D7, 0x0C950,
+    0x0D4A0, 0x1D8A6, 0x0B550, 0x056A0, 0x1A5B4, 0x025D0, 0x092D0, 0x0D2B2,
+    0x0A950, 0x0B557, 0x06CA0, 0x0B550, 0x15355, 0x04DA0, 0x0A5D0, 0x14573,
+    0x052D0, 0x0A9A8, 0x0E950, 0x06AA0, 0x0AEA6, 0x0AB50, 0x04B60, 0x0AAE4,
+    0x0A570, 0x05260, 0x0F263, 0x0D950, 0x05B57, 0x056A0, 0x096D0, 0x04DD5,
+    0x04AD0, 0x0A4D0, 0x0D4D4, 0x0D250, 0x0D558, 0x0B540, 0x0B6A0, 0x195A6,
+    0x095B0, 0x049B0, 0x0A974, 0x0A4B0, 0x0B27A, 0x06A50, 0x06D40, 0x0AF46,
+    0x0AB60, 0x09570, 0x04AF5, 0x04970, 0x064B0, 0x074A3, 0x0EA50, 0x06B58,
+    0x055C0, 0x0AB60, 0x096D5, 0x092E0, 0x0C960, 0x0D954, 0x0D4A0, 0x0DA50,
+    0x07552, 0x056A0, 0x0ABB7, 0x025D0, 0x092D0, 0x0CAB5, 0x0A950, 0x0B4A0,
+    0x0BAA4, 0x0AD50, 0x055D9, 0x04BA0, 0x0A5B0, 0x15176, 0x052B0, 0x0A930,
+    0x07954, 0x06AA0, 0x0AD50, 0x05B52, 0x04B60, 0x0A6E6, 0x0A4E0, 0x0D260,
+    0x0EA65, 0x0D530, 0x05AA0, 0x076A3, 0x096D0, 0x04BD7, 0x04AD0, 0x0A4D0,
+    0x1D0B6, 0x0D250, 0x0D520, 0x0DD45, 0x0B5A0, 0x056D0, 0x055B2, 0x049B0,
+    0x0A577, 0x0A4B0, 0x0AA50, 0x1B255, 0x06D20, 0x0ADA0, 0x14B63,
+)
+LUNAR_MONTH_NAMES = ("正", "二", "三", "四", "五", "六", "七", "八", "九", "十", "冬", "腊")
+LUNAR_DAY_PREFIXES = ("初", "十", "廿", "卅")
+LUNAR_DAY_NAMES = ("一", "二", "三", "四", "五", "六", "七", "八", "九", "十")
+ZODIACS = ("鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪")
+HEAVENLY_STEMS = ("甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸")
+EARTHLY_BRANCHES = ("子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥")
+YI_ACTIONS = (
+    "祭祀", "祈福", "求嗣", "嫁娶", "纳采", "开市", "交易", "签约",
+    "出行", "搬家", "入宅", "安床", "修造", "动土", "栽种", "纳财",
+)
+JI_ACTIONS = (
+    "开光", "掘井", "开仓", "安葬", "破土", "伐木", "远行", "诉讼",
+    "置产", "作灶", "移徙", "嫁娶", "开市", "动土", "安床", "纳畜",
+)
 
 
 # ===== 新闻（去来源 + 去重）=====
-def get_news():
+def get_news(limit=3):
+    """Fetch finance news titles from Google News RSS."""
+    if find_spec("requests") is None:
+        return [NEWS_FETCH_FAILED] * limit
+
+    import requests
+
     try:
-        url = "https://news.google.com/rss/search?q=财经&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
-        res = requests.get(url, timeout=10)
+        res = requests.get(NEWS_URL, timeout=10)
+        res.raise_for_status()
         res.encoding = "utf-8"
 
         root = ET.fromstring(res.text)
-
         news = []
         seen = set()
 
         for item in root.findall(".//item"):
-            title = item.find("title").text.strip()
+            title_node = item.find("title")
+            if title_node is None or not title_node.text:
+                continue
+
+            title = title_node.text.strip()
 
             # 去掉来源（- xxx）
             if " - " in title:
-                title = title.split(" - ")[0]
+                title = title.rsplit(" - ", 1)[0]
 
-            if title not in seen:
+            if title and title not in seen:
                 seen.add(title)
                 news.append(title)
 
-            if len(news) >= 3:
+            if len(news) >= limit:
                 break
 
-        while len(news) < 3:
-            news.append("暂无财经要闻")
+        while len(news) < limit:
+            news.append(DEFAULT_NEWS)
 
         return news
 
-    except:
-        return ["新闻获取失败"] * 3
+    except (requests.RequestException, ET.ParseError):
+        return [NEWS_FETCH_FAILED] * limit
+
+
+def escape_news(news):
+    """Escape news text before inserting it into the HTML template."""
+    return [html.escape(title, quote=True) for title in news]
+
+
+# ===== 农历 / 黄历 =====
+def get_lunar_year_days(year):
+    info = LUNAR_INFO[year - 1900]
+    days = 348
+    for month_index in range(12):
+        if info & (0x8000 >> month_index):
+            days += 1
+    return days + get_lunar_leap_days(year)
+
+
+def get_lunar_leap_month(year):
+    return LUNAR_INFO[year - 1900] & 0xF
+
+
+def get_lunar_leap_days(year):
+    if get_lunar_leap_month(year):
+        return 30 if LUNAR_INFO[year - 1900] & 0x10000 else 29
+    return 0
+
+
+def get_lunar_month_days(year, month):
+    return 30 if LUNAR_INFO[year - 1900] & (0x10000 >> month) else 29
+
+
+def solar_to_lunar(solar_date):
+    """Convert a Gregorian date to a Chinese lunar date from 1900 through 2050."""
+    max_year = 1900 + len(LUNAR_INFO) - 1
+    if not date(1900, 1, 31) <= solar_date <= date(max_year, 12, 31):
+        raise ValueError(f"solar_date must be between 1900-01-31 and {max_year}-12-31")
+
+    offset = (solar_date - LUNAR_BASE_DATE).days
+    lunar_year = 1900
+
+    while lunar_year <= max_year:
+        year_days = get_lunar_year_days(lunar_year)
+        if offset < year_days:
+            break
+        offset -= year_days
+        lunar_year += 1
+
+    leap_month = get_lunar_leap_month(lunar_year)
+    lunar_month = 1
+    is_leap = False
+
+    while lunar_month <= 12:
+        if leap_month == lunar_month and not is_leap:
+            month_days = get_lunar_leap_days(lunar_year)
+            is_leap = True
+        else:
+            month_days = get_lunar_month_days(lunar_year, lunar_month)
+
+        if offset < month_days:
+            break
+
+        offset -= month_days
+        if is_leap and leap_month == lunar_month:
+            is_leap = False
+        else:
+            lunar_month += 1
+
+    return {
+        "year": lunar_year,
+        "month": lunar_month,
+        "day": offset + 1,
+        "is_leap": is_leap,
+    }
+
+
+def format_lunar_day(day):
+    if day == 10:
+        return "初十"
+    if day == 20:
+        return "二十"
+    if day == 30:
+        return "三十"
+    return LUNAR_DAY_PREFIXES[(day - 1) // 10] + LUNAR_DAY_NAMES[(day - 1) % 10]
+
+
+def format_lunar_date(lunar_date):
+    year = lunar_date["year"]
+    stem_branch = HEAVENLY_STEMS[(year - 4) % 10] + EARTHLY_BRANCHES[(year - 4) % 12]
+    zodiac = ZODIACS[(year - 4) % 12]
+    leap = "闰" if lunar_date["is_leap"] else ""
+    month = LUNAR_MONTH_NAMES[lunar_date["month"] - 1]
+    day = format_lunar_day(lunar_date["day"])
+    return f"农历：{stem_branch}{zodiac}年 {leap}{month}月{day}"
+
+
+def pick_lunar_actions(actions, seed, count=3):
+    return [actions[(seed + index * 5) % len(actions)] for index in range(count)]
+
+
+def get_huangli(current_datetime=None):
+    """Build a daily Chinese lunar-calendar almanac summary."""
+    current_datetime = current_datetime or datetime.now(CHINA_TZ)
+    china_date = current_datetime.astimezone(CHINA_TZ).date()
+    lunar_date = solar_to_lunar(china_date)
+    seed = (
+        lunar_date["year"] * 17
+        + lunar_date["month"] * 31
+        + lunar_date["day"] * 43
+        + (7 if lunar_date["is_leap"] else 0)
+    )
+
+    return {
+        "lunar": format_lunar_date(lunar_date),
+        "yi": " ".join(pick_lunar_actions(YI_ACTIONS, seed)),
+        "ji": " ".join(pick_lunar_actions(JI_ACTIONS, seed + 9)),
+    }
 
 
 # ===== UI =====
-def make_html(news):
-    now = datetime.now()
+def make_html(news, output_path=HTML_PATH):
+    now = datetime.now(CHINA_TZ)
 
     year = now.strftime("%Y")
     date_big = now.strftime("%m.%d")
-    weekday = ["MON","TUE","WED","THU","FRI","SAT","SUN"][now.weekday()]
+    weekday = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"][now.weekday()]
 
-    yi = "嫁娶 祭祀 祈福"
-    ji = "开光 掘井 开仓"
+    huangli = get_huangli(now)
+    safe_news = escape_news(news)
 
-    html = f"""
+    html_content = f"""
     <html>
     <head>
     <meta charset="utf-8">
     <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700;900&display=swap" rel="stylesheet">
     </head>
 
     <body style="
         margin:0;
         width:750px;
         height:1334px;
         font-family:'Noto Sans SC';
         background:linear-gradient(180deg,#f4f6f9,#e8edf2);
     ">
 
     <!-- LOGO -->
     <div style="position:absolute;top:40px;left:42px;">
         <div style="font-size:30px;font-weight:700;">通途控股</div>
         <div style="font-size:14px;color:#888;margin-top:4px;">TONGTU HOLDINGS</div>
     </div>
 
     <!-- 背景大字 -->
     <div style="
         position:absolute;
         top:130px;
         left:40px;
@@ -90,148 +261,175 @@ def make_html(news):
     </div>
 
     <!-- 主标题（上移） -->
     <div style="
         position:absolute;
         top:230px;
         left:40px;
         font-size:92px;
         font-weight:900;
     ">
         <span style="color:#5b6f7c;">通途</span>
         <span style="color:#c8a060;margin-left:8px;">早安</span>
     </div>
 
     <!-- 日期（上移） -->
     <div style="
         position:absolute;
         top:200px;
         right:48px;
         text-align:right;
     ">
         <div style="font-size:24px;color:#666;">{year}</div>
         <div style="font-size:84px;font-weight:900;line-height:1;">{date_big}</div>
         <div style="font-size:20px;color:#999;margin-top:2px;">{weekday}</div>
 
-        <!-- 黄历（更紧凑） -->
+        <!-- 黄历（按中国农历日期每日更新） -->
         <div style="margin-top:10px;font-size:20px;line-height:1.5;">
-            <span style="color:#1fa463;">宜：{yi}</span><br>
-            <span style="color:#e05a5a;">忌：{ji}</span>
+            <span style="color:#666;">{huangli["lunar"]}</span><br>
+            <span style="color:#1fa463;">宜：{huangli["yi"]}</span><br>
+            <span style="color:#e05a5a;">忌：{huangli["ji"]}</span>
         </div>
     </div>
 
     <!-- 卡片 -->
     <div style="
         position:absolute;
         top:420px;
         left:30px;
         width:690px;
         background:#f6f7f9;
         border-radius:34px;
         padding:32px;
     ">
 
         <!-- 标题 -->
         <div style="
             background:#6f8796;
             color:#fff;
             display:inline-block;
             padding:10px 30px;
             border-radius:20px;
             font-size:24px;
             margin-bottom:24px;
         ">
             每日资讯
         </div>
 
         <!-- 内容 -->
         <div style="
             font-size:26px;
             color:#333;
             line-height:1.65;
         ">
-            <p style="margin:0 0 18px 0;">{news[0]}</p>
+            <p style="margin:0 0 18px 0;">{safe_news[0]}</p>
 
             <div style="border-top:1px dashed #dcdcdc;margin:16px 0;"></div>
 
-            <p style="margin:0 0 18px 0;">{news[1]}</p>
+            <p style="margin:0 0 18px 0;">{safe_news[1]}</p>
 
             <div style="border-top:1px dashed #dcdcdc;margin:16px 0;"></div>
 
-            <p style="margin:0;">{news[2]}</p>
+            <p style="margin:0;">{safe_news[2]}</p>
         </div>
 
     </div>
 
     <!-- 底部 -->
     <div style="
         position:absolute;
         bottom:90px;
         left:40px;
     ">
 
         <div style="font-size:34px;color:#5c7a8a;font-weight:700;">
             人民币最新存款利率
         </div>
 
         <div style="margin-top:16px;font-size:30px;">
             活期存款：<span style="color:#c9a063;">0.05%</span>
         </div>
 
         <div style="margin-top:6px;font-size:30px;">
             一年定期：<span style="color:#c9a063;">0.95%</span>
         </div>
 
         <div style="margin-top:34px;font-size:34px;color:#5c7a8a;font-weight:700;">
             天弘余额宝最新七日年化
         </div>
 
         <div style="margin-top:10px;font-size:48px;color:#c9a063;font-weight:900;">
             1.0000%
         </div>
 
     </div>
 
     </body>
     </html>
     """
 
-    with open("temp.html", "w", encoding="utf-8") as f:
-        f.write(html)
+    output_path = Path(output_path)
+    output_path.write_text(html_content, encoding="utf-8")
+    return output_path
 
 
 # ===== 截图 =====
-def screenshot():
+def screenshot(html_path=HTML_PATH, image_path=IMAGE_PATH):
+    html_path = Path(html_path).resolve()
+    image_path = Path(image_path).resolve()
+
+    if find_spec("playwright") is None:
+        raise RuntimeError("playwright package is required to capture screenshots")
+
+    from playwright.sync_api import sync_playwright
+
     with sync_playwright() as p:
         browser = p.chromium.launch(args=["--no-sandbox"])
         page = browser.new_page(
-            viewport={"width":750,"height":1334},
-            device_scale_factor=2
+            viewport={"width": 750, "height": 1334},
+            device_scale_factor=2,
         )
-        page.goto("file://" + os.getcwd() + "/temp.html")
-        page.screenshot(path="out.png")
+        page.goto(html_path.as_uri())
+        page.screenshot(path=str(image_path))
         browser.close()
 
+    return image_path
+
 
 # ===== 发送 =====
-def send():
-    img = open("out.png","rb").read()
+def send(image_path=IMAGE_PATH):
+    if not WEBHOOK:
+        raise RuntimeError("WEBHOOK environment variable is required")
+
+    if find_spec("requests") is None:
+        raise RuntimeError("requests package is required to send webhook images")
+
+    import requests
+
+    image_path = Path(image_path)
+    img = image_path.read_bytes()
 
-    requests.post(WEBHOOK, json={
-        "msgtype":"image",
-        "image":{
-            "base64": base64.b64encode(img).decode(),
-            "md5": hashlib.md5(img).hexdigest()
-        }
-    })
+    response = requests.post(
+        WEBHOOK,
+        json={
+            "msgtype": "image",
+            "image": {
+                "base64": base64.b64encode(img).decode(),
+                "md5": hashlib.md5(img).hexdigest(),
+            },
+        },
+        timeout=10,
+    )
+    response.raise_for_status()
+    return response
 
 
 # ===== 主流程 =====
 def main():
     news = get_news()
-    make_html(news)
-    screenshot()
-    send()
+    html_path = make_html(news)
+    image_path = screenshot(html_path)
+    send(image_path)
 
 
 if __name__ == "__main__":
     main()
 
EOF
)
