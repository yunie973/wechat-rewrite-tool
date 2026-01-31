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
# 1) Theme + Tabs 文案常显（全局样式 + JS）
# =============================
st.markdown("""
<style>
:root, body, .stApp { color-scheme: light !important; }
.stApp { background:#fff !important; color:#000 !important; }

/* 标题 */
h1 { color:#07c160 !important; font-family:"Microsoft YaHei"; text-align:center; font-weight:900; }

/* TextInput */
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

/* Select / Slider */
div[data-baseweb="select"] > div{
  background:#fff !important;
  color:#000 !important;
  border-radius:12px !important;
  border:1px solid rgba(7,193,96,0.45) !important;
}
div[data-baseweb="slider"] * { color:#000 !important; }

/* 按钮 */
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

/* Expander（高级设置） */
div[data-testid="stExpander"] details{
  border: 1px solid rgba(7,193,96,0.35) !important;
  border-radius: 12px !important;
  background: #fff !important;
  overflow: visible !important;
}
div[data-testid="stExpander"] summary{
  background: #f6fbf8 !important;
  color: #000 !important;
  padding: 12px 14px !important;
  border-radius: 12px !important;
  font-weight: 900 !important;
}
div[data-testid="stExpander"] summary:hover{
  background: rgba(7,193,96,0.10) !important;
}
div[data-testid="stExpander"] details > div{
  background:#fff !important;
  padding: 14px !important;
}

/* NumberInput：白底 + 绿按钮 */
div[data-testid="stNumberInput"] div[data-baseweb="input"]{
  border: 2px solid #07c160 !important;
  border-radius: 12px !important;
  overflow: hidden !important;
  background:#fff !important;
}
div[data-testid="stNumberInput"] input[type="number"]{
  background:#fff !important;
  color:#000 !important;
  -webkit-text-fill-color:#000 !important;
  font-weight: 900 !important;
  opacity: 1 !important;
}
div[data-testid="stNumberInput"] button{
  background:#07c160 !important;
  color:#fff !important;
  border:none !important;
  font-weight:900 !important;
}
div[data-testid="stNumberInput"] button:hover{
  background:#06b457 !important;
}
div[data-testid="stNumberInput"] button + button{
  border-left: 1px solid rgba(255,255,255,0.25) !important;
}

/* 提升网页端清晰度 */
html, body, .stApp, * {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
}

/* ✅ Footer 固定 + 自动留白（JS 写入 --footerH） */
:root{ --footerH: 0px; }

/* 固定 footer */
.footer{
  position:fixed; left:0; bottom:0; width:100%;
  background:#fff; padding:12px 0; border-top:2px solid #07c160;
  z-index:999; display:flex; justify-content:center; align-items:center; gap:20px;
}

/* ✅ 核心：内容区底部留白 = footer真实高度 + 额外空隙 */
div[data-testid="stAppViewContainer"] .main .block-container{
  padding-bottom: calc(var(--footerH) + 36px + env(safe-area-inset-bottom)) !important;
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
  .qr-box{ width:150px !important; }
}
</style>

<!-- ✅ 滚轮落在数字框上时，不抢页面滚动 -->
<script>
(function () {
  function bindWheelBlur() {
    const inputs = document.querySelectorAll('input[type="number"]');
    inputs.forEach((inp) => {
      if (inp.__wheelBound) return;
      inp.__wheelBound = true;
      inp.addEventListener('wheel', () => { inp.blur(); }, { passive: true });
    });
  }
  bindWheelBlur();
  setInterval(bindWheelBlur, 900);
})();
</script>

<div class="footer">
  <span style="color:#000;">© 2026 <b>@兴洪</b> 版权所有</span>
  <div class="qr-item">📗 微信加我
    <div class="qr-box"><img src="https://raw.githubusercontent.com/yunie973/wechat-rewrite-tool/main/wechat_qr.png.jpg" style="width:100%;"></div>
  </div>
  <div class="qr-item">🪐 知识星球
    <div class="qr-box"><img src="https://raw.githubusercontent.com/yunie973/wechat-rewrite-tool/main/star_qr.png.jpg" style="width:100%;"></div>
  </div>
</div>

<!-- ✅ 自动测量 footer 高度，写入 --footerH -->
<script>
(function () {
  function setFooterSpace(){
    const footer = document.querySelector('.footer');
    if(!footer) return;
    const h = Math.ceil(footer.getBoundingClientRect().height || 0);
    document.documentElement.style.setProperty('--footerH', h + 'px');
  }
  setFooterSpace();
  setTimeout(setFooterSpace, 200);
  setTimeout(setFooterSpace, 800);
  window.addEventListener('resize', setFooterSpace);
  setInterval(setFooterSpace, 1200);
})();
</script>
""", unsafe_allow_html=True)


