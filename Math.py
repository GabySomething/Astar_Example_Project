import heapq
import multiprocessing
from math import sqrt, sin, pi
from time import time_ns

import numpy as np
from matplotlib.path import Path as mPath

CPU_NUMBER: int = multiprocessing.cpu_count()


def distance(a, b):
    return sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def pathfind(start, goal, grid: np.ndarray, disable_diagonal_movement=False):
    start = start[0], start[1]
    goal = goal[0], goal[1]
    if disable_diagonal_movement:
        movement = [(0, -1),  # UP
                    (-1, 0), (1, 0),  # SIDES
                    (0, 1)]  # DOWN
    else:
        movement = [(-1, -1), (0, -1), (1, -1),  # UP and corners
                    (-1, 0), (1, 0),  # SIDES
                    (-1, 1), (0, 1), (1, 1)]  # DOWN and corners
    closed_nodes = set()
    closed_nodes_list = []
    open_nodes = []
    g_score = {start: 0}
    f_score = {start: distance(start, goal)}
    origin = {}
    heapq.heappush(open_nodes, (f_score[start], start))
    t = time_ns()
    while open_nodes:
        c_node = heapq.heappop(open_nodes)[1]
        if c_node == goal:
            path = []
            while c_node in origin:
                path.append(c_node)
                c_node = origin[c_node]
            path.append(start)
            print(f'Done in {(time_ns() - t) / 10.0 ** 6}ms')
            return path[::-1], open_nodes, closed_nodes_list
        closed_nodes.add(c_node)
        closed_nodes_list.append(c_node)
        for x, y in movement:
            n_node = c_node[0] + x, c_node[1] + y
            g = g_score[c_node] + distance(c_node, n_node)
            if 0 <= n_node[0] < grid.shape[0]:
                if 0 <= n_node[1] < grid.shape[1]:
                    if grid[n_node[0]][n_node[1]]:
                        continue
                else:
                    continue
            else:
                continue
            if n_node in closed_nodes and g >= g_score.get(n_node, 0):
                continue
            if g < g_score.get(n_node, 0) or n_node not in [node[1] for node in open_nodes]:
                origin[n_node] = c_node
                g_score[n_node] = g
                f_score[n_node] = g + distance(n_node, goal)
                heapq.heappush(open_nodes, (f_score[n_node], n_node))


def Poly_Area_Sep(x: np.ndarray, y: np.ndarray):
    if type(x) != np.ndarray:
        x = np.asarray(x)
    if type(y) != np.ndarray:
        y = np.asarray(y)
    return 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))


def Poly_Area(points):
    return Poly_Area_Sep(*zip(*points))


def print_grid(grid):
    for row in grid:
        print(row)


def create_grid_with_collisions(width: int, height: int, *obs: mPath):
    x = np.linspace(0, width - 1, width, dtype=int)
    y = np.linspace(0, height - 1, height, dtype=int)
    points = np.asarray(np.meshgrid(x, y)).T.reshape(-1, 2)
    result = np.zeros(width * height, dtype=int)
    for obj in obs:
        result += obj.contains_points(points).astype(int)
    return np.array_split(result, width)
