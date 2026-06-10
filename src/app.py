# app.py

import streamlit as st
import pandas as pd
import seaborn as sns
import plotly.express as px
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="Global Mortality Intelligence Dashboard",
    layout="wide"
)

sns.set_style("white")


def standard_plot(fig):
    fig.update_layout(height=450)

    left, center, right = st.columns([1, 4, 1])

    with center:
        st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------


@st.cache_data
def load_data():

    deaths = pd.read_csv('data/raw/number-of-deaths.csv')
    pop = pd.read_csv('data/raw/population.csv')
    gdp = pd.read_csv('data/raw/gdp-per-capita-maddison-project-database.csv')
    life_exp = pd.read_csv('data/raw/life-expectancy-unwpp.csv')

    # Rename columns
    deaths = deaths.rename(columns={'Number of deaths, total': 'deaths'})
    pop = pop.rename(columns={'Population': 'population'})
    gdp = gdp.rename(columns={'GDP': 'gdp_per_capita'})
    life_exp = life_exp.rename(columns={'Life Expectancy': 'life_exp'})

    # Lowercase columns
    for df in (deaths, pop, gdp, life_exp):
        df.columns = df.columns.str.lower()

    # Merge
    df = deaths.merge(
        pop,
        on=['entity', 'year', 'code'],
        how='inner'
    ).merge(
        gdp,
        on=['entity', 'year', 'code'],
        how='inner'
    ).merge(
        life_exp,
        on=['entity', 'year', 'code'],
        how='inner'
    )

    # Feature engineering
    df['mortality_rate'] = df['deaths'] / df['population']
    df['mortality_per_1000'] = df['mortality_rate'] * 1000

    return df


df = load_data()

# ---------------------------------------------------
# TITLE
# ---------------------------------------------------

st.title("Global Mortality Intelligence Dashboard")

st.markdown("""
Interactive analysis of global mortality trends, economic indicators,
life expectancy, and forecasting from 1950–2022.
""")

# ---------------------------------------------------
# KPI SECTION
# ---------------------------------------------------

latest_year = df['year'].max()

latest_global = df[df['year'] == latest_year]

global_mortality = (
    latest_global['deaths'].sum() /
    latest_global['population'].sum()
) * 1000

col1, col2, col3, col4 = st.columns(4)

col1.metric("Countries", df['entity'].nunique())
col2.metric("Years Covered", df['year'].nunique())
col3.metric("Latest Global Mortality", f"{global_mortality:.2f}")
col4.metric("Latest Year", latest_year)

# ---------------------------------------------------
# TABS
# ---------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs([
    "Global Overview",
    "Country Analysis",
    "COVID Impact",
    "Forecasting"
])

# ===================================================
# TAB 1 — GLOBAL OVERVIEW
# ===================================================

with tab1:

    st.subheader("Global Mortality Choropleth")

    metric = 'mortality_per_1000'

    fig = px.choropleth(
        df,
        locations='code',
        color=metric,
        hover_name='entity',
        hover_data={
            'year': True,
            'mortality_per_1000': ':.2f',
            'gdp_per_capita': ':.0f',
            'life_exp': ':.1f'
        },
        animation_frame='year',
        color_continuous_scale='Reds'
    )

    fig.update_geos(
        projection_type='natural earth',
        showcoastlines=True,
        showframe=False
    )

    fig.update_layout(
        height=700,
        title='Global Mortality Rate (1950–2022)'
    )

    st.plotly_chart(fig, use_container_width=True)

    # GLOBAL TREND

    st.subheader("Global Mortality Trend")

    global_trend = (
        df.groupby('year')
        .apply(lambda x: (
            x['deaths'].sum() /
            x['population'].sum()
        ) * 1000)
        .reset_index(name='mortality_per_1000')
    )

    fig2 = px.line(
        global_trend,
        x='year',
        y='mortality_per_1000',
        title='Global Mortality Trend'
    )

    fig2.add_vrect(
        x0=2020,
        x1=2022,
        fillcolor="grey",
        opacity=0.25,
        line_width=0
    )

    fig2.update_layout(
        xaxis_title='Year',
        yaxis_title='Mortality per 1000')

    standard_plot(fig2)

# ===================================================
# TAB 2 — COUNTRY ANALYSIS
# ===================================================
with tab2:

    col1, col2 = st.columns(2)

    with col1:
        selected_country = st.selectbox(
            "Select Country",
            sorted(df['entity'].unique()),
            index=sorted(df['entity'].unique()).index('Nigeria')
        )

    with col2:
        year_range = st.slider(
            "Select Year Range",
            int(df['year'].min()),
            int(df['year'].max()),
            (2000, 2022)
        )

    filtered_df = df[
        (df['entity'] == selected_country) &
        (df['year'].between(year_range[0], year_range[1]))
    ]

