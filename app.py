import streamlit as st
import requests
import xmltodict
import pandas as pd

def fetch_book_info(isbn):
    url = "https://iss.ndl.go.jp/api/opensearch"
    params = {"isbn": isbn}

    try:
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = xmltodict.parse(response.text)
            record = data["rss"]["channel"].get("item", None)

            if record:
                title = record.get("title", "タイトル不明")
                creator = record.get("author", "著者情報不明")
                ndc = record.get("dc:subject", "NDC分類不明")
                return title, creator, ndc
            else:
                return "データが見つかりませんでした", None, None
        else:
            return "APIエラー", f"{response.status_code}", None
    except Exception as e:
        return "エラーが発生しました", f"{e}", None

def fetch_book_info2(isbn):
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {"q": f"isbn:{isbn}",
              "country": "JP"}
    try:
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            record = data["items"][0]["volumeInfo"]

            if record:
                title = record.get("title", "タイトル不明")
                creator = record.get("authors", "著者情報不明")
                ndc = "NDC分類不明"
                return title, creator, ndc
            else:
                return "データが見つかりませんでした", None, None
        else:
            return "APIエラー", f"{response.status_code}", None
    except Exception as e:
        return "エラーが発生しました", f"{e}", None

def get_thumbnail(isbn):
    if isbn == "":
        return "NoImage.png"

    url = "https://ndlsearch.ndl.go.jp/thumbnail/" + str(isbn) + ".jpg"
    
    if requests.get(url).status_code == 404:
        url_ = "https://www.googleapis.com/books/v1/volumes"
        params = {"q": f"isbn:{isbn}",
                "country": "JP"}
        response = requests.get(url_, params=params)
        if response.status_code == 200:
            try:
                tmp_thumbnail = response.json()["items"][0]["volumeInfo"]["imageLinks"].get("thumbnail", "NoImage.png")
            except:
                return "NoImage.png"
    else:
        tmp_thumbnail = url
    return tmp_thumbnail

def load_data():
    file_name = "data.csv"
    try:
        return pd.read_csv(file_name)
    except FileNotFoundError:
        return pd.DataFrame(columns=["ISBN", "タイトル", "著者", "NDC分類", "サムネイル"])

def save_to_csv(dataframe):
    file_name = "data.csv"
    dataframe.to_csv(file_name, index=False)

st.set_page_config(page_title="NDLサーチAPIで書籍情報を取得", layout="wide")

def main_page():
    if "data" not in st.session_state:
        st.session_state.data = load_data()

    st.title("ISBNで書籍情報を取得")

    isbn_input = st.text_input("ISBN番号を入力してください", "")
    if "title" not in st.session_state:
        st.session_state.title = ""
        st.session_state.creator = ""
        st.session_state.message = ""
        st.session_state.thumbnail = ""

    if st.button("検索"):
        if isbn_input.strip():
            st.session_state.title, st.session_state.creator, st.session_state.message = fetch_book_info(isbn_input)
            if st.session_state.title in ["データが見つかりませんでした", "APIエラー", "エラーが発生しました"]:
                st.session_state.title, st.session_state.creator, st.session_state.message = fetch_book_info2(isbn_input)
        else:
            st.error("ISBN番号を入力してください。")

    col1, col2 = st.columns([1, 3])
    with col1:
        tmp_thumbnail = get_thumbnail(isbn_input)
        st.image(tmp_thumbnail)
    with col2:
        title_box = st.text_input("タイトル", value=st.session_state.title)
        creator_box = st.text_input("著者", value=st.session_state.creator)
        message_box = st.text_input("NDC分類", value=st.session_state.message)

    if st.button("データを追加"):
        new_row = pd.DataFrame({
            "ISBN": isbn_input,
            "タイトル": title_box,
            "著者": creator_box,
            "NDC分類": message_box
        }, index=[0])
        st.session_state.data = pd.concat([st.session_state.data, new_row]).reset_index(drop=True)
        st.success("データを追加しました。")

    if st.button("データを保存"):
        save_to_csv(st.session_state.data)
        st.success("データを保存しました。")

def data_page():
    cols_per_row = st.slider("Number of columns per row", 3, 10, 5)

    ndc_list = sorted(st.session_state.data["NDC_大分類"].dropna().unique().tolist())
    selected_ndc = st.multiselect("NDC分類から抽出", ndc_list)

    if selected_ndc != []:
        filtered_data = st.session_state.data[st.session_state.data["NDC_大分類"].isin(selected_ndc)]
    else:
        filtered_data = st.session_state.data

    cols = st.columns(cols_per_row)

    for i, (_, row) in enumerate(filtered_data.iterrows()):
        col = cols[i % cols_per_row]
        tmp_thumbnail = get_thumbnail(row["ISBN"])
        with col:
            st.image(tmp_thumbnail, caption=row["タイトル"], width=100)

page = st.sidebar.radio("ページを選択してください", ["書籍登録", "サムネ表示", "データ表示"])

if page == "書籍登録":
    main_page()
elif page == "サムネ表示":
    data_page()
elif page == "データ表示":
    st.dataframe(st.session_state.data)
