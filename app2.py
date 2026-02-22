import streamlit as st
import google.generativeai as genai
from groq import Groq  # Groqを追加
import time

st.set_page_config(page_title="マルチAIアシスタント", page_icon="🤖")

# ==========================================
# 1. サイドバー（設定メニュー）
# ==========================================
with st.sidebar:
    st.title("⚙️ 設定")
    
    # 3つのモデルから選べるように変更
    selected_model_label = st.selectbox(
        "AIモデルを選択",
        [
            "Gemini 2.5 Flash (Google/高速)", 
            "Gemini 2.5 Pro (Google/高性能)",
            "Llama 3 8B (Groq/爆速)"  # 追加！
        ]
    )
    
    st.divider()
    if st.button("💬 会話履歴をリセット"):
        st.session_state.messages = []
        st.rerun()

# ==========================================
# 2. APIの初期設定
# ==========================================
st.title("マルチAIアシスタント")

try:
    # Geminiの設定
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Groqの設定
    groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    
    system_instruction = "あなたは非常に優秀でフレンドリーなエンジニアです。簡潔に答えてください。"
except Exception as e:
    st.error("APIキーの設定エラーです。secrets.tomlを確認してください。")
    st.stop()

# ==========================================
# 3. 記憶の管理と表示
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ==========================================
# 4. チャット処理（モデル切り替え）
# ==========================================
if prompt := st.chat_input("何でも相談してください"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            # --- Geminiが選ばれた場合の処理 ---
            if "Gemini" in selected_model_label:
                target_model = "gemini-1.5-flash" if "Flash" in selected_model_label else "gemini-1.5-pro"
                model = genai.GenerativeModel(model_name=target_model, system_instruction=system_instruction)
                
                # Gemini用の履歴データ作成
                history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                chat = model.start_chat(history=history)
                
                responses = chat.send_message(prompt, stream=True)
                for chunk in responses:
                    if chunk.text:
                        for char in chunk.text:
                            full_response += char
                            time.sleep(0.01) # 少し速めに設定
                            response_placeholder.markdown(full_response + "▌")
            
            # --- Groq (Llama 3)が選ばれた場合の処理 ---
            else:
                # Groq用の履歴データ作成（OpenAIと同じ形式）
                messages = [{"role": "system", "content": system_instruction}]
                for m in st.session_state.messages:
                    messages.append({"role": m["role"], "content": m["content"]})
                
                # 爆速APIを呼び出す
                stream = groq_client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=messages,
                    stream=True,
                )
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        full_response += chunk.choices[0].delta.content
                        time.sleep(0.01)
                        response_placeholder.markdown(full_response + "▌")

            # 最終的な確定表示と保存
            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")