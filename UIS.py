import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.colors as pc
import re

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION & CUSTOM CSS (shared by both dashboards)
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Indicator Analysis App", layout="wide")

st.markdown(
    """
    <style>
    /* Overall background */
    .stApp {
        background-color: #f8f8f2;
    }
    /* Sidebar background and text color */
    [data-testid="stSidebar"] {
        background-color: #e8f5e9;
        color: #333333;
    }
    /* Button styling for general buttons */
    div.stButton > button {
        background-color: #4b6c5d;
        color: white;
        padding: 2rem 3rem !important;
        font-size: 1.5rem !important;
        border-radius: 0.5rem !important;
        border: none;
    }
    div.stButton > button:hover {
        background-color: #3a594f;
        color: white;
    }
    /* Header styling */
    h1, h2, h3, h4, h5, h6 {
        color: #4b6c5d;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Inject custom CSS to style the button in the sidebar
st.sidebar.markdown(
    """
    <style>
    /* Target any button inside a Streamlit button container */
    div.stButton > button {
        background-color: #4CAF50;  /* Green background */
        color: white;               /* White text */
        padding: 10px 20px;         /* Padding */
        font-size: 16px;            /* Font size */
        border: none;               /* No border */
        border-radius: 20px;         /* Rounded corners */
        cursor: pointer;            /* Pointer cursor on hover */
    }
    /* Optional: Change background color on hover */
    div.stButton > button:hover {
        background-color: #45a049;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# =============================================================================
# SDG4 DASHBOARD FUNCTIONS 
# =============================================================================
@st.cache_data
def load_data_sdg4():
    data = pd.read_csv('UNESCO_edu_data.csv')
    metadata = pd.read_csv('SDG_METADATA.csv')
    data.drop('indicator_desc', axis=1, inplace=True)
    data.rename(columns={'indicator_id': 'INDICATOR_ID'}, inplace=True)
    data['INDICATOR_ID'] = data['INDICATOR_ID'].str.upper().str.strip()
    label_data = pd.merge(data, metadata, on="INDICATOR_ID", how="left")
    return label_data

sdg4_data = load_data_sdg4()

def create_line_chart_with_selection_sdg4(country_code):
    df = sdg4_data[sdg4_data['country_id'] == country_code]
    unique_indicators = df[['INDICATOR_ID', 'INDICATOR_LABEL_EN']].drop_duplicates().sort_values('INDICATOR_ID')
    indicator_options = unique_indicators['INDICATOR_ID'].tolist()
    
    def format_indicator(ind):
        label = unique_indicators[unique_indicators['INDICATOR_ID'] == ind]['INDICATOR_LABEL_EN'].iloc[0]
        return f"{ind} - {label}"
    
    selected_indicators = st.sidebar.multiselect(
        "Select SDG4 Indicator(s) to Display",
        options=indicator_options,
        format_func=format_indicator
    )
    if not selected_indicators:
        st.sidebar.warning("Please select at least one indicator.")
        return None

    df_filtered = df[df['INDICATOR_ID'].isin(selected_indicators)].drop_duplicates()
    
    base_colors = pc.qualitative.Plotly
    indicator_color_map = {ind: base_colors[i % len(base_colors)] 
                           for i, ind in enumerate(sorted(selected_indicators))}
    
    fig = px.line(
        df_filtered,
        x='year',
        y='value',
        color='INDICATOR_ID',
        markers=True,
        custom_data=['INDICATOR_LABEL_EN'],
        template='plotly_white',
        labels={'year': 'Year', 'value': 'Value'}
    )
    fig.update_traces(
        hovertemplate='<b>%{customdata[0]}</b><br>Year: %{x}<br>Value: %{y}<extra></extra>'
    )
    for trace in fig.data:
        ind = trace.name
        if ind in indicator_color_map:
            trace.line.color = indicator_color_map[ind]
            trace.line.width = 3
    fig.update_layout(margin=dict(l=60, r=60, t=40, b=80))
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=[
                dict(count=5, label='Last 5 Years', step='year', stepmode='backward'),
                dict(count=10, label='Last 10 Years', step='year', stepmode='backward'),
                dict(step='all', label='All Years')
            ]
        )
    )
    return fig


