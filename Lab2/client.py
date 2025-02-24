import grpc
import messaging_pb2
import messaging_pb2_grpc
import threading
import time
import os
import string
import hashlib
import itertools

def parse_map(map_str):
    lines = map_str.strip().splitlines()
    header = lines[0].split()
    rows, cols = int(header[0]), int(header[1])
    grid = []
    for line in lines[1:]:
        grid.append([int(x) for x in line.split()])
    return rows, cols, grid

def find_valid_pin(serial_number):
    charset = string.ascii_letters + string.digits
    for length in range(1, 6):
        for pin in itertools.product(charset, repeat=length):
            pin = ''.join(pin)
            temp_key = serial_number + pin
            hash_value = hashlib.sha256(temp_key.encode()).hexdigest()
            if hash_value.startswith('000000'):
                return pin
    return None

def run_rover(rover_num):
    print(f"Rover {rover_num} starting.")
    
    channel = grpc.insecure_channel('localhost:50051')
    stub = messaging_pb2_grpc.RoverServiceStub(channel)
    
    map_response = stub.GetMap(messaging_pb2.Null())
    rows, cols, grid = parse_map(map_response.map)

    output = [['0' for _ in range(cols)] for _ in range(rows)]
    output[0][0] = '*' 
    x, y = 0, 0

    command_stream = stub.GetCommandStream(messaging_pb2.CommandRequest(rover_num=rover_num))
    commands = [cmd.command for cmd in command_stream]

    success = True
    message = f"Rover {rover_num} executed all commands successfully."
    i = 0

    while i < len(commands) - 1:
        move = commands[i]
        dig_flag = commands[i+1]
        i += 1

        next_x, next_y = x, y
        if move == 'L':
            next_y -= 1
        elif move == 'R':
            next_y += 1
        elif move == 'M':
            next_x += 1
        else:
            continue

        # Check if the next move is within the map boundaries.
        if not (0 <= next_x < rows and 0 <= next_y < cols):
            continue

        if grid[next_x][next_y] == 1:
            if dig_flag == 'D':
                serial_response = stub.GetMineSerialNumber(messaging_pb2.Null())
                pinNum = find_valid_pin(serial_response.serial_number)
                pin = messaging_pb2.PIN(pin=pinNum)
                stub.ShareMinePIN(pin)

                x, y = next_x, next_y
                output[x][y] = '*'
            else:
                x, y = next_x, next_y
                output[x][y] = '*'
                success = False
                message = f"Rover {rover_num} exploded at ({x}, {y})."
                break
        else:
            x, y = next_x, next_y
            output[x][y] = '*'

    # Write the rover's path to an output file.
    output_folder = "Output"
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
    output_filename = os.path.join(output_folder, f"path_{rover_num}.txt")
    with open(output_filename, "w") as f:
        for row in output:
            f.write(" ".join(row) + "\n")
    
    # Report the execution status back to the server.
    status = messaging_pb2.Status(success=success, message=message)
    stub.ReportCommandExecutionStatus(status)
    print(f"Rover {rover_num} finished execution with status: {message}")

num_of_rovers = 10
thread_list = []
initial_time = time.time()

for i in range(1, num_of_rovers + 1):
    thread = threading.Thread(target=run_rover, args=(i,))
    thread_list.append(thread)
    thread.start()

for thread in thread_list:
    thread.join()

final_time = time.time()
print(f"Execution time: {final_time - initial_time}")