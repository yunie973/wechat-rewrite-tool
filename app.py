import streamlit as st
import streamlit.components.v1 as components
import requests
import json
from bs4 import BeautifulSoup
import re
import html
import time

# =============================
# 0) Page
# =============================
st.set_page_config(page_title="高级原创二创助手", layout="centered")

# =============================
# 1) Theme + Tabs 文案常显
# =============================
st.markdown("""
<style>
:root, body, .stApp { color-scheme: light !important; }
.stApp { background:#fff !important; color:#000 !important; padding-bottom: 90px; }

h1 { color:#07c160 !important; font-family:"Microsoft YaHei"; text-align:center; font-weight:900; }

.stTextInput > div > div {
  border: 2px solid #07c160 !important;
  border-radius: 12px !important;
  background: #ffffff !important;
}
.stTextInput input {
  background:#fff !important;
  color:#000 !important;
  font-weight:700 !important;
}

div[data-baseweb="select"] > div{
  background:#fff !important;
  color:#000 !important;
  border-radius:12px !important;
  border:1px solid rgba(7,193,96,0.45) !important;
}
div[data-baseweb="slider"] * { color:#000 !important; }

/* 覆盖按钮为绿色 */
div.stButton > button{
  background:#07c160 !important;
  color:#fff !important;
  border:none !important;
  border-radius:10px !important;
  font-weight:900 !important;
  height:46px !important;
  width:100% !important;
}
div.stButton > button:hover{ background:#06b457 !important; }
div.stButton > button:disabled{ background:#9be4be !important; color:#fff !important; }

/* Tabs：文字常显 */
div[data-baseweb="tab-list"] button *{
  opacity:1 !important;
  visibility:visible !important;
  display:inline !important;
  font-size:16px !important;
  font-weight:900 !important;
  color:#000 !important;
}
div[data-baseweb="tab-list"] button[aria-selected="true"] *{ color:#07c160 !important; }
div[data-baseweb="tab-list"]{ gap:12px !important; }

/* Footer */
.footer{
  position:fixed; left:0; bottom:0; width:100%;
  background:#fff; padding:12px 0; border-top:2px solid #07c160;
  z-index:999; display:flex; justify-content:center; align-items:center; gap:20px;
}
.qr-item{ color:#07c160; font-weight:900; cursor:pointer; position:relative; }
.qr-box{
  display:none; position:absolute; bottom:45px; left:50%;
  transform:translateX(-50%); width:180px; background:#fff;
  padding:10px; border:2px solid #07c160; border-radius:10px;
  box-shadow:0 8px 25px rgba(0,0,0,0.2);
}
.qr-item:hover .qr-box{ display:block; }

@media (max-width:768px){
  h1{ font-size:26px !important; }
  div.stButton > button{ height:50px !important; border-radius:12px !important; }
  .stApp{ padding-bottom:20px !important; }
  .footer{ position:relative !important; border-top:1px solid rgba(7,193,96,0.35) !important; padding:10px 0 !important; gap:12px !important; }
  .qr-box{ width:150px !important; }
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
def ss_init(k, v):
    if k not in st.session_state:
        st.session_state[k] = v

ss_init("is_generating", False)
ss_init("manual_text", "")
ss_init("last_source_text", None)
ss_init("last_error", None)

ss_init("result_md", "")
ss_init("result_plain", "")
ss_init("result_rich_html", "")

ss_init("editor_initial_html", "")
ss_init("editor_version", 0)
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

    # 只用 ;；|｜/ 分割（不动逗号顿号等标点）
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
        return "不单是" + m.group("a") + "更是"
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
    prev_blank = False

    for ln in lines:
        if ln.strip() == "":
            if prev_blank:
                continue
            prev_blank = True
            parts.append('<p style="margin:0 0 14px 0; line-height:1;"><br/></p>')
            continue

        prev_blank = False
        s = ln.strip()

        if re.match(r'^0[1-4]\.\s+.+$', s) or s == "【推荐爆款标题】":
            parts.append(
                f'<h2 style="margin:18px 0 8px 0;font-family:SimHei,黑体,sans-serif;'
                f'font-size:18px;font-weight:800;border-left:5px solid #07c160;'
                f'padding-left:10px;">{html.escape(s)}</h2>'
            )
        else:
            parts.append(f'<p style="margin:0 0 14px 0;">{html.escape(ln)}</p>')

    parts.append("</div>")
    return "".join(parts)

# =============================
# 4) 抓取（尽量抗验证）
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
            code, page_html = fetch_page_cached(url, ua_idx)
            if code != 200:
                last_hint = f"HTTP {code}（第{attempt}次）"
                continue
            if looks_like_verify_page(page_html):
                last_hint = f"疑似验证/拦截页（第{attempt}次）"
                continue
            text = extract_wechat_text(page_html)
            if not text:
                last_hint = f"未找到 js_content（第{attempt}次）"
                continue
            return text, "来自链接抓取"
        except requests.exceptions.Timeout:
            last_hint = f"抓取超时（第{attempt}次）"
        except requests.exceptions.RequestException as e:
            last_hint = f"网络错误：{e}（第{attempt}次）"
    return None, (last_hint or "抓取失败")

# =============================
# 5) DeepSeek 流式生成
# =============================
def length_to_max_tokens(mode: str) -> int:
    return {"短": 1200, "中": 1800, "长": 2600}.get(mode, 1800)

def length_to_hint(mode: str) -> str:
    if mode == "短":
        return "正文尽量精炼，信息密度高，控制在约900-1200字。"
    if mode == "长":
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
            {"role": "user", "content": f"原文=（{text}）"},
        ],
        "stream": True,
        "temperature": float(temperature),
        "max_tokens": int(length_to_max_tokens(length_mode)),
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    return requests.post(url, headers=headers, json=payload, stream=True, timeout=120)

# =============================
# 6) 自动跳到 tab
# =============================
def jump_to_tab_by_text(tab_text: str):
    safe_text = json.dumps(tab_text)
    components.html(f"""
<script>
(function(){{
  const target = {safe_text};
  const tabs = parent.document.querySelectorAll('button[data-baseweb="tab"]');
  for (const b of tabs) {{
    const t = (b.innerText || '').trim();
    if (t.includes(target)) {{ b.click(); break; }}
  }}
}})();
</script>
""", height=0)

# =============================
# 7) 免Key编辑器（Quill）——删表格 + 丰富表情 + 字号10-50 + 字体选项 + 去掉alert
#    ✅ 关键修复：这里不使用 f-string，避免 CSS 的 { } 触发语法错误
# =============================
def render_wechat_editor(initial_html: str, version: int):
    init_js = json.dumps(initial_html or "")
    ver_js = json.dumps(str(version))

    template = r"""
<link href="https://cdn.jsdelivr.net/npm/quill@1.3.7/dist/quill.snow.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/quill@1.3.7/dist/quill.min.js"></script>
<script src="https://unpkg.com/turndown/dist/turndown.js"></script>

<div id="toast" style="position:fixed;top:14px;right:14px;z-index:99999;display:none;
  background:rgba(17,17,17,0.92);color:#fff;padding:10px 12px;border-radius:10px;
  font-weight:800;font-size:14px;box-shadow:0 10px 30px rgba(0,0,0,0.2);">
</div>

<div id="wrap" style="border:1px solid #07c160;border-radius:12px;background:#fff;">
  <div id="topbar" style="position:sticky;top:0;z-index:50;background:#fff;border-bottom:1px solid rgba(0,0,0,0.08);
       padding:12px;border-top-left-radius:12px;border-top-right-radius:12px;">
    <div style="display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap;">
      <div style="font-weight:900;font-family:Microsoft YaHei;color:#000;font-size:18px;">
        公众号排版编辑器（所见即所得）
      </div>
      <div style="display:flex;gap:10px;flex-wrap:wrap;">
        <button id="btnApply" style="background:#07c160;color:#fff;border:none;border-radius:10px;padding:10px 14px;cursor:pointer;font-weight:900;">✨ 一键排版</button>
        <button id="btnCopyRich" style="background:#07c160;color:#fff;border:none;border-radius:10px;padding:10px 14px;cursor:pointer;font-weight:900;">📋 复制富文本</button>
        <button id="btnCopyMd" style="background:#07c160;color:#fff;border:none;border-radius:10px;padding:10px 14px;cursor:pointer;font-weight:900;">🧾 复制Markdown</button>
        <button id="btnClear" style="background:#f2f2f2;color:#000;border:1px solid rgba(0,0,0,0.12);border-radius:10px;padding:10px 14px;cursor:pointer;font-weight:900;">🧹 清空</button>
      </div>
    </div>

    <div id="toolbar" style="margin-top:10px;border:1px solid rgba(0,0,0,0.08);border-radius:10px;padding:6px 8px;">
      <span class="ql-formats">
        <button class="ql-undo" type="button">↶</button>
        <button class="ql-redo" type="button">↷</button>
      </span>

      <span class="ql-formats">
        <select class="ql-font" id="fontSelect">
          <option value="wechat" selected>公众号默认</option>
          <option value="simsun">宋体</option>
          <option value="simhei">黑体</option>
          <option value="kaiti">楷体</option>
          <option value="fangsong">仿宋</option>
          <option value="yahei">微软雅黑</option>
          <option value="pingfang">苹方</option>
          <option value="notosans">Noto Sans SC</option>
          <option value="sourcehan">思源黑体</option>
          <option value="arial">Arial</option>
          <option value="helvetica">Helvetica</option>
          <option value="times">Times New Roman</option>
          <option value="georgia">Georgia</option>
          <option value="verdana">Verdana</option>
          <option value="tahoma">Tahoma</option>
          <option value="courier">Courier New</option>
        </select>
      </span>

      <span class="ql-formats" style="display:inline-flex;align-items:center;gap:6px;">
        <select class="ql-size" id="sizeSelect"></select>
        <input id="sizeInput" type="number" min="10" max="50" step="1"
          style="width:72px;border:1px solid rgba(0,0,0,0.15);border-radius:8px;padding:6px 8px;font-weight:800;"
          title="输入 10-50 的字号（px）" />
        <span style="font-weight:800;color:#666;">px</span>
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

      <!-- HR + Emoji（已删除表格） -->
      <span class="ql-formats">
        <button id="btnHr" type="button">—</button>
        <button id="btnEmoji" type="button">😊</button>
      </span>
    </div>
  </div>

  <div id="editorHost" style="padding:12px;">
    <div id="editor" style="border:1px solid rgba(0,0,0,0.08);border-radius:12px;"></div>
    <div style="margin-top:10px;color:#666;font-size:12px;line-height:1.6;">
      提示：复制富文本可直接贴公众号后台；复制Markdown用于二次处理（不保证公众号完全等效渲染）。
    </div>
  </div>
</div>

<div id="emojiModal" style="display:none;position:fixed;inset:0;z-index:99998;background:rgba(0,0,0,0.35);">
  <div style="width:min(820px,92vw);max-height:min(620px,82vh);overflow:hidden;background:#fff;border-radius:14px;
              position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);
              box-shadow:0 20px 60px rgba(0,0,0,0.25);border:1px solid rgba(0,0,0,0.08);">
    <div style="display:flex;justify-content:space-between;align-items:center;padding:12px 14px;border-bottom:1px solid rgba(0,0,0,0.08);">
      <div style="font-weight:900;font-size:16px;">选择表情</div>
      <button id="emojiClose" style="border:none;background:#f2f2f2;border-radius:10px;padding:8px 10px;font-weight:900;cursor:pointer;">✖</button>
    </div>

    <div style="display:flex;gap:10px;align-items:center;padding:10px 14px;border-bottom:1px solid rgba(0,0,0,0.06);flex-wrap:wrap;">
      <input id="emojiSearch" placeholder="搜索（输入表情/编号）" style="flex:1;min-width:220px;border:1px solid rgba(0,0,0,0.12);border-radius:10px;padding:10px 12px;font-weight:800;">
      <div style="display:flex;gap:8px;flex-wrap:wrap;">
        <button class="emojiTab" data-tab="common">常用</button>
        <button class="emojiTab" data-tab="face">表情</button>
        <button class="emojiTab" data-tab="hand">手势</button>
        <button class="emojiTab" data-tab="life">生活</button>
        <button class="emojiTab" data-tab="sign">符号</button>
      </div>
    </div>

    <div id="emojiGrid" style="padding:12px 14px;overflow:auto;max-height:min(520px,68vh);display:grid;
                              grid-template-columns:repeat(12,1fr);gap:8px;"></div>
  </div>
