import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")

st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            background-color: #4b6c5d !important;
        }
        .notes-box {
            background-color:hsl(198, 16.00%, 84.10%); /* Light green background */
            padding: 10px;
            border-radius: 10px;
            margin-top: 10px;
            color: black;
            font-size: 14px;
        }
        :root {
            --primary-color: #81909A !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

file_path = "ParameterDataset.xlsx"
df = pd.read_excel(file_path, sheet_name="Table", engine="openpyxl")

# Data cleanup
df["Year"] = pd.to_numeric(df["Year"], errors="coerce")  # Convert to numeric, forcing non-numeric to NaN
df = df.dropna(subset=["Year", "Value", "Country", "Parameter", "Level", "Kind"])  # Drop rows with NaN in critical columns
df["Year"] = df["Year"].astype(int)  # Convert "Year" to integers
df["Value"] = pd.to_numeric(df["Value"], errors="coerce")

# Streamlit app
st.title("Country-wise Parameter Visualization")

# Sidebar filter for country
countries = sorted(df["Country"].unique())
selected_country = st.sidebar.selectbox("Select Country", countries)

# Sidebar filter for parameters
country_df = df[df["Country"] == selected_country]
parameters = sorted(country_df["Parameter"].unique())
selected_parameters = st.sidebar.multiselect("Select Parameters", parameters)

# Display notes as text in the sidebar
notes = sorted(country_df["Notes"].dropna().unique())
regular_notes = [note for note in notes if not note.startswith('*')]
starred_notes = sorted([note for note in notes if note.startswith('*')], key=lambda x: (len(x), x))

all_notes = "<br>".join(regular_notes + starred_notes)
st.sidebar.markdown(f'<div class="notes-box"><strong>Notes:</strong><br>{all_notes}</div>', unsafe_allow_html=True)

# Filter data by selected parameters
filtered_df = country_df[country_df["Parameter"].isin(selected_parameters)]

# Loop through each parameter and create separate plots
for selected_parameter in selected_parameters:
    fig = go.Figure()
    parameter_df = filtered_df[filtered_df["Parameter"] == selected_parameter]

    source = parameter_df["Source"].dropna().unique()
    source_link = source[0] if len(source) > 0 else "Source not available"

    source_name = parameter_df["Source name"].dropna().unique()
    source_name_text = source_name[0] if len(source_name) > 0 else "Source"

    y_axis_title = parameter_df["Y-axis"].dropna().unique()
    y_axis_title = y_axis_title[0] if len(y_axis_title) > 0 else "Value"
    
    # Sidebar filter for levels
    levels = sorted(parameter_df["Level"].dropna().unique())
    if levels == ["-"]:
        selected_levels = ["-"]
    else:   
        selected_levels = st.multiselect(f"Select Levels for {selected_parameter}", levels, default=[])
    
    # Sidebar filter for kind, but auto-select "-" if it's the only option
    kinds = sorted(parameter_df["Kind"].dropna().unique())

    if kinds == ["-"]:  # If the only kind is "-", auto-select it
        selected_kinds = ["-"]
    else:
        selected_kinds = st.multiselect(f"Select Kind for {selected_parameter}", kinds, default=[])

    
    for selected_level in selected_levels:
        level_df = parameter_df[parameter_df["Level"] == selected_level]
        
        for kind in selected_kinds:
            kind_df = level_df[level_df["Kind"] == kind]
            if not kind_df.empty:
            
                if selected_level == "-" and kind == "-":
                    name = ""
                elif selected_level == "-":
                    name = f"{kind}"
                elif kind == "-":
                    name = f"{selected_level}"
                else:
                    name = f"{selected_level} - {kind}"
                
                line_styles = ['solid', 'dash', 'dot', 'dashdot']
                line_style = line_styles[levels.index(selected_level) % len(line_styles)]
                
                trace = go.Scatter(
                    x=kind_df["Year"], 
                    y=kind_df["Value"], 
                    mode='lines+markers', 
                    name=name,
                    line=dict(width=2, dash=line_style),
                    marker=dict(size=6)
                )
                fig.add_trace(trace)

        fig.update_layout(
            title=f"{selected_country} - {selected_parameter}",
            xaxis_title="Year",
            yaxis_title=y_axis_title,
            template="plotly",
            showlegend=True,
            hovermode="x unified",
            margin=dict(t=50, b=50, l=50, r=50),
            font=dict(family="Arial", size=12, color="black")
        )

    # Plot graph with unique key
    if not parameter_df.empty:
        unique_key = f"{selected_country}_{selected_parameter}_{'_'.join(selected_levels)}_{'_'.join(selected_kinds)}"
        st.plotly_chart(fig, key=unique_key)

    # Get all unique sources and their corresponding years
    unique_sources = parameter_df[["Year", "Source", "Source name"]].dropna().drop_duplicates()

    # Filter sources by year for dropdown
    available_years = sorted(unique_sources["Year"].unique())
    selected_source_year = st.selectbox("Select Year for Sources", available_years, index=0)
    
    # Filter sources based on the selected year
    filtered_sources = unique_sources[unique_sources["Year"] == selected_source_year]
    if not filtered_sources.empty:
        source_links = [
            f"**{row['Year']} -** [{row['Source name']}]({row['Source']})"
            for _, row in filtered_sources.iterrows()
        ]
        
        st.markdown("**Sources:**<br>" + "<br>".join(source_links), unsafe_allow_html=True)
