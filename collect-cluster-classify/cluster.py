import matplotlib.pyplot as plt
import networkx as nx
import json
from sklearn import metrics
#import networkx.algorithms.community.centrality.girvan_newman as gn

data_base_directory  = "./data/"
tag_file_name = 'bitcoin_tweets.txt'
tag_friends_file_name = 'bitcoin_tweets_friends.txt'
output_file_name = 'cluster_result.txt'

def create_graph(users):
    graph = nx.Graph()
    for user in users:
        graph.add_node(user['screen_name'])
        for other_user in users:
            if other_user != user:
                jaccard_score = get_jaccard_score(user['friend_ids'], other_user['friend_ids'])
                if jaccard_score > 0.002:
                    graph.add_edge(user['screen_name'], other_user['screen_name'])
    return graph

def get_jaccard_score(user_a, user_b):
    common = set(user_a).intersection(user_b)
    union = set().union(user_a, user_b)
    return len(common) / len(union)

def get_subgraph(graph, min_degree):
    subgraph = nx.Graph()
    for node in graph.nodes():
        if len(graph.neighbors(node)) >= min_degree:
            subgraph.add_node(node)
    for outer_node in subgraph.nodes():
        for inner_node in subgraph.nodes():
            if graph.has_edge(inner_node, outer_node):
                subgraph.add_edge(inner_node, outer_node)
    return subgraph

def draw_network(graph, filename):
    pos = nx.spring_layout(graph)
    plt.figure(figsize=(15, 15))
    plt.axis('off')
    nx.draw_networkx(graph, pos, node_color='blue', edge_color='gray', with_labels=False)
    plt.savefig(filename)
    
def get_users_friends(file_path):
    users_friends = list()
    f = open(file_path, 'r')
    for line in f:
        if len(line) > 1:
            users_friends.append(json.loads(line))
    f.close()
    return users_friends

def girvan_newman(G, most_valuable_edge=None):
    """Finds communities in a graph using the Girvan–Newman method.
    Notes
    -----
    The Girvan–Newman algorithm detects communities by progressively
    removing edges from the original graph. The algorithm removes the
    "most valuable" edge, traditionally the edge with the highest
    betweenness centrality, at each step. As the graph breaks down into
    pieces, the tightly knit community structure is exposed and the
    result can be depicted as a dendrogram.
    """
    # If the graph is already empty, simply return its connected
    # components.
    if G.number_of_edges() == 0:
        yield tuple(nx.connected_components(G))
        return
    # If no function is provided for computing the most valuable edge,
    # use the edge betweenness centrality.
    if most_valuable_edge is None:
        def most_valuable_edge(G):
            """Returns the edge with the highest betweenness centrality
            in the graph `G`.
            """
            # We have guaranteed that the graph is non-empty, so this
            # dictionary will never be empty.
            betweenness = nx.edge_betweenness_centrality(G)
            return max(betweenness, key=betweenness.get)
    # The copy of G here must include the edge weight data.
    # Self-loops must be removed because their removal has no effect on
    # the connected components of the graph.
    G.remove_edges_from(G.selfloop_edges())
    while G.number_of_edges() > 0:
        yield _without_most_central_edges(G, most_valuable_edge)



def _without_most_central_edges(G, most_valuable_edge):
    original_num_components = nx.number_connected_components(G)
    num_new_components = original_num_components
    while num_new_components <= original_num_components:
        edge = most_valuable_edge(G)
        G.remove_edge(*edge)
        new_components = tuple(nx.connected_components(G))
        num_new_components = len(new_components)
    return new_components

def main():
    users_friends = get_users_friends(data_base_directory + tag_friends_file_name)
    graph = create_graph(users_friends)
    sub_graph = get_subgraph(graph, 2)
    draw_network(sub_graph, 'network.png')
    result = girvan_newman(sub_graph)
    communities = (tuple((c) for c in next(result)))
    unique_user = set()
    for user in users_friends:
        unique_user.add(user['screen_name'])
    with open(output_file_name, 'w') as f:
        f.write('Cluster results: ')
        f.write('\n\nNumber of users collected: ' + str(len(unique_user)))
        f.write('\nNumber of communities discovered: ' + str(len(communities)))
        total_users = 0
        for users in communities:
            total_users += len(users)
        if len(communities) > 0:
            f.write('\nAverage number of users per community: ' + str(total_users / len(communities)))
        else:
            f.write('\nAverage number of users per community: ' + str(0))
        f.write('\n\n')

if __name__ == '__main__':
    main()