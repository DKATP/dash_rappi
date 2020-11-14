import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import base64

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
    "run": None,
    "clean": None

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
        html.Img(src='/content/dash_rappi/Captura.png'),
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
            "", className="lead", id="user-msg"
        ),
        dcc.Graph(
            id = 'shopping-list',
            figure = ff.create_table(pd.DataFrame({"Shopping List":["Please add at least 3 products"]}))
        ),
        dbc.Row([ 

          dbc.Row([

              dbc.Col([
                  html.Button("Optimize Order",id='run-btn',disabled=False, style={'margin-top':'20px','margin-left':'40px', 'padding': '20px', 'width': '180px', 'font-weight':'bold'}),
              ]),
              dbc.Col([
                  html.Button("New Order",id='clean-btn',disabled=False, style={'margin-top':'20px','margin-left':'30px', 'padding': '20px', 'width': '150px', 'font-weight':'bold'}),

              
              ]),
          ]),    
          dbc.Row([  
                  dbc.Nav(
                      [
                          dbc.NavLink("Product Category Analysis", href="/page-1", id="page-1-link", style={'margin-left':'130px', 'font-weight':'bold'}),
                  #         dbc.NavLink("Page 2", href="/page-2", id="page-2-link"),
                  #         dbc.NavLink("Page 3", href="/page-3", id="page-3-link"),
                      ],
                  #     vertical=True,
                  #     pills=True,
                  ),


          ]),
        ], style={'border': '3px solid black', 'border-radius': '8px','margin-top':'100px'}),  
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


# # this callback uses the current pathname to set the active state of the
# # corresponding nav link to true, allowing users to tell see page they are on
#@app.callback(
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
    [Output('shopping-list', 'figure'), Output('user-msg', 'children'), Output('run-btn', 'disabled')],
    [Input('add-btn', 'n_clicks'),Input('products-dropdown', 'value'),Input('clean-btn', 'n_clicks')]
)
def update_shopping_list(n_clicks,value,n_clicks_clean):
    global global_n_clicks, shopping_list

    if global_n_clicks["add"] == n_clicks or value == "Seleccione un Producto":
        if global_n_clicks["clean"] != n_clicks_clean:
            global_n_clicks["clean"] = n_clicks_clean
            shopping_list = []
            fig =  ff.create_table(pd.DataFrame({"SHOPPING LIST":["Please add at least 3 products"]}))
            return fig,"", len(shopping_list) <= 2

        if len(shopping_list) == 0:
            fig =  ff.create_table(pd.DataFrame({"SHOPPING LIST":["Please add at least 3 products"]}))
        else:
            df = pd.DataFrame({"SHOPPING LIST":shopping_list})
            fig =  ff.create_table(df)
        return fig,"", len(shopping_list) <= 2
    else:
        global_n_clicks["add"] = n_clicks
        if value in shopping_list:
            df = pd.DataFrame({"SHOPPING LIST":shopping_list})
            print(df)
            fig =  ff.create_table(df)

            return fig,"Please select a different product", len(shopping_list) <= 2
        else:        
            shopping_list.append(value)
            fig =  ff.create_table(pd.DataFrame({"SHOPPING LIST":shopping_list}))
            return fig,"", len(shopping_list) <= 2

@app.callback(
    Output('page-content', 'children'),
    [Input('run-btn', 'n_clicks'),Input('run-btn', 'disabled'),Input("url", "pathname")]
)
def optimize(n_clicks,disabled,pathname):
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
            html.H3("ORDER RESUME", className="display-6", style={'textAlign':'center','font-weight':'bold','backgroundColor':'#fed8b1'}),
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
              ], style={'border': '2px solid black', 'border-radius': '8px','margin-right':'400px','margin-left': '400px', 'margin-bottom':'30px','background-color':'lightyellow'}),
            ]),
            html.H3("INITIAL SHOPPING LIST", className="display-6", style={'textAlign':'center','font-weight':'bold','backgroundColor':'#fed8b1'}),
            dbc.Row([  
              dbc.Col([ 
                  dcc.Graph(
                      figure = fig2
                  ),
              ]),           
              dbc.Col([
                  dbc.Alert(
                      "Estimated picking time: {}".format(description["estimated_time"]), className="display-4.5", color="primary", style={'backgroundColor':'#ff7152','textAlign':'center','font-weight':'bold'} 
                      ),
              ], style={'margin-top':'100px','margin-bottom': '50px','margin-right':'50px','margin-left':'50px'}), 
            ], style={'margin-bottom':'30px'}),    
            html.H3("TIMELINE BY PRODUCT", className="display-6", style={'textAlign':'center','font-weight':'bold','backgroundColor':'#fed8b1'}),  
            dcc.Graph(
                id = 'marginal-plot',
                figure = fig
            ),
            html.H3("FINAL SHOPPING LIST", className="display-6", style={'textAlign':'center','font-weight':'bold','backgroundColor':'#fed8b1'}),
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
                "Estimated time for final shopping list: {}".format(engine.get_estimated_shoping_time(sorted_shopping_list)), className="display-4.5", color="primary", style={'backgroundColor':'#bfff52','textAlign':'center','font-weight':'bold'} 
              ),
              ], style={'margin-top':'100px','margin-bottom': '50px','margin-right':'50px','margin-left':'50px'}),
            ]),
        ]
        return content

    if pathname == "/cat_analysis":
        return "Graficas"
    return ""


if __name__ == "__main__":
    app.run_server(port=5000)
