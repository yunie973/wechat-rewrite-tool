import streamlit as st
import streamlit.components.v1 as components
import requests
import json
from bs4 import BeautifulSoup
import re
import html

st.set_page_config(page_title="深度重构级专业工作台", layout="centered")

# ---------- 全局样式 ----------
st.markdown("""
<style>
:root, body, .stApp { color-scheme: light !important; }
.stApp { background:#ffffff !important; color:#000000 !important; padding-bottom: 90px; }

h1 { color:#07c160 !important; font-family:"Microsoft YaHei"; text-align:center; font-weight:900; }

.stTextInput > div > div {
  border: 2px solid #07c160 !important;
  border-radius: 12px !important;
  background: #ffffff !important;
}
.stTextInput input { background:#fff !important; color:#000 !important; font-weight:700 !important; }

/* tabs 始终可见 */
.stTabs [data-baseweb="tab"] { font-size: 16px !important; font-weight: 900 !important; color:#111 !important; opacity:1 !important; }
.stTabs [aria-selected="true"] { color:#07c160 !important; }
.stTabs [data-baseweb="tab-border"] { background: rgba(7,193,96,0.25) !important; }

/* 绿色按钮 */
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


# ---------- 工具函数 ----------
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
1. 第一行写【推荐爆款标题】，接着输出5个爆款标题，每行一个（标题标点不要删）。
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
    if not text:
        return ""
    text = text.replace("\\n", "\n")
    # 仅规避“不是..而是”句式，不动标点
    text = re.sub(r"不是(.{0,40})而是", r"不单是\1更是", text)
    text = re.sub(r"(【推荐爆款标题】)\s*", r"【推荐爆款标题】\n", text)
    text = re.sub(r"(\n?)(##\s*0[1-4]\.)", r"\n\n\2", text)
    return text.strip()


def plain_to_rich_html(plain: str) -> str:
    if not plain:
        return ""
    lines = plain.splitlines()
    out = []
    for ln in lines:
        s = ln.strip()
        if not s:
            out.append("<p><br></p>")
            continue
        if s.startswith("##"):
            title = html.escape(s.replace("##", "", 1).strip())
            out.append(
                "<p><span style='font-family:SimHei, \"Microsoft YaHei\", sans-serif; "
                "font-size:18px; font-weight:700;'>%s</span></p>" % title
            )
        else:
            out.append(
                "<p><span style='font-family:SimSun, serif; font-size:17px;'>%s</span></p>"
                % html.escape(s)
            )
    return "\n".join(out)


# ---------- Session State ----------
if "pending_generate" not in st.session_state:
    st.session_state.pending_generate = False
if "pending_payload" not in st.session_state:
    st.session_state.pending_payload = {}
if "is_generating" not in st.session_state:
    st.session_state.is_generating = False
if "last_plain" not in st.session_state:
    st.session_state.last_plain = ""
if "last_rich_html" not in st.session_state:
    st.session_state.last_rich_html = ""


# ---------- 编辑器组件（Quill）----------
def render_wechat_editor(initial_html: str):
    safe_initial_json = json.dumps(initial_html or "")

    component_html = """
<!doctype html><html><head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />

<style>
body{margin:0;background:#fff;}
.wrap{border:2px solid #07c160;border-radius:14px;padding:14px;background:#fff;font-family:"Microsoft YaHei",sans-serif;}
.header{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:10px;}
.title{font-size:18px;font-weight:900;color:#111;}
.actions{display:flex;gap:10px;flex-wrap:wrap;justify-content:flex-end;}
.btn{border:none;border-radius:10px;padding:10px 14px;font-weight:900;cursor:pointer;font-size:14px;}
.btn-green{background:#07c160;color:#fff;}
.btn-green:hover{background:#06b457;}
.btn-ghost{background:#f3f5f7;color:#111;border:1px solid rgba(0,0,0,0.12);}

.toolbarRow{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin:10px 0;}
.field{display:flex;align-items:center;gap:6px;padding:6px 10px;border:1px solid rgba(0,0,0,0.12);border-radius:10px;background:#fff;}
.field label{font-size:12px;font-weight:900;color:#333;white-space:nowrap;}
.field select,.field input{border:none;outline:none;font-size:14px;font-weight:900;background:transparent;}
.field input{width:70px;}

#editorShell{border:1px solid rgba(0,0,0,0.12);border-radius:12px;overflow:hidden;background:#fff;}
#toolbar{background:#fff;position:sticky;top:0;z-index:5;border-bottom:1px solid rgba(0,0,0,0.10);}
.toast{position:fixed;right:16px;top:16px;background:rgba(17,17,17,0.92);color:#fff;padding:10px 12px;border-radius:10px;font-size:13px;font-weight:900;opacity:0;transform:translateY(-6px);transition:all .2s ease;z-index:9999;pointer-events:none;}
.toast.show{opacity:1;transform:translateY(0);}

/* 关键：保证编辑区一定有高度，不会塌陷 */
.ql-container{min-height:420px;}
.ql-editor{min-height:420px;line-height:2;padding:18px 16px;overflow-y:auto;}
</style>
</head>
<body>
<div class="toast" id="toast">完成</div>

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

    <div style="font-size:12px;color:#666;font-weight:900;">
      提示：编辑区可滚动；工具栏/复制按钮固定在顶部。
    </div>
  </div>

  <div id="editorShell">
    <div id="toolbar"></div>
    <div id="editor"></div>
  </div>

  <div style="margin-top:10px;color:#666;font-size:12px;font-weight:900;">
    复制富文本用于直接粘贴公众号；复制Markdown用于你二次处理（公众号内不保证完全等效渲染）。
  </div>
</div>

<script>
  // 多 CDN 兜底加载（防止国内网络导致编辑器不出来）
  function loadCSS(url){
    return new Promise((res, rej)=>{
      const l=document.createElement('link');
      l.rel='stylesheet'; l.href=url;
      l.onload=()=>res(url); l.onerror=()=>rej(url);
      document.head.appendChild(l);
    });
  }
  function loadJS(url){
    return new Promise((res, rej)=>{
      const s=document.createElement('script');
      s.src=url; s.onload=()=>res(url); s.onerror=()=>rej(url);
      document.head.appendChild(s);
    });
  }

  const CSS_LIST = [
    "https://cdn.jsdelivr.net/npm/quill@1.3.7/dist/quill.snow.css",
    "https://unpkg.com/quill@1.3.7/dist/quill.snow.css",
    "https://cdn.staticfile.org/quill/1.3.7/quill.snow.min.css"
  ];

  const JS_LIST = [
    "https://cdn.jsdelivr.net/npm/quill@1.3.7/dist/quill.min.js",
    "https://unpkg.com/quill@1.3.7/dist/quill.min.js",
    "https://cdn.staticfile.org/quill/1.3.7/quill.min.js"
  ];

  const TURNDOWN_LIST = [
    "https://cdn.jsdelivr.net/npm/turndown@7.1.2/dist/turndown.js",
    "https://unpkg.com/turndown@7.1.2/dist/turndown.js",
    "https://cdn.staticfile.org/turndown/7.1.2/turndown.min.js"
  ];

  const INITIAL_HTML = __INITIAL_HTML__;

  function showToast(msg){
    const t=document.getElementById('toast');
    t.textContent = msg || "完成";
    t.classList.add('show');
    setTimeout(()=>t.classList.remove('show'), 900);
  }

  async function tryLoad(list, loader){
    let lastErr = null;
    for(const u of list){
      try{ await loader(u); return u; }catch(e){ lastErr=e; }
    }
    throw lastErr;
  }

  function computeEditorHeight(){
    const w = window.innerWidth || 1024;
    const vh = window.innerHeight || 800;
    let h = Math.round(vh * 0.55);
    if (w <= 768) h = Math.max(360, Math.min(420, h));
    else h = Math.max(520, Math.min(640, h));
    return h;
  }

  function applyEditorHeight(){
    const h = computeEditorHeight();
    const container = document.querySelector('.ql-container');
    const editor = document.querySelector('.ql-editor');
    if(container) container.style.height = h + 'px';
    if(editor) editor.style.height = h + 'px';
  }

  function escapeHtml(s){
    return String(s)
      .replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;")
      .replaceAll('"',"&quot;").replaceAll("'","&#039;");
  }

  async function init(){
    try{
      await tryLoad([CSS_LIST[0]], loadCSS).catch(()=>{});
      // CSS 兜底
      for (let i=1;i<CSS_LIST.length;i++){
        loadCSS(CSS_LIST[i]).catch(()=>{});
      }

      await tryLoad(JS_LIST, loadJS);
      await tryLoad(TURNDOWN_LIST, loadJS);

      // toolbar（不带表格，保留 emoji/列表/引用等）
      document.getElementById('toolbar').innerHTML = `
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
        <span class="ql-formats">
          <button class="ql-clean"></button>
        </span>
      `;

      const Font = Quill.import('formats/font');
      Font.whitelist = [
        'wechat','simsun','simhei','yahei','pingfang','kaiti','fangsong',
        'arial','times','georgia','courier','verdana','tahoma','impact','comic'
      ];
      Quill.register(Font, true);

      const quill = new Quill('#editor', {
        theme: 'snow',
        modules: { toolbar: '#toolbar', history: { delay: 500, maxStack: 200, userOnly: true } }
      });

      // 初始化后再算高度（避免 0 高度）
      setTimeout(()=>{
        applyEditorHeight();
        window.addEventListener('resize', applyEditorHeight);
      }, 50);

      // 填入初始内容
      if (INITIAL_HTML && INITIAL_HTML.trim().length > 0){
        quill.clipboard.dangerouslyPasteHTML(INITIAL_HTML);
      }else{
        quill.clipboard.dangerouslyPasteHTML("<p><span style='font-family:SimSun,serif;font-size:17px;'>在这里开始编辑…</span></p>");
      }

      // 外部控件（方案A：只有字号输入框）
      const fontSelect = document.getElementById('fontSelect');
      const sizeInput = document.getElementById('sizeInput');

      function applyFont(v){ quill.format('font', v); }
      function applySize(px){
        const n = parseInt(String(px).replace('px',''), 10);
        if (isNaN(n)) return;
        const clamped = Math.min(50, Math.max(10, n));
        quill.format('size', clamped + 'px');
        sizeInput.value = clamped;
      }

      fontSelect.addEventListener('change', ()=>applyFont(fontSelect.value));
      sizeInput.addEventListener('input', ()=>applySize(sizeInput.value));
      sizeInput.addEventListener('change', ()=>applySize(sizeInput.value));
      sizeInput.addEventListener('keydown', (e)=>{ if(e.key==='Enter') applySize(sizeInput.value); });

      // 默认：宋体 17
      applyFont('simsun');
      applySize(17);

      function oneKeyFormat(){
        const ps = quill.root.querySelectorAll('p');
        ps.forEach(p=>{
          const txt=(p.innerText||'').trim();
          if(!txt){ p.innerHTML="<br>"; return; }
          if(txt.startsWith("##") || /^[0-9]{2}[\\.、]/.test(txt)){
            const t = txt.replace(/^##\\s*/, '');
            p.innerHTML = "<span style='font-family:SimHei, \"Microsoft YaHei\", sans-serif; font-size:18px; font-weight:700;'>" + escapeHtml(t) + "</span>";
          }else{
            const hasSpan = p.querySelector('span');
            if(!hasSpan){
              p.innerHTML = "<span style='font-family:SimSun, serif; font-size:17px;'>" + escapeHtml(txt) + "</span>";
            }
          }
        });
      }

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
            const temp=document.createElement('div');
            temp.style.position='fixed'; temp.style.left='-9999px';
            temp.innerHTML = htmlStr; document.body.appendChild(temp);
            const range=document.createRange(); range.selectNodeContents(temp);
            const sel=window.getSelection(); sel.removeAllRanges(); sel.addRange(range);
            document.execCommand('copy'); sel.removeAllRanges(); document.body.removeChild(temp);
          }
          showToast("已复制富文本");
        }catch(e){
          showToast("复制失败");
        }
      }

      function copyMarkdown(){
        const htmlStr = quill.root.innerHTML;
        const turndown = new TurndownService({ headingStyle:'atx', codeBlockStyle:'fenced' });
        let md = turndown.turndown(htmlStr);
        md = md.replace(/\\n{3,}/g, "\\n\\n").trim();
        if(navigator.clipboard){
          navigator.clipboard.writeText(md).then(()=>showToast("已复制Markdown"));
        }else{
          const ta=document.createElement('textarea'); ta.value=md;
          document.body.appendChild(ta); ta.select(); document.execCommand('copy'); document.body.removeChild(ta);
          showToast("已复制Markdown");
        }
      }

      function clearEditor(){ quill.setText(''); showToast("已清空"); }

      document.getElementById('btnFormat').onclick = ()=>{ oneKeyFormat(); showToast("已应用排版"); };
      document.getElementById('btnCopyRich').onclick = copyRich;
      document.getElementById('btnCopyMd').onclick = copyMarkdown;
      document.getElementById('btnClear').onclick = clearEditor;

    }catch(e){
      document.body.innerHTML = "<div style='padding:16px;font-family:Microsoft YaHei;font-weight:900;color:#b00020'>编辑器资源加载失败（可能网络限制/CDN不可达）。建议开代理或换可访问 CDN。</div>";
    }
  }

  init();
</script>
</body></html>
""".replace("__INITIAL_HTML__", safe_initial_json)

    components.html(component_html, height=780, scrolling=True)


# ---------- Tabs ----------
tab_gen, tab_edit = st.tabs(["🚀 二创生成", "🧩 手动排版"])


# ==========================
# A) 二创生成页（两段式 rerun，按钮必变）
# ==========================
with tab_gen:
    st.subheader("🔗 粘贴公众号链接开始生成")
    url = st.text_input("链接", placeholder="https://mp.weixin.qq.com/s/xxxxx")

    with st.expander("高级设置（可选）", expanded=False):
        temperature = st.slider("风格强度（temperature）", 0.2, 1.2, 0.8, 0.01)

    # 关键：按钮文案由状态控制
    btn_label = "正在生成中…" if st.session_state.is_generating else "开始生成"
    clicked = st.button(btn_label, disabled=st.session_state.is_generating)

    # 第一步：只写状态 + rerun，让按钮立刻变化
    if clicked and not st.session_state.is_generating:
        st.session_state.pending_generate = True
        st.session_state.pending_payload = {"url": url, "temperature": float(temperature)}
        st.session_state.is_generating = True
        st.rerun()

    # 第二步：在“状态已变”的 rerun 中真正开始生成
    if st.session_state.pending_generate and st.session_state.is_generating:
        api_key = st.secrets.get("DEEPSEEK_API_KEY")
        payload = st.session_state.pending_payload or {}
        target_url = payload.get("url", "")
        temp = payload.get("temperature", 0.8)

        if not api_key:
            st.error("未配置 DEEPSEEK_API_KEY")
            st.session_state.pending_generate = False
            st.session_state.is_generating = False
        elif not target_url:
            st.error("请先粘贴链接")
            st.session_state.pending_generate = False
            st.session_state.is_generating = False
        else:
            with st.spinner("正在生成中…"):
                raw = get_article_content(target_url)
                if not raw:
                    st.error("内容抓取失败（可能链接不可访问或反爬）")
                else:
                    full = ""
                    try:
                        resp = stream_ai_rewrite(raw[:8000], api_key, temperature=temp)
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
                            except:
                                continue
                    except Exception as e:
                        st.error(f"生成失败：{e}")

                    final_plain = normalize_text(full)
                    st.session_state.last_plain = final_plain
                    st.session_state.last_rich_html = plain_to_rich_html(final_plain)
                    st.success("✅ 已生成完成，并已自动同步到「手动排版」编辑器里（去手动排版页即可编辑/复制）。")

        # 收尾：恢复初始状态
        st.session_state.pending_generate = False
        st.session_state.is_generating = False
        st.session_state.pending_payload = {}


# ==========================
# B) 手动排版页（内容自动进编辑器）
# ==========================
with tab_edit:
    st.subheader("🧩 手动排版（可滚动可编辑 + 一键复制）")
    render_wechat_editor(st.session_state.last_rich_html)
