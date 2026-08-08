import pandas as pd


def cost_sales_scatter_data(product_df):
    df = product_df.copy()
    df['Cost per Unit'] = df['Total_Cost'] / df['Total_Units']
    df['Sales per Unit'] = df['Total_Sales'] / df['Total_Units']
    return df


def flag_margin_risk(product_df, margin_threshold=30, sales_threshold_pct=50):
    df = product_df.copy()
    sales_cutoff = df['Total_Sales'].quantile(sales_threshold_pct / 100)

    def flag(row):
        if row['Gross Margin %'] < margin_threshold and row['Total_Sales'] >= sales_cutoff:
            return 'Reprice / Cost Renegotiate'
        elif row['Gross Margin %'] < margin_threshold and row['Total_Sales'] < sales_cutoff:
            return 'Discontinuation Review'
        elif row['Gross Margin %'] >= margin_threshold and row['Total_Sales'] >= sales_cutoff:
            return 'Core Performer'
        else:
            return 'Niche / Monitor'

    df['Risk Flag'] = df.apply(flag, axis=1)
    return df
