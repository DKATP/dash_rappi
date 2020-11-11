from sqlalchemy import create_engine

from random import shuffle, choice, random, randint
import pandas as pd
import numpy as np
import json

class AppBackend(object):
    def __init__(self):
        _db_credentials = json.load(open("credentials.json"))
        self._db_engine = create_engine('postgresql://{user}:{password}@{host}:{port}/{database}'.format(**_db_credentials))
    
    def __get_df_from_query(self, query):
        df = pd.read_sql(query, self._db_engine)
        return df

    def get_eda(self):
        pass

    def get_stimated_shoping_time(self, shopping_list, agg=False):
        if agg:
            max_value = round(random()+randint(0,100),2)
            x = np.arange(len(shopping_list))
            y = max_value*(1-np.exp(-x/int(len(shopping_list)*.2)))
            y[-1] = max_value
            return max_value,zip(shopping_list,y.tolist())
        else:
            return round(random()+randint(0,100),2)


    def sort_shopping_list(self, shopping_list):
        sorted_shopping_list = shopping_list.copy()
        shuffle(sorted_shopping_list)
        return sorted_shopping_list

    def describe_shopping_list(self, shopping_list):
        products_id = [str(int(float(product.split("-@-")[1]))) for product in shopping_list]
        query = """
                    WITH   cat1 AS (
                            SELECT COUNT(*) 
                            FROM (
                                SELECT DISTINCT cat1_name 
                                FROM  product_categories
                                WHERE product_id IN ({products_id})
                            ) AS cat1_count
                        ), cat2 AS (
                            SELECT COUNT(*) 
                            FROM (
                                SELECT DISTINCT cat2_name 
                                FROM  product_categories
                                WHERE product_id IN ({products_id})
                            ) AS cat2_count
                        ), cat3 AS (
                            SELECT COUNT(*) 
                            FROM (
                                SELECT DISTINCT cat3_name 
                                FROM  product_categories
                                WHERE product_id IN ({products_id})
                            ) AS cat3_count
                        )
                    SELECT cat1.count as c1, cat2.count as c2, cat3.count as c3 FROM cat1, cat2, cat3;
                """.format(products_id=",".join(products_id))
        counts = self.__get_df_from_query(query=query)
        print(counts["c1"][0])
        stimated_time,marginal_plot = self.get_stimated_shoping_time(shopping_list,agg=True)

        return {"n_items": len(shopping_list),
                "n_cat1": counts["c1"][0],
                "n_cat2": counts["c2"][0],
                "n_cat3": counts["c3"][0],
                "stimated_time": stimated_time,
                "marginal_plot": dict(marginal_plot)}


    def get_random_categories(self):
        query = """
                    SELECT cat3_name
                    FROM product_categories
                    ORDER BY RANDOM() LIMIT 10;
                """
        return list(self.__get_df_from_query(query=query)["cat3_name"])

    def get_random_products(self,category):
        query = """
                    SELECT product_name, product_id
                    FROM product_categories
                    WHERE cat3_name = '{category}'
                    ORDER BY RANDOM() LIMIT 5;
                """.format(category=category)
        products = self.__get_df_from_query(query=query)
        return list(products.agg("{0[product_name]}-@-{0[product_id]}".format, axis=1))
        
if __name__ == "__main__":
    a = AppBackend()
    b = a.get_random_categories()
    shopping_list = a.get_random_products(choice(b))
    print("shopping_list: ",shopping_list)
    print(a.describe_shopping_list(shopping_list))
    # ['Comida fresca', 'Despensa y productos secos',
    #    'Cuidado y limpieza del hogar', 'Cuidado del bebé', 'Bebidas',
    #    'Cuidado personal', 'Mascotas', 'Ferretería y jardín',
    #    'Comida preparada', 'Farmacia', 'Fiestas y piñatas',
    #    'Accesorios bebés y niños', 'Cigarrillos', 'Papelería y oficina',
    #    'Decoración y hogar', 'Flores y Plantas']
