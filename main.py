# ============================================
# 1. 道具を読みこむ（os / gradio / OpenAI を使えるようにする）
# ============================================
import os
import gradio as gr
from openai import OpenAI


# ============================================
# 2. AIとつなぐ準備をする
# ============================================
BASE_URL = "https://education-demo-app.services.ai.azure.com/openai/v1"
API_KEY = os.environ.get("AZURE_OPENAI_API_KEY")
if not API_KEY:
    raise RuntimeError("環境変数 AZURE_OPENAI_API_KEY が設定されていません。")

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)


# ============================================
# 3. AIの性格・ルール・話し方を決める
# ============================================
system_prompt = """
あなたは高校生向けの「地元のお店紹介AI」です。
目的は、ユーザーと会話しながら、ユーザーの行きたいお店を一緒に決めることです。

基本方針:
- いきなり最終案を決めつけない（まずは希望や条件を整理するところから）
- ユーザーの回答に合わせて、少しずつ候補を絞る
- 会話を通して「候補出し → 比較 → 絞り込み → 当日プラン」まで進める

会話の進め方:
1. 最初に、行きたいエリア・日時・予算・一緒に行く人数・興味（自然/カフェ/ショッピングなど）を確認する
2. 情報が足りない場合は、質問を1〜2個だけする
3. 混雑を避けやすい条件（時間帯・曜日・穴場エリア）を意識して、候補を3つほど出す
4. ユーザーの反応を聞いて、方向性を絞る
5. 決まったスポットについて、混雑を避けるおすすめの時間帯・回り方・持ち物を一緒に考える

回答ルール:
- 毎回、最後に次の一歩につながる質問をする。ただし質問攻めにしない
- ユーザーが迷っている時は、選びやすい選択肢を出す
- 混雑しやすい時間帯やイベント時は、代わりの時間帯や穴場を提案する
- まだ決まっていないことを勝手に決めない

話し方:
- 高校生にもわかりやすく
- 明るく、友達に相談している感じ
- でも現実的で、実際に行ける案を出す
"""


# ============================================
# 3.5 画面の色テーマを定義する
# ============================================
custom_css = """
:root {
    --bg-grad-1: #f5fbff;
    --bg-grad-2: #fff6e8;
    --surface: #ffffff;
    --text-main: #1f2937;
    --accent: #0f766e;
    --accent-strong: #0b5f59;
    --user-bubble: #d1fae5;
    --bot-bubble: #ffffff;
}

body {
    background: linear-gradient(135deg, var(--bg-grad-1), var(--bg-grad-2));
}

.gradio-container {
    max-width: 860px !important;
    margin: 24px auto !important;
}

h1 {
    color: var(--accent) !important;
    font-weight: 800 !important;
}

.wrap {
    background: rgba(255, 255, 255, 0.85) !important;
    border: 1px solid #dbeafe !important;
    border-radius: 16px !important;
}

button.primary {
    background: var(--accent) !important;
    border-color: var(--accent) !important;
}

button.primary:hover {
    background: var(--accent-strong) !important;
    border-color: var(--accent-strong) !important;
}

[data-testid="user"] .message {
    background: var(--user-bubble) !important;
    color: var(--text-main) !important;
}

[data-testid="bot"] .message {
    background: var(--bot-bubble) !important;
    color: var(--text-main) !important;
    border: 1px solid #e5e7eb !important;
}
"""

 
# ============================================
# 4. メッセージが送られるたびに呼ばれる関数を定義する
# ============================================
def chat(message, history):
    messages = [{"role": "system", "content": system_prompt}]
    messages += [
        {"role": m["role"], "content": m["content"]}
        for m in history
    ]
    messages.append({"role": "user", "content": message})

    res = client.chat.completions.create(
        model="gpt-5.4-mini",
        messages=messages,
    )
    return res.choices[0].message.content


# ============================================
# 5. チャット画面を作成して起動する
# ============================================
with gr.Blocks(title="地元のお店紹介AI") as demo:
    gr.Markdown("# 地元のお店紹介AI")
    gr.ChatInterface(
        fn=chat,
        textbox=gr.Textbox(placeholder="メッセージを入力"),
    )
 
demo.launch(
    css=custom_css,
    share=True,
    auth=("student", "edu2026"),
)