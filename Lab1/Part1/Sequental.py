import requests
import json
import os

base_url = 'https://coe892.reev.dev/lab1/rover/'
numOfRovers = 10
mapFilename = 'map1.txt'
minesFilename = 'mines.txt'
rows, cols = 0, 0
map_data = []
outputBase = 'SequentalOutput'

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
    print(rows, cols)
    print(map_data)

# Create the Ouput Folder
try:
    os.mkdir(outputBase)
except FileExistsError:
    pass

for i in range(1, 2):#numOfRovers + 1):
    # Get Rover Commands using the API
    response = requests.get(base_url + str(i))
    commands = json.loads(response.text)
    moves = commands['data']['moves']
    moves = list(moves)
    output = []
    print(moves)
    while moves:
        move = moves.pop(0)
        print(move)
        # Implement the move
        if move == 'L':
            print('L')
        elif move == 'R':
            print('R')
        elif move == 'M':
            print('M')
        elif move == 'D':
            print('Mine Found!')
        else:
            print('Invalid Command')
    
