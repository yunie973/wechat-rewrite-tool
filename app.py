import streamlit as st
import requests
import json
from bs4 import BeautifulSoup

# --- 页面设置 ---
st.set_page_config(page_title="极简二创助手", layout="centered")
st.title("🚀 极简二创工作台")

# --- 核心抓取 ---
def get_text(url):
    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X)"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        content = soup.find('div', id='js_content')
        return content.get_text(separator='\n', strip=True) if content else None
    except: return None

# --- 流式逻辑 ---
def stream_ai(text, api_key):
    url = "https://api.deepseek.com/chat/completions"
    
    # 极简提示词：强制禁止废话，禁止标签
    system_prompt = "你是一个只会输出成品文章的机器人。禁止任何开场白、解释说明。禁止使用‘标题：’、‘正文：’、‘主体：’等标签词。"
    user_prompt = f"""
    任务：对以下内容进行原创深度二创。
    要求：
    1. 最开头直接给出5个爆款标题，每行一个。
    2. 空一行后直接开始正文。
    3. 严格遵循原创建议：句型重组、视角转换、内容拓展。
    4. 禁止出现任何“以下是、好的、改写如下”等字样。
    
    原文内容：({text})
    """
    
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "stream": True,
        "temperature": 0.7
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

# --- 界面 ---
url = st.text_input("粘贴文章链接", placeholder="https://mp.weixin.qq.com/s/...")

if st.button("✨ 立即开始二创", type="primary", use_container_width=True):
    api_key = st.secrets.get("DEEPSEEK_API_KEY")
    if not api_key:
        st.error("请先配置 Secrets 中的 DEEPSEEK_API_KEY")
    elif url:
        raw_text = get_text(url)
        if raw_text:
            status_placeholder = st.empty()
            content_placeholder = st.empty()
            full_content = ""
            
            status_placeholder.info("⚡ 正在极速生成...")
            
            # 流式展示
            for chunk in stream_ai(raw_text, api_key):
                full_content += chunk
                content_placeholder.markdown(full_content + "▌")
            
            status_placeholder.empty()
            content_placeholder.empty()
            
            # 分离展示并提供复制按钮
            tab1, tab2 = st.tabs(["📋 纯文本 (一键复制)", "📝 Markdown (一键复制)"])
            
            with tab1:
                # 去除 Markdown 符号的“干净”文本
                clean_text = full_content.replace("#", "").replace("**", "").strip()
                st.code(clean_text, language="text")
                st.caption("适合直接粘贴到公众号普通编辑器")
                
            with tab2:
                # 保留所有 Markdown 格式
                st.code(full_content, language="markdown")
                st.caption("适合粘贴到 MdNice 或其他 Markdown 排版工具")
                
            st.success("✅ 生成完毕")
        else:
            st.error("内容提取失败")
