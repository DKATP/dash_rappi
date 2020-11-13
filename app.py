import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import pandas as pd
from plotly.offline import init_notebook_mode, iplot


from backend import *

#DATA
products = pd.read_csv('./files/product_categories.csv')
sh1 = pd.read_csv('./files/shopper1_fix_pids.csv')
sh2 = pd.read_csv('./files/shopper2_fix_pids.csv')
rt = pd.read_csv('./files/rt_fix_pid.csv')

st.title("Rappi app")
################################################################################################

side_bar = st.sidebar
side_bar.header('Shopping list')


explorer = AppBackend()
categories_ = tuple(explorer.get_random_categories())
my_categories = side_bar.selectbox("Selecciona la categoria", categories_)


selected_products = explorer.get_random_products(category=my_categories)

products_ = side_bar.selectbox("Productos", selected_products)


st.write("La categoria que seleccione es: ", my_categories)
st.write("El producto que seleccione es: ", products_)
# Main page

############################################################################

#BOX-PLOTS
rt = pd.read_csv('./files/rt_fix_pid.csv')
rt["datetime"]=pd.to_datetime(rt["CREATED_AT"])
rt["time"]=rt["datetime"].dt.hour
rt.head(50)
join_test=pd.merge(rt, products, how='inner', on="PRODUCT_ID")
join_test.head()
r0=join_test.groupby(['ORDER_ID']).agg({'time':'max',"CAT1_NAME":"count"})
fig2 = px.box(r0, x="CAT1_NAME", y="time", template="plotly_white")
st.plotly_chart(fig2)

#CUADRITOS
shoppers = sh1.append(sh2)
shp_cat = shoppers.merge(products, on='PRODUCT_ID')
shp_cat_c=shp_cat.query("ITEM_TIME<3600").copy()
shp_cat_c['prev_item']=shp_cat_c.PICKING_ORDER-1
shp_pairs = (shp_cat.merge(shp_cat_c, left_on=['ORDER_ID','STOREKEEPER_ID','PICKING_ORDER'], right_on=['ORDER_ID','STOREKEEPER_ID','prev_item'])
[['DIA_x','ORDER_ID','PRODUCT_ID_x','CREATED_AT_x','PRODUCT_NAME_x','PICKING_ORDER_x','CAT1_NAME_x','CAT2_NAME_x','CAT3_NAME_x','PRODUCT_ID_y',
  'CREATED_AT_y','PICKING_ORDER_y','ITEM_TIME_y','PRODUCT_NAME_y','CAT1_NAME_y','CAT2_NAME_y','CAT3_NAME_y']])
cat1_shop = pd.DataFrame(shp_pairs.groupby(['CAT1_NAME_x','CAT1_NAME_y']).ITEM_TIME_y.mean()).reset_index().pivot(index='CAT1_NAME_x',columns='CAT1_NAME_y',values='ITEM_TIME_y')
dats = pd.DataFrame(shp_pairs.groupby(['CAT1_NAME_x','CAT1_NAME_y']).agg({'ITEM_TIME_y':['mean','count']}))
filt_dats=dats[dats[('ITEM_TIME_y','count')]>30].reset_index().pivot(index='CAT1_NAME_x',columns='CAT1_NAME_y',values=('ITEM_TIME_y','mean'))

fig3 = px.imshow(filt_dats, template="plotly_white")
st.plotly_chart(fig3)

#BAR PLOTS
g1=products.groupby(by=["CAT1_NAME"]).agg({"PRODUCT_NAME":"count"}).sort_values(by="PRODUCT_NAME", ascending=False)
g1.reset_index(inplace=True)
fig4 = px.bar(g1, x='CAT1_NAME', y='PRODUCT_NAME', template="plotly_white")
fig4.update_xaxes(
        tickangle = 90,
        title_text = "MAIN CATEGORIES",
        title_font = {"size": 10},
        title_standoff = 10)
fig4.update_yaxes(
        title_text = "PRODUCTS",
        title_standoff = 25)
st.plotly_chart(fig4)

#LINEAL PLOT
fig5 = px.line(g1, x='CAT1_NAME', y='PRODUCT_NAME')#, color='CAT1_NAME')
fig5.update_xaxes(
        tickangle = 90,
        title_text = "MAIN CATEGORIES",
        title_font = {"size": 10},
        title_standoff = 10)
