import streamlit as st
from typing import List
import streamlit.components.v1 as components
from db.model import Word
from modules.db_manager import (
    get_session,
    create_word,
    get_wordlist,
    get_word,
    update_word,
    delete_word,
)
from modules.dataclass import WordInput, build_word_entity
from modules.utils import esc, load_users


# ----------------------------
# Utils
# ----------------------------
def show_exception(e: Exception, context: str):
    st.error(f"❌ {context} に失敗しました: {type(e).__name__}: {e}")


# ----------------------------
# State
# ----------------------------
def ensure_state():
    if "page_mode" not in st.session_state:
        st.session_state.page_mode = "list"  # "list" or "edit"

    if "edit_id" not in st.session_state:
        st.session_state.edit_id = None

    if "user_id" not in st.session_state:
        st.session_state.user_id = None

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False


def go_list():
    st.session_state.page_mode = "list"
    st.session_state.edit_id = None
    st.rerun()


def go_edit(word_id: int):
    st.session_state.page_mode = "edit"
    st.session_state.edit_id = word_id
    st.rerun()


# ----------------------------
# Delete dialog
# ----------------------------
@st.dialog("削除確認")
def open_delete_dialog(word_id: int):
    st.warning("本当に削除しますか？")

    # 対象表示（任意）
    session = get_session()
    try:
        target = get_word(session, word_id, st.session_state.user_id)
    except Exception as e:
        show_exception(e, "削除対象取得")
        target = None
    finally:
        session.close()

    if target:
        st.write(f"対象： **{target.word}**")

    col1, col2 = st.columns(2)

    if col1.button("削除する", use_container_width=True):
        session = get_session()
        try:
            ok = delete_word(session, word_id, st.session_state.user_id)
            if ok:
                st.success("✅ 削除しました。")
                # ダイアログ閉じた後に一覧へ
                go_list()
            else:
                st.warning("削除対象が見つかりませんでした。")
        except Exception as e:
            show_exception(e, "削除")
        finally:
            session.close()

    if col2.button("キャンセル", use_container_width=True):
        st.rerun()


# ----------------------------
# Pages
# ----------------------------
def login_page():
    try:
        USERS = load_users()
    except Exception as e:
        show_exception(e, "設定読取")
        st.stop()

    st.title("ログイン")

    user = st.text_input("ユーザー名")
    password = st.text_input("パスワード", type="password")

    if st.button("ログイン"):
        info = USERS.get(user)
        if info and password == info["password"]:
            st.session_state.logged_in = True
            st.session_state.user_id = user
            st.success("ログインしました")
            st.rerun()
        else:
            st.error("ユーザー名またはパスワードが違います")


def show_list_page():
    st.subheader("📃 一覧・検索")

    # 一覧取得
    session = get_session()
    try:
        word_list: List[Word] = get_wordlist(session, st.session_state.user_id)
    except Exception as e:
        show_exception(e, "一覧取得")
        st.stop()
    finally:
        session.close()

    # 検索・絞り込み
    filter_col1, filter_col2, filter_col3 = st.columns([2, 1, 1])

    with filter_col1:
        search_text = st.text_input(
            "検索（単語 / 意味 / メモ）", placeholder="キーワードで検索"
        )

    categories = sorted(
        {
            word_row.category.strip()
            for word_row in word_list
            if word_row.category and word_row.category.strip()
        }
    )
    categories = ["(すべて)"] + categories

    with filter_col2:
        selected_cat = st.selectbox("カテゴリ", categories)

    with filter_col3:
        show_count = st.selectbox("表示件数", [10, 25, 50, 100], index=1)

    def match(word_row: Word) -> bool:
        if selected_cat != "(すべて)":
            if (word_row.category or "").strip() != selected_cat:
                return False

        if search_text.strip():
            key = search_text.strip().lower()
            hay = " ".join(
                [
                    (word_row.word or ""),
                    (word_row.meaning or ""),
                    (word_row.memo or ""),
                    (word_row.category or ""),
                ]
            ).lower()
            return key in hay

        return True

    filtered = [word_row for word_row in word_list if match(word_row)]
    st.write(f"件数: **{len(filtered)}** 件（全 {len(word_list)} 件）")

    st.subheader("📚 単語一覧（カード表示）")

    cards = st.columns(2)

    for idx, word_row in enumerate(filtered[:show_count]):
        with cards[idx % 2]:
            card_html = f"""
            <div style="
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 12px;
                margin-bottom: 8px;
                background-color: #fafafa;
                font-family: sans-serif;
            ">
                <div style="font-size: 1.1em; font-weight: bold; word-break: break-word; overflow-wrap: break-word">
                    {esc(word_row.word)}
                    <span style="color:#666; font-size:0.85em;">
                        {f"[{esc(word_row.category)}]" if word_row.category else ""}
                    </span>
                </div>

                <div style="margin-top:6px; white-space: pre-wrap; word-break: break-word; overflow-wrap: break-word;">{esc(word_row.meaning)}</div>

                <div style='margin-top:6px; color:#555; white-space: pre-wrap; word-break: break-word; overflow-wrap: break-word;'>📝メモ<br>{esc(word_row.memo)}</div>

                <div style="margin-top:8px; color:#888; font-size:0.8em;">
                    更新: {word_row.updated_at.strftime("%Y-%m-%d %H:%M")}
                </div>
            </div>
            """
            # Markdownを通さずHTML描画
            components.html(card_html, height=240, scrolling=True)

            # ボタン（columnsは使わず縦に置く：ネスト制限回避＆スマホで押しやすい）
            if st.button(
                "✏ 編集ページへ",
                key=f"edit_{word_row.word_id}",
                use_container_width=True,
            ):
                go_edit(word_row.word_id)

            if st.button(
                "🗑 削除", key=f"del_{word_row.word_id}", use_container_width=True
            ):
                open_delete_dialog(word_row.word_id)


