import json
import streamlit.components.v1 as components

def render_wechat_editor(initial_html: str, version: int):
    init_js = json.dumps(initial_html or "")
    ver_js = json.dumps(str(version))

    # 下面这一整段就是你现在的 components.html(f""" ... """)
    # 直接从你原来的 render_wechat_editor 里复制粘贴到这里
    components.html(f"""
<link href="https://cdn.jsdelivr.net/npm/quill@1.3.7/dist/quill.snow.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/quill@1.3.7/dist/quill.min.js"></script>
<script src="https://unpkg.com/turndown/dist/turndown.js"></script>

<!-- 你原来的 HTML + CSS + JS 全部保持不动 -->
<div>...</div>

<script>
const INITIAL_HTML = {init_js};
const VERSION = {ver_js};
/* 你原来的脚本保持不动 */
</script>
""", height=900, scrolling=True)
