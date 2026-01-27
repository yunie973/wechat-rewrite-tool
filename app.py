import streamlit as st
import requests
import json
from bs4 import BeautifulSoup
import markdown
import streamlit.components.v1 as components

# --- 1. 兴洪专属视觉皮肤 (微信绿主题) ---
st.set_page_config(page_title="23456666.xyz 兴洪专业版", layout="centered")

st.markdown("""
    <style>
    /* 整体背景与文字颜色 */
    .stApp { background-color: #f7fcf9; }
    h1 { color: #07c160 !important; font-family: "Microsoft YaHei", sans-serif; text-align: center; font-weight: 800; }
    
    /* 微信绿按钮定制 */
    div.stButton > button {
        background-color: #07c160 !important;
        color: white !important;
        border-radius: 12px;
        height: 52px;
        font-size: 18px;
        font-weight: bold;
        border: none;
        box-shadow: 0 4px 12px rgba(7, 193, 96, 0.2);
    }
    
    /* 输入框边框微信绿 */
    .stTextInput div div { border-color: #07c160 !important; }

    /* 固定页脚与二维码交互 */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: white;
        color: #333;
        text-align: center;
        padding: 15px 0;
        font-size: 14px;
        border-top: 2px solid #07c160;
        z-index: 999;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 20px;
    }
    .qr-item { position: relative; color: #07c160; font-weight: bold; cursor: pointer; }
    .qr-box {
        display: none;
        position: absolute;
        bottom: 45px;
        left: 50%;
        transform: translateX(-50%);
        width: 200px;
        background: white;
        padding: 10px;
        border: 2px solid #07c160;
        border-radius: 10px;
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
                <p style="margin:5px 0 0 0; font-size:12px;">扫一扫，与我联系</p>
            </div>
        </div>
        <div class="qr-item">
            🪐 知识星球
            <div class="qr-box">
                <img src="https://raw.githubusercontent.com/yunie973/wechat-rewrite-tool/main/star_qr.png.jpg" style="width:100%;">
                <p style="margin:5px 0 0 0; font-size:12px;">免费领取进阶干货</p>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.title("🛡️ 兴洪·自媒体深度二创工作台")

# --- 2. 核心算法：全套原创逻辑与硬核过滤器 ---

def hard_filter(text):
    """物理拦截：强制抹除违禁词汇与符号"""
    # 彻底封杀“不是...而是”句式
    text = text.replace("不是", "不单是").replace("而是", "更是")
    # 彻底封杀破折号
    text = text.replace("——", "，").replace("—", "，")
    # 彻底封杀结构化符号 (防止AI偷懒分点)
    for char in ["*", "●", "○", "■", "➢", "- ", "1.", "2.", "3.", "4.", "5."]:
        text = text.replace(char, "")
    return text

def stream_ai_rewrite(text, api_key):
    url = "https://api.deepseek.com/chat/completions"
    
    # 注入用户提供的全套自媒体作家提示词
    system_prompt = """假设你是一个专业的自媒体作家。我希望你能对下方的文字进行二次创作，确保其具有较高的原创性。
    请严格参考以下原创性加强建议:
    1. 句型与词汇调整:通过替换原文中的句子结构和词汇以传达同样的思想。
    2. 内容拓展与插入:增添背景知识、实例，以丰富文章内容，并降低关键词密度。
    3. 避免关键词使用:避免使用原文中的明显关键词或用其它词汇替换。
    4. 结构与逻辑调整:重新排列文章的结构和逻辑流程，确保与原文的相似度降低。
    5. 变更叙事视角:在某些情境下，选择使用第三人称代替第一人称以降低风格相似性。
    6. 重点聚焦:更改文章的主要讨论点，以减少模糊匹配的风险。
    7. 关键词分析:对比原文和重写版本，调整或稀释高度相似的关键词。
    8. 角度与焦点转换:从不同的角度描述相同的主题，以减少内容相似性。
    9. 避免直接引用:确保没有直接复制原文或其他已知来源的内容。
    10. 综合抄袭检测反馈:进行有针对性的调整。

    【绝对红线禁令】：
    - 永远不要出现“不是....，而是”的句式。
    - 绝对不要出现破折号（——）。
    - 绝对不要结构化：禁止使用任何列表、分点（如1.2.3.或●）、禁止使用小标题。
    - 必须保持全文为流畅、自然的段落叙事。"""
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"原文=（{text}）"}],
        "stream": True,
        "temperature": 0.85
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

# --- 3. 业务逻辑 (抓取与展示) ---
def get_article_content(url):
    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X)"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        content_div = soup.find('div', id='js_content')
        return content_div.get_text(separator='\n', strip=True) if content_div else None
    except: return None

target_url = st.text_input("🔗 粘贴文章链接，开始高原创重写")

if st.button("🚀 极速生成兴洪重写版", type="primary", use_container_width=True):
    api_key = st.secrets.get("DEEPSEEK_API_KEY")
    if target_url and api_key:
        raw_text = get_article_content(target_url)
        if raw_text:
            full_content = ""
            placeholder = st.empty() 
            for chunk in stream_ai_rewrite(raw_text, api_key):
                full_content += chunk
                # 实时物理过滤
                placeholder.markdown(hard_filter(full_content) + "▌")
            
            final_text = hard_filter(full_content)
            placeholder.markdown(final_text)
            
            # 渲染预览区 (17号宋体)
            styled_output = f"""
            <div id="copy-area" style="padding:20px; background:white; line-height:1.8; font-family:'SimSun'; font-size:17px; color:#333; border-left:5px solid #07c160;">
                {markdown.markdown(final_text)}
            </div>
            """
            st.subheader("🟢 最终预览 (已抹除所有禁忌符号)")
            st.markdown(styled_output, unsafe_allow_html=True)
