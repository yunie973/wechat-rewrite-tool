import streamlit as st
import requests
import json
from bs4 import BeautifulSoup
import markdown
import streamlit.components.v1 as components
import re

# --- 1. 强效视觉补丁：锁死纯黑字，解决“看不清” ---
st.set_page_config(page_title="深度重构专业工作台", layout="centered")

st.markdown("""
    <style>
    /* 全局颜色强制：白底、绝对纯黑字 */
    .stApp { background-color: #ffffff; color: #000000 !important; }
    h1 { color: #07c160 !important; font-family: "Microsoft YaHei"; text-align: center; font-weight: 800; }
    
    /* 输入框文字必须黑，边框绿 */
    .stTextInput input { color: #000000 !important; font-weight: bold !important; font-size: 16px !important; }
    .stTextInput div div { border-color: #07c160 !important; }

    /* 结果区域：浅灰背景，纯黑字，强制保留换行 */
    .output-box {
        background-color: #f6f6f6 !important;
        color: #000000 !important;
        padding: 30px;
        border-radius: 8px;
        border: 1px solid #07c160;
        font-family: 'SimSun', 'STSong', serif;
        font-size: 17px;
        line-height: 2.2;
        white-space: pre-wrap; /* 物理保留所有换行 */
        text-align: justify;
    }

    /* 微信绿按钮 */
    div.stButton > button { 
        background-color: #07c160 !important; 
        color: white !important; 
        border-radius: 8px; 
        height: 52px; 
        font-weight: bold; 
        width: 100%; 
        font-size: 18px;
        border: none;
    }

    /* 底部页脚 */
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

# --- 2. 核心函数：物理纠偏逻辑 ---

def get_article_content(url):
    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X)"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        content_div = soup.find('div', id='js_content')
        return content_div.get_text(separator='\n', strip=True) if content_div else None
    except: return None

def final_output_filter(text):
    """【物理过滤器】纠正排版鬼畜，移除指令残留"""
    # 移除 AI 误打出的排版指令
    text = text.replace("(空三行)", "\n\n\n").replace("（空三行）", "\n\n\n")
    # 移除莫名其妙出现的孤立数字“0” (针对截图 image_2ec2cb 修复)
    text = re.sub(r'^\s*0\s*$', '', text, flags=re.MULTILINE)
    
    # 强制执行“三不”拦截
    text = text.replace("不是", "不单是").replace("而是", "更是").replace("——", "，").replace("—", "，")
    
    # 强制爆款标题断行：匹配 1. 2. 3. 模式并在前加换行
    text = re.sub(r'([1-5]\. )', r'\n\1', text)
    # 强制 ## 01. 格式前后空行
    text = re.sub(r'(\n?)(## 0[1-4]\.)', r'\n\n\2', text)
    return text.strip()

def stream_ai_rewrite(text, api_key):
    url = "https://api.deepseek.com/chat/completions"
    # 极其严厉的 Prompt：禁止输出元指令
    system_prompt = """你是一个专业的自媒体作家。对下文进行深度二创。
    【核心禁令】：严禁使用“不是...而是”，严禁出现破折号，严禁结构化分点。
    【写作要求】：
    1. 第一行写【推荐爆款标题】，下方紧跟 5 个爆款标题，每行一个。
    2. 标题区写完后，**实际空出三行**，不要写出“(空三行)”这种字。
    3. 正文开头写150字引入语。
    4. 小标题格式 ## 01. XXX，总数 2-4 个。"""
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"原文=（{text}）"}],
        "stream": True, "temperature": 0.8
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    return requests.post(url, headers=headers, json=payload, stream=True)

# --- 3. 执行与排版渲染 ---

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
                        placeholder.markdown(final_output_filter(full_content) + "▌")
                    except: continue
            
            final_text = final_output_filter(full_content)
            placeholder.empty()

            # --- 双格式：纯文本在前，预览在后 ---
            st.subheader("📋 1. 纯文本格式 (纯黑字)")
            st.markdown(f'<div class="output-box">{final_text}</div>', unsafe_allow_html=True)
            
            # JS 一键复制脚本
            txt_safe = final_text.replace('`', '\\`').replace('$', '\\$')
            components.html(f"""
                <button onclick="copyTxt()" style="width:100%;height:48px;background:#07c160;color:white;border:none;border-radius:8px;font-weight:bold;cursor:pointer;font-size:16px;">📋 复制纯文本</button>
                <script>
                function copyTxt() {{
                    const el = document.createElement('textarea');
                    el.value = `{txt_safe}`;
                    document.body.appendChild(el); el.select();
                    document.execCommand('copy');
                    document.body.removeChild(el);
                    alert('纯文本已复制！');
                }}
                </script>
            """, height=60)

            st.divider()

            st.subheader("🎨 2. Markdown 预览 (18号黑体/17号宋体)")
            # 解决 NameError：明确渲染逻辑
            rendered_html = markdown.markdown(final_text)
            st.markdown(f"""
                <div id="md-view" class="output-box" style="background:#ffffff !important;">
                    <style>
                        #md-view {{ font-family: "SimSun", serif !important; font-size: 17px !important; color: #000 !important; }}
                        #md-view h2 {{ font-size: 18px !important; font-family: "SimHei", sans-serif !important; font-weight: bold !important; color: #000 !important; margin-top: 30px; border-left: 5px solid #07c160; padding-left: 10px; }}
                        #md-view p {{ margin-bottom: 18px; color: #000 !important; }}
                    </style>
                    {rendered_html}
                </div>
            """, unsafe_allow_html=True)
            
            components.html("""
                <button onclick="copyMd()" style="width:100%;height:48px;background:#07c160;color:white;border:none;border-radius:8px;font-weight:bold;cursor:pointer;font-size:16px;">📋 复制 Markdown 预览</button>
                <script>
                function copyMd() {
                    const range = document.createRange();
                    range.selectNode(parent.document.getElementById('md-view'));
                    window.getSelection().removeAllRanges();
                    window.getSelection().addRange(range);
                    document.execCommand('copy');
                    alert('预览格式已复制！');
                }
                </script>
            """, height=60)
        else: st.error("抓取失败")
