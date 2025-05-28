import streamlit as st
import pandas as pd
import altair as alt

# ✅ This MUST be the first Streamlit command
st.set_page_config(layout="wide")

st.title("👥 GitLab Account Dashboard")

# --- 🔘 Choose CSV Source ---
st.subheader("Select User Group")
col1, col2 = st.columns(2)

selected_group = None
with col1:
    if st.button("🧠 AI Developers"):
        selected_group = "aidevelopers_gitlab_collegewise.csv"
with col2:
    if st.button("🛠️ Tech Leads"):
        selected_group = "techlead_gitlab_collegewise.csv"

if not selected_group:
    st.warning("Please select a group to load the data.")
    st.stop()

# Load data
try:
    df = pd.read_csv(selected_group)
except FileNotFoundError:
    st.error(f"Could not find `{selected_group}`.")
    st.stop()

df.fillna('Unknown', inplace=True)

# Use first word of Affiliation for x-axis grouping
df['Short Affiliation'] = df['Affiliation'].apply(lambda x: str(x).split(" ")[0])

# Sort by total registrations
df = df.sort_values(by='total_registrations', ascending=False)

st.title("🎓 GitLab Account Creation Status by Affiliation")

# Sidebar: Top N selector
top_n = st.sidebar.slider("Show Top N Affiliations", min_value=1, max_value=10, value=5)

# Prepare top N data
top_df = df.head(top_n)

# Melt for grouped bars
chart_data = pd.melt(
    top_df,
    id_vars=['Short Affiliation'],
    value_vars=['no_of_accounts_created', 'no_of_accounts_needed'],
    var_name='Status',
    value_name='Count'
)

# Map colors
status_color_map = {
    'no_of_accounts_created': 'green',
    'no_of_accounts_needed': 'red'
}
chart_data['Color'] = chart_data['Status'].map(status_color_map)
chart_data['Status Label'] = chart_data['Status'].map({
    'no_of_accounts_created': 'Created',
    'no_of_accounts_needed': 'Needs'
})

# Grouped bar chart
bar_chart = alt.Chart(chart_data).mark_bar().encode(
    x=alt.X('Short Affiliation:N', title='Affiliation', sort='-y'),
    y=alt.Y('Count:Q'),
    color=alt.Color('Status Label:N', scale=alt.Scale(domain=['Created', 'Needs'], range=['#4CAF50', '#F44336'])),
    tooltip=['Short Affiliation', 'Status Label', 'Count'],
    column=alt.Column('Status Label:N', title=None)
).properties(
    width=800,
    height=400
).configure_axisX(labelAngle=-45)

# This creates grouped bars
grouped_bar = alt.Chart(chart_data).mark_bar().encode(
    x=alt.X('Short Affiliation:N', title='Affiliation', axis=alt.Axis(labelAngle=-45)),
    y=alt.Y('Count:Q'),
    color=alt.Color('Status Label:N', scale=alt.Scale(domain=['Created', 'Needs'], range=['#4CAF50', '#F44336'])),
    tooltip=['Short Affiliation', 'Status Label', 'Count'],
    xOffset='Status Label:N'  # <- THIS makes them grouped side-by-side
).properties(
    width=900,
    height=400,
    title=f"Top {top_n} Affiliations"
)

st.altair_chart(grouped_bar, use_container_width=True)

# --- Search Bar ---
st.subheader("🔍 Search for a College or Organization")

search_term = st.text_input("Type to search affiliation:", "")
filtered_options = df[df['Affiliation'].str.contains(search_term, case=False, na=False)]['Affiliation'].unique()

if len(filtered_options) > 0:
    selected_affiliation = st.selectbox("Matching affiliations:", options=filtered_options)
    selected_data = df[df['Affiliation'] == selected_affiliation].iloc[0]

    # Show detailed chart for selected college
    st.markdown(f"### 📊 Account Status for: {selected_affiliation}")

    detail_df = pd.DataFrame({
        'Status': ['Created', 'Needs'],
        'Count': [selected_data['no_of_accounts_created'], selected_data['no_of_accounts_needed']],
        'Color': ['#4CAF50', '#F44336']
    })

    detail_chart = alt.Chart(detail_df).mark_bar().encode(
        x=alt.X('Status:N'),
        y=alt.Y('Count:Q'),
        color=alt.Color('Color:N', scale=None),
        tooltip=['Status', 'Count']
    ).properties(width=300, height=300)

    st.altair_chart(detail_chart)
else:
    if search_term:
        st.warning("No matching affiliations found.")
