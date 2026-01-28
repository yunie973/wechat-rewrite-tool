import streamlit as st
import streamlit.components.v1 as components
import requests
import json
from bs4 import BeautifulSoup
import re
import html
import time

# =============================
# 1) UI：微信绿 + 强制浅色 + 手机自适配
# =============================
st.set_page_config(page_title="高级原创二创助手", layout="centered")

st.markdown("""
<style>
/* ========== 强制浅色：不受系统深色影响 ========== */
:root, body, .stApp { color-scheme: light !important; }
.stApp { background-color: #ffffff !important; color: #000000 !important; padding-bottom: 90px; }

/* 标题 */
h1 { color: #07c160 !important; font-family: "Microsoft YaHei"; text-align: center; font-weight: 900; }

/* 输入框：白底黑字绿边 */
.stTextInput > div > div {
  border: 2px solid #07c160 !important;
  border-radius: 12px !important;
  background: #ffffff !important;
}
.stTextInput input {
  background: #ffffff !important;
  color: #000000 !important;
  font-weight: 700 !important;
}
div[data-baseweb="input"] { background: #ffffff !important; }

/* 下拉选择：白底黑字（避免深色系统发黑） */
div[data-baseweb="select"] > div {
  background: #ffffff !important;
  color: #000000 !important;
  border-radius: 12px !important;
  border: 1px solid rgba(7,193,96,0.45) !important;
}

/* Slider 文案颜色 */
div[data-baseweb="slider"] * { color: #000000 !important; }

/* 绿色按钮（覆盖 Streamlit 默认） */
div.stButton > button {
  background-color: #07c160 !important;
  color: #ffffff !important;
  border: none !important;
  border-radius: 10px !important;
  font-weight: 900 !important;
  height: 46px !important;
  width: 100% !important;
}
div.stButton > button:hover { background-color: #06b457 !important; }
div.stButton > button:disabled { background-color: #9be4be !important; color: #ffffff !important; }

/* 页脚与二维码 */
.footer {
  position: fixed; left: 0; bottom: 0; width: 100%;
  background-color: #ffffff; padding: 12px 0; border-top: 2px solid #07c160;
  z-index: 999; display: flex; justify-content: center; align-items: center; gap: 20px;
}
.qr-item { color: #07c160; font-weight: 900; cursor: pointer; position: relative; }
.qr-box {
  display: none; position: absolute; bottom: 45px; left: 50%;
  transform: translateX(-50%); width: 180px; background: white;
  padding: 10px; border: 2px solid #07c160; border-radius: 10px; box-shadow: 0 8px 25px rgba(0,0,0,0.2);
}
.qr-item:hover .qr-box { display: block; }

/* ========== 手机端自适配 ========== */
@media (max-width: 768px) {
  h1 { font-size: 26px !important; }
  .stTextInput input { font-size: 16px !important; }
  div.stButton > button { height: 50px !important; border-radius: 12px !important; }
  .stApp { padding-bottom: 20px !important; }

  /* 手机端 footer 不固定，避免遮挡内容 */
  .footer {
    position: relative !important;
    border-top: 1px solid rgba(7,193,96,0.35) !important;
    padding: 10px 0 !important;
    gap: 12px !important;
  }
  .qr-box { width: 150px !important; }
}
</style>

<div class="footer">
  <span style="color:#000;">© 2026 <b>@兴洪</b> 版权所有</span>
  <div class="qr-item">📗 微信加我
    <div class="qr-box"><img src="https://raw.githubusercontent.com/yunie973/wechat-rewrite-tool/main/wechat_qr.png.jpg" style="width:100%;"></div>
  </div>
  <div class="qr-item">🪐 知识星球
    <div class="qr-box"><img src="https://raw.githubusercontent.com/yunie973/wechat-rewrite-tool/main/star_qr.png.jpg" style="width:100%;"></div>
  </div>
</div>
""", unsafe_allow_html=True)

st.title("🛡️ 深度重构级专业工作台")


# =============================
# 2) session_state
# =============================
if "is_generating" not in st.session_state:
    st.session_state.is_generating = False

if "result_md" not in st.session_state:
    st.session_state.result_md = None
if "result_plain" not in st.session_state:
    st.session_state.result_plain = None
if "result_rich_html" not in st.session_state:
    st.session_state.result_rich_html = None

if "last_source_text" not in st.session_state:
    st.session_state.last_source_text = None
if "last_source_hint" not in st.session_state:
    st.session_state.last_source_hint = None
if "use_last_source" not in st.session_state:
    st.session_state.use_last_source = False

if "manual_text" not in st.session_state:
    st.session_state.manual_text = ""

