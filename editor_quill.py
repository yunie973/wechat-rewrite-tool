# editor_quill.py
import json
import streamlit.components.v1 as components

_TEMPLATE = r"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <link href="https://cdn.jsdelivr.net/npm/quill@1.3.7/dist/quill.snow.css" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/quill@1.3.7/dist/quill.min.js"></script>
  <script src="https://unpkg.com/turndown/dist/turndown.js"></script>
</head>
<body style="margin:0;background:#fff;">

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
        提示：复制富文本可直接贴公众号后台；复制Markdown用于二次处理。
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
      </span>
    </div>
  </div>

  <div id="editorHost" style="padding:12px;">
    <div id="editor" style="border:1px solid rgba(0,0,0,0.08);border-radius:12px;"></div>
  </div>
</div>

<style>
.ql-font-wechat { font-family: -apple-system,BlinkMacSystemFont,"PingFang SC","Helvetica Neue",Arial,"Microsoft YaHei",sans-serif; }
.ql-font-simsun { font-family: SimSun,宋体,serif; }
.ql-font-simhei { font-family: SimHei,黑体,sans-serif; }
.ql-font-yahei { font-family: "Microsoft YaHei","微软雅黑",sans-serif; }
.ql-font-pingfang { font-family: "PingFang SC","苹方",-apple-system,BlinkMacSystemFont,sans-serif; }
.ql-font-kaiti { font-family: KaiTi,楷体,serif; }
.ql-font-fangsong { font-family: FangSong,仿宋,serif; }
.ql-font-arial { font-family: Arial,sans-serif; }
.ql-font-helvetica { font-family: Helvetica,Arial,sans-serif; }
.ql-font-times { font-family: "Times New Roman",Times,serif; }
.ql-font-georgia { font-family: Georgia,serif; }
.ql-font-courier { font-family: "Courier New",Courier,monospace; }
.ql-font-monospace { font-family: ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,"Liberation Mono","Courier New",monospace; }

:root { --editorH: 600px; }
#editor .ql-container { height: var(--editorH) !important; border: none !important; }
#editor .ql-editor {
  height: 100% !important;
  overflow-y: auto !important;
  font-size: 17px;
  line-height: 2;
  color: #000;
  padding: 14px 14px !important;
}
</style>

<script>
const INITIAL_HTML = __INIT__;
const VERSION = __VER__;

function toast(msg) {
  const el = document.getElementById('toast');
  if (!el) return;
  el.textContent = msg || '完成';
  el.style.display = 'inline-block';
  clearTimeout(window.__toastTimer);
  window.__toastTimer = setTimeout(() => { el.style.display = 'none'; }, 1600);
}

function computeEditorH() {
  const w = window.innerWidth || 1024;
  const h = window.innerHeight || 900;
  if (w <= 768) {
    let val = Math.round(h * 0.52);
    val = Math.max(360, Math.min(420, val));
    document.documentElement.style.setProperty('--editorH', val + 'px');
  } else {
    let val = Math.round(h * 0.62);
    val = Math.max(520, Math.min(640, val));
    document.documentElement.style.setProperty('--editorH', val + 'px');
  }
}
computeEditorH();
window.addEventListener('resize', computeEditorH);

const Font = Quill.import('formats/font');
Font.whitelist = ['wechat','simsun','simhei','yahei','pingfang','kaiti','fangsong','arial','helvetica','times','georgia','courier','monospace'];
Quill.register(Font, true);

const SizeStyle = Quill.import('attributors/style/size');
SizeStyle.whitelist = null;
Quill.register(SizeStyle, true);

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
  saveTimer = setTimeout(saveLocal, 400);
});

document.querySelector('.ql-undo').addEventListener('click', () => quill.history.undo());
document.querySelector('.ql-redo').addEventListener('click', () => quill.history.redo());

document.getElementById('btnHr').addEventListener('click', () => {
  const range = quill.getSelection(true) || { index: quill.getLength() };
  quill.clipboard.dangerouslyPasteHTML(range.index, '<p><hr/></p>');
  toast('已插入分割线');
});

async function copyRichAll() {
  const root = getEditorRoot();
  if (!root) return;

  const clone = root.cloneNode(true);
  const htmlText = `<div style="font-size:17px;line-height:2;color:#000;">${clone.innerHTML}</div>`;
  const plainText = root.innerText || '';

  try {
    if (navigator.clipboard && window.ClipboardItem) {
      const htmlBlob = new Blob([htmlText], { type: "text/html" });
      const textBlob = new Blob([plainText], { type: "text/plain" });
      const item = new ClipboardItem({ "text/html": htmlBlob, "text/plain": textBlob });
      await navigator.clipboard.write([item]);
      toast("已复制富文本");
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
    toast("已复制富文本");
  } catch(e) {
    toast("复制失败：请使用 HTTPS 或更换浏览器");
  }
}
document.getElementById('btnCopyRich').addEventListener('click', copyRichAll);

async function copyMarkdownAll() {
  const root = getEditorRoot();
  if (!root) return;

  const htmlInner = root.innerHTML || '';
  let md = '';
  try {
    const service = new TurndownService({ headingStyle:'atx', codeBlockStyle:'fenced', emDelimiter:'*' });
    md = service.turndown(htmlInner);
  } catch(e) {
    md = root.innerText || '';
  }

  try {
    await navigator.clipboard.writeText(md);
    toast("已复制 Markdown");
  } catch(e) {
    const el = document.createElement("textarea");
    el.value = md;
    document.body.appendChild(el);
    el.select();
    document.execCommand('copy');
    document.body.removeChild(el);
    toast("已复制 Markdown");
  }
}
document.getElementById('btnCopyMd').addEventListener('click', copyMarkdownAll);

document.getElementById('btnClear').addEventListener('click', () => {
  if (!confirm("确定清空编辑器内容？")) return;
  quill.setText('');
  localStorage.setItem(KEY_HTML, '');
  localStorage.setItem(KEY_VER, VERSION);
  toast('已清空');
});
</script>

</body>
</html>
"""

def render_wechat_editor(initial_html: str, version: int, height: int = 900):
    init_js = json.dumps(initial_html or "")
    ver_js = json.dumps(str(version))
    html = _TEMPLATE.replace("__INIT__", init_js).replace("__VER__", ver_js)
    components.html(html, height=height, scrolling=True)
