from typing import Iterable, Iterator, Tuple, TypeVar, Generic, Union, Any

T = TypeVar('T')


class BaseGraph(Generic[T]):
    def __init__(self):
        self.nodes: list[T] = []
        self.edges = []

    def add_node(self, node: T):
        self.nodes.append(node)

    def add_edge(self, from_node, to_node, **kwargs):
        self.edges.append((from_node, to_node, kwargs))

    def add_nodes_from(self, nodes: Iterable[T]):
        for node in nodes:
            self.add_node(node)

    def in_edges(self, node: T, data: bool = False) -> Iterator[Union[Tuple[T, T], Tuple[T, T, dict[str, Any]]]]:
        for from_node, to_node, edge_data in self.edges:
            if to_node == node:
                if data:
                    yield (from_node, to_node, edge_data)
                else:
                    yield (from_node, to_node)
