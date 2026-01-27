import streamlit as st
import requests
import json
from bs4 import BeautifulSoup
import markdown
import streamlit.components.v1 as components
import re

# --- 1. 界面定制 (微信绿主题 + 纯黑字 + 浅灰白背景) ---
st.set_page_config(page_title="高级原创二创助手", layout="centered")

st.markdown("""
    <style>
    /* 全局颜色锁死：纯白背景，纯黑字体 */
    .stApp { background-color: #ffffff; color: #000000 !important; }
    h1 { color: #07c160 !important; font-family: "Microsoft YaHei"; text-align: center; font-weight: bold; }
    
    /* 输入框加固 */
    .stTextInput input { color: #000000 !important; font-weight: bold !important; }
    .stTextInput > div > div { border: 2px solid #07c160 !important; }

    /* 输出容器样式：浅灰色背景装饰 */
    .output-box {
        background-color: #f7f7f7 !important;
        color: #000000 !important;
        padding: 25px;
        border-radius: 8px;
        border: 1px solid #07c160;
        font-family: "SimSun", "宋体", serif;
        font-size: 17px;
        line-height: 2;
        white-space: pre-wrap;
        margin-bottom: 10px;
    }

    /* 微信绿按钮 */
    .copy-btn {
        width: 100%; height: 50px; background-color: #07c160; color: white !important;
        border: none; border-radius: 8px; cursor: pointer; font-size: 18px;
        font-weight: bold; margin-bottom: 40px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ 深度重构级专业工作台")

# --- 2. 核心算法：100% 遵从你的写作与排版指令 ---

def safety_filter(text):
    """【物理过滤器】执行禁令，强制执行标题换行逻辑"""
    text = text.replace("\\n", "\n")
    # 物理拦截禁令
    text = text.replace("不是", "不单是").replace("而是", "更是").replace("——", "，").replace("—", "，")
    
    # 【爆款标题换行】确保每个标题单独一行
    text = re.sub(r'(【推荐爆款标题】)', r'\1\n', text)
    text = re.sub(r'([1-5]\. )', r'\n\1', text)
    
    # 【小标题换行】## 01. 这种格式前后必须有空行
    text = re.sub(r'(\n?)(## 0[1-4]\.)', r'\n\n\2\n', text)
    return text.strip()

# (stream_ai_rewrite 与 get_article_content 保持你满意的原始指令)

# --- 3. 业务展示区：纯文本在前，Markdown在后 ---

target_url = st.text_input("🔗 粘贴链接开始深度重构")

if st.button("🚀 开始极速生成"):
    api_key = st.secrets.get("DEEPSEEK_API_KEY")
    if target_url and api_key:
        # raw_text = get_article_content(target_url)
        # 此处省略抓取和 AI 循环代码，确保使用你原本能跑通的流式逻辑
        
        final_text = safety_filter("这里是生成的完整文本内容...") 

        # --- 第一部分：纯文本显示与复制 ---
        st.subheader("📋 1. 纯文本格式")
        st.markdown(f'<div class="output-box">{final_text}</div>', unsafe_allow_html=True)
        
        # 纯文本复制脚本：通过 JS 变量注入，解决 iframe 权限问题
        components.html(f"""
            <button id="t-btn" style="width:100%; height:50px; background:#07c160; color:white; border:none; border-radius:8px; font-weight:bold; cursor:pointer; font-size:18px;">📋 一键复制纯文本</button>
            <script>
            document.getElementById('t-btn').onclick = function() {{
                const text = `{final_text.replace('`', '\\`').replace('$', '\\$')}`;
                const el = document.createElement('textarea');
                el.value = text;
                document.body.appendChild(el);
                el.select();
                document.execCommand('copy');
                document.body.removeChild(el);
                this.innerText = '✅ 纯文本已复制';
            }}
            </script>
        """, height=70)

        st.divider()

        # --- 第二部分：Markdown 预览与复制 (带 18/17号排版) ---
        st.subheader("🎨 2. Markdown 预览")
        html_rendered = markdown.markdown(final_text)
        st.markdown(f"""
            <div id="md-render" class="output-box" style="background:#ffffff !important;">
                <style>
                    #md-render {{ font-family: "SimSun", serif !important; font-size: 17px !important; color: #000000 !important; }}
                    #md-render h2 {{ font-size: 18px !important; font-family: "SimHei", sans-serif !important; font-weight: bold !important; color: #000000 !important; margin-top: 30px; }}
                    #md-render p {{ margin-bottom: 20px; color: #000000 !important; }}
                </style>
                {html_rendered}
            </div>
        """, unsafe_allow_html=True)
        
        # 富文本复制脚本：通过 Range 选中 DOM 节点，保留颜色和字号
        components.html("""
            <button id="m-btn" style="width:100%; height:50px; background:#07c160; color:white; border:none; border-radius:8px; font-weight:bold; cursor:pointer; font-size:18px;">📋 一键复制 Markdown 成品</button>
            <script>
            document.getElementById('m-btn').onclick = function() {
                const area = parent.document.getElementById('md-render');
                const range = document.createRange();
                range.selectNode(area);
                const sel = window.getSelection();
                sel.removeAllRanges(); sel.addRange(range);
                document.execCommand('copy');
                this.innerText = '✅ 成品已复制，可直接贴入公众号';
                sel.removeAllRanges();
            };
            </script>
        """, height=70)
