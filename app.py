import streamlit as st
import requests
import json
from bs4 import BeautifulSoup
import markdown
import streamlit.components.v1 as components
import re

# --- 1. 界面定制 (微信绿主题 + 浅色底纯黑字) ---
st.set_page_config(page_title="23456666.xyz 兴洪专业版", layout="centered")

st.markdown("""
    <style>
    /* 全局背景与标题 */
    .stApp { background-color: #ffffff; }
    h1 { color: #07c160 !important; font-family: "Microsoft YaHei"; text-align: center; }
    
    /* 极简绿色输入框 */
    .stTextInput > div > div {
        border: 2px solid #07c160 !important;
        background-color: #ffffff !important;
        border-radius: 8px !important;
    }

    /* 核心输出区：浅色背景，纯黑字体 */
    .light-container {
        background-color: #f9f9f9 !important; /* 极浅灰色背景 */
        color: #000000 !important;          /* 绝对纯黑字体 */
        padding: 25px;
        border-radius: 8px;
        font-family: 'SimSun', '宋体', serif;
        line-height: 1.8;
        margin-bottom: 15px;
        white-space: pre-wrap;              /* 保留换行 */
        border: 1px solid #eeeeee;
    }

    /* 微信绿按钮样式 */
    .copy-btn {
        width: 100%; height: 45px; background: #07c160; color: white; 
        border: none; border-radius: 8px; cursor: pointer; font-weight: bold;
        margin-bottom: 40px; font-size: 16px;
    }

    /* 页脚样式 */
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: white; text-align: center;
        padding: 12px 0; border-top: 2px solid #07c160; z-index: 999;
        display: flex; justify-content: center; gap: 20px; font-size: 14px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ 兴洪·深度二创工作台")

# --- 2. 核心算法 (硬核过滤 & 强制换行) ---

def hard_filter(text):
    """物理拦截禁令：强制抹除“不是...而是”与破折号，并修正标题换行"""
    text = text.replace("不是", "不单是").replace("而是", "更是")
    text = text.replace("——", "，").replace("—", "，")
    # 强制五个小标题换行：识别数字标题并在其前后插入换行符
    text = re.sub(r'(\n?)(第[一二三四五]个小标题|0[1-5]\.|[1-5]\. )', r'\n\n\2', text)
    return text.strip()

# (此处省略 stream_ai_rewrite 和 get_article_content，请保留你原有的完整代码)

# --- 3. 业务展示区 ---
target_url = st.text_input("🔗 粘贴链接，立即生成纯黑字二创内容")

if st.button("🚀 开始极速重写", type="primary", use_container_width=True):
    api_key = st.secrets.get("DEEPSEEK_API_KEY")
    if target_url and api_key:
        with st.status("内容生成中...", expanded=False):
            # 这里的抓取与流式逻辑请确保完整
            # raw_text = get_article_content(target_url)
            # 模拟生成的内容用于演示
            generated_text = "这里是AI生成的文章内容，包含五个小标题：\n01.第一个小标题内容...\n02.第二个小标题内容..." 
        
        final_text = hard_filter(generated_text)

        # --- A. 纯文本区 (顺序第一) ---
        st.subheader("📋 1. 纯文本格式 (纯黑字)")
        st.markdown(f'<div class="light-container">{final_text}</div>', unsafe_allow_html=True)
        
        # 纯文本复制脚本
        txt_js = f"""
            <button onclick="copyTxt()" class="copy-btn">一键复制纯文本</button>
            <script>
            function copyTxt() {{
                const el = document.createElement('textarea');
                el.value = `{final_text}`;
                document.body.appendChild(el);
                el.select();
                document.execCommand('copy');
                document.body.removeChild(el);
                alert('纯文本已成功复制！');
            }}
            </script>
        """
        components.html(txt_js, height=60)

        st.divider()

        # --- B. Markdown 预览区 (顺序第二) ---
        st.subheader("🎨 2. Markdown 预览 (纯黑字/17号宋体)")
        html_md = markdown.markdown(final_text)
        st.markdown(f'<div id="md-box" class="light-container" style="font-size:17px; color:#000000 !important;">{html_md}</div>', unsafe_allow_html=True)
        
        # Markdown 复制脚本
        md_js = """
            <button onclick="copyHtml()" class="copy-btn">一键复制 Markdown 预览</button>
            <script>
            function copyHtml() {
                const range = document.createRange();
                range.selectNode(parent.document.getElementById('md-box'));
                window.getSelection().removeAllRanges();
                window.getSelection().addRange(range);
                document.execCommand('copy');
                alert('带格式预览已复制！');
            }
            </script>
        """
        components.html(md_js, height=60)
