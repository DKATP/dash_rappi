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
        dbc.Row([ 
          dbc.Col([
            html.H3("Select your products", className="display-5.5", style={'margin-top':'50px', 'padding-bottom': '5px'}),
          ], width={"size": 9, "order": "first"}),
          dbc.Col([
            html.Img(src=app.get_asset_url('favicon.ico'), style={"height" : "60%", 'padding-bottom': '5px'}),
          ], width={"size": 3, "order": "last"}),
        ], style={'height': '100px', 'margin-top':'-40px'}),  
        
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
                  html.Button("SEND LIST",id='run-btn',disabled=False, style={'margin-top':'20px','margin-left':'40px', 'padding': '20px', 'width': '180px', 'font-weight':'bold'}),
              ]),
              dbc.Col([
                  html.Button("New Order",id='clean-btn',disabled=False, style={'margin-top':'20px','margin-left':'30px', 'padding': '20px', 'width': '150px', 'font-weight':'bold'}),

              
              ]),
          ]),    
          dbc.Row([  
                  dbc.Nav(
                      [
                          dbc.NavLink("Product Category Analysis", href="/cat_analysis", id="page-1-link", style={'margin-left':'130px', 'font-weight':'bold'}),
                  #         dbc.NavLink("Page 2", href="/page-2", id="page-2-link"),
                  #         dbc.NavLink("Page 3", href="/page-3", id="page-3-link"),
                      ],
                  #     vertical=True,
                  #     pills=True,
                  ),


          ]),
        ], style={'margin-top':'100px'}),#'border': '3px solid black', 'border-radius': '8px',}),  
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

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

        fig = px.line(x=list(range(1,len(description["marginal_plot"])+1)),y= description["marginal_plot"].values(),template="plotly_white")
        fig.update_layout(yaxis={"title":"Time [s]"},xaxis={"title":"Product", "tick0":0, "dtick":0})

        sorted_shopping_list = engine.sort_shopping_list(shopping_list)
      
        df1=pd.DataFrame({'ORDER RECEIVED':shopping_list})
        fig2 =  ff.create_table(df1)
        #fig.show()

        df2=pd.DataFrame({'ORDER SORTED':sorted_shopping_list})
        fig3 =  ff.create_table(df2)

        content = [
            html.H3("ORDER RESUME", className="display-6", style={'textAlign':'center','font-weight':'bold','backgroundColor':'#fed8b1', 'border-bottom-style': 'solid'}),
            dbc.Row([ 
              dbc.Col([
                html.P(
                    "Number of different products: {}".format(description["n_items"]), className="lead", style={'textAlign':'center','font-weight':'bold'}
                ),
                html.P(
                    "Number of categories L1: {}".format(description["n_cat1"]), className="lead", style={'textAlign':'center','font-weight':'bold'}
                ),
                html.P(
                    "Number of categories L2: {}".format(description["n_cat2"]), className="lead", style={'textAlign':'center','font-weight':'bold'}
                ),
                html.P(
                    "Number of categories L3: {}".format(description["n_cat3"]), className="lead", style={'textAlign':'center','font-weight':'bold'}
                ),
              ], style={'border': '2px solid black', 'border-radius': '8px','margin-right':'400px','margin-left': '400px', 'margin-bottom':'30px','background-color':'lightyellow'}),
            ]),
            html.H3("INITIAL SHOPPING LIST", className="display-6", style={'textAlign':'center','font-weight':'bold','backgroundColor':'#fed8b1', 'border-bottom-style': 'solid'}),
            dbc.Row([  
              dbc.Col([ 
                  dcc.Graph(
                      figure = fig2
                  ),
              ]),           
              dbc.Col([
                  html.P("Estimated picking time:" ,className="display-4.5", style={'textAlign':'center','font-weight':'bold'}), 
                  dbc.Alert(
                      "{}".format(description["estimated_time"]), className="display-3", color="primary", style={'backgroundColor':'#ff7152','textAlign':'center','font-weight':'bold', 'height':'100px'} 
                      ),
              ], style={'margin-top':'60px'}),#,'margin-bottom': '50px','margin-right':'50px','margin-left':'50px'}), 
            ], style={'margin-bottom':'30px'}),    
            html.H3("TIMELINE BY PRODUCT", className="display-6", style={'textAlign':'center','font-weight':'bold','backgroundColor':'#fed8b1', 'border-bottom-style': 'solid'}),  
            dcc.Graph(
                id = 'marginal-plot',
                figure = fig
            ),
            html.H3("FINAL SHOPPING LIST", className="display-6", style={'textAlign':'center','font-weight':'bold','backgroundColor':'#fed8b1', 'border-bottom-style': 'solid'}),
            dbc.Row([
              dbc.Col([           
                dcc.Graph(
                figure = fig3
            #html.P(
             #   "Sorted Shopping list: {}".format(sorted_shopping_list), className="lead"
                ),
            ]),
              dbc.Col([
                html.P("Estimated final picking time:" ,className="display-4.5", style={'textAlign':'center','font-weight':'bold'}), 
                dbc.Alert(
                "{}".format(engine.get_estimated_shoping_time(sorted_shopping_list)), className="display-3", color="primary", style={'backgroundColor':'#bfff52','textAlign':'center','font-weight':'bold', 'height':'100px'} 
              ),
              ], style={'margin-top':'60px'}),
            ]),
        ]
        return content

    if pathname == "/cat_analysis":
        if pathname == "/cat_analysis":
          fig5 = px.imshow(engine.get_eda())
        return dcc.Graph(figure = fig5, style={'height': '800px'})
    return ""


if __name__ == "__main__":
    app.run_server(port=5000)
