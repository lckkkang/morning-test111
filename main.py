import requests
from datetime import datetime
import os
import base64
import hashlib
from playwright.sync_api import sync_playwright
import xml.etree.ElementTree as ET

WEBHOOK = os.getenv("WEBHOOK")

# ===== 获取新闻（Google News，全球稳定）=====
def get_news():
    try:
        url = "https://news.google.com/rss/search?q=财经&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
        res = requests.get(url, timeout=10)
        res.encoding = "utf-8"

        root = ET.fromstring(res.text)

        news = []
        for item in root.findall(".//item")[:5]:
            title = item.find("title").text
            news.append(title)

        if not news:
            return ["暂无财经新闻"]

        return news

    except Exception as e:
        return ["新闻获取失败", str(e)]


# ===== 生成HTML=====
def make_html(news):
    date = datetime.now().strftime("%Y-%m-%d")

    html = f"""
    <html>
    <head>
    <meta charset="utf-8">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC&display=swap" rel="stylesheet">
    </head>

    <body style="
        width:750px;
        height:1334px;
        font-family:'Noto Sans SC', Arial;
        background:linear-gradient(#f5f7fa,#e4ecf3);
        padding:40px;
    ">

    <h1 style="font-size:60px;">早安资讯</h1>
    <h3 style="color:#666;">{date}</h3>

    <div style="
        margin-top:60px;
        background:#ffffff;
        padding:30px;
        border-radius:20px;
        font-size:28px;
        line-height:1.6;
    ">
    {''.join([f'<p>• {n}</p>' for n in news])}
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


# ===== 发送=====
def send():
    with open("out.png", "rb") as f:
        img = f.read()

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
