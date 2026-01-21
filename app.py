import streamlit as st
import requests
import json
from bs4 import BeautifulSoup
import markdown
import streamlit.components.v1 as components

# --- 页面基础设置 ---
st.set_page_config(page_title="极简二创-精修版", layout="centered")
st.title("✍️ 深度二创专业工作台")

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
    # 强化数量限制和结构指令
    system_prompt = """你是一个专业的公众号改写专家。
    【绝对禁令】：严禁输出“导语、主体、结语、总结”等词汇。严禁任何开场白。
    【结构规范】：
    1. 第一行【推荐爆款标题】，接着5个标题（每行一个，空两行）。
    2. 正文开头必须有100字左右引入语。
    3. 小标题格式固定为 ## 01. XXX。
    4. **数量限制**：正文小标题总数必须控制在 2 到 4 个之间，不得过多。"""
    
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
target_url = st.text_input("🔗 粘贴微信链接并开始")

if st.button("🚀 开始极速生成", type="primary", use_container_width=True):
    api_key = st.secrets.get("DEEPSEEK_API_KEY")
    if target_url and api_key:
        raw_text = get_article_content(target_url)
        if raw_text:
            full_content = ""
            main_placeholder = st.empty() 
            
            for chunk in stream_ai_rewrite(raw_text, api_key):
                full_content += chunk
                main_placeholder.markdown(full_content + "▌")
            
            main_placeholder.empty()
            html_content = markdown.markdown(full_content)
            
            # --- 精准匹配你的排版要求 ---
            # h2 对应小标题：18px, 黑体(SimHei), 加粗
            # p 对应正文：17px, 宋体(SimSun)
            wechat_styled_html = f"""
            <div id="copy-area" style="padding: 20px; background: #fff; color: #333; line-height: 1.8;">
                <style>
                    h2 {{ 
                        font-size: 18px; 
                        font-family: "SimHei", "Microsoft YaHei", sans-serif; 
                        font-weight: bold; 
                        color: #000; 
                        margin-top: 30px; 
                        margin-bottom: 10px;
                        border-left: 5px solid #000;
                        padding-left: 10px;
                    }}
                    p {{ 
                        font-size: 17px; 
                        font-family: "SimSun", "STSong", serif; 
                        margin-bottom: 15px; 
                        text-align: justify;
                    }}
                </style>
                {html_content}
            </div>
            """
            
            st.subheader("🟢 排版预览（已按要求设定字号字体）")
            st.markdown(wechat_styled_html, unsafe_allow_html=True)
            
            # 一键复制 JS 按钮
            copy_button_js = f"""
            <div style="text-align:center; margin-top:20px;">
                <button id="copy-btn" style="
                    background-color: #222; color: white; border: none; 
                    padding: 15px 30px; font-size: 18px; border-radius: 8px; 
                    width: 100%; cursor: pointer;
                ">📋 一键复制成品 (18号黑体/17号宋体)</button>
            </div>
            <script>
            document.getElementById('copy-btn').onclick = function() {{
                const area = parent.document.getElementById('copy-area');
                const range = document.createRange();
                range.selectNode(area);
                const selection = window.getSelection();
                selection.removeAllRanges();
                selection.addRange(range);
                try {{
                    document.execCommand('copy');
                    this.innerText = '✅ 复制成功，已保留格式';
                    this.style.backgroundColor = '#07c160';
                }} catch (err) {{ alert('复制失败，请尝试手动长按预览区'); }}
                selection.removeAllRanges();
            }};
            </script>
            """
            components.html(copy_button_js, height=100)
            
            with st.expander("查看原始 Markdown 数据"):
                st.code(full_content, language="markdown")
        else: st.error("内容抓取失败")
