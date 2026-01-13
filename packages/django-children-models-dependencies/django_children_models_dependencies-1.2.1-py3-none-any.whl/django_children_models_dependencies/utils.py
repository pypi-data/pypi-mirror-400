"""Utils functions to compute a dependencies graph."""

from collections import OrderedDict, defaultdict

from .exceptions import CircularRelationshipException, UnresolvableDependenciesTree

DUMMY_NODE = "=(^_^)="


def graph_from_edges(edges):
    """
    return a graph from a set of edges
    edges are a 2tuple in the form of (from_node, to_node)
    Copied from digraphtools
    """
    # pylint: disable=invalid-name
    graph = defaultdict(set)
    for a, b in edges:
        graph[a].add(b)
        # pylint: disable=pointless-statement
        graph[b]  # seems not used, but it is set because of the use of `defaultdict`

    # replaced `list` by `sorted` to always have the same order
    return {a: sorted(b) for a, b in graph.items()}


def postorder_traversal(graph, root):
    """
    Traverse a graph post-order and yield a list of nodes
    Copied from digraphtools
    """
    # pylint: disable=invalid-name
    if root in graph:
        for n in graph[root]:
            yield from postorder_traversal(graph, n)
    yield root


def compute_dependencies_order(dependencies):
    """
    Get the dependencies in this order: starts with entries without dependencies
    """

    # First we need to add a dummy dependency "on top" to make sure we have
    # a single tree.
    from_nodes = [model for model, __ in dependencies]
    dependencies.append((DUMMY_NODE, from_nodes))

    # Now we build the list of dependency relationships... (a list of (from, to) pairs)
    relationships = [(from_node, node) for from_node, nodes in dependencies for node in nodes]

    # ... from which we can build a list of unique dependencies nodes...
    all_nodes = set(sum(relationships, ()))

    # .. and create the dependencies tree, as a directed acyclic graph.
    tree = graph_from_edges(relationships)

    # The call to `postorder_traversal(graph, node)` returns
    # the ordered list of nodes to traverse from a starting node to reach
    # the end of a dependencies chain.
    try:
        chain = list(postorder_traversal(tree, DUMMY_NODE))
    except RuntimeError:
        raise CircularRelationshipException(
            f"Unable to traverse the dependencies tree, please check for potential circular relationships:\n{tree}"
        ) from None

    # We check that the chain really contains all the nodes of the tree.
    if all_nodes.difference(chain):
        raise UnresolvableDependenciesTree(
            f"Unable to resolve the dependencies tree, please check for potential problem:\n{tree}"
        )

    # The chain may still contain multiple occurences of the same node. Each
    # dependency only needs to be processed once, so we may safely discard all
    # duplicates, as long as we preserve the global order. This efficient way of
    # doing so is explained here: http://stackoverflow.com/questions/480214#17016257

    # We remove the dummy node at the end of the chain.
    chain.pop()

    # And return the properly ordered list.
    return list(OrderedDict.fromkeys(chain))
