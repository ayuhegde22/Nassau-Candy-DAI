import pandas as pd


def load_data(path, sheet_name='in'):
    if str(path).lower().endswith('.csv'):
        try:
            df = pd.read_csv(path)
        except UnicodeDecodeError:
            df = pd.read_excel(path, sheet_name=sheet_name)
    else:
        df = pd.read_excel(path, sheet_name=sheet_name)
    return df


def clean_data(df):
    df = df.copy()
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Ship Date'] = pd.to_datetime(df['Ship Date'])

    df = df[df['Sales'] > 0]
    df = df[df['Cost'] >= 0]
    df = df[df['Units'].notna()]
    df = df[df['Units'] > 0]

    df['Division'] = df['Division'].str.strip()
    df['Product Name'] = df['Product Name'].str.strip()
    df['Region'] = df['Region'].str.strip()
    df['State/Province'] = df['State/Province'].str.strip()

    recomputed_profit = df['Sales'] - df['Cost']
    mismatch = (recomputed_profit - df['Gross Profit']).abs() > 0.01
    df.loc[mismatch, 'Gross Profit'] = recomputed_profit[mismatch]

    df = df.drop_duplicates(subset=['Row ID'])

    return df.reset_index(drop=True)


def load_factory_mapping(factories_path, mapping_path):
    factories = pd.read_csv(factories_path)
    mapping = pd.read_csv(mapping_path)
    return mapping.merge(factories, on='Factory', how='left')
