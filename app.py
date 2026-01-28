import streamlit as st
import streamlit.components.v1 as components
import requests
import json
from bs4 import BeautifulSoup
import re
import html

# --- 1. UI 视觉锁死：微信绿 + 纯黑字 ---
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

# --- 2. 文本处理核心逻辑 ---

def format_title_block(text: str) -> str:
    """强制执行 5 个标题及空三行逻辑"""
    marker = "【推荐爆款标题】"
    if marker not in text: return text
    start = text.find(marker) + len(marker)
    after = text[start:]
    m1 = re.search(r"\n##\s*0[1-4]\.", after)
    m2 = re.search(r"\n{3,}", after)
    candidates = [m.start() for m in [m1, m2] if m]
    end_idx = min(candidates) if candidates else len(after)
    title_block = after[:end_idx]
    rest = after[end_idx:]
    raw_lines = [ln.strip() for ln in title_block.split("\n") if ln.strip()]
    titles = raw_lines[:5]
    fixed = marker + "\n" + ("\n".join(titles)).strip() + "\n\n\n"
    return text[:text.find(marker)] + fixed + rest.lstrip("\n")

def safety_filter(text: str) -> str:
    """物理拦截禁令"""
    text = text.replace("\\n", "\n")
    text = text.replace("不是", "不单是").replace("而是", "更是")
    text = text.replace("——", " ").replace("—", " ")
    text = re.sub(r'(\n?)(##\s*0[1-4]\.)', r'\n\n\2', text)
    return format_title_block(text)

def build_rich_html(md_text: str) -> str:
    """精准排版：Heading-18号黑体，Body-17号宋体"""
    # 先剔除MD标记
    t = re.sub(r'^\s*##\s*', '', md_text, flags=re.MULTILINE)
    lines = t.split("\n")
    parts = ['<div style="font-family:SimSun,宋体,serif;font-size:17px;line-height:2;color:#000;text-align:justify;">']
    for ln in lines:
        if not ln.strip():
            parts.append("<p><br/></p>")
            continue
        # 匹配小标题 01.
        if re.match(r'^\s*0[1-4]\.\s*.+\s*$', ln) or ln.strip() == "【推荐爆款标题】":
            parts.append(f'<p style="margin:20px 0 10px 0;font-family:SimHei,黑体,sans-serif;font-size:18px;font-weight:bold;">{html.escape(ln.strip())}</p>')
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
    system_prompt = """假设你是一个专业的自媒体作家。请对下文进行二创。
    【核心禁令】：严禁出现“不是...而是”，严禁破折号，严禁列表分点。
    【输出结构】：第一行写【推荐爆款标题】，接着输出5个爆款标题（每行一个），空三行。正文开头写150字引入语，小标题格式 ## 01. XXX。"""
    payload = {"model": "deepseek-chat", "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"原文=（{text}）"}], "stream": True, "temperature": 0.8}
    return requests.post(url, headers={"Authorization": f"Bearer {api_key}"}, json=payload, stream=True)

# --- 4. 业务展示与复制 ---

target_url = st.text_input("🔗 粘贴文章链接")

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
            
            # --- 展示富文本块 ---
            st.subheader("📋 1) 保留格式复制 (18号黑体/17号宋体)")
            rich_html = build_rich_html(md_final)
            components.html(f"""
                <div id="c" style="padding:15px; border:1px solid #07c160; border-radius:8px; background:#fff; position:relative;">
                    <button id="b" style="position:absolute; top:10px; right:10px; background:#07c160; color:#fff; border:none; padding:8px 15px; border-radius:5px; cursor:pointer; font-weight:bold;">📋 复制成品</button>
                    <div id="t">{rich_html}</div>
                </div>
                <script>
                document.getElementById('b').onclick = async () => {{
                    const h = document.getElementById('t').innerHTML;
                    const b = new Blob([h], {{type: 'text/html'}});
                    const t = new Blob([document.getElementById('t').innerText], {{type: 'text/plain'}});
                    try {{
                        await navigator.clipboard.write([new ClipboardItem({{'text/html': b, 'text/plain': t}})]);
                        alert('复制成功！可直接粘贴至公众号');
                    }} catch(e) {{ alert('请使用 HTTPS 环境或 Chrome 浏览器'); }}
                }}
                </script>
            """, height=500, scrolling=True)

            # --- 展示 Markdown 原文 ---
            st.subheader("🧾 2) Markdown 原文复制")
            st.code(md_final, language="markdown")
