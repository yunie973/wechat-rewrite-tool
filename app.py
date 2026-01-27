import streamlit as st
import requests
import json
from bs4 import BeautifulSoup
import markdown
import streamlit.components.v1 as components
import re

# --- 1. 界面定制 (微信绿主题 + 浅底纯黑字) ---
st.set_page_config(page_title="23456666.xyz 兴洪专业版", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    h1 { color: #07c160 !important; font-family: "Microsoft YaHei"; text-align: center; font-weight: bold; }
    
    /* 绿色极简输入框 */
    .stTextInput > div > div {
        border: 2px solid #07c160 !important;
        background-color: #ffffff !important;
        border-radius: 8px !important;
    }
    .stTextInput input { color: #000000 !important; font-weight: bold; }

    /* 输出区：浅灰背景，纯黑字体，高对比度 */
    .black-text-box {
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

    /* 一键复制按钮样式 */
    .copy-btn {
        width: 100%; height: 45px; background: #07c160; color: white !important;
        border: none; border-radius: 8px; cursor: pointer; font-weight: bold;
        font-size: 16px; margin-bottom: 40px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ 兴洪·深度二创全限制版")

# --- 2. 核心算法：全套原创性加强建议 & 禁令强制执行 ---

def hard_filter(text):
    """物理拦截：强制执行“三不”禁令 & 标题换行"""
    # 1. 禁令：彻底封杀“不是...而是”句式
    text = text.replace("不是", "不单是").replace("而是", "更是")
    # 2. 禁令：彻底封杀破折号
    text = text.replace("——", "，").replace("—", "，")
    # 3. 禁令：彻底封杀结构化符号（不要符号分点）
    for char in ["*", "●", "○", "■", "➢", "- "]:
        text = text.replace(char, "")
    # 4. 强制要求：五个小标题必须换行
    # 匹配“01.”或“1.”或“第一个小标题”这类模式，在前面强制加两个回车
    text = re.sub(r'(\n?)(第[一二三四五]个小标题|0[1-5]\.|[1-5]\. )', r'\n\n\2', text)
    return text.strip()

def stream_ai_rewrite(text, api_key):
    url = "https://api.deepseek.com/chat/completions"
    
    # 完整植入你提供的全套专业自媒体作家约束
    system_prompt = """假设你是一个专业的自媒体作家。请对下方的文字进行二次创作，参考以下原创性加强建议:
    - 句型与词汇调整：替换句子结构和词汇。
    - 内容拓展与插入：增添背景知识、实例，丰富内容。
    - 避免关键词使用：替换原文中的明显关键词。
    - 结构与逻辑调整：重新排列文章结构和逻辑。
    - 变更叙事视角：使用第三人称代替第一人称。
    - 重点聚焦：更改主要讨论点。
    - 关键词分析：调整或稀释高度相似的关键词。
    - 角度与焦点转换：从不同角度描述相同主题。
    - 避免直接引用：确保没有直接复制原文内容。
    - 综合抄袭检测反馈：进行有针对性的调整。

    【核心硬约束】：
    - 必须包含 5 个小标题。
    - 永远不要出现“不是....，而是”的句式。
    - 绝对不要出现破折号（——）。
    - 不要结构化：禁止使用任何列表符号、分点符号。
    - 依照上述建议，根据原文开始你的创作。"""
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"原文=（{text}）"}],
        "stream": True,
        "temperature": 0.8
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    return requests.post(url, headers=headers, json=payload, stream=True, timeout=15)

# (get_article_content 函数保持不变)

# --- 3. 业务展示区：纯文本在前，Markdown在后 ---

target_url = st.text_input("🔗 粘贴链接，严格执行禁令生成")

if st.button("🚀 开始深度原创重写", type="primary", use_container_width=True):
    api_key = st.secrets.get("DEEPSEEK_API_KEY")
    if target_url and api_key:
        # 抓取逻辑...
        raw_text = "此处模拟抓取的内容" # 实际请保留你的 get_article_content 调用
        
        full_content = ""
        placeholder = st.empty()
        # 这里进行 AI 请求并流式展示...
        
        final_text = hard_filter("这里是模拟生成的包含五个小标题的内容...") 

        # --- 顺序一：纯文本区 (灰底纯黑字) ---
        st.subheader("📋 1. 纯文本格式 (纯黑字)")
        st.markdown(f'<div class="black-text-box">{final_text}</div>', unsafe_allow_html=True)
        components.html(f"""
            <button onclick="navigator.clipboard.writeText(`{final_text}`)" class="copy-btn">一键复制纯文本</button>
        """, height=60)

        st.divider()

        # --- 顺序二：Markdown 预览区 (灰底纯黑字) ---
        st.subheader("🎨 2. Markdown 预览 (17号宋体)")
        html_md = markdown.markdown(final_text)
        st.markdown(f'<div id="md-v" class="black-text-box">{html_md}</div>', unsafe_allow_html=True)
        components.html("""
            <button onclick="copyRich()" class="copy-btn">一键复制预览格式</button>
            <script>
            function copyRich() {
                const range = document.createRange();
                range.selectNode(parent.document.getElementById('md-v'));
                window.getSelection().removeAllRanges();
                window.getSelection().addRange(range);
                document.execCommand('copy');
                alert('已复制带格式预览！');
            }
            </script>
        """, height=60)
