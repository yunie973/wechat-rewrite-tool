import streamlit as st
import requests
import json
from bs4 import BeautifulSoup
import markdown
import streamlit.components.v1 as components
import re

# --- 1. 视觉皮肤 (微信绿 + 纯黑字 + 高对比度) ---
st.set_page_config(page_title="高级原创二创助手", layout="centered")

st.markdown("""
    <style>
    /* 全局颜色强制：背景白，文字绝对纯黑 */
    .stApp { background-color: #ffffff; color: #000000 !important; }
    h1 { color: #07c160 !important; font-family: "Microsoft YaHei"; text-align: center; font-weight: 800; }
    
    /* 输入框加固：文字黑色，边框绿色 */
    .stTextInput input { color: #000000 !important; font-weight: bold !important; font-size: 16px !important; }
    .stTextInput > div > div { border: 2px solid #07c160 !important; }

    /* 输出容器：浅灰背景，纯黑字体，保留换行 */
    .result-box {
        background-color: #f6f6f6 !important;
        color: #000000 !important;
        padding: 30px;
        border-radius: 8px;
        border: 1px solid #07c160;
        font-family: 'SimSun', 'STSong', '宋体', serif;
        font-size: 17px;
        line-height: 2.2;
        white-space: pre-wrap; /* 强制保留所有换行 */
        text-align: justify;
    }

    /* 微信绿按钮 */
    div.stButton > button { background-color: #07c160 !important; color: white !important; border-radius: 8px; height: 50px; font-weight: bold; width: 100%; border: none; font-size: 18px; }

    /* 固定页脚样式 */
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: white; padding: 12px 0; border-top: 2px solid #07c160;
        z-index: 999; display: flex; justify-content: center; align-items: center; gap: 20px;
    }
    .qr-item { color: #07c160; font-weight: bold; cursor: pointer; position: relative; }
    .qr-box {
        display: none; position: absolute; bottom: 45px; left: 50%;
        transform: translateX(-50%); width: 180px; background: white;
        padding: 10px; border: 2px solid #07c160; border-radius: 10px; box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    }
    .qr-item:hover .qr-box { display: block; }
    </style>

    <div class="footer">
        <span style="color:#000;">© 2026 <b>@兴洪</b> 版权所有</span>
        <div class="qr-item">📗 微信加我 <div class="qr-box"><img src="https://raw.githubusercontent.com/yunie973/wechat-rewrite-tool/main/wechat_qr.png.jpg" style="width:100%;"></div></div>
        <div class="qr-item">🪐 知识星球 <div class="qr-box"><img src="https://raw.githubusercontent.com/yunie973/wechat-rewrite-tool/main/star_qr.png.jpg" style="width:100%;"></div></div>
    </div>
""", unsafe_allow_html=True)

st.title("🛡️ 深度重构级专业工作台")

# --- 2. 核心算法 ---

def get_article_content(url):
    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X)"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        content_div = soup.find('div', id='js_content')
        return content_div.get_text(separator='\n', strip=True) if content_div else None
    except: return None

def safety_filter(text):
    """【物理过滤器】执行禁令，强制标题断行"""
    text = text.replace("\\n", "\n")
    # 物理拦截禁令
    text = text.replace("不是", "不单是").replace("而是", "更是").replace("——", "，").replace("—", "，")
    # 物理强制换行：给爆款标题和小标题补位
    text = re.sub(r'(【推荐爆款标题】)', r'\1\n', text)
    text = re.sub(r'([1-5]\. )', r'\n\1', text)
    text = re.sub(r'(\n?)(## 0[1-4]\.)', r'\n\n\2', text)
    return text

def stream_ai_rewrite(text, api_key):
    url = "https://api.deepseek.com/chat/completions"
    system_prompt = """假设你是一个专业的自媒体作家。对下文进行二创。
    【核心禁令】：严禁使用“不是...而是”，严禁出现破折号，严禁使用列表/分点。
    【结构要求 - 严格执行】：
    1. 第一行写：【推荐爆款标题】。
    2. 下方列出 5 个爆款标题，每个标题必须独占一行。
    3. 标题列表结束后，必须按 3 次回车进行换行。
    4. 正文开头写150字引入语。
    5. 正文中使用 ## 01. XXX 格式的小标题，且前后各空一行。"""
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"原文=（{text}）"}],
        "stream": True, "temperature": 0.8
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    return requests.post(url, headers=headers, json=payload, stream=True)

# --- 3. 展示逻辑 (修复 NameError) ---

target_url = st.text_input("🔗 粘贴链接开始深度重构")

if st.button("🚀 开始极速重写"):
    api_key = st.secrets.get("DEEPSEEK_API_KEY")
    if target_url and api_key:
        raw_text = get_article_content(target_url)
        if raw_text:
            full_content = ""
            placeholder = st.empty()
            response = stream_ai_rewrite(raw_text, api_key)
            for line in response.iter_lines():
                if line:
                    chunk = line.decode('utf-8').removeprefix('data: ')
                    if chunk == '[DONE]': break
                    try:
                        data = json.loads(chunk)
                        full_content += data['choices'][0]['delta'].get('content', '')
                        placeholder.markdown(safety_filter(full_content) + "▌")
                    except: continue
            
            final_text = safety_filter(full_content)
            placeholder.empty()

            # --- A. 纯文本区 (顺序第一) ---
            st.subheader("📋 1. 纯文本格式")
            st.markdown(f'<div class="result-box">{final_text}</div>', unsafe_allow_html=True)
            
            txt_safe = final_text.replace('`', '\\`').replace('$', '\\$')
            components.html(f"""
                <button onclick="copyTxt()" style="width:100%;height:45px;background:#07c160;color:white;border:none;border-radius:8px;font-weight:bold;cursor:pointer;font-size:18px;">📋 一键复制纯文本</button>
                <script>
                function copyTxt() {{
                    const el = document.createElement('textarea');
                    el.value = `{txt_safe}`;
                    document.body.appendChild(el); el.select();
                    document.execCommand('copy');
                    document.body.removeChild(el);
                    alert('纯文本复制成功！');
                }}
                </script>
            """, height=60)

            st.divider()

            # --- B. Markdown 预览区 (顺序第二) ---
            st.subheader("🎨 2. Markdown 预览 (18号/17号)")
            
            # 【重要】在这里明确定义变量，解决 NameError
            final_html = markdown.markdown(final_text) 
            
            st.markdown(f"""
                <div id="md-view" class="result-box" style="background:#ffffff !important;">
                    <style>
                        #md-view {{ font-family: "SimSun", serif !important; font-size: 17px !important; color: #000000 !important; }}
                        #md-view h2 {{ font-size: 18px !important; font-family: "SimHei", sans-serif !important; font-weight: bold !important; color: #000000 !important; margin-top: 30px; border-left: 5px solid #07c160; padding-left: 10px; }}
                        #md-view p {{ margin-bottom: 20px; color: #000000 !important; }}
                    </style>
                    {final_html}
                </div>
            """, unsafe_allow_html=True)
            
            components.html("""
                <button onclick="copyMd()" style="width:100%;height:45px;background:#07c160;color:white;border:none;border-radius:8px;font-weight:bold;cursor:pointer;font-size:18px;">📋 一键复制 Markdown 成品</button>
                <script>
                function copyMd() {
                    const range = document.createRange();
                    range.selectNode(parent.document.getElementById('md-view'));
                    window.getSelection().removeAllRanges();
                    window.getSelection().addRange(range);
                    document.execCommand('copy');
                    alert('Markdown 预览已复制，可贴入公众号！');
                }
                </script>
            """, height=60)
        else: st.error("内容抓取失败")
