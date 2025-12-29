import streamlit as st
from modules.pages import (
    ensure_state,
    login_page,
    show_edit_page,
    show_create_panel,
    show_list_page,
)
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="個人辞書",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={},
)
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)
st.title("📘 個人辞書（単語・用語管理）")
st.caption("単語と意味を登録し、検索・編集・削除できます（スマホ/PC対応・DB同期）")

ensure_state()

# 画面分岐
if not st.session_state.get("logged_in"):
    # ログインページ
    login_page()
    st.stop()

if st.session_state.page_mode == "edit":
    # 編集ページ（左右レイアウトは不要にする方が自然）
    show_edit_page(st.session_state.edit_id)

else:
    # 一覧ページ：左=登録 / 右=検索・一覧
    left, right = st.columns([1, 2], gap="large")
    with left:
        show_create_panel()
    with right:
        show_list_page()
