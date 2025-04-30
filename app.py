
# Install in Colab:
# !pip install dash jupyter-dash pyngrok pandas plotly

import pandas as pd
import networkx as nx
import plotly.express as px
import plotly.graph_objects as go
from jupyter_dash import JupyterDash
from dash import dcc, html, Input, Output, dash_table

# Load data
df = pd.read_csv("dashboard_data_with_abstract.csv")

# Build bipartite graph
B = nx.Graph()
for _, row in df.iterrows():
    if pd.notnull(row["name"]) and pd.notnull(row["title_x"]):
        B.add_node(row["name"], bipartite="authors")
        B.add_node(row["title_x"], bipartite="papers")
        B.add_edge(row["name"], row["title_x"])

authors = [n for n, d in B.nodes(data=True) if d["bipartite"] == "authors"]
papers = [n for n in B if n not in authors]

pos = {}
for i, author in enumerate(authors): pos[author] = (0, i)
for i, paper in enumerate(papers): pos[paper] = (1.5, i)

# Initialize app
app = JupyterDash(__name__)
app.layout = html.Div([
    html.H1("Research Dashboard", style={"textAlign": "center"}),

    html.Div([
        dcc.Dropdown(id="author-dropdown",
            options=[{"label": a, "value": a} for a in df["name"].dropna().unique()],
            multi=True, placeholder="Filter by Author"),
        dcc.Dropdown(id="topic-dropdown",
            options=[{"label": t, "value": t} for t in df["topic_label"].dropna().unique()],
            multi=True, placeholder="Filter by Topic"),
        dcc.Input(id="keyword-input", type="text", placeholder="Keyword search..."),
    ], style={"margin": "20px"}),

    dcc.Graph(id="publications-bar"),
    dcc.Graph(id="topic-distribution-bar"),
    dcc.Graph(id="topic-timeseries"),
    dcc.Graph(id="citation-timeseries"),

    html.H2("Papers Table"),
    dash_table.DataTable(
        id="paper-table",
        columns=[
            {"name": "Title", "id": "title_x"},
            {"name": "Author", "id": "name"},
            {"name": "Year", "id": "year_x"},
            {"name": "Citations", "id": "citations_x"},
            {"name": "Topic", "id": "topic_label"},
            {"name": "Abstract", "id": "abstract_x", "presentation": "markdown"}
        ],
        tooltip_data=[], tooltip_duration=None, page_size=10,
        style_table={"overflowX": "auto"},
        style_data_conditional=[{
            "if": {"column_id": "abstract_x"},
            "textOverflow": "ellipsis", "maxWidth": 0
        }]
    ),

    html.H2("Top Authors by Citations"),
    dash_table.DataTable(
        id="author-stats-table",
        columns=[
            {"name": "Author", "id": "name"},
            {"name": "Total Citations", "id": "total_citations"},
            {"name": "Paper Count", "id": "paper_count"}
        ],
        data=[], sort_action="native", page_size=10,
        style_table={"overflowX": "auto"}
    ),

    html.H2("Interactive Co-authorship Network"),
    dcc.Graph(id="coauthorship-network"),

    html.H2("Author-Paper Bipartite Network"),
    dcc.Graph(id="bipartite-network"),
])

