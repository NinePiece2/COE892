import grpc
from concurrent import futures
import time
import requests
import json

import messaging_pb2
import messaging_pb2_grpc

base_url = 'https://coe892.reev.dev/lab1/rover/'

# Load the 2D map from file (map1.txt)
def load_map(filename="map1.txt"):
    with open(filename, 'r') as f:
        content = f.read()
    return content

def load_mines(filename="mines.txt"):
    with open(filename, 'r') as f:
        return [line.strip() for line in f.readlines()]
    
mines = load_mines("mines.txt")  

class RoverServiceServicer(messaging_pb2_grpc.RoverServiceServicer):

    def GetMap(self, request, context):
        map_content = load_map("map1.txt")
        return messaging_pb2.MapData(map=map_content)

    def GetCommandStream(self, request, context):
        moves = json.loads(requests.get(base_url + str(request.rover_num)).text)['data']['moves']
        for cmd in moves:
            yield messaging_pb2.Command(command=cmd)

    def GetMineSerialNumber(self, request, context):
        serial = mines.pop(0) if mines else "UNKNOWN"
        return messaging_pb2.Serial(serial_number=serial)

    def ReportCommandExecutionStatus(self, request, context):
        print(f"Execution status reported: success={request.success}, message='{request.message}'")
        return messaging_pb2.Null()

    def ShareMinePIN(self, request, context):
        print(f"Received mine PIN: {request.pin}")
        return messaging_pb2.Null()

server = grpc.server(futures.ThreadPoolExecutor(max_workers=25))
messaging_pb2_grpc.add_RoverServiceServicer_to_server(RoverServiceServicer(), server)
server.add_insecure_port('[::]:50051')
server.start()
print("Ground Control started on port 50051.")
try:
    while True:
        continue
except KeyboardInterrupt:
    server.stop(0)

