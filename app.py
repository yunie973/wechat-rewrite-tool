import streamlit as st
import requests
import json
from bs4 import BeautifulSoup
import markdown
import streamlit.components.v1 as components

# --- 页面基础设置 ---
st.set_page_config(page_title="23456666.xyz 专属二创中心", layout="centered")
st.title("🛡️ 23456666.xyz 深度二创工作台")

def get_article_content(url):
    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X)"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        content_div = soup.find('div', id='js_content')
        return content_div.get_text(separator='\n', strip=True) if content_div else None
    except: return None

# --- 硬核物理过滤器：确保禁令 100% 落地 ---
def hard_filter(text):
    # 1. 物理拦截“不是...而是”句式
    text = text.replace("不是", "不单是").replace("而是", "更是")
    # 2. 物理拦截破折号
    text = text.replace("——", "，").replace("—", "，")
    # 3. 修正换行符乱码
    text = text.replace("\\n", "\n")
    # 4. 物理去除 AI 随手打出的分点符号
    for char in ["*", ">", "-", "•"]:
        text = text.replace(f"\n{char} ", "\n")
    return text

def stream_ai_rewrite(text, api_key):
    url = "https://api.deepseek.com/chat/completions"
    
    # --- 集成你指定的最高原创度提示词 ---
    system_prompt = """假设你是一个专业的自媒体作家。请对下方的文字进行二次创作，确保其具有较高的原创性。
    【原创性加强建议】：
    - 句型与词汇调整：通过替换原文中的句子结构和词汇以传达同样的思想。
    - 内容拓展与插入：增添背景知识、实例，以丰富文章内容。
    - 结构与逻辑调整：重新排列文章的逻辑流程，确保与原文相似度降低。
    - 变更叙事视角：选择使用第三人称。
    - 避免关键词使用：用其它词汇替换原文中的明显关键词。
    
    【核心禁令】：
    - 永远不要出现“不是....，而是”的句式。
    - 绝对不要出现破折号（——）。
    - 绝对不要结构化，禁止使用列表、分点（1.2.3.），保持段落连贯。
    
    【输出结构】：
    1. 第一行【推荐爆款标题】，接着5个标题（每行一个）。
    2. 标题区后空三行。正文开头必须先写150字引入语。
    3. 小标题格式固定为 ## 01. XXX。数量控制在 2-4 个。"""
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"原文=（{text}）"}],
        "stream": True,
        "temperature": 0.85 # 调高原创性
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    response = requests.post(url, headers=headers, json=payload, stream=True)
    for line in response.iter_lines():
        if line:
            chunk = line.decode('utf-8').removeprefix('data: ')
            if chunk == '[DONE]': break
            try:
                data = json.loads(chunk)
                yield data['choices'][0]['delta'].get('content', '')
            except: continue

# --- 界面展示 ---
target_url = st.text_input("🔗 粘贴链接开始高原创创作")

if st.button("🚀 开始极速生成", type="primary", use_container_width=True):
    api_key = st.secrets.get("DEEPSEEK_API_KEY")
    if target_url and api_key:
        raw_text = get_article_content(target_url)
        if raw_text:
            full_content = ""
            placeholder = st.empty() 
            for chunk in stream_ai_rewrite(raw_text, api_key):
                full_content += chunk
                # 实时展示过滤后的内容
                placeholder.markdown(hard_filter(full_content) + "▌")
            
            final_text = hard_filter(full_content)
            placeholder.markdown(final_text)
            
            # --- 精准排版区：18号黑体/17号宋体 ---
            html_main = markdown.markdown(final_text)
            styled_output = f"""
            <div id="copy-area" style="padding: 20px; background: #fff; line-height: 1.8; text-align: justify;">
                <style>
                    /* 17号宋体正文 */
                    .rich-content {{ font-family: "SimSun", "STSong", serif; font-size: 17px; color: #333; }}
                    /* 18号黑体加粗标题 */
                    h2 {{ 
                        font-size: 18px !important; 
                        font-family: "SimHei", "Microsoft YaHei", sans-serif !important; 
                        font-weight: bold !important; 
                        color: #000 !important; 
                        margin: 25px 0 10px 0; 
                    }}
                    p {{ font-size: 17px; margin-bottom: 15px; }}
                </style>
                <div class="rich-content">{html_main}</div>
            </div>
            """
            st.subheader("🟢 最终预览（带18/17号格式）")
            st.markdown(styled_output, unsafe_allow_html=True)
            
            # 手机端一键复制按钮
            copy_js = f"""
            <div style="text-align:center; margin-top:20px;">
                <button id="c-btn" style="background:#07c160; color:white; border:none; padding:15px 30px; font-size:18px; border-radius:8px; width:100%;">📋 一键复制成品 (保留格式)</button>
            </div>
            <script>
            document.getElementById('c-btn').onclick = function() {{
                const area = parent.document.getElementById('copy-area');
                const range = document.createRange();
                range.selectNode(area);
                const sel = window.getSelection();
                sel.removeAllRanges(); sel.addRange(range);
                document.execCommand('copy');
                this.innerText = '✅ 复制成功';
                sel.removeAllRanges();
            }};
            </script>
            """
            components.html(copy_js, height=100)
        else: st.error("内容抓取失败")