@app.callback(
    [Output("publications-bar", "figure"),
     Output("topic-distribution-bar", "figure"),
     Output("topic-timeseries", "figure"),
     Output("citation-timeseries", "figure"),
     Output("paper-table", "data"),
     Output("paper-table", "tooltip_data"),
     Output("author-stats-table", "data"),
     Output("coauthorship-network", "figure"),
     Output("bipartite-network", "figure")],
    [Input("author-dropdown", "value"),
     Input("topic-dropdown", "value"),
     Input("keyword-input", "value")]
)
def update_dashboard(authors_filter, topics_filter, keyword):
    dff = df.copy()
    if authors_filter:
        dff = dff[dff['name'].isin(authors_filter)]
    if topics_filter:
        dff = dff[dff['topic_label'].isin(topics_filter)]
    if keyword:
        dff = dff[dff['processed_text'].str.contains(keyword, case=False, na=False)]

    pub_fig = px.histogram(dff, x='year_x', color_discrete_sequence=["#636EFA"], title="Publications Over Time")
    topic_fig = px.histogram(dff, x='topic_label', color='topic_label', title="Topic Distribution")
    topic_years = dff.groupby(['year_x', 'topic_label']).size().reset_index(name='count')
    topic_ts = px.line(topic_years, x='year_x', y='count', color='topic_label', title='Topic Evolution Over Time', markers=True)
    citation_years = dff.groupby('year_x')['citations_x'].sum().reset_index()
    citation_ts = px.line(citation_years, x='year_x', y='citations_x', title='Citations Over Time', markers=True)

    table_data = dff.sort_values("citations_x", ascending=False).to_dict("records")
    tooltips = [{"abstract_x": {"value": str(row["abstract_x"])[:500] + "...", "type": "markdown"}} for _, row in dff.iterrows()]

    author_stats = dff.groupby("name").agg(
        total_citations=("citations_x", "sum"),
        paper_count=("paper_id", "nunique")
    ).reset_index().sort_values("total_citations", ascending=False)

    # Co-authorship network
    G = nx.Graph()
    for paper_id, group in dff.groupby("paper_id"):
        authors = group["name"].dropna().unique()
        for i in range(len(authors)):
            for j in range(i + 1, len(authors)):
                G.add_edge(authors[i], authors[j])
    pos = nx.spring_layout(G, seed=42)
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]
    node_x, node_y, text, sizes = [], [], [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        papers = df[df['name'] == node]['paper_id'].nunique()
        citations = df[df['name'] == node]['citations_x'].sum()
        sizes.append(10 + papers)
        text.append(f"{node}<br>Papers: {papers}<br>Citations: {citations}")
    edge_trace = go.Scatter(x=edge_x, y=edge_y, mode='lines', line=dict(width=0.5, color='#888'), hoverinfo='none')
    node_trace = go.Scatter(x=node_x, y=node_y, mode='markers', hoverinfo='text', text=text,
                            marker=dict(color='MediumPurple', size=sizes, line_width=2))
    coauthor_fig = go.Figure(data=[edge_trace, node_trace])
    coauthor_fig.update_layout(title='Co-authorship Network', showlegend=False, hovermode='closest',
                               margin=dict(b=20, l=5, r=5, t=40),
                               xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                               yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))

    # Bipartite Graph
    edge_x, edge_y, node_x, node_y, node_text, node_color = [], [], [], [], [], []
    for edge in B.edges():
        x0, y0 = pos.get(edge[0], (0, 0))
        x1, y1 = pos.get(edge[1], (1.5, 0))
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]
    for node in B.nodes():
        x, y = pos.get(node, (0, 0))
        node_x.append(x)
        node_y.append(y)
        label = "Author" if node in authors else "Paper"
        node_text.append(f"{label}: {node}")
        node_color.append('#1f77b4' if label == "Author" else '#ff7f0e')
    edge_trace = go.Scatter(x=edge_x, y=edge_y, mode='lines', line=dict(width=0.5, color='#ccc'), hoverinfo='none')
    node_trace = go.Scatter(x=node_x, y=node_y, mode='markers', text=node_text, hoverinfo='text',
                            marker=dict(color=node_color, size=8, line_width=1))
    bipartite_fig = go.Figure(data=[edge_trace, node_trace])
    bipartite_fig.update_layout(title='Author-Paper Bipartite Network', showlegend=False, hovermode='closest')

    return pub_fig, topic_fig, topic_ts, citation_ts, table_data, tooltips, author_stats.to_dict("records"), coauthor_fig, bipartite_fig

app.run_server(mode="external")
