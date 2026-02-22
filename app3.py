import streamlit as st
import google.generativeai as genai
import time

# ページ設定
st.set_page_config(page_title="高機能AIアシスタント", page_icon="🤖")

# ==========================================
# 1. サイドバー（設定メニュー）の作成
# ==========================================
with st.sidebar:
    st.title("⚙️ 設定")
    
    # プルダウンメニューでモデルを選択
    selected_model_label = st.selectbox(
        "AIモデルを選択",
        ["Gemini 2.5 Flash (高速・軽量)", "Gemini 2.5 Pro (高性能・複雑な推論)"]
    )
    
    # 選んだメニューに合わせて、実際のモデル名を決定
    if selected_model_label == "Gemini 2.5 Flash (高速・軽量)":
        target_model_name = "gemini-2.5-flash"
    else:
        target_model_name = "gemini-2.5-pro"
        
    st.divider() # 区切り線
    
    # 会話履歴をリセットするボタン
    if st.button("💬 会話履歴をリセット"):
        st.session_state.messages = []
        st.rerun() # 画面を再読み込みしてまっさらにする

# ==========================================
# 2. メイン画面とAIの設定
# ==========================================
st.title("高機能AIアシスタント")

try:
    GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
    
    system_instruction = "あなたは非常に優秀でフレンドリーなエンジニアです。回答は簡潔かつ専門的に行ってください。"
    
    # サイドバーで決定した target_model_name をセットする
    model = genai.GenerativeModel(
        model_name=target_model_name,
        system_instruction=system_instruction
    )
except Exception as e:
    st.error(f"設定エラー: {e}")
    st.stop()

# ==========================================
# 3. 記憶の管理
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ==========================================
# 4. チャット処理
# ==========================================
if prompt := st.chat_input("何でも相談してください"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        history = [
            {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
            for m in st.session_state.messages[:-1]
        ]
        
        chat = model.start_chat(history=history)
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            # プロンプト送信（ストリーミング）
            responses = chat.send_message(prompt, stream=True)
            
            for chunk in responses:
                if chunk.text:
                    for char in chunk.text:
                        full_response += char
                        time.sleep(0.02) 
                        response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")