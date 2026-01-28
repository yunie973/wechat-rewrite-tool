import streamlit as st
import requests
import json
from bs4 import BeautifulSoup
import re
import html

# -----------------------------
# 1) UI：微信绿 + 白底黑字
# -----------------------------
st.set_page_config(page_title="高级原创二创助手", layout="centered")

st.markdown("""
<style>
.stApp { background-color: #ffffff; color: #000000 !important; }
h1 { color: #07c160 !important; font-family: "Microsoft YaHei"; text-align: center; font-weight: bold; }

.stTextInput input { color: #000000 !important; font-weight: bold !important; }
.stTextInput > div > div { border: 2px solid #07c160 !important; }

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

# -----------------------------
# 2) 文本处理
# -----------------------------
def format_title_block(text: str) -> str:
    """
    强制【推荐爆款标题】后面标题：每行一个，标题区后空三行。
    不删除标题标点（只做结构分行）。
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

    raw_lines = [ln.strip() for ln in title_block.split("\n") if ln.strip()]

    # 如果挤成一行：仅用 ;；|｜/ 这些“常见分隔符”拆（不动逗号顿号等标点）
    if len(raw_lines) < 5 and raw_lines:
        joined = " ".join(raw_lines)
        parts = re.split(r"(?:\s*[;；]\s*|\s*[|｜]\s*|\s*/\s*)", joined)
        raw_lines = [p.strip() for p in parts if p.strip()]

    titles = raw_lines[:5]
    fixed = marker + "\n" + ("\n".join(titles)).strip() + "\n\n\n"
    return text[:text.find(marker)] + fixed + rest.lstrip("\n")


def safety_filter(text: str) -> str:
    """
    禁令拦截 + 结构修正：
    - 不删正常标点
    - 只处理破折号字符（禁令要求）
    - 强制标题区分行与空行
    """
    text = text.replace("\\n", "\n")

    # 禁令句式（按你原逻辑保留）
    text = text.replace("不是", "不单是").replace("而是", "更是")

    # 禁用破折号：只替换破折号字符，不影响其他标点
    text = text.replace("——", " ").replace("—", " ")

    # 小标题前空行
    text = re.sub(r'(\n?)(##\s*0[1-4]\.)', r'\n\n\2', text)

    # 标题区：每行一个+空三行
    text = format_title_block(text)
    return text


def to_plain_text(md_text: str) -> str:
    """markdown -> 真·纯文本（用于生成富文本显示/复制时的内容骨架）"""
    t = md_text
    t = re.sub(r'^\s*##\s*', '', t, flags=re.MULTILINE)           # 去掉 ## 前缀
    t = re.sub(r'\*\*(.+?)\*\*', r'\1', t)                         # 去掉 ** **
    t = re.sub(r'\*(.+?)\*', r'\1', t)                             # 去掉 * *
    t = re.sub(r'`(.+?)`', r'\1', t)                               # 去掉 ` `
    t = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', t)                 # [text](url) -> text
    return t


def build_rich_html(plain_text: str) -> str:
    """
    生成“可粘贴保留字体字号”的 HTML：
    - 小标题：黑体18加粗
    - 正文：宋体17
    """
    lines = plain_text.split("\n")
    parts = ['<div style="font-family:SimSun,宋体,serif;font-size:17px;line-height:2;color:#000;">']
    for ln in lines:
        if ln.strip() == "":
            parts.append("<p><br/></p>")
            continue

        # 小标题：01. XXX
        if re.match(r'^\s*0[1-4]\.\s*.+\s*$', ln):
            parts.append(
                f'<p style="margin:18px 0 8px 0;font-family:SimHei,黑体,sans-serif;font-size:18px;font-weight:800;">'
                f'{html.escape(ln.strip())}</p>'
            )
            continue

        # 标题区 “【推荐爆款标题】”以及其后5行，也给黑体18更像标题
        if ln.strip() == "【推荐爆款标题】":
            parts.append(
                f'<p style="margin:0 0 10px 0;font-family:SimHei,黑体,sans-serif;font-size:18px;font-weight:800;">'
                f'{html.escape(ln.strip())}</p>'
            )
            continue

        parts.append(f'<p style="margin:0 0 14px 0;">{html.escape(ln)}</p>')

    parts.append("</div>")
    return "".join(parts)


# -----------------------------
# 3) 抓取 & DeepSeek 流式
# -----------------------------
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


# -----------------------------
# 4) 右上角复制组件（富文本/Markdown）
# -----------------------------
def render_block_with_copy_rich(rich_html: str, plain_fallback: str, title: str):
    """
    显示富文本块 + 右上角复制按钮：
    - 优先写入 text/html
    - 同时写入 text/plain 作为 fallback
    """
    rich_js = json.dumps(rich_html)
    plain_js = json.dumps(plain_fallback)
    title_esc = html.escape(title)

    components.html(f"""
<div style="position:relative;border:1px solid #07c160;border-radius:10px;background:#fff;padding:18px 18px 12px 18px;">
  <div style="font-weight:800;color:#000;margin:0 0 12px 0;font-family:Microsoft YaHei;">{title_esc}</div>

  <button id="copyBtn"
    style="position:absolute;top:12px;right:12px;background:#07c160;color:#fff;border:none;border-radius:8px;
           padding:8px 12px;cursor:pointer;font-weight:800;">
    📋 复制
  </button>

  <div id="content">
    {rich_html}
  </div>
</div>

<script>
async function copyRich(){{
  const htmlText = {rich_js};
  const plainText = {plain_js};

  // 1) 新版：ClipboardItem 复制 HTML + 纯文本
  try {{
    if (navigator.clipboard && window.ClipboardItem) {{
      const htmlBlob = new Blob([htmlText], {{ type: "text/html" }});
      const textBlob = new Blob([plainText], {{ type: "text/plain" }});
      const item = new ClipboardItem({{
        "text/html": htmlBlob,
        "text/plain": textBlob
      }});
      await navigator.clipboard.write([item]);
      alert("已复制（保留字体字号）");
      return;
    }}
  }} catch(e) {{}}

  // 2) 兼容：选中 contenteditable 然后 execCommand('copy')（很多环境也能复制富文本）
  try {{
    const temp = document.createElement("div");
    temp.setAttribute("contenteditable", "true");
    temp.style.position = "fixed";
    temp.style.left = "-9999px";
    temp.innerHTML = htmlText;
    document.body.appendChild(temp);

    const range = document.createRange();
    range.selectNodeContents(temp);
    const sel = window.getSelection();
    sel.removeAllRanges();
    sel.addRange(range);

    document.execCommand("copy");
    sel.removeAllRanges();
    document.body.removeChild(temp);

    alert("已复制（保留字体字号）");
    return;
  }} catch(e) {{}}

  // 3) 最后兜底：至少复制纯文本
  try {{
    await navigator.clipboard.writeText(plainText);
    alert("已复制（降级为纯文本）");
  }} catch(e) {{
    alert("复制失败：请使用浏览器 HTTPS 环境或更换浏览器");
  }}
}}

document.getElementById("copyBtn").addEventListener("click", copyRich);
</script>
""", height=520)


def render_block_with_copy_markdown(md_text: str, title: str):
    """显示 Markdown 原样 + 右上角复制按钮（复制 text/plain）"""
    md_esc = html.escape(md_text)
    md_js = json.dumps(md_text)
    title_esc = html.escape(title)

    components.html(f"""
<div style="position:relative;border:1px solid #07c160;border-radius:10px;background:#fff;padding:18px;">
  <div style="font-weight:800;color:#000;margin:0 0 12px 0;font-family:Microsoft YaHei;">{title_esc}</div>

  <button id="copyBtnMd"
    style="position:absolute;top:12px;right:12px;background:#07c160;color:#fff;border:none;border-radius:8px;
           padding:8px 12px;cursor:pointer;font-weight:800;">
    📋 复制
  </button>

  <pre style="margin:0;white-space:pre-wrap;line-height:1.8;font-size:14px;
              font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,'Liberation Mono','Courier New',monospace;
              background:#ffffff;border-radius:8px;">{md_esc}</pre>
</div>

<script>
async function copyMd(){{
  const text = {md_js};
  try {{
    await navigator.clipboard.writeText(text);
    alert("Markdown 已复制");
  }} catch(e) {{
    // fallback
    const el = document.createElement("textarea");
    el.value = text;
    document.body.appendChild(el);
    el.select();
    document.execCommand("copy");
    document.body.removeChild(el);
    alert("Markdown 已复制");
  }}
}}
document.getElementById("copyBtnMd").addEventListener("click", copyMd);
</script>
""", height=520)


# -----------------------------
# 5) 页面逻辑
# -----------------------------
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
                chunk = line.decode('utf-8', errors='ignore').removeprefix('data: ').strip()
                if chunk == "[DONE]":
                    break
                try:
                    data = json.loads(chunk)
                    full_content += data["choices"][0]["delta"].get("content", "")
                    placeholder.markdown(safety_filter(full_content) + "▌")
                except:
                    continue

            placeholder.empty()

            md_final = safety_filter(full_content)     # Markdown 原文
            plain_final = to_plain_text(md_final)      # 用来生成富文本
            rich_html = build_rich_html(plain_final)   # 富文本HTML（保留字号字体）

            st.subheader("🖨️ 1) 一键复制：保留字体字号（富文本）")
            render_block_with_copy_rich(
                rich_html=rich_html,
                plain_fallback=plain_final,
                title="富文本成品（小标题黑体18 / 正文宋体17）"
            )

            st.subheader("🧾 2) 一键复制：Markdown 原文")
            render_block_with_copy_markdown(
                md_text=md_final,
                title="Markdown 原文（原样显示）"
            )
