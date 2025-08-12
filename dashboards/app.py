import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go 
import numpy as np
import yaml

# -----------------------
# Load Data
# -----------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/processed/merged_data.csv", parse_dates=["datetime"])
    df.rename(columns={"datetime": "date"}, inplace=True)  # standardize to 'date'
    return df

df = load_data()

# Load city info from the single source of truth
with open("config/config.yaml", "r") as f:
    config = yaml.safe_load(f)
city_info = config["cities"]


#-----------------------
#Sidebar Filters
#-----------------------
st.sidebar.title("🔍Filters")
cities = st.sidebar.multiselect(
    "🌆 Select Cities",
    df["city"].unique(),
    default=df["city"].unique()
)

start_date, end_date = st.sidebar.date_input(
    "📅 select Date Range",
    [df["date"].min(), df["date"].max()]
)

filtered_df = df[
    (df["city"].isin(cities)) &
    (df["date"] >= pd.to_datetime(start_date)) &
    (df["date"] <= pd.to_datetime(end_date))
]




# -----------------------
# 1️⃣ Geographic Overview
st.title(" Energy & Weather Dashboard")
st.header("1. Geographic Overview")

# Prepare latest data per city
latest_df = df.sort_values("date").groupby("city").tail(1).copy()

# Get % change in usage from yesterday
def get_prev_usage(city, date):
    prev = df[(df["city"] == city) & (df["date"] == date - pd.Timedelta(days=1))]
    return prev["energy_consumption_mw"].values[0] if not prev.empty else np.nan

latest_df["prev_energy"] = latest_df.apply(lambda row: get_prev_usage(row["city"], row["date"]), axis=1)
latest_df["energy_change_pct"] = ((latest_df["energy_consumption_mw"] - latest_df["prev_energy"]) / latest_df["prev_energy"]) * 100

# Add lat/lon
latest_df["lat"] = latest_df["city"].map(lambda x: city_info[x]["lat"])
latest_df["lon"] = latest_df["city"].map(lambda x: city_info[x]["lon"])

# Define high/low energy usage based on average
avg_energy = latest_df["energy_consumption_mw"].mean()
latest_df["usage_level"] = latest_df["energy_consumption_mw"].apply(lambda x: "High" if x > avg_energy else "Low")
latest_df["color"] = latest_df["usage_level"].map({"High": "red", "Low": "green"})

# Custom hover text
latest_df["hover_info"] = latest_df.apply(
    lambda row: f"<b>{row['city'].title()}</b><br>🌡 Avg Temp: {row['avg_temp_f']:.1f}°F<br>⚡ Usage: {row['energy_consumption_mw']:.0f} MW<br>📉 Change: {row['energy_change_pct']:.1f}%<br>🔵 Usage Level: {row['usage_level']}",
    axis=1
)

# Create map

# Coordinates for center of the map (central USA)
map_center = {"lat": 39.8283, "lon": -98.5795}

fig_map = go.Figure()

for _, row in latest_df.iterrows():
    fig_map.add_trace(go.Scattermapbox(
        lat=[row["lat"]],
        lon=[row["lon"]],
        mode='markers+text',
        marker=go.scattermapbox.Marker(
            size=18,
            color=row["color"]
        ),
        text=f"{row['city'].title()}",
        textposition="bottom center",
        hovertemplate=(
            f"<b>{row['city'].title()}</b><br>"
            f"🌡 Avg Temp: {row['avg_temp_f']:.1f}°F<br>"
            f"⚡ Usage: {row['energy_consumption_mw']:.0f} MW<br>"
            f"📉 Change: {row['energy_change_pct']:.1f}%<br>"
            f"🔵 Usage Level: {row['usage_level']}"
        ),
        showlegend=False
    ))

fig_map.update_layout(
    mapbox=dict(
        style="carto-positron",
        center=map_center,
        zoom=2.5
    ),
    height=650,
    margin=dict(l=0, r=0, t=50, b=10),
    title="📍 Latest Energy Use & Weather Conditions by City",
    title_x=0.02,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=0.01,
        xanchor="right",
        x=1
    )
)

# Add a manual legend
fig_map.add_trace(go.Scattermapbox(
    lat=[None],
    lon=[None],
    mode='markers',
    marker=dict(size=12, color='red'),
    name='High Usage'
))

fig_map.add_trace(go.Scattermapbox(
    lat=[None],
    lon=[None],
    mode='markers',
    marker=dict(size=12, color='green'),
    name='Low Usage'
))

st.plotly_chart(fig_map, use_container_width=True)

update_time = latest_df["date"].max().strftime("%B %d, %Y")
st.caption(f"🕒 Last updated: {update_time}")




# -----------------------
# 2️⃣ Time Series Analysis
st.header("2. Time Series Analysis")

# Convert date column if not already
df["date"] = pd.to_datetime(df["date"])

# Filter to last 90 days
last_90 = df["date"].max() - pd.Timedelta(days=90)
recent_df = df[df["date"] >= last_90]

# City selector
city_option = st.selectbox("Select city", ["All Cities"] + sorted(recent_df["city"].unique()))

# Filter by selected city
ts_df = recent_df if city_option == "All Cities" else recent_df[recent_df["city"] == city_option]

