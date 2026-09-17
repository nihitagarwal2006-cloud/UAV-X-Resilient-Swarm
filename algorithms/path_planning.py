import networkx as nx


class AStarPlanner:

    def __init__(self, width=20, height=20):
        self.width = width
        self.height = height

    def create_graph(self, obstacles):

        graph = nx.grid_2d_graph(self.width, self.height)

        for obstacle in obstacles:
            if obstacle in graph:
                graph.remove_node(obstacle)

        return graph

    def plan(self, start, goal, obstacles=None):

        if obstacles is None:
            obstacles = []

        graph = self.create_graph(obstacles)

        if start not in graph or goal not in graph:
            return []

        try:
            path = nx.astar_path(
                graph,
                start,
                goal,
                heuristic=lambda a, b: abs(a[0] - b[0]) + abs(a[1] - b[1])
            )

            return path

        except nx.NetworkXNoPath:
            return []