import streamlit as st
import requests
import json
from bs4 import BeautifulSoup

# --- 页面基础设置 ---
st.set_page_config(page_title="高级二创工作台", layout="centered")
st.title("✍️ 高级二创一体化工具")

# --- 核心抓取函数 ---
def get_article_content(url):
    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15"}
    try:
        res = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        content_div = soup.find('div', id='js_content')
        if not content_div:
            return None
        # 提取文字并保持一定的换行结构
        return content_div.get_text(separator='\n', strip=True)
    except:
        return None

# --- 流式 AI 逻辑 ---
def stream_ai_rewrite(text, api_key):
    url = "https://api.deepseek.com/chat/completions"
    
    # 深度强制指令：确保序号、小标题、无废话
    system_prompt = """你是一个只会输出成品推文的专业改写机器人。
    1. 禁止输出任何开场白（如“好的”、“为您改写”）。
    2. 禁止输出任何标签词（如“标题：”、“正文：”、“导语：”、“小标题：”）。
    3. 结构必须为：5个带数字序号的爆款标题 -> 空行 -> 带小标题的正文。
    4. 正文的小标题必须独立成行，模仿原文的叙事节奏。"""
    
    user_prompt = f"""任务：对以下干细胞推文内容进行深度二创。
    
    要求：
    - 开头直接给出5个爆款标题，必须带序号 1. 2. 3. 4. 5. 且每行一个。
    - 正文必须根据原文逻辑，设置至少3-4个核心小标题。
    - 严格执行原创建议：句型重组、视角转换、内容拓展。
    
    原文内容：
    ({text})
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

# --- 界面展示 ---
target_url = st.text_input("🔗 粘贴微信文章链接", placeholder="https://mp.weixin.qq.com/s/...")

if st.button("🚀 开始极速二创", type="primary", use_container_width=True):
    api_key = st.secrets.get("DEEPSEEK_API_KEY")
    if not api_key:
        st.error("请先在 Secrets 中配置 DEEPSEEK_API_KEY")
    elif target_url:
        with st.spinner("正在抓取并同步改写中..."):
            raw_text = get_article_content(target_url)
            if raw_text:
                content_placeholder = st.empty()
                full_content = ""
                
                # 流式输出，保证第一时间看到标题
                for chunk in stream_ai_rewrite(raw_text, api_key):
                    full_content += chunk
                    content_placeholder.markdown(full_content + "▌")
                
                content_placeholder.empty()
                
                # --- 分页展示与一键复制 ---
                tab1, tab2 = st.tabs(["📋 纯文本版 (适合直接粘贴)", "📝 Markdown版 (适合排版工具)"])
                
                with tab1:
                    # 纯文本版去掉 Markdown 符号
                    clean_text = full_content.replace("#", "").replace("**", "").strip()
                    st.code(clean_text, language="text")
                    st.caption("✨ 特点：带序号标题，带换行小标题，无代码符号")
                    
                with tab2:
                    # Markdown版保留格式
                    st.code(full_content, language="markdown")
                    st.caption("✨ 特点：保留加粗和层级，适合粘贴至 MdNice")
                    
                st.success("✅ 生成完毕！请点击右上方按钮复制。")
            else:
                st.error("无法抓取文章，请确认链接是否正确。")