if "last_error" not in st.session_state:
    st.session_state.last_error = None


# =============================
# 3) 文本处理
# =============================
def format_title_block(text: str) -> str:
    marker = "【推荐爆款标题】"
    if marker not in text:
        return text

    start = text.find(marker) + len(marker)
    after = text[start:]

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

    # 如果标题挤成一行，只用 ;；|｜/ 分割，不动逗号顿号等标点
    if len(raw_lines) < 5 and raw_lines:
        joined = " ".join(raw_lines)
        parts = re.split(r"(?:\s*[;；]\s*|\s*[|｜]\s*|\s*/\s*)", joined)
        raw_lines = [p.strip() for p in parts if p.strip()]

    titles = raw_lines[:5]
    fixed = marker + "\n" + ("\n".join(titles)).strip() + "\n\n\n"
    return text[:text.find(marker)] + fixed + rest.lstrip("\n")


def replace_bushi_ershi(text: str) -> str:
    pattern = re.compile(r"不是(?P<a>.{0,60}?)而是", flags=re.DOTALL)

    def _repl(m):
        a = m.group("a")
        return "不单是" + a + "更是"

    return pattern.sub(_repl, text)


def safety_filter(text: str) -> str:
    text = text.replace("\\n", "\n")
    text = replace_bushi_ershi(text)
    text = text.replace("——", " ").replace("—", " ")
    text = re.sub(r'(\n?)(##\s*0[1-4]\.)', r'\n\n\2', text)
    return format_title_block(text)


def to_plain_text(md_text: str) -> str:
    t = md_text
    t = re.sub(r'^\s*##\s*', '', t, flags=re.MULTILINE)
    t = re.sub(r'\*\*(.+?)\*\*', r'\1', t)
    t = re.sub(r'\*(.+?)\*', r'\1', t)
    t = re.sub(r'`(.+?)`', r'\1', t)
    t = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', t)
    return t


def build_rich_html(plain_text: str) -> str:
    lines = plain_text.split("\n")
    parts = ['<div style="font-family:SimSun,宋体,serif;font-size:17px;line-height:2;color:#000;">']

    for ln in lines:
        if ln.strip() == "":
            parts.append("<p><br/></p>")
            continue

        # 小标题：01. XXX
        if re.match(r'^\s*0[1-4]\.\s*.+\s*$', ln):
            parts.append(
                f'<p style="margin:18px 0 8px 0;font-family:SimHei,黑体,sans-serif;'
                f'font-size:18px;font-weight:800;">{html.escape(ln.strip())}</p>'
            )
            continue

        if ln.strip() == "【推荐爆款标题】":
            parts.append(
                f'<p style="margin:0 0 10px 0;font-family:SimHei,黑体,sans-serif;'
                f'font-size:18px;font-weight:800;">{html.escape(ln.strip())}</p>'
            )
            continue

        parts.append(f'<p style="margin:0 0 14px 0;">{html.escape(ln)}</p>')

    parts.append("</div>")
    return "".join(parts)


# =============================
# 4) 抓取（识别验证页 + 多 UA 重试 + 缓存）
# =============================
VERIFY_KEYWORDS = [
    "环境异常", "访问过于频繁", "请在微信客户端打开",
    "请输入验证码", "安全验证", "验证后继续",
]

UA_LIST = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
]

@st.cache_data(ttl=600, show_spinner=False)
def fetch_page_cached(url: str, ua_idx: int):
    headers = {"User-Agent": UA_LIST[ua_idx], "Accept-Language": "zh-CN,zh;q=0.9"}
    res = requests.get(url, headers=headers, timeout=12)
    return res.status_code, res.text


def looks_like_verify_page(page_html: str) -> bool:
    if not page_html:
        return True
    s = page_html[:20000]
    return any(k in s for k in VERIFY_KEYWORDS)


def extract_wechat_text(page_html: str):
    soup = BeautifulSoup(page_html, "html.parser")
    content_div = soup.find("div", id="js_content")
    return content_div.get_text(separator="\n", strip=True) if content_div else None


def get_article_text_smart(url: str):
    last_hint = None
    for attempt, ua_idx in enumerate([0, 1, 2], start=1):
        try:
            status_code, page_html = fetch_page_cached(url, ua_idx)
            if status_code != 200:
                last_hint = f"抓取失败 HTTP {status_code}（第{attempt}次尝试）"
                continue
            if looks_like_verify_page(page_html):
                last_hint = f"疑似验证/拦截页（第{attempt}次尝试）"
                continue
            text = extract_wechat_text(page_html)
            if not text:
                last_hint = f"未找到正文区域 js_content（第{attempt}次尝试）"
                continue
            return text, "来自链接抓取"
        except requests.exceptions.Timeout:
            last_hint = f"抓取超时（第{attempt}次尝试）"
        except requests.exceptions.RequestException as e:
            last_hint = f"抓取网络错误：{e}（第{attempt}次尝试）"
    return None, (last_hint or "抓取失败")