def show_create_panel():
    st.subheader("➕ 新規登録")

    with st.form("create_form", clear_on_submit=True):
        input_word = st.text_input("単語", placeholder="例: おはよう")
        input_meaning = st.text_area("意味", placeholder="例: 挨拶", height=120)
        input_category = st.text_input(
            "カテゴリ（任意）", placeholder="例: 日本語, C#, DB, 業務"
        )
        input_memo = st.text_area(
            "メモ（任意）", placeholder="補足や自分なりの理解", height=120
        )

        submitted = st.form_submit_button("登録する", use_container_width=True)

    if submitted:
        if not input_word.strip() or not input_meaning.strip():
            st.warning("「単語」と「意味」は必須です。")
            return

        session = get_session()
        try:
            entity = build_word_entity(
                WordInput(
                    word=input_word,
                    meaning=input_meaning,
                    category=input_category,
                    memo=input_memo,
                )
            )
            entity.user_id = st.session_state.user_id
            create_word(session, entity)
            st.success("✅ 登録しました。")
            st.rerun()
        except Exception as e:
            show_exception(e, "登録")
        finally:
            session.close()


def show_edit_page(word_id: int):
    st.subheader("✏ 編集ページ")

    # 対象取得
    session = get_session()
    try:
        target = get_word(session, word_id, st.session_state.user_id)
    except Exception as e:
        show_exception(e, "編集対象取得")
        target = None
    finally:
        session.close()

    if target is None:
        st.warning("編集対象が見つかりませんでした。")
        if st.button("← 一覧へ戻る", use_container_width=True):
            go_list()
        return

    # 一覧へ戻る
    if st.button("← 一覧へ戻る", use_container_width=True):
        go_list()

    st.divider()

    with st.form("edit_form"):
        edit_word = st.text_input("単語", value=target.word)
        edit_meaning = st.text_area("意味", value=target.meaning, height=140)
        edit_category = st.text_input("カテゴリ（任意）", value=target.category or "")
        edit_memo = st.text_area("メモ（任意）", value=target.memo or "", height=140)

        save = st.form_submit_button("更新する", use_container_width=True)

    if save:
        if not edit_word.strip() or not edit_meaning.strip():
            st.warning("「単語」と「意味」は必須です。")
            return

        session = get_session()
        try:
            entity = build_word_entity(
                WordInput(
                    word=edit_word,
                    meaning=edit_meaning,
                    category=edit_category,
                    memo=edit_memo,
                )
            )
            entity.user_id = st.session_state.user_id
            ok = update_word(session, target.word_id, target.user_id, entity)
            if ok:
                st.success("✅ 更新しました。")
                go_list()
            else:
                st.warning("更新対象が見つかりませんでした。")
        except Exception as e:
            show_exception(e, "更新")
        finally:
            session.close()
