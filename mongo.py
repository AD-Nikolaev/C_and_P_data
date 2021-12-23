from pprint import pprint
from pymongo import MongoClient

from get_vacancy import get_vacancy_info


MONGO_URL = "127.0.0.1:27017"
MONGO_DB = "vacancies"

client = MongoClient(MONGO_URL)
db = client[MONGO_DB]
collection = db["vacancies_hh"]


def find_by_min_salary(collection, salary_min):
    result = collection.find({'salary_min': {"$gt": salary_min}},
                             {'_id': 0, 'input_website': 0})
    for item in result:
        pprint(item)


def find_by_salary(collection, salary_min, salary_max):
    result = collection.find({"$or": [
        {"$and": [{'salary_min': {"$gt": salary_min}}, {'salary_max': {"$lt": salary_max}}]},
        {"$and": [{'salary_min': {"$gt": salary_min}}, {'salary_max': {"$eq": None}}]},
        ]},
                             {'_id': 0, 'input_website': 0})
    for item in result:
        pprint(item)


def insert_vacancies_to_db(collection, vacancy):
    print('Идет загрузка вакансий...')
    vacancy_info = get_vacancy_info(vacancy)
    for item in vacancy_info:
        collection.update_many({'hyperlink': {"$eq": item['hyperlink']}},
                               {'$set': item}, upsert=True)
    print('Вакансии загружены в базу данных!')


if __name__ == '__main__':
    insert_vacancies_to_db(collection, 'волшебник')
    insert_vacancies_to_db(collection, 'аналитик данных')
    find_by_min_salary(collection, 170000)
    find_by_salary(collection, 100000, 150000)