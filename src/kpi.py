import pandas as pd


def add_row_kpis(df):
    df = df.copy()
    df['Gross Margin %'] = df['Gross Profit'] / df['Sales'] * 100
    df['Profit per Unit'] = df['Gross Profit'] / df['Units']
    return df


def product_kpis(df):
    total_sales = df['Sales'].sum()
    total_profit = df['Gross Profit'].sum()

    grouped = df.groupby('Product Name').agg(
        Division=('Division', 'first'),
        Total_Sales=('Sales', 'sum'),
        Total_Units=('Units', 'sum'),
        Total_Cost=('Cost', 'sum'),
        Total_Profit=('Gross Profit', 'sum'),
        Order_Count=('Order ID', 'nunique'),
    ).reset_index()

    grouped['Gross Margin %'] = grouped['Total_Profit'] / grouped['Total_Sales'] * 100
    grouped['Profit per Unit'] = grouped['Total_Profit'] / grouped['Total_Units']
    grouped['Revenue Contribution %'] = grouped['Total_Sales'] / total_sales * 100
    grouped['Profit Contribution %'] = grouped['Total_Profit'] / total_profit * 100

    monthly = df.copy()
    monthly['YearMonth'] = monthly['Order Date'].dt.to_period('M')
    monthly_margin = monthly.groupby(['Product Name', 'YearMonth']).apply(
        lambda g: g['Gross Profit'].sum() / g['Sales'].sum() * 100 if g['Sales'].sum() > 0 else None,
        include_groups=False
    ).reset_index(name='monthly_margin')
    volatility = monthly_margin.groupby('Product Name')['monthly_margin'].std().reset_index()
    volatility.columns = ['Product Name', 'Margin Volatility']

    grouped = grouped.merge(volatility, on='Product Name', how='left')

    return grouped.sort_values('Total_Profit', ascending=False).reset_index(drop=True)


def classify_products(product_df, margin_median=None, sales_median=None):
    df = product_df.copy()
    if margin_median is None:
        margin_median = df['Gross Margin %'].median()
    if sales_median is None:
        sales_median = df['Total_Sales'].median()

    def label(row):
        high_sales = row['Total_Sales'] >= sales_median
        high_margin = row['Gross Margin %'] >= margin_median
        if high_sales and high_margin:
            return 'High-Profit / High-Margin'
        elif high_sales and not high_margin:
            return 'High-Sales / Low-Margin'
        elif not high_sales and not high_margin:
            return 'Low-Sales / Low-Profit'
        else:
            return 'Low-Sales / High-Margin'

    df['Quadrant'] = df.apply(label, axis=1)
    return df


def division_kpis(df):
    total_sales = df['Sales'].sum()
    total_profit = df['Gross Profit'].sum()

    grouped = df.groupby('Division').agg(
        Total_Sales=('Sales', 'sum'),
        Total_Units=('Units', 'sum'),
        Total_Cost=('Cost', 'sum'),
        Total_Profit=('Gross Profit', 'sum'),
        Order_Count=('Order ID', 'nunique'),
        Product_Count=('Product Name', 'nunique'),
    ).reset_index()

    grouped['Gross Margin %'] = grouped['Total_Profit'] / grouped['Total_Sales'] * 100
    grouped['Revenue Contribution %'] = grouped['Total_Sales'] / total_sales * 100
    grouped['Profit Contribution %'] = grouped['Total_Profit'] / total_profit * 100
    grouped['Revenue-Profit Imbalance'] = grouped['Revenue Contribution %'] - grouped['Profit Contribution %']

    return grouped.sort_values('Total_Profit', ascending=False).reset_index(drop=True)
