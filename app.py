import streamlit as st
import requests
import json
from bs4 import BeautifulSoup
import markdown
import streamlit.components.v1 as components

# --- 页面设置 ---
st.set_page_config(page_title="二创精修版", layout="centered")
st.title("✍️ 深度二创专业工作台")

def get_article_content(url):
    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X)"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        content_div = soup.find('div', id='js_content')
        return content_div.get_text(separator='\n', strip=True) if content_div else None
    except: return None

def stream_ai_rewrite(text, api_key):
    url = "https://api.deepseek.com/chat/completions"
    # 强制指令：标题双换行，正文小标题 2-4 个
    system_prompt = """你是一个专业的公众号改写专家。
    【绝对禁令】：严禁输出“导语、主体、结语、总结、前言”等词汇。严禁任何开场白。
    【结构规范】：
    1. 第一行写：【推荐爆款标题】
    2. 接下来输出 5 个爆款标题，每个标题后面必须跟两个换行符(\\n\\n)，确保标题之间有明显的空行。
    3. 标题区结束后空三行。正文开头必须先写一段100字引入语，严禁直接使用小标题。
    4. 正文小标题格式：## 01. [标题内容]（以此类推）。
    5. **数量限制**：正文小标题总数必须控制在 2 到 4 个之间。"""
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"原文=({text})"}],
        "stream": True,
        "temperature": 0.7
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

# --- 界面 ---
target_url = st.text_input("🔗 粘贴微信链接并开始")

if st.button("🚀 开始极速生成", type="primary", use_container_width=True):
    api_key = st.secrets.get("DEEPSEEK_API_KEY")
    if target_url and api_key:
        raw_text = get_article_content(target_url)
        if raw_text:
            full_content = ""
            placeholder = st.empty() 
            for chunk in stream_ai_rewrite(raw_text, api_key):
                full_content += chunk
                placeholder.markdown(full_content + "▌")
            placeholder.markdown(full_content)
            
            # --- 核心排版逻辑 ---
            # 标题部分：18px 黑体
            # 正文小标题：18px 黑体加粗
            # 正文：17px 宋体
            html_content = markdown.markdown(full_content)
            
            styled_output = f"""
            <div id="copy-area" style="padding: 20px; background: #fff; color: #333; line-height: 1.8; text-align: justify;">
                <style>
                    /* 针对 AI 输出的爆款标题列表 */
                    .rich-content {{ font-family: "SimSun", "STSong", serif; font-size: 17px; }}
                    
                    /* 小标题：18号 黑体 加粗 */
                    h2 {{ 
                        font-size: 18px; 
                        font-family: "SimHei", "Microsoft YaHei", sans-serif; 
                        font-weight: bold; 
                        color: #000; 
                        margin-top: 30px; 
                        margin-bottom: 15px;
                    }}
                    
                    /* 正文段落：17号 宋体 */
                    p {{ 
                        font-size: 17px; 
                        font-family: "SimSun", "STSong", serif; 
                        margin-bottom: 15px; 
                    }}

                    /* 针对开头推荐标题的样式模拟 */
                    .title-box {{ font-weight: bold; font-family: "SimHei"; font-size: 18px; margin-bottom: 20px; }}
                </style>
                <div class="rich-content">
                    {html_content}
                </div>
            </div>
            """
            
            st.subheader("🟢 排版预览（长按此区域全选复制）")
            st.markdown(styled_output, unsafe_allow_html=True)
            
            # 一键复制按钮
            copy_button_js = f"""
            <div style="text-align:center; margin-top:20px;">
                <button id="copy-btn" style="
                    background-color: #07c160; color: white; border: none; 
                    padding: 15px 30px; font-size: 18px; border-radius: 8px; 
                    width: 100%; cursor: pointer;
                ">📋 一键复制成品 </button>
            </div>
            <script>
            document.getElementById('copy-btn').onclick = function() {{
                const area = parent.document.getElementById('copy-area');
                const range = document.createRange();
                range.selectNode(area);
                const selection = window.getSelection();
                selection.removeAllRanges();
                selection.addRange(range);
                try {{
                    document.execCommand('copy');
                    this.innerText = '✅ 复制成功，去公众号粘贴吧';
                    this.style.backgroundColor = '#059653';
                }} catch (err) {{ alert('请尝试手动长按预览区进行复制'); }}
                selection.removeAllRanges();
            }};
            </script>
            """
            components.html(copy_button_js, height=100)
            
            with st.expander("查看原始数据"):
                st.code(full_content, language="markdown")
        else: st.error("内容抓取失败")
