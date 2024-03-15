import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import networkx as nx
from pyvis.network import Network


def adjust_weight(weight, average):
    new_weight = weight / average

    if new_weight < 25:
        return 25
    return new_weight


# Read dataset (CSV)
df_groups = pd.read_csv('data/edges.csv')
weight_mean = df_groups["Weight"].mean()
df_groups["NewWeights"] = df_groups["Weight"].apply(lambda x: adjust_weight(x, weight_mean))

# Set header title
st.title('Network Graph Visualization of Terror Group Attacks by Country')

# Define list of selection options and sort alphabetically
group_list = df_groups["Label"].unique()
group_list.sort()

# Implement multiselect dropdown menu for option selection (returns a list)
selected_group = st.selectbox('Select group(s) to visualize', group_list)

# Set info message on initial site load
if len(selected_group) == 0:
    st.text('Choose a group to get started')

# Create network graph when user selects >= 1 item
else:

    df_select = df_groups[df_groups['Label'] == selected_group]
    df_select = df_select.reset_index(drop=True)
    # Create networkx graph object from pandas dataframe
    G = nx.from_pandas_edgelist(df_select, 'Source', 'Target', 'Weight')

    # Initiate PyVis network object
    group_net = Network(height='650px', bgcolor='#222222', font_color='white')

    # Take Networkx graph and translate it to a PyVis graph format
    group_net.from_nx(G)

    # Generate network with specific layout settings
    group_net.repulsion(node_distance=420, central_gravity=0.33,
                        spring_length=110, spring_strength=0.10,
                        damping=0.95)
    weight_dict = {}
    for index, row in df_select.iterrows():
        weight_dict[row["Source"]] = row["NewWeights"]

    for n in group_net.nodes:
        weight = weight_dict.get(n["id"])
        if weight:
            n["size"] = weight
        else:
            weight = 25

        n["font"] = {"size": 30, "color": "white"}

    # Save and read graph as HTML file (on Streamlit Sharing)
    try:
        path = '/tmp'
        group_net.save_graph(f'{path}/pyvis_graph.html')
        HtmlFile = open(f'{path}/pyvis_graph.html', 'r', encoding='utf-8')

    # Save and read graph as HTML file (locally)
    except:
        path = '/html_files'
        group_net.save_graph(f'{path}/pyvis_graph.html')
        HtmlFile = open(f'{path}/pyvis_graph.html', 'r', encoding='utf-8')

    # Load HTML file in HTML component for display on Streamlit page
    components.html(HtmlFile.read(), height=650)
