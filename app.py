import streamlit as st
import requests
import json
from bs4 import BeautifulSoup
import markdown
import streamlit.components.v1 as components
import re
import html

# --- 1. 界面视觉：微信绿主题 + 纯白底 + 纯黑字 ---
st.set_page_config(page_title="高级原创二创助手", layout="centered")

st.markdown("""
<style>
/* 全局对比度锁死 */
.stApp { background-color: #ffffff; color: #000000 !important; }
h1 { color: #07c160 !important; font-family: "Microsoft YaHei"; text-align: center; font-weight: bold; }

/* 输入框：文字必须是纯黑 */
.stTextInput input { color: #000000 !important; font-weight: bold !important; }
.stTextInput > div > div { border: 2px solid #07c160 !important; }

/* 输出容器：极浅灰底，绝对纯黑字 */
.output-container {
    background-color: #f9f9f9 !important;
    color: #000000 !important;
    padding: 25px;
    border-radius: 8px;
    border: 1px solid #07c160;
    font-family: 'SimSun', '宋体', serif;
    font-size: 17px;
    line-height: 2;
    white-space: pre-wrap; /* 保留所有换行 */
    margin-bottom: 16px;
}

/* 纯文本区：对“## 01.”这类小标题做黑体18号 */
.plaintext-render {
    font-family: 'SimSun','宋体', serif !important;
    font-size: 17px !important;
    color: #000000 !important;
}
.plaintext-render .pt-h2 {
    font-family: 'SimHei','黑体', sans-serif !important;
    font-size: 18px !important;
    font-weight: 800 !important;
    margin-top: 18px;
    margin-bottom: 8px;
}

/* 微信绿按钮 */
.copy-btn {
    width: 100%;
    height: 48px;
    background-color: #07c160;
    color: #fff !important;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 22px;
}

/* 页脚与二维码 */
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
    <div class="qr-item">📗 微信加我
        <div class="qr-box">
            <img src="https://raw.githubusercontent.com/yunie973/wechat-rewrite-tool/main/wechat_qr.png.jpg" style="width:100%;">
        </div>
    </div>
    <div class="qr-item">🪐 知识星球
        <div class="qr-box">
            <img src="https://raw.githubusercontent.com/yunie973/wechat-rewrite-tool/main/star_qr.png.jpg" style="width:100%;">
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.title("🛡️ 深度重构级专业工作台")

# --- 2. 核心函数：严格执行写作指令 ---

def safety_filter(text: str) -> str:
    """【物理拦截网】仅执行禁令，不删正常标点，强制换行"""
    text = text.replace("\\n", "\n")
    # 绝对执行禁令句式拦截
    text = text.replace("不是", "不单是").replace("而是", "更是").replace("——", "，").replace("—", "，")

    # 【强制换行】爆款标题后面加换行，## 小标题前面加换行
    text = re.sub(r'(【推荐爆款标题】)', r'\1\n', text)
    text = re.sub(r'(\n?)(## 0[1-4]\.)', r'\n\n\2', text)
    return text

def get_article_content(url: str):
    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X)"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        content_div = soup.find('div', id='js_content')
        return content_div.get_text(separator='\n', strip=True) if content_div else None
    except:
        return None

def stream_ai_rewrite(text: str, api_key: str):
    url = "https://api.deepseek.com/chat/completions"
    system_prompt = """假设你是一个专业的自媒体作家。对下文进行二创。
【原创加强建议】：句型词汇调整、内容拓展、避免关键词、结构逻辑调整、视角切换、重点聚焦、角度转换、避免直接引用。
【核心禁令】：
- 永远不要出现“不是....，而是”的句式。
- 绝对不要出现破折号（——）。
- 绝对禁止结构化：禁止使用列表、分点（如1.2.3.或●），保持段落连贯性。
【输出结构】：
1. 第一行写【推荐爆款标题】，接着输出5个爆款标题，每行一个。
2. 标题区后空三行。
3. 正文开头必须先写150字引入语。
4. 小标题格式固定为 ## 01. XXX，总数控制在 2-4 个。"""

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"原文=（{text}）"}
        ],
        "stream": True,
        "temperature": 0.8
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    return requests.post(url, headers=headers, json=payload, stream=True)

