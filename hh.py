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


url = "https://hh.ru/search/vacancy"
u_input_search = input('Введите параметры поиска: ')
u_input_employment = input('''Выберите тип занятости: 
0 - не важно;
1 - полная;
2 - частичная;
3 - стажировка;
4 - проектная работа;
''')
u_input_price_exists = input('Зарплата должна быть указана? (y/n): ')
emp_dict = {"0": "none", "1": "full", "2": "part", "3": "probation", "4": "project"}
if u_input_employment not in emp_dict.keys():
    u_input_employment = "0"
if u_input_price_exists == "y":
    price_exists = "true"
else:
    price_exists = "false"
params = {
    "text": u_input_search,
    # "area": 1,  # Для поиска только по Москве
    "employment": emp_dict[u_input_employment],
    "only_with_salary": price_exists,
    "page": 0
}
headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/89.0.4389.114 Safari/537.36"
}

r = get(url, headers, params)

path = "hh.rsp"
save_pickle(r, path)
r = load_pickle(path)
soup = bs(r.text, "html.parser")

next_button = True
items_info = []
i = 0
with open(f"hh_{u_input_search}_search_errors.txt", "w") as f:
    print('')
while True:
    items = soup.find_all(attrs={"class": "vacancy-serp-item"})
    for item in items:
        info = {}
        a = item.find("a", attrs={"class": "bloko-link"})
        info["href"] = a.attrs["href"]
        info["name"] = a.text
        info["city/region"] = item.find(attrs={"data-qa": "vacancy-serp__vacancy-address"}).text
        a = item.find("a", attrs={"class": "bloko-link bloko-link_secondary"})
        company = a.text.replace("\xa0", " ")
        info["company"] = company
        try:
            price = item.find(attrs={"class": "vacancy-serp-item__sidebar"}).text.replace("\u202f", "").split()
            if price[0] == 'от':
                info["price_min"] = price[1]
                info["price_max"] = "-"
            elif price[0] == 'до':
                info["price_min"] = "-"
                info["price_max"] = price[1]
            else:
                info["price_min"] = price[0]
                info["price_max"] = price[2]
            info["currency"] = price[-1]
        # добавил модули, чтобы убрать ошибки в файл и чуток их причесать (раньше вообще их никак не обрабатывал)
        except Exception as e:
            e_type, e_val, e_tb = sys.exc_info()
            err = f"Error on page {params['page']} with object №{i}, name: {info['name']}"
            with open(f"hh_{u_input_search}_search_errors.txt", "a", encoding='utf8') as f:
                print(err, file=f)
                traceback.print_exception(e_type, e_val, e_tb, file=f)
                print("---||---", file=f)

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
    next_button = soup.find("a", attrs={"data-qa": "pager-next"})
    time.sleep(0.4)

os.remove(path)
save_json(f"hh_{u_input_search}_search_result.json", items_info)
data = load_json(f"hh_{u_input_search}_search_result.json")

df = pd.DataFrame(data)

# ширина дисплея и ширина колонок pandas DataFrame
pd.options.display.width = 1200
pd.options.display.max_colwidth = 20

print("\nResutls -->\n")
time.sleep(0.5)

# отобразить весь pandas DataFrame
with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    print(df)