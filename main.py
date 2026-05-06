import requests
from datetime import datetime
import os
import base64
import hashlib
from playwright.sync_api import sync_playwright
import xml.etree.ElementTree as ET

WEBHOOK = os.getenv("WEBHOOK")

# ===== 新闻（稳定）=====
def get_news():
    try:
        url = "https://news.google.com/rss/search?q=财经&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
        res = requests.get(url, timeout=10)
        res.encoding = "utf-8"

        root = ET.fromstring(res.text)

        news = []
        for item in root.findall(".//item")[:5]:
            news.append(item.find("title").text)

        return news if news else ["暂无财经新闻"]

    except Exception as e:
        return ["新闻获取失败"]


# ===== 生成HTML（复刻版）=====
def make_html(news):
    now = datetime.now()
    date_str = now.strftime("%Y.%m.%d")
    weekday = ["MON","TUE","WED","THU","FRI","SAT","SUN"][now.weekday()]

    yi = "嫁娶 祭祀 祈福"
    ji = "开光 掘井 开仓"

    rate1 = "0.05%"
    rate2 = "0.95%"
    yuebao = "1.0000%"

    html = f"""
    <html>
    <head>
    <meta charset="utf-8">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;600;700&display=swap" rel="stylesheet">
    </head>

    <body style="
        margin:0;
        width:750px;
        height:1334px;
        font-family:'Noto Sans SC';
        background:linear-gradient(#f4f6f9,#e6edf3);
    ">

    <!-- 顶部 -->
    <div style="padding:40px;">

        <div style="font-size:22px;color:#999;">
            TONGTU HOLDINGS
        </div>

        <div style="
            font-size:120px;
            font-weight:700;
            color:#d8dee6;
            margin-top:10px;
        ">
            TONGTU
        </div>

        <div style="
            font-size:80px;
            font-weight:700;
            margin-top:-40px;
        ">
            <span style="color:#5c6f7c;">通途</span>
            <span style="color:#c9a063;">早安</span>
        </div>

    </div>

    <!-- 右侧日期 -->
    <div style="
        position:absolute;
        top:80px;
        right:40px;
        text-align:right;
    ">
        <div style="font-size:28px;color:#333;">{date_str}</div>
        <div style="font-size:22px;color:#888;margin-top:5px;">{weekday}</div>

        <div style="margin-top:20px;font-size:22px;line-height:1.6;">
            <span style="color:#16a34a;">宜：{yi}</span><br>
            <span style="color:#dc2626;">忌：{ji}</span>
        </div>
    </div>

    <!-- 新闻卡片 -->
    <div style="
        margin:20px 30px;
        background:#ffffff;
        border-radius:30px;
        padding:30px;
        box-shadow:0 10px 40px rgba(0,0,0,0.08);
    ">

        <div style="
            font-size:32px;
            font-weight:700;
            color:#5c7a8a;
            margin-bottom:20px;
        ">
            每日资讯
        </div>

        <div style="font-size:26px;line-height:1.8;color:#333;">
            {''.join([f'<p style="margin-bottom:20px;">{n}</p>' for n in news])}
        </div>

    </div>

    <!-- 利率 -->
    <div style="padding:40px;">

        <div style="font-size:30px;color:#5c7a8a;font-weight:700;">
            人民币最新存款利率
        </div>

        <div style="margin-top:20px;font-size:28px;">
            活期存款：<span style="color:#c9a063;">{rate1}</span>
        </div>

        <div style="margin-top:10px;font-size:28px;">
            一年定期：<span style="color:#c9a063;">{rate2}</span>
        </div>

        <div style="
            margin-top:40px;
            font-size:30px;
            color:#5c7a8a;
            font-weight:700;
        ">
            天弘余额宝最新七日年化
        </div>

        <div style="
            margin-top:10px;
            font-size:42px;
            color:#c9a063;
            font-weight:700;
        ">
            {yuebao}
        </div>

    </div>

    </body>
    </html>
    """

    with open("temp.html", "w", encoding="utf-8") as f:
        f.write(html)


# ===== 截图=====
def screenshot():
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox"])
        page = browser.new_page(
            viewport={"width":750, "height":1334},
            device_scale_factor=2
        )
        page.goto("file://" + os.getcwd() + "/temp.html")
        page.screenshot(path="out.png")
        browser.close()


# ===== 发送企业微信=====
def send():
    img = open("out.png", "rb").read()

    requests.post(WEBHOOK, json={
        "msgtype": "image",
        "image": {
            "base64": base64.b64encode(img).decode(),
            "md5": hashlib.md5(img).hexdigest()
        }
    })


# ===== 主流程=====
def main():
    news = get_news()
    make_html(news)
    screenshot()
    send()


if __name__ == "__main__":
    main()
