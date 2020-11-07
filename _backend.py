from sqlalchemy import create_engine

from random import shuffle, choice
import pandas as pd
import json

class AppBackend(object):
    def __init__(self):
        _db_credentials = json.load(open("credentials.json"))
        self._db_engine = create_engine('postgresql://{user}:{password}@{host}:{port}/{database}'.format(**_db_credentials))
    
    def __get_df_from_query(self, query):
        df = pd.read_sql(query, self._db_engine)
        return df

    def get_random_categories(self, n=5):
        query = """
                    SELECT cat3name
                    FROM product_categories
                    ORDER BY RANDOM() LIMIT {n};
                """.format(n=n)
        return list(self.__get_df_from_query(query=query)["cat3name"])

    def get_random_products(self,category):
        query = """
                    SELECT productname
                    FROM product_categories
                    WHERE cat3name = '{category}'
                    ORDER BY RANDOM() LIMIT 5;
                """.format(category=category)
        return list(self.__get_df_from_query(query=query)["productname"])
        
if __name__ == "__main__":
    a = AppBackend()
    b = a.get_random_categories()
    print(b)
    print(a.get_random_products(choice(b)))