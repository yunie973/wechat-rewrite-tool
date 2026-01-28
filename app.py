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

    <div style="display:flex;gap:8px;flex-wrap:wrap;">
      <button id="btnApply" style="background:#07c160;color:#fff;border:none;border-radius:10px;padding:10px 14px;cursor:pointer;font-weight:900;">✨ 一键排版</button>
      <button id="btnCopyRich" style="background:#07c160;color:#fff;border:none;border-radius:10px;padding:10px 14px;cursor:pointer;font-weight:900;">📋 复制富文本</button>
      <button id="btnCopyMd" style="background:#07c160;color:#fff;border:none;border-radius:10px;padding:10px 14px;cursor:pointer;font-weight:900;">🧾 复制Markdown</button>
    </div>
  </div>

  <!-- 工具栏（尽量贴近公众号后台） -->
  <div id="toolbar" style="margin-top:12px;border:1px solid rgba(0,0,0,0.08);border-radius:10px;">
    <span class="ql-formats">
      <button class="ql-undo" type="button">↶</button>
      <button class="ql-redo" type="button">↷</button>
    </span>

    <span class="ql-formats">
      <select class="ql-size">
        <option value="small">14px</option>
        <option selected>17px</option>
        <option value="large">18px</option>
        <option value="huge">22px</option>
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

  <!-- 编辑区 -->
  <div id="editor"
       style="margin-top:10px;border:1px solid rgba(0,0,0,0.08);border-radius:12px;">
  </div>

  <div style="margin-top:10px;color:#666;font-size:12px;line-height:1.6;">
    提示：这是免Key版本编辑器。复制“富文本”会保留样式；复制Markdown用于二次处理（不保证公众号完全等效渲染）。
  </div>
</div>

<style>
/* 让内容更像公众号 */
.ql-container {{
  border: none !important;
  font-family: SimSun, 宋体, serif;
}}
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
/* 手机端高度更舒服 */
@media (max-width: 768px) {{
  .ql-editor {{ min-height: 420px; }}
}}
</style>

<script>
const INITIAL_HTML = {init_js};

// Quill 默认 size 只有 small/normal/large/huge，我们映射到像公众号常用的字号
const Size = Quill.import('attributors/style/size');
Size.whitelist = ['14px','17px','18px','22px'];
Quill.register(Size, true);

function mapSize(value) {{
  if (value === 'small') return '14px';
  if (value === 'large') return '18px';
  if (value === 'huge') return '22px';
  return '17px';
}}

const quill = new Quill('#editor', {{
  theme: 'snow',
  modules: {{
    toolbar: '#toolbar',
    history: {{
      delay: 300,
      maxStack: 100,
      userOnly: true
    }}
  }}
}});

// 初始化内容
if (INITIAL_HTML && INITIAL_HTML.trim()) {{
  quill.clipboard.dangerouslyPasteHTML(INITIAL_HTML);
}}

// 自定义 undo/redo
document.querySelector('.ql-undo').addEventListener('click', () => quill.history.undo());
document.querySelector('.ql-redo').addEventListener('click', () => quill.history.redo());

// HR
document.getElementById('btnHr').addEventListener('click', () => {{
  const range = quill.getSelection(true);
  quill.insertEmbed(range.index, 'divider', true);
}});

// Quill 没有 divider embed：用 HTML 方式插入
document.getElementById('btnHr').addEventListener('click', () => {{
  const range = quill.getSelection(true) || {{ index: quill.getLength() }};
  quill.clipboard.dangerouslyPasteHTML(range.index, '<p><hr/></p>');
}});

// 表格（基础：插入一个 2x3 表格 HTML）
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

// 一键排版：宋体17、行距2、段间距、自动把“01.”开头的段落转成 h2 + 左绿条
function applyWechatLayout() {{
  const root = document.querySelector('#editor .ql-editor');
  if (!root) return;

  // 全局
  root.style.fontFamily = 'SimSun,宋体,serif';
  root.style.fontSize = '17px';
  root.style.lineHeight = '2';
  root.style.color = '#000';

  // 段落统一
  root.querySelectorAll('p').forEach(p => {{
    p.style.margin = '0 0 14px 0';
    p.style.fontFamily = 'SimSun,宋体,serif';
    p.style.fontSize = '17px';
    p.style.lineHeight = '2';
  }});

  // 自动识别小标题
  root.querySelectorAll('p').forEach(p => {{
    const t = (p.innerText || '').trim();
    if (/^0[1-4]\\.\\s+/.test(t)) {{
      const h2 = document.createElement('h2');
      h2.innerText = t;
      h2.style.fontFamily = 'SimHei,黑体,sans-serif';
      h2.style.fontSize = '18px';
      h2.style.fontWeight = '800';
      h2.style.margin = '18px 0 8px 0';
      h2.style.borderLeft = '5px solid #07c160';
      h2.style.paddingLeft = '10px';
      p.replaceWith(h2);
    }}
  }});

  alert('已应用公众号排版');
}}

document.getElementById('btnApply').addEventListener('click', applyWechatLayout);

// 复制富文本：把编辑区 HTML 克隆一份并强制补齐 inline style，再写入剪贴板
async function copyRichAll() {{
  const root = document.querySelector('#editor .ql-editor');
  if (!root) return;

  // clone + 强制 inline（防止粘贴丢样式）
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

  const htmlText = root.innerHTML || '';
  let md = '';
  try {{
    const service = new TurndownService({{
      headingStyle: 'atx',
      codeBlockStyle: 'fenced',
      emDelimiter: '*'
    }});
    md = service.turndown(htmlText);
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
""", height=760)
