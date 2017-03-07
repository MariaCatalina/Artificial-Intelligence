''' bot_clean '''
from __future__ import print_function

import sys
from copy import deepcopy
from itertools import izip

FILENAME = 'tests/test1.in'
INFINITY = 10000
UNDEFINED = -1


def dijkstra(graph, source, distances, prev):
    '''' calculate the minimum distances  '''

    queue = []
    for i in range(len(graph)):
        queue.append(i)
        distances.append(INFINITY)
        prev.append(UNDEFINED)

    distances[source] = 0
    while queue != []:

        min_val = INFINITY
        node = UNDEFINED
        for i, val in enumerate(queue):
            if distances[val] < min_val:
                min_val = distances[val]
                node = val

        queue.remove(node)

        for neighbor in range(len(graph)):
            if graph[node][neighbor] != 0:
                alt = distances[node] + graph[node][neighbor]

                if alt < distances[neighbor]:
                    distances[neighbor] = alt
                    prev[neighbor] = node


def get_route(prev, target):
    ''' create the route from start to target '''

    source = []
    while prev[target] != UNDEFINED:
        source.insert(0, target)
        target = prev[target]

    return source


def dirty_rooms(rooms):
    ''' create list with all dirty rooms '''
    list_rooms = []
    for i in rooms.keys():
        dictionary_room = rooms[i]
        if dictionary_room['state'] == 1:
            list_rooms.append(i)

    return list_rooms


def get_next_room(dist, dirty_rooms_list, rooms):
    '''get next room that can be cleaned  '''

    min_val = -1000
    room = UNDEFINED

    if len(dirty_rooms_list) == 1:
        room = dirty_rooms_list[0]
    else:
        for i, val in enumerate(dist):
            if i in dirty_rooms_list:
                report = float(rooms[i]['dim']) / (val + 1) # avoid dividing by 0

                if report > min_val:
                    min_val = report
                    room = i

    return room


def get_next_room_min(dist, dirty_rooms_list):
    '''get next room that has the minimum distance from the current position  '''

    min_val = INFINITY
    room = UNDEFINED

    if len(dirty_rooms_list) == 1:
        room = dirty_rooms_list[0]
    else:
        for i, val in enumerate(dist):
            if i in dirty_rooms_list:
                if min_val > val:
                    min_val = val
                    room = i

    return room


def pairwise(iterable):
    ''' generate pairs (x, y) '''

    parameter = iter(iterable)
    return izip(parameter, parameter)


def check_clean_room(substances, rooms):
    ''' verify if the robot contains enough substances '''

    list_subst = rooms['listSubst']
    for id_subst, val in pairwise(list_subst):
        if id_subst in substances.keys() and val > substances[id_subst]:
            return False

    return True


def decrease_substances(substances, room_substances):
    ''' decrease the numbers of substances that are used to clean the current room '''

    for subst_id, val in pairwise(room_substances):
        substances[subst_id] -= val


def get_deposit(distances, deposit_list):
    ''' return the closest deposit '''

    min_val = INFINITY
    room = UNDEFINED

    for i, val in enumerate(distances):
        if i in deposit_list and val < min_val:
            min_val = val
            room = i

    return room


def create_plan1(start, list_dirty_rooms, total_time, substances, rooms,
                 graph, total_substances, deposit_list, capacity, heuristic):

    ''' method return a plan and the score'''

    time = 0
    score = 0
    result_list = []

    while list_dirty_rooms != [] and time < total_time:

        distances = []
        prev_steps = []

        dijkstra(graph, start, distances, prev_steps)

        # in function of heuristic choose the perfect room
        if heuristic == 0:
            current_room = get_next_room(distances, list_dirty_rooms, rooms)
        else:
            current_room = get_next_room_min(distances, list_dirty_rooms)

        # if any room can't be cleaned then go to refill the robot
        if check_clean_room(substances, rooms[current_room]):
            next_hop = get_route(prev_steps, current_room)

            for i in next_hop:

                time += graph[start][i]
                result = 'Move(' + str(start) + ", " + str(i) + ")"
                result_list.append(result)

                if i == current_room:
                    decrease_substances(substances, rooms[current_room]['listSubst'])

                    result = 'Clean(' + str(i) + ")"
                    result_list.append(result)

                    time += rooms[current_room]['dim']
                    score += rooms[current_room]['dim']

                start = i

            list_dirty_rooms.remove(current_room)

        else:
            deposit = get_deposit(distances, deposit_list)
            next_hop = get_route(prev_steps, deposit)

            for i in next_hop:
                time += graph[start][i]

                result = 'Move(' + str(start) + ", " + str(i) + ")"
                result_list.append(result)

                if i == deposit:
                    result = 'Refill(' + str(i) + ")"
                    result_list.append(result)
                    time += 1

                    for j in range(total_substances):
                        substances[j] = capacity

                start = i

    return score, result_list


def makeplan(filename):
    ''' create plan '''

    open_file = open(filename, 'r')

    # read from file
    line_split = open_file.readline().split(" ")

    nr_graph = int(line_split[0])
    total_time = int(line_split[1])
    total_substances = int(line_split[2])
    capacity = int(line_split[3])
    nr_deposits = int(line_split[4])
    nr_rooms = int(line_split[5])
    nr_edges = int(line_split[6])
    start = int(line_split[7])

    # create substances dictionary= {1: C, 2: C, 3: C }
    substances = {}
    for i in range(total_substances):
        substances[i] = capacity

    deposit_list = []
    line_split = open_file.readline().split(" ")

    for i in range(nr_deposits):
        deposit_list.append(int(line_split[i]))

    # build graph
    graph = [[0 for i in range(nr_graph)] for j in range(nr_graph)]

    for edge in range(nr_edges):
        line_split = open_file.readline().split(" ")
        i = int(line_split[0])
        j = int(line_split[1])
        cost = int(line_split[2])
        graph[i][j] = cost
        graph[j][i] = cost

    # rooms = {id: _ , stare: _, dim: _, nrSubst: _, listSubst: []}
    rooms = {}
    for i in range(nr_rooms):
        line_split = open_file.readline().split(" ")

        id_room = int(line_split[0])
        state = int(line_split[1])
        dimension = int(line_split[2])
        nr_substances = int(line_split[3])

        list_substances = []
        for j in range(nr_substances * 2):
            list_substances.append(int(line_split[j + 4]))

        new_room = {'id': id_room,
                    'state': state,
                    'dim': dimension,
                    'nrSubst': nr_substances,
                    'listSubst': list_substances}

        rooms[id_room] = new_room

    list_dirty_rooms = dirty_rooms(rooms)

    (score1, result_list1) = create_plan1(start, deepcopy(list_dirty_rooms), total_time,
                                          deepcopy(substances), rooms, graph, total_substances,
                                          deposit_list, capacity, 0)

    (score2, result_list2) = create_plan1(start, deepcopy(list_dirty_rooms), total_time,
                                          deepcopy(substances), rooms, graph, total_substances,
                                          deposit_list, capacity, 1)

    if score1 > score2:
        return deepcopy(result_list1)
    else:
        return deepcopy(result_list2)


def main(argv):
    ''' main '''
    print(makeplan(FILENAME))


if __name__ == '__main__':
    main(sys.argv)