# Create figure
fig_ts = go.Figure()

# Plot for each city or selected city
for city in ts_df["city"].unique():
    city_data = ts_df[ts_df["city"] == city]

    fig_ts.add_trace(go.Scatter(
        x=city_data["date"],
        y=city_data["avg_temp_f"],
        mode='lines',
        name=f"{city} Temp",
        yaxis='y1'
    ))

    fig_ts.add_trace(go.Scatter(
        x=city_data["date"],
        y=city_data["energy_consumption_mw"],
        mode='lines',
        name=f"{city} Energy",
        yaxis='y2',
        line=dict(dash='dot')
    ))

# Highlight weekends
weekends = ts_df[ts_df["date"].dt.weekday >= 5]["date"].dt.normalize().unique()
for wd in weekends:
    fig_ts.add_vrect(
        x0=wd,
        x1=wd + pd.Timedelta(days=1),
        fillcolor="gray",
        opacity=0.1,
        line_width=0
    )

# Update layout
fig_ts.update_layout(
    title=dict(
        text=f"Temperature vs Energy Consumption ({city_option}) - Last 90 Days",
        x=0.5,  # Center align
        xanchor='center'
    ),
    xaxis_title="Date",
    yaxis=dict(title="Temperature (°F)"),
    yaxis2=dict(title="Energy Consumption (MW)", overlaying="y", side="right"),
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.25,  # Push it below the chart
        xanchor="center",
        x=0.5
    ),
    hovermode="x unified",
    margin=dict(t=60, b=80)  # Top and bottom padding
)


# Display chart
st.plotly_chart(fig_ts, use_container_width=True)



# 3️⃣ Correlation Analysis
# -----------------------
st.header("3. Correlation Analysis")

corr_df = filtered_df.dropna(subset=["avg_temp_f", "energy_consumption_mw"])

# Scatter plot with regression line
fig_corr = px.scatter(
    corr_df,
    x="avg_temp_f",
    y="energy_consumption_mw",
    color="city",
    hover_data={"date": True, "avg_temp_f": ":.2f", "energy_consumption_mw": ":.2f"},
    trendline="ols",
    title="Temperature vs Energy Consumption (All Cities)"
)

# Extract regression model to get R² and coefficients
results_df = px.get_trendline_results(fig_corr)
model = results_df.iloc[0]["px_fit_results"]
intercept = model.params[0]
slope = model.params[1]
r_squared = model.rsquared
corr_coef = corr_df["avg_temp_f"].corr(corr_df["energy_consumption_mw"])

# Display regression equation + stats
regression_eq = f"y = {slope:.2f}x + {intercept:.2f}"
annotation_text = f"{regression_eq}<br>R² = {r_squared:.2f}<br>r = {corr_coef:.2f}"

fig_corr.add_annotation(
    text=annotation_text,
    xref="paper", yref="paper",
    x=0.95, y=0.05,
    showarrow=False,
    align="right",
    bgcolor="white",
    bordercolor="black",
    borderwidth=1
)

fig_corr.update_layout(
    xaxis_title="Average Temperature (°F)",
    yaxis_title="Energy Consumption (MW)",
    legend_title="City",
    margin=dict(t=60, b=40),
    hovermode="closest"
)

st.plotly_chart(fig_corr, use_container_width=True)



# -----------------------
# 4️⃣ Usage Patterns Heatmap (Final Version)
# -----------------------
st.header("4. Usage Patterns Heatmap")

# 1. Add weekday column and order it
filtered_df["weekday"] = filtered_df["date"].dt.day_name()
weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
filtered_df["weekday"] = pd.Categorical(filtered_df["weekday"], categories=weekday_order, ordered=True)

# 2. Create temperature bins
bins = [-float("inf"), 50, 60, 70, 80, 90, float("inf")]
labels = ["<50°F", "50-60°F", "60-70°F", "70-80°F", "80-90°F", ">90°F"]
filtered_df["temp_bin"] = pd.cut(filtered_df["avg_temp_f"], bins=bins, labels=labels)

# 3. City selection
city_selected = st.selectbox("Select city for heatmap", sorted(filtered_df["city"].unique()))
city_df = filtered_df[filtered_df["city"] == city_selected]

# 4. Group and pivot
heat_df = city_df.groupby(["temp_bin", "weekday"])["energy_consumption_mw"].mean().reset_index()
pivot = heat_df.pivot(index="temp_bin", columns="weekday", values="energy_consumption_mw")
pivot = pivot.reindex(index=labels, columns=weekday_order)  # Ensure consistent order

# 5. Create heatmap
fig_heatmap = px.imshow(
    pivot,
    text_auto=".1f",  # Show values on cells
    color_continuous_scale="RdYlBu_r",  # Blue (low) to red (high)
    aspect="auto",
    labels=dict(color="Avg Energy (MW)"),
    title=f"Energy Usage by Temperature and Weekday – {city_selected}"
)

# 6. Add layout improvements
fig_heatmap.update_layout(
    xaxis_title="Day of Week",
    yaxis_title="Temperature Range (°F)",
    margin=dict(t=50, b=40),
    coloraxis_colorbar=dict(title="Avg Energy (MW)"),
)

# 7. Show plot
st.plotly_chart(fig_heatmap, use_container_width=True)
