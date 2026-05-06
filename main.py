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


# ===== UI模板 =====
def make_html(news):
    now = datetime.now()
    date_big = now.strftime("%m.%d")
    year = now.strftime("%Y")
    weekday = ["MON","TUE","WED","THU","FRI","SAT","SUN"][now.weekday()]

    yi = "嫁娶 祭祀 祈福"
    ji = "开光 掘井 开仓"

    html = f"""
    <html>
    <head>
    <meta charset="utf-8">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;600;700;900&display=swap" rel="stylesheet">
    </head>

    <body style="
        margin:0;
        width:750px;
        height:1334px;
        font-family:'Noto Sans SC';
        background:linear-gradient(180deg,#f5f7fa,#e4ecf3);
        overflow:hidden;
    ">

    <!-- 顶部光效 -->
    <div style="
        position:absolute;
        width:600px;
        height:600px;
        background:radial-gradient(circle, rgba(255,220,150,0.8), transparent 70%);
        top:-100px;
        right:-100px;
    "></div>

    <!-- 大字背景 -->
    <div style="
        position:absolute;
        top:140px;
        left:40px;
        font-size:120px;
        font-weight:900;
        color:#dfe5ea;
        letter-spacing:10px;
    ">
        TONGTU
    </div>

    <!-- LOGO文字 -->
    <div style="position:absolute;top:40px;left:40px;">
        <div style="font-size:26px;font-weight:700;">通途控股</div>
        <div style="font-size:14px;color:#888;">TONGTU HOLDINGS</div>
    </div>

    <!-- 主标题 -->
    <div style="
        position:absolute;
        top:240px;
        left:40px;
        font-size:90px;
        font-weight:900;
    ">
        <span style="color:#5c6f7c;">通途</span>
        <span style="color:#c9a063;">早安</span>
    </div>

    <!-- 日期 -->
    <div style="
        position:absolute;
        top:200px;
        right:40px;
        text-align:right;
    ">
        <div style="font-size:24px;color:#666;">{year}</div>
        <div style="font-size:64px;font-weight:900;">{date_big}</div>
        <div style="font-size:20px;color:#888;">{weekday}</div>

        <div style="margin-top:20px;font-size:22px;">
            <span style="color:#16a34a;">宜：{yi}</span><br>
            <span style="color:#dc2626;">忌：{ji}</span>
        </div>
    </div>

    <!-- 卡片 -->
    <div style="
        position:absolute;
        top:420px;
        left:30px;
        width:690px;
        background:rgba(255,255,255,0.9);
        border-radius:30px;
        padding:30px;
        box-shadow:0 20px 50px rgba(0,0,0,0.1);
    ">

        <!-- 标题 -->
        <div style="
            background:linear-gradient(90deg,#5c7a8a,#8aa6b5);
            color:#fff;
            display:inline-block;
            padding:12px 30px;
            border-radius:20px;
            font-size:26px;
            margin-bottom:20px;
        ">
            每日资讯
        </div>

        <!-- 内容 -->
        <div style="font-size:26px;line-height:1.8;color:#333;">
            <p>{news[0]}</p>
            <hr style="border:none;border-top:2px dashed #ccc;margin:20px 0;">
            <p>{news[1]}</p>
            <hr style="border:none;border-top:2px dashed #ccc;margin:20px 0;">
            <p>{news[2]}</p>
        </div>

    </div>

    <!-- 底部 -->
    <div style="
        position:absolute;
        bottom:80px;
        left:40px;
    ">
        <div style="font-size:30px;color:#5c7a8a;font-weight:700;">
            人民币最新存款利率
        </div>

        <div style="margin-top:15px;font-size:28px;">
            活期存款：<span style="color:#c9a063;">0.05%</span>
        </div>

        <div style="margin-top:5px;font-size:28px;">
            一年定期：<span style="color:#c9a063;">0.95%</span>
        </div>

        <div style="margin-top:30px;font-size:30px;color:#5c7a8a;font-weight:700;">
            天弘余额宝最新七日年化
        </div>

        <div style="margin-top:10px;font-size:40px;color:#c9a063;font-weight:900;">
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
