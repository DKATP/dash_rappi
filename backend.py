from sqlalchemy import create_engine

from random import shuffle, choice, random, randint
import pandas as pd
import numpy as np
import json
import ortools
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

class AppBackend(object):
    def __init__(self):
        _db_credentials = json.load(open("credentials.json"))
        self._db_engine = create_engine('postgresql://{user}:{password}@{host}:{port}/{database}'.format(**_db_credentials))
    
    def __get_df_from_query(self, query):
        df = pd.read_sql(query, self._db_engine)
        return df

    def get_eda(self):
        query = """
                    SELECT * FROM product_times;
                """
        data = self.__get_df_from_query(query)
        data = data.pivot(index='cat2_name_x',columns='cat2_name_y',values='item_time_y')
        return data

    def get_estimated_shoping_time(self, shopping_list, agg=False):
        if agg:
            max_value = round(random()+randint(0,100),2)
            x = np.arange(len(shopping_list))
            y = max_value*(1-np.exp(-x/round(len(shopping_list)*.2)))
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
        estimated_time,marginal_plot = self.get_estimated_shoping_time(shopping_list,agg=True)

        return {"n_items": len(shopping_list),
                "n_cat1": counts["c1"][0],
                "n_cat2": counts["c2"][0],
                "n_cat3": counts["c3"][0],
                "estimated_time": estimated_time,
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

    def get_product_times(self):
        query = """
                SELECT * FROM PRODUCT_TIMES;
                   """
        query_cm = """
                        SELECT * FROM CAT_MAP;
                           """
        prod_times = self.__get_df_from_query(query=query)
        cat_map = self.__get_df_from_query(query=query_cm)

        return prod_times, cat_map

    def get_categories2_from_prods(self, shopping_list):
        products_id = [str(int(float(product.split("-@-")[1]))) for product in shopping_list]
        query = """
                   SELECT DISTINCT cat2_name, product_id
                   FROM  product_categories
                   WHERE product_id IN ({products_id})
                    """.format(products_id=",".join(products_id))
        product_categories = self.__get_df_from_query(query=query)
        return product_categories

    # Creates the time(cost) matrix between products(nodes) and depot(value=0)
    def create_time_matrix(self, map_cats_nodes, product_times, map_cats_filtered):
        # sorted nodes
        M = 10000000
        nodes = list(map_cats_nodes.values())
        nodes.append(0)
        nodes = sorted(nodes)
        dimension = len(nodes)
        df = product_times[(product_times['cat2_name_x'].isin(map_cats_filtered)) &
                           (product_times['cat2_name_y'].isin(map_cats_filtered))]
        df = df.replace({'cat2_name_x': map_cats_nodes, 'cat2_name_y': map_cats_nodes})

        # Initialize
        matrix = np.full((dimension, dimension), M)

        # Fill
        for i, row in df.iterrows():
            ind_x = int(row['cat2_name_x'])
            ind_y = int(row['cat2_name_y'])
            matrix[ind_x, ind_y] = row['item_time_y']

        # dismiss the depot
        matrix[:, 0] = 0
        matrix[0, :] = 0

        return matrix, nodes, map_cats_nodes

    def solve_optimization(self, time_matrix):
        # Create the routing index manager.
        manager = pywrapcp.RoutingIndexManager(len(time_matrix), 1, 0)
        # Create Routing Model.
        routing = pywrapcp.RoutingModel(manager)

        def distance_callback(from_index, to_index):
            """Returns the distance between the two nodes."""
            # Convert from routing variable Index to distance matrix NodeIndex.
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return time_matrix[from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

        def print_solution(manager, routing, solution):
            """Prints solution on console."""
            print('Objective: {} miles'.format(solution.ObjectiveValue()))
            index = routing.Start(0)
            plan_output = 'Picking route:\n'
            route_distance = 0
            list_answer = []
            while not routing.IsEnd(index):
                plan_output += ' {} ->'.format(manager.IndexToNode(index))
                list_answer.append(manager.IndexToNode(index))
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
            plan_output += ' {}\n'.format(manager.IndexToNode(index))
            print(plan_output)
            plan_output += 'Picking time: {}seconds\n'.format(route_distance)
            return list_answer, route_distance

        solution = routing.SolveWithParameters(search_parameters)
        if solution:
            list_answer, route_distance = print_solution(manager, routing, solution)
        else:
            list_answer = range(len(time_matrix)).append(0)
            route_distance = 95*len(time_matrix)
        return list_answer, route_distance

    def optimization_answer_processing(self,shopping_list, map_cats_filtered, product_times, cat_map, product_categories):
        prod_id_map = {}
        for product in shopping_list:
            prod_id = str(int(float(product.split("-@-")[1])))
            prod_name = str(product.split("-@-")[0])
            prod_id_map[prod_id] = prod_name

        prod_cats = product_categories.merge(cat_map[cat_map['map_value'].isin(map_cats_filtered)], how='inner')
        map_cats_nodes = dict(zip(map_cats_filtered, range(1, len(map_cats_filtered) + 1)))
        matrix, nodes, map_cats_nodes = self.create_time_matrix(map_cats_nodes, product_times, map_cats_filtered)
        list_answer, picking_time = self.solve_optimization(matrix)
        order_map_cats = []
        for i in list_answer:
            for catm, nodem in map_cats_nodes.items():
                if nodem == i:
                    order_map_cats.append(catm)
        prods_answer = []
        prods_picking_time = []
        for i in order_map_cats:
            for indexj, j in prod_cats.query("map_value==@i").iterrows():
                prod_name = prod_id_map[str(int(j['product_id']))]
                prods_answer.append(prod_name+"-@-"+str(j['product_id']))

        prod_cats['map_value_cat'] = pd.Categorical(prod_cats['map_value'],
                                                   categories = order_map_cats,
                                                   ordered = True)
        prod_cats = prod_cats.sort_values('map_value_cat')

        row_iterator = prod_cats.iterrows()
        _, last = row_iterator.__next__()  # take first item from row_iterator
        for i, row in row_iterator:
            prev = last['map_value']
            next = row['map_value']
            time = 60
            try:
                print(product_times.query("cat2_name_x==@prev & cat2_name_y==@next"))
                time = product_times.query("cat2_name_x==@prev & cat2_name_y==@next").iloc[0]['item_time_y']
            except:
                print("not found")
            prods_picking_time.append(time)
            last = row

        print(prods_answer)
        print(prods_picking_time)
        return prods_answer, prods_picking_time
        
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
