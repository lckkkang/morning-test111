import requests
from datetime import datetime
import os
import base64
import hashlib
import re
from playwright.sync_api import sync_playwright

WEBHOOK = os.getenv("WEBHOOK")

# ===== 获取财经新闻（稳定版）=====
def get_news():
    try:
        url = "https://finance.sina.com.cn/"
        res = requests.get(url, timeout=10)

        # 关键：处理中文乱码
        res.encoding = "gbk"
        html = res.text

        # 提取标题
        titles = re.findall(r'<a[^>]+>(.*?)</a>', html)

        news = []
        for t in titles:
            t = re.sub('<.*?>', '', t).strip()

            # 过滤无效内容
            if len(t) > 10 and "新浪" not in t and "广告" not in t:
                news.append(t)

            if len(news) >= 5:
                break

        if not news:
            return ["暂无财经新闻", "市场数据整理中", "请稍后查看"]

        return news

    except Exception as e:
        return [
            "财经新闻获取失败",
            "请检查网络或稍后重试",
            str(e)
        ]

# ===== 生成HTML海报=====
def make_html(news):
    date = datetime.now().strftime("%Y-%m-%d")

    html = f"""
    <html>
    <body style="
        width:750px;
        height:1334px;
        font-family:"WenQuanYi Zen Hei","Noto Sans CJK SC","Microsoft YaHei",Arial;
        background:linear-gradient(#f5f7fa,#e4ecf3);
        padding:40px;
    ">

    <h1 style="font-size:60px;margin-bottom:20px;">早安资讯</h1>
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

    <div style="position:absolute;bottom:40px;color:#999;">
    每日自动推送
    </div>

    </body>
    </html>
    """

    with open("temp.html", "w", encoding="utf-8") as f:
        f.write(html)

# ===== 截图生成图片=====
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
    with open("out.png", "rb") as f:
        img = f.read()

    data = {
        "msgtype": "image",
        "image": {
            "base64": base64.b64encode(img).decode(),
            "md5": hashlib.md5(img).hexdigest()
        }
    }

    requests.post(WEBHOOK, json=data)

# ===== 主流程=====
def main():
    print("开始执行...")

    news = get_news()
    make_html(news)
    screenshot()
    send()

    print("完成发送")

if __name__ == "__main__":
    main()
