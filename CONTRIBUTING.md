# Contributing

This started as a self-contained analysis project, but issues and pull requests are welcome — whether that's a bug fix, a new KPI, an additional dashboard view, or a documentation improvement.

## Getting set up

```bash
git clone https://github.com/<your-username>/nassau-candy.git
cd nassau-candy
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

The raw data file (`data/Nassau_Candy_Distributor.xlsx`) is not tracked in git — you'll need to supply your own copy at that path, or point `src/pipeline.py` / `app.py` at a differently located file. `data/factories.csv` and `data/product_factory_map.csv` are reference data and are tracked.

## Project layout

See the [README](README.md#project-structure) for the module breakdown (`data_prep`, `kpi`, `pareto`, `cost_diagnostics`, `pipeline`) and what each one owns.

## Making a change

1. Open an issue first for anything non-trivial (new KPI definitions, dashboard restructuring), so the approach can be agreed on before code is written.
2. Keep new logic in `src/`, with `pipeline.py` orchestrating and `app.py` staying a thin presentation layer over the same functions — avoid duplicating calculation logic between the two.
3. Run the pipeline end-to-end and spot-check the CSVs in `outputs/` before opening a PR:
   ```bash
   cd src
   python3 pipeline.py --data ../data/Nassau_Candy_Distributor.xlsx \
                        --factories ../data/factories.csv \
                        --mapping ../data/product_factory_map.csv \
                        --outputs ../outputs
   ```
4. Launch the dashboard (`streamlit run app.py`) and confirm any affected tab/filter still behaves correctly.
5. Keep pull requests focused — one logical change per PR makes review easier.

## Reporting bugs / requesting features

Open a GitHub issue with:
- What you expected vs. what happened
- Steps to reproduce (including which filters/date ranges, if dashboard-related)
- Python version and OS, if it looks environment-related

## Code style

- Plain, readable pandas — the existing modules favor small, single-purpose functions over long chained pipelines. Match that style.
- No enforced formatter/linter yet; if you'd like to propose one (e.g. `black`, `ruff`), that's a welcome PR on its own.
