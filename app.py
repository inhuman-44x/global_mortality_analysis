import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

df = pd.read_csv('merged_data.csv')

df = df[df['code'].notna()]

df["log_mortality"] = np.log(df["mortality_per_1000"])

# UI Layout
st.set_page_config(layout='wide')
st.title("Global Mortality Analysis")

# Sidebar filters
st.sidebar.header("Filters")

year = st.sidebar.slider(
    "Select Year",
    int(df['year'].min()),
    int(df['year'].max()),
    int(df['year'].max())
)

metric = st.sidebar.selectbox(
    "Select Metric",
    ["mortality_per_1000", "log_mortality"]
)

# Map
df_year = df[df['year'] == year]

fig_map = px.choropleth(
    df_year,
    locations = 'code',
    color = metric,
    hover_name = 'entity',
    hover_data = {
        "gdp_per_capita" : ":.0f",
        "life_exp" : ":.1f",
        "mortality_per_1000" : ":.2f"
    },
    color_continuous_scale = 'blues',
    range_color = (df[metric].min(), df[metric].quantile(0.95))
)

fig_map.update_layout(
    height = 500,
    margin = dict(l = 0, r = 0, t = 40, b = 0),
    coloraxis_colorbar = dict(
        title = 'Mortality rate',
        orientation = 'h',
        x = 0.5,
        xanchor = 'center',
        y = -0.15
    )
)

fig_map.update_geos(
    projection_type = "natural earth",
    showcoastlines = True,
    showland = True,
    showframe = False
)

st.plotly_chart(fig_map, use_container_width=True)

# Country selection
countries = df['entity'].unique()

selected_country = st.selectbox(
    'Select country for a detailed view',
    sorted(countries)
)

country_df = df[df['entity'] == selected_country]

# Time series
col1, col2 = st.columns([2,1])

with col1:
    fig_line = px.line(
        country_df,
        x = 'year',
        y = 'mortality_per_1000',
        title=f"{selected_country} - Mortality Trend"
    )
    
    st.plotly_chart(fig_line, use_container_width=True)

with col2:
    country_data = country_df[country_df['year'] == year]
    
    st.subheader(selected_country)
    
    if not country_data.empty:
        st.metric(
            'Mortality (per 1000)',
            f"{country_data['mortality_per_1000'].values[0]:.2f}"
        )

        st.metric(
            "GDP per Capita",
            f"{country_data['gdp_per_capita'].values[0]:,.0f}"
        )

        st.metric(
            "Life Expectancy",
            f"{country_data['life_exp'].values[0]:.1f}"
        )

# Scatterplot

st.subheader('GDP vs Mortality')

fig_scatter = px.scatter(
    df_year,
    x = 'gdp_per_capita',
    y = metric,
    hover_name = 'entity',
    trendline= 'lowess',
    log_x = True
)

st.plotly_chart(fig_scatter, use_container_width=True)