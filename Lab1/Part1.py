import requests
import json
import os

base_url = 'https://coe892.reev.dev/lab1/rover/'
numOfRovers = 10
mapFilename = 'map1.txt'
minesFilename = 'mines.txt'
rows, cols = 0, 0
map_data = []
outputBase = 'SequentialOutput'

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

# Extract rows and columns and the map from the map file
with open(mapFilename, 'r') as f:
    rows, cols = [int(x) for x in f.readline().split()]
    map_data = f.readlines()

    # Split mapdata into 2d array
    map_data = [list(map(int, row.strip().split())) for row in map_data]

# Create the Ouput Folder
try:
    os.mkdir(outputBase)
except FileExistsError:
    pass

def run_rover(rover_num, map_data_cpy):
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
                        map_data_cpy[x][y - 1] = 0
                        y -= 1
                        output[x][y] = '*'
                        continue
                    
                    y -= 1
                    map_data_cpy[x][y] = 0
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
                        map_data_cpy[x][y + 1] = 0
                        y += 1
                        output[x][y] = '*'
                        continue
                    
                    y += 1
                    map_data_cpy[x][y] = 0
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
                        map_data_cpy[x + 1][y] = 0
                        x += 1
                        output[x][y] = '*'
                        continue
                    
                    x += 1
                    map_data_cpy[x][y] = 0
                    output[x][y] = '*'
                    break
                else:
                    x += 1
                    output[x][y] = '*'
    
    return output


map_data_copy = map_data.copy()
for i in range(1, numOfRovers + 1): 
    output = run_rover(i, map_data_copy)        
    # Printing the output nicely
    print(f'Rover {i}')
    for row in output:
        print(' '.join(map(str, row)))
    print('\n')