<!-- ✅ 解决：滚轮落在数字输入框上时页面不下滑（滚轮被用来改数字） -->
<script>
(function () {
  function bind() {
    const inputs = document.querySelectorAll('input[type="number"]');
    inputs.forEach((inp) => {
      if (inp.__wheelBound) return;
      inp.__wheelBound = true;
      inp.addEventListener('wheel', () => { inp.blur(); }, { passive: true });
    });
  }
  bind();
  setInterval(bind, 800);
})();
</script>

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

# 生成结果
ss_init("result_md", "")
ss_init("result_plain", "")
ss_init("result_rich_html", "")

# 编辑器输入（新生成会覆盖它）
ss_init("editor_initial_html", "")
ss_init("editor_version", 0)         # 每次新生成+1，用于通知前端覆盖 localStorage
ss_init("jump_to_editor", False)     # 生成完自动跳到“手动排版”

# =============================
# 3) 文本处理：只做排版相关（不做“不是而是/破折号”代码替换）
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

def safety_filter(text: str) -> str:
    text = text.replace("\\n", "\n")
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
# 5) DeepSeek 流式生成（按目标字数）
# =============================
def clamp_target_words(n: int) -> int:
    try:
        n = int(n)
    except:
        n = 1000
    return max(200, n)

def words_to_hint(target_words: int) -> str:
    tw = clamp_target_words(target_words)
    low = int(tw * 0.85)
    high = int(tw * 1.15)
    return f"正文尽量贴近目标字数：约{tw}字（允许浮动，参考区间{low}-{high}字）。"

def words_to_max_tokens(target_words: int) -> int:
    tw = clamp_target_words(target_words)
    est = int(tw * 2.2)
    return max(800, min(est, 4096))