with tab2:

    st.subheader(f"{selected_country} Analysis")

    # Mortality trend

    fig3 = px.line(
        filtered_df,
        x='year',
        y='mortality_per_1000',
        title=f'{selected_country} Mortality Trend'
    )

    fig3.update_layout(
        width=800,
        height=450,
        xaxis_title='Year',
        yaxis_title='Mortality per 1000'
    )

    standard_plot(fig3)

    # GDP trend

    fig4 = px.line(
        filtered_df,
        x='year',
        y='gdp_per_capita',
        title=f'{selected_country} GDP per Capita Trend'
    )

    fig4.update_layout(
        xaxis_title='Year',
        yaxis_title='GDP per Capita'
    )

    standard_plot(fig4)

    # Life expectancy trend

    fig5 = px.line(
        filtered_df,
        x='year',
        y='life_exp',
        title=f'{selected_country} Life Expectancy Trend'
    )

    fig5.update_layout(
        xaxis_title='Year',
        yaxis_title='Life Expectancy'
    )

    standard_plot(fig5)

    # Summary statistics

    st.subheader("Summary Statistics")

    st.dataframe(
        filtered_df[
            [
                'year',
                'mortality_per_1000',
                'gdp_per_capita',
                'life_exp'
            ]
        ].describe()
    )

# ===================================================
# TAB 3 — COVID IMPACT
# ===================================================

with tab3:

    st.subheader("COVID-19 Impact on Mortality")

    pre_covid = (
        df[(df['year'] >= 2015) & (df['year'] <= 2019)]
        .groupby('entity')['mortality_per_1000']
        .mean()
        .reset_index(name='pre_covid_mr')
    )

    covid = (
        df[(df['year'] >= 2020) & (df['year'] <= 2022)]
        .groupby('entity')['mortality_per_1000']
        .mean()
        .reset_index(name='covid_mr')
    )

    covid_change = pre_covid.merge(
        covid,
        on='entity'
    )

    covid_change['absolute_change'] = (
        covid_change['covid_mr'] -
        covid_change['pre_covid_mr']
    )

    # Top worsening countries
    worst_10 = covid_change.sort_values(
        'absolute_change',
        ascending=False
    ).head(10)

    # Least affected countries
    best_10 = covid_change.sort_values(
        'absolute_change',
        ascending=True
    ).head(10)

    # Combine
    combined = pd.concat([best_10, worst_10])

    # Sort for plotting
    combined = combined.sort_values('absolute_change')

    combined['entity'] = combined['entity'].replace({
        'United Arab Emirates': 'UAE',
        'Central African Republic': 'CAR'})

    # Color groups
    combined['impact'] = combined['absolute_change'].apply(
        lambda x: 'Increase' if x > 0 else 'Decrease'
    )

    fig6 = px.bar(
        combined,
        x='absolute_change',
        y='entity',
        orientation='h',
        color='impact',
        color_discrete_map={
            'Increase': "#3CB7E7",
            'Decrease': "#2ECCC1"
        },
        title='COVID-19 Impact on Mortality Rates (Largest Increases vs Lowest Changes)'
    )

    fig6.update_layout(
        xaxis_title='Change in Mortality Rate per 1,000',
        yaxis_title='Country',
        showlegend=False,
        width=800,
        height=700
    )

    st.plotly_chart(fig6)

# ===================================================
# TAB 4 — FORECASTING
# ===================================================

with tab4:

    st.subheader("Global Mortality Forecast to 2050")

    X = global_trend[['year']]
    y = global_trend['mortality_per_1000']

    forecast_df = pd.DataFrame({
        'year': range(2023, 2051)
    })

    # ETS Forecast

    ets_df = global_trend.set_index(
        pd.to_datetime(global_trend['year'], format='%Y')
    )

    ets_model = ExponentialSmoothing(
        ets_df['mortality_per_1000'],
        trend='add',
        damped_trend=True
    ).fit()

    ets_forecast = ets_model.forecast(28)

    forecast_df['ets_forecast'] = ets_forecast.values

    # Plot

    fig7 = px.line(
        global_trend,
        x='year',
        y='mortality_per_1000',
        title='Global Mortality Forecast to 2050 (ETS Model)'
    )

    # ETS
    fig7.add_scatter(
        x=forecast_df['year'],
        y=forecast_df['ets_forecast'],
        mode='lines',
        name='ETS Forecast'
    )

    fig7.update_layout(
        xaxis_title='Year',
        yaxis_title='Mortality per 1000'
    )

    standard_plot(fig7)

    st.dataframe(forecast_df)
