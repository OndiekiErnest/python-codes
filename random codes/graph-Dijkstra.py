
""" priority queue will be used to sort the vertices
    that haven't been visited yet, shortest cost first
"""
from queue import PriorityQueue


class Graph():

    def __init__(self, num_of_vertices):
        self.v = num_of_vertices
        self.edges = [[-1 for i in range(self.v)] for j in range(self.v)]
        self.visited = []

    def add_edge(self, u, v, weight):
        """ add an edge to the graph """
        self.edges[u][v] = weight
        self.edges[v][u] = weight

    def dijkstra(self, start_vertex) -> dict:
        """ find the shortest paths between nodes in the graph """
        # D keeps the shortest paths from start_vertex
        # initialize D values to infinity
        D = {v: float("inf") for v in range(self.v)}
        # distance from self is 0
        D[start_vertex] = 0
        pq = PriorityQueue()
        # (cost, vertex)
        pq.put((0, start_vertex))

        while not pq.empty():
            cost, current_vertex = pq.get()
            self.visited.append(current_vertex)

            for neighbour in range(self.v):
                if self.edges[current_vertex][neighbour] != -1:
                    distance = self.edges[current_vertex][neighbour]
                    if neighbour not in self.visited:
                        old_cost = D[neighbour]
                        new_cost = D[current_vertex] + distance
                        if new_cost < old_cost:
                            pq.put((new_cost, neighbour))
                            D[neighbour] = new_cost
        return D


if __name__ == '__main__':
    g = Graph(9)
    data = ((0, 1, 4), (0, 6, 7), (1, 6, 11),
            (1, 7, 20), (1, 2, 9), (2, 3, 6),
            (2, 4, 2), (3, 4, 10), (3, 5, 5),
            (4, 5, 15), (4, 7, 1), (4, 8, 5),
            (5, 8, 12), (6, 7, 1), (7, 8, 3))
    for vertex_u, vertex_v, weight in data:
        g.add_edge(vertex_u, vertex_v, weight)
    print(g.edges)
    D = g.dijkstra(0)
    for vertex in range(len(D)):
        print("Shortest distance from vertex 0 to vertex",
              vertex, "is", D[vertex])
