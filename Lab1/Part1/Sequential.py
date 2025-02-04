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

def run_rover(rover_num):
    moves = list(json.loads(requests.get(base_url + str(i)).text)['data']['moves'])
    #print(moves)

    output = [[0 for _ in range(cols)] for _ in range(rows)]
    dug = [[0 for _ in range(cols)] for _ in range(rows)]

    output[0][0] = '*'
    x, y = 0, 0

    while moves:
        move = moves.pop(0)
        if move == 'L':
            new_x, new_y = x, y - 1

        elif move == 'R':
            new_x, new_y = x, y + 1

        elif move == 'M':
            new_x, new_y = x + 1, y
            
        elif move == 'D':
            dug[x][y] = 1
            #print('Mine Found!')
            continue
        else:
            print('Invalid Command')
        
        if 0 <= new_x < rows and 0 <= new_y < cols:
            if output[new_x][new_y] == "1":
                if dug[x][y] == 1:
                    print("Dig")
                    output[new_x][new_y] = "0"
                else:
                    print("Mine exploded")
                    output[new_x][new_y] = "0"
                    break

            # Move rover to new position
            x, y = new_x, new_y
            output[x][y] = "*"

            # print('\n')
            # for row in output:
            #     print(' '.join(map(str, row)))
            # print('\n')
            # if map_data[y][x] == 1:
            #     if dug[y][x] == 0:
            #         print(f'Mine Found! {x, y}')
            #         break
    
    return output


for i in range(1, numOfRovers + 1): 
    output = run_rover(i)
        
    # Printing the output nicely
    print(f'Rover {i}')
    for row in output:
        print(' '.join(map(str, row)))
    print('\n')
