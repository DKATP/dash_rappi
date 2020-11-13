import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

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
global_n_clicks  = 0

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
            "Select a Product", className="lead", id="shopping-list"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Page 1", href="/page-1", id="page-1-link"),
                dbc.NavLink("Page 2", href="/page-2", id="page-2-link"),
                dbc.NavLink("Page 3", href="/page-3", id="page-3-link"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


# this callback uses the current pathname to set the active state of the
# corresponding nav link to true, allowing users to tell see page they are on
@app.callback(
    [Output(f"page-{i}-link", "active") for i in range(1, 4)],
    [Input("url", "pathname")],
)
def toggle_active_links(pathname):
    if pathname == "/":
        # Treat page 1 as the homepage / index
        return True, False, False
    return [pathname == f"/page-{i}" for i in range(1, 4)]


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname in ["/", "/page-1"]:
        return html.P("This is the content of page 1!")
    elif pathname == "/page-2":
        return html.P("This is the content of page 2. Yay!")
    elif pathname == "/page-3":
        return html.P("Oh cool, this is page 3!")
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )

@app.callback(
    Output('products-dropdown', 'options'),
    [Input('categories-dropdown', 'value')]
)
def update_output(category):
    print(category)
    products = engine.get_random_products(category)
    return [{"label":product,"value":product} for product in products]

@app.callback(
    Output('shopping-list', 'children'),
    [Input('add-btn', 'n_clicks'),Input('products-dropdown', 'value')]
)
def update_shopping_list(n_clicks,value):
    global global_n_clicks

    if global_n_clicks == n_clicks or value == 'Seleccione un Producto':
        return ""
    else:
        global_n_clicks = n_clicks
        if value in shopping_list:
            return "Seleccione un producto diferente"
        else:        
            shopping_list.append(value)
            print(shopping_list)
            return "Producto Agregado"



if __name__ == "__main__":
    app.run_server(port=5000)