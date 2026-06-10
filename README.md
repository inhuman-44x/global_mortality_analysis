# Global Mortality Analysis

An interactive Streamlit dashboard for exploring global mortality trends, demographic indicators, and long-term forecasting using publicly available health and socioeconomic data.

## Overview

This is a data visualization and forecasting project designed to help public health analysts, researchers, and data enthusiasts explore historical mortality patterns across countries and regions.

The dashboard combines mortality data with key demographic and economic indicators, allowing users to examine relationships between mortality rates, population dynamics, life expectancy, and economic development over time.

## Features

* Interactive visualizations of global mortality trends
* Country-level and temporal exploration of mortality patterns
* Descriptive statistical summaries and trend analysis
* Forecasting of future mortality rates using Exponential Smoothing (ETS)
* Interactive dashboard built with Streamlit and Plotly

## Data Sources

The project uses publicly available datasets from: **Our World in Data (OWID)**

### Coverage

* **Time period:** 1950–2022
* **Geographic scope:** Global (166 Countries)

## Methodology

### Data Preparation

* Data integration from multiple OWID datasets
* Cleaning and preprocessing of missing and inconsistent records
* Creation of a consolidated analytical dataset

### Analysis

The project focuses on descriptive analysis and visual exploration of mortality trends, including:

* Historical mortality patterns
* Cross-country comparisons
* Long-term trend assessment

### Forecasting

Future mortality rates are projected using the Exponential Smoothing (ETS) model, providing a time-series forecasting framework for trend estimation.

## Technology Stack

* Python
* Streamlit
* Pandas
* NumPy
* Scikit-learn
* Plotly
* Matplotlib

## Live Dashboard

**Streamlit App:**
https://globalmortalityanalysis-mxtsbbfus5escnbzhnvwrx.streamlit.app/

## Future Improvements

* Compare ETS with alternative forecasting approaches
* Country-specific forecasting models
* Forecast confidence intervals and uncertainty visualization
* Additional public health indicators
* Enhanced filtering and dashboard customization
