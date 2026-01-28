import streamlit as st
import requests
import json
from bs4 import BeautifulSoup
import markdown
import streamlit.components.v1 as components
import re

# --- 1. 视觉皮肤 (彻底锁死纯黑字，解决看不清的问题) ---
st.set_page_config(page_title="高级原创二创助手", layout="centered")

st.markdown("""
    <style>
    /* 全局背景强制白色，文字强制绝对纯黑 */
    .stApp { background-color: #ffffff; color: #000000 !important; }
    h1 { color: #07c160 !important; font-family: "Microsoft YaHei"; text-align: center; font-weight: 800; }
    
    /* 强制输入框内部文字也为纯黑 */
    .stTextInput input { color: #000000 !important; font-weight: bold !important; font-size: 16px !important; }
    .stTextInput > div > div { border: 2px solid #07c160 !important; }

    /* 输出容器：极浅灰色背景装饰，确保换行可见 */
    .result-box {
        background-color: #f6f6f6 !important;
        color: #000000 !important;
        padding: 30px;
        border-radius: 8px;
        border: 1px solid #07c160;
        font-family: 'SimSun', 'STSong', '宋体', serif;
        font-size: 17px;
        line-height: 2.2;
        white-space: pre-wrap; /* 强制保留 AI 生成的所有物理换行 */
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
    """【物理过滤器】锁死标题换行逻辑，杜绝挤在一起"""
    text = text.replace("\\n", "\n")
    # 强制执行拦截禁令
    text = text.replace("不是", "不单是").replace("而是", "更是").replace("——", "，").replace("—", "，")
    
    # 物理修正标题断行：给爆款标题和正文标题前后补位
    text = re.sub(r'(【推荐爆款标题】)', r'\1\n', text)
    text = re.sub(r'([1-5]\. )', r'\n\1', text)
    text = re.sub(r'(\n?)(## 0[1-4]\.)', r'\n\n\2', text)
    return text

def stream_ai_rewrite(text, api_key):
    url = "https://api.deepseek.com/chat/completions"
    # 完全采用你给的最满意的写作指令细节
    system_prompt = """假设你是一个专业的自媒体作家。对下文进行二创。
    【原创加强建议】：句型词汇调整、内容拓展、避免关键词、结构逻辑调整、视角切换、重点聚焦、角度转换、避免直接引用。
    【核心禁令】：
    - 永远不要出现“不是....，而是”的句式。
    - 绝对不要出现破折号（——）。
    - 绝对禁止结构化：禁止使用列表、分点（如1.2.3.或●），保持段落叙述的连贯性。
    【输出结构要求】：
    1. 第一行写【推荐爆款标题】，接着输出5个爆款标题，每行一个。
    2. 标题区后空三行。
    3. 正文开头必须先写150字引入语。
    4. 小标题格式固定为 ## 01. XXX，总数控制在 2-4 个。"""
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"原文=（{text}）"}],
        "stream": True, "temperature": 0.8
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    return requests.post(url, headers=headers, json=payload, stream=True)

# --- 3. 业务展示区：纯文本与预览并行 (修复 NameError) ---

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
            st.subheader("📋 1. 纯文本格式 (纯黑字)")
            st.markdown(f'<div class="result-box">{final_text}</div>', unsafe_allow_html=True)
            
            # 使用 JS 直接传递变量注入，解决复制失效
            txt_safe = final_text.replace('`', '\\`').replace('$', '\\$')
            components.html(f"""
                <button onclick="copyTxt()" style="width:100%;height:45px;background:#07c160;color:white;border:none;border-radius:8px;font-weight:bold;cursor:pointer;font-size:18px;">📋 一键复制纯文本</button>
                <script>
                function copyTxt() {{
                    const text = `{txt_safe}`;
                    const el = document.createElement('textarea');
                    el.value = text;
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
            
            # 【修复点】明确定义 html_output 变量，防止报错
            html_output = markdown.markdown(final_text) 
            
            st.markdown(f"""
                <div id="md-view" class="result-box" style="background:#ffffff !important;">
                    <style>
                        #md-view {{ font-family: "SimSun", serif !important; font-size: 17px !important; color: #000000 !important; }}
                        #md-view h2 {{ font-size: 18px !important; font-family: "SimHei", sans-serif !important; font-weight: bold !important; color: #000000 !important; margin-top: 30px; border-left: 5px solid #07c160; padding-left: 10px; }}
                        #md-view p {{ margin-bottom: 20px; color: #000000 !important; }}
                    </style>
                    {html_output}
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
                    alert('预览格式复制成功，可直接贴入公众号！');
                }
                </script>
            """, height=60)
        else: st.error("内容抓取失败")
