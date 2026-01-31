import json
import time
import streamlit as st
import streamlit.components.v1 as components

from ui_shell import inject_shell
from text_utils import safety_filter, to_plain_text, build_rich_html
from fetch_wechat import get_article_text_smart
from deepseek_stream import stream_ai_rewrite
from editor_quill import render_wechat_editor


# =============================
# Page
# =============================
st.set_page_config(page_title="高级原创二创助手", layout="centered")

# ✅ 只注入一次：样式 + footer + 自动留白
inject_shell()

st.title("🛡️ 深度重构级专业工作台")

# =============================
# session_state
# =============================
def ss_init(k, v):
    if k not in st.session_state:
        st.session_state[k] = v

ss_init("is_generating", False)
ss_init("manual_text", "")
ss_init("last_source_text", None)
ss_init("last_error", None)

ss_init("result_md", "")
ss_init("result_plain", "")
ss_init("result_rich_html", "")

ss_init("editor_initial_html", "")
ss_init("editor_version", 0)
ss_init("jump_to_editor", False)


# =============================
# 自动跳到 tab
# =============================
def jump_to_tab_by_text(tab_text: str):
    safe_text = json.dumps(tab_text)
    components.html(f"""
<script>
(function(){{
  const target = {safe_text};
  const tabs = parent.document.querySelectorAll('button[data-baseweb="tab"]');
  for (const b of tabs) {{
    const t = (b.innerText || '').trim();
    if (t.includes(target)) {{ b.click(); break; }}
  }}
}})();
</script>
""", height=0)


# =============================
# UI Tabs
# =============================
tab_gen, tab_manual = st.tabs(["🚀 二创生成", "📝 手动排版"])

with tab_gen:
    target_url = st.text_input("🔗 粘贴链接开始深度重构")

    with st.expander("高级设置（可选）", expanded=False):
        st.markdown("**风格强度（temperature）**")
        st.caption("越低越稳；越高越创意（更敢改但更易跑题）")
        temperature = st.slider("风格强度（建议 0.70–0.85）", 0.5, 1.0, 0.8, 0.05)

        st.markdown("---")
        target_words = st.number_input(
            "目标字数（默认1000，可点击输入）",
            min_value=200,
            value=1000,
            step=100,
            key="target_words"
        )
        st.caption("建议 800–2000；可随意输入。模型会尽量贴近目标字数（允许少量浮动）。")

    with st.expander("抓取失败？这里可手动粘贴原文继续生成（可选）", expanded=False):
        st.session_state.manual_text = st.text_area(
            "📄 粘贴原文（抓不到链接时会用这里的内容）",
            value=st.session_state.manual_text,
            height=180,
            placeholder="当公众号链接抓取失败时，把文章原文粘贴到这里再点“开始生成”。"
        )

    if st.session_state.last_error and not st.session_state.is_generating:
        st.error(st.session_state.last_error)

    btn_text = "正在生成中..." if st.session_state.is_generating else "开始生成"
    clicked = st.button(btn_text, disabled=st.session_state.is_generating, key="gen_btn")

    if clicked and not st.session_state.is_generating:
        st.session_state.is_generating = True
        st.session_state.last_error = None
        st.rerun()

    if st.session_state.is_generating:
        st.info("正在生成中，请稍候…")
        live_placeholder = st.empty()

        try:
            api_key = st.secrets.get("DEEPSEEK_API_KEY")
            if not api_key:
                st.session_state.last_error = "未检测到 DEEPSEEK_API_KEY，请在 .streamlit/secrets.toml 配置。"
                st.session_state.is_generating = False
                st.rerun()

            source_text = None
            if target_url.strip():
                with st.spinner("正在抓取文章内容…"):
                    text, hint = get_article_text_smart(target_url.strip())
                if text:
                    source_text = text
                else:
                    manual = (st.session_state.manual_text or "").strip()
                    if manual:
                        source_text = manual
                    else:
                        st.session_state.last_error = f"内容抓取失败：{hint}。你可以展开“手动粘贴原文”后再生成。"
                        st.session_state.is_generating = False
                        st.rerun()
            else:
                manual = (st.session_state.manual_text or "").strip()
                if manual:
                    source_text = manual
                else:
                    st.session_state.last_error = "请粘贴链接，或展开“手动粘贴原文”输入内容后再生成。"
                    st.session_state.is_generating = False
                    st.rerun()

            st.session_state.last_source_text = source_text

            full_content = ""
            response = stream_ai_rewrite(
                text=source_text,
                api_key=api_key,
                temperature=temperature,
                target_words=int(target_words)
            )

            if response.status_code != 200:
                msg = response.text[:400] if response.text else ""
                st.session_state.last_error = f"模型接口请求失败：HTTP {response.status_code}\n\n{msg}"
                st.session_state.is_generating = False
                st.rerun()

            last_render_len = 0
            last_tick = time.time()

            for line in response.iter_lines():
                if not line:
                    continue
                chunk = line.decode("utf-8", errors="ignore").removeprefix("data: ").strip()
                if chunk == "[DONE]":
                    break
                try:
                    data = json.loads(chunk)
                    delta = data["choices"][0]["delta"].get("content", "")
                    if not delta:
                        continue
                    full_content += delta

                    now = time.time()
                    if (len(full_content) - last_render_len >= 120) or (now - last_tick >= 0.35):
                        last_render_len = len(full_content)
                        last_tick = now
                        live_placeholder.markdown(safety_filter(full_content) + "▌")
                except:
                    continue

            live_placeholder.empty()

            md_final = safety_filter(full_content)
            plain_final = to_plain_text(md_final)
            rich_html_out = build_rich_html(plain_final)

            st.session_state.result_md = md_final
            st.session_state.result_plain = plain_final
            st.session_state.result_rich_html = rich_html_out

            st.session_state.editor_initial_html = rich_html_out
            st.session_state.editor_version += 1
            st.session_state.jump_to_editor = True

            st.session_state.is_generating = False
            st.session_state.last_error = None
            st.rerun()

        except Exception as e:
            st.session_state.last_error = f"发生错误：{e}"
            st.session_state.is_generating = False
            st.rerun()

    if (not st.session_state.is_generating) and st.session_state.editor_initial_html:
        st.success("✅ 已生成完成，并已自动导入到「手动排版」编辑器。")

with tab_manual:
    st.subheader("🧩 手动排版（工具栏 + 一键排版 + 一键复制）")
    render_wechat_editor(st.session_state.editor_initial_html, st.session_state.editor_version)

if st.session_state.jump_to_editor:
    st.session_state.jump_to_editor = False
    jump_to_tab_by_text("手动排版")
