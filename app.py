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
st.set_page_config(page_title="深度重构级专业工作台", layout="centered")

# =============================
# 1) Global CSS（强制浅色 + 绿色主题 + tabs 常显）
# =============================
st.markdown("""
<style>
:root, body, .stApp { color-scheme: light !important; }
.stApp { background:#ffffff !important; color:#000000 !important; padding-bottom: 90px; }

h1 { color:#07c160 !important; font-family:"Microsoft YaHei"; text-align:center; font-weight:900; }

/* 输入框 */
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

/* Streamlit tabs：始终显示文字，不要 hover 才清晰 */
.stTabs [data-baseweb="tab"] {
  font-size: 16px !important;
  font-weight: 800 !important;
  color: #111 !important;
  opacity: 1 !important;
}
.stTabs [aria-selected="true"] {
  color:#07c160 !important;
}
.stTabs [data-baseweb="tab-border"] {
  background: rgba(7,193,96,0.25) !important;
}

/* 绿色按钮（覆盖默认） */
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

/* 页脚 */
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

/* 让 components iframe 不要太窄 */
.block-container { max-width: 980px; }
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


# =============================
# 2) Helpers
# =============================
def get_article_content(url: str):
    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X)"}
    try:
        res = requests.get(url, headers=headers, timeout=12)
        soup = BeautifulSoup(res.text, "html.parser")
        content_div = soup.find("div", id="js_content")
        return content_div.get_text(separator="\n", strip=True) if content_div else None
    except:
        return None


def stream_ai_rewrite(text: str, api_key: str, temperature: float = 0.8):
    url = "https://api.deepseek.com/chat/completions"
    system_prompt = """假设你是一个专业的自媒体作家。对下文进行二创。
【原创加强建议】：句型词汇调整、内容拓展、避免关键词、结构逻辑调整、视角切换、重点聚焦、角度转换、避免直接引用。
【核心禁令】：
- 永远不要出现“不是....，而是”的句式。
- 绝对不要出现破折号（——）。
- 绝对禁止结构化：禁止使用列表、分点（如1.2.3.或●），保持段落连贯性。
【输出结构】：
1. 第一行写【推荐爆款标题】，接着输出5个爆款标题，每行一个（标题的标点不要删）。
2. 标题区后空三行。
3. 正文开头必须先写150字引入语。
4. 小标题格式固定为 ## 01. XXX，总数控制在 2-4 个。
"""
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"原文=（{text}）"},
        ],
        "stream": True,
        "temperature": float(temperature),
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    return requests.post(url, headers=headers, json=payload, stream=True, timeout=60)


def normalize_text(text: str) -> str:
    """
    只做必要规范化：
    - 还原 \\n
    - 强制标题区域每个标题换行（模型若粘连会拆开不了，这里只保证已有换行不被吃掉）
    - 禁止“不是..而是”句式的硬替换（只替换这一类，不动标点）
    """
    if not text:
        return ""
    text = text.replace("\\n", "\n")

    # 只对“不是...而是”做规避（不动破折号、标题标点）
    text = re.sub(r"不是(.{0,40})而是", r"不单是\1更是", text)

    # 保证【推荐爆款标题】后一定换行
    text = re.sub(r"(【推荐爆款标题】)\s*", r"【推荐爆款标题】\n", text)

    # 小标题前空行
    text = re.sub(r"(\n?)(##\s*0[1-4]\.)", r"\n\n\2", text)

    return text.strip()


def plain_to_rich_html(plain: str) -> str:
    """
    把生成的纯文本转为默认“公众号排版感”的 HTML：
    - 正文：宋体 17px
    - 小标题（## 01.）：黑体 18px 加粗
    - 标题区：按段落输出
    """
    if not plain:
        return ""

    lines = plain.splitlines()
    out = []
    for ln in lines:
        s = ln.strip()
        if not s:
            out.append("<p><br></p>")
            continue

        # 小标题：## 01.
        if s.startswith("##"):
            title = html.escape(s.replace("##", "", 1).strip())
            out.append(f"<p><span style='font-family:SimHei, \"Microsoft YaHei\", sans-serif; font-size:18px; font-weight:700;'>{title}</span></p>")
            continue

        # 其它：正文
        out.append(f"<p><span style='font-family:SimSun, serif; font-size:17px;'>{html.escape(s)}</span></p>")

    return "\n".join(out)


# =============================
# 3) Session State
# =============================
if "is_generating" not in st.session_state:
    st.session_state.is_generating = False
if "last_plain" not in st.session_state:
    st.session_state.last_plain = ""
if "last_rich_html" not in st.session_state:
    st.session_state.last_rich_html = ""


# =============================
# 4) Editor Component (Quill)
# =============================
def render_wechat_editor(initial_html: str):
    """
    - 工具栏 sticky
    - 编辑区可滚动（内部滚动）
    - 字号：只保留输入框 10-50（方案A）
    - 字体：下拉（宋体/黑体/公众号默认+常见）
    - emoji：quill-emoji（较丰富）
    - 无表格按钮/脚本
    - 复制：富文本（HTML）/ Markdown（turndown）
    - 无 alert 弹窗（用右上角 toast）
    """
    # 注意：不要用 Python f-string 直接写 CSS 花括号，容易触发 SyntaxError
    safe_initial = initial_html or ""
    safe_initial_json = json.dumps(safe_initial)

    component_html = """
<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />

<link href="https://cdn.jsdelivr.net/npm/quill@1.3.7/dist/quill.snow.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/quill-emoji@0.1.7/dist/quill-emoji.css" rel="stylesheet">

<style>
  body { margin:0; padding:0; background:#fff; }

  .wrap{
    border:2px solid #07c160;
    border-radius:14px;
    padding:14px;
    background:#fff;
    font-family: "Microsoft YaHei", sans-serif;
  }

  .header{
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:12px;
    margin-bottom:10px;
  }

  .title{
    font-size:18px;
    font-weight:900;
    color:#111;
  }

  .actions{
    display:flex;
    gap:10px;
    flex-wrap:wrap;
    justify-content:flex-end;
  }

  .btn{
    border:none;
    border-radius:10px;
    padding:10px 14px;
    font-weight:900;
    cursor:pointer;
    font-size:14px;
  }
  .btn-green{ background:#07c160; color:#fff; }
  .btn-green:hover{ background:#06b457; }
  .btn-ghost{
    background:#f3f5f7; color:#111; border:1px solid rgba(0,0,0,0.12);
  }

  .toolbarRow{
    display:flex;
    align-items:center;
    gap:10px;
    flex-wrap:wrap;
    margin:10px 0 10px 0;
  }

  .field{
    display:flex;
    align-items:center;
    gap:6px;
    padding:6px 10px;
    border:1px solid rgba(0,0,0,0.12);
    border-radius:10px;
    background:#fff;
  }
  .field label{
    font-size:12px;
    font-weight:800;
    color:#333;
    white-space:nowrap;
  }
  .field select, .field input{
    border:none;
    outline:none;
    font-size:14px;
    font-weight:800;
    background:transparent;
  }
  .field input{
    width:70px;
  }

  /* Quill 外框 */
  #editorShell{
    border:1px solid rgba(0,0,0,0.12);
    border-radius:12px;
    overflow:hidden;
    background:#fff;
  }

  /* 工具栏 sticky */
  #toolbar{
    background:#fff;
    position:sticky;
    top:0;
    z-index:5;
    border-bottom:1px solid rgba(0,0,0,0.10);
  }

  .ql-toolbar.ql-snow{
    border:none;
    padding:10px;
  }
  .ql-container.ql-snow{
    border:none;
  }

  /* 编辑区滚动：高度由 JS 动态设置 */
  .ql-editor{
    line-height:2;
    padding:18px 16px;
    overflow-y:auto;
  }

  /* toast */
  .toast{
    position:fixed;
    right:16px;
    top:16px;
    background: rgba(17,17,17,0.92);
    color:#fff;
    padding:10px 12px;
    border-radius:10px;
    font-size:13px;
    font-weight:800;
    opacity:0;
    transform: translateY(-6px);
    transition: all .2s ease;
    z-index:9999;
    pointer-events:none;
  }
  .toast.show{
    opacity:1;
    transform: translateY(0);
  }

  /* 字体映射：Quill font class -> font-family */
  .ql-font-wechat { font-family: -apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif; }
  .ql-font-simsun { font-family: SimSun, "宋体", serif; }
  .ql-font-simhei { font-family: SimHei, "黑体","Microsoft YaHei",sans-serif; }
  .ql-font-yahei  { font-family: "Microsoft YaHei", sans-serif; }
  .ql-font-pingfang { font-family: "PingFang SC", -apple-system, sans-serif; }
  .ql-font-kaiti  { font-family: KaiTi, "楷体", serif; }
  .ql-font-fangsong { font-family: FangSong, "仿宋", serif; }
  .ql-font-arial  { font-family: Arial, sans-serif; }
  .ql-font-times  { font-family: "Times New Roman", serif; }
  .ql-font-georgia{ font-family: Georgia, serif; }
  .ql-font-courier{ font-family: "Courier New", monospace; }
  .ql-font-verdana{ font-family: Verdana, sans-serif; }
  .ql-font-tahoma { font-family: Tahoma, sans-serif; }
  .ql-font-impact { font-family: Impact, sans-serif; }
  .ql-font-comic  { font-family: "Comic Sans MS", cursive; }

  /* 移除 Quill 默认 size 下拉样式残留（我们不使用 size dropdown） */
  .ql-size { display:none !important; }

</style>
</head>

<body>
<div class="toast" id="toast">已复制</div>

<div class="wrap">
  <div class="header">
    <div class="title">公众号排版编辑器（所见即所得）</div>
    <div class="actions">
      <button class="btn btn-green" id="btnFormat">✨ 一键排版</button>
      <button class="btn btn-green" id="btnCopyRich">📋 复制富文本</button>
      <button class="btn btn-green" id="btnCopyMd">🧾 复制Markdown</button>
      <button class="btn btn-ghost" id="btnClear">🧹 清空</button>
    </div>
  </div>

  <div class="toolbarRow">
    <div class="field">
      <label>字体</label>
      <select id="fontSelect">
        <option value="wechat">公众号默认</option>
        <option value="simsun">宋体</option>
        <option value="simhei">黑体</option>
        <option value="yahei">微软雅黑</option>
        <option value="pingfang">苹方</option>
        <option value="kaiti">楷体</option>
        <option value="fangsong">仿宋</option>
        <option value="arial">Arial</option>
        <option value="times">Times New Roman</option>
        <option value="georgia">Georgia</option>
        <option value="courier">Courier New</option>
        <option value="verdana">Verdana</option>
        <option value="tahoma">Tahoma</option>
        <option value="impact">Impact</option>
        <option value="comic">Comic Sans MS</option>
      </select>
    </div>

    <div class="field">
      <label>字号</label>
      <input id="sizeInput" type="number" min="10" max="50" step="1" value="17" />
      <span style="font-weight:900;color:#333;">px</span>
    </div>

    <div style="font-size:12px;color:#666;font-weight:800;">
      提示：编辑区可滚动；工具栏/复制按钮固定在顶部。
    </div>
  </div>

  <div id="editorShell">
    <div id="toolbar">
      <!-- Quill toolbar：不含表格 -->
      <span class="ql-formats">
        <button class="ql-undo">↶</button>
        <button class="ql-redo">↷</button>
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
        <button class="ql-list" value="ordered"></button>
        <button class="ql-list" value="bullet"></button>
        <button class="ql-indent" value="-1"></button>
        <button class="ql-indent" value="+1"></button>
      </span>

      <span class="ql-formats">
        <button class="ql-blockquote"></button>
        <button class="ql-code-block"></button>
        <button class="ql-link"></button>
      </span>

      <!-- emoji：更丰富 -->
      <span class="ql-formats">
        <button class="ql-emoji"></button>
      </span>
    </div>

    <div id="editor"></div>
  </div>

  <div style="margin-top:10px;color:#666;font-size:12px;font-weight:800;">
    复制富文本用于直接粘贴公众号；复制Markdown用于你二次处理（公众号内不保证完全等效渲染）。
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/quill@1.3.7/dist/quill.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/quill-emoji@0.1.7/dist/quill-emoji.js"></script>
<script src="https://cdn.jsdelivr.net/npm/turndown@7.1.2/dist/turndown.js"></script>

<script>
  const INITIAL_HTML = __INITIAL_HTML__;

  function showToast(msg){
    const t = document.getElementById('toast');
    t.textContent = msg || '完成';
    t.classList.add('show');
    setTimeout(()=>t.classList.remove('show'), 900);
  }

  // 动态计算编辑区高度（手机 360~420；桌面 520~640）
  function computeEditorHeight(){
    const w = window.innerWidth || 1024;
    const vh = window.innerHeight || 800;
    let h = Math.round(vh * 0.55);

    if (w <= 768){
      h = Math.max(360, Math.min(420, h));
    }else{
      h = Math.max(520, Math.min(640, h));
    }
    return h;
  }

  // Quill 注册 font whitelist
  const Font = Quill.import('formats/font');
  Font.whitelist = [
    'wechat','simsun','simhei','yahei','pingfang','kaiti','fangsong',
    'arial','times','georgia','courier','verdana','tahoma','impact','comic'
  ];
  Quill.register(Font, true);

  // 自定义 Undo/Redo（防止工具栏空）
  function undoChange() { this.quill.history.undo(); }
  function redoChange() { this.quill.history.redo(); }

  // 初始化 Quill
  const quill = new Quill('#editor', {
    theme: 'snow',
    modules: {
      toolbar: {
        container: '#toolbar',
        handlers: {
          'undo': undoChange,
          'redo': redoChange
        }
      },
      history: { delay: 500, maxStack: 200, userOnly: true },
      "emoji-toolbar": true,
      "emoji-textarea": false,
      "emoji-shortname": true
    }
  });

  // 设置编辑区滚动高度
  function applyEditorHeight(){
    const h = computeEditorHeight();
    const container = document.querySelector('.ql-container');
    const editor = document.querySelector('.ql-editor');
    if(container) container.style.height = h + 'px';
    if(editor) editor.style.height = h + 'px';
  }
  applyEditorHeight();
  window.addEventListener('resize', applyEditorHeight);

  // 默认内容
  if (INITIAL_HTML && INITIAL_HTML.trim().length > 0){
    quill.clipboard.dangerouslyPasteHTML(INITIAL_HTML);
  }else{
    quill.clipboard.dangerouslyPasteHTML("<p><span style='font-family:SimSun,serif;font-size:17px;'>在这里开始编辑…</span></p>");
  }

  // 外部控件：字体/字号（方案A：只有输入框）
  const fontSelect = document.getElementById('fontSelect');
  const sizeInput = document.getElementById('sizeInput');

  function applyFont(fontVal){
    quill.format('font', fontVal);
  }

  function applySize(px){
    const n = parseInt(String(px).replace('px',''), 10);
    if (isNaN(n)) return;
    const clamped = Math.min(50, Math.max(10, n));
    quill.format('size', clamped + 'px');
    sizeInput.value = clamped;
  }

  fontSelect.addEventListener('change', () => {
    applyFont(fontSelect.value);
  });

  // 输入/滚轮/回车 都生效
  sizeInput.addEventListener('input', () => applySize(sizeInput.value));
  sizeInput.addEventListener('change', () => applySize(sizeInput.value));
  sizeInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') applySize(sizeInput.value);
  });

  // 默认：公众号常用（正文宋体17）
  applyFont('simsun');
  applySize(17);

  // 一键排版：把“## 01.”识别成黑体18、加粗；其余段落宋体17
  function oneKeyFormat(){
    const root = quill.root;
    const ps = root.querySelectorAll('p');
    ps.forEach(p => {
      const txt = (p.innerText || '').trim();
      if (!txt){
        // 空行
        p.innerHTML = "<br>";
        return;
      }
      if (txt.startsWith("##")){
        const t = txt.replace(/^##\s*/, '');
        p.innerHTML = "<span style='font-family:SimHei, \"Microsoft YaHei\", sans-serif; font-size:18px; font-weight:700;'>" + escapeHtml(t) + "</span>";
      }else{
        // 其它正文
        // 保留原有内联格式就不强行覆盖；但如果纯文本则补默认样式
        const hasSpan = p.querySelector('span');
        if(!hasSpan){
          p.innerHTML = "<span style='font-family:SimSun, serif; font-size:17px;'>" + escapeHtml(txt) + "</span>";
        }
      }
    });
  }

  function escapeHtml(s){
    return String(s)
      .replaceAll("&","&amp;")
      .replaceAll("<","&lt;")
      .replaceAll(">","&gt;")
      .replaceAll('"',"&quot;")
      .replaceAll("'","&#039;");
  }

  // 复制富文本（HTML）到剪贴板：使用 Clipboard API + html/plain 双格式
  async function copyRich(){
    const htmlStr = quill.root.innerHTML;
    const plainStr = quill.getText();

    try{
      if (navigator.clipboard && window.ClipboardItem){
        const item = new ClipboardItem({
          "text/html": new Blob([htmlStr], {type:"text/html"}),
          "text/plain": new Blob([plainStr], {type:"text/plain"})
        });
        await navigator.clipboard.write([item]);
      }else{
        // fallback：选区复制
        const temp = document.createElement('div');
        temp.style.position = 'fixed';
        temp.style.left = '-9999px';
        temp.innerHTML = htmlStr;
        document.body.appendChild(temp);

        const range = document.createRange();
        range.selectNodeContents(temp);
        const sel = window.getSelection();
        sel.removeAllRanges();
        sel.addRange(range);

        document.execCommand('copy');
        sel.removeAllRanges();
        document.body.removeChild(temp);
      }
      showToast("已复制富文本");
    }catch(e){
      showToast("复制失败（浏览器限制）");
    }
  }

  // 复制 Markdown（用 Turndown）
  function copyMarkdown(){
    const htmlStr = quill.root.innerHTML;
    const turndownService = new TurndownService({
      headingStyle: 'atx',
      codeBlockStyle: 'fenced'
    });
    let md = turndownService.turndown(htmlStr);

    // 小修：把可能的连续空行收敛
    md = md.replace(/\\n{3,}/g, "\\n\\n").trim();

    // 写入剪贴板
    if(navigator.clipboard){
      navigator.clipboard.writeText(md).then(()=>showToast("已复制Markdown"));
    }else{
      const ta = document.createElement('textarea');
      ta.value = md;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
      showToast("已复制Markdown");
    }
  }

  function clearEditor(){
    quill.setText('');
    showToast("已清空");
  }

  document.getElementById('btnFormat').addEventListener('click', ()=>{ oneKeyFormat(); showToast("已应用排版"); });
  document.getElementById('btnCopyRich').addEventListener('click', copyRich);
  document.getElementById('btnCopyMd').addEventListener('click', copyMarkdown);
  document.getElementById('btnClear').addEventListener('click', clearEditor);

</script>
</body>
</html>
""".replace("__INITIAL_HTML__", safe_initial_json)

    components.html(component_html, height=760, scrolling=True)


# =============================
# 5) UI: Tabs
# =============================
tab_gen, tab_edit = st.tabs(["🚀 二创生成", "🧩 手动排版"])

with tab_gen:
    st.subheader("🔗 粘贴公众号链接开始生成")
    target_url = st.text_input("链接", placeholder="https://mp.weixin.qq.com/s/xxxxx")

    # 高级设置（可选）
    with st.expander("高级设置（可选）", expanded=False):
        temperature = st.slider("风格强度（temperature）", 0.2, 1.2, 0.8, 0.01)
        length_mode = st.selectbox("篇幅", ["中", "短", "长"], index=0, help="短=更精炼；长=更充分展开。")

    # 生成按钮：点击后显示“正在生成中”
    btn_label = "正在生成中…" if st.session_state.is_generating else "开始生成"
    clicked = st.button(btn_label, disabled=st.session_state.is_generating)

    if clicked:
        api_key = st.secrets.get("DEEPSEEK_API_KEY")
        if not api_key:
            st.error("未配置 DEEPSEEK_API_KEY（请在 Streamlit Secrets 中添加）")
        elif not target_url:
            st.error("请先粘贴链接")
        else:
            raw_text = get_article_content(target_url)
            if not raw_text:
                st.error("内容抓取失败（可能链接不可访问或被反爬）")
            else:
                st.session_state.is_generating = True

                # 篇幅模式对原文做一点引导（不改变系统 prompt 结构）
                if length_mode == "短":
                    raw_text = raw_text[:3500]
                elif length_mode == "中":
                    raw_text = raw_text[:6000]
                else:
                    raw_text = raw_text[:9000]

                placeholder = st.empty()
                full = ""
                try:
                    resp = stream_ai_rewrite(raw_text, api_key, temperature=temperature)
                    for line in resp.iter_lines():
                        if not line:
                            continue
                        chunk = line.decode("utf-8", errors="ignore")
                        if chunk.startswith("data: "):
                            chunk = chunk[len("data: "):]
                        if chunk.strip() == "[DONE]":
                            break
                        try:
                            data = json.loads(chunk)
                            delta = data["choices"][0]["delta"].get("content", "")
                            if delta:
                                full += delta
                                show = normalize_text(full)
                                # 生成过程中给个可读预览（纯文本）
                                placeholder.markdown("```\n" + show + "\n```")
                        except:
                            continue
                except Exception as e:
                    st.error(f"生成失败：{e}")
                finally:
                    st.session_state.is_generating = False

                final_plain = normalize_text(full)
                st.session_state.last_plain = final_plain
                st.session_state.last_rich_html = plain_to_rich_html(final_plain)

                st.success("生成完成 ✅ 已同步到「手动排版」编辑器（可直接去修改 + 复制富文本/Markdown）")

with tab_edit:
    st.subheader("🧩 手动排版（工具栏 + 一键排版 + 一键复制）")

    # 这里直接把“上次生成内容”作为编辑器初始值（用户无需再点导入）
    render_wechat_editor(st.session_state.last_rich_html)
