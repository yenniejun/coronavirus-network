import pandas as pd
import networkx as nx
import re
import plotly.graph_objects as go
import math

def list_flatten(l, a=None):
    #check a
    if a is None:
        #initialize with empty list
        a = []

    for i in l:
        if isinstance(i, list):
            list_flatten(i, a)
        else:
            if (len(i) != 1): a.append(i)
    return a

def make_middle_node_trace():
    return go.Scatter(
        x=[],
        y=[],
        text=[],
        mode='markers',
        hoverinfo='text',
        marker=dict(
            opacity=0,
        ),
        hoverlabel=dict(
            bgcolor="white", 
            font_size=13, 
            font_family="Rockwell"
        )
    )

def make_edge(x, y, text, width):
    return  go.Scatter(x         = x,
                       y         = y,
                       line      = dict(width = width, color = '#888'),
                       hoverinfo = 'text',
                       text      = ([text]),
                       mode      = 'lines')

def make_node_trace():
    # Make a node trace
    return go.Scatter(
        x = [],
        y = [],
        text = [],
        textposition = "top center",
        textfont_size = 10,
        mode      = 'markers',
        hoverinfo = 'text',
        marker    = dict(
            colorscale='Sunsetdark',
            reversescale=True,
            size=[],
            colorbar=dict(
                thickness=15,
                title='Node Frequency',
                xanchor='left',
                titleside='right'
            ),
        line_width=2,
        color = [],
        line  = None
        )
    )


def network_graph(country):
    edgelist = pd.read_csv(f"data/{country}_edgelist_weight.csv")
    edgelist.drop(columns="Unnamed: 0", inplace=True)
    nodelist = pd.read_csv(f"data/{country}_nodelist.csv")
    nodelist.drop(columns="Unnamed: 0", inplace=True)

    graph = nx.Graph()
    edges = edgelist[:50]

    # get the list of nodes/topics
    topics = list(set(list_flatten(edges[['node1', 'node2']].values.tolist())))

    # dictionary mapping topic to name
    topic_name_dict = nodelist[nodelist.topic.isin(topics)]

    # add edges and weights
    for index, value in edges.iterrows():
        graph.add_edge(value['node1'], value['node2'], weight=value['weight'])
        
    # position the nodes in the graph. can use different layout
    pos_ = nx.shell_layout(graph)

    # The annoying workaround to show the labels on the lines
    # https://stackoverflow.com/questions/46037897/line-hover-text-in-plotly
    middle_node_trace = make_middle_node_trace()

    # For each edge, make an edge_trace, append to list
    edge_trace = []
    for edge in graph.edges():
        char_1 = edge[0]
        char_2 = edge[1]
        x0, y0 = pos_[char_1]
        x1, y1 = pos_[char_2]
        
        weight = graph.edges()[edge]['weight']
        
        text = str(weight) + " [" + char_1 + '-' + char_2 + "]"
    #     print(text)

        trace = make_edge([x0, x1, None], [y0, y1, None], text, 
                           width = math.log2(weight/1000))
        edge_trace.append(trace)
        
        middle_node_trace['x'] += tuple([(x0+x1)/2])
        middle_node_trace['y'] += tuple([(y0+y1)/2])
        middle_node_trace['text'] +=  tuple([text])

    node_trace = make_node_trace()

    # For each node, get the position and size and add to the node_trace
    for node in graph.nodes():
        x, y = pos_[node]
        nodesize = nodelist.loc[nodelist['topic'] == node]['totalcount'].values[0]/180
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        nodename = re.search('\d+', node).group()
        node_trace['text'] += tuple(['<b>' + str(nodename) + '</b>'])
        node_trace['marker']['size'] += tuple([nodesize])

    node_adjacencies = []
    node_text = []
    node_annotations = []

    for node,adjacencies in enumerate(graph.adjacency()):
        node_adjacencies.append(len(adjacencies[1]))

        topic_info = topic_name_dict[topic_name_dict['topic'] == adjacencies[0]]
        topic_label = ' '.join(topic_info.label.values[0].split()[0:3]) # Just the first 3

        node_text.append(topic_label + " (" + str(len(adjacencies[1])) + " connections)")

        nodename = re.search('\d+', adjacencies[0]).group()

        node_annotations.append(
            dict(
                x = pos_[adjacencies[0]][0],
                y = pos_[adjacencies[0]][1],
                text = nodename, # node name that will be displayed
                font = dict(color='white', size=10),
                showarrow=False, arrowhead=1, ax=-10, ay=-10)
            )

    # Plot the graph
    node_trace.marker.color = node_adjacencies
    node_trace.text = node_text

    fig = go.Figure(data=[node_trace, middle_node_trace],
                 layout=go.Layout(
                    # title='Network Analysis of Coronavirus Topics',
                    titlefont_size=16,
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    annotations=node_annotations, 
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )

    # Add all edge traces
    for trace in edge_trace:
        fig.add_trace(trace)
        
    return fig