def build_plaintext_html(text: str) -> str:
    """
    把纯文本做成“视觉排版”：小标题黑体18号，正文宋体17号。
    复制仍然复制 text 本身（纯文本）。
    """
    # HTML转义，防止内容里有 < > & 导致渲染混乱
    safe = html.escape(text)

    # 将 "## 01. xxx" 变成视觉小标题，其余按换行分段
    lines = safe.split("\n")
    out = ['<div class="output-container plaintext-render">']
    for ln in lines:
        # 保留空行
        if ln.strip() == "":
            out.append("<br/>")
            continue

        # 匹配 ## 01. XXX
        m = re.match(r'^\s*##\s*(0[1-4]\.\s*.+)\s*$', html.unescape(ln))
        # 注意：上面用 unescape 是因为 ln 已 escape；这里仅用于匹配逻辑，不输出它
        if re.match(r'^\s*##\s*0[1-4]\.\s*.+\s*$', html.unescape(ln)):
            # 取掉##，显示成小标题块
            title_txt = re.sub(r'^\s*##\s*', '', html.unescape(ln)).strip()
            out.append(f'<div class="pt-h2">{html.escape(title_txt)}</div>')
        else:
            out.append(f'<div>{ln}</div>')
    out.append("</div>")
    return "\n".join(out)

def js_copy_button(button_text: str, content: str, success_msg: str, height: int = 70):
    """
    生成通用复制按钮：复制 content 到剪贴板（纯文本方式）。
    用 JSON.stringify 防止反引号、换行、引号把 JS 打断。
    """
    # 用 json.dumps 安全注入字符串（包含换行/引号）
    js_safe = json.dumps(content)

    components.html(f"""
<button class="copy-btn" onclick="copyNow()">{button_text}</button>
<script>
async function copyNow(){{
  const text = {js_safe};
  try {{
    await navigator.clipboard.writeText(text);
    alert("{success_msg}");
  }} catch (e) {{
    // 兼容老浏览器 fallback
    const el = document.createElement('textarea');
    el.value = text;
    document.body.appendChild(el);
    el.select();
    document.execCommand('copy');
    document.body.removeChild(el);
    alert("{success_msg}");
  }}
}}
</script>
""", height=height)

# --- 3. 业务展示区：纯文本在前，Markdown在后 ---

target_url = st.text_input("🔗 粘贴链接开始深度重构")

if st.button("🚀 开始极速生成", type="primary"):
    api_key = st.secrets.get("DEEPSEEK_API_KEY")
    if target_url and api_key:
        raw_text = get_article_content(target_url)
        if raw_text:
            full_content = ""
            placeholder = st.empty()
            response = stream_ai_rewrite(raw_text, api_key)

            for line in response.iter_lines():
                if not line:
                    continue
                chunk = line.decode('utf-8', errors='ignore')
                chunk = chunk.removeprefix('data: ').strip()
                if chunk == '[DONE]':
                    break
                try:
                    data = json.loads(chunk)
                    full_content += data['choices'][0]['delta'].get('content', '')
                    placeholder.markdown(safety_filter(full_content) + "▌")
                except:
                    continue

            final_text = safety_filter(full_content)
            placeholder.empty()

            # --- A. 纯文本区 (顺序第一) ---
            st.subheader("📋 1. 纯文本格式（小标题黑体18 / 正文宋体17）")

            st.markdown(build_plaintext_html(final_text), unsafe_allow_html=True)

            js_copy_button(
                button_text="📋 一键复制纯文本",
                content=final_text,
                success_msg="纯文本复制成功！"
            )

            st.divider()

            # --- B. Markdown 成品区 (顺序第二) ---
            st.subheader("🎨 2. Markdown 成品（预览 + 一键复制 Markdown 原文）")

            # 渲染预览（注意：你原来这里变量写错了，应该用 html_md）
            html_md = markdown.markdown(final_text, extensions=["extra"])

            st.markdown(f"""
<div id="md-render" class="output-container" style="background:#ffffff !important;">
  <style>
    #md-render {{ font-family: "SimSun","宋体", serif !important; font-size: 17px !important; color: #000000 !important; }}
    #md-render h2 {{ font-size: 18px !important; font-family: "SimHei","黑体", sans-serif !important;
                    font-weight: 800 !important; color: #000000 !important; margin-top: 30px;
                    border-left: 5px solid #07c160; padding-left: 10px; }}
    #md-render p {{ margin-bottom: 20px; color: #000000 !important; }}
  </style>
  {html_md}
</div>
""", unsafe_allow_html=True)

            # 复制的是“Markdown原文”，而不是复制渲染后的 HTML
            js_copy_button(
                button_text="📋 一键复制 Markdown 原文",
                content=final_text,
                success_msg="Markdown 原文复制成功，可直接贴入公众号！"
            )
        else:
            st.error("内容抓取失败")
    else:
        st.error("请检查：链接是否填写、DEEPSEEK_API_KEY 是否已配置在 st.secrets 中。")