def sdg4_show_nepal():
    st.subheader("Nepal Analysis")
    fig = create_line_chart_with_selection_sdg4('NPL')
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)

def sdg4_show_estonia():
    st.subheader("Estonia Analysis")
    fig = create_line_chart_with_selection_sdg4('EST')
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)

def sdg4_show_sierra_leone():
    st.subheader("Sierra Leone Analysis")
    fig = create_line_chart_with_selection_sdg4('SLE')
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)

def sdg4_show_usa():
    st.subheader("USA Analysis")
    fig = create_line_chart_with_selection_sdg4('USA')
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)

def show_sdg4_individual():
    st.title(":green[SDG-4 indicators -> Individual Analysis]")
    selected_country = st.sidebar.radio("Select Country", options=["Nepal", "USA", "Estonia", "Sierra Leone"])
    if selected_country == "Nepal":
        sdg4_show_nepal()
    elif selected_country == "USA":
        sdg4_show_usa()
    elif selected_country == "Estonia":
        sdg4_show_estonia()
    elif selected_country == "Sierra Leone":
        sdg4_show_sierra_leone()
    st.markdown("**SOURCE**: [SDG-4 Indicators](https://databrowser.uis.unesco.org/browser/EDUCATION/UIS-SDG4Monitoring)")

def show_sdg4_cross():
    st.title(":green[SDG-4 indicators -> Cross-country Analysis]")
    st.markdown("**SOURCE**: [SDG-4 Indicators](https://databrowser.uis.unesco.org/browser/EDUCATION/UIS-SDG4Monitoring)")
    indicators = {
        "EA.3T8.AG25T99": "Educational attainment rate, completed upper secondary education or higher, population 25+ years, both sexes (%)",
        "XGOVEXP.IMF": "Expenditure on education as a percentage of total government expenditure (%)",
        "XGDP.FSGOV": "Government expenditure on education as a percentage of GDP (%)",
        "XUNIT.PPPCONST.2T3.FSGOV.FFNTR": "Initial government funding per secondary student, constant PPP$",
        "NER.02.CP": "Net enrolment rate, pre-primary, both sexes (%)",
        "ROFST.1T3.CP": "Out-of-school rate for children, adolescents and youth of primary, lower secondary and upper secondary school age, both sexes (%)",
        "ROFST.1T3.F.CP": "Out-of-school rate for children, adolescents and youth of primary, lower secondary and upper secondary school age, female (%)",
        "ROFST.1T3.M.CP": "Out-of-school rate for children, adolescents and youth of primary, lower secondary and upper secondary school age, male (%)",
        "ROFST.H.3": "Out-of-school rate for youth of upper secondary school age, both sexes (household survey data) (%)",
        "ROFST.3.F.CP": "Out-of-school rate for youth of upper secondary school age, female (%)",
        "ROFST.3.M.CP": "Out-of-school rate for youth of upper secondary school age, male (%)",
        "SCHBSP.2.WELEC": "Proportion of lower secondary schools with access to electricity (%)",
        "SCHBSP.1.WCOMPUT": "Proportion of primary schools with access to computers for pedagogical purposes (%)",
        "SCHBSP.1.WELEC": "Proportion of primary schools with access to electricity (%)",
        "SCHBSP.2T3.WCOMPUT": "Proportion of secondary schools with access to computers for pedagogical purposes (%)",
        "SCHBSP.3.WELEC": "Proportion of upper secondary schools with access to electricity (%)"
    }
    selected_indicator = st.sidebar.selectbox(
        "Select an Indicator",
        options=list(indicators.keys()),
        format_func=lambda x: f"{x} - {indicators[x]}"
    )
    st.markdown(
    f"""
    <h4>Displaying cross-country analysis for:- </h4>
    <i><span style='border-bottom: 3px solid green;'>{indicators[selected_indicator]}</span></i>
    </h5>
    """,
    unsafe_allow_html=True
    )
      
    st.markdown("<br><br>", unsafe_allow_html=True)
    df = sdg4_data[sdg4_data["INDICATOR_ID"] == selected_indicator].drop_duplicates()
    base_colors = {
        "NPL": "#FF6347",
        "USA": "#000080",
        "SLE": "#FFDB58",
        "EST": "#4682B4"
    }
    fig_line = px.line(
        df,
        x="year",
        y="value",
        color="country_id",
        markers=True,
        template="plotly_white",
        labels={"year": "Year", "value": "Value", "country_id": "Country"},
        color_discrete_map=base_colors,
        height=700
    )
    fig_line.update_layout(margin=dict(l=60, r=60, t=40, b=80))
    for trace in fig_line.data:
        trace.line.width = 3
    fig_line.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=[
                dict(count=5, label="Last 5 Years", step="year", stepmode="backward"),
                dict(count=10, label="Last 10 Years", step="year", stepmode="backward"),
                dict(step="all", label="All Years")
            ]
        )
    )
    st.plotly_chart(fig_line, use_container_width=True)
    with st.expander("Show Area Chart"):
        fig_area = px.area(
            df,
            x="year",
            y="value",
            color="country_id",
            template="plotly_white",
            labels={"year": "Year", "value": "Value", "country_id": "Country"},
            color_discrete_map=base_colors,
            height=700
        )
        fig_area.update_traces(opacity=0.75)
        fig_area.update_layout(margin=dict(l=60, r=60, t=40, b=80))
        fig_area.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=[
                    dict(count=5, label="Last 5 Years", step="year", stepmode="backward"),
                    dict(count=10, label="Last 10 Years", step="year", stepmode="backward"),
                    dict(step="all", label="All Years")
                ]
            )
        )
        st.plotly_chart(fig_area, use_container_width=True)
    
    with st.expander("Show Bar Chart"):
        df_bar = df.groupby(["year", "country_id"])["value"].mean().reset_index()
        fig_bar = px.bar(
            df_bar,
            x="year",
            y="value",
            color="country_id",
            barmode="group",
            template="plotly_white",
            labels={"year": "Year", "value": "Average Value", "country_id": "Country"},
            color_discrete_map=base_colors,
            height=700
        )
        fig_bar.update_layout(margin=dict(l=60, r=60, t=40, b=80))
        st.plotly_chart(fig_bar, use_container_width=True)
    
    

