import requests
from bs4 import BeautifulSoup
import streamlit as st

VERIFY_KEYWORDS = ["环境异常", "访问过于频繁", "请在微信客户端打开", "请输入验证码", "安全验证", "验证后继续"]
UA_LIST = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
]

@st.cache_data(ttl=600, show_spinner=False)
def fetch_page_cached(url: str, ua_idx: int):
    headers = {"User-Agent": UA_LIST[ua_idx], "Accept-Language": "zh-CN,zh;q=0.9"}
    res = requests.get(url, headers=headers, timeout=12)
    return res.status_code, res.text

def looks_like_verify_page(page_html: str) -> bool:
    if not page_html:
        return True
    s = page_html[:20000]
    return any(k in s for k in VERIFY_KEYWORDS)

def extract_wechat_text(page_html: str):
    soup = BeautifulSoup(page_html, "html.parser")
    content_div = soup.find("div", id="js_content")
    return content_div.get_text(separator="\n", strip=True) if content_div else None

def get_article_text_smart(url: str):
    last_hint = None
    for attempt, ua_idx in enumerate([0, 1, 2], start=1):
        try:
            code, page_html = fetch_page_cached(url, ua_idx)
            if code != 200:
                last_hint = f"HTTP {code}（第{attempt}次）"
                continue
            if looks_like_verify_page(page_html):
                last_hint = f"疑似验证/拦截页（第{attempt}次）"
                continue
            text = extract_wechat_text(page_html)
            if not text:
                last_hint = f"未找到 js_content（第{attempt}次）"
                continue
            return text, "来自链接抓取"
        except requests.exceptions.Timeout:
            last_hint = f"抓取超时（第{attempt}次）"
        except requests.exceptions.RequestException as e:
            last_hint = f"网络错误：{e}（第{attempt}次）"
    return None, (last_hint or "抓取失败")
