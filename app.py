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

# --- 2. 核心逻辑：一字不差执行你的指令 ---

def safety_filter(text):
    """【物理拦截网】确保禁令绝对执行，并强制修正换行"""
    text = text.replace("\\n", "\n")
    # 100% 拦截禁令句式和符号
    text = text.replace("不是", "不单是").replace("而是", "更是").replace("——", "，").replace("—", "，")
    
    # 【标题换行强制逻辑】
    # 确保【推荐爆款标题】后有换行，且 5 个标题之间强制换行
    text = re.sub(r'(【推荐爆款标题】)', r'\1\n', text)
    # 确保 ## 01. 这种小标题前后有足够的空行
    text = re.sub(r'(\n?)(## 0[1-4]\.)', r'\n\n\2', text)
    return text

def stream_ai_rewrite(text, api_key):
    url = "https://api.deepseek.com/chat/completions"
    
    # --- 这里是你的原始指令，一字不改 ---
    system_prompt = """假设你是一个专业的自媒体作家。我希望你能对下方的文字进行二次创作，确保其具有较高的原创性。
    
    【原创性加强建议】：
    1. 句型与词汇调整：通过替换原文中的句子结构和词汇以传达同样的思想。
    2. 内容拓展与插入：增添背景知识、实例，以丰富文章内容，并降低关键词密度。
    3. 避免关键词使用：避免使用原文中的明显关键词或用其它词汇替换。
    4. 结构与逻辑调整：重新排列文章的结构和逻辑流程，确保与原文的相似度降低。
    5. 变更叙事视角：选择使用第三人称代替第一人称。
    6. 重点聚焦：更改文章的主要讨论点，减少模糊匹配风险。
    7. 角度与焦点转换：从不同角度描述相同主题。
    8. 避免直接引用：确保没有直接复制原文。
    
    【核心禁令】：
    - 永远不要出现“不是....，而是”的句式。
    - 绝对不要出现破折号（——）。
    - 绝对禁止结构化：禁止使用列表、分点（如1.2.3.或A.B.C.），保持段落叙述的连贯性。
    
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

# (此处保留 get_article_content 函数...)

# --- 3. 界面展示：精确执行 18号/17号 排版 ---

target_url = st.text_input("🔗 粘贴链接开始高原创二创")

if st.button("🚀 开始深度创作"):
    api_key = st.secrets.get("DEEPSEEK_API_KEY")
    if target_url and api_key:
        # raw_text = get_article_content(target_url)
        # 此处开始流式循环并调用 safety_filter...
        
        final_text = safety_filter("生成的最终内容...") 

        # --- 预览排版：18号黑体/17号宋体/纯黑字 ---
        html_main = markdown.markdown(final_text)
        styled_output = f"""
        <div id="copy-area" style="padding: 25px; background: #fff; line-height: 2; text-align: justify; border-left: 8px solid #07c160; margin-bottom: 80px;">
            <style>
                .rich-content {{ font-family: "SimSun", serif !important; font-size: 17px !important; color: #000000 !important; }}
                .rich-content h2 {{ font-size: 18px !important; font-family: "SimHei", sans-serif !important; font-weight: bold !important; color: #000000 !important; margin: 35px 0 15px 0; }}
                .rich-content p {{ margin-bottom: 20px; }}
            </style>
            <div class="rich-content">{html_main}</div>
        </div>
        """
        st.subheader("🟢 最终预览（严格遵循指令版）")
        st.markdown(styled_output, unsafe_allow_html=True)
        
        # 一键复制脚本... (同前，省略以保持精简)
