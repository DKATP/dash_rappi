import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc


app = dash.Dash()
app.title= "Rappi app"
app.layout = html.Div([
    html.Div([
    html.Img(src = app.get_asset_url("rappi-logo1.png"),
        className = 'main-logo'
    ),
    html.H1("Optimizing groceries picking time Dashboard", className = 'main-title')
    ]),
    html.Br(),
    html.Br(),

    # Optimization sample
     html.Div([
        html.H2("Optimization sample"),
        html.Br(),
        html.Img(src = app.get_asset_url("1.jpg"),
        style = {"height": "20%", "width":"20%"}),
        html.Img(src = app.get_asset_url("2.jpg"),
        className= "img2"),
        html.Img(src = app.get_asset_url("3.jpg"),
        className= "img3")
    ], className = 'div-general'),

    html.Br(),

    # Descriptive statistics
    html.Div([
        html.H2("Dataset Descriptive Statistics"),
         html.Br(),
         html.Img(src = app.get_asset_url("4.jpg"),
         style = {"height": "30%", "width":"30%"}),
         html.Img(src = app.get_asset_url("5.jpg"),
          className= "img5"),
         html.Img(src = app.get_asset_url("6.jpg"),
          className= "img6")
    ], className = 'div-general'),

    html.Br(),

    # Product Category Analyisis
    html.Div([
        html.H2("Product Category analysis"),
        html.Br(),
        html.Img(src = app.get_asset_url("7.jpg"),
        style = {"height": "40%", "width":"40%"}),
        html.Img(src = app.get_asset_url("8.jpg"),
        className= "img8")

    ], className = 'div-general'),

    html.Div([
                html.Img(
                    src=app.get_asset_url("correlation-1.png"),
                    style={'height': '10%',
                            'width': '35%',
                            'padding-bottom': '1%',
                            'padding-right': '1%',
                            'right': '0%',
                            'bottom':'0%',
                            'position':'relative'
                        
                    })

    ])
])
           

if __name__ == '__main__':
    app.run_server(debug = True, 
                    port = 5000)