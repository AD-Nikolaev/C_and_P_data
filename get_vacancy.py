import time
import requests
import traceback
import sys
from fp.fp import FreeProxy
from bs4 import BeautifulSoup as bs
import pprint


def get(url, headers, params, proxies):
    r = requests.get(url, headers=headers, params=params, proxies=proxies)
    return r


def get_vacancy(url, vacancy, headers, proxies, page, employment, price_exists):
    params = {
        "L_save_area": "true",
        "clusters": "true",
        "enable_snippets": "true",
        "salary": {"st": "searchVacancy"},
        "text": f'{vacancy}',
        "showClusters": "true",
        "page": f"{page}",
        "area": 1,  # Для поиска только по Москве
        "employment": employment,
        "only_with_salary": price_exists,
    }
    r = requests.get(url, headers=headers, params=params, proxies=proxies)
    return bs(r.text, "html.parser")


def get_vacancy_info(vac_name, employment, price_exists):
    url = "https://hh.ru/search/vacancy"
    proxies = {'http': f'{FreeProxy().get()}'}
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/89.0.4389.114 Safari/537.36"
    }
    next_button = True
    items_info = []
    i = 0
    with open(f"hh_{vac_name}_search_errors.txt", "w") as f:
        print('')
    while True:
        soup = get_vacancy(url, vac_name, headers, proxies, str(i), employment, price_exists)
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

            except Exception as e:
                e_type, e_val, e_tb = sys.exc_info()
                err = f"Error on page {i} with object №{i}, name: {info['name']}"
                with open(f"hh_{u_input_search}_search_errors.txt", "a", encoding='utf8') as f:
                    print(err, file=f)
                    traceback.print_exception(e_type, e_val, e_tb, file=f)
                    print("---||---", file=f)

            info["site_from"] = item.url
            items_info.append(info)
        if next_button is None:
            break
        i += 1

        soup = get_vacancy(url, u_input_search, headers, proxies, str(i), emp_dict[u_input_employment], price_exists)
        next_button = soup.find("a", attrs={"data-qa": "pager-next"})
        time.sleep(0.1)
    return items_info


if __name__ == '__main__':
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
    items_info = get_vacancy_info(u_input_search, emp_dict[u_input_employment], price_exists)
    pprint(items_info)


# save_json(f"hh_{u_input_search}_search_result.json", items_info)
# data = load_json(f"hh_{u_input_search}_search_result.json")

# df = pd.DataFrame(data)
#
# pd.options.display.width = 1200
# pd.options.display.max_colwidth = 20
#
# print("\nResutls -->\n")
# time.sleep(0.5)

# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#     print(df)