# =============================================================================
# OPRI DASHBOARD FUNCTIONS 
# =============================================================================
@st.cache_data
def load_data_opri():
    # Read the CSV files back into DataFrames
    other_data_part1 = pd.read_csv("OPRI_NATIONAL_1.csv")
    other_data_part2 = pd.read_csv("OPRI_NATIONAL_2.csv")
    other_data_part3 = pd.read_csv("OPRI_NATIONAL_3.csv")
    other_data_part4 = pd.read_csv("OPRI_NATIONAL_4.csv")
    other_data_part5 = pd.read_csv("OPRI_NATIONAL_5.csv")

    # Combine the DataFrames to restore the original dataset
    other_data = pd.concat([other_data_part1, other_data_part2, other_data_part3, other_data_part4, other_data_part5], ignore_index=True)
    other_label = pd.read_csv('OPRI_LABEL.csv')
    
    subset_codes = ['NPL', 'USA', 'SLE', 'EST']
    other_uis = other_data[other_data['country_id'].isin(subset_codes)]
    
    other_uis['indicator_id'] = other_uis['indicator_id'].astype(str)
    other_uis.rename(columns={'indicator_id': 'INDICATOR_ID'}, inplace=True)
    
    label_other_data = pd.merge(other_uis, other_label, on="INDICATOR_ID", how="left")
    
    filtered_data = label_other_data[~label_other_data['INDICATOR_LABEL_EN'].str.contains('tertiary', case=False, na=False)]
    
    regions = ['Africa:', 'Asia:', 'Caribbean and Central America:', 'Europe:', 'North America:', 'Oceania:', 'South America']
    keep_list = [
        'Africa: Students from Sierra Leone, both sexes (number)',
        'Asia: Students from Nepal, both sexes (number)',
        'Europe: Students from Estonia, both sexes (number)',
        'North America: Students from the United States, both sexes (number)'
    ]
    mask_region = filtered_data['INDICATOR_LABEL_EN'].str.startswith(tuple(regions))
    mask_keep = filtered_data['INDICATOR_LABEL_EN'].isin(keep_list)
    filtered_data = filtered_data[~mask_region | mask_keep]
    
    zero_ratio = filtered_data.groupby('INDICATOR_ID')['value'].apply(lambda x: (x == 0).mean())
    indicators_to_keep = zero_ratio[zero_ratio <= 0.7].index
    filtered_data_df = filtered_data[filtered_data['INDICATOR_ID'].isin(indicators_to_keep)]
    
    def assign_category(indicator):
        s = indicator.lower().strip()
        if "teaching staff compensation" in s:
            return "Expenditure"
        if "expenditure" in s:
            return "Expenditure"
        if "enrol" in s:
            return "Enrollment"
        if "attendance" in s:
            return "Attendance"
        if "duration" in s:
            return "Duration"
        if "mean years of schooling" in s:
            return "Duration"
        if "official entrance" in s:
            return "Duration"
        if "illiterate" in s or "illiteracy" in s:
            return "Illiteracy"
        if "mobile" in s or "mobility" in s or "net flow" in s:
            return "Mobility"
        if 'students from' in s:
            return "Mobility"
        if "out-of-school" in s:
            return "Out-of-School"
        if "teacher" in s:
            return "Teachers"
        if "repeat" in s or "repetition" in s:
            return "Repetition"
        if "survival" in s:
            return "Survival rates"
        if "school age population" in s or "school life expectancy" in s or 'compulsory school age' in s:
            return "General School Characteristics"
        return "Uncategorized"
    
    filtered_data_df['CATEGORY'] = filtered_data_df['INDICATOR_LABEL_EN'].apply(assign_category)
    return filtered_data_df

