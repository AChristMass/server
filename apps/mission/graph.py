import logging

import networkx as nx
from math import sqrt


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



def points_on_polygons_gen(all_polygons, x_min, y_min):
    for polygons in all_polygons:
        for ipt in range(-1, len(polygons) - 1):
            cur_x, cur_y = int(polygons[ipt][0]), int(polygons[ipt][1])
            nxt_x, nxt_y = int(polygons[ipt + 1][0]), int(polygons[ipt + 1][1])
            if cur_y == nxt_y:
                for pace_x in range(min(cur_x, nxt_x), max(cur_x, nxt_x)):
                    yield pace_x - x_min, cur_y - y_min
            else:
                for pace_y in range(min(cur_y, nxt_y), max(cur_y, nxt_y)):
                    yield cur_x - x_min, pace_y - y_min



def create_graph(data, size, x_min, y_min):
    graph = nx.Graph()
    add_edge = lambda x1, y1, x2, y2, w: graph.add_edge((x1 * size + x_min, y1 * size + y_min),
                                                        (x2 * size + x_min, y2 * size + y_min),
                                                        weight=w)
    
    for y in range(len(data)):
        for x in range(len(data[y])):
            if not data[y][x]:
                if y + 1 < len(data) and not data[y + 1][x]:
                    add_edge(x, y, x, (y + 1), 1)
                if y - 1 >= 0 and not data[y - 1][x]:
                    add_edge(x, y, x, (y - 1), 1)
                if x + 1 < len(data[y]) and not data[y][x + 1]:
                    add_edge(x, y, (x + 1), y, 1)
                if x - 1 >= 0 and not data[y][x - 1]:
                    add_edge(x, y, (x - 1), y, 1)
                # diagonals
                if y + 1 < len(data) and x + 1 < len(data[y]) and not data[y + 1][x + 1]:
                    add_edge(x, y, (x + 1), (y + 1), sqrt(2))
                if y - 1 >= 0 and x + 1 < len(data[y]) and not data[y - 1][x + 1]:
                    add_edge(x, y, (x + 1), (y - 1), sqrt(2))
                if y + 1 < len(data) and x - 1 >= 0 and not data[y + 1][x - 1]:
                    add_edge(x, y, (x - 1), (y + 1), sqrt(2))
                if y - 1 >= 0 and x - 1 >= 0 and not data[y - 1][x - 1]:
                    add_edge(x, y, (x - 1), (y - 1), sqrt(2))
    return graph



def reduce(matrix, size):
    data = [[0] * (len(matrix[0]) // size + 1) for _ in range(len(matrix) // size + 1)]
    
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



def create_actions_and_finalpath(path, directions, all_actions):
    direction = directions["NORTH"]
    actions = []
    lst_pos = path[0]
    final_path = [lst_pos]
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
                final_path.append(path[i - 1])
                actions.append(all_actions["MOVE"](lst_pos, path[i - 1]))
                lst_pos = path[i - 1]
            actions.append(all_actions["TURN"](direction, way))
            direction = way
    actions.append(all_actions["MOVE"](lst_pos, path[-1]))
    return final_path, actions



def create_matrix(ifc_data, floor, cell_div, stretch_size):
    data = ifc_data
    spaces_polygons = data["floors"][floor]["spacesPolygons"]
    doors_polygons = data["floors"][floor]["doorsPolygons"]
    x_min = int(data["dimensions"]["xMin"])
    y_min = int(data["dimensions"]["yMin"])
    width = int(data["dimensions"]["xMax"] - data["dimensions"]["xMin"])
    height = int(data["dimensions"]["yMax"] - data["dimensions"]["yMin"])
    m = [[0] * (width + 1) for _ in range(height + 1)]
    walls_points = []
    # add walls
    for x, y in points_on_polygons_gen(spaces_polygons.values(), x_min, y_min):
        m[y][x] = 1
        walls_points.append((x, y))
    
    # remove points on doors to create passages
    door_way_points = []
    door_board_points = []
    for x, y in points_on_polygons_gen(doors_polygons.values(), x_min, y_min):
        if m[y][x]:
            door_way_points.append((x, y))
            m[y][x] = 0
        else:
            door_board_points.append((x, y))
            m[y][x] = 1
    
    # stretch all walls
    for x, y in points_on_polygons_gen(spaces_polygons.values(), x_min, y_min):
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



def actions_and_path_from_ifc(ifc_data, floor, source, target, robot_config):
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
    m = create_matrix(ifc_data, floor, cell_div, stretch_size)
    graph = create_graph(m, cell_div, int(ifc_data["dimensions"]["xMin"]),
                         int(ifc_data["dimensions"]["yMin"]))
    # find path between two points
    
    path = nx.algorithms.shortest_paths.generic.shortest_path(
        graph, source=source, target=target, weight="weight")
    
    return create_actions_and_finalpath(path, directions, actions)
