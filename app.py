import streamlit as st
import requests
import xmltodict
import pandas as pd

def fetch_book_info(isbn):
    """NDLサーチAPIを利用して書籍情報を取得"""
    url = "https://iss.ndl.go.jp/api/opensearch"
    params = {"isbn": isbn}

    try:
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = xmltodict.parse(response.text)
            record = data["rss"]["channel"].get("item", None)

            if record:
                title = record.get('title', 'タイトルなし')
                creator = record.get('author', '著者情報なし')
                ndc = record.get('dc:subject', 'NDC分類なし')
                thumbnail = record.get('guid', None)  # サムネイルURLを取得
                return title, creator, ndc, thumbnail
            else:
                return None, None, "データが見つかりませんでした。", None
        else:
            return None, None, f"APIエラー: {response.status_code}", None
    except Exception as e:
        return None, None, f"エラーが発生しました: {e}", None

def get_thumbnail(isbn):
    url = "https://ndlsearch.ndl.go.jp/thumbnail/" + str(isbn) + ".jpg"
    response = requests.get(url)
    return url

def load_data():
    """CSVファイルを読み込んでデータフレームとして返す"""
    file_name = "data.csv"
    try:
        return pd.read_csv(file_name)
    except FileNotFoundError:
        return pd.DataFrame(columns=["ISBN", "タイトル", "著者", "NDC分類", "サムネイル"])

def save_to_csv(dataframe):
    """データフレームをCSVファイルに保存"""
    file_name = "data.csv"
    dataframe.to_csv(file_name, index=False)

# アプリの初期化
st.set_page_config(page_title="NDLサーチAPIで書籍情報を取得", layout="wide")

def main_page():
    if "data" not in st.session_state:
        st.session_state.data = load_data()

    st.title("NDLサーチAPIで書籍情報を取得")

    isbn_input = st.text_input("ISBN番号を入力してください", "9784488663353")
    if "title" not in st.session_state:
        st.session_state.title = ""
        st.session_state.creator = ""
        st.session_state.message = ""
        st.session_state.thumbnail = ""

    if st.button("検索"):
        if isbn_input.strip():
            st.session_state.title, st.session_state.creator, st.session_state.message, st.session_state.thumbnail = fetch_book_info(isbn_input)
        else:
            st.error("ISBN番号を入力してください。")

    title_box = st.text_input("タイトル", value=st.session_state.title)
    creator_box = st.text_input("著者", value=st.session_state.creator)
    message_box = st.text_input("NDC分類", value=st.session_state.message)

    if st.button("データを追加"):
        new_row = pd.DataFrame({
            "ISBN": isbn_input,
            "タイトル": title_box,
            "著者": creator_box,
            "NDC分類": message_box,
            "サムネイル": st.session_state.thumbnail
        }, index=[0])
        st.session_state.data = pd.concat([st.session_state.data, new_row]).reset_index(drop=True)
        st.success("データを追加しました。")

    if st.button("データを保存"):
        save_to_csv(st.session_state.data)
        st.success("データを保存しました。")

def data_page():
    st.title("保存されたデータ")
    st.write("現在のデータフレームの内容:")

    for _, row in st.session_state.data.iterrows():
        col1, col2 = st.columns([1, 3])
        tmp_thumbnail = get_thumbnail(row["ISBN"])
        with col1:
            if pd.notna(tmp_thumbnail):
                st.image(tmp_thumbnail, width=100)
            else:
                st.write("サムネイルなし")
        with col2:
            st.write(f"**タイトル:** {row['タイトル']}")
            st.write(f"**著者:** {row['著者']}")
            st.write(f"**NDC分類:** {row['NDC分類']}")

# ページ選択
page = st.sidebar.selectbox("ページを選択してください", ["検索", "データ表示"])

if page == "検索":
    main_page()
elif page == "データ表示":
    data_page()
