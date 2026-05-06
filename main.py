import requests
from datetime import datetime
import os
import base64
import hashlib
from playwright.sync_api import sync_playwright
import xml.etree.ElementTree as ET

WEBHOOK = os.getenv("WEBHOOK")


# ===== 新闻（去来源 + 去重）=====
def get_news():
    try:
        url = "https://news.google.com/rss/search?q=财经&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
        res = requests.get(url, timeout=10)
        res.encoding = "utf-8"

        root = ET.fromstring(res.text)

        news = []
        seen = set()

        for item in root.findall(".//item"):
            title = item.find("title").text.strip()

            # 去掉来源（- xxx）
            if " - " in title:
                title = title.split(" - ")[0]

            if title not in seen:
                seen.add(title)
                news.append(title)

            if len(news) >= 3:
                break

        while len(news) < 3:
            news.append("暂无财经要闻")

        return news

    except:
        return ["新闻获取失败"] * 3


# ===== UI =====
def make_html(news):
    now = datetime.now()

    year = now.strftime("%Y")
    date_big = now.strftime("%m.%d")
    weekday = ["MON","TUE","WED","THU","FRI","SAT","SUN"][now.weekday()]

    yi = "嫁娶 祭祀 祈福"
    ji = "开光 掘井 开仓"

    html = f"""
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
        font-size:150px;
        font-weight:900;
        color:#e2e7ec;
        letter-spacing:14px;
    ">
        TONGTU
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

        <!-- 黄历（更紧凑） -->
        <div style="margin-top:10px;font-size:20px;line-height:1.5;">
            <span style="color:#1fa463;">宜：{yi}</span><br>
            <span style="color:#e05a5a;">忌：{ji}</span>
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
            <p style="margin:0 0 18px 0;">{news[0]}</p>

            <div style="border-top:1px dashed #dcdcdc;margin:16px 0;"></div>

            <p style="margin:0 0 18px 0;">{news[1]}</p>

            <div style="border-top:1px dashed #dcdcdc;margin:16px 0;"></div>

            <p style="margin:0;">{news[2]}</p>
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

    with open("temp.html", "w", encoding="utf-8") as f:
        f.write(html)


# ===== 截图 =====
def screenshot():
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox"])
        page = browser.new_page(
            viewport={"width":750,"height":1334},
            device_scale_factor=2
        )
        page.goto("file://" + os.getcwd() + "/temp.html")
        page.screenshot(path="out.png")
        browser.close()


# ===== 发送 =====
def send():
    img = open("out.png","rb").read()

    requests.post(WEBHOOK, json={
        "msgtype":"image",
        "image":{
            "base64": base64.b64encode(img).decode(),
            "md5": hashlib.md5(img).hexdigest()
        }
    })


# ===== 主流程 =====
def main():
    news = get_news()
    make_html(news)
    screenshot()
    send()


if __name__ == "__main__":
    main()
