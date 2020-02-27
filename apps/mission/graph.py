import json
import logging
from math import sqrt

import networkx as nx

from ifc.models import IfcModel


logger = logging.getLogger(__name__)



def set_if_possible(matrix, x, y, val):
    if y >= len(matrix) or x >= len(matrix[y]):
        return
    matrix[y][x] = val



def stretch(matrix, x, y, dist, val=1):
    if dist == 0 or y >= len(matrix) or x >= len(matrix[y]):
        return
    pos = [(x + dist, y), (x - dist, y), (x, y + dist), (x, y - dist)]
    for xd, yd in pos:
        set_if_possible(matrix, xd, yd, val)



def to_x_y(coord, div):
    return int(coord[0] // div), int(coord[1] // div)



def points_on_polygons_gen(all_polygons, div):
    for polygons in all_polygons:
        for ipt in range(-1, len(polygons) - 1):
            cur_x, cur_y = to_x_y(polygons[ipt], div)
            nxt_x, nxt_y = to_x_y(polygons[ipt + 1], div)
            if cur_y == nxt_y:
                for pace_x in range(min(cur_x, nxt_x), max(cur_x, nxt_x)):
                    yield pace_x, -cur_y
            else:
                for pace_y in range(min(cur_y, nxt_y), max(cur_y, nxt_y)):
                    yield cur_x, -pace_y



def create_graph(data, size):
    graph = nx.Graph()
    
    for y in range(len(data)):
        for x in range(len(data[y])):
            if not data[y][x]:
                if y + 1 < len(data) and not data[y + 1][x]:
                    graph.add_edge((x * size, y * size),
                                   (x * size, (y + 1) * size), weight=1)
                if y - 1 >= 0 and not data[y - 1][x]:
                    graph.add_edge((x * size, y * size),
                                   (x * size, (y - 1) * size), weight=1)
                if x + 1 < len(data[y]) and not data[y][x + 1]:
                    graph.add_edge((x * size, y * size),
                                   ((x + 1) * size, y * size), weight=1)
                if x - 1 >= 0 and not data[y][x - 1]:
                    graph.add_edge((x * size, y * size),
                                   ((x - 1) * size, y * size), weight=1)
                # diagonals
                if y + 1 < len(data) and x + 1 < len(data[y]) and not data[y + 1][x + 1]:
                    graph.add_edge((x * size, y * size),
                                   ((x + 1) * size, (y + 1) * size), weight=sqrt(2))
                if y - 1 >= 0 and x + 1 < len(data[y]) and not data[y - 1][x + 1]:
                    graph.add_edge((x * size, y * size),
                                   ((x + 1) * size, (y - 1) * size), weight=sqrt(2))
                if y + 1 < len(data) and x - 1 >= 0 and not data[y + 1][x - 1]:
                    graph.add_edge((x * size, y * size),
                                   ((x - 1) * size, (y + 1) * size), weight=sqrt(2))
                if y - 1 >= 0 and x - 1 >= 0 and not data[y - 1][x - 1]:
                    graph.add_edge((x * size, y * size),
                                   ((x - 1) * size, (y - 1) * size), weight=sqrt(2))
    return graph



def reduce(matrix, size):
    data = [[0] * (len(matrix[0])) for _ in range(len(matrix))]
    for y in range(0, len(matrix), size):
        block = matrix[y:y + size]
        for x in range(0, len(matrix[0]), size):
            for k in range(len(block)):
                if any(block[k][x:x + size]):
                    data[y // size][x // size] = 1
                    break
    return data



def create_turn_action(cur_dir, nxt_dir, directions):
    angle_turn = 360 // len(directions)
    if cur_dir == nxt_dir:
        return 0
    turn = 0
    for i in range(1, len(directions)):
        if (cur_dir + i) % len(directions) == nxt_dir:
            turn = i
            break
        if (cur_dir - i) % len(directions) == nxt_dir:
            turn = -i
            break
    angle = turn * angle_turn
    if angle > 180:
        angle = -(angle - 180)
    return angle



def create_move_action(cur_pos, nxt_pos):
    c_x, c_y = cur_pos
    n_x, n_y = nxt_pos
    distance = sqrt((c_x - n_x)**2 + (c_y - n_y)**2)
    # 10 multiplication to pass from centimeter to millimeter distance
    return distance * 10



def create_actions_path(path, directions, all_actions):
    direction = directions["NORTH"]
    actions = []
    lst_pos = path[0]
    for i in range(1, len(path)):
        nxt_x, nxt_y = path[i]
        lst_x, lst_y = path[i - 1]
        dir_x, dir_y = nxt_x - lst_x, nxt_y - lst_y
        direction_name = ""
        if dir_y > 0:
            direction_name = direction_name + "SOUTH"
        elif dir_y < 0:
            direction_name = direction_name + "NORTH"
        if dir_x > 0:
            direction_name = direction_name + "EAST"
        elif dir_x < 0:
            direction_name = direction_name + "WEST"
        way = directions[direction_name]
        if direction != way:
            if i > 1:
                actions.append(all_actions["MOVE"](lst_pos, path[i - 1]))
                lst_pos = path[i - 1]
            actions.append(all_actions["TURN"](direction, way))
            direction = way
    actions.append(all_actions["MOVE"](lst_pos, path[-1]))
    return actions



def create_matrix(ifc, floor, cell_div, stretch_size):
    data = json.loads(ifc.data)
    spaces_polygons = data[floor]["spacesPolygons"]
    doors_polygons = data[floor]["doorsPolygons"]
    width = int(abs(data["x_max"] - data["x_min"]))+1 // cell_div
    height = int(abs(data["y_max"] - data["y_min"]))+1 // cell_div
    m = [[0] * width for _ in range(height)]
    walls_points = []
    # add walls
    for x, y in points_on_polygons_gen(spaces_polygons.values(), cell_div):
        m[y][x] = 1
        walls_points.append((x, y))
    
    # remove points on doors to create passages
    door_way_points = []
    door_board_points = []
    for x, y in points_on_polygons_gen(doors_polygons.values(), cell_div):
        if m[y][x]:
            door_way_points.append((x, y))
            m[y][x] = 0
        else:
            door_board_points.append((x, y))
            m[y][x] = 1
    
    # stretch all walls
    for x, y in points_on_polygons_gen(spaces_polygons.values(), cell_div):
        stretch(m, x, y, stretch_size)
    
    # stretch door boards
    # dist shouldn't have to be changed here
    for x, y in door_board_points:
        stretch(m, x, y, stretch_size)
    
    # unstretch door ways
    for x, y in door_way_points:
        stretch(m, x, y, stretch_size, val=0)
    
    # reduce to CELL_DIV size
    m = reduce(m, cell_div)
    
    return m



def actions_from_ifc(ifc_id, floor, source, target, robot_config):
    ifc = IfcModel.objects.get(id=ifc_id)
    
    cell_div = robot_config["cell_div"]
    stretch_size = robot_config["stretch_size"]
    directions = {
        "WEST":      0,
        "NORTHWEST": 1,
        "NORTH":     2,
        "NORTHEAST": 3,
        "EAST":      4,
        "SOUTHEAST": 5,
        "SOUTH":     6,
        "SOUTHWEST": 7
    }
    
    actions = {
        "TURN": lambda cur_dir, nxt_dir: ("T", create_turn_action(cur_dir, nxt_dir, directions)),
        "MOVE": lambda cur_pos, nxt_pos: ("M", create_move_action(cur_pos, nxt_pos))
    }
    
    # create final graph
    m = create_matrix(ifc, floor, cell_div, stretch_size)
    graph = create_graph(m, cell_div)
    
    # find path between two points
    path = nx.algorithms.shortest_paths.generic.shortest_path(
        graph, source=source, target=target, weight="weight")
    
    return create_actions_path(path, directions, actions)
