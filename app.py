import streamlit as st
import requests
import json
from bs4 import BeautifulSoup
import markdown
import streamlit.components.v1 as components

# --- 页面基础设置 ---
st.set_page_config(page_title="极速二创-一键复制版", layout="centered")
st.title("⚡ 极速二创直出工作台")

# --- 核心函数 ---
def get_article_content(url):
    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X)"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        content_div = soup.find('div', id='js_content')
        return content_div.get_text(separator='\n', strip=True) if content_div else None
    except: return None

def stream_ai_rewrite(text, api_key):
    url = "https://api.deepseek.com/chat/completions"
    system_prompt = """你是一个专业的公众号深度改写专家。禁止废话。禁止输出导语、结语等词汇。
    结构：开头【推荐爆款标题】，接着5个标题（每行一个，空两行），正文必有100字引入语。小标题格式 ## 01. XXX。"""
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

# --- 界面展示 ---
target_url = st.text_input("🔗 粘贴链接并开始")

if st.button("🚀 立即生成", type="primary", use_container_width=True):
    api_key = st.secrets.get("DEEPSEEK_API_KEY")
    if target_url and api_key:
        raw_text = get_article_content(target_url)
        if raw_text:
            full_content = ""
            main_placeholder = st.empty() 
            
            # 1. 流式生成
            for chunk in stream_ai_rewrite(raw_text, api_key):
                full_content += chunk
                main_placeholder.markdown(full_content + "▌")
            
            main_placeholder.empty()
            
            # 2. 转换 Markdown 为 HTML
            html_content = markdown.markdown(full_content)
            
            # 3. 注入微信排版样式
            wechat_styled_html = f"""
            <div id="copy-area" style="padding: 15px; background: #fff; color: #333; line-height: 1.8; font-family: sans-serif;">
                <style>
                    h2 {{ color: #07c160; font-size: 1.4em; margin-top: 25px; border-bottom: 2px solid #07c160; padding-bottom: 5px; }}
                    p {{ margin-bottom: 15px; }}
                    ul, ol {{ margin-left: 20px; }}
                </style>
                {html_content}
            </div>
            """
            
            # 4. 展示预览区
            st.subheader("🟢 富文本预览")
            st.markdown(wechat_styled_html, unsafe_allow_html=True)
            
            # 5. 【核心】手机端一键复制 JavaScript 按钮
            # 针对 vivo 等安卓机型优化的剪贴板脚本
            copy_button_js = f"""
            <div style="text-align:center; margin-top:20px;">
                <button id="copy-btn" style="
                    background-color: #07c160; 
                    color: white; 
                    border: none; 
                    padding: 15px 30px; 
                    font-size: 18px; 
                    border-radius: 10px; 
                    width: 100%;
                    cursor: pointer;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                ">📋 一键复制成品 (带格式)</button>
            </div>

            <script>
            document.getElementById('copy-btn').onclick = function() {{
                const area = parent.document.getElementById('copy-area');
                if (!area) {{
                    alert('未找到内容区域，请重试');
                    return;
                }}
                
                const range = document.createRange();
                range.selectNode(area);
                const selection = window.getSelection();
                selection.removeAllRanges();
                selection.addRange(range);
                
                try {{
                    const successful = document.execCommand('copy');
                    if(successful) {{
                        this.innerText = '✅ 复制成功！可以直接粘贴了';
                        this.style.backgroundColor = '#059653';
                    }} else {{
                        alert('复制失败，请尝试长按手动复制');
                    }}
                }} catch (err) {{
                    alert('浏览器不支持自动复制，请手动选中。');
                }}
                selection.removeAllRanges();
            }};
            </script>
            """
            # 使用 components.html 嵌入脚本
            components.html(copy_button_js, height=100)
            
            st.divider()
            with st.expander("辅助复制 (纯文本/Markdown)"):
                st.code(full_content, language="markdown")
        else: st.error("内容抓取失败")
