import streamlit as st
import requests
import json
from bs4 import BeautifulSoup
import markdown  # 新增库

# --- 页面基础设置 ---
st.set_page_config(page_title="二创 HTML 增强版", layout="centered")
st.title("✍️ 深度二创专业工作台")

# --- 核心抓取函数 ---
def get_article_content(url):
    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15"}
    try:
        res = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        content_div = soup.find('div', id='js_content')
        return content_div.get_text(separator='\n', strip=True) if content_div else None
    except: return None

# --- 流式 AI 逻辑 ---
def stream_ai_rewrite(text, api_key):
    url = "https://api.deepseek.com/chat/completions"
    system_prompt = """你是一个专业的公众号深度改写专家。
    【绝对禁令】：严禁输出“导语、主体、结语、前言、后记、总结”等词汇。严禁任何开场白。
    【标题规范】：第一行写【推荐爆款标题】，接着输出5个爆款标题，每个标题后跟两个换行。
    【正文规范】：标题结束后空三行。正文开头必须先写100字左右引入语，严禁直接使用小标题。
    【小标题格式】：使用 '## 01. [标题]' 格式，前后保持空行。"""
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"原文=({text})"}],
        "stream": True,
        "temperature": 0.7
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    response = requests.post(url, headers=headers, json=payload, stream=True)
    for line in response.iter_lines():
        if line:
            chunk = line.decode('utf-8').removeprefix('data: ')
            if chunk == '[DONE]': break
            try:
                data = json.loads(chunk)
                yield data['choices'][0]['delta'].get('content', '')
            except: continue

# --- UI 界面 ---
target_url = st.text_input("🔗 粘贴微信文章链接")

if st.button("🚀 开始极速生成并转换", type="primary", use_container_width=True):
    api_key = st.secrets.get("DEEPSEEK_API_KEY")
    if target_url and api_key:
        with st.status("正在处理中...") as status:
            raw_text = get_article_content(target_url)
            if raw_text:
                full_content = ""
                placeholder = st.empty()
                for chunk in stream_ai_rewrite(raw_text, api_key):
                    full_content += chunk
                    placeholder.markdown(full_content + "▌")
                placeholder.markdown(full_content)
                status.update(label="✅ 生成完毕", state="complete")
                
                st.divider()
                
                # --- 多版本复制选项卡 ---
                tab1, tab2, tab3 = st.tabs(["📱 富文本预览 (推荐)", "📋 纯文本", "📝 Markdown"])
                
                with tab1:
                    # 定义微信风格 HTML 样式
                    wechat_css = """
                    <style>
                        .rich-text { padding: 15px; border: 1px solid #f0f0f0; border-radius: 10px; line-height: 1.8; color: #333; }
                        .rich-text h2 { font-size: 1.25em; color: #07c160; border-bottom: 2px solid #07c160; padding-bottom: 5px; margin-top: 25px; }
                        .rich-text p { margin-bottom: 15px; }
                    </style>
                    """
                    # 转换 Markdown 为 HTML
                    html_content = markdown.markdown(full_content)
                    st.markdown(wechat_css + f'<div class="rich-text">{html_content}</div>', unsafe_allow_html=True)
                    st.caption("💡 手机端：在此区域【长按全选】复制，粘贴到公众号可保留大标题和颜色。")
                
                with tab2:
                    st.code(full_content.replace("## ", "").replace("**", ""), language="text")
                
                with tab3:
                    st.code(full_content, language="markdown")
            else: st.error("内容抓取失败")
