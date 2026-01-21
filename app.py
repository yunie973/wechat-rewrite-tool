import streamlit as st
import requests
import json
from bs4 import BeautifulSoup
import markdown

# --- 页面配置 ---
st.set_page_config(page_title="AI二创排版一体化", layout="centered")
st.title("📱 移动端二创排版工作台")

# --- 核心抓取逻辑 ---
def get_article_text(url):
    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X)"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        content = soup.find('div', id='js_content')
        return content.get_text(separator='\n', strip=True) if content else None
    except: return None

# --- 流式 AI 逻辑 ---
def stream_ai_rewrite(text, api_key):
    url = "https://api.deepseek.com/chat/completions"
    # 这里使用您提供的原创性加强建议
    prompt = f"假设你是一个专业的自媒体作家...原文=({text})"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "stream": True # 开启流式，提高反应速度
    }
    response = requests.post(url, headers=headers, json=payload, stream=True)
    for line in response.iter_lines():
        if line:
            chunk = line.decode('utf-8').removeprefix('data: ')
            if chunk == '[DONE]': break
            try:
                data = json.loads(chunk)
                yield data['choices'][0]['delta'].get('content', '')
            except: continue

# --- 界面 UI ---
target_url = st.text_input("粘贴文章链接")

if st.button("✨ 极速二创并预览", type="primary", use_container_width=True):
    api_key = st.secrets.get("DEEPSEEK_API_KEY")
    if not api_key:
        st.error("请配置 API Key")
    elif target_url:
        raw_text = get_article_text(target_url)
        if raw_text:
            st.info("🚀 正在流式生成，请稍候...")
            placeholder = st.empty() # 文字展示区
            full_content = ""
            
            # 流式展示 Markdown 原文
            for chunk in stream_ai_rewrite(raw_text, api_key):
                full_content += chunk
                placeholder.markdown(full_content + "▌")
            
            placeholder.markdown(full_content)
            
            st.divider()
            
            # --- 自制预览区 (手机端长按复制此处) ---
            st.subheader("🟢 微信预览区（长按此处复制）")
            # 使用微信常用的排版样式
            wechat_style = """
            <style>
                .wechat-box { 
                    padding: 15px; border: 1px solid #eee; border-radius: 8px; 
                    line-height: 1.8; color: #333; font-family: sans-serif;
                }
                .wechat-box h2 { color: #07c160; border-bottom: 2px solid #07c160; }
            </style>
            """
            # 将 Markdown 转为 HTML
            rendered_html = markdown.markdown(full_content)
            st.markdown(wechat_style + f'<div class="wechat-box">{rendered_html}</div>', unsafe_allow_html=True)
            
            # 同时也提供一个代码框方便复制 Markdown 源码
            st.code(full_content, language="markdown")
