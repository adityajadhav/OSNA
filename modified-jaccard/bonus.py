import networkx as nx


def jaccard_wt(graph, node):
  """
  The weighted jaccard score, defined above.
  Args:
    graph....a networkx graph
    node.....a node to score potential new edges for.
  Returns:
    A list of ((node, ni), score) tuples, representing the 
              score assigned to edge (node, ni)
              (note the edge order)
  """
  result = []
  for n in graph.nodes():
      if n not in graph.neighbors(node) and n != node:
          common = set(graph.neighbors(node)) & set(graph.neighbors(n))
          common_score=0
          for node_common in common:
              node_common_degree = graph.degree(node_common)
              common_score = common_score + (1/ node_common_degree)
          neighbor_score_node,neighbor_score_n=0,0
          for neighbor_node in set(graph.neighbors(node)):
              neighbor_score_node = neighbor_score_node + graph.degree(neighbor_node)
          for neighbor_n in set(graph.neighbors(n)):
              neighbor_score_n = neighbor_score_n + graph.degree(neighbor_n)
          jaccard_score = common_score / ((1/neighbor_score_node) + (1/neighbor_score_n))
          result.append(((node, n), jaccard_score))
  result = sorted(result, key=lambda a: (-a[1], a[0][1]))
  return result


def example_graph():
    """
    I have referred to the graph from class to test the output.
    """
    g = nx.Graph()
    g.add_edges_from([('A', 'B'), ('A', 'C'), ('B', 'C'), ('B', 'D'), ('D', 'E'), ('D', 'F'), ('D', 'G'), ('E', 'F'), ('G', 'F')])
    return g


def main():
    graph = example_graph()
    for node in graph.nodes():
        print("Node to score potential new edges for:" , node,jaccard_wt(graph,node))

if __name__ == '__main__':
    main()
