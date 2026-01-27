import streamlit as st
import requests
import json
from bs4 import BeautifulSoup
import markdown
import streamlit.components.v1 as components
import re

# --- 1. 兴洪专属视觉皮肤 (微信绿主题 + 高对比度纯黑字) ---
st.set_page_config(page_title="高级原创二创助手", layout="centered")

st.markdown("""
    <style>
    /* 强制背景为白色，文字为纯黑，解决看得清的问题 */
    .stApp { background-color: #ffffff; color: #000000 !important; }
    h1 { color: #07c160 !important; font-family: "Microsoft YaHei"; text-align: center; font-weight: bold; }
    
    /* 极简绿色输入框 */
    .stTextInput > div > div {
        border: 2px solid #07c160 !important;
        background-color: #ffffff !important;
        border-radius: 8px !important;
    }
    .stTextInput input { color: #000000 !important; }

    /* 微信绿按钮 */
    div.stButton > button {
        background-color: #07c160 !important;
        color: white !important;
        border-radius: 8px;
        height: 50px;
        font-weight: bold;
        border: none;
    }

    /* 固定页脚与二维码交互 */
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: white; padding: 12px 0; border-top: 2px solid #07c160;
        z-index: 999; display: flex; justify-content: center; align-items: center; gap: 20px;
        font-size: 14px; color: #333;
    }
    .qr-item { color: #07c160; font-weight: bold; cursor: pointer; position: relative; }
    .qr-box {
        display: none; position: absolute; bottom: 45px; left: 50%;
        transform: translateX(-50%); width: 180px; background: white;
        padding: 10px; border: 2px solid #07c160; border-radius: 10px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    }
    .qr-item:hover .qr-box { display: block; }
    </style>

    <div class="footer">
        <span>© 2026 <b>@兴洪</b> 版权所有</span>
        <span>|</span>
        <span>WX/QQ: 3326843406</span>
        <div class="qr-item">
            📗 微信加我
            <div class="qr-box">
                <img src="https://raw.githubusercontent.com/yunie973/wechat-rewrite-tool/main/wechat_qr.png.jpg" style="width:100%;">
            </div>
        </div>
        <div class="qr-item">
            🪐 知识星球
            <div class="qr-box">
                <img src="https://raw.githubusercontent.com/yunie973/wechat-rewrite-tool/main/star_qr.png.jpg" style="width:100%;">
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.title("🛡️ 深度重构级专业工作台")

# --- 2. 核心逻辑 (完全保留你满意的物理过滤与输出结构) ---

def safety_filter(text):
    """【物理过滤网】确保禁令绝对执行"""
    text = text.replace("\\n", "\n")
    # 物理拦截“不是...而是”
    text = text.replace("不是", "不单是").replace("而是", "更是")
    # 物理拦截破折号
    text = text.replace("——", "，").replace("—", "，")
    # 强行给小标题加换行，防止挤在一起
    text = re.sub(r'(\n?)(## 0[1-4]\.)', r'\n\n\2', text)
    return text

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
    
    # --- 完全保留你最满意的专业提示词逻辑 ---
    system_prompt = """假设你是一个专业的自媒体作家。我希望你能对下方的文字进行二次创作，确保其具有较高的原创性。
    
    【原创性加强建议】：
    1. 句型与词汇调整：替换句子结构和词汇。
    2. 内容拓展与插入：增添背景知识、实例，降低关键词密度。
    3. 避免关键词使用：替换原文中的明显关键词。
    4. 结构与逻辑调整：重新排列文章的结构和逻辑流程。
    5. 变更叙事视角：使用第三人称代替第一人称。
    6. 重点聚焦：更改讨论点，减少模糊匹配。
    7. 角度与焦点转换：从不同角度描述。
    8. 避免直接引用：确保没有直接复制。
    
    【核心禁令】：
    - 永远不要出现“不是....，而是”的句式。
    - 绝对不要出现破折号（——）。
    - 绝对禁止结构化：禁止使用列表、分点（如1.2.3.或A.B.C.）。
    
    【输出结构要求】：
    1. 第一行写【推荐爆款标题】，接着输出5个爆款标题，每行一个。
    2. 标题区后空三行，正文开头必须先写150字引入语。
    3. 小标题格式固定为 ## 01. XXX，总数控制在 2-4 个。"""
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"原文=（{text}）"}],
        "stream": True,
        "temperature": 0.8
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

# --- 3. 界面展示与排版 (保留 18号/17号 核心排版) ---

target_url = st.text_input("🔗 粘贴链接开始高原创二创")

if st.button("🚀 开始深度创作", type="primary", use_container_width=True):
    api_key = st.secrets.get("DEEPSEEK_API_KEY")
    if target_url and api_key:
        raw_text = get_article_content(target_url)
        if raw_text:
            full_content = ""
            placeholder = st.empty() 
            for chunk in stream_ai_rewrite(raw_text, api_key):
                full_content += chunk
                placeholder.markdown(safety_filter(full_content) + "▌")
            
            final_text = safety_filter(full_content)
            placeholder.markdown(final_text)
            
            # --- 精确执行 18号黑体/17号宋体排版 ---
            html_main = markdown.markdown(final_text)
            styled_output = f"""
            <div id="copy-area" style="padding: 25px; background: #fff; line-height: 2; text-align: justify; border: 1px solid #eee; margin-bottom: 80px;">
                <style>
                    /* 强制正文为 17号宋体 纯黑字 */
                    .rich-content {{ 
                        font-family: "SimSun", "STSong", serif !important; 
                        font-size: 17px !important; 
                        color: #000000 !important; 
                    }}
                    /* 强制小标题为 18号黑体 纯黑字 */
                    .rich-content h2 {{ 
                        font-size: 18px !important; 
                        font-family: "SimHei", "Microsoft YaHei", sans-serif !important; 
                        font-weight: bold !important; 
                        color: #000000 !important; 
                        margin: 30px 0 15px 0;
                        border-left: 5px solid #07c160;
                        padding-left: 10px;
                    }}
                    .rich-content p {{ margin-bottom: 20px; }}
                </style>
                <div class="rich-content">{html_main}</div>
            </div>
            """
            st.subheader("🟢 最终预览")
            st.markdown(styled_output, unsafe_allow_html=True)
            
            # 一键复制成品
            copy_js = f"""
            <div style="text-align:center; margin-top:10px;">
                <button id="c-btn" style="background:#07c160; color:white; border:none; padding:15px; font-size:18px; border-radius:8px; width:100%; cursor:pointer;">📋 一键复制成品 (保留18号/17号格式)</button>
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
            }};
            </script>
            """
            components.html(copy_js, height=100)
        else: st.error("内容抓取失败")
