import streamlit as st
import requests
import json
from bs4 import BeautifulSoup
import markdown
import streamlit.components.v1 as components

# --- 页面基础设置 ---
st.set_page_config(page_title="二创精修工作台", layout="centered")
st.title("✍️ 深度二创专业工作台")

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
    # 强化指令：标题双换行，小标题 2-4 个，开头无小标题
    system_prompt = """你是一个专业的公众号改写专家。禁止废话。
    【结构规范】：
    1. 开头写【推荐爆款标题】，接着5个标题。
    2. 关键：每个标题后必须跟两个换行符(\\n\\n)，严禁挤在一起。
    3. 标题区结束后空三行。正文开头必须先写100字引入语，严禁直接使用小标题。
    4. 小标题格式固定为 ## 01. XXX。数量控制在 2-4 个。"""
    
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

# --- 界面 ---
target_url = st.text_input("🔗 粘贴微信链接并开始")

if st.button("🚀 开始极速生成", type="primary", use_container_width=True):
    api_key = st.secrets.get("DEEPSEEK_API_KEY")
    if target_url and api_key:
        raw_text = get_article_content(target_url)
        if raw_text:
            full_content = ""
            placeholder = st.empty() 
            # 1. 流式展示
            for chunk in stream_ai_rewrite(raw_text, api_key):
                full_content += chunk
                placeholder.markdown(full_content + "▌")
            placeholder.markdown(full_content)
            
            # 2. 转换 Markdown 为 HTML，并注入 18号/17号 样式
            html_main = markdown.markdown(full_content)
            styled_output = f"""
            <div id="copy-area" style="padding: 20px; background: #fff; line-height: 1.8; text-align: justify;">
                <style>
                    /* 18号黑体小标题 */
                    h2 {{ 
                        font-size: 18px; 
                        font-family: "SimHei", "STHeiti", sans-serif; 
                        font-weight: bold; 
                        color: #000; 
                        margin: 25px 0 10px 0; 
                    }}
                    /* 17号宋体正文 */
                    p {{ 
                        font-size: 17px; 
                        font-family: "SimSun", "STSong", serif; 
                        color: #333;
                        margin-bottom: 15px; 
                    }}
                </style>
                <div class="rich-content">{html_main}</div>
            </div>
            """
            
            st.subheader("🟢 最终预览（带 18号/17号 格式）")
            st.markdown(styled_output, unsafe_allow_html=True)
            
            # 3. 手机一键复制按钮
            copy_js = f"""
            <div style="text-align:center; margin-top:20px;">
                <button id="c-btn" style="background:#07c160; color:white; border:none; padding:15px 30px; font-size:18px; border-radius:8px; width:100%;">📋 一键复制成品 (保留标题字号)</button>
            </div>
            <script>
            document.getElementById('c-btn').onclick = function() {{
                const area = parent.document.getElementById('copy-area');
                const range = document.createRange();
                range.selectNode(area);
                const sel = window.getSelection();
                sel.removeAllRanges(); sel.addRange(range);
                document.execCommand('copy');
                this.innerText = '✅ 复制成功，去粘贴吧';
                sel.removeAllRanges();
            }};
            </script>
            """
            components.html(copy_js, height=100)
            
            # 4. 提供纯文本和 Markdown 源码供备用
            with st.expander("辅助复制 (纯文本/Markdown)"):
                st.code(full_content.replace("## ", ""), language="text")
                st.code(full_content, language="markdown")
        else: st.error("抓取失败")