fig5.update_yaxes(
        title_text = "PRODUCTS",
        title_standoff = 25)
st.plotly_chart(fig5)

#CUADRITOS 2
rt_cat = rt.merge(products, on='PRODUCT_ID')
rt_cat_c=rt_cat.query("ITEM_TIME<3600").copy()
rt_cat_c['prev_item']=rt_cat_c.PICKING_ORDER-1
rt_pairs = (rt_cat.merge(rt_cat_c, left_on=['ORDER_ID','STOREKEEPER_ID','PICKING_ORDER'], right_on=['ORDER_ID','STOREKEEPER_ID','prev_item'])
[['DIA_x','ORDER_ID','PRODUCT_ID_x','CREATED_AT_x','PRODUCT_NAME_x','PICKING_ORDER_x','CAT1_NAME_x','CAT2_NAME_x','CAT3_NAME_x','PRODUCT_ID_y',
  'CREATED_AT_y','PICKING_ORDER_y','ITEM_TIME_y','PRODUCT_NAME_y','CAT1_NAME_y','CAT2_NAME_y','CAT3_NAME_y']])
cat1_shop_rt = pd.DataFrame(rt_pairs.groupby(['CAT1_NAME_x','CAT1_NAME_y']).ITEM_TIME_y.mean()).reset_index().pivot(index='CAT1_NAME_x',columns='CAT1_NAME_y',values='ITEM_TIME_y')
dats_rt = pd.DataFrame(rt_pairs.groupby(['CAT1_NAME_x','CAT1_NAME_y']).agg({'ITEM_TIME_y':['mean','count']}))
filt_dats_rt=dats_rt[dats_rt[('ITEM_TIME_y','count')]>30].reset_index().pivot(index='CAT1_NAME_x',columns='CAT1_NAME_y',values=('ITEM_TIME_y','mean'))

fig6 = px.imshow(filt_dats_rt, template="plotly_white")
st.plotly_chart(fig5)

#PARETO
join_rt_products=pd.merge(rt, products, how='inner', on="PRODUCT_ID")
join_rt_products.sort_values(by="PRODUCT_ID", ascending=True)
y2=len(join_rt_products)

x2=join_rt_products.groupby("CAT1_NAME").agg({"ORDER_ID":"count"}).sort_values(by="ORDER_ID", ascending=False)
#x2.plot.bar()
x2["Percentage"]=x2["ORDER_ID"].cumsum()/y2
x2=x2.reset_index()

trace1 = dict(type='bar',
    x=x2["CAT1_NAME"],
    y=x2["ORDER_ID"],
    marker=dict(
        color='#2196F3'
    ),
    name='Number of products',
    opacity=0.8
)
trace2 = dict(type='scatter',
    x=x2["CAT1_NAME"],
    y=x2["Percentage"],
    marker=dict(
        color='#263238'
    ),
    line=dict(
        color= '#263238', 
        width= 1.5),
    name='Percentage',
    xaxis='x1', 
    yaxis='y2' 
)
data = [trace1, trace2]
layout = go.Layout(
    title='MARGINAL CONTRIBUTION PER PRODUCT',
    legend= dict(orientation="h"),
    yaxis=dict(
        #range=[0,2625000],
        title='Number of Products',
        titlefont=dict(
            color="#2196F3"
        )
    ),
    yaxis2=dict(
        title='Percentage',
        titlefont=dict(
            color='#263238'
        ),
        #range=[0,105],
        overlaying='y',
        anchor='x',
        side='right'
        )
    )
fig7 = go.Figure(data=data, layout=layout)
st.plotly_chart(fig7)
#iplot(fig7, filename="pareto")


#GANTT CHART
df = pd.DataFrame([
    dict(Task="Job A", Start='2009-01-01', Finish='2009-02-28', Completion_pct=50),
    dict(Task="Job B", Start='2009-03-05', Finish='2009-04-15', Completion_pct=25),
    dict(Task="Job C", Start='2009-02-20', Finish='2009-05-30', Completion_pct=75)
])

fig8 = px.timeline(df, x_start="Start", x_end="Finish", y="Task", color="Completion_pct", template="plotly_white")
fig8.update_yaxes(autorange="reversed")
st.plotly_chart(fig8)