def stream_ai_rewrite(text: str, api_key: str, temperature: float, target_words: int):
    url = "https://api.deepseek.com/chat/completions"
    system_prompt = f"""假设你是一个专业的自媒体作家。对下文进行二创。
【原创加强建议】：句型词汇调整、内容拓展、避免关键词、结构逻辑调整、视角切换、重点聚焦、角度转换、避免直接引用。

【硬性禁令（必须严格遵守）】
- 永远不要出现“不是……而是……”的句式（任何变体都不行）。
- 全文绝对不要出现破折号：—— 或 —（如果需要停顿，用逗号或句号）。
- 绝对禁止结构化：禁止使用列表、分点（如1.2.3.或●），保持段落连贯性。

【输出结构】
1. 第一行写【推荐爆款标题】，接着输出5个爆款标题，每行一个（保留标题标点）。
2. 标题区后空三行。
3. 正文开头必须先写150字引入语。
4. 小标题格式固定为 ## 01. XXX，总数控制在 2-4 个。
【篇幅要求】：{words_to_hint(target_words)}
"""
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"原文=（{text}）"},
        ],
        "stream": True,
        "temperature": float(temperature),
        "max_tokens": int(words_to_max_tokens(target_words)),
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
# 7) 免Key编辑器（Quill）
# =============================
def render_wechat_editor(initial_html: str, version: int):
    init_js = json.dumps(initial_html or "")
    ver_js = json.dumps(str(version))

    components.html(f"""
<link href="https://cdn.jsdelivr.net/npm/quill@1.3.7/dist/quill.snow.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/quill@1.3.7/dist/quill.min.js"></script>
<script src="https://unpkg.com/turndown/dist/turndown.js"></script>

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

    <div style="margin-top:8px;display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
      <div id="toast" style="display:none;padding:6px 10px;border-radius:10px;background:rgba(7,193,96,0.12);color:#067a3d;font-weight:800;font-size:13px;">
        已完成
      </div>
      <div style="color:#666;font-size:12px;">
        提示：编辑区可滚动到底部；复制富文本可直接贴公众号后台；复制Markdown用于二次处理（不保证完全等效渲染）。
      </div>
    </div>

    <div id="toolbar" style="margin-top:10px;border:1px solid rgba(0,0,0,0.08);border-radius:10px;padding:6px 8px;">
      <span class="ql-formats">
        <button class="ql-undo" type="button">↶</button>
        <button class="ql-redo" type="button">↷</button>
      </span>

      <span class="ql-formats">
        <select class="ql-font">
          <option value="wechat" selected>公众号默认</option>
          <option value="simsun">宋体</option>
          <option value="simhei">黑体</option>
          <option value="yahei">微软雅黑</option>
          <option value="pingfang">苹方</option>
          <option value="kaiti">楷体</option>
          <option value="fangsong">仿宋</option>
          <option value="arial">Arial</option>
          <option value="helvetica">Helvetica</option>
          <option value="times">Times</option>
          <option value="georgia">Georgia</option>
          <option value="courier">Courier</option>
          <option value="monospace">Monospace</option>
        </select>
      </span>

      <span class="ql-formats" style="display:inline-flex;align-items:center;gap:6px;">
        <span style="font-weight:800;color:#000;font-size:12px;">字号</span>
        <input id="fontSizeInput" type="number" min="10" max="50" value="17"
          style="width:72px;padding:6px 8px;border:1px solid rgba(0,0,0,0.15);border-radius:8px;outline:none;font-weight:800;">
        <span style="font-weight:800;color:#000;font-size:12px;">px</span>
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
        <button id="btnEmoji" type="button">😊</button>
      </span>
    </div>
  </div>

  <div id="editorHost" style="padding:12px;">
    <div id="editor" style="border:1px solid rgba(0,0,0,0.08);border-radius:12px;"></div>

    <div id="emojiPanel" style="display:none;margin-top:10px;border:1px solid rgba(0,0,0,0.10);border-radius:12px;padding:10px;background:#fff;">
      <div style="display:flex;justify-content:space-between;align-items:center;gap:10px;">
        <div style="font-weight:900;color:#000;">表情库（120+）</div>
        <button id="emojiClose" style="background:#f2f2f2;color:#000;border:1px solid rgba(0,0,0,0.12);border-radius:10px;padding:6px 10px;cursor:pointer;font-weight:900;">关闭</button>
      </div>
      <div id="emojiGrid" style="margin-top:10px;display:grid;grid-template-columns:repeat(12, 1fr);gap:6px;max-height:180px;overflow:auto;padding-right:4px;"></div>
      <div style="margin-top:8px;color:#666;font-size:12px;">点一下就会插入到光标处。</div>
    </div>
  </div>
</div>

<style>
.ql-font-wechat {{ font-family: -apple-system,BlinkMacSystemFont,"PingFang SC","Helvetica Neue",Arial,"Microsoft YaHei",sans-serif; }}
.ql-font-simsun {{ font-family: SimSun,宋体,serif; }}
.ql-font-simhei {{ font-family: SimHei,黑体,sans-serif; }}
.ql-font-yahei {{ font-family: "Microsoft YaHei","微软雅黑",sans-serif; }}
.ql-font-pingfang {{ font-family: "PingFang SC","苹方",-apple-system,BlinkMacSystemFont,sans-serif; }}
.ql-font-kaiti {{ font-family: KaiTi,楷体,serif; }}
.ql-font-fangsong {{ font-family: FangSong,仿宋,serif; }}
.ql-font-arial {{ font-family: Arial,sans-serif; }}
.ql-font-helvetica {{ font-family: Helvetica,Arial,sans-serif; }}
.ql-font-times {{ font-family: "Times New Roman",Times,serif; }}
.ql-font-georgia {{ font-family: Georgia,serif; }}
.ql-font-courier {{ font-family: "Courier New",Courier,monospace; }}
.ql-font-monospace {{ font-family: ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,"Liberation Mono","Courier New",monospace; }}

:root {{
  --editorH: 600px;
}}
#editor .ql-container {{
  height: var(--editorH) !important;
  border: none !important;
}}
#editor .ql-editor {{
  height: 100% !important;
  overflow-y: auto !important;
  font-size: 17px;
  line-height: 2;
  color: #000;
  padding: 14px 14px !important;
}}
</style>

<script>
const INITIAL_HTML = {init_js};
const VERSION = {ver_js};

function toast(msg) {{
  const el = document.getElementById('toast');
  if (!el) return;
  el.textContent = msg || '完成';
  el.style.display = 'inline-block';
  clearTimeout(window.__toastTimer);
  window.__toastTimer = setTimeout(() => {{
    el.style.display = 'none';
  }}, 1600);
}}

function computeEditorH() {{
  const w = window.innerWidth || 1024;
  const h = window.innerHeight || 900;
  if (w <= 768) {{
    let val = Math.round(h * 0.52);
    val = Math.max(360, Math.min(420, val));
    document.documentElement.style.setProperty('--editorH', val + 'px');
  }} else {{
    let val = Math.round(h * 0.62);
    val = Math.max(520, Math.min(640, val));
    document.documentElement.style.setProperty('--editorH', val + 'px');
  }}
}}
computeEditorH();
window.addEventListener('resize', computeEditorH);

const Font = Quill.import('formats/font');
Font.whitelist = ['wechat','simsun','simhei','yahei','pingfang','kaiti','fangsong','arial','helvetica','times','georgia','courier','monospace'];
Quill.register(Font, true);

const SizeStyle = Quill.import('attributors/style/size');
SizeStyle.whitelist = null;
Quill.register(SizeStyle, true);

const quill = new Quill('#editor', {{
  theme: 'snow',
  modules: {{
    toolbar: '#toolbar',
    history: {{ delay: 300, maxStack: 100, userOnly: true }}
  }}
}});

const KEY_HTML = 'wechat_editor_html';
const KEY_VER  = 'wechat_editor_ver';

function setEditorHtml(h) {{
  quill.clipboard.dangerouslyPasteHTML(h || "");
}}

function getEditorRoot() {{
  return document.querySelector('#editor .ql-editor');
}}

function saveLocal() {{
  const root = getEditorRoot();
  if (!root) return;
  localStorage.setItem(KEY_HTML, root.innerHTML || "");
  localStorage.setItem(KEY_VER, VERSION);
}}

(function initContent(){{
  const savedVer = localStorage.getItem(KEY_VER);
  const savedHtml = localStorage.getItem(KEY_HTML);

  if (savedHtml && savedVer === VERSION) {{
    setEditorHtml(savedHtml);
  }} else {{
    setEditorHtml(INITIAL_HTML);
    localStorage.setItem(KEY_VER, VERSION);
    localStorage.setItem(KEY_HTML, INITIAL_HTML || "");
  }}
}})();

let saveTimer = null;
quill.on('text-change', function(){{
  if (saveTimer) clearTimeout(saveTimer);
  saveTimer = setTimeout(saveLocal, 400);
}});

document.querySelector('.ql-undo').addEventListener('click', () => quill.history.undo());
document.querySelector('.ql-redo').addEventListener('click', () => quill.history.redo());

document.getElementById('btnHr').addEventListener('click', () => {{
  const range = quill.getSelection(true) || {{ index: quill.getLength() }};
  quill.clipboard.dangerouslyPasteHTML(range.index, '<p><hr/></p>');
  toast('已插入分割线');
}});

const fontSizeInput = document.getElementById('fontSizeInput');
function clampSize(n) {{
  n = parseInt(n || '17', 10);
  if (isNaN(n)) n = 17;
  if (n < 10) n = 10;
  if (n > 50) n = 50;
  return n;
}}
function applySizeFromInput() {{
  const n = clampSize(fontSizeInput.value);
  fontSizeInput.value = String(n);
  const range = quill.getSelection(true) || {{ index: quill.getLength(), length: 0 }};
  quill.setSelection(range.index, range.length, 'silent');
  quill.format('size', n + 'px');
  saveLocal();
}}
fontSizeInput.addEventListener('change', applySizeFromInput);
fontSizeInput.addEventListener('blur', applySizeFromInput);

const EMOJIS = [
  '😀','😁','😂','🤣','😃','😄','😅','😆','😉','😊','😋','😎','😍','😘','🥰','😗','😙','😚','🙂','🤗',
  '🤩','🤔','🫡','🤨','😐','😑','😶','🫥','😶‍🌫️','🙄','😏','😣','😥','😮','🤐','😯','😪','😫','🥱','😴',
  '😌','😛','😜','😝','🤤','😒','😓','😔','😕','🫤','🙃','🫠','🤑','😲','☹️','🙁','😖','😞','😟','😤',
  '😢','😭','😦','😧','😨','😩','😬','😰','😱','🥵','🥶','😳','🤯','😡','😠','🤬','😷','🤒','🤕','🤢',
  '🤮','🤧','😇','🥳','🥺','🫶','❤️','🧡','💛','💚','💙','💜','🖤','🤍','🤎','💔','💕','💞','💓','💗',
  '✅','☑️','✔️','✳️','⭐','🌟','🔥','💥','💯','📌','📍','🧠','🧩','📈','📊','📝','📚','🎯','⚡','🔒',
  '👍','👎','👏','🙌','🤝','👊','✊','🤞','✌️','👌','🙏','💪','🫰','🧿','🧧','🎁','🎉','🏆','🥇','🥈',
  '🥉','🚀','🛰️','🌈','☀️','🌙','⭐️','🌊','🍀','🌻','🌸','🍎','🍵','☕','🥗','🍜','🍣','🍰','🎵','🎬'
];

const emojiGrid = document.getElementById('emojiGrid');
function buildEmojiGrid() {{
  emojiGrid.innerHTML = '';
  EMOJIS.forEach(e => {{
    const b = document.createElement('button');
    b.type = 'button';
    b.textContent = e;
    b.style.cursor = 'pointer';
    b.style.border = '1px solid rgba(0,0,0,0.08)';
    b.style.background = '#fff';
    b.style.borderRadius = '10px';
    b.style.padding = '6px 0';
    b.style.fontSize = '18px';
    b.addEventListener('click', () => {{
      const range = quill.getSelection(true) || {{ index: quill.getLength(), length: 0 }};
      quill.insertText(range.index, e);
      quill.setSelection(range.index + 2, 0);
      saveLocal();
    }});
    emojiGrid.appendChild(b);
  }});
}}
buildEmojiGrid();

const emojiPanel = document.getElementById('emojiPanel');
document.getElementById('btnEmoji').addEventListener('click', () => {{
  emojiPanel.style.display = (emojiPanel.style.display === 'none' || !emojiPanel.style.display) ? 'block' : 'none';
}});
document.getElementById('emojiClose').addEventListener('click', () => {{
  emojiPanel.style.display = 'none';
}});

function getFontFamilyByKey(key) {{
  const map = {{
    wechat: '-apple-system,BlinkMacSystemFont,"PingFang SC","Helvetica Neue",Arial,"Microsoft YaHei",sans-serif',
    simsun: 'SimSun,宋体,serif',
    simhei: 'SimHei,黑体,sans-serif',
    yahei: '"Microsoft YaHei","微软雅黑",sans-serif',
    pingfang: '"PingFang SC","苹方",-apple-system,BlinkMacSystemFont,sans-serif',
    kaiti: 'KaiTi,楷体,serif',
    fangsong: 'FangSong,仿宋,serif',
    arial: 'Arial,sans-serif',
    helvetica: 'Helvetica,Arial,sans-serif',
    times: '"Times New Roman",Times,serif',
    georgia: 'Georgia,serif',
    courier: '"Courier New",Courier,monospace',
    monospace: 'ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,"Liberation Mono","Courier New",monospace'
  }};
  return map[key] || map.wechat;
}}

function getToolbarFontKey() {{
  const sel = document.querySelector('#toolbar .ql-font');
  const v = (sel && sel.value) ? sel.value : 'wechat';
  return v;
}}

function getToolbarSizePx() {{
  return clampSize(fontSizeInput.value);
}}

function applyWechatLayout() {{
  const root = getEditorRoot();
  if (!root) return;

  const fontKey = getToolbarFontKey();
  const baseSize = getToolbarSizePx();

  root.style.fontFamily = getFontFamilyByKey(fontKey);
  root.style.fontSize = baseSize + 'px';
  root.style.lineHeight = '2';
  root.style.color = '#000';

  root.querySelectorAll('p').forEach(p => {{
    p.style.margin = '0 0 14px 0';
    p.style.fontFamily = getFontFamilyByKey(fontKey);
    p.style.fontSize = baseSize + 'px';
    p.style.lineHeight = '2';
    p.style.color = '#000';
  }});

  root.querySelectorAll('p').forEach(p => {{
    const t = (p.innerText || '').trim();
    if (/^0[1-4]\\.\\s+/.test(t) || t === "【推荐爆款标题】") {{
      const h2 = document.createElement('h2');
      h2.innerText = t;
      h2.style.fontFamily = 'SimHei,黑体,sans-serif';
      h2.style.fontSize = (Math.max(16, Math.min(22, baseSize + 1))) + 'px';
      h2.style.fontWeight = '800';
      h2.style.margin = '18px 0 8px 0';
      h2.style.borderLeft = '5px solid #07c160';
      h2.style.paddingLeft = '10px';
      h2.style.color = '#000';
      p.replaceWith(h2);
    }}
  }});

  saveLocal();
  toast('已应用公众号排版');
}}
document.getElementById('btnApply').addEventListener('click', applyWechatLayout);

async function copyRichAll() {{
  const root = getEditorRoot();
  if (!root) return;

  const fontKey = getToolbarFontKey();
  const baseSize = getToolbarSizePx();

  const clone = root.cloneNode(true);
  clone.querySelectorAll('p').forEach(p => {{
    p.style.margin = '0 0 14px 0';
    p.style.fontFamily = getFontFamilyByKey(fontKey);
    p.style.fontSize = baseSize + 'px';
    p.style.lineHeight = '2';
    p.style.color = '#000';
  }});
  clone.querySelectorAll('h2').forEach(h2 => {{
    h2.style.fontFamily = 'SimHei,黑体,sans-serif';
    h2.style.fontSize = (Math.max(16, Math.min(22, baseSize + 1))) + 'px';
    h2.style.fontWeight = '800';
    h2.style.margin = '18px 0 8px 0';
    h2.style.borderLeft = '5px solid #07c160';
    h2.style.paddingLeft = '10px';
    h2.style.color = '#000';
  }});

  const htmlText = `<div style="font-family:${{getFontFamilyByKey(fontKey)}};font-size:${{baseSize}}px;line-height:2;color:#000;">${{clone.innerHTML}}</div>`;
  const plainText = root.innerText || '';

  try {{
    if (navigator.clipboard && window.ClipboardItem) {{
      const htmlBlob = new Blob([htmlText], {{ type: "text/html" }});
      const textBlob = new Blob([plainText], {{ type: "text/plain" }});
      const item = new ClipboardItem({{ "text/html": htmlBlob, "text/plain": textBlob }});
      await navigator.clipboard.write([item]);
      toast("已复制富文本");
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
    sel.removeAllRanges(); sel.addRange(range);

    document.execCommand('copy');
    sel.removeAllRanges();
    document.body.removeChild(temp);
    toast("已复制富文本");
  }} catch(e) {{
    toast("复制失败：请使用 HTTPS 或更换浏览器");
  }}
}}
document.getElementById('btnCopyRich').addEventListener('click', copyRichAll);

async function copyMarkdownAll() {{
  const root = getEditorRoot();
  if (!root) return;

  const htmlInner = root.innerHTML || '';
  let md = '';
  try {{
    const service = new TurndownService({{
      headingStyle:'atx',
      codeBlockStyle:'fenced',
      emDelimiter:'*'
    }});
    md = service.turndown(htmlInner);
  }} catch(e) {{
    md = root.innerText || '';
  }}

  try {{
    await navigator.clipboard.writeText(md);
    toast("已复制 Markdown");
  }} catch(e) {{
    const el = document.createElement("textarea");
    el.value = md;
    document.body.appendChild(el);
    el.select();
    document.execCommand('copy');
    document.body.removeChild(el);
    toast("已复制 Markdown");
  }}
}}
document.getElementById('btnCopyMd').addEventListener('click', copyMarkdownAll);

document.getElementById('btnClear').addEventListener('click', () => {{
  if (!confirm("确定清空编辑器内容？")) return;
  quill.setText('');
  localStorage.setItem(KEY_HTML, '');
  localStorage.setItem(KEY_VER, VERSION);
  toast('已清空');
}});
</script>
""", height=900, scrolling=True)

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
        target_words = st.number_input(
            "目标字数（默认1000，可点击输入）",
            min_value=200,
            value=1000,
            step=100,
            key="target_words"
        )
        st.caption("建议 800–2000；可随意输入。模型会尽量贴近目标字数（允许少量浮动）。")

    with st.expander("抓取失败？这里可手动粘贴原文继续生成（可选）", expanded=False):
        st.session_state.manual_text = st.text_area(
            "📄 粘贴原文（抓不到链接时会用这里的内容）",
            value=st.session_state.manual_text,
            height=180,
            placeholder="当公众号链接抓取失败时，把文章原文粘贴到这里再点“开始生成”。"
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
                target_words=int(target_words)
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



