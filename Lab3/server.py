import grpc
from concurrent import futures
import time
import requests
import json
import threading
import pika

import messaging_pb2
import messaging_pb2_grpc

BASE_URL = 'https://coe892.reev.dev/lab1/rover/'

def load_map(filename="map1.txt"):
    with open(filename, 'r') as f:
        return f.read()

def load_mines(filename="mines.txt"):
    with open(filename, 'r') as f:
        return [line.strip() for line in f.readlines()]

mines = load_mines("mines.txt")

class RoverServiceServicer(messaging_pb2_grpc.RoverServiceServicer):
    def GetMap(self, request, context):
        map_content = load_map("map1.txt")
        return messaging_pb2.MapData(map=map_content)

    def GetCommandStream(self, request, context):
        moves = json.loads(requests.get(BASE_URL + str(request.rover_num)).text)['data']['moves']
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

def rabbitmq_defused_mines_listener():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='192.168.8.24'))
    channel = connection.channel()
    channel.queue_declare(queue='Defused-Mines')
    def callback(ch, method, properties, body):
        print(f"[RabbitMQ] Defused mine PIN received: {body.decode()}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    channel.basic_consume(queue='Defused-Mines', on_message_callback=callback)
    print("Started RabbitMQ consumer for Defused-Mines")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    connection.close()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=25))
    messaging_pb2_grpc.add_RoverServiceServicer_to_server(RoverServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Ground Control gRPC server started on port 50051.")

    # Start RabbitMQ consumer in a separate thread.
    thread = threading.Thread(target=rabbitmq_defused_mines_listener, daemon=True)
    thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
