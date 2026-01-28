def render_wechat_editor(initial_html: str, version: int):
    init_js = json.dumps(initial_html or "")
    ver_js = json.dumps(str(version))

    # 用占位符，最后再替换，避免 f-string 和 .format 的大括号问题
    html = """
<link href="https://cdn.jsdelivr.net/npm/quill@1.3.7/dist/quill.snow.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/quill@1.3.7/dist/quill.min.js"></script>
<script src="https://unpkg.com/turndown/dist/turndown.js"></script>

<div id="wrap" style="border:1px solid #07c160;border-radius:12px;background:#fff;">
  <!-- 顶部固定操作区 -->
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

    <!-- 顶部消息条（替代各种 alert/confirm/prompt） -->
    <div id="msgBar" style="margin-top:6px;font-size:12px;min-height:18px;color:#07c160;"></div>

    <!-- 工具栏固定在 topbar 内 -->
    <div id="toolbar" style="margin-top:10px;border:1px solid rgba(0,0,0,0.08);border-radius:10px;padding:6px 8px;display:flex;flex-wrap:wrap;gap:6px;align-items:center;">
      <span class="ql-formats">
        <button class="ql-undo" type="button">↶</button>
        <button class="ql-redo" type="button">↷</button>
      </span>

      <!-- 自由字号 10–50px -->
      <span class="ql-formats">
        <label style="font-size:12px;margin-right:4px;color:#666;">字号(px)</label>
        <input id="fontSizeInput" type="number" min="10" max="50" value="17" style="width:64px;padding:2px 4px;font-size:12px;"/>
        <button id="btnFontSizeApply" type="button" style="padding:2px 6px;font-size:12px;">应用</button>
      </span>

      <!-- 字体下拉 -->
      <span class="ql-formats">
        <select id="fontSelect" style="min-width:170px;font-size:12px;">
          <option value="">公众号默认字体</option>
          <option value="SimSun,宋体,serif">宋体（正文推荐）</option>
          <option value="SimHei,黑体,sans-serif">黑体（小标题推荐）</option>
          <option value="Microsoft YaHei,微软雅黑,sans-serif">微软雅黑</option>
          <option value="KaiTi,楷体,serif">楷体</option>
          <option value="FangSong,仿宋,serif">仿宋</option>
          <option value="PingFang SC,Helvetica Neue,Arial,sans-serif">苹方</option>
          <option value="Arial,Helvetica,sans-serif">Arial</option>
          <option value="Times New Roman,Times,serif">Times New Roman</option>
          <option value="Tahoma,Geneva,sans-serif">Tahoma</option>
          <option value="Verdana,Geneva,sans-serif">Verdana</option>
          <option value="Georgia,serif">Georgia</option>
          <option value="Courier New,Courier,monospace">Courier New</option>
        </select>
        <button id="btnFontApply" type="button" style="padding:2px 6px;font-size:12px;">应用</button>
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
        <button id="btnEmoji" type="button">😊</button>
      </span>
    </div>

    <!-- 富表情面板 -->
    <div id="emojiPanel" class="emoji-panel"></div>
  </div>

  <!-- 可滚动编辑区 -->
  <div id="editorHost" style="padding:12px;">
    <div id="editor" style="border:1px solid rgba(0,0,0,0.08);border-radius:12px;"></div>
    <div style="margin-top:10px;color:#666;font-size:12px;line-height:1.6;">
      提示：复制富文本可直接贴公众号后台；复制Markdown用于二次处理（不保证公众号完全等效渲染）。
    </div>
  </div>
</div>

<style>
.ql-container {{ border:none !important; font-family:SimSun,宋体,serif; }}
.ql-editor {{
  min-height: 520px;
  font-size: 17px;
  line-height: 2;
  color: #000;
}}
@media (max-width: 768px) {{
  .ql-editor {{ min-height: 420px; }}
}}
.emoji-panel {{
  display:none;
  margin-top:8px;
  border:1px solid rgba(0,0,0,0.08);
  border-radius:10px;
  padding:8px;
  max-height:210px;
  overflow-y:auto;
  background:#fff;
  box-shadow:0 4px 16px rgba(0,0,0,0.08);
}}
.emoji-item {{
  font-size:20px;
  padding:4px 6px;
  margin:2px;
  border:none;
  background:transparent;
  cursor:pointer;
}}
.emoji-item:hover {{
  background:#f3f3f3;
}}
</style>

<script>
const INITIAL_HTML = __INITIAL_HTML__;
const VERSION = __VERSION__;

// 注册字体/字号（使用 style attributor）
const Font = Quill.import('attributors/style/font');
Font.whitelist = [
  'SimSun,宋体,serif',
  'SimHei,黑体,sans-serif',
  'Microsoft YaHei,微软雅黑,sans-serif',
  'KaiTi,楷体,serif',
  'FangSong,仿宋,serif',
  'PingFang SC,Helvetica Neue,Arial,sans-serif',
  'Arial,Helvetica,sans-serif',
  'Times New Roman,Times,serif',
  'Tahoma,Geneva,sans-serif',
  'Verdana,Geneva,sans-serif',
  'Georgia,serif',
  'Courier New,Courier,monospace'
];
Quill.register(Font, true);

const SizeStyle = Quill.import('attributors/style/size');
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

function getMsgBar() {
  return document.getElementById('msgBar');
}
function showMsg(text, isError) {
  const bar = getMsgBar();
  if (!bar) return;
  bar.textContent = text || '';
  bar.style.color = isError ? '#d03050' : '#07c160';
  if (text) {
    const current = text;
    setTimeout(() => {
      if (bar.textContent === current) bar.textContent = '';
    }, 3000);
  }
}

function setEditorHtml(h) {
  quill.clipboard.dangerouslyPasteHTML(h || "");
}

function getEditorRoot() {
  return document.querySelector('#editor .ql-editor');
}

function saveLocal() {
  const root = getEditorRoot();
  if (!root) return;
  localStorage.setItem(KEY_HTML, root.innerHTML || "");
  localStorage.setItem(KEY_VER, VERSION);
}

// 首次加载
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

// 编辑时节流保存
let saveTimer = null;
quill.on('text-change', function(){
  if (saveTimer) clearTimeout(saveTimer);
  saveTimer = setTimeout(saveLocal, 400);
});

// undo/redo
document.querySelector('.ql-undo').addEventListener('click', () => quill.history.undo());
document.querySelector('.ql-redo').addEventListener('click', () => quill.history.redo());

// HR
document.getElementById('btnHr').addEventListener('click', () => {
  const range = quill.getSelection(true) || { index: quill.getLength() };
  quill.clipboard.dangerouslyPasteHTML(range.index, '<p><hr/></p>');
  saveLocal();
});

// 字号应用（10–50px）
document.getElementById('btnFontSizeApply').addEventListener('click', () => {
  const input = document.getElementById('fontSizeInput');
  let v = parseInt(input.value || '0', 10);
  if (!v || v < 10 || v > 50) {
    showMsg('字号范围为 10–50px', true);
    return;
  }
  const range = quill.getSelection();
  const len = quill.getLength();
  const target = (range && range.length > 0) ? range : { index: 0, length: len };
  quill.formatText(target.index, target.length, 'size', v + 'px');
  saveLocal();
  showMsg('已应用字号 ' + v + 'px');
});

// 字体应用
document.getElementById('btnFontApply').addEventListener('click', () => {
  const select = document.getElementById('fontSelect');
  const value = select.value;
  const range = quill.getSelection();
  const len = quill.getLength();
  const target = (range && range.length > 0) ? range : { index: 0, length: len };
  if (value) {
    quill.formatText(target.index, target.length, 'font', value);
    showMsg('已应用字体');
  } else {
    quill.formatText(target.index, target.length, 'font', false);
    showMsg('已恢复默认字体');
  }
  saveLocal();
});

// 富表情面板
const EMOJIS = [
  '😀','😁','😂','🤣','😃','😄','😅','😆','😉','😊','😋','😍','😘','😗','😙','😚','🙂','🤗','🤩','🤔',
  '😐','😑','😶','🙄','😏','😣','😥','😮','🤐','😯','😪','😫','🥱','😴','😌','😛','😜','😝','🤤','😓',
  '😔','😕','🙃','🤑','😲','☹️','🙁','😖','😞','😟','😤','😢','😭','😦','😧','😨','😩','🤯','😬','😰',
  '😱','🥵','🥶','😳','🤪','😵','😡','😠','🤬','😷','🤒','🤕','🤢','🤮','🤧','😇','🥰','🤝','👍','👎',
  '👌','🙏','👏','💪','🔥','⭐','🌟','🚀','🎯','📌','📍','🧠','💡','✅','❌'
];

const emojiPanel = document.getElementById('emojiPanel');
EMOJIS.forEach(e => {
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'emoji-item';
  btn.textContent = e;
  btn.addEventListener('click', () => {
    const range = quill.getSelection(true) || { index: quill.getLength() };
    quill.insertText(range.index, e);
    quill.setSelection(range.index + e.length);
    saveLocal();
  });
  emojiPanel.appendChild(btn);
});

document.getElementById('btnEmoji').addEventListener('click', () => {
  if (!emojiPanel) return;
  const visible = emojiPanel.style.display === 'block';
  emojiPanel.style.display = visible ? 'none' : 'block';
});

// 一键排版
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
    if (/^0[1-4]\\.\s+/.test(t) || t === "【推荐爆款标题】") {
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
  showMsg('已应用公众号排版');
}
document.getElementById('btnApply').addEventListener('click', applyWechatLayout);

// 复制富文本（不自动排版）
async function copyRichAll() {
  const root = getEditorRoot();
  if (!root) return;

  const htmlText = `<div style="font-family:SimSun,宋体,serif;font-size:17px;line-height:2;color:#000;">${root.innerHTML}</div>`;
  const plainText = root.innerText || '';

  try {
    if (navigator.clipboard && window.ClipboardItem) {
      const htmlBlob = new Blob([htmlText], { type: "text/html" });
      const textBlob = new Blob([plainText], { type: "text/plain" });
      const item = new ClipboardItem({ "text/html": htmlBlob, "text/plain": textBlob });
      await navigator.clipboard.write([item]);
      showMsg("已复制（富文本，保留样式）");
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
    showMsg("已复制（富文本，保留样式）");
  } catch(e) {
    showMsg("复制失败：请使用支持剪贴板的浏览器", true);
  }
}
document.getElementById('btnCopyRich').addEventListener('click', copyRichAll);

// 复制 Markdown
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
    showMsg("已复制 Markdown");
  } catch(e) {
    const el = document.createElement("textarea");
    el.value = md;
    document.body.appendChild(el);
    el.select();
    document.execCommand('copy');
    document.body.removeChild(el);
    showMsg("已复制 Markdown（兼容模式）");
  }
}
document.getElementById('btnCopyMd').addEventListener('click', copyMarkdownAll);

// 清空
document.getElementById('btnClear').addEventListener('click', () => {
  quill.setText('');
  localStorage.setItem(KEY_HTML, '');
  localStorage.setItem(KEY_VER, VERSION);
  showMsg('已清空编辑器内容');
});
</script>
"""

    html = html.replace("__INITIAL_HTML__", init_js).replace("__VERSION__", ver_js)
    components.html(html, height=860)
