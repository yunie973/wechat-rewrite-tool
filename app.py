def render_block_with_copy_markdown(md_text: str, title: str, height_px: int = 520):
    """
    Markdown 原文块：内容可滚动，复制按钮固定在容器右上角（不随内容滚动）
    """
    md_esc = html.escape(md_text)
    md_js = json.dumps(md_text)
    title_esc = html.escape(title)

    components.html(f"""
<div style="border:1px solid #07c160;border-radius:10px;background:#fff;padding:14px;">

  <!-- 顶栏：标题 + 右上角按钮（不随内容滚动） -->
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
    <div style="font-weight:800;color:#000;font-family:Microsoft YaHei;">{title_esc}</div>

    <button id="copyBtnMd"
      style="background:#07c160;color:#fff;border:none;border-radius:8px;
             padding:8px 12px;cursor:pointer;font-weight:800;flex-shrink:0;">
      📋 复制
    </button>
  </div>

  <!-- 可滚动内容区 -->
  <div id="scrollAreaMd"
       style="height:{height_px}px; overflow-y:auto; padding-right:6px;">

    <pre style="margin:0;white-space:pre-wrap;line-height:1.8;font-size:14px;
                font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,'Liberation Mono','Courier New',monospace;
                background:#ffffff;border-radius:8px;">{md_esc}</pre>

  </div>
</div>

<script>
async function copyMd(){{
  const text = {md_js};
  try {{
    await navigator.clipboard.writeText(text);
    alert("Markdown 已复制");
  }} catch(e) {{
    const el = document.createElement("textarea");
    el.value = text;
    document.body.appendChild(el);
    el.select();
    document.execCommand("copy");
    document.body.removeChild(el);
    alert("Markdown 已复制");
  }}
}}
document.getElementById("copyBtnMd").addEventListener("click", copyMd);
</script>
""", height=height_px + 110)
