import streamlit as st
import requests
import json
from bs4 import BeautifulSoup

# --- 页面基础设置 ---
st.set_page_config(page_title="高级二创工作台", layout="centered")
st.title("✍️ 深度二创排版助手")

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
    
    # 终极死命令：禁止特定词汇，强制标题格式
    system_prompt = """你是一个专业的公众号深度二创机器人。
    1. 严禁输出：导语、主体、结语、前言、后记、改写如下、好的、总结。
    2. 结构要求：
       - 开头第一行写：【推荐爆款标题】
       - 紧接着输出 5 个带序号的标题（1. 2. 3. 4. 5.）。
       - 空两行后直接开始正文。
    3. 正文格式：
       - 必须包含 3-4 个小标题。
       - 小标题格式严格统一为：## 01 [标题内容]、## 02 [标题内容] 等。
       - 正文段落之间保持空行。
    4. 语气：犀利、专业、极具传播力。"""
    
    user_prompt = f"任务：对以下内容进行深度二创。原文=（{text}）"
    
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
        st.error("请配置 DEEPSEEK_API_KEY")
    elif target_url:
        with st.spinner("正在抓取并改写中..."):
            raw_text = get_article_content(target_url)
            if raw_text:
                full_content = ""
                placeholder = st.empty()
                
                # 流式输出
                for chunk in stream_ai_rewrite(raw_text, api_key):
                    full_content += chunk
                    placeholder.markdown(full_content + "▌")
                
                placeholder.markdown(full_content)
                
                st.divider()
                
                # --- 多版本展示 ---
                tab1, tab2 = st.tabs(["📋 Markdown 纯文本版", "📱 手机长按预览版"])
                
                with tab1:
                    st.code(full_content, language="markdown")
                    st.caption("✨ 此版本保留 ## 标记，粘贴到公众号或 MdNice 会自动识别大小标题")
                
                with tab2:
                    # 自定义预览区，强制显示大小区别
                    st.markdown("""
                    <style>
                        .preview-box { padding:10px; border:1px solid #ddd; border-radius:8px; line-height:1.7; color:#333; }
                        .preview-box h2 { font-size: 1.3em; color: #07c160; margin-top:20px; }
                        .preview-box p { margin-bottom: 15px; }
                    </style>
                    """, unsafe_allow_html=True)
                    
                    # 将内容转为简单的 HTML 预览
                    import markdown
                    html_preview = markdown.markdown(full_content)
                    st.markdown(f'<div class="preview-box">{html_preview}</div>', unsafe_allow_html=True)
                    st.caption("✨ 手机端建议长按此处绿色标题区域进行全选复制")
            else:
                st.error("提取失败，请检查链接。")
