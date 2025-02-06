import requests
import json
import os
import threading
import time
import hashlib
import itertools
import string
import copy  # Import copy module to create deep copies

base_url = 'https://coe892.reev.dev/lab1/rover/'
numOfRovers = 10
mapFilename = 'map1.txt'
minesFilename = 'mines.txt'
rows, cols = 0, 0
map_data = []
seqOutputBase = 'SequentialOutput'
paraOutputBase = 'ParallelOutput'

def load_mines(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f.readlines()]

def find_valid_pin(serial_number):
    charset = string.ascii_letters + string.digits
    for length in range(1, 6):  # Limiting PIN length to 5 for efficiency
        for pin in itertools.product(charset, repeat=length):
            pin = ''.join(pin)
            temp_key = serial_number + pin
            hash_value = hashlib.sha256(temp_key.encode()).hexdigest()
            if hash_value.startswith('000000'):
                return pin
    return None

mines = load_mines(minesFilename)

with open(mapFilename, 'r') as f:
    rows, cols = [int(x) for x in f.readline().split()]
    map_data = [list(map(int, row.strip().split())) for row in f.readlines()]

def run_rover(rover_num, map_data_cpy, mines_cpy):
    moves = list(json.loads(requests.get(base_url + str(rover_num)).text)['data']['moves'])
    output = [[0 for _ in range(cols)] for _ in range(rows)]
    output[0][0] = '*'
    x, y = 0, 0
    currentPointer = 0
    for move in moves:
        digThisSpot = moves[currentPointer + 1] if currentPointer < len(moves) - 2 else ''
        isDug = digThisSpot == 'D'

        if move == 'L' and y > 0:
            y -= 1
        elif move == 'R' and y < cols - 1:
            y += 1
        elif move == 'M' and x < rows - 1:
            x += 1
        
        if map_data_cpy[x][y] == 1:  # Mine detected
            if isDug:
                serial_number = mines_cpy.pop(0) if mines_cpy else 'UNKNOWN'
                pin = find_valid_pin(serial_number)
                if pin:
                    map_data_cpy[x][y] = 0  # Mine disarmed
                    output[x][y] = '*'
                    continue
            output[x][y] = '*'
            break  # Rover explodes
        output[x][y] = '*'
        currentPointer += 1

# Sequential Execution
initial_time = time.time()
for i in range(1, numOfRovers + 1):
    map_data_copy = copy.deepcopy(map_data)
    mines_copy = list(mines)  # Independent copy for each rover
    run_rover(i, map_data_copy, mines_copy)
print(f'Sequential Time: {time.time() - initial_time}')

# Parallel Execution
thread_list = []
initial_time = time.time()
for i in range(1, numOfRovers + 1):
    map_data_copy = copy.deepcopy(map_data)  # Unique copy per thread
    mines_copy = list(mines)  # Unique mine list per thread
    thread = threading.Thread(target=run_rover, args=(i, map_data_copy, mines_copy))
    thread_list.append(thread)
    thread.start()

for thread in thread_list:
    thread.join()
print(f'Parallel Time: {time.time() - initial_time}')
