import streamlit as st
import streamlit.components.v1 as components
import requests
import json
from bs4 import BeautifulSoup
import re
import html
import time

# =============================
# 1) UI：微信绿 + 强制浅色 + 手机自适配 + Tabs文字强制常显
# =============================
st.set_page_config(page_title="高级原创二创助手", layout="centered")

st.markdown("""
<style>
/* 强制浅色：不受系统深色影响 */
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

/* 下拉选择 */
div[data-baseweb="select"] > div {
  background: #ffffff !important;
  color: #000000 !important;
  border-radius: 12px !important;
  border: 1px solid rgba(7,193,96,0.45) !important;
}

/* Slider 文案颜色 */
div[data-baseweb="slider"] * { color: #000000 !important; }

/* 绿色按钮覆盖 */
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

/* Tabs：强制文字常显（解决“只显示图标/悬停才显示”） */
div[data-baseweb="tab-list"] button * {
  opacity: 1 !important;
  visibility: visible !important;
  display: inline !important;
  font-size: 16px !important;
  font-weight: 900 !important;
  color: #000 !important;
}
div[data-baseweb="tab-list"] button[aria-selected="true"] * {
  color: #07c160 !important;
}
div[data-baseweb="tab-list"] {
  gap: 12px !important;
}

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

/* 手机端自适配 */
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
def ss_init(key, default):
    if key not in st.session_state:
        st.session_state[key] = default

ss_init("is_generating", False)
ss_init("last_source_text", None)
ss_init("last_source_hint", None)
ss_init("use_last_source", False)
ss_init("manual_text", "")
ss_init("last_error", None)

# 生成结果（只用于导入编辑器）
ss_init("result_md", None)
ss_init("result_plain", None)
ss_init("result_rich_html", "")

# 编辑器内容（始终从这里读）
ss_init("editor_initial_html", "")

# 生成完自动跳到“手动排版”
ss_init("jump_to_editor", False)


# =============================
# 3) 文本处理：不乱删标点，标题强制换行
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

    # 若标题挤一行，仅用 ;；|｜/ 分割，不动逗号顿号等标点
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
    # 禁止破折号（——），但不删除其它标题标点
    text = text.replace("——", " ").replace("—", " ")
    # 小标题前加空行
    text = re.sub(r'(\n?)(##\s*0[1-4]\.)', r'\n\n\2', text)
    return format_title_block(text)


def to_plain_text(md_text: str) -> str:
    t = md_text
    t = re.sub(r'^\s*##\s*', '', t, flags=re.MULTILINE)     # 去掉Markdown小标题符号
    t = re.sub(r'\*\*(.+?)\*\*', r'\1', t)
    t = re.sub(r'\*(.+?)\*', r'\1', t)
    t = re.sub(r'`(.+?)`', r'\1', t)
    t = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', t)
    return t


def build_rich_html(plain_text: str) -> str:
    """
    小标题黑体18 / 正文宋体17 / 行距2
    折叠连续空行，避免大空白
    """
    lines = plain_text.split("\n")
    parts = ['<div style="font-family:SimSun,宋体,serif;font-size:17px;line-height:2;color:#000;">']
    prev_blank = False

    for ln in lines:
        if ln.strip() == "":
            if prev_blank:
                continue
            prev_blank = True
            parts.append('<p style="margin:0 0 14px 0; line-height:1;"><br/></p>')
            continue

        prev_blank = False

        # 把 “01. xxx” 这种作为小标题（导入编辑器后也能识别）
        if re.match(r'^\s*0[1-4]\.\s*.+\s*$', ln):
            parts.append(
                f'<h2 style="margin:18px 0 8px 0;font-family:SimHei,黑体,sans-serif;'
                f'font-size:18px;font-weight:800;border-left:5px solid #07c160;'
                f'padding-left:10px;">{html.escape(ln.strip())}</h2>'
            )
            continue

        # 爆款标题区的“【推荐爆款标题】”也当小标题
        if ln.strip() == "【推荐爆款标题】":
            parts.append(
                f'<h2 style="margin:18px 0 8px 0;font-family:SimHei,黑体,sans-serif;'
                f'font-size:18px;font-weight:800;border-left:5px solid #07c160;'
                f'padding-left:10px;">{html.escape(ln.strip())}</h2>'
            )
            continue

        parts.append(f'<p style="margin:0 0 14px 0;">{html.escape(ln)}</p>')

    parts.append("</div>")
    return "".join(parts)


# =============================
# 4) 抓取：识别验证页 + 多UA重试 + 缓存
# =============================
VERIFY_KEYWORDS = ["环境异常", "访问过于频繁", "请在微信客户端打开", "请输入验证码", "安全验证", "验证后继续"]
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
# 5) DeepSeek 流式生成
# =============================
def length_to_max_tokens(length_mode: str) -> int:
    return {"短": 1200, "中": 1800, "长": 2600}.get(length_mode, 1800)

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
        "messages": [{"role": "system", "content": system_prompt},
                     {"role": "user", "content": f"原文=（{text}）"}],
        "stream": True,
        "temperature": float(temperature),
        "max_tokens": int(length_to_max_tokens(length_mode)),
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    return requests.post(url, headers=headers, json=payload, stream=True, timeout=120)


# =============================
# 6) 免Key编辑器（Quill）：一键排版 + 复制富文本 + 复制Markdown
# =============================
def render_wechat_editor(initial_html: str):
    init_js = json.dumps(initial_html or "")

    components.html(f"""
<link href="https://cdn.jsdelivr.net/npm/quill@1.3.7/dist/quill.snow.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/quill@1.3.7/dist/quill.min.js"></script>
<script src="https://unpkg.com/turndown/dist/turndown.js"></script>

<div style="border:1px solid #07c160;border-radius:12px;background:#fff;padding:12px;">

  <div style="display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap;">
    <div style="font-weight:900;font-family:Microsoft YaHei;color:#000;font-size:18px;">
      公众号排版编辑器（所见即所得）
    </div>

    <div style="display:flex;gap:10px;flex-wrap:wrap;">
      <button id="btnApply" style="background:#07c160;color:#fff;border:none;border-radius:10px;padding:10px 14px;cursor:pointer;font-weight:900;">✨ 一键排版</button>
      <button id="btnCopyRich" style="background:#07c160;color:#fff;border:none;border-radius:10px;padding:10px 14px;cursor:pointer;font-weight:900;">📋 复制富文本</button>
      <button id="btnCopyMd" style="background:#07c160;color:#fff;border:none;border-radius:10px;padding:10px 14px;cursor:pointer;font-weight:900;">🧾 复制Markdown</button>
    </div>
  </div>

  <!-- 工具栏（更像公众号后台） -->
  <div id="toolbar" style="margin-top:12px;border:1px solid rgba(0,0,0,0.08);border-radius:10px;">
    <span class="ql-formats">
      <button class="ql-undo" type="button">↶</button>
      <button class="ql-redo" type="button">↷</button>
    </span>

    <span class="ql-formats">
      <select class="ql-size">
        <option value="14px">14px</option>
        <option value="17px" selected>17px</option>
        <option value="18px">18px</option>
        <option value="22px">22px</option>
      </select>
    </span>

    <span class="ql-formats">
      <button class="ql-bold"></button>
      <button class="ql-italic"></button>
      <button class="ql-underline"></button>
      <button class="ql-strike"></button>
    </span>

    <span class="ql-formats">
      <select class="ql-color"></select>
      <select class="ql-background"></select>
      <button class="ql-clean"></button>
    </span>

    <span class="ql-formats">
      <button class="ql-align" value=""></button>
      <button class="ql-align" value="center"></button>
      <button class="ql-align" value="right"></button>
      <button class="ql-align" value="justify"></button>
    </span>

    <span class="ql-formats">
      <button class="ql-indent" value="-1"></button>
      <button class="ql-indent" value="+1"></button>
    </span>

    <span class="ql-formats">
      <button class="ql-list" value="ordered"></button>
      <button class="ql-list" value="bullet"></button>
      <button class="ql-blockquote"></button>
      <button class="ql-code-block"></button>
    </span>

    <span class="ql-formats">
      <button id="btnHr" type="button">—</button>
      <button id="btnTable" type="button">▦</button>
      <button id="btnEmoji" type="button">😊</button>
    </span>
  </div>

  <div id="editor" style="margin-top:10px;border:1px solid rgba(0,0,0,0.08);border-radius:12px;"></div>

  <div style="margin-top:10px;color:#666;font-size:12px;line-height:1.6;">
    提示：一键排版=默认“小标题黑体18/正文宋体17/行距2/左绿条”。复制富文本可直接贴公众号后台。
  </div>
</div>

<style>
.ql-container {{ border: none !important; font-family: SimSun, 宋体, serif; }}
.ql-editor {{
  min-height: 520px;
  font-size: 17px;
  line-height: 2;
  color: #000;
}}
.ql-toolbar.ql-snow {{
  border: none !important;
  border-bottom: 1px solid rgba(0,0,0,0.08) !important;
  border-top-left-radius: 10px;
  border-top-right-radius: 10px;
}}
@media (max-width: 768px) {{
  .ql-editor {{ min-height: 420px; }}
}}
</style>

<script>
const INITIAL_HTML = {init_js};

const Size = Quill.import('attributors/style/size');
Size.whitelist = ['14px','17px','18px','22px'];
Quill.register(Size, true);

const quill = new Quill('#editor', {{
  theme: 'snow',
  modules: {{
    toolbar: '#toolbar',
    history: {{ delay: 300, maxStack: 100, userOnly: true }}
  }}
}});

// 初始化内容
if (INITIAL_HTML && INITIAL_HTML.trim()) {{
  quill.clipboard.dangerouslyPasteHTML(INITIAL_HTML);
}}

// undo/redo
document.querySelector('.ql-undo').addEventListener('click', () => quill.history.undo());
document.querySelector('.ql-redo').addEventListener('click', () => quill.history.redo());

// HR
document.getElementById('btnHr').addEventListener('click', () => {{
  const range = quill.getSelection(true) || {{ index: quill.getLength() }};
  quill.clipboard.dangerouslyPasteHTML(range.index, '<p><hr/></p>');
}});

// 表格（基础2x2）
document.getElementById('btnTable').addEventListener('click', () => {{
  const range = quill.getSelection(true) || {{ index: quill.getLength() }};
  const table = `
    <table style="border-collapse:collapse;width:100%;margin:10px 0;">
      <tr>
        <td style="border:1px solid #ccc;padding:8px;">单元格</td>
        <td style="border:1px solid #ccc;padding:8px;">单元格</td>
      </tr>
      <tr>
        <td style="border:1px solid #ccc;padding:8px;">单元格</td>
        <td style="border:1px solid #ccc;padding:8px;">单元格</td>
      </tr>
    </table><p></p>`;
  quill.clipboard.dangerouslyPasteHTML(range.index, table);
}});

// 表情（基础插入）
document.getElementById('btnEmoji').addEventListener('click', () => {{
  const emojis = ['😀','😁','😂','🥹','😊','😍','👍','🔥','✅','⭐','📌','🧠'];
  const pick = prompt('输入序号选择表情：\\n' + emojis.map((e,i)=>`${{i+1}}. ${{e}}`).join('\\n'));
  const n = parseInt(pick||'');
  if (!n || n<1 || n>emojis.length) return;
  const range = quill.getSelection(true) || {{ index: quill.getLength() }};
  quill.insertText(range.index, emojis[n-1]);
}});

// 一键排版：默认公众号风格 + 自动识别“01.”段落转小标题
function applyWechatLayout() {{
  const root = document.querySelector('#editor .ql-editor');
  if (!root) return;

  root.style.fontFamily = 'SimSun,宋体,serif';
  root.style.fontSize = '17px';
  root.style.lineHeight = '2';
  root.style.color = '#000';

  root.querySelectorAll('p').forEach(p => {{
    p.style.margin = '0 0 14px 0';
    p.style.fontFamily = 'SimSun,宋体,serif';
    p.style.fontSize = '17px';
    p.style.lineHeight = '2';
    p.style.color = '#000';
  }});

  root.querySelectorAll('p').forEach(p => {{
    const t = (p.innerText || '').trim();
    if (/^0[1-4]\\.\\s+/.test(t) || t === "【推荐爆款标题】") {{
      const h2 = document.createElement('h2');
      h2.innerText = t;
      h2.style.fontFamily = 'SimHei,黑体,sans-serif';
      h2.style.fontSize = '18px';
      h2.style.fontWeight = '800';
      h2.style.margin = '18px 0 8px 0';
      h2.style.borderLeft = '5px solid #07c160';
      h2.style.paddingLeft = '10px';
      h2.style.color = '#000';
      p.replaceWith(h2);
    }}
  }});

  alert('已应用公众号排版');
}}

document.getElementById('btnApply').addEventListener('click', applyWechatLayout);

// 复制富文本：强制inline样式后写入剪贴板
async function copyRichAll() {{
  const root = document.querySelector('#editor .ql-editor');
  if (!root) return;

  const clone = root.cloneNode(true);
  clone.querySelectorAll('p').forEach(p => {{
    p.style.margin = '0 0 14px 0';
    p.style.fontFamily = 'SimSun,宋体,serif';
    p.style.fontSize = '17px';
    p.style.lineHeight = '2';
    p.style.color = '#000';
  }});
  clone.querySelectorAll('h2').forEach(h2 => {{
    h2.style.fontFamily = 'SimHei,黑体,sans-serif';
    h2.style.fontSize = '18px';
    h2.style.fontWeight = '800';
    h2.style.margin = '18px 0 8px 0';
    h2.style.borderLeft = '5px solid #07c160';
    h2.style.paddingLeft = '10px';
    h2.style.color = '#000';
  }});

  const htmlText = `<div style="font-family:SimSun,宋体,serif;font-size:17px;line-height:2;color:#000;">${{clone.innerHTML}}</div>`;
  const plainText = root.innerText || '';

  try {{
    if (navigator.clipboard && window.ClipboardItem) {{
      const htmlBlob = new Blob([htmlText], {{ type: "text/html" }});
      const textBlob = new Blob([plainText], {{ type: "text/plain" }});
      const item = new ClipboardItem({{
        "text/html": htmlBlob,
        "text/plain": textBlob
      }});
      await navigator.clipboard.write([item]);
      alert("已复制（富文本，保留样式）");
      return;
    }}
  }} catch(e) {{}}

  try {{
    const temp = document.createElement('div');
    temp.setAttribute('contenteditable','true');
    temp.style.position='fixed';
    temp.style.left='-9999px';
    temp.innerHTML = htmlText;
    document.body.appendChild(temp);

    const range = document.createRange();
    range.selectNodeContents(temp);
    const sel = window.getSelection();
    sel.removeAllRanges();
    sel.addRange(range);

    document.execCommand('copy');
    sel.removeAllRanges();
    document.body.removeChild(temp);
    alert("已复制（富文本，保留样式）");
  }} catch(e) {{
    alert("复制失败：请使用 HTTPS 或更换浏览器");
  }}
}}
document.getElementById('btnCopyRich').addEventListener('click', copyRichAll);

// 复制 Markdown：HTML -> Markdown
async function copyMarkdownAll() {{
  const root = document.querySelector('#editor .ql-editor');
  if (!root) return;

  const htmlInner = root.innerHTML || '';
  let md = '';
  try {{
    const service = new TurndownService({{
      headingStyle: 'atx',
      codeBlockStyle: 'fenced',
      emDelimiter: '*'
    }});
    md = service.turndown(htmlInner);
  }} catch(e) {{
    md = root.innerText || '';
  }}

  try {{
    await navigator.clipboard.writeText(md);
    alert("已复制 Markdown");
  }} catch(e) {{
    const el = document.createElement("textarea");
    el.value = md;
    document.body.appendChild(el);
    el.select();
    document.execCommand('copy');
    document.body.removeChild(el);
    alert("已复制 Markdown");
  }}
}}
document.getElementById('btnCopyMd').addEventListener('click', copyMarkdownAll);
</script>
""", height=820)


# =============================
# 7) 生成完成后：自动切到“手动排版”Tab（JS点击Tab）
# =============================
def jump_to_tab_by_text(tab_text: str):
    # 通过 DOM 找到包含 tab_text 的 tab 按钮并 click
    safe_text = json.dumps(tab_text)
    components.html(f"""
<script>
(function(){{
  const target = {safe_text};
  const tabs = parent.document.querySelectorAll('button[data-baseweb="tab"]');
  for (const b of tabs) {{
    const t = (b.innerText || '').trim();
    if (t.includes(target)) {{
      b.click();
      break;
    }}
  }}
}})();
</script>
""", height=0)


# =============================
# 8) 页面：两个Tab（文字常显）
# =============================
tab_gen, tab_manual = st.tabs(["🚀 二创生成", "📝 手动排版"])


# -----------------------------
# Tab 1：二创生成（生成完直接导入编辑器，不再显示富文本/Markdown输出框）
# -----------------------------
with tab_gen:
    target_url = st.text_input("🔗 粘贴链接开始深度重构")

    with st.expander("高级设置（可选）", expanded=False):
        st.markdown("**风格强度（temperature）**")
        st.caption("越低越稳（更像改写/更少发散）；越高越创意（更敢改但更易跑题）")
        temperature = st.slider("风格强度（建议 0.70–0.85）", 0.5, 1.0, 0.8, 0.05)

        st.markdown("---")
        length_mode = st.selectbox("篇幅", ["中", "短", "长"], index=0)
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

    if clicked_regen and can_regen:
        st.session_state.is_generating = True
        st.session_state.use_last_source = True
        st.session_state.last_error = None
        st.rerun()

    # 生成中：展示实时预览（不作为最终输出）
    if st.session_state.is_generating:
        st.info("正在生成中，请稍候…")
        live_placeholder = st.empty()
        live_progress = st.empty()

        try:
            api_key = st.secrets.get("DEEPSEEK_API_KEY")
            if not api_key:
                st.session_state.last_error = "未检测到 DEEPSEEK_API_KEY，请在 .streamlit/secrets.toml 配置。"
                st.session_state.is_generating = False
                st.rerun()

            # 获取原文
            source_text = None
            source_hint = None

            if st.session_state.use_last_source and st.session_state.last_source_text:
                source_text = st.session_state.last_source_text
                source_hint = "来自上一次原文（再生成一次）"
            else:
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

            # 调模型
            full_content = ""
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

                    now = time.time()
                    if (len(full_content) - last_render_len >= 80) or (now - last_tick >= 0.25):
                        last_render_len = len(full_content)
                        last_tick = now
                        live_progress.caption(f"已生成约 {len(full_content)} 字…")
                        live_placeholder.markdown(safety_filter(full_content) + "▌")
                except:
                    continue

            live_progress.empty()
            live_placeholder.empty()

            md_final = safety_filter(full_content)
            plain_final = to_plain_text(md_final)
            rich_html_out = build_rich_html(plain_final)

            # 保存结果（但页面不再单独显示富文本/markdown）
            st.session_state.result_md = md_final
            st.session_state.result_plain = plain_final
            st.session_state.result_rich_html = rich_html_out

            # ✅ 关键：生成完直接塞进编辑器（默认排版已带好）
            st.session_state.editor_initial_html = rich_html_out

            # ✅ 自动跳到“手动排版”
            st.session_state.jump_to_editor = True

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

    # 非生成中：给一个提示（避免用户找不到结果）
    if (not st.session_state.is_generating) and st.session_state.editor_initial_html:
        st.success("✅ 已生成完成，并已自动导入到「手动排版」编辑器。你可以切换到上方「手动排版」继续修改。")


# -----------------------------
# Tab 2：手动排版（页面只显示这个编辑器 + 复制富文本/markdown）
# -----------------------------
with tab_manual:
    st.subheader("🧩 公众号后台同款排版（工具栏 + 一键排版 + 一键复制）")

    # 可选操作：导入/清空（不冗余输出框）
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("📥 导入：上次生成的内容", disabled=not bool(st.session_state.result_rich_html), key="import_last"):
            st.session_state.editor_initial_html = st.session_state.result_rich_html or ""
            st.success("已导入。")
    with c2:
        if st.button("🧹 清空编辑器内容", key="clear_editor"):
            st.session_state.editor_initial_html = ""
            st.success("已清空。")

    render_wechat_editor(st.session_state.editor_initial_html)


# 自动跳tab：放到页面最后执行更稳
if st.session_state.jump_to_editor:
    st.session_state.jump_to_editor = False
    jump_to_tab_by_text("手动排版")
