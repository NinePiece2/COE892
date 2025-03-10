import pika
import sys
import json
import time
import string
import hashlib
import itertools

def find_valid_pin(serial_number):
    charset = string.ascii_letters + string.digits
    for length in range(1, 6):
        for pin_tuple in itertools.product(charset, repeat=length):
            pin = ''.join(pin_tuple)
            temp_key = serial_number + pin
            hash_value = hashlib.sha256(temp_key.encode()).hexdigest()
            if hash_value.startswith('000000'):
                return pin
    return None

def on_demine_task(ch, method, properties, body, deminer_num, channel):
    task = json.loads(body.decode())
    rover_num = task.get("rover_num")
    x = task.get("x")
    y = task.get("y")
    serial_number = task.get("serial_number")
    print(f"Deminer {deminer_num} received task: Rover {rover_num}, Coordinates: ({x}, {y}), Serial: {serial_number}")

    pin = find_valid_pin(serial_number)
    result = {
        "deminer_num": deminer_num,
        "x": x,
        "y": y,
        "serial_number": serial_number,
        "PIN": pin
    }

    channel.basic_publish(exchange='',
                          routing_key='Defused-Mines',
                          body=json.dumps(result))
    print(f"Deminer {deminer_num} defused mine at ({x}, {y}) with PIN: {pin}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    if len(sys.argv) < 2:
        print("Usage: python deminer.py <deminer_num>")
        sys.exit(1)
    
    deminer_num = int(sys.argv[1])
    if deminer_num not in [1, 2]:
        print("Invalid deminer number. Please enter 1 or 2.")
        sys.exit(1)

    connection = pika.BlockingConnection(pika.ConnectionParameters(host='192.168.8.24'))
    channel = connection.channel()
    channel.queue_declare(queue='Demine-Queue')
    channel.queue_declare(queue='Defused-Mines')

    channel.basic_qos(prefetch_count=1)
    on_message_callback = lambda ch, method, properties, body: on_demine_task(ch, method, properties, body, deminer_num, channel)
    channel.basic_consume(queue='Demine-Queue', on_message_callback=on_message_callback)

    print(f"Deminer {deminer_num} ready")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    connection.close()

if __name__ == '__main__':
    main()
