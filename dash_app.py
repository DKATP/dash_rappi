import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd

import plotly.graph_objects as go
import plotly.express as px
import plotly.offline as pyo
import plotly.figure_factory as ff

from backend import AppBackend 

engine = AppBackend()

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "30rem",
    "padding": "2rem 1rem",
    "background-color": "#fd624f",
    "color": "#ffffff"
}

global global_n_clicks, shopping_list

shopping_list = []
global_n_clicks  = {
    "add": None,
    "run": None
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "30rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H3("Select your products", className="display-6"),
        html.Hr(),
        html.P(
            "Please put together your shopping list with the products available below", className="lead"
        ),
        html.P(
            "Select a Category", className="lead"
        ),
        dcc.Dropdown(
            id='categories-dropdown',
            style={"color": "#000000"},
            options=[ 
                {'label': category, 'value': category} for category in engine.get_random_categories()
            ],
            value='Seleccione una categoria'
        ),
        html.P(
            "Select a Product", className="lead"
        ),
        dcc.Dropdown(
            id='products-dropdown',
            style={"color": "#000000"},
            options=[],
            value='Seleccione un Producto'
        ),
        html.Button("Add Product",id='add-btn',disabled=False),
        html.P(
            "", className="lead", id="shopping-list"
        ),
        html.Button("Optimize",id='run-btn',disabled=False),
        # dbc.Nav(
        #     [
        #         dbc.NavLink("Page 1", href="/page-1", id="page-1-link"),
        #         dbc.NavLink("Page 2", href="/page-2", id="page-2-link"),
        #         dbc.NavLink("Page 3", href="/page-3", id="page-3-link"),
        #     ],
        #     vertical=True,
        #     pills=True,
        # ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


# # this callback uses the current pathname to set the active state of the
# # corresponding nav link to true, allowing users to tell see page they are on
# @app.callback(
#     [Output(f"page-{i}-link", "active") for i in range(1, 4)],
#     [Input("url", "pathname")],
# )
# def toggle_active_links(pathname):
#     if pathname == "/":
#         # Treat page 1 as the homepage / index
#         return True, False, False
#     return [pathname == f"/page-{i}" for i in range(1, 4)]


# @app.callback(Output("page-content", "children"), [Input("url", "pathname")])
# def render_page_content(pathname):
#     if pathname in ["/", "/page-1"]:
#         return html.P("This is the content of page 1!")
#     elif pathname == "/page-2":
#         return html.P("This is the content of page 2. Yay!")
#     elif pathname == "/page-3":
#         return html.P("Oh cool, this is page 3!")
#     # If the user tries to reach a different page, return a 404 message
#     return dbc.Jumbotron(
#         [
#             html.H1("404: Not found", className="text-danger"),
#             html.Hr(),
#             html.P(f"The pathname {pathname} was not recognised..."),
#         ]
#     )

@app.callback(
    Output('products-dropdown', 'options'),
    [Input('categories-dropdown', 'value')]
)
def update_output(category):
    print(category)
    products = engine.get_random_products(category)
    return [{"label":product,"value":product} for product in products]

@app.callback(
    [Output('shopping-list', 'children'), Output('run-btn', 'disabled')],
    [Input('add-btn', 'n_clicks'),Input('products-dropdown', 'value')]
)
def update_shopping_list(n_clicks,value):
    global global_n_clicks
    
    print(global_n_clicks["add"], n_clicks)
    if global_n_clicks["add"] == n_clicks or value == "Seleccione un Producto":
        return "", len(shopping_list) <= 2
    else:
    
        global_n_clicks["add"] = n_clicks
        if value in shopping_list:
            print(len(shopping_list))
            return "Seleccione un producto diferente", len(shopping_list) <= 2
        else:        
            shopping_list.append(value)
            print(shopping_list)
            print(len(shopping_list))
            return "Producto Agregado", len(shopping_list) <= 2

@app.callback(
    Output('page-content', 'children'),
    [Input('run-btn', 'n_clicks'),Input('run-btn', 'disabled')]
)
def optimize(n_clicks,disabled):
    global global_n_clicks

    if not(disabled) and global_n_clicks["run"]!=n_clicks:
        global_n_clicks["run"] = n_clicks

        description = engine.describe_shopping_list(shopping_list)

        fig = px.line(x=list(range(1,len(description["marginal_plot"])+1)),y= description["marginal_plot"].values())
        fig.update_layout(yaxis={"title":"Time [s]"},xaxis={"title":"Product", "tick0":0, "dtick":0})

        sorted_shopping_list = engine.sort_shopping_list(shopping_list)
      
        df1=pd.DataFrame({'ORDER RECEIVED':shopping_list})
        fig2 =  ff.create_table(df1)
        #fig.show()

        df2=pd.DataFrame({'ORDER SORTED':sorted_shopping_list})
        fig3 =  ff.create_table(df2)

        content = [
            html.H3("ORDER RESUME", className="display-6", style={'textAlign':'center','font-weight':'bold','backgroundColor':'#fd624f','opacity':'0.6'}),
            dbc.Row([ 
              dbc.Col([
                html.P(
                    "Number of different products: {}".format(description["n_items"]), className="lead", style={'textAlign':'center','font-weight':'bold'}
                ),
                html.P(
                    "   Number of categories L1: {}".format(description["n_cat1"]), className="lead", style={'textAlign':'center','font-weight':'bold'}
                ),
                html.P(
                    "     Number of categories L2: {}".format(description["n_cat2"]), className="lead", style={'textAlign':'center','font-weight':'bold'}
                ),
                html.P(
                    "       Number of categories L3: {}".format(description["n_cat3"]), className="lead", style={'textAlign':'center','font-weight':'bold'}
                ),
              ]),
            ]),
            html.H3("INITIAL SHOPPING LIST", className="display-6", style={'textAlign':'center','font-weight':'bold','backgroundColor':'#fd624f','opacity':'0.6'}),
            dbc.Row([  
              dbc.Col([ 
                  dcc.Graph(
                      figure = fig2
                  ),
              ]),           
              dbc.Col([
                  dbc.Alert(
                      "Estimated picking time: {}".format(description["estimated_time"]), className="display-5", color="primary"#, style={'height':'100px','widht':'15%','backgroundColor':'yellow', 'vertical-align':'middle'} 
                      ),
              ]), 
            ]),    
            html.H3("TIMELINE BY PRODUCT", className="display-6", style={'textAlign':'center','font-weight':'bold','backgroundColor':'#fd624f','opacity':'0.6'}),  
            dcc.Graph(
                id = 'marginal-plot',
                figure = fig
            ),
            html.H3("FINAL SHOPPING LIST", className="display-6", style={'textAlign':'center','font-weight':'bold','backgroundColor':'#fd624f','opacity':'0.6'}),
            dbc.Row([
              dbc.Col([           
                dcc.Graph(
                figure = fig3
            #html.P(
             #   "Sorted Shopping list: {}".format(sorted_shopping_list), className="lead"
                ),
            ]),
              dbc.Col([
                dbc.Alert(
                "Estimated time for final shopping list: {}".format(engine.get_estimated_shoping_time(sorted_shopping_list)), className="display-5", color="warning"
              ),
              ]),
            ]),
        ]
        return content
    return ""


if __name__ == "__main__":
    app.run_server(port=5000)
