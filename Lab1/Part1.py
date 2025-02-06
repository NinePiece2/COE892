import requests
import json
import os
import threading
import time

base_url = 'https://coe892.reev.dev/lab1/rover/'
numOfRovers = 10
mapFilename = 'map1.txt'
minesFilename = 'mines.txt'
rows, cols = 0, 0
map_data = []
seqOutputBase = 'SequentialOutput'
paraOutputBase = 'ParallellOutput'

# Enumerate Direction
# Down - 0
# Right - 1
# Up - 2
# Left - 3
direction = 0

# Rover leaves where mine is without digging it explodes and all subsequent commands are ignored
# Write assumptions in lab report

# 1st Output
# * 1 0
# * 0 0
# * 0 0
# 0 0 0

# Assumptions
# 1. Rover starts at 0,0 and is facing down (South)
# 2. Rover can move in 3 directions (Left, Right, Down)
#   In the lab manual: L - Left, R - Right, M - Move
#   Assumes that L and R also move the rover and they are relative to the map such that a left move will always move the rover to the left of the current position
#   and a right move will always move the rover to the right of the current position.
# 3. Rovers are run independently, that is to say a previous rover's path does not affect the next rover's path
# 4. If a rover encounters a mine and does not dig it up the rover will explode and all subsequent commands are ignored
# 5. If a rover encounters a mine and digs it up the rover will continue to move in the direction specified by the next command


# Extract rows and columns and the map from the map file
with open(mapFilename, 'r') as f:
    rows, cols = [int(x) for x in f.readline().split()]
    map_data = f.readlines()

    # Split mapdata into 2d array
    map_data = [list(map(int, row.strip().split())) for row in map_data]

# Create the Ouput Folder
try:
    os.mkdir(seqOutputBase)
except FileExistsError:
    pass

try:
    os.mkdir(paraOutputBase)
except FileExistsError:
    pass

def run_rover(rover_num, map_data_cpy, sequential=True):
    moves = list(json.loads(requests.get(base_url + str(rover_num)).text)['data']['moves'])
    #print(moves)

    output = [[0 for _ in range(cols)] for _ in range(rows)]

    output[0][0] = '*'
    x, y = 0, 0

    currentPointer = 0
    for move in moves:
        digThisSpot = moves[currentPointer + 1]

        if currentPointer < len(moves) - 2:
            currentPointer += 1

        isDug = 0
        if digThisSpot == 'D':
            isDug = 1

        if move == 'L':
            if (x < 0) or (x >= rows) or (y - 1 < 0) or (y - 1>= cols):
                pass

            else:
                if map_data_cpy[x][y - 1] == 1:
                    if isDug:
                        #map_data_cpy[x][y - 1] = 0
                        y -= 1
                        output[x][y] = '*'
                        continue
                    
                    y -= 1
                    #map_data_cpy[x][y] = 0
                    output[x][y] = '*'
                    break
                else:
                    y -= 1
                    output[x][y] = '*'
                
        elif move == 'R':
            if (x < 0) or (x >= rows) or (y + 1 < 0) or (y + 1 >= cols):
                pass

            else:
                if map_data_cpy[x][y + 1] == 1:
                    if isDug:
                        #map_data_cpy[x][y + 1] = 0
                        y += 1
                        output[x][y] = '*'
                        continue
                    
                    y += 1
                    #map_data_cpy[x][y] = 0
                    output[x][y] = '*'
                    break
                else:
                    y += 1
                    output[x][y] = '*'

        elif move == 'M':
            if (x + 1 < 0) or (x + 1 >= rows) or (y < 0) or (y >= cols):
                pass

            else:
                if map_data_cpy[x + 1][y] == 1:
                    if isDug:
                        #map_data_cpy[x + 1][y] = 0
                        x += 1
                        output[x][y] = '*'
                        continue
                    
                    x += 1
                    #map_data_cpy[x][y] = 0
                    output[x][y] = '*'
                    break
                else:
                    x += 1
                    output[x][y] = '*'
    if sequential:
        with open(f'{seqOutputBase}/path_{rover_num}.txt', 'w') as f:
            for row in output:
                f.write(' '.join(map(str, row)) + '\n')
    else:
        with open(f'{paraOutputBase}/path_{rover_num}.txt', 'w') as f:
            for row in output:
                f.write(' '.join(map(str, row)) + '\n')


initial_time = time.time()
map_data_copy = map_data.copy()
for i in range(1, numOfRovers + 1): 
    run_rover(i, map_data_copy)        
    
final_time = time.time()

print(f'Sequential Time: {final_time-initial_time}')

thread_list = []
initial_time = time.time()
map_data_copy = map_data.copy()
for i in range(1, numOfRovers + 1): 
    thread = threading.Thread(target=run_rover, args=(i, map_data_copy, False))
    thread_list.append(thread)
    thread.start()

for i in range(numOfRovers):
    thread_list[i].join()

final_time = time.time()
print(f'Parallel Time: {final_time-initial_time}')