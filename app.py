import streamlit as st
import requests
import json

st.set_page_config(page_title="爆款二创-流式版", layout="centered")
st.title("⚡ 极速二创工作台")

def get_article_text(url):
    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X)"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(res.text, 'html.parser')
        content = soup.find('div', id='js_content')
        return content.get_text(separator='\n', strip=True) if content else None
    except:
        return None

def stream_ai_rewrite(text, api_key):
    """流式生成器函数"""
    url = "https://api.deepseek.com/chat/completions"
    prompt = f"假设你是一个专业的自媒体作家...（此处补全你之前的专业提示词）...原文=（{text}）"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "stream": True  # 开启流式传输
    }

    response = requests.post(url, headers=headers, json=payload, stream=True)
    
    # 解析流式数据块
    for line in response.iter_lines():
        if line:
            chunk = line.decode('utf-8').removeprefix('data: ')
            if chunk == '[DONE]': break
            try:
                data = json.loads(chunk)
                delta = data['choices'][0]['delta'].get('content', '')
                yield delta
            except:
                continue

target_url = st.text_input("粘贴微信文章链接")

if st.button("✨ 立即生成 (流式预览)", type="primary"):
    api_key = st.secrets.get("DEEPSEEK_API_KEY")
    if not api_key:
        st.error("请先配置 API Key")
    elif target_url:
        raw_text = get_article_text(target_url)
        if raw_text:
            st.subheader("🔥 创作进行中...")
            # 使用 Streamlit 的流式显示容器
            placeholder = st.empty()
            full_content = ""
            
            # 实时更新文字到页面
            for chunk in stream_ai_rewrite(raw_text, api_key):
                full_content += chunk
                placeholder.markdown(full_content + "▌")
            
            placeholder.markdown(full_content) # 完成后移除光标
            st.success("生成完毕！")
            st.code(full_content, language="markdown")
        else:
            st.error("内容抓取失败")
