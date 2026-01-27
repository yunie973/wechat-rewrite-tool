import streamlit as st
import requests
import json
from bs4 import BeautifulSoup
import markdown
import streamlit.components.v1 as components
import time

# --- 1. 界面配置 (保持极简微信绿) ---
st.set_page_config(page_title="23456666.xyz 兴洪极速版", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #f7fcf9; }
    h1 { color: #07c160 !important; font-family: "Microsoft YaHei"; text-align: center; }
    
    /* 极简输入框 */
    .stTextInput > div > div {
        border: 2px solid #07c160 !important;
        background-color: #ffffff !important;
        border-radius: 10px !important;
        box-shadow: none !important;
    }

    /* 固定页脚 */
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: white; text-align: center;
        padding: 12px 0; border-top: 2px solid #07c160; z-index: 999;
        display: flex; justify-content: center; gap: 20px; font-size: 14px;
    }
    .qr-item { color: #07c160; font-weight: bold; cursor: pointer; position: relative; }
    .qr-box {
        display: none; position: absolute; bottom: 40px; left: 50%;
        transform: translateX(-50%); width: 180px; background: white;
        padding: 10px; border: 2px solid #07c160; border-radius: 10px;
    }
    .qr-item:hover .qr-box { display: block; }
    </style>

    <div class="footer">
        <span>© 2026 <b>@兴洪</b> 版权所有</span>
        <div class="qr-item">📗 微信加我 <div class="qr-box"><img src="https://raw.githubusercontent.com/yunie973/wechat-rewrite-tool/main/wechat_qr.png.jpg" style="width:100%;"></div></div>
        <div class="qr-item">🪐 知识星球 <div class="qr-box"><img src="https://raw.githubusercontent.com/yunie973/wechat-rewrite-tool/main/star_qr.png.jpg" style="width:100%;"></div></div>
    </div>
""", unsafe_allow_html=True)

st.title("🛡️ 兴洪·深度二创极速版")

# --- 2. 核心算法 (硬核过滤 & 极速流) ---

def hard_filter(text):
    """物理拦截：强制执行禁令"""
    text = text.replace("不是", "不单是").replace("而是", "更是")
    text = text.replace("——", "，").replace("—", "，")
    for char in ["*", "●", "○", "■", "➢", "- ", "1.", "2.", "3.", "4.", "5."]:
        text = text.replace(char, "")
    return text

def stream_ai_rewrite(text, api_key):
    url = "https://api.deepseek.com/chat/completions"
    system_prompt = """假设你是一个专业的自媒体作家。请参考建议对文字进行二创，确保高原创性。
    建议：句型词汇调整、内容拓展、避免原文关键词、逻辑重排、变更视角、焦点转换。
    【绝对禁令】：严禁出现“不是...而是”，严禁出现破折号，严禁结构化（无列表/分点/小标题）。全文需为流畅段落。"""
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"原文=（{text}）"}],
        "stream": True,
        "temperature": 0.7  # 降低温度可略微提升首字响应速度
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    return requests.post(url, headers=headers, json=payload, stream=True, timeout=15)

# --- 3. 极速业务流 ---

target_url = st.text_input("🔗 粘贴链接，立即秒出二创")

if st.button("🚀 极速生成", type="primary", use_container_width=True):
    api_key = st.secrets.get("DEEPSEEK_API_KEY")
    
    if not api_key:
        st.error("❌ 未配置 API Key")
    elif not target_url:
        st.warning("⚠️ 请先粘贴链接")
    else:
        # 使用 st.status 提供即时反馈
        with st.status("正在全力创作中...", expanded=True) as status:
            st.write("🔍 正在抓取文章内容...")
            # 抓取逻辑 (此处假设 get_article_content 已在代码中)
            # raw_text = get_article_content(target_url) 
            # 模拟抓取过程，请确保你的代码里包含真实的抓取函数
            
            st.write("🧠 正在连接 AI 构思文案...")
            # 开始 AI 请求
            try:
                response = stream_ai_rewrite("这里是抓取到的原文内容", api_key)
                status.update(label="✅ 内容已就绪，正在排版显示...", state="complete", expanded=False)
            except:
                st.error("❌ 网络连接超时，请重试")

        # 实时流式展示区
        full_content = ""
        placeholder = st.empty()
        
        for line in response.iter_lines():
            if line:
                chunk = line.decode('utf-8').removeprefix('data: ')
                if chunk == '[DONE]': break
                try:
                    data = json.loads(chunk)
                    content = data['choices'][0]['delta'].get('content', '')
                    full_content += content
                    # 每获得一点内容就立刻物理过滤并显示
                    placeholder.markdown(hard_filter(full_content) + "▌")
                except: continue
        
        # 最终 17号宋体渲染
        final_text = hard_filter(full_content)
        placeholder.markdown(final_text)
        st.markdown(f"""
            <div style="padding:20px; background:white; line-height:1.8; font-family:'SimSun'; font-size:17px; border-left:6px solid #07c160;">
                {markdown.markdown(final_text)}
            </div>
        """, unsafe_allow_html=True)