# =============================
# 5) DeepSeek 流式（温度/篇幅）
# =============================
def length_to_max_tokens(length_mode: str) -> int:
    if length_mode == "短":
        return 1200
    if length_mode == "长":
        return 2600
    return 1800


def length_to_hint(length_mode: str) -> str:
    if length_mode == "短":
        return "正文尽量精炼，信息密度高，控制在约900-1200字。"
    if length_mode == "长":
        return "正文更充分展开，增加细节与案例，控制在约1800-2400字。"
    return "正文适中展开，控制在约1200-1800字。"


def stream_ai_rewrite(text: str, api_key: str, temperature: float, length_mode: str):
    url = "https://api.deepseek.com/chat/completions"
    system_prompt = f"""假设你是一个专业的自媒体作家。对下文进行二创。
【原创加强建议】：句型词汇调整、内容拓展、避免关键词、结构逻辑调整、视角切换、重点聚焦、角度转换、避免直接引用。
【核心禁令】：
- 永远不要出现“不是....，而是”的句式。
- 绝对不要出现破折号（——）。
- 绝对禁止结构化：禁止使用列表、分点（如1.2.3.或●），保持段落连贯性。
【输出结构】：
1. 第一行写【推荐爆款标题】，接着输出5个爆款标题，每行一个（保留标题标点）。
2. 标题区后空三行。
3. 正文开头必须先写150字引入语。
4. 小标题格式固定为 ## 01. XXX，总数控制在 2-4 个。
【篇幅要求】：{length_to_hint(length_mode)}
"""
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"原文=（{text}）"}
        ],
        "stream": True,
        "temperature": float(temperature),
        "max_tokens": int(length_to_max_tokens(length_mode)),
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    return requests.post(url, headers=headers, json=payload, stream=True, timeout=120)


# =============================
# 6) 输出组件：高度自动适配（clamp）
#    手机：360~420  左右；桌面：520~640 左右
# =============================
SCROLLBOX_HEIGHT_CSS = "clamp(360px, 60vh, 640px)"  # ✅ 核心：自动适配
IFRAME_HEIGHT = 820  # iframe 高度留够（内部滚动区自动控制）


def render_block_with_copy_rich(rich_html: str, plain_fallback: str, title: str):
    rich_js = json.dumps(rich_html)
    plain_js = json.dumps(plain_fallback)
    title_esc = html.escape(title)

    components.html(f"""
<div style="border:1px solid #07c160;border-radius:10px;background:#fff;padding:14px;">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
    <div style="font-weight:900;color:#000;font-family:Microsoft YaHei;">{title_esc}</div>

    <button id="copyBtn"
      style="background:#07c160;color:#fff;border:none;border-radius:8px;
             padding:8px 12px;cursor:pointer;font-weight:900;flex-shrink:0;">
      📋 复制
    </button>
  </div>

  <div class="scrollbox" style="height:{SCROLLBOX_HEIGHT_CSS}; overflow-y:auto; padding-right:6px;">
    <style>
      .scrollbox::-webkit-scrollbar {{ width: 8px; }}
      .scrollbox::-webkit-scrollbar-thumb {{ background: #bdeed6; border-radius: 10px; }}
      .scrollbox::-webkit-scrollbar-track {{ background: #f6fffa; }}
    </style>
    {rich_html}
  </div>
</div>

<script>
async function copyRich(){{
  const htmlText = {rich_js};
  const plainText = {plain_js};

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

  try {{
    await navigator.clipboard.writeText(plainText);
    alert("已复制（降级为纯文本）");
  }} catch(e) {{
    alert("复制失败：请使用 HTTPS 或更换浏览器");
  }}
}}

document.getElementById("copyBtn").addEventListener("click", copyRich);
</script>
""", height=IFRAME_HEIGHT)


