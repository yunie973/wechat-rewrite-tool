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
    .stTextInput input { color: #000000 !important; }
    div.stButton > button { background-color: #07c160 !important; color: white !important; border-radius: 8px; height: 50px; font-weight: bold; border: none; width: 100%; }
    
    /* 页脚与二维码交互 */
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: white; padding: 12px 0; border-top: 2px solid #07c160;
        z-index: 999; display: flex; justify-content: center; align-items: center; gap: 20px; font-size: 14px;
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
        <span style="color:#333;">© 2026 <b>@兴洪</b> 版权所有 | WX/QQ: 3326843406</span>
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
    """【物理拦截网】严格执行禁令并强制换行"""
    text = text.replace("\\n", "\n")
    # 拦截禁令
    text = text.replace("不是", "不单是").replace("而是", "更是").replace("——", "，").replace("—", "，")
    # 爆款标题换行
    text = re.sub(r'(【推荐爆款标题】)', r'\1\n', text)
    # 小标题换行
    text = re.sub(r'(\n?)(## 0[1-4]\.)', r'\n\n\2', text)
    return text

def stream_ai_rewrite(text, api_key):
    url = "https://api.deepseek.com/chat/completions"
    system_prompt = """假设你是一个专业的自媒体作家。我希望你能对下方的文字进行二次创作，确保其具有较高的原创性。
    【原创性加强建议】：句型词汇调整、内容拓展、避免关键词、结构逻辑调整、视角切换、重点聚焦、角度转换、避免直接引用。
    【核心禁令】：
    - 永远不要出现“不是....，而是”的句式。
    - 绝对不要出现破折号（——）。
    - 绝对禁止结构化：禁止使用列表、分点（如1.2.3.或A.B.C.），保持段落连贯性。
    【输出结构】：
    1. 第一行写【推荐爆款标题】，接着输出5个爆款标题，每行一个。
    2. 标题区后空三行，正文开头必须先写150字引入语。
    3. 小标题格式固定为 ## 01. XXX，总数控制在 2-4 个。"""
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"原文=（{text}）"}],
        "stream": True, "temperature": 0.8
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    return requests.post(url, headers=headers, json=payload, stream=True)

# --- 3. 执行逻辑 ---

target_url = st.text_input("🔗 粘贴链接开始高原创二创")

if st.button("🚀 开始深度创作"):
    api_key = st.secrets.get("DEEPSEEK_API_KEY")
    if not api_key:
        st.error("请先在 Streamlit Secrets 中配置 DEEPSEEK_API_KEY")
    elif target_url:
        raw_text = get_article_content(target_url)
        if raw_text:
            full_content = ""
            placeholder = st.empty()
            
            # --- 真正的数据流循环 ---
            response = stream_ai_rewrite(raw_text, api_key)
            for line in response.iter_lines():
                if line:
                    chunk = line.decode('utf-8').removeprefix('data: ')
                    if chunk == '[DONE]': break
                    try:
                        data = json.loads(chunk)
                        full_content += data['choices'][0]['delta'].get('content', '')
                        # 实时显示过滤后的内容
                        placeholder.markdown(safety_filter(full_content) + "▌")
                    except: continue
            
            final_text = safety_filter(full_content)
            placeholder.empty() # 清除流式占位

            # --- 最终 18/17号 排版 ---
            html_main = markdown.markdown(final_text)
            styled_output = f"""
            <div id="copy-area" style="padding: 25px; background: #fff; line-height: 2; text-align: justify; border-left: 8px solid #07c160; margin-bottom: 80px;">
                <style>
                    .rich-content {{ font-family: "SimSun", serif !important; font-size: 17px !important; color: #000000 !important; }}
                    .rich-content h2 {{ font-size: 18px !important; font-family: "SimHei", sans-serif !important; font-weight: bold !important; color: #000000 !important; margin: 30px 0 15px 0; }}
                    .rich-content p {{ margin-bottom: 20px; color: #000 !important; }}
                </style>
                <div class="rich-content">{html_main}</div>
            </div>
            """
            st.markdown(styled_output, unsafe_allow_html=True)
            
            # 复制脚本
            components.html(f"""
                <button id="c-btn" style="width:100%; height:50px; background:#07c160; color:white; border:none; border-radius:8px; font-weight:bold; font-size:18px; cursor:pointer;">📋 一键复制成品</button>
                <script>
                document.getElementById('c-btn').onclick = function() {{
                    const area = parent.document.getElementById('copy-area');
                    const range = document.createRange();
                    range.selectNode(area);
                    window.getSelection().removeAllRanges();
                    window.getSelection().addRange(range);
                    document.execCommand('copy');
                    this.innerText = '✅ 复制成功';
                }}
                </script>
            """, height=80)
        else:
            st.error("抓取失败，请检查链接是否为微信公众号文章")
