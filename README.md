# Nassau Candy Distributor — Product Line Profitability & Margin Performance Analysis

Product- and division-level profitability analysis, cost diagnostics, and a Streamlit dashboard, built against the "Product Line Profitability & Margin Performance Analysis for Nassau Candy Distributor" project brief.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Streamlit](https://img.shields.io/badge/built%20with-Streamlit-FF4B4B)

## Objectives

- Determine which product lines deliver the highest gross margin
- Determine whether high-sales products are actually profitable
- Measure how profitability varies across product divisions
- Identify products that represent margin risk

## Project structure

```
nassau-candy/
├── app.py                          Streamlit dashboard (4 modules + filters)
├── data/
│   ├── Nassau_Candy_Distributor.xlsx   raw order data (not tracked in git)
│   ├── factories.csv                    factory coordinates (reference data, tracked)
│   └── product_factory_map.csv          product-to-factory mapping (reference data, tracked)
├── outputs/                        computed KPI tables (not tracked in git)
├── src/
│   ├── data_prep.py                 loading, validation, cleaning
│   ├── kpi.py                       gross margin, profit/unit, contribution %, volatility, quadrant classification
│   ├── pareto.py                    80% revenue / profit concentration, geographic concentration
│   ├── cost_diagnostics.py          cost-vs-sales scatter data, margin risk flags
│   └── pipeline.py                  orchestrates the full flow end to end
├── requirements.txt
├── README.md
├── CONTRIBUTING.md
├── LICENSE
└── .gitignore
```

## Setup

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Place the raw file at `data/Nassau_Candy_Distributor.xlsx` (despite the `.csv` name on the original upload, the source file is actually an Excel workbook with sheet `in`; `data_prep.load_data` handles this automatically).

## Running the pipeline

```
cd src
python3 pipeline.py --data ../data/Nassau_Candy_Distributor.xlsx \
                     --factories ../data/factories.csv \
                     --mapping ../data/product_factory_map.csv \
                     --outputs ../outputs
```

## Running the dashboard

```
streamlit run app.py
```

### Dashboard modules
- **Product Profitability Overview** — margin leaderboard, profit-contribution chart, sales-vs-margin bubble chart
- **Division Performance** — revenue vs profit contribution by division, margin distribution box plot
- **Cost vs Margin Diagnostics** — cost-per-unit vs sales-per-unit scatter, margin risk flag table
- **Profit Concentration** — Pareto chart and 80%-threshold metrics, geographic (state-level) sales concentration

### Filters (sidebar, apply across all four tabs)
- Order date range
- Division
- Margin risk threshold (drives the risk-flag logic in Cost vs Margin Diagnostics)
- Product name search

## Methodology

**Data validation/cleaning**: dropped rows with zero/negative Sales, negative Cost, or missing/zero Units (none were found — the dataset was already clean); reconciled any Gross Profit values that didn't equal Sales − Cost (none needed correction); standardized text fields; de-duplicated on Row ID.

**KPIs** (per the brief's definitions):
- Gross Margin % = Gross Profit ÷ Sales
- Profit per Unit = Gross Profit ÷ Units
- Revenue Contribution % = product/division sales ÷ total sales
- Profit Contribution % = product/division profit ÷ total profit
- Margin Volatility = standard deviation of monthly gross margin % per product

**Product classification**: each product is labeled against the median sales and median margin across the current filter — High-Profit/High-Margin, High-Sales/Low-Margin, Low-Sales/High-Margin, or Low-Sales/Low-Profit.

**Risk flags**: products are flagged Core Performer, Niche/Monitor, Reprice/Cost Renegotiate, or Discontinuation Review based on where they sit relative to the margin threshold (adjustable in the dashboard) and the median sales volume.

**Pareto/concentration analysis**: products ranked by revenue and by profit separately, with the cumulative percentage tracked to find the smallest set of products responsible for 80% of each — done independently since a product can be revenue-heavy without being equally profit-heavy.

## Results (full dataset, unfiltered)

**Division performance:**

| Division | Revenue Contribution % | Profit Contribution % | Gross Margin % | Products |
|---|---|---|---|---|
| Chocolate | 92.9% | 95.1% | 67.4% | 5 |
| Other | 6.8% | 4.6% | 44.8% | 3 |
| Sugar | 0.3% | 0.3% | 66.6% | 7 |

**Concentration risk**: the 5 Chocolate Wonka Bar products alone drive both 80% of total revenue and 80% of total profit. "Other" and "Sugar" divisions combined contribute barely 7% of revenue despite holding 10 of the 15 products in the catalog — the business is heavily dependent on a narrow product set.

**Margin risk flag caught a real outlier**: Kazookles (Other division) has a 7.7% gross margin — far below every other product — and is flagged "Reprice / Cost Renegotiate."

**Geographic concentration**: California, New York, and Texas together account for ~40% of total sales.

## Known caveats

- The source file is named `.csv` but is actually an Excel workbook — this is handled in `data_prep.load_data`, but worth knowing if you re-export or re-upload the raw data.
- Margin Volatility came out at essentially zero for every product — each product has a fixed price/cost structure in this dataset, so margin doesn't vary month to month. This is a genuine finding, not a bug, but means the volatility KPI won't surface anything additional on this particular dataset.
- The project brief's conclusion paragraph references "shipping route efficiency," which doesn't match the rest of the brief (product/margin profitability). This looks like a leftover artifact from a different project template and was not built against.
- Ship Date values in the raw data are 2+ years after the corresponding Order Date, which is inconsistent with a real fulfillment timeline — not used in any KPI here, but worth a data-quality conversation with whoever owns the source system before this feeds anything downstream.

## Not yet built

- Research paper (EDA writeup, insights, recommendations)
- Executive summary for stakeholders

Deferred by design, consistent with the churn project — can be produced directly from the Results section above and the CSVs in `outputs/`.

## Contributing

Issues and pull requests are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md) for local setup, project conventions, and how to run the pipeline/dashboard before submitting a change.

## License

Released under the [MIT License](LICENSE).
