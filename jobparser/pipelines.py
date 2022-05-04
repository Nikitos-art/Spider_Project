# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient


class JobparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongobase = client.vacancy1204

    def process_item(self, item, spider):
        if spider.name == 'hhru':
            item['min_salary'], item['max_salary'], item['currency'] = self.process_salary(item['salary'])
            del item['salary']
        else:
            pass

        collection = self.mongobase[spider.name]
        collection.insert_one(item)

        return item

    def process_salary(self, salary):
        vacancy_salary_data = {}
        if 'з/п не указана' in salary:
            salary['min_salary'] = 'не указана'
            salary['max_salary'] = 'не указана'
            salary['currency'] = 'не указана'
        else:
            salary = salary.text.replace("\xa0", '').split()
            if 'от' in salary and 'до' not in salary:
                if 'руб.' in salary:
                    vacancy_salary_data['min_salary'] = int(salary[1])
                    vacancy_salary_data['max_salary'] = 'не указана'
                    vacancy_salary_data['currency'] = 'руб.'
                if 'USD' in salary:
                    vacancy_salary_data['min_salary'] = int(salary[1])
                    vacancy_salary_data['max_salary'] = 'не указана'
                    vacancy_salary_data['currency'] = 'USD'
            if 'до' in salary and 'от' not in salary:
                if 'руб.' in salary:
                    vacancy_salary_data['min_salary'] = 'не указана'
                    vacancy_salary_data['max_salary'] = int(salary[1])
                    vacancy_salary_data['currency'] = 'руб.'
                if 'USD' in salary:
                    vacancy_salary_data['min_salary'] = 'не указана'
                    vacancy_salary_data['max_salary'] = int(salary[1])
                    vacancy_salary_data['currency'] = 'USD'
            if 'от' not in salary and 'до' not in salary:
                if 'руб.' in salary:
                    vacancy_salary_data['min_salary'] = int(salary[0])
                    vacancy_salary_data['max_salary'] = int(salary[2])
                    vacancy_salary_data['currency'] = 'руб.'
                if 'USD' in salary:
                    vacancy_salary_data['min_salary'] = int(salary[0])
                    vacancy_salary_data['max_salary'] = int(salary[2])
                    vacancy_salary_data['currency'] = 'USD'

