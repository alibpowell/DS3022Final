# DS3022Final
Final project for data science machine learning

## Data split

The fixed reporting set is in [`Data/reporting/`](Data/reporting/). **Do not open,
explore, preprocess, or use these files until the project's final reporting phase.**
Use only [`Data/development/`](Data/development/) for exploratory analysis,
training, validation, feature selection, and hyperparameter tuning.

Both datasets are time series. The latest 20% is reserved chronologically, using
January 1, 2023 as the shared cutoff to keep the same dates out of development
across both datasets. Rows dated before that cutoff belong to development;
rows on or after it belong to reporting. No rows are shuffled or discarded.

| Dataset | Total rows | Development | Reporting |
| --- | ---: | ---: | ---: |
| Almond monthly data | 180 | 144 | 36 (20%) |
| California weekly DSCI | 784 | 627 | 157 (20.03%) |

The DSCI reporting count is 20% rounded to the nearest whole row. The source
includes one observation in December 2010, which stays in development.

The two CSVs at the repository root are the original full source files, preserved
for provenance. **Do not load those full files for analysis**, because they include
the reserved reporting observations. Start notebooks with the files under
`Data/development/`, and join or aggregate only those development data for now.

Fit imputation, scaling, and other learned transformations on training data only.
Use time-ordered validation within the development period. Freeze the model and
preprocessing choices before using the reporting set for the final evaluation.

[`Data/split_manifest.json`](Data/split_manifest.json) records the cutoff, row
counts, and SHA-256 hashes. [`scripts/create_data_split.py`](scripts/create_data_split.py)
created the split using Python's standard library and refuses to overwrite it.
Reporting CSVs are read-only as a local safeguard; Git does not preserve that
read-only setting, so the holdout rule still applies in other checkouts.
