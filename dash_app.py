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


app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP], title="RappiProject")

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
            html.H3("Select your products", className="display-5.5", style={'margin-top':'50px', 'padding-bottom': '5px','font-weight':'bold'}),
          ], width={"size": 9, "order": "first"}),
          dbc.Col([
            html.Img(src=app.get_asset_url('favicon.ico'), style={"height" : "50%", 'padding-bottom': '5px'}),
          ], width={"size": 3, "order": "last"}),
        ], style={'height': '100px', 'margin-top':'-40px'}),  
        
        html.Hr(),
        html.P(
            "Please put together your shopping list with the products available below", className="lead"
        ),
        html.P(
            "Select a Category", className="lead", style={'font-weight':'bold', "margin-top": "1rem", "margin-bottom": "0rem"}
        ),
        dcc.Dropdown(
            id='categories-dropdown',
            style={"color": "#777777"},
            options=[ 
                {'label': category, 'value': category} for category in engine.get_random_categories()
            ],
            value='Seleccione una categoria'
        ),
        html.P(
            "Select a Product", className="lead", style={'font-weight':'bold', "margin-top": "1rem", "margin-bottom": "0rem"}
        ),
        dcc.Dropdown(
            id='products-dropdown',
            style={"color": "#777777"},
            options=[],
            value='Seleccione un Producto'
        ),
        html.Button("Add Product",id='add-btn',disabled=False, style={"margin-top": "2rem", "margin-bottom": "1rem", "margin-left": "15px", "padding":"15px", 'font-weight':'bold', "width": "180px", 'border-radius': "1rem", "border":"none", "background-color":"#FFFFFF","color":"rgb(253,98,79)"}),
        html.P(
            "", className="lead", id="user-msg"
        ),
        dcc.Graph(
            id = 'shopping-list',
            figure = ff.create_table(pd.DataFrame({"Shopping List":["Please add at least 3 products"]}),colorscale=[[0, '#444444'],[.5, '#ffffff'],[1, '#ffffff']])
        ),
        dbc.Row([ 

          dbc.Row([

              dbc.Col([
                  html.Button("Send",id='run-btn',disabled=False, style={'margin-top':'20px','margin-left':'30px', 'padding': '15px', 'width': '180px', 'font-weight':'bold', 'border-radius': "1rem", "border":"none", "background-color":"#FFFFFF","color":"rgb(253,98,79)"}),
              ]),
              dbc.Col([
                  html.Button("Clean",id='clean-btn',disabled=False, style={'margin-top':'20px','margin-left':'30px', 'padding': '15px', 'width': '180px', 'font-weight':'bold', 'border-radius': "1rem", "border":"none", "background-color":"#FFFFFF", "color":"rgb(253,98,79)"}),

              
              ]),
          ]),    
          dbc.Row([  
                  dbc.Nav(
                      [
                          dbc.NavLink("Product Category Analysis", href="/cat_analysis", id="page-1-link", style={'margin-top':'1rem','margin-left':'130px', 'font-weight':'bold', "color": "#ffffff"})
                      ],
                  ),


          ]),
        ], style={'margin-top':'1rem'}),#'border': '3px solid black', 'border-radius': '8px',}),  
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div([
                    html.Img(src=app.get_asset_url('front_page.png'), style={"display": "block","margin-left": "auto","margin-right": "auto", "padding":"15% 0"})
                   ],
                   id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

@app.callback(
    Output('products-dropdown', 'options'),
    [Input('categories-dropdown', 'value')]
)
def update_output(category):
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
            fig =  ff.create_table(pd.DataFrame({"SHOPPING LIST":["Please add at least 3 products"]}),colorscale=[[0, '#444444'],[.5, '#ffffff'],[1, '#ffffff']])
            return fig,"", len(shopping_list) <= 2

        if len(shopping_list) == 0:
            fig =  ff.create_table(pd.DataFrame({"SHOPPING LIST":["Please add at least 3 products"]}),colorscale=[[0, '#444444'],[.5, '#ffffff'],[1, '#ffffff']])
        else:
            df = pd.DataFrame({"SHOPPING LIST":shopping_list})
            fig =  ff.create_table(df,colorscale=[[0, '#444444'],[.5, '#ffffff'],[1, '#ffffff']])
        return fig,"", len(shopping_list) <= 2
    else:
        global_n_clicks["add"] = n_clicks
        if value in shopping_list:
            df = pd.DataFrame({"SHOPPING LIST":shopping_list})
            fig =  ff.create_table(df,colorscale=[[0, '#444444'],[.5, '#ffffff'],[1, '#ffffff']])

            return fig,"Please select a different product", len(shopping_list) <= 2
        else:        
            shopping_list.append(value)
            fig =  ff.create_table(pd.DataFrame({"SHOPPING LIST":shopping_list}),colorscale=[[0, '#444444'],[.5, '#ffffff'],[1, '#ffffff']])
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
        print(shopping_list)
        product_times, cat_map = engine.get_product_times()
        product_categories = engine.get_categories2_from_prods(shopping_list)
        cats_2 = list(product_categories.cat2_name)
        map_cats_filtered = list(cat_map[cat_map['cat2_name'].isin(cats_2)].map_value)
        sorted_shopping_list, prods_picking_time = engine.optimization_answer_processing(shopping_list, map_cats_filtered, product_times, cat_map, product_categories)
        print(sorted_shopping_list)

        fig = px.line(x=list(range(1,len(prods_picking_time)+2)),y=[0]+prods_picking_time,template="plotly_white")
        fig.update_layout(
            yaxis={"title":"Time [s]"},
            font=dict(size=18, color="#444444"),
            xaxis = dict(
                title = "Product",
                tickmode = 'array',
                tickangle=0,
                tickvals = list(range(1,len(prods_picking_time)+2)),
                ticktext = [product[:10] if len(product)>=10 else product for product in sorted_shopping_list]))
        fig.update_traces(line_color='#FD624F')

        df1=pd.DataFrame({'ORDER RECEIVED':shopping_list})
        fig2 =  ff.create_table(df1,colorscale=[[0, '#444444'],[.5, '#ffffff'],[1, '#ffffff']])


        df2=pd.DataFrame({'ORDER SORTED':sorted_shopping_list})
        fig3 =  ff.create_table(df2,colorscale=[[0, '#444444'],[.5, '#ffffff'],[1, '#ffffff']])

        content = [
            html.H3("Order Resume", className="display-5.5", style={'textAlign':'left','font-weight':'bold','backgroundColor':'#ffffff', 'border-bottom-style': 'solid', "color": "#fd624f", "padding-left":"1.5rem","padding-left":"1.5rem","padding-bottom":"1rem","margin-bottom": "1.5rem"}),
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
              ], style={'border-radius': '50px','margin-right':'400px','margin-left': '400px', 'margin-bottom':'30px','background-color':"#777777", "color": "#ffffff", "padding-top": "1rem"}),
            ]),
            html.H3("Final Shopping List", className="display-5.5", style={'textAlign':'left','font-weight':'bold','backgroundColor':'#ffffff', 'border-bottom-style': 'solid', "color": "#fd624f", "padding-left":"1.5rem","padding-left":"1.5rem","padding-bottom":"1rem","margin-bottom": "1.5rem"}),
            dbc.Row([
              dbc.Col([           
                dcc.Graph(
                figure = fig3
                ),
            ]),
              dbc.Col([
                html.P("Estimated picking time:" ,className="display-4.5", style={'textAlign':'center','font-weight':'bold', "margin-bottom": "0px"}), 
                dbc.Alert(
                "{} seg".format(int(sum(prods_picking_time))), className="display-3", color="primary", style={'backgroundColor':'#ffffff','border-color':'#ffffff','textAlign':'center','font-weight':'bold', 'height':'100px', "color":"#008540", "padding-bottom": "0px"}
              ),
              ], style={'margin-top':'12px'}),
            ], style={'margin-bottom':'30px'}),
            html.H3("Timeline By Product", className="display-5.5", style={'textAlign':'left','font-weight':'bold','backgroundColor':'#ffffff', 'border-bottom-style': 'solid', "color": "#fd624f", "padding-left":"1.5rem","padding-left":"1.5rem","padding-bottom":"1rem","margin-bottom": "1.5rem"}),  
            dcc.Graph(
                id = 'marginal-plot',
                figure = fig
            ),
        ]
        return content

    if pathname == "/cat_analysis":
        if pathname == "/cat_analysis":
            heatmap = engine.get_eda()
            fig5 = px.imshow(heatmap, labels={"x":"Current Category","y":"Next Catedory","color":"Time [s]"},x = list(heatmap.columns),y = list(heatmap.columns))
        return dcc.Graph(figure = fig5, style={'height': '800px'})
    return html.Img(src=app.get_asset_url('front_page.png'), style={"display": "block","margin-left": "auto","margin-right": "auto"})


if __name__ == "__main__":
    app.run_server(port=5000)