opri_data = load_data_opri()

@st.cache_data
def get_country_indicators_opri(country_code):
    data = load_data_opri()
    df = data[data['country_id'] == country_code]
    unique_indicators = df[['INDICATOR_ID', 'INDICATOR_LABEL_EN', 'CATEGORY']].drop_duplicates().sort_values('INDICATOR_ID')
    indicator_dict = dict(zip(unique_indicators['INDICATOR_ID'], unique_indicators['INDICATOR_LABEL_EN']))
    return unique_indicators, indicator_dict

category_base_colors_opri = {
    "Expenditure": "#d62728",
    "Enrollment": "#1f77b4",
    "Attendance": "#2ca02c",
    "Duration": "#ff7f0e",
    "Illiteracy": "#9467bd",
    "Mobility": "#8c564b",
    "Out-of-School": "#e377c2",
    "Teachers": "#7f7f7f",
    "Repetition": "#bcbd22",
    "Survival rates": "#17becf",
    "General School Characteristics": "#8c6d31",
    "Uncategorized": "#7f7f7f"
}

def create_individual_chart_multi_opri(country_code):                                           # custom dash/marker logic
    data = load_data_opri()
    country_df = data[data['country_id'] == country_code]
    available_categories = sorted(country_df['CATEGORY'].unique())
    selected_categories = st.sidebar.multiselect("Select Category(s)", options=available_categories, default=[])
    if not selected_categories:
        st.sidebar.info("Please select at least one category.")
        return None
    df_cat = country_df[country_df['CATEGORY'].isin(selected_categories)]
    unique_indicators = df_cat[['INDICATOR_ID', 'INDICATOR_LABEL_EN', 'CATEGORY']].drop_duplicates().sort_values('INDICATOR_ID')
    indicator_dict = dict(zip(unique_indicators['INDICATOR_ID'], unique_indicators['INDICATOR_LABEL_EN']))
    selected_indicators = st.sidebar.multiselect(
        "Select Indicator(s) to Display",
        options=list(indicator_dict.keys()),
        format_func=lambda x: f"{x} - {indicator_dict[x]}",
        default=[]
    )
    if not selected_indicators:
        st.sidebar.info("Please select at least one indicator.")
        return None
    graph_df = df_cat[df_cat['INDICATOR_ID'].isin(selected_indicators)].sort_values('year')
    unique_labels = graph_df['INDICATOR_LABEL_EN'].unique()
    y_label = unique_labels[0] if len(unique_labels) == 1 else 'Value'
    
    indicator_color_map = {}
    dash_map = {}
    marker_map = {}
    dash_styles = ['solid', 'dot', 'dash', 'longdash', 'dashdot']
    marker_symbols = ['circle', 'square', 'diamond', 'cross', 'x']
    for cat in selected_categories:
        inds_in_cat = unique_indicators[unique_indicators['CATEGORY'] == cat]['INDICATOR_ID'].tolist()
        inds_in_cat = [ind for ind in inds_in_cat if ind in selected_indicators]
        if not inds_in_cat:
            continue
        base_color = category_base_colors_opri.get(cat, "#000000")
        for i, ind in enumerate(sorted(inds_in_cat)):
            indicator_color_map[ind] = base_color
            dash_map[ind] = dash_styles[i % len(dash_styles)]
            marker_map[ind] = marker_symbols[i % len(marker_symbols)]
    
    country_map = {"NPL": "Nepal", "USA": "USA", "EST": "Estonia", "SLE": "Sierra Leone"}
    c_name = country_map.get(country_code, "")
    
    fig = px.line(
        graph_df,
        x='year',
        y='value',
        color='INDICATOR_ID',
        color_discrete_map=indicator_color_map,
        markers=True,
        title=f'Individual Analysis for Country: {c_name}',
        labels={'year': 'Year', 'value': y_label, 'INDICATOR_LABEL_EN': 'Indicator'},
        hover_data={'INDICATOR_LABEL_EN': True},
        template='plotly_white'
    )
    fig.update_traces(
        hovertemplate='Indicator: %{customdata[0]}<br>Year: %{x}<br>Value: %{y}<extra></extra>',
        customdata=graph_df[['INDICATOR_LABEL_EN']].values
    )
    for trace in fig.data:
        ind = trace.name
        if ind in dash_map:
            trace.line.dash = dash_map[ind]
            trace.marker.symbol = marker_map[ind]
            trace.line.width = 3
    fig.update_layout(
        width=1100,
        height=900,
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    return fig

def create_cross_country_chart_multi_opri():
    data = load_data_opri()
    available_categories = sorted(data['CATEGORY'].unique())
    selected_categories = st.sidebar.multiselect("Select Category(s)", options=available_categories, default=[])
    if not selected_categories:
        st.sidebar.info("Please select at least one category.")
        return None
    df_cat = data[data['CATEGORY'].isin(selected_categories)]
    unique_indicators = df_cat[['INDICATOR_ID', 'INDICATOR_LABEL_EN', 'CATEGORY']].drop_duplicates().sort_values('INDICATOR_ID')
    indicator_dict = dict(zip(unique_indicators['INDICATOR_ID'], unique_indicators['INDICATOR_LABEL_EN']))
    selected_indicator = st.sidebar.selectbox(
        "Select Indicator",
        options=list(indicator_dict.keys()),
        format_func=lambda x: f"{x} - {indicator_dict[x]}"
    )
    graph_df = df_cat[df_cat['INDICATOR_ID'] == selected_indicator].sort_values('year')
    unique_labels = graph_df['INDICATOR_LABEL_EN'].unique()
    y_label = unique_labels[0] if len(unique_labels) == 1 else 'Value'
    
    fig = px.line(
        graph_df,
        x='year',
        y='value',
        color='country_id',
        markers=True,
        title="Cross-Country Analysis",
        labels={'year': 'Year', 'value': y_label, 'country_id': 'Country', 'INDICATOR_LABEL_EN': 'Indicator'},
        hover_data={'INDICATOR_LABEL_EN': True},
        template='plotly_white',
        height=700
    )
    fig.update_layout(
        width=1100,
        height=900,
        paper_bgcolor='white',
        plot_bgcolor='white',
        margin=dict(l=60, r=60, t=40, b=80)
    )
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=[
                dict(count=5, label='Last 5 Years', step='year', stepmode='backward'),
                dict(count=10, label='Last 10 Years', step='year', stepmode='backward'),
                dict(step='all', label='All Years')
            ]
        )
    )
    return fig

