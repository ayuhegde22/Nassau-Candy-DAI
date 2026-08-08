import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from data_prep import load_data, clean_data, load_factory_mapping
from kpi import add_row_kpis, product_kpis, classify_products, division_kpis
from pareto import products_for_80_percent, geographic_concentration
from cost_diagnostics import cost_sales_scatter_data, flag_margin_risk

st.set_page_config(page_title='Nassau Candy — Profitability Analysis', layout='wide')

DATA_PATH = 'data/Nassau_Candy_Distributor.xlsx'
FACTORIES_PATH = 'data/factories.csv'
MAPPING_PATH = 'data/product_factory_map.csv'


@st.cache_data
def load_base_data():
    df = load_data(DATA_PATH)
    df = clean_data(df)
    df = add_row_kpis(df)
    return df


@st.cache_data
def load_factory_data():
    return load_factory_mapping(FACTORIES_PATH, MAPPING_PATH)


df = load_base_data()
factory_map = load_factory_data()

st.title('Product Line Profitability & Margin Performance')
st.caption('Nassau Candy Distributor')

st.sidebar.header('Filters')

min_date, max_date = df['Order Date'].min().date(), df['Order Date'].max().date()
date_range = st.sidebar.date_input('Order date range', value=(min_date, max_date), min_value=min_date, max_value=max_date)

divisions = st.sidebar.multiselect('Division', options=sorted(df['Division'].unique()), default=sorted(df['Division'].unique()))

margin_threshold = st.sidebar.slider('Margin risk threshold (%)', 0, 100, 30)

search_term = st.sidebar.text_input('Product search')

filtered = df.copy()
if len(date_range) == 2:
    start, end = date_range
    filtered = filtered[(filtered['Order Date'].dt.date >= start) & (filtered['Order Date'].dt.date <= end)]
if divisions:
    filtered = filtered[filtered['Division'].isin(divisions)]
if search_term:
    filtered = filtered[filtered['Product Name'].str.contains(search_term, case=False, na=False)]

if filtered.empty:
    st.warning('No records match the current filters.')
    st.stop()

product_df = product_kpis(filtered)
product_df = classify_products(product_df)
product_df = cost_sales_scatter_data(product_df)
product_df = flag_margin_risk(product_df, margin_threshold=margin_threshold)
division_df = division_kpis(filtered)

tab1, tab2, tab3, tab4 = st.tabs([
    'Product Profitability Overview', 'Division Performance', 'Cost vs Margin Diagnostics', 'Profit Concentration'
])

with tab1:
    st.subheader('Margin Leaderboard')
    st.dataframe(
        product_df[['Product Name', 'Division', 'Total_Sales', 'Total_Profit', 'Gross Margin %', 'Profit per Unit', 'Quadrant']]
        .sort_values('Gross Margin %', ascending=False),
        use_container_width=True
    )

    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.bar(
            product_df.sort_values('Profit Contribution %', ascending=True),
            x='Profit Contribution %', y='Product Name', orientation='h',
            title='Profit Contribution by Product', color='Division'
        )
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        fig2 = px.scatter(
            product_df, x='Total_Sales', y='Gross Margin %', size='Total_Profit',
            color='Quadrant', hover_name='Product Name', title='Sales vs Margin (bubble = profit)'
        )
        st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.subheader('Division Performance')
    st.dataframe(division_df, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        fig3 = go.Figure()
        fig3.add_bar(x=division_df['Division'], y=division_df['Revenue Contribution %'], name='Revenue %')
        fig3.add_bar(x=division_df['Division'], y=division_df['Profit Contribution %'], name='Profit %')
        fig3.update_layout(barmode='group', title='Revenue vs Profit Contribution by Division')
        st.plotly_chart(fig3, use_container_width=True)
    with col2:
        fig4 = px.box(
            product_df, x='Division', y='Gross Margin %', points='all',
            title='Margin Distribution by Division', hover_data=['Product Name']
        )
        st.plotly_chart(fig4, use_container_width=True)

with tab3:
    st.subheader('Cost vs Margin Diagnostics')
    fig5 = px.scatter(
        product_df, x='Cost per Unit', y='Sales per Unit', color='Risk Flag',
        size='Total_Sales', hover_name='Product Name', title='Cost per Unit vs Sales per Unit'
    )
    fig5.add_shape(type='line', x0=0, y0=0, x1=product_df['Cost per Unit'].max(), y1=product_df['Cost per Unit'].max(),
                    line=dict(dash='dash', color='gray'))
    st.plotly_chart(fig5, use_container_width=True)

    st.subheader('Margin Risk Flags')
    st.dataframe(
        product_df[['Product Name', 'Division', 'Gross Margin %', 'Total_Sales', 'Risk Flag']]
        .sort_values('Gross Margin %'),
        use_container_width=True
    )

with tab4:
    st.subheader('Profit Concentration (Pareto)')
    n_rev, pct_rev, pareto_rev = products_for_80_percent(product_df, 'Total_Sales')
    n_profit, pct_profit, pareto_profit = products_for_80_percent(product_df, 'Total_Profit')

    col1, col2 = st.columns(2)
    col1.metric('Products driving 80% of revenue', f'{n_rev} of {len(product_df)}', f'{pct_rev:.0f}% of catalog')
    col2.metric('Products driving 80% of profit', f'{n_profit} of {len(product_df)}', f'{pct_profit:.0f}% of catalog')

    fig6 = go.Figure()
    fig6.add_bar(x=pareto_profit['Product Name'], y=pareto_profit['Total_Profit'], name='Profit')
    fig6.add_scatter(x=pareto_profit['Product Name'], y=pareto_profit['cumulative_pct'], name='Cumulative %', yaxis='y2')
    fig6.update_layout(
        title='Profit Pareto', yaxis=dict(title='Profit'),
        yaxis2=dict(title='Cumulative %', overlaying='y', side='right', range=[0, 100])
    )
    st.plotly_chart(fig6, use_container_width=True)

    st.subheader('Geographic Concentration (Sales by State)')
    state_conc = geographic_concentration(filtered, 'State/Province', 'Sales')
    st.dataframe(state_conc.head(15), use_container_width=True)