def render_block_with_copy_markdown(md_text: str, title: str):
    md_esc = html.escape(md_text)
    md_js = json.dumps(md_text)
    title_esc = html.escape(title)

    components.html(f"""
<div style="border:1px solid #07c160;border-radius:10px;background:#fff;padding:14px;">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
    <div style="font-weight:900;color:#000;font-family:Microsoft YaHei;">{title_esc}</div>

    <button id="copyBtnMd"
      style="background:#07c160;color:#fff;border:none;border-radius:8px;
             padding:8px 12px;cursor:pointer;font-weight:900;flex-shrink:0;">
      📋 复制
    </button>
  </div>

  <div class="scrollbox" style="height:{SCROLLBOX_HEIGHT_CSS}; overflow-y:auto; padding-right:6px;">
    <style>
      .scrollbox::-webkit-scrollbar {{ width: 8px; }}
      .scrollbox::-webkit-scrollbar-thumb {{ background: #bdeed6; border-radius: 10px; }}
      .scrollbox::-webkit-scrollbar-track {{ background: #f6fffa; }}
    </style>

    <pre style="margin:0;white-space:pre-wrap;line-height:1.8;font-size:14px;
                font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,'Liberation Mono','Courier New',monospace;
                background:#ffffff;border-radius:8px;">{md_esc}</pre>
  </div>
</div>

<script>
async function copyMd(){{
  const text = {md_js};
  try {{
    await navigator.clipboard.writeText(text);
    alert("Markdown 已复制");
  }} catch(e) {{
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
""", height=IFRAME_HEIGHT)


# =============================
# 7) 页面：输入 + 高级设置（标签行）+ 手动兜底
# =============================
target_url = st.text_input("🔗 粘贴链接开始深度重构")

with st.expander("高级设置（可选）", expanded=False):
    st.markdown("**风格强度（temperature）**")
    st.caption("越低越稳（更像改写/更少发散）；越高越创意（更敢改但更易跑题）")

    temperature = st.slider("风格强度（建议 0.70–0.85）", 0.5, 1.0, 0.8, 0.05)

    # 直观标签行
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.markdown("<div style='text-align:left;font-size:12px;color:#666;'>0.50<br><b>最稳</b></div>", unsafe_allow_html=True)
    c2.markdown("<div style='text-align:center;font-size:12px;color:#666;'>0.65<br>稳</div>", unsafe_allow_html=True)
    c3.markdown("<div style='text-align:center;font-size:12px;color:#666;'>0.80<br><b>推荐</b></div>", unsafe_allow_html=True)
    c4.markdown("<div style='text-align:center;font-size:12px;color:#666;'>0.90<br>创意</div>", unsafe_allow_html=True)
    c5.markdown("<div style='text-align:right;font-size:12px;color:#666;'>1.00<br><b>最创意</b></div>", unsafe_allow_html=True)

    if temperature <= 0.65:
        st.info("当前：偏稳 ✅ 适合严肃科普/降AI味/少发散")
    elif temperature <= 0.85:
        st.success("当前：均衡 ⭐ 推荐默认（稳定 + 有一定改写力度）")
    else:
        st.warning("当前：偏创意 ⚠️ 适合标题党/情绪化文风，但可能更容易跑题")

    st.markdown("---")
    st.markdown("**篇幅**")
    length_mode = st.selectbox("选择输出长度", ["中", "短", "长"], index=0)
    st.caption("短：更精炼；中：默认；长：更充分展开（更耗 tokens）")

with st.expander("抓取失败？这里可手动粘贴原文继续生成（可选）", expanded=False):
    st.session_state.manual_text = st.text_area(
        "📄 粘贴原文（抓不到链接时会自动用这里的内容）",
        value=st.session_state.manual_text,
        height=180,
        placeholder="当公众号链接抓取失败（验证/403/空内容）时，把文章原文粘贴到这里再点“开始生成”。"
    )

if st.session_state.last_error and (not st.session_state.is_generating):
    st.error(st.session_state.last_error)

# 两个按钮：开始生成 / 再生成一次
col1, col2 = st.columns([2, 1])
with col1:
    btn_text = "正在生成中..." if st.session_state.is_generating else "开始生成"
    clicked_generate = st.button(btn_text, disabled=st.session_state.is_generating, key="gen_btn")

with col2:
    can_regen = (st.session_state.last_source_text is not None) and (not st.session_state.is_generating)
    clicked_regen = st.button("再生成一次", disabled=not can_regen, key="regen_btn")

if clicked_generate and not st.session_state.is_generating:
    st.session_state.is_generating = True
    st.session_state.use_last_source = False
    st.session_state.last_error = None
    st.rerun()

if clicked_regen and (not st.session_state.is_generating) and st.session_state.last_source_text:
    st.session_state.is_generating = True
    st.session_state.use_last_source = True
    st.session_state.last_error = None
    st.rerun()

