import grpc
import messaging_pb2
import messaging_pb2_grpc
import sys

def run(rover_id):
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = messaging_pb2_grpc.RoverServiceStub(channel)

        # Retrieve the map
        map_response = stub.GetMap(messaging_pb2.Empty())
        map_data = map_response.map
        print(f"Rover {rover_id} received map.")

        # Execute command stream
        try:
            for command in stub.GetCommandStream(messaging_pb2.Empty()):
                print(f"Rover {rover_id} executing command: {command.command}")
                # Implement command execution logic here
                # If a mine is encountered:
                mine_location = messaging_pb2.MineLocation(x=10, y=20)  # Example coordinates
                serial_response = stub.GetMineSerialNumber(mine_location)
                serial_number = serial_response.serial_number
                print(f"Rover {rover_id} found mine with serial number: {serial_number}")
                # Disarm the mine and obtain the PIN
                mine_pin = "0000"  # Example PIN
                stub.ShareMinePIN(messaging_pb2.MinePIN(pin=mine_pin))
        except Exception as e:
            stub.ReportCommandExecutionStatus(messaging_pb2.CommandStatus(success=False, message=str(e)))
        else:
            stub.ReportCommandExecutionStatus(messaging_pb2.CommandStatus(success=True, message="All commands executed successfully."))

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python rover_client.py <rover_id>")
        sys.exit(1)
    rover_id = sys.argv[1]
    run(rover_id)
