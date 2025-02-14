from concurrent import futures
import grpc
import messaging_pb2
import messaging_pb2_grpc

class RoverServiceServicer(messaging_pb2_grpc.RoverServiceServicer):
    def GetMap(self, request, context):
        # Load and return the 2D map
        with open('map1.txt', 'r') as file:
            map_data = file.read()
        return messaging_pb2.MapData(map=map_data)

    def GetCommandStream(self, request, context):
        # Stream commands to the rover
        with open('commands.txt', 'r') as file:
            commands = file.readlines()
        for cmd in commands:
            yield messaging_pb2.Command(command=cmd.strip())

    def GetMineSerialNumber(self, request, context):
        # Retrieve mine serial number based on location
        # Implement logic to find the serial number
        serial_number = "12345"  # Example serial number
        return messaging_pb2.MineSerial(serial_number=serial_number)

    def ReportCommandExecutionStatus(self, request, context):
        # Log the command execution status
        if request.success:
            print(f"Rover reported success: {request.message}")
        else:
            print(f"Rover reported failure: {request.message}")
        return messaging_pb2.Empty()

    def ShareMinePIN(self, request, context):
        # Log the received mine PIN
        print(f"Received mine PIN: {request.pin}")
        return messaging_pb2.Empty()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    messaging_pb2_grpc.add_RoverServiceServicer_to_server(RoverServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
