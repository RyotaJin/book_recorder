import pandas as pd
import requests
import xmltodict

def get_ndc_from_isbn(isbn):
    base_url = "http://iss.ndl.go.jp/api/opensearch"
    params = {"isbn": isbn}

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = xmltodict.parse(response.text)

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

        return ndc if ndc else "No data"

    except requests.exceptions.RequestException as e:
        return f"エラーが発生しました: {e}"

ndc_major_dict = {"0": "0: 総記",
                  "1": "1: 哲学",
                  "2": "2: 歴史",
                  "3": "3: 社会科学",
                  "4": "4: 自然科学",
                  "5": "5: 技術",
                  "6": "6: 産業",
                  "7": "7: 芸術",
                  "8": "8: 言語",
                  "9": "9: 文学",
                  "N": ""
                  }

# isbn_list = [4522421842, 4522422520]
isbn_list = pd.read_csv(r"D:\OneDrive\Projects\読書リスト - シート1.csv").ISBN.to_list()
output_ndc = []
output_ndc_major = []
for i in isbn_list:
    result = get_ndc_from_isbn(str(i))
    output_ndc.append(result)
    output_ndc_major.append(ndc_major_dict[result[0]])

df = pd.DataFrame({"ISBN": isbn_list,
                   "NDC": output_ndc,
                   "NDC_major": output_ndc_major})
df.query("NDC == 'No item'")
df.to_csv("foo.csv", encoding="shift-jis", quoting=1)
