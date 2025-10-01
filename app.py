import os, sys
import streamlit as st
from dotenv import load_dotenv

# --- APIキーのロード ---
load_dotenv()
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
else:
    st.error("❌ OPENAI_API_KEY が未設定です。Secrets または .env に設定してください。")
    st.stop()

# --- サブフォルダを import パスに追加 ---
BASE_DIR = os.path.dirname(__file__)
MODULE_DIR = os.path.join(BASE_DIR, "ダウンロード用", "company_inner_search_app")
if MODULE_DIR not in sys.path:
    sys.path.insert(0, MODULE_DIR)

import constants as ct
import utils
import components as cn
from initialize import initialize
import logging, traceback

# --- ページ設定は最初の一度だけ ---
st.set_page_config(page_title=getattr(ct, "APP_NAME", "company_inner_search_app"))

# --- ロガー設定 ---
logger = logging.getLogger(getattr(ct, "LOGGER_NAME", "ApplicationLog"))

# --- 初期化処理 ---
try:
    initialize()
except Exception as e:
    st.error("初期化処理でエラーが発生しました（詳細を表示します）", icon="⚠️")
    st.exception(e)
    st.code(traceback.format_exc(), language="text")
    st.stop()

# --- 初期表示 ---
cn.display_app_title()
cn.display_select_mode()
cn.display_initial_ai_message()

# --- 会話ログ ---
try:
    cn.display_conversation_log()
except Exception as e:
    st.error("会話ログ表示中にエラーが発生しました", icon="⚠️")
    st.exception(e)
    st.stop()

# --- チャット入力 ---
chat_message = st.chat_input(ct.CHAT_INPUT_HELPER_TEXT)

if chat_message:
    logger.info({"message": chat_message, "application_mode": st.session_state.mode})
    with st.chat_message("user"):
        st.markdown(chat_message)

    res_box = st.empty()
    with st.spinner(ct.SPINNER_TEXT):
        try:
            llm_response = utils.get_llm_response(chat_message)
        except Exception as e:
            st.error("LLM応答処理でエラー", icon="⚠️")
            st.exception(e)
            st.stop()

    with st.chat_message("assistant"):
        try:
            if st.session_state.mode == ct.ANSWER_MODE_1:
                content = cn.display_search_llm_response(llm_response)
            elif st.session_state.mode == ct.ANSWER_MODE_2:
                content = cn.display_contact_llm_response(llm_response)
            logger.info({"message": content, "application_mode": st.session_state.mode})
        except Exception as e:
            st.error("回答表示処理でエラー", icon="⚠️")
            st.exception(e)
            st.stop()

    st.session_state.messages.append({"role": "user", "content": chat_message})
    st.session_state.messages.append({"role": "assistant", "content": content})
