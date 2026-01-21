import streamlit as st
import requests
import json
from bs4 import BeautifulSoup

# --- 页面基础设置 ---
st.set_page_config(page_title="极简二创 Pro", layout="centered")
st.title("✍️ 深度二创专业工作台")

# --- 核心抓取函数 ---
def get_article_content(url):
    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15"}
    try:
        res = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        content_div = soup.find('div', id='js_content')
        if not content_div: return None
        return content_div.get_text(separator='\n', strip=True)
    except: return None

# --- 流式 AI 逻辑 ---
def stream_ai_rewrite(text, api_key):
    url = "https://api.deepseek.com/chat/completions"
    
    # 终极提示词指令
    system_prompt = """你是一个专业的公众号深度改写专家。
    【禁令】：严禁输出“导语、主体、结语、前言、后记、总结”等词汇。严禁任何开场白。
    【结构要求】：
    1. 第一行直接写：【推荐爆款标题】
    2. 接下来输出5个爆款标题，每个标题必须独占一行，且标题与标题之间必须空一行。格式为：1. XXX \n\n 2. XXX。
    3. 标题结束后，空三行进入正文。
    4. 正文开头：严禁直接使用小标题。必须先写一段100字左右的引入性文字，直接进入主题。
    5. 正文后续：使用 ## 01. [内容]、## 02. [内容] 的格式设置小标题，小标题前后必须有换行。
    6. 语气：犀利、专业、引人入胜。"""
    
    user_prompt = f"请根据原文进行深度二创。原文内容=（{text}）"
    
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

# --- 界面展示 ---
target_url = st.text_input("🔗 粘贴微信文章链接")

if st.button("🚀 开始极速生成", type="primary", use_container_width=True):
    api_key = st.secrets.get("DEEPSEEK_API_KEY")
    if not api_key:
        st.error("请配置环境变量 DEEPSEEK_API_KEY")
    elif target_url:
        with st.status("正在处理中...", expanded=True) as status:
            raw_text = get_article_content(target_url)
            if raw_text:
                full_content = ""
                placeholder = st.empty()
                
                # 流式输出预览
                for chunk in stream_ai_rewrite(raw_text, api_key):
                    full_content += chunk
                    placeholder.markdown(full_content + "▌")
                placeholder.markdown(full_content)
                status.update(label="✅ 生成完毕", state="complete")
                
                st.divider()
                
                # --- 多版本展示与复制 ---
                tab1, tab2 = st.tabs(["📋 纯文本 (公众号直接粘贴)", "📝 Markdown (排版工具使用)"])
                
                with tab1:
                    # 纯文本版：去除 Markdown 符号但保留换行逻辑
                    clean_text = full_content.replace("## ", "").replace("**", "").strip()
                    st.code(clean_text, language="text")
                    st.caption("✨ 此版本已带序号，标题已换行，适合直接复制到微信编辑器")
                
                with tab2:
                    st.code(full_content, language="markdown")
                    st.caption("✨ 此版本带 ## 标记，建议粘贴到 MdNice 进行二次排版")
            else:
                st.error("内容抓取失败，请检查链接有效性。")
