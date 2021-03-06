import pandas as pd
import networkx as nx
import re
import plotly.graph_objects as go
import math
import ast

def normalize(x, weights):
    return (x - min(weights)) / (max(weights) - min(weights))

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


def network_graph(country, slider):
    edgelist = pd.read_csv(f"data/{country}_edgelist_weight.csv")
    edgelist.drop(columns="Unnamed: 0", inplace=True)
    nodelist = pd.read_csv(f"data/{country}_nodelist.csv")
    nodelist.drop(columns="Unnamed: 0", inplace=True)

    # Topic seventyfive is contact tracing
    seventyfive = edgelist[edgelist['node1'] == "Topic75"]
    seventyfive = seventyfive.append(edgelist[edgelist['node2'] == "Topic75"])
    seventyfive = seventyfive.sort_values(by="weight", ascending = False)

    edges = edgelist[edgelist.weight > slider]
    graph = nx.Graph()

    # get the list of nodes/topics
    topics = list(set(list_flatten(edges[['node1', 'node2']].values.tolist())))
    topics.remove("Topic75")
    topics.insert(0, "Topic75")

    # dictionary mapping topic to name
    topic_name_dict = nodelist[nodelist.topic.isin(topics)]
    topic_name_dict["label"] = topic_name_dict.label.apply(lambda a: ast.literal_eval(a))

    # add edges and weights
    for index, value in edges.iterrows():
        graph.add_edge(value['node1'], value['node2'], weight=value['weight'])

    # https://stackoverflow.com/questions/14283341/how-to-increase-node-spacing-for-networkx-spring-layout
    nodes_of_largest_component  = max(nx.connected_components(graph), key = len)
    largest_component = graph.subgraph(nodes_of_largest_component)
    graph = largest_component
    dfg = pd.DataFrame(index=graph.nodes(), columns=graph.nodes())
    for row, data in nx.shortest_path_length(graph):
        for col, dist in data.items():
            dfg.loc[row,col] = dist

    dfg = dfg.fillna(dfg.max().max())
    pos_ = nx.kamada_kawai_layout(graph, dist=dfg.to_dict())
        
    # The annoying workaround to show the labels on the lines
    # https://stackoverflow.com/questions/46037897/line-hover-text-in-plotly
    middle_node_trace = make_middle_node_trace()

    # For each edge, make an edge_trace, append to list
    # For normalization
    edge_weights = []
    for edge in graph.edges():
        weight = graph.edges()[edge]['weight']
        edge_weights.append(weight)
        
    # For each edge, make an edge_trace, append to list
    edge_trace = []
    for edge in graph.edges():
        char_1 = edge[0]
        char_2 = edge[1]
        x0, y0 = pos_[char_1]
        x1, y1 = pos_[char_2]
        
        weight = graph.edges()[edge]['weight']
        
        text = str(weight) + " [" + char_1 + '-' + char_2 + "]"
        trace = make_edge([x0, x1, None], [y0, y1, None], text, 
                          width = ((normalize(weight, edge_weights)+0.1) * 2))
    #                        width = math.log2(weight/1000))
        edge_trace.append(trace)
        
        middle_node_trace['x'] += tuple([(x0+x1)/2])
        middle_node_trace['y'] += tuple([(y0+y1)/2])
        middle_node_trace['text'] +=  tuple([text])


    node_trace = make_node_trace()

    # Normalize node weights
    node_weights = []
    for node in graph.nodes():
        x, y = pos_[node]
        nodesize = nodelist.loc[nodelist['topic'] == node]['totalcount'].values[0]
        node_weights.append(nodesize)
        
        
    # For each node, get the position and size and add to the node_trace
    for node in graph.nodes():
        x, y = pos_[node]
        nodesize = nodelist.loc[nodelist['topic'] == node]['totalcount'].values[0]
        nodesize = (normalize(nodesize, node_weights)+0.8) * 30
        
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        
        nodename = re.search('\d+', node).group()
        
        node_trace['text'] += tuple(['<b>' + str(nodename) + '</b>'])
        node_trace['marker']['size'] += tuple([nodesize])

    
    node_adjacencies = []
    node_text = []
    node_annotations = []

    for node,adjacencies in enumerate(graph.adjacency()):
        nodesize = nodelist.loc[nodelist['topic'] == adjacencies[0]]['totalcount'].values[0]
        # nodesize = (normalize(nodesize, node_weights)+1) * 30

        node_adjacencies.append(nodesize)

        topic_info = topic_name_dict[topic_name_dict['topic'] == adjacencies[0]]
        topic_label = topic_info.label.values[0][0:8] # Just the first 4
        topic_label = ' '.join(["-".join(topic_label[i:i+2]) for i in range(0, len(topic_label), 2)])

        node_text.append(topic_label + f" [{nodesize}]")
        nodename = re.search('\d+', adjacencies[0]).group()

        node_annotations.append(
            dict(
                x = pos_[adjacencies[0]][0],
                y = pos_[adjacencies[0]][1],
                text = nodename, # node name that will be displayed
                font = dict(color='white', size=10),
                showarrow=False, arrowhead=1, ax=-10, ay=-10))


    # Specifically for Topic 75
    seventyfive2 = edges[edges['node1'] == "Topic75"]
    seventyfive2 = seventyfive2.append(edges[edges['node2'] == "Topic75"])
    seventyfive2 = seventyfive2.sort_values(by="weight", ascending = False)

    subtitle = ["Topic 75 [contact tracing] edges:"]
    for i, row in seventyfive2.iterrows():
        subtitle.append(f"{row.node1}-{row.node2}[{row.weight}]")



    # Plot the graph
    node_trace.marker.color = node_adjacencies
    node_trace.text = node_text

    fig = go.Figure(data=[node_trace, middle_node_trace],
                 layout=go.Layout(
                    # title='Network Analysis of Coronavirus Topics',
                    titlefont_size=16,
                    xaxis_title='<br>'.join([s for s in subtitle]),
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

