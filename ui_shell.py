import streamlit as st

def inject_shell():
    st.markdown(r"""
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

/* Expander */
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
div[data-testid="stExpander"] summary:hover{ background: rgba(7,193,96,0.10) !important; }
div[data-testid="stExpander"] details > div{ background:#fff !important; padding: 14px !important; }

/* NumberInput */
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
div[data-testid="stNumberInput"] button:hover{ background:#06b457 !important; }
div[data-testid="stNumberInput"] button + button{
  border-left: 1px solid rgba(255,255,255,0.25) !important;
}

/* 字体渲染 */
html, body, .stApp, * {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
}

/* ========= 关键：给 fixed footer 自动留白 ========= */
:root{ --footerH: 0px; }

.footer{
  position:fixed; left:0; right:0; bottom:0;
  background:#fff; padding:12px 0; border-top:2px solid #07c160;
  z-index:999; display:flex; justify-content:center; align-items:center; gap:20px;
}

/* ✅ 核心：内容区底部留白 = footer真实高度 + 额外空隙 */
div[data-testid="stAppViewContainer"] .main .block-container{
  padding-bottom: calc(var(--footerH) + 40px + env(safe-area-inset-bottom)) !important;
}
/* 兼容一些老结构 */
section.main .block-container{
  padding-bottom: calc(var(--footerH) + 40px + env(safe-area-inset-bottom)) !important;
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

  function setFooterSpace(){
    const footer = document.querySelector('.footer');
    if(!footer) return;
    const h = Math.ceil(footer.getBoundingClientRect().height || 0);
    document.documentElement.style.setProperty('--footerH', h + 'px');
  }

  function init(){
    bindWheelBlur();
    setFooterSpace();
    setTimeout(setFooterSpace, 200);
    window.addEventListener('resize', setFooterSpace);

    try {
      const footer = document.querySelector('.footer');
      if (footer && window.ResizeObserver) {
        const ro = new ResizeObserver(setFooterSpace);
        ro.observe(footer);
      }
    } catch(e) {}
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
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
