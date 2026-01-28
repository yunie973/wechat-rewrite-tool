def render_block_with_copy_rich(rich_html: str, plain_fallback: str, title: str, height_px: int = 520):
    """
    富文本块：内容可滚动，复制按钮固定在容器右上角（不跟内容滚动）
    """
    rich_js = json.dumps(rich_html)
    plain_js = json.dumps(plain_fallback)
    title_esc = html.escape(title)

    components.html(f"""
<div style="border:1px solid #07c160;border-radius:10px;background:#fff;padding:14px;">

  <!-- 顶栏：标题 + 右上角按钮（不随内容滚动） -->
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
    <div style="font-weight:800;color:#000;font-family:Microsoft YaHei;">{title_esc}</div>

    <button id="copyBtn"
      style="background:#07c160;color:#fff;border:none;border-radius:8px;
             padding:8px 12px;cursor:pointer;font-weight:800;flex-shrink:0;">
      📋 复制
    </button>
  </div>

  <!-- 可滚动内容区 -->
  <div id="scrollArea"
       style="height:{height_px}px; overflow-y:auto; padding-right:6px;">

    {rich_html}

  </div>
</div>

<script>
async function copyRich(){{
  const htmlText = {rich_js};
  const plainText = {plain_js};

  try {{
    if (navigator.clipboard && window.ClipboardItem) {{
      const htmlBlob = new Blob([htmlText], {{ type: "text/html" }});
      const textBlob = new Blob([plainText], {{ type: "text/plain" }});
      const item = new ClipboardItem({{
        "text/html": htmlBlob,
        "text/plain": textBlob
      }});
      await navigator.clipboard.write([item]);
      alert("已复制（保留字体字号）");
      return;
    }}
  }} catch(e) {{}}

  // fallback：execCommand（可能复制富文本）
  try {{
    const temp = document.createElement("div");
    temp.setAttribute("contenteditable", "true");
    temp.style.position = "fixed";
    temp.style.left = "-9999px";
    temp.innerHTML = htmlText;
    document.body.appendChild(temp);

    const range = document.createRange();
    range.selectNodeContents(temp);
    const sel = window.getSelection();
    sel.removeAllRanges();
    sel.addRange(range);

    document.execCommand("copy");
    sel.removeAllRanges();
    document.body.removeChild(temp);
    alert("已复制（保留字体字号）");
    return;
  }} catch(e) {{}}

  // 最后兜底：纯文本
  try {{
    await navigator.clipboard.writeText(plainText);
    alert("已复制（降级为纯文本）");
  }} catch(e) {{
    alert("复制失败：请使用 HTTPS 或更换浏览器");
  }}
}}

document.getElementById("copyBtn").addEventListener("click", copyRich);
</script>
""", height=height_px + 110)
