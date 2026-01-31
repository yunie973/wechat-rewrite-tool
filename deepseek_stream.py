import requests

def clamp_target_words(n: int) -> int:
    try:
        n = int(n)
    except:
        n = 1000
    return max(200, n)

def words_to_hint(target_words: int) -> str:
    tw = clamp_target_words(target_words)
    low = int(tw * 0.85)
    high = int(tw * 1.15)
    return f"正文尽量贴近目标字数：约{tw}字（允许浮动，参考区间{low}-{high}字）。"

def words_to_max_tokens(target_words: int) -> int:
    tw = clamp_target_words(target_words)
    est = int(tw * 2.2)
    return max(800, min(est, 4096))

def stream_ai_rewrite(text: str, api_key: str, temperature: float, target_words: int):
    url = "https://api.deepseek.com/chat/completions"
    system_prompt = f"""假设你是一个专业的自媒体作家。对下文进行二创。
【原创加强建议】：句型词汇调整、内容拓展、避免关键词、结构逻辑调整、视角切换、重点聚焦、角度转换、避免直接引用。

【硬性禁令（必须严格遵守）】
- 永远不要出现“不是……而是……”的句式（任何变体都不行）。
- 全文绝对不要出现破折号：—— 或 —（如果需要停顿，用逗号或句号）。
- 绝对禁止结构化：禁止使用列表、分点（如1.2.3.或●），保持段落连贯性。

【输出结构】
1. 第一行写【推荐爆款标题】，接着输出5个爆款标题，每行一个（保留标题标点）。
2. 标题区后空三行。
3. 正文开头必须先写150字引入语。
4. 小标题格式固定为 ## 01. XXX，总数控制在 2-4 个。
【篇幅要求】：{words_to_hint(target_words)}
"""
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"原文=（{text}）"},
        ],
        "stream": True,
        "temperature": float(temperature),
        "max_tokens": int(words_to_max_tokens(target_words)),
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    return requests.post(url, headers=headers, json=payload, stream=True, timeout=120)
