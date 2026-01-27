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
    /* 强制全局背景白色，所有文字纯黑 */
    .stApp { background-color: #ffffff; color: #000000 !important; }
    h1 { color: #07c160 !important; font-family: "Microsoft YaHei"; text-align: center; font-weight: bold; }
    
    /* 输入框加固：文字纯黑 */
    .stTextInput input { color: #000000 !important; font-weight: bold !important; }
    .stTextInput > div > div { border: 2px solid #07c160 !important; }

    /* 微信绿按钮 */
    div.stButton > button { background-color: #07c160 !important; color: white !important; border-radius: 8px; height: 50px; font-weight: bold; width: 100%; border: none; }

    /* 结果容器：灰底纯黑字，保留所有换行 */
    .result-container {
        background-color: #f7f7f7 !important;
        color: #000000 !important;
        padding: 30px;
        border-radius: 8px;
        border: 1px solid #07c160;
        font-family: "SimSun", serif;
        font-size: 17px;
        line-height: 2;
        white-space: pre-wrap; /* 关键：保留 AI 吐出的所有换行 */
        text-align: justify;
    }

    /* 页脚 */
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: white; padding: 12px 0; border-top: 2px solid #07c160;
        z-index: 999; display: flex; justify-content: center; align-items: center; gap: 20px;
    }
    .qr-item { color: #07c160; font-weight: bold; cursor: pointer; position: relative; }
    .qr-box {
        display: none; position: absolute; bottom: 45px; left: 50%;
        transform: translateX(-50%); width: 180px; background: white;
        padding: 10px; border: 2px solid #07c160; border-radius: 10px;
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

# --- 2. 核心函数 ---

def get_article_content(url):
    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X)"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        content_div = soup.find('div', id='js_content')
        return content_div.get_text(separator='\n', strip=True) if content_div else None
    except: return None

def safety_filter(text):
    """【精准过滤器】保留标点，只拦截禁令，强制换行"""
    # 1. 修复换行符显示错误
    text = text.replace("\\n", "\n")
    # 2. 绝对执行禁令句式拦截
    text = text.replace("不是", "不单是").replace("而是", "更是").replace("——", "，").replace("—", "，")
    
    # 3. 【换行修复】确保爆款标题和正文标题前后有空行
    # 在 1. 2. 3. 这种标题前强制加换行
    text = re.sub(r'([1-5]\. )', r'\n\1', text)
    # 在 ## 01. 这种小标题前强制加双换行
    text = re.sub(r'(\n?)(## 0[1-4]\.)', r'\n\n\2', text)
    return text

def stream_ai_rewrite(text, api_key):
    url = "https://api.deepseek.com/chat/completions"
    # 完全执行你给的所有指令细节
    system_prompt = """假设你是一个专业的自媒体作家。对下文进行二创。
    建议：句型词汇调整、内容拓展、避免关键词、结构逻辑调整、视角切换、角度转换。
    禁令：严禁“不是...而是”，严禁破折号，严禁结构化。
    结构：
    1. 第一行写【推荐爆款标题】，接着输出5个爆款标题，每行一个。
    2. 标题区后空三行。
    3. 正文开头写150字引入语。
    4. 小标题格式 ## 01. XXX，总数 2-4 个。"""
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"原文=（{text}）"}],
        "stream": True, "temperature": 0.8
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    return requests.post(url, headers=headers, json=payload, stream=True)

# --- 3. 业务逻辑 ---

target_url = st.text_input("🔗 粘贴链接开始高原创二创")

if st.button("🚀 开始深度创作"):
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
                        # 实时流式显示，保持换行
                        placeholder.markdown(safety_filter(full_content) + "▌")
                    except: continue
            
            final_text = safety_filter(full_content)
            placeholder.empty()

            # --- 最终排版：18号黑体/17号宋体/纯黑字 ---
            html_main = markdown.markdown(final_text)
            styled_output = f"""
            <div id="copy-area" class="result-container">
                <style>
                    /* 强制 17号宋体 正文 */
                    #copy-area {{ font-family: "SimSun", serif !important; font-size: 17px !important; color: #000000 !important; }}
                    /* 强制 18号黑体 标题 */
                    #copy-area h2 {{ font-size: 18px !important; font-family: "SimHei", sans-serif !important; font-weight: bold !important; color: #000000 !important; margin: 30px 0 15px 0; }}
                    #copy-area p {{ margin-bottom: 20px; }}
                </style>
                {html_main}
            </div>
            """
            st.markdown(styled_output, unsafe_allow_html=True)
            
            # --- 一键复制脚本 (修复版) ---
            components.html(f"""
                <button id="c-btn" style="width:100%; height:50px; background:#07c160; color:white; border:none; border-radius:8px; font-weight:bold; font-size:18px; cursor:pointer;">📋 一键复制成品</button>
                <script>
                document.getElementById('c-btn').onclick = function() {{
                    const area = parent.document.getElementById('copy-area');
                    const range = document.createRange();
                    range.selectNode(area);
                    const sel = window.getSelection();
                    sel.removeAllRanges(); sel.addRange(range);
                    document.execCommand('copy');
                    this.innerText = '✅ 复制成功';
                }}
                </script>
            """, height=80)
        else:
            st.error("内容抓取失败")
