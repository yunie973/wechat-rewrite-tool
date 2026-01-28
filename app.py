import streamlit as st
import streamlit.components.v1 as components
import requests
import json
from bs4 import BeautifulSoup
import re
import html

# --- 1. 视觉皮肤：微信绿 + 纯白底 + 纯黑字 (解决看不清问题) ---
st.set_page_config(page_title="高级原创二创助手", layout="centered")

st.markdown("""
<style>
.stApp { background-color: #ffffff; color: #000000 !important; }
h1 { color: #07c160 !important; font-family: "Microsoft YaHei"; text-align: center; font-weight: bold; }
.stTextInput input { color: #000000 !important; font-weight: bold !important; }
.stTextInput > div > div { border: 2px solid #07c160 !important; }

/* 底部交互页脚 */
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

# --- 2. 核心文本处理 (保留 GPT 逻辑，锁死换行) ---

def safety_filter(text: str) -> str:
    """拦截禁令并强制修正换行，保留所有标点"""
    text = text.replace("\\n", "\n")
    # 物理拦截禁令
    text = text.replace("不是", "不单是").replace("而是", "更是").replace("——", " ").replace("—", " ")
    
    # 强制爆款标题断行
    text = re.sub(r'(【推荐爆款标题】)', r'\1\n', text)
    text = re.sub(r'([1-5]\. )', r'\n\1', text)
    
    # 强制 ## 小标题前后空行
    text = re.sub(r'(\n?)(##\s*0[1-4]\.)', r'\n\n\2', text)
    return text

def build_rich_html(md_text: str) -> str:
    """生成保留字号字体的 HTML：小标题黑体18 / 正文宋体17"""
    # 剔除 ## 标记以便纯净排版
    clean_text = re.sub(r'^\s*##\s*', '', md_text, flags=re.MULTILINE)
    lines = clean_text.split("\n")
    parts = ['<div style="font-family:SimSun,宋体,serif;font-size:17px;line-height:2.2;color:#000;text-align:justify;">']
    for ln in lines:
        if not ln.strip():
            parts.append("<p><br/></p>")
            continue
        # 匹配标题行：小标题 01. 或爆款标题标记
        if re.match(r'^\s*0[1-4]\.\s*.+\s*$', ln) or "【推荐爆款标题】" in ln:
            parts.append(f'<p style="margin:25px 0 10px 0;font-family:SimHei,黑体,sans-serif;font-size:18px;font-weight:bold;">{html.escape(ln.strip())}</p>')
        else:
            parts.append(f'<p style="margin-bottom:15px;">{html.escape(ln)}</p>')
    parts.append("</div>")
    return "".join(parts)

# --- 3. 抓取与 API 逻辑 ---

def get_article_content(url):
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        content = soup.find('div', id='js_content')
        return content.get_text(separator='\n', strip=True) if content else None
    except: return None

def stream_ai_rewrite(text, api_key):
    url = "https://api.deepseek.com/chat/completions"
    system_prompt = """假设你是一个专业的自媒体作家。对下文进行二创。
    【原创要求】：句型词汇调整、内容拓展、视角切换、角度转换。
    【核心禁令】：严禁出现“不是...而是”，严禁破折号，严禁结构化分点。
    【输出结构】：第一行写【推荐爆款标题】，接着输出5个爆款标题（每行一个），标题区后空三行。正文开头写150字引入语，小标题格式 ## 01. XXX。"""
    payload = {"model": "deepseek-chat", "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"原文=（{text}）"}], "stream": True, "temperature": 0.8}
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    return requests.post(url, headers=headers, json=payload, stream=True)

# --- 4. 业务逻辑与稳健复制组件 ---

target_url = st.text_input("🔗 粘贴文章链接开始深度重构")

if st.button("🚀 开始极速生成", type="primary", use_container_width=True):
    api_key = st.secrets.get("DEEPSEEK_API_KEY")
    if target_url and api_key:
        raw_text = get_article_content(target_url)
        if raw_text:
            full_content = ""
            placeholder = st.empty()
            response = stream_ai_rewrite(raw_text, api_key)
            for line in response.iter_lines():
                if line:
                    chunk = line.decode('utf-8').removeprefix('data: ').strip()
                    if chunk == "[DONE]": break
                    try:
                        data = json.loads(chunk)
                        full_content += data["choices"][0]["delta"].get("content", "")
                        placeholder.markdown(safety_filter(full_content) + "▌")
                    except: continue
            
            md_final = safety_filter(full_content)
            placeholder.empty()
            
            # --- 展示与复制块 (集成 GPT 稳健逻辑) ---
            rich_html = build_rich_html(md_final)
            
            st.subheader("📋 1) 成品复制 (保留18号黑体/17号宋体)")
            components.html(f"""
                <div style="border:1px solid #07c160; border-radius:10px; padding:20px; background:#fff; position:relative;">
                    <button id="b" style="position:absolute; top:15px; right:15px; background:#07c160; color:#fff; border:none; padding:10px 20px; border-radius:8px; cursor:pointer; font-weight:bold; font-size:16px;">📋 一键复制</button>
                    <div id="t" style="color:#000;">{rich_html}</div>
                </div>
                <script>
                document.getElementById('b').onclick = async () => {{
                    const h = document.getElementById('t').innerHTML;
                    const b_html = new Blob([h], {{type: 'text/html'}});
                    const b_text = new Blob([document.getElementById('t').innerText], {{type: 'text/plain'}});
                    try {{
                        await navigator.clipboard.write([new ClipboardItem({{'text/html': b_html, 'text/plain': b_text}})]);
                        alert('✅ 复制成功！样式已保留，可直接贴入公众号');
                    }} catch(e) {{
                        alert('复制失败：请确保在 HTTPS 环境或 Chrome 浏览器下使用');
                    }}
                }}
                </script>
            """, height=600, scrolling=True)

            st.subheader("🧾 2) Markdown 原文区")
            st.code(md_final, language="markdown")
        else: st.error("内容抓取失败")
