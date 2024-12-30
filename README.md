# CrossfitGames

This repo is a collection of functions that allow you to collect data from the Crossfit Games leaderboard open API.

You can use this repo to access structured data from the Crossfit Games open API to do analysis on.


## Using the data
You need to join games_info_competitors to games_info_scores if you want to get the names of the competitors.


## Improvements on the roadmap

### Fixing some data quality issues needed for analysis
### Unit testing and data quality testing
### Add all competitions, i.e. regionals, sanctionals, the open etc.
### Include a function that writes the data to a storage account.

## Getting started

Before starting on work with this project, please make sure 


├── LICENSE
├── Makefile           <- Makefile with commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├── external       <- Data from third party sources.
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`.
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
├── src                <- Source code for use in this project.
│   ├── __init__.py    <- Makes src a Python module
│   │
│   ├── data           <- Scripts to download or generate data
│   │   └── make_csv.py
│   │
│
└── tox.ini            <- tox file with settings for running tox; see tox.readthedocs.io

Project base on the https://github.com/drivendata/cookiecutter-data-science template