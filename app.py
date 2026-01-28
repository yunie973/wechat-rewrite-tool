def render_wechat_editor(initial_html: str, version: int):
    init_js = json.dumps(initial_html or "")
    ver_js = json.dumps(str(version))

    # 普通三引号字符串，不是 f-string
    html = """
<link href="https://cdn.jsdelivr.net/npm/quill@1.3.7/dist/quill.snow.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/quill@1.3.7/dist/quill.min.js"></script>
<script src="https://unpkg.com/turndown/dist/turndown.js"></script>

<div id="toast" style="position:fixed;top:14px;right:14px;z-index:99999;display:none;
  background:rgba(17,17,17,0.92);color:#fff;padding:10px 12px;border-radius:10px;
  font-weight:800;font-size:14px;box-shadow:0 10px 30px rgba(0,0,0,0.2);">
</div>

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

    <!-- 工具栏固定在 topbar 内 -->
    <div id="toolbar" style="margin-top:10px;border:1px solid rgba(0,0,0,0.08);border-radius:10px;padding:6px 8px;">
      <span class="ql-formats">
        <button class="ql-undo" type="button">↶</button>
        <button class="ql-redo" type="button">↷</button>
      </span>

      <!-- 字体 -->
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

      <!-- 字号：10-50 下拉 + 数字输入 -->
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

      <!-- HR + Emoji（无表格按钮） -->
      <span class="ql-formats">
        <button id="btnHr" type="button">—</button>
        <button id="btnEmoji" type="button">😊</button>
      </span>
    </div>
  </div>

  <!-- 可滚动编辑区 -->
  <div id="editorHost" style="padding:12px;">
    <div id="editor" style="border:1px solid rgba(0,0,0,0.08);border-radius:12px;"></div>
    <div style="margin-top:10px;color:#666;font-size:12px;line-height:1.6;">
      提示：复制富文本可直接贴公众号后台；复制Markdown用于二次处理（不保证公众号完全等效渲染）。
    </div>
  </div>
</div>

<!-- Emoji Modal -->
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
                              grid-template-columns:repeat(12,1fr);gap:8px;">
    </div>
  </div>
</div>

<style>
.ql-container { border:none !important; }
.ql-editor {
  font-family: SimSun,宋体,serif;
  font-size: 17px;
  line-height: 2;
  color: #000;
  min-height: 520px;
}

/* 自适配高度：手机更低，桌面更高 */
@media (max-width: 768px) {
  .ql-editor { min-height: 420px; }
}

/* emoji tab button */
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

/* emoji cell */
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
const INITIAL_HTML = __INIT_JS__;
const VERSION = __VER_JS__;

function showToast(msg, ms=1600) {
  const el = document.getElementById('toast');
  el.innerText = msg;
  el.style.display = 'block';
  clearTimeout(el.__t);
  el.__t = setTimeout(()=>{ el.style.display='none'; }, ms);
}

/* ===== Quill 注册：字体 + 字号（10-50px） ===== */
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

/* ===== 内容持久化 ===== */
const KEY_HTML = 'wechat_editor_html';
const KEY_VER  = 'wechat_editor_ver';

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

// undo/redo
document.querySelector('.ql-undo').addEventListener('click', () => quill.history.undo());
document.querySelector('.ql-redo').addEventListener('click', () => quill.history.redo());

// HR
document.getElementById('btnHr').addEventListener('click', () => {
  const range = quill.getSelection(true) || { index: quill.getLength() };
  quill.clipboard.dangerouslyPasteHTML(range.index, '<p><hr/></p><p></p>');
});

/* ===== 字号：下拉 + 数字输入 ===== */
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
  if (!found && sizeSelect.options.length) {
    sizeSelect.value = '17px';
  }
}
sizeSelect.addEventListener('change', () => applySize(sizeSelect.value));
sizeInput.addEventListener('change', () => {
  const v = parseInt(sizeInput.value || '17', 10);
  applySize(v + 'px');
});
applySize('17px');

/* 一键排版 */
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

/* 复制富文本（不自动排版） */
async function copyRichAll() {
  const root = getEditorRoot();
  if (!root) return;

  const clone = root.cloneNode(true);
  clone.querySelectorAll('p').forEach(p => {
    if (!p.style.margin) p.style.margin = '0 0 14px 0';
    if (!p.style.fontFamily) p.style.fontFamily = 'SimSun,宋体,serif';
    if (!p.style.fontSize) p.style.fontSize = '17px';
    if (!p.style.lineHeight) p.style.lineHeight = '2';
    if (!p.style.color) p.style.color = '#000';
  });
  clone.querySelectorAll('h2').forEach(h2 => {
    if (!h2.style.fontFamily) h2.style.fontFamily = 'SimHei,黑体,sans-serif';
    if (!h2.style.fontSize) h2.style.fontSize = '18px';
    if (!h2.style.fontWeight) h2.style.fontWeight = '800';
    if (!h2.style.margin) h2.style.margin = '18px 0 8px 0';
    if (!h2.style.borderLeft) h2.style.borderLeft = '5px solid #07c160';
    if (!h2.style.paddingLeft) h2.style.paddingLeft = '10px';
    if (!h2.style.color) h2.style.color = '#000';
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

/* 复制 Markdown */
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

/* 清空（无 confirm；如果你想保留确认，可以恢复） */
document.getElementById('btnClear').addEventListener('click', () => {
  quill.setText('');
  localStorage.setItem(KEY_HTML, '');
  localStorage.setItem(KEY_VER, VERSION);
  showToast("已清空");
});

/* Emoji：分组 + 搜索 */
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
    d.title = String(i+1);
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
function closeEmoji() {
  emojiModal.style.display = 'none';
}
function setTab(tab) {
  currentTab = tab;
  emojiTabs.forEach(b => b.classList.toggle('active', b.dataset.tab === tab));
  renderEmojis(tab, emojiSearch.value);
}

document.getElementById('btnEmoji').addEventListener('click', openEmoji);
emojiClose.addEventListener('click', closeEmoji);
emojiModal.addEventListener('click', (e) => {
  if (e.target === emojiModal) closeEmoji();
});
emojiTabs.forEach(btn => {
  btn.addEventListener('click', () => setTab(btn.dataset.tab));
});
emojiSearch.addEventListener('input', () => renderEmojis(currentTab, emojiSearch.value));
setTab('common');
</script>
"""

    # 把占位符替换成真正的 JS 字符串
    html = html.replace("__INIT_JS__", init_js).replace("__VER_JS__", ver_js)
    components.html(html, height=860)