def show_individual_opri():
    st.title(":green[Other Policy Indicators -> Individual Analysis]")
    selected_country = st.sidebar.radio("Select Country", options=["Nepal", "USA", "Estonia", "Sierra Leone"])
    if selected_country == "Nepal":
        opri_show_nepal()
    elif selected_country == "USA":
        opri_show_usa()
    elif selected_country == "Estonia":
        opri_show_est()
    elif selected_country == "Sierra Leone":
        opri_show_sle()
    st.markdown("**SOURCE**: [OPRI (Other Policy related indicators)](https://databrowser.uis.unesco.org/browser/EDUCATION/UIS-EducationOPRI)")

def opri_show_nepal():
    st.subheader("Nepal Analysis")
    fig = create_individual_chart_multi_opri('NPL')
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)

def opri_show_usa():
    st.subheader("USA Analysis")
    fig = create_individual_chart_multi_opri('USA')
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)

def opri_show_est():
    st.subheader("Estonia Analysis")
    fig = create_individual_chart_multi_opri('EST')
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)

def opri_show_sle():
    st.subheader("Sierra Leone Analysis")
    fig = create_individual_chart_multi_opri('SLE')
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)

def show_cross_opri():
    st.title(":green[Other Policy Indicators -> Cross-country Analysis]")
    fig = create_cross_country_chart_multi_opri()
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("**SOURCE**: [OPRI (Other Policy related indicators)](https://databrowser.uis.unesco.org/browser/EDUCATION/UIS-EducationOPRI)")


