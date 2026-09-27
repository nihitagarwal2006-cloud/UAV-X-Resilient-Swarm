import math


class WorldPlanner:
    """Straight-line POC planner for the official open GC1 arena.

    The arena has no obstacle geometry in the supplied GC1 sample scenario.
    The planner therefore generates a continuous path target while the
    mission controller enforces the swarm separation constraint.
    """

    def plan(self, start, goal, step_m=25.0):
        sx, sy = start
        gx, gy = goal
        distance = math.hypot(gx - sx, gy - sy)
        count = max(1, int(math.ceil(distance / step_m)))
        return [
            (sx + (gx - sx) * i / count, sy + (gy - sy) * i / count)
            for i in range(1, count + 1)
        ]