# 展示上一次结果
if (not st.session_state.is_generating) and st.session_state.result_md:
    if st.session_state.last_source_hint:
        st.caption(f"上次原文：{st.session_state.last_source_hint}")

    st.subheader("🖨️ 1) 一键复制：保留字体字号（富文本）")
    render_block_with_copy_rich(
        rich_html=st.session_state.result_rich_html,
        plain_fallback=st.session_state.result_plain,
        title="富文本成品（小标题黑体18 / 正文宋体17）"
    )

    st.subheader("🧾 2) 一键复制：Markdown 原文")
    render_block_with_copy_markdown(
        md_text=st.session_state.result_md,
        title="Markdown 原文（原样显示）"
    )


# =============================
# 8) 生成流程
# =============================
if st.session_state.is_generating:
    try:
        api_key = st.secrets.get("DEEPSEEK_API_KEY")
        if not api_key:
            st.session_state.last_error = "未检测到 DEEPSEEK_API_KEY，请在 .streamlit/secrets.toml 配置。"
            st.session_state.is_generating = False
            st.rerun()

        source_text = None
        source_hint = None

        # 1) 再生成一次：直接用上一次原文
        if st.session_state.use_last_source and st.session_state.last_source_text:
            source_text = st.session_state.last_source_text
            source_hint = "来自上一次原文（再生成一次）"
        else:
            # 2) URL 抓取 -> 失败用手动
            if target_url.strip():
                with st.spinner("正在抓取文章内容…"):
                    text, hint = get_article_text_smart(target_url.strip())
                if text:
                    source_text = text
                    source_hint = hint
                else:
                    manual = (st.session_state.manual_text or "").strip()
                    if manual:
                        source_text = manual
                        source_hint = f"链接抓取不可用（{hint}），改用手动原文"
                    else:
                        st.session_state.last_error = f"内容抓取失败：{hint}。你可以展开“手动粘贴原文”后再生成。"
                        st.session_state.is_generating = False
                        st.rerun()
            else:
                manual = (st.session_state.manual_text or "").strip()
                if manual:
                    source_text = manual
                    source_hint = "来自手动粘贴原文"
                else:
                    st.session_state.last_error = "请粘贴链接，或展开“手动粘贴原文”输入内容后再生成。"
                    st.session_state.is_generating = False
                    st.rerun()

        st.session_state.last_source_text = source_text
        st.session_state.last_source_hint = source_hint

        st.info("正在生成中，请稍候…")

        full_content = ""
        placeholder = st.empty()
        progress = st.empty()

        response = stream_ai_rewrite(
            text=source_text,
            api_key=api_key,
            temperature=temperature,
            length_mode=length_mode
        )

        if response.status_code != 200:
            msg = response.text[:400] if response.text else ""
            st.session_state.last_error = f"模型接口请求失败：HTTP {response.status_code}\n\n{msg}"
            st.session_state.is_generating = False
            st.session_state.use_last_source = False
            st.rerun()

        last_render_len = 0
        last_tick = time.time()

        for line in response.iter_lines():
            if not line:
                continue
            chunk = line.decode("utf-8", errors="ignore").removeprefix("data: ").strip()
            if chunk == "[DONE]":
                break
            try:
                data = json.loads(chunk)
                delta = data["choices"][0]["delta"].get("content", "")
                if not delta:
                    continue
                full_content += delta

                # 节流：每 60 字或 0.25s 刷新一次
                now = time.time()
                if (len(full_content) - last_render_len >= 60) or (now - last_tick >= 0.25):
                    last_render_len = len(full_content)
                    last_tick = now
                    progress.caption(f"已生成约 {len(full_content)} 字…")
                    placeholder.markdown(safety_filter(full_content) + "▌")
            except:
                continue

        progress.empty()
        placeholder.empty()

        md_final = safety_filter(full_content)
        plain_final = to_plain_text(md_final)
        rich_html_out = build_rich_html(plain_final)

        st.session_state.result_md = md_final
        st.session_state.result_plain = plain_final
        st.session_state.result_rich_html = rich_html_out
        st.session_state.last_error = None

        st.session_state.is_generating = False
        st.session_state.use_last_source = False
        st.rerun()

    except requests.exceptions.Timeout:
        st.session_state.last_error = "请求超时：可能网络不稳定或接口响应慢。请稍后重试。"
        st.session_state.is_generating = False
        st.session_state.use_last_source = False
        st.rerun()

    except requests.exceptions.RequestException as e:
        st.session_state.last_error = f"网络请求异常：{e}"
        st.session_state.is_generating = False
        st.session_state.use_last_source = False
        st.rerun()

    except Exception as e:
        st.session_state.last_error = f"发生未知错误：{e}"
        st.session_state.is_generating = False
        st.session_state.use_last_source = False
        st.rerun()
