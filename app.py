import streamlit as st
import requests
import json
from bs4 import BeautifulSoup
import markdown
import streamlit.components.v1 as components

st.set_page_config(page_title="二创精修版", layout="centered")
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
    system_prompt = """你是一个专业的公众号改写专家。禁止输出导语、结语等词汇。禁止任何开场白。
    【结构】：开头写【推荐爆款标题】，接着5个标题（每个标题必须单独一行）。
    【正文】：标题区结束后空三行。正文开头先写100字引入语。小标题格式 ## 01. XXX。
    【限制】：小标题总数控制在2-4个。标题之间严禁挤在一起。"""
    
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

target_url = st.text_input("🔗 粘贴微信链接并开始")

if st.button("🚀 开始极速生成", type="primary", use_container_width=True):
    api_key = st.secrets.get("DEEPSEEK_API_KEY")
    if target_url and api_key:
        raw_text = get_article_content(target_url)
        if raw_text:
            full_content = ""
            placeholder = st.empty() 
            for chunk in stream_ai_rewrite(raw_text, api_key):
                full_content += chunk
                # 修复预览时的标题换行显示
                placeholder.markdown(full_content.replace("\\n", "\n") + "▌")
            
            # 修正 AI 可能输出的错误换行符
            final_content = full_content.replace("\\n", "\n")
            placeholder.markdown(final_content)
            
            # --- 核心排版区：18号黑体/17号宋体 ---
            html_main = markdown.markdown(final_content)
            styled_output = f"""
            <div id="copy-area" style="padding: 20px; background: #fff; line-height: 1.8; text-align: justify;">
                <style>
                    .rich-content {{ font-family: "SimSun", "STSong", serif; font-size: 17px; color: #333; }}
                    h2 {{ font-size: 18px; font-family: "SimHei", sans-serif; font-weight: bold; color: #000; margin: 25px 0 10px 0; }}
                    p {{ margin-bottom: 15px; }}
                </style>
                <div class="rich-content">{html_main}</div>
            </div>
            """
            
            st.subheader("🟢 排版预览（长按此区域或点击下方按钮复制）")
            st.markdown(styled_output, unsafe_allow_html=True)
            
            # 一键复制按钮代码
            copy_js = f"""
            <div style="text-align:center; margin-top:20px;">
                <button id="c-btn" style="background:#07c160; color:white; border:none; padding:15px 30px; font-size:18px; border-radius:8px; width:100%; cursor:pointer;">📋 一键复制成品 (带18/17号格式)</button>
            </div>
            <script>
            document.getElementById('c-btn').onclick = function() {{
                const area = parent.document.getElementById('copy-area');
                const range = document.createRange();
                range.selectNode(area);
                const sel = window.getSelection();
                sel.removeAllRanges(); sel.addRange(range);
                document.execCommand('copy');
                this.innerText = '✅ 复制成功';
                sel.removeAllRanges();
            }};
            </script>
            """
            components.html(copy_js, height=100)
        else: st.error("内容抓取失败")
