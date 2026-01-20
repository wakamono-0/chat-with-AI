import streamlit as st
import google.generativeai as genai
import time

st.title("高機能AIアシスタント")

# --- 1. AIの設定とキャラクター付け ---
try:
    GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
    
    # ここで性格を指定できます（例：親切なプロのエンジニア）
    system_instruction = "あなたは非常に優秀でフレンドリーなエンジニアです。回答は簡潔かつ専門的に行ってください。"
    
    model = genai.GenerativeModel(
        model_name='gemini-2.5-flash',
        system_instruction=system_instruction
    )
except Exception as e:
    st.error("設定エラーが発生しました。secrets.tomlやAPIキーを確認してください。")
    st.stop()

# --- 2. 記憶の管理（Gemini形式への変換） ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# 保存されているメッセージを画面に表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 3. チャット処理 ---
if prompt := st.chat_input("何でも相談してください"):
    # ユーザーの入力を表示・保存
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AIの回答処理
    with st.chat_message("assistant"):
        # 過去の履歴をGeminiが理解できる形式に変換して渡す
        history = [
            {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
            for m in st.session_state.messages[:-1]
        ]
        chat = model.start_chat(history=history)
        
        # ストリーミング（逐次表示）で回答を生成
        response_placeholder = st.empty()
        full_response = ""
        
    # AIの回答処理
    with st.chat_message("assistant"):
        # 履歴を含めたチャットを開始
        chat = model.start_chat(history=history)
        
        response_placeholder = st.empty()
        full_response = ""
        
        # AIからの応答を受け取る
        responses = chat.send_message(prompt, stream=True)
        
        for chunk in responses:
            # 届いた塊（chunk.text）を1文字ずつループ回す
            for char in chunk.text:
                full_response += char
                # 少しだけ待つ（0.02〜0.05秒くらいが人間にとって心地よい速度）
                time.sleep(0.02) 
                # カーソル演出を加えて表示を更新
                response_placeholder.markdown(full_response + "▌")
        
        # 最後にカーソルを消して確定させる
        response_placeholder.markdown(full_response)  
    # AIの回答を保存
    st.session_state.messages.append({"role": "assistant", "content": full_response})