</div>

<style>
.ql-font-wechat { font-family: -apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei","Helvetica Neue",Arial,sans-serif; }
.ql-font-simsun { font-family: SimSun,"宋体",serif; }
.ql-font-simhei { font-family: SimHei,"黑体",sans-serif; }
.ql-font-kaiti { font-family: KaiTi,"楷体",serif; }
.ql-font-fangsong { font-family: FangSong,"仿宋",serif; }
.ql-font-yahei { font-family: "Microsoft YaHei","微软雅黑",sans-serif; }
.ql-font-pingfang { font-family: "PingFang SC","苹方",-apple-system,BlinkMacSystemFont,sans-serif; }
.ql-font-notosans { font-family: "Noto Sans SC","Noto Sans CJK SC",sans-serif; }
.ql-font-sourcehan { font-family: "Source Han Sans SC","Source Han Sans","思源黑体",sans-serif; }
.ql-font-arial { font-family: Arial,sans-serif; }
.ql-font-helvetica { font-family: Helvetica,Arial,sans-serif; }
.ql-font-times { font-family: "Times New Roman",Times,serif; }
.ql-font-georgia { font-family: Georgia,serif; }
.ql-font-verdana { font-family: Verdana,sans-serif; }
.ql-font-tahoma { font-family: Tahoma,sans-serif; }
.ql-font-courier { font-family: "Courier New",Courier,monospace; }

.ql-container { border:none !important; }
.ql-editor {
  font-family: SimSun,宋体,serif;
  font-size: 17px;
  line-height: 2;
  color: #000;
  min-height: 520px;
}
@media (max-width: 768px) { .ql-editor { min-height: 420px; } }

.emojiTab{
  border:1px solid rgba(0,0,0,0.12);
  background:#fff;
  border-radius:10px;
  padding:8px 10px;
  font-weight:900;
  cursor:pointer;
}
.emojiTab.active{
  background:#07c160;
  color:#fff;
  border-color:#07c160;
}
.emojiCell{
  border:1px solid rgba(0,0,0,0.10);
  border-radius:10px;
  padding:10px 0;
  text-align:center;
  cursor:pointer;
  font-size:20px;
  user-select:none;
}
.emojiCell:hover{
  border-color:#07c160;
  box-shadow:0 6px 18px rgba(7,193,96,0.15);
}
</style>

<script>
const INITIAL_HTML = __INIT_HTML__;
const VERSION = __VER__;

function showToast(msg, ms=1600) {
  const el = document.getElementById('toast');
  el.innerText = msg;
  el.style.display = 'block';
  clearTimeout(el.__t);
  el.__t = setTimeout(()=>{ el.style.display='none'; }, ms);
}

const Font = Quill.import('formats/font');
Font.whitelist = [
  'wechat','simsun','simhei','kaiti','fangsong','yahei','pingfang','notosans','sourcehan',
  'arial','helvetica','times','georgia','verdana','tahoma','courier'
];
Quill.register(Font, true);

const Size = Quill.import('attributors/style/size');
const SIZE_LIST = Array.from({length: 41}, (_,i)=> (10+i) + 'px'); // 10px~50px
Size.whitelist = SIZE_LIST;
Quill.register(Size, true);

const quill = new Quill('#editor', {
  theme: 'snow',
  modules: {
    toolbar: '#toolbar',
    history: { delay: 300, maxStack: 100, userOnly: true }
  }
});

const KEY_HTML = 'wechat_editor_html';
const KEY_VER  = 'wechat_editor_ver';

function setEditorHtml(h) { quill.clipboard.dangerouslyPasteHTML(h || ""); }
function getEditorRoot() { return document.querySelector('#editor .ql-editor'); }
function saveLocal() {
  const root = getEditorRoot();
  if (!root) return;
  localStorage.setItem(KEY_HTML, root.innerHTML || "");
  localStorage.setItem(KEY_VER, VERSION);
}

(function initContent(){
  const savedVer = localStorage.getItem(KEY_VER);
  const savedHtml = localStorage.getItem(KEY_HTML);

  if (savedHtml && savedVer === VERSION) {
    setEditorHtml(savedHtml);
  } else {
    setEditorHtml(INITIAL_HTML);
    localStorage.setItem(KEY_VER, VERSION);
    localStorage.setItem(KEY_HTML, INITIAL_HTML || "");
  }
})();

let saveTimer = null;
quill.on('text-change', function(){
  if (saveTimer) clearTimeout(saveTimer);
  saveTimer = setTimeout(saveLocal, 350);
});

document.querySelector('.ql-undo').addEventListener('click', () => quill.history.undo());
document.querySelector('.ql-redo').addEventListener('click', () => quill.history.redo());

document.getElementById('btnHr').addEventListener('click', () => {
  const range = quill.getSelection(true) || { index: quill.getLength() };
  quill.clipboard.dangerouslyPasteHTML(range.index, '<p><hr/></p><p></p>');
});

const sizeSelect = document.getElementById('sizeSelect');
const sizeInput  = document.getElementById('sizeInput');

function fillSizeSelect() {
  sizeSelect.innerHTML = '';
  const common = [12,14,16,17,18,20,22,24,26,28,30,36,40,48];
  const commonSet = new Set(common.map(n=>n+'px'));

  common.forEach(n => {
    const opt = document.createElement('option');
    opt.value = n + 'px';
    opt.innerText = n + 'px';
    if (n === 17) opt.selected = true;
    sizeSelect.appendChild(opt);
  });

  for (let n=10; n<=50; n++) {
    const v = n + 'px';
    if (commonSet.has(v)) continue;
    const opt = document.createElement('option');
    opt.value = v;
    opt.innerText = v;
    sizeSelect.appendChild(opt);
  }
}
fillSizeSelect();
sizeInput.value = 17;

function applySize(px) {
  if (!px) return;
  const n = parseInt(px.replace('px',''), 10);
  if (isNaN(n)) return;
  const clamped = Math.min(50, Math.max(10, n));
  const val = clamped + 'px';
  quill.format('size', val);

  sizeInput.value = clamped;
  let found = false;
  for (const o of sizeSelect.options) {
    if (o.value === val) { sizeSelect.value = val; found = true; break; }
  }
  if (!found) {
    let best = '17px';
    let bestDiff = 999;
    for (const o of sizeSelect.options) {
      const m = parseInt(o.value,10);
      const d = Math.abs(m - clamped);
      if (d < bestDiff) { bestDiff = d; best = o.value; }
    }
    sizeSelect.value = best;
  }
}

sizeSelect.addEventListener('change', () => applySize(sizeSelect.value));
sizeInput.addEventListener('change', () => {
  const v = parseInt(sizeInput.value || '17', 10);
  applySize(v + 'px');
});
applySize('17px');

function applyWechatLayout() {
  const root = getEditorRoot();
  if (!root) return;

  root.style.fontFamily = 'SimSun,宋体,serif';
  root.style.fontSize = '17px';
  root.style.lineHeight = '2';
  root.style.color = '#000';

  root.querySelectorAll('p').forEach(p => {
    p.style.margin = '0 0 14px 0';
    p.style.fontFamily = 'SimSun,宋体,serif';
    p.style.fontSize = '17px';
    p.style.lineHeight = '2';
    p.style.color = '#000';
  });

  root.querySelectorAll('p').forEach(p => {
    const t = (p.innerText || '').trim();
    if (/^0[1-4]\.\s+/.test(t) || t === "【推荐爆款标题】") {
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
    }
  });

  saveLocal();
  showToast('已应用公众号排版');
}
document.getElementById('btnApply').addEventListener('click', applyWechatLayout);

async function copyRichAll() {
  const root = getEditorRoot();
  if (!root) return;

  const clone = root.cloneNode(true);
  clone.querySelectorAll('p').forEach(p => {
    p.style.margin = p.style.margin || '0 0 14px 0';
    p.style.fontFamily = p.style.fontFamily || 'SimSun,宋体,serif';
    p.style.fontSize = p.style.fontSize || '17px';
    p.style.lineHeight = p.style.lineHeight || '2';
    p.style.color = p.style.color || '#000';
  });
  clone.querySelectorAll('h2').forEach(h2 => {
    h2.style.fontFamily = h2.style.fontFamily || 'SimHei,黑体,sans-serif';
    h2.style.fontSize = h2.style.fontSize || '18px';
    h2.style.fontWeight = h2.style.fontWeight || '800';
    h2.style.margin = h2.style.margin || '18px 0 8px 0';
    h2.style.borderLeft = h2.style.borderLeft || '5px solid #07c160';
    h2.style.paddingLeft = h2.style.paddingLeft || '10px';
    h2.style.color = h2.style.color || '#000';
  });

  const htmlText = `<div style="font-family:SimSun,宋体,serif;font-size:17px;line-height:2;color:#000;">${clone.innerHTML}</div>`;
  const plainText = root.innerText || '';

  try {
    if (navigator.clipboard && window.ClipboardItem) {
      const htmlBlob = new Blob([htmlText], { type: "text/html" });
      const textBlob = new Blob([plainText], { type: "text/plain" });
      const item = new ClipboardItem({ "text/html": htmlBlob, "text/plain": textBlob });
      await navigator.clipboard.write([item]);
      showToast("已复制富文本（保留样式）");
      return;
    }
  } catch(e) {}

  try {
    const temp = document.createElement('div');
    temp.setAttribute('contenteditable','true');
    temp.style.position='fixed';
    temp.style.left='-9999px';
    temp.innerHTML = htmlText;
    document.body.appendChild(temp);

    const range = document.createRange();
    range.selectNodeContents(temp);
    const sel = window.getSelection();
    sel.removeAllRanges(); sel.addRange(range);

    document.execCommand('copy');
    sel.removeAllRanges();
    document.body.removeChild(temp);
    showToast("已复制富文本（保留样式）");
  } catch(e) {
    showToast("复制失败：建议用 Chrome/Edge + HTTPS");
  }
}
document.getElementById('btnCopyRich').addEventListener('click', copyRichAll);

async function copyMarkdownAll() {
  const root = getEditorRoot();
  if (!root) return;

  const htmlInner = root.innerHTML || '';
  let md = '';
  try {
    const service = new TurndownService({
      headingStyle:'atx',
      codeBlockStyle:'fenced',
      emDelimiter:'*'
    });
    md = service.turndown(htmlInner);
  } catch(e) {
    md = root.innerText || '';
  }

  try {
    await navigator.clipboard.writeText(md);
    showToast("已复制 Markdown");
  } catch(e) {
    const el = document.createElement("textarea");
    el.value = md;
    document.body.appendChild(el);
    el.select();
    document.execCommand('copy');
    document.body.removeChild(el);
    showToast("已复制 Markdown");
  }
}
document.getElementById('btnCopyMd').addEventListener('click', copyMarkdownAll);

document.getElementById('btnClear').addEventListener('click', () => {
  if (!confirm("确定清空编辑器内容？")) return;
  quill.setText('');
  localStorage.setItem(KEY_HTML, '');
  localStorage.setItem(KEY_VER, VERSION);
  showToast("已清空");
});

const emojiModal = document.getElementById('emojiModal');
const emojiGrid = document.getElementById('emojiGrid');
const emojiSearch = document.getElementById('emojiSearch');
const emojiClose = document.getElementById('emojiClose');
const emojiTabs = Array.from(document.querySelectorAll('.emojiTab'));

const EMOJIS = {
  common: ["😀","😁","😂","🤣","🥹","😊","😇","🙂","😉","😍","😘","😎","🤩","🥳","🤔","🫡","😴","😮","😤","😭","👍","👎","👏","🙏","🔥","✅","⭐","📌","🧠","💡","📈","📉","🧾","📋","✍️","🧩","🚀","⏳","⚡","🎯","🎁","💰","📣","📰","📷","🎬","🎧","🍀"],
  face: ["😄","😃","😀","😁","😆","😅","😂","🤣","🥲","🥹","😊","😇","🙂","🙃","😉","😌","😍","🥰","😘","😗","😙","😚","😋","😛","😝","😜","🤪","🤨","🧐","🤓","😎","🥸","🤩","🥳","😏","😒","😞","😔","😟","😕","🙁","☹️","😣","😖","😫","😩","🥺","😢","😭","😤","😠","😡","🤬","😳","🥵","🥶","😱","😨","😰","😥","😓","🫣","🤗","🫠","🤭","🫢","🫡","🤫","🤥","😶","😶‍🌫️","😐","😑","😬","🙄","😯","😦","😧","😮","😲","🥱","😴","🤤","😪","😵","😵‍💫","🤐","🥴","🤢","🤮","🤧","😷","🤒","🤕"],
  hand: ["👍","👎","👌","🤌","🤏","✌️","🤞","🤟","🤘","🤙","👊","✊","🤛","🤜","👏","🙌","🫶","👐","🤲","🙏","✍️","💪","🦾","🖐️","✋","🖖","👋","🤚","🫱","🫲","🫳","🫴","👉","👈","👆","👇","☝️","👀","🫵","🤝"],
  life: ["🍎","🍊","🍋","🍌","🍉","🍇","🍓","🫐","🍒","🍑","🥭","🍍","🥑","🍅","🥦","🥕","🌽","🍞","🥐","🥯","🍚","🍜","🍣","🍔","🍟","🍕","🌮","🥗","🍰","🍪","🍫","🍿","☕","🍵","🥤","🧋","🍺","🍷","🎉","🎊","🎈","🎁","🎀","🎯","🏆","🥇","📣","📢","🔔","🧠","💡","📌","📎","🧷","📝","📓","📘","📕","🗂️","📊","📈","🧾","💻","📱","⌨️","🖥️","🖨️","📷","🎥","🎬","🎧","🎵","🚗","✈️","🚀","🛰️","🏝️","⛰️","🌧️","☀️","🌙","⭐","⚡","🔥","🧯","✅","❌","🟢","🟡","🔴"],
  sign: ["✅","☑️","✔️","✖️","❌","⚠️","❗","‼️","❓","❔","💯","🔺","🔻","⬆️","⬇️","➡️","⬅️","↗️","↘️","↙️","↖️","🔁","🔄","⏸️","▶️","⏩","⏪","⏫","⏬","➕","➖","✳️","✴️","⭐","🌟","✨","💥","🔥","⚡","🟢","🟡","🔴","🟣","🟤","⚪","⚫","🟥","🟧","🟨","🟩","🟦","🟪"]
};

let currentTab = 'common';

function renderEmojis(tab, keyword='') {
  const list = EMOJIS[tab] || [];
  const kw = (keyword || '').trim();

  let filtered = list;
  if (kw) {
    const idx = parseInt(kw, 10);
    if (!isNaN(idx) && idx >= 1 && idx <= list.length) {
      filtered = [list[idx-1]];
    } else {
      filtered = list.filter(e => e.includes(kw));
    }
  }

  emojiGrid.innerHTML = '';
  filtered.forEach((e, i) => {
    const d = document.createElement('div');
    d.className = 'emojiCell';
    d.title = `${i+1}`;
    d.innerText = e;
    d.addEventListener('click', () => {
      const range = quill.getSelection(true) || { index: quill.getLength() };
      quill.insertText(range.index, e);
      closeEmoji();
      saveLocal();
      showToast('已插入表情');
    });
    emojiGrid.appendChild(d);
  });
}

function openEmoji() {
  emojiModal.style.display = 'block';
  emojiSearch.value = '';
  setTab(currentTab);
  setTimeout(() => emojiSearch.focus(), 50);
}
function closeEmoji() { emojiModal.style.display = 'none'; }

function setTab(tab) {
  currentTab = tab;
  emojiTabs.forEach(b => b.classList.toggle('active', b.dataset.tab === tab));
  renderEmojis(tab, emojiSearch.value);
}

document.getElementById('btnEmoji').addEventListener('click', openEmoji);
emojiClose.addEventListener('click', closeEmoji);
emojiModal.addEventListener('click', (e) => { if (e.target === emojiModal) closeEmoji(); });
emojiTabs.forEach(btn => { btn.addEventListener('click', () => setTab(btn.dataset.tab)); });
emojiSearch.addEventListener('input', () => renderEmojis(currentTab, emojiSearch.value));
setTab('common');
</script>
"""
    html_str = template.replace("__INIT_HTML__", init_js).replace("__VER__", ver_js)
    components.html(html_str, height=860)

# =============================
# 8) UI Tabs
# =============================
tab_gen, tab_manual = st.tabs(["🚀 二创生成", "📝 手动排版"])

with tab_gen:
    target_url = st.text_input("🔗 粘贴链接开始深度重构")

    with st.expander("高级设置（可选）", expanded=False):
        st.markdown("**风格强度（temperature）**")
        st.caption("越低越稳；越高越创意（更敢改但更易跑题）")
        temperature = st.slider("风格强度（建议 0.70–0.85）", 0.5, 1.0, 0.8, 0.05)

        st.markdown("---")
        length_mode = st.selectbox("篇幅", ["中", "短", "长"], index=0)
        st.caption("短：更精炼；中：默认；长：更充分展开（更耗 tokens）")

    with st.expander("抓取失败？这里可手动粘贴原文继续生成（可选）", expanded=False):
        st.session_state.manual_text = st.text_area(
            "📄 粘贴原文（抓不到链接时会用这里的内容）",
            value=st.session_state.manual_text,
            height=180,
            placeholder="公众号链接经常验证/拦截。抓取失败时，把文章原文复制到这里再点“开始生成”。"
        )

    if st.session_state.last_error and not st.session_state.is_generating:
        st.error(st.session_state.last_error)

    btn_text = "正在生成中..." if st.session_state.is_generating else "开始生成"
    clicked = st.button(btn_text, disabled=st.session_state.is_generating, key="gen_btn")

    if clicked and not st.session_state.is_generating:
        st.session_state.is_generating = True
        st.session_state.last_error = None
        st.rerun()

    if st.session_state.is_generating:
        st.info("正在生成中，请稍候…")
        live_placeholder = st.empty()

        try:
            api_key = st.secrets.get("DEEPSEEK_API_KEY")
            if not api_key:
                st.session_state.last_error = "未检测到 DEEPSEEK_API_KEY，请在 .streamlit/secrets.toml 配置。"
                st.session_state.is_generating = False
                st.rerun()

            source_text = None
            if target_url.strip():
                with st.spinner("正在抓取文章内容…"):
                    text, hint = get_article_text_smart(target_url.strip())
                if text:
                    source_text = text
                else:
                    manual = (st.session_state.manual_text or "").strip()
                    if manual:
                        source_text = manual
                    else:
                        st.session_state.last_error = f"内容抓取失败：{hint}。你可以展开“手动粘贴原文”后再生成。"
                        st.session_state.is_generating = False
                        st.rerun()
            else:
                manual = (st.session_state.manual_text or "").strip()
                if manual:
                    source_text = manual
                else:
                    st.session_state.last_error = "请粘贴链接，或展开“手动粘贴原文”输入内容后再生成。"
                    st.session_state.is_generating = False
                    st.rerun()

            st.session_state.last_source_text = source_text

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
                    if (len(full_content) - last_render_len >= 120) or (now - last_tick >= 0.35):
                        last_render_len = len(full_content)
                        last_tick = now
                        live_placeholder.markdown(safety_filter(full_content) + "▌")
                except:
                    continue

            live_placeholder.empty()

            md_final = safety_filter(full_content)
            plain_final = to_plain_text(md_final)
            rich_html_out = build_rich_html(plain_final)

            st.session_state.result_md = md_final
            st.session_state.result_plain = plain_final
            st.session_state.result_rich_html = rich_html_out

            st.session_state.editor_initial_html = rich_html_out
            st.session_state.editor_version += 1
            st.session_state.jump_to_editor = True

            st.session_state.is_generating = False
            st.session_state.last_error = None
            st.rerun()

        except Exception as e:
            st.session_state.last_error = f"发生错误：{e}"
            st.session_state.is_generating = False
            st.rerun()

    if (not st.session_state.is_generating) and st.session_state.editor_initial_html:
        st.success("✅ 已生成完成，并已自动导入到「手动排版」编辑器。")

with tab_manual:
    st.subheader("🧩 手动排版（工具栏 + 一键排版 + 一键复制）")
    render_wechat_editor(st.session_state.editor_initial_html, st.session_state.editor_version)

if st.session_state.jump_to_editor:
    st.session_state.jump_to_editor = False
    jump_to_tab_by_text("手动排版")
