import requests
from datetime import datetime
import os
import base64
import hashlib
from playwright.sync_api import sync_playwright
import xml.etree.ElementTree as ET

WEBHOOK = os.getenv("WEBHOOK")


# ===== 新闻 =====
def get_news():
    try:
        url = "https://news.google.com/rss/search?q=财经&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
        res = requests.get(url, timeout=10)
        res.encoding = "utf-8"

        root = ET.fromstring(res.text)
        news = [item.find("title").text for item in root.findall(".//item")[:3]]

        return news if news else ["暂无财经新闻"]

    except:
        return ["新闻获取失败"]


# ===== UI（已对齐模板）=====
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
        background:linear-gradient(180deg,#f3f5f7,#e7edf2);
    ">

    <!-- LOGO -->
    <div style="position:absolute;top:50px;left:40px;">
        <div style="font-size:30px;font-weight:700;">通途控股</div>
        <div style="font-size:16px;color:#777;margin-top:4px;">TONGTU HOLDINGS</div>
    </div>

    <!-- 背景大字 -->
    <div style="
        position:absolute;
        top:180px;
        left:40px;
        font-size:140px;
        font-weight:900;
        color:#d8dee6;
        letter-spacing:8px;
    ">
        TONGTU
    </div>

    <!-- 主标题 -->
    <div style="
        position:absolute;
        top:300px;
        left:40px;
        font-size:96px;
        font-weight:900;
        letter-spacing:2px;
    ">
        <span style="color:#5c6f7c;">通途</span>
        <span style="color:#c9a063;">早安</span>
    </div>

    <!-- 日期 -->
    <div style="
        position:absolute;
        top:260px;
        right:50px;
        text-align:right;
    ">
        <div style="font-size:26px;color:#666;">{year}</div>
        <div style="font-size:78px;font-weight:900;line-height:1;">{date_big}</div>
        <div style="font-size:22px;color:#888;margin-top:6px;">{weekday}</div>

        <div style="margin-top:18px;font-size:22px;line-height:1.6;">
            <span style="color:#16a34a;">宜：{yi}</span><br>
            <span style="color:#dc2626;">忌：{ji}</span>
        </div>
    </div>

    <!-- 卡片 -->
    <div style="
        position:absolute;
        top:460px;
        left:30px;
        width:690px;
        background:#f7f8fa;
        border-radius:32px;
        padding:34px;
    ">

        <!-- 标题 -->
        <div style="
            background:#6f8796;
            color:#fff;
            display:inline-block;
            padding:12px 32px;
            border-radius:22px;
            font-size:26px;
            margin-bottom:26px;
        ">
            每日资讯
        </div>

        <!-- 内容 -->
        <div style="
            font-size:28px;
            color:#333;
            line-height:1.8;
        ">
            <p style="margin:0 0 22px 0;">{news[0]}</p>

            <div style="border-top:2px dashed #cfcfcf;margin:18px 0;"></div>

            <p style="margin:0 0 22px 0;">{news[1]}</p>

            <div style="border-top:2px dashed #cfcfcf;margin:18px 0;"></div>

            <p style="margin:0;">{news[2]}</p>
        </div>

    </div>

    <!-- 底部利率 -->
    <div style="
        position:absolute;
        bottom:90px;
        left:40px;
    ">

        <div style="font-size:34px;color:#5c7a8a;font-weight:700;">
            人民币最新存款利率
        </div>

        <div style="margin-top:18px;font-size:30px;">
            活期存款：<span style="color:#c9a063;">0.05%</span>
        </div>

        <div style="margin-top:8px;font-size:30px;">
            一年定期：<span style="color:#c9a063;">0.95%</span>
        </div>

        <div style="margin-top:38px;font-size:34px;color:#5c7a8a;font-weight:700;">
            天弘余额宝最新七日年化
        </div>

        <div style="margin-top:12px;font-size:46px;color:#c9a063;font-weight:900;">
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
            viewport={"width":750, "height":1334},
            device_scale_factor=2
        )
        page.goto("file://" + os.getcwd() + "/temp.html")
        page.screenshot(path="out.png")
        browser.close()


# ===== 发送 =====
def send():
    img = open("out.png", "rb").read()

    requests.post(WEBHOOK, json={
        "msgtype": "image",
        "image": {
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
