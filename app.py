import streamlit as st
import requests
import xmltodict
import pandas as pd

def get_ndc(data):
    if "item" not in data["rss"]["channel"].keys():
        return "No item"

    if type(data["rss"]["channel"]["item"]) == dict:
        item = data["rss"]["channel"]["item"]
        ndc = None
        for i in item["dc:subject"]:
            if type(i) == dict:
                if i["@xsi:type"].find("dcndl:NDC") >= 0:
                    ndc = i["#text"]
                    break
    else:
        for j in data["rss"]["channel"]["item"]:
            ndc = None
            if "dc:subject" in j.keys():
                for i in j["dc:subject"]:
                    if type(i) == dict:
                        if i["@xsi:type"].find("dcndl:NDC") >= 0:
                            ndc = i["#text"]
                            break

    return ndc if ndc else "NDC分類不明"

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
                ndc = get_ndc(data)
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
        return pd.DataFrame(columns=["ISBN", "Title", "Author", "NDC分類", "サムネイル"])

def save_to_csv(dataframe):
    file_name = "data.csv"
    dataframe.to_csv(file_name, index=False)

st.set_page_config(layout="wide")

def main_page():
    if "data" not in st.session_state:
        st.session_state.data = load_data()

    isbn_input = st.text_input("ISBN番号を入力してください", "")
    if "title" not in st.session_state:
        st.session_state.title = ""
        st.session_state.creator = ""
        st.session_state.ndc = ""
        st.session_state.ndc_major = ""
        st.session_state.note = ""

    if st.button("検索"):
        if int(isbn_input) in st.session_state.data["ISBN"].to_list():
            st.error("同一のISBNが登録されています。")
        if isbn_input.strip():
            st.session_state.title, st.session_state.creator, st.session_state.ndc = fetch_book_info(isbn_input)
            if st.session_state.title in ["データが見つかりませんでした", "APIエラー", "エラーが発生しました"]:
                st.session_state.title, st.session_state.creator, st.session_state.ndc = fetch_book_info2(isbn_input)
        else:
            st.error("ISBN番号を入力してください。")

    col1, col2 = st.columns([1, 3])
    with col1:
        tmp_thumbnail = get_thumbnail(isbn_input)
        st.image(tmp_thumbnail)
    with col2:
        title_box = st.text_input("タイトル", value=st.session_state.title)
        creator_box = st.text_input("著者", value=st.session_state.creator)
        ndc_box = st.text_input("NDC分類", value=st.session_state.ndc)
        ndc_mjor_index = 10 if st.session_state.ndc in ["", "NDC分類不明"] else int(st.session_state.ndc[0])
        ndc_major_box = st.selectbox("NDC大分類",
                                     ("0: 総記", "1: 哲学", "2: 歴史", "3: 社会科学", "4: 自然科学", "5: 技術",
                                      "6: 産業", "7: 芸術", "8: 言語", "9: 文学", "No Data"),
                                      index=ndc_mjor_index)
        note_box = st.text_input("備考", value=st.session_state.note)

    if st.button("データを保存"):
        new_row = pd.DataFrame({
            "ISBN": isbn_input,
            "Title": title_box,
            "Author": creator_box,
            "NDC": ndc_box,
            "NDC_major": ndc_major_box,
            "Note": note_box
        }, index=[0])
        st.session_state.data = pd.concat([st.session_state.data, new_row]).reset_index(drop=True).sort_values(["Author", "Title"])

        save_to_csv(st.session_state.data)
        st.success("データを保存しました。")

def data_page():
    cols_per_row = st.slider("Number of columns per row", 3, 10, 5)

    ndc_list = sorted(st.session_state.data["NDC_major"].dropna().unique().tolist())
    selected_ndc = st.multiselect("NDC分類から抽出", ndc_list)

    if selected_ndc != []:
        filtered_data = st.session_state.data[st.session_state.data["NDC_major"].isin(selected_ndc)]
    else:
        filtered_data = st.session_state.data

    cols = st.columns(cols_per_row)

    for i, (_, row) in enumerate(filtered_data.iterrows()):
        col = cols[i % cols_per_row]
        tmp_thumbnail = get_thumbnail(row["ISBN"])
        with col:
            st.image(tmp_thumbnail, caption=row["Title"], width=100)

page = st.sidebar.radio("ページを選択してください", ["書籍登録", "サムネ表示", "データ表示"])

if page == "書籍登録":
    main_page()
elif page == "サムネ表示":
    data_page()
elif page == "データ表示":
    st.dataframe(st.session_state.data, use_container_width=True)