# =============================================================================
# SIDEBAR NAVIGATION FOR UIS INDICATORS
# =============================================================================
def show_uis_sidebar():

    st.sidebar.header("UIS Indicators Navigation")
    # Radio to choose dashboard type
    dashboard_type = st.sidebar.radio(
        "Select Indicator Type",
        options=["SDG4 Indicators", "OPRI Indicators"]
    )
    st.session_state.dashboard_type = dashboard_type
    
    # Depending on selection, show analysis options
    if dashboard_type == "SDG4 Indicators":
        analysis_option = st.sidebar.radio(
            "Select Analysis",
            options=["Individual Analysis", "Cross-country Analysis"]
        )
        st.session_state.analysis = analysis_option
    elif dashboard_type == "OPRI Indicators":
        analysis_option = st.sidebar.radio(
            "Select Analysis",
            options=["Individual Analysis", "Cross-country Analysis"]
        )
        st.session_state.analysis = analysis_option

        
# =============================================================================
# MAIN APP FUNCTION
# =============================================================================
def main():
    # Initialize session state defaults so the app launches directly into analysis mode.
    if "page" not in st.session_state:
        st.session_state.page = "uis"  # bypass the home page entirely
    if "dashboard_type" not in st.session_state:
        st.session_state.dashboard_type = "SDG4 Indicators"
    if "analysis" not in st.session_state:
        st.session_state.analysis = "Individual Analysis"
    
    # Always show the UIS sidebar navigation.
    show_uis_sidebar()
    
    # Dispatch to the appropriate analysis view.
    if st.session_state.dashboard_type == "SDG4 Indicators":
        if st.session_state.analysis == "Individual Analysis":
            show_sdg4_individual()
        elif st.session_state.analysis == "Cross-country Analysis":
            show_sdg4_cross()
    elif st.session_state.dashboard_type == "OPRI Indicators":
        if st.session_state.analysis == "Individual Analysis":
            show_individual_opri()
        elif st.session_state.analysis == "Cross-country Analysis":
            show_cross_opri()


if __name__ == "__main__":
    main()