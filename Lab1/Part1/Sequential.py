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


for i in range(1, numOfRovers + 1):
    # Get Rover Commands using the API
    response = requests.get(base_url + str(i))
    commands = json.loads(response.text)
    moves = commands['data']['moves']
    moves = list(moves)
    print(moves)
    output = [[0 for _ in range(cols)] for _ in range(rows)]
    dug = [[0 for _ in range(cols)] for _ in range(rows)]
    output[0][0] = '*'
    x, y = 0, 0
    direction = 0
    while moves:
        move = moves.pop(0)
        if move == 'L':
            if direction == 0:
                direction = 1
            elif direction == 1:
                direction = 2
            elif direction == 2:
                direction = 3
            elif direction == 3:
                direction = 0
            
            direction = 3
        elif move == 'R':
            if direction == 0:
                direction = 3
            elif direction == 1:
                direction = 0
            elif direction == 2:
                direction = 1
            elif direction == 3:
                direction = 2

            direction = 1
        elif move == 'M':
            if direction == 0:
                y+=1
            elif direction == 1:
                x+=1
            elif direction == 2:
                y-=1
            elif direction == 3:
                x-=1
            if x < 0 or y < 0 or x >= cols or y >= rows:
                if x >= cols:
                    x-=1
                elif y >= rows:
                    y-=1
                elif x < 0:
                    x+=1
                elif y < 0:
                    y+=1
                
                print(x, y)
            else:
                output[y][x] = '*'
                print('\n')
                for row in output:
                    print(' '.join(map(str, row)))
                print('\n')
                if map_data[y][x] == 1:
                    if dug[y][x] == 0:
                        print(f'Mine Found! {x, y}')
                        break
        elif move == 'D':
            dug[y][x] = 1
            #print('Mine Found!')
            continue
        else:
            print('Invalid Command')
        
    # Printing the output nicely
    for row in output:
        print(' '.join(map(str, row)))
