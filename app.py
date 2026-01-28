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
    white-space: pre-wrap; /* 核心：保留所有换行 */
    margin-bottom: 16px;
}

/* 纯文本区：小标题黑体18号，正文宋体17号 */
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
    color: white !important;
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

# -------------------------------
# 2. 工具函数
# -------------------------------

def format_title_block(text: str) -> str:
    """
    强制【推荐爆款标题】后面 5 个标题：每行一个，并在标题区后空三行。
    """
    marker = "【推荐爆款标题】"
    if marker not in text:
        return text

    start = text.find(marker) + len(marker)
    after = text[start:]

    # 标题区结束：遇到第一个小标题 ## 01. 或者连续空行（>=3）就结束
    m1 = re.search(r"\n##\s*0[1-4]\.", after)
    m2 = re.search(r"\n{3,}", after)
    candidates = [m.start() for m in [m1, m2] if m]
    if candidates:
        end_idx = min(candidates)
        title_block = after[:end_idx]
        rest = after[end_idx:]
    else:
        title_block = after
        rest = ""

    # 拆标题：优先按换行；不足 5 行再用 ;；|｜/ 分割（不动逗号顿号等标点）
    raw_lines = [ln.strip() for ln in title_block.split("\n") if ln.strip()]
    if len(raw_lines) < 5:
        joined = " ".join(raw_lines)
        parts = re.split(r"(?:\s*[;；]\s*|\s*[|｜]\s*|\s*/\s*)", joined)
        raw_lines = [p.strip() for p in parts if p.strip()]

    titles = raw_lines[:5]
    fixed = marker + "\n" + ("\n".join(titles)).strip() + "\n\n\n"

    return text[:text.find(marker)] + fixed + rest.lstrip("\n")


def safety_filter(text: str) -> str:
    """禁令拦截 + 强制结构修正（不乱动标题标点）"""
    text = text.replace("\\n", "\n")

    # 禁令句式（按你原逻辑保留）
    text = text.replace("不是", "不单是").replace("而是", "更是")

    # 禁用破折号：仅替换破折号字符本身，不影响其他标点
    text = text.replace("——", " ").replace("—", " ")

    # 保证小标题前有空行
    text = re.sub(r'(\n?)(##\s*0[1-4]\.)', r'\n\n\2', text)

    # 强制标题区：每行一个 + 空三行
    text = format_title_block(text)
    return text


def to_plain_text(md_text: str) -> str:
    """
    markdown -> 真·纯文本：
    - 去掉 ## 标题符号
    - 去掉 ** * ` 等符号（不删内容）
    - 保留标点、保留换行
    """
    t = md_text

    # 去掉标题前缀 '## '
    t = re.sub(r'^\s*##\s*', '', t, flags=re.MULTILINE)

    # 去掉粗体/斜体/代码符号（保留内容）
    t = re.sub(r'\*\*(.+?)\*\*', r'\1', t)
    t = re.sub(r'\*(.+?)\*', r'\1', t)
    t = re.sub(r'`(.+?)`', r'\1', t)

    # [text](url) -> text
    t = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', t)

    return t


def build_plaintext_html(text: str) -> str:
    """
    纯文本展示：识别 “## 01.” 或者 “01.” 两种小标题，渲染为 黑体18号。
    """
    safe = html.escape(text)
    lines = safe.split("\n")

    out = ['<div class="output-container plaintext-render">']
    for ln in lines:
        if ln.strip() == "":
            out.append("<br/>")
            continue

        raw = html.unescape(ln)

        if re.match(r'^\s*(##\s*)?0[1-4]\.\s*.+\s*$', raw):
            title_txt = re.sub(r'^\s*##\s*', '', raw).strip()
            out.append(f'<div class="pt-h2">{html.escape(title_txt)}</div>')
        else:
            out.append(f'<div>{ln}</div>')
    out.append("</div>")
    return "\n".join(out)


def js_copy_button(button_text: str, content: str, success_msg: str, height: int = 70):
    """
    复制按钮：复制 content（文本）到剪贴板
    """
    js_safe = json.dumps(content)  # 安全注入（含换行/引号）
    components.html(f"""
<button class="copy-btn" onclick="copyNow()">{button_text}</button>
<script>
async function copyNow(){{
  const text = {js_safe};
  try {{
    await navigator.clipboard.writeText(text);
    alert("{success_msg}");
  }} catch (e) {{
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

# -------------------------------
# 3. 业务展示
# -------------------------------

target_url = st.text_input("🔗 粘贴链接开始深度重构")

if st.button("🚀 开始极速生成", type="primary"):
    api_key = st.secrets.get("DEEPSEEK_API_KEY")

    if not target_url:
        st.error("请先粘贴链接。")
    elif not api_key:
        st.error("未检测到 DEEPSEEK_API_KEY，请在 .streamlit/secrets.toml 配置。")
    else:
        raw_text = get_article_content(target_url)
        if not raw_text:
            st.error("内容抓取失败")
        else:
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

            # ✅ 纯文本导出：去掉 markdown 语法（复制用）
            plain_text = to_plain_text(final_text)

            # --- A. 纯文本区 ---
            st.subheader("📋 1. 纯文本格式（小标题黑体18 / 正文宋体17）")
            st.markdown(build_plaintext_html(plain_text), unsafe_allow_html=True)

            js_copy_button(
                button_text="📋 一键复制纯文本",
                content=plain_text,
                success_msg="纯文本复制成功！"
            )

            st.divider()

            # --- B. Markdown 成品区 ---
            st.subheader("🎨 2. Markdown 成品（预览 + 一键复制 Markdown 原文）")

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

            js_copy_button(
                button_text="📋 一键复制 Markdown 原文",
                content=final_text,
                success_msg="Markdown 原文复制成功，可直接贴入公众号！"
            )
