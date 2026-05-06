import requests
from datetime import datetime
import os
import base64
import hashlib
from playwright.sync_api import sync_playwright
import xml.etree.ElementTree as ET

WEBHOOK = os.getenv("WEBHOOK")


# ===== 新闻（稳定源）=====
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

    except:
        return ["新闻获取失败"]


# ===== 黄历（简化版稳定）=====
def get_huangli():
    # 不用API，避免失败
    return {
        "yi": "出行 交易 签约",
        "ji": "争执 冲动 投资"
    }


# ===== 利率（写死稳定版，可后续升级）=====
def get_rate():
    return {
        "lpr1": "3.45%",
        "lpr5": "3.95%"
    }


# ===== UI生成（终极版）=====
def make_html(news, hl, rate):
    now = datetime.now()
    date = now.strftime("%Y年%m月%d日")
    weekday = ["星期一","星期二","星期三","星期四","星期五","星期六","星期日"][now.weekday()]

    html = f"""
    <html>
    <head>
    <meta charset="utf-8">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;700&display=swap" rel="stylesheet">
    </head>

    <body style="
        width:750px;
        height:1334px;
        margin:0;
        font-family:'Noto Sans SC', sans-serif;
        background:linear-gradient(135deg,#667eea,#764ba2);
        padding:30px;
        box-sizing:border-box;
        color:#333;
    ">

    <!-- 主卡片 -->
    <div style="
        background:#ffffff;
        border-radius:30px;
        padding:40px;
        height:100%;
        box-shadow:0 20px 60px rgba(0,0,0,0.15);
    ">

    <!-- 标题 -->
    <div style="font-size:64px;font-weight:700;">
        早安资讯
    </div>

    <!-- 日期 -->
    <div style="color:#888;margin-top:10px;font-size:24px;">
        {date} · {weekday}
    </div>

    <!-- 黄历 -->
    <div style="
        margin-top:30px;
        display:flex;
        gap:20px;
    ">
        <div style="
            flex:1;
            background:#f0fdf4;
            border-radius:20px;
            padding:20px;
        ">
            <div style="color:#16a34a;font-weight:700;">宜</div>
            <div style="margin-top:10px;">{hl['yi']}</div>
        </div>

        <div style="
            flex:1;
            background:#fef2f2;
            border-radius:20px;
            padding:20px;
        ">
            <div style="color:#dc2626;font-weight:700;">忌</div>
            <div style="margin-top:10px;">{hl['ji']}</div>
        </div>
    </div>

    <!-- 新闻 -->
    <div style="margin-top:40px;">
        <div style="font-size:30px;font-weight:700;">财经要闻</div>

        <div style="margin-top:20px;font-size:26px;line-height:1.6;">
        {''.join([f'<p>• {n}</p>' for n in news])}
        </div>
    </div>

    <!-- 利率 -->
    <div style="
        margin-top:40px;
        background:#f8fafc;
        border-radius:20px;
        padding:20px;
        font-size:24px;
    ">
        <div>1年期LPR：{rate['lpr1']}</div>
        <div style="margin-top:10px;">5年期LPR：{rate['lpr5']}</div>
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
        page = browser.new_page(viewport={"width":750,"height":1334}, device_scale_factor=2)
        page.goto("file://" + os.getcwd() + "/temp.html")
        page.screenshot(path="out.png")
        browser.close()


# ===== 发送=====
def send():
    img = open("out.png","rb").read()

    requests.post(WEBHOOK, json={
        "msgtype":"image",
        "image":{
            "base64": base64.b64encode(img).decode(),
            "md5": hashlib.md5(img).hexdigest()
        }
    })


# ===== 主流程=====
def main():
    news = get_news()
    hl = get_huangli()
    rate = get_rate()

    make_html(news, hl, rate)
    screenshot()
    send()


if __name__ == "__main__":
    main()
