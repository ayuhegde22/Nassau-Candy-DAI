import argparse
import pandas as pd

from data_prep import load_data, clean_data, load_factory_mapping
from kpi import add_row_kpis, product_kpis, classify_products, division_kpis
from pareto import products_for_80_percent, geographic_concentration
from cost_diagnostics import cost_sales_scatter_data, flag_margin_risk


def run(data_path, factories_path, mapping_path, outputs_dir):
    df = load_data(data_path)
    df = clean_data(df)
    df = add_row_kpis(df)

    product_df = product_kpis(df)
    product_df = classify_products(product_df)
    product_df = cost_sales_scatter_data(product_df)
    product_df = flag_margin_risk(product_df)

    division_df = division_kpis(df)

    n_products_rev, pct_products_rev, pareto_rev = products_for_80_percent(product_df, 'Total_Sales')
    n_products_profit, pct_products_profit, pareto_profit = products_for_80_percent(product_df, 'Total_Profit')

    state_concentration = geographic_concentration(df, 'State/Province', 'Sales')

    factory_map = load_factory_mapping(factories_path, mapping_path)
    product_with_factory = product_df.merge(
        factory_map[['Product Name', 'Factory', 'Latitude', 'Longitude']],
        on='Product Name', how='left'
    )

    df.to_csv(f'{outputs_dir}/cleaned_orders.csv', index=False)
    product_df.to_csv(f'{outputs_dir}/product_kpis.csv', index=False)
    division_df.to_csv(f'{outputs_dir}/division_kpis.csv', index=False)
    pareto_rev.to_csv(f'{outputs_dir}/pareto_revenue.csv', index=False)
    pareto_profit.to_csv(f'{outputs_dir}/pareto_profit.csv', index=False)
    state_concentration.to_csv(f'{outputs_dir}/state_concentration.csv', index=False)
    product_with_factory.to_csv(f'{outputs_dir}/product_with_factory.csv', index=False)

    print(f'Rows after cleaning: {len(df)}')
    print()
    print('Division KPIs:')
    print(division_df.to_string(index=False))
    print()
    print('Product KPIs (top 5 by profit):')
    print(product_df.head(5)[['Product Name', 'Division', 'Total_Sales', 'Total_Profit', 'Gross Margin %', 'Quadrant', 'Risk Flag']].to_string(index=False))
    print()
    print(f'{n_products_rev} of {len(product_df)} products ({pct_products_rev:.1f}%) drive 80% of revenue')
    print(f'{n_products_profit} of {len(product_df)} products ({pct_products_profit:.1f}%) drive 80% of profit')
    print()
    print('Top 5 states by sales concentration:')
    print(state_concentration.head(5).to_string(index=False))

    return df, product_df, division_df


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', default='data/Nassau_Candy_Distributor.xlsx')
    parser.add_argument('--factories', default='data/factories.csv')
    parser.add_argument('--mapping', default='data/product_factory_map.csv')
    parser.add_argument('--outputs', default='outputs')
    args = parser.parse_args()

    run(args.data, args.factories, args.mapping, args.outputs)
