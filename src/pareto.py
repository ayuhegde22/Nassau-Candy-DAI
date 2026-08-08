import pandas as pd


def pareto_analysis(product_df, value_col):
    df = product_df.sort_values(value_col, ascending=False).reset_index(drop=True)
    total = df[value_col].sum()
    df['cumulative'] = df[value_col].cumsum()
    df['cumulative_pct'] = df['cumulative'] / total * 100
    df['rank'] = range(1, len(df) + 1)
    return df


def products_for_80_percent(product_df, value_col):
    pareto = pareto_analysis(product_df, value_col)
    cutoff_idx = (pareto['cumulative_pct'] >= 80).idxmax()
    n_products = cutoff_idx + 1
    pct_of_products = n_products / len(pareto) * 100
    return n_products, pct_of_products, pareto


def geographic_concentration(df, group_col='State/Province', value_col='Sales'):
    total = df[value_col].sum()
    grouped = df.groupby(group_col)[value_col].sum().sort_values(ascending=False).reset_index()
    grouped['pct_of_total'] = grouped[value_col] / total * 100
    grouped['cumulative_pct'] = grouped['pct_of_total'].cumsum()
    return grouped
