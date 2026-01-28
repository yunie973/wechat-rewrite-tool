# --- 按钮：绿色 + 点击后显示“正在生成中...” ---
# 用 session_state 记录生成状态
if "is_generating" not in st.session_state:
    st.session_state.is_generating = False

btn_text = "正在生成中..." if st.session_state.is_generating else "开始生成"

# 绿色按钮样式（覆盖 Streamlit 默认 primary）
st.markdown("""
<style>
div.stButton > button {
    background-color: #07c160 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 800 !important;
    height: 46px !important;
    width: 100% !important;
}
div.stButton > button:hover {
    background-color: #06b457 !important;
}
div.stButton > button:disabled {
    background-color: #9be4be !important;
    color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)

clicked = st.button(btn_text, disabled=st.session_state.is_generating)

if clicked and not st.session_state.is_generating:
    st.session_state.is_generating = True
    st.rerun()   # 立刻刷新，让按钮马上变“正在生成中...”

# ✅ 当 is_generating=True 时，开始执行生成流程
if st.session_state.is_generating:
    api_key = st.secrets.get("DEEPSEEK_API_KEY")

    if not target_url:
        st.error("请先粘贴链接。")
        st.session_state.is_generating = False
        st.rerun()

    elif not api_key:
        st.error("未检测到 DEEPSEEK_API_KEY，请在 .streamlit/secrets.toml 配置。")
        st.session_state.is_generating = False
        st.rerun()

    else:
        raw_text = get_article_content(target_url)
        if not raw_text:
            st.error("内容抓取失败")
            st.session_state.is_generating = False
            st.rerun()
        else:
            full_content = ""
            placeholder = st.empty()

            response = stream_ai_rewrite(raw_text, api_key)

            for line in response.iter_lines():
                if not line:
                    continue
                chunk = line.decode('utf-8', errors='ignore').removeprefix('data: ').strip()
                if chunk == "[DONE]":
                    break
                try:
                    data = json.loads(chunk)
                    full_content += data["choices"][0]["delta"].get("content", "")
                    placeholder.markdown(safety_filter(full_content) + "▌")
                except:
                    continue

            placeholder.empty()

            md_final = safety_filter(full_content)
            plain_final = to_plain_text(md_final)
            rich_html = build_rich_html(plain_final)

            st.subheader("🖨️ 1) 一键复制：保留字体字号（富文本）")
            render_block_with_copy_rich(
                rich_html=rich_html,
                plain_fallback=plain_final,
                title="富文本成品（小标题黑体18 / 正文宋体17）",
                height_px=520
            )

            st.subheader("🧾 2) 一键复制：Markdown 原文")
            render_block_with_copy_markdown(
                md_text=md_final,
                title="Markdown 原文（原样显示）",
                height_px=520
            )

            # ✅ 生成完成：恢复按钮
            st.session_state.is_generating = False
            st.rerun()
