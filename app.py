import streamlit as st
import requests
import json
from bs4 import BeautifulSoup
import markdown
import streamlit.components.v1 as components
import re

# --- 1. 界面视觉：微信绿主题 + 高对比度纯黑字 ---
st.set_page_config(page_title="高级原创二创助手", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #000000 !important; }
    h1 { color: #07c160 !important; font-family: "Microsoft YaHei"; text-align: center; font-weight: bold; }
    .stTextInput > div > div { border: 2px solid #07c160 !important; background-color: #ffffff !important; border-radius: 8px !important; }
    .stTextInput input { color: #000000 !important; font-weight: bold; }
    div.stButton > button { background-color: #07c160 !important; color: white !important; border-radius: 8px; height: 50px; font-weight: bold; border: none; width: 100%; }
    
    /* 灰底黑字容器样式 */
    .output-container {
        background-color: #f4f4f4 !important;
        color: #000000 !important;
        padding: 25px;
        border-radius: 8px;
        border: 1px solid #07c160;
        font-family: 'SimSun', serif;
        font-size: 17px;
        line-height: 2;
        white-space: pre-wrap;
        margin-bottom: 10px;
    }

    /* 页脚与二维码 */
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
        <span style="color:#333;">© 2026 <b>@兴洪</b> 版权所有</span>
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
    """【物理拦截网】确保禁令绝对执行，并强制换行"""
    text = text.replace("\\n", "\n")
    # 物理拦截禁令
    text = text.replace("不是", "不单是").replace("而是", "更是").replace("——", "，").replace("—", "，")
    # 强制爆款标题每行一个
    text = re.sub(r'([1-5]\. )', r'\n\1', text)
    # 强制小标题前后空行
    text = re.sub(r'(\n?)(## 0[1-4]\.)', r'\n\n\2', text)
    return text.strip()

def stream_ai_rewrite(text, api_key):
    url = "https://api.deepseek.com/chat/completions"
    system_prompt = """假设你是一个专业的自媒体作家。请参考建议对文字进行二创。
    【原创加强】：句型词汇调整、内容拓展、避免关键词、逻辑重排、视角切换等。
    【核心禁令】：严禁使用“不是...而是”，严禁出现破折号，严禁结构化。
    【输出结构】：
    1. 第一行写【推荐爆款标题】，接着输出5个爆款标题，每行一个。
    2. 标题区后空三行。
    3. 正文开头先写150字引入语。
    4. 小标题格式 ## 01. XXX，总数 2-4 个。"""
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"原文=（{text}）"}],
        "stream": True, "temperature": 0.8
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    return requests.post(url, headers=headers, json=payload, stream=True)

# --- 3. 业务逻辑 ---

target_url = st.text_input("🔗 粘贴链接开始深度二创")

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
            st.markdown(f'<div class="output-container">{final_text}</div>', unsafe_allow_html=True)
            
            # 使用 JS 直接将变量传递进按钮，解决复制失效问题
            txt_safe = final_text.replace('`', '\\`').replace('$', '\\$')
            components.html(f"""
                <button onclick="copyTxt()" style="width:100%;height:45px;background:#07c160;color:white;border:none;border-radius:8px;font-weight:bold;cursor:pointer;">点击复制纯文本</button>
                <script>
                function copyTxt() {{
                    const text = `{txt_safe}`;
                    const el = document.createElement('textarea');
                    el.value = text;
                    document.body.appendChild(el);
                    el.select();
                    document.execCommand('copy');
                    document.body.removeChild(el);
                    alert('纯文本复制成功！');
                }}
                </script>
            """, height=55)

            st.divider()

            # --- B. Markdown 预览区 (顺序第二) ---
            st.subheader("🎨 2. Markdown 预览 (18号/17号)")
            html_md = markdown.markdown(final_text)
            st.markdown(f"""
                <div id="md-box" class="output-container" style="background:#fff !important;">
                    <style>
                        #md-box h2 {{ font-size: 18px !important; font-family: "SimHei" !important; color: #000 !important; margin-top: 25px; }}
                        #md-box p {{ font-size: 17px !important; font-family: "SimSun" !important; color: #000 !important; }}
                    </style>
                    {html_md}
                </div>
            """, unsafe_allow_html=True)
            
            components.html("""
                <button onclick="copyMd()" style="width:100%;height:45px;background:#07c160;color:white;border:none;border-radius:8px;font-weight:bold;cursor:pointer;">点击复制 Markdown 预览</button>
                <script>
                function copyMd() {
                    const range = document.createRange();
                    range.selectNode(parent.document.getElementById('md-box'));
                    window.getSelection().removeAllRanges();
                    window.getSelection().addRange(range);
                    document.execCommand('copy');
                    alert('预览格式复制成功，可直接贴入公众号！');
                }
                </script>
            """, height=55)
        else:
            st.error("抓取失败")
