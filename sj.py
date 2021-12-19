import json
import time
import pickle
import requests
import pandas as pd
import traceback
import sys
import os
from bs4 import BeautifulSoup as bs


def save_pickle(o, path):
    with open(path, 'wb') as f:
        pickle.dump(o, f)


def load_pickle(path):
    with open(path, 'rb') as f:
        return pickle.load(f)


def get(url, headers, params):
    r = requests.get(url, headers=headers, params=params)
    return r


def save_json(f_name, data):
    with open(f_name, "w", encoding='utf8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_json(f_name):
    with open(f_name, "r", encoding='utf8') as f:
        return json.load(f)


url = "https://russia.superjob.ru/vacancy/search"
u_input_search = input('Введите параметры поиска: ')
u_input_employment = input('''Выберите тип занятости:
0 - не важно;
9 - вахта;
6 - полный день;
12 - сменная;
10 - неполная;
14 - неполная дистанционная
''')
u_input_price_exists = input('Зарплата должна быть указана? (y/n): ')
if u_input_employment not in ("9", "6", "12", "10", "14"):
    u_input_employment = "0"
if u_input_price_exists == "y":
    price_exists = 1
else:
    price_exists = 0
params = {
    "keywords": u_input_search,
    # "geo[t][0]": 4,  # Для поиска только по Москве
    "payment_defined": price_exists,
    "work_type[0]": u_input_employment,
    "page": 1
}
headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/89.0.4389.114 Safari/537.36"
}

r = get(url, headers, params)

path = "sj.rsp"
save_pickle(r, path)
r = load_pickle(path)
soup = bs(r.text, "html.parser")

next_button = True
items_info = []
i = 0
while True:
    items = soup.find_all(attrs={"class": "f-test-search-result-item"})
    for item in items:
        respond_button = item.find("button", attrs={
            "class": "bs_sM f-test-vacancy-response-button f-test-button-Otkliknutsya"})
        if respond_button is None:
            continue
        info = {}
        a = item.find("a", attrs={"target": "_blank"})
        info["name"] = a.text
        try:
            a = item.find("a", attrs={"target": "_self"})
            info["href"] = "https://russia.superjob.ru" + a.attrs["href"]
            info["company"] = a.text
        except Exception as e:
            e_type, e_val, e_tb = sys.exc_info()
            err = f"Error on page {params['page']} with object №{i}, name: {info['name']}"
            with open(f"sj_{u_input_search}_search_errors.txt", "a", encoding='utf8') as f:
                print(err, file=f)
                traceback.print_exception(e_type, e_val, e_tb, file=f)
                print("---||---", file=f)
        info["time, city/region"] = item.find(
            "span", attrs={"class": "_3mfro f-test-text-company-item-location _9fXTd _2JVkc _2VHxz"}
        ).text
        price = item.find(
            "span", attrs={"class": "_3mfro _2Wp8I PlM3e _2JVkc _2VHxz"}
        ).text.replace("&nbsp", "").split()
        if price[0] == 'от':
            info["price_min"] = price[1] + price[2]
            info["price_max"] = "-"
            info["currency"] = price[-1]
        elif price[0] == 'до':
            info["price_min"] = "-"
            info["price_max"] = price[1] + price[2]
            info["currency"] = price[-1]
        elif price[0] == 'По':
            info["price_min"] = price[0] + " " + price[1]
            info["price_max"] = price[0] + " " + price[1]
        elif price[2] == '-':
            info["price_min"] = price[0] + price[1]
            info["price_max"] = price[-3] + price[-2]
            info["currency"] = price[-1]
        else:
            info["price_min"] = price[0] + price[1]
            info["price_max"] = price[-3] + price[-2]
            info["currency"] = price[-1]

        info["site_from"] = r.url
        items_info.append(info)
        i += 1
    print(f"page №{params['page']} done...")
    if next_button is None:
        break
    params["page"] += 1

    r = get(url, headers, params)

    save_pickle(r, path)
    r = load_pickle(path)
    soup = bs(r.text, "html.parser")
    next_button = soup.find("a", attrs={"rel": "next"})
    time.sleep(0.4)

save_json(f"sj_{u_input_search}_search_result.json", items_info)
data = load_json(f"sj_{u_input_search}_search_result.json")
os.remove(path)

df = pd.DataFrame(data)

# ширина дисплея и ширина колонок pandas DataFrame
pd.options.display.width = 1200
pd.options.display.max_colwidth = 30

print("\nResutls -->\n")
time.sleep(0.5)

# отобразить весь pandas DataFrame
with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    print(df)