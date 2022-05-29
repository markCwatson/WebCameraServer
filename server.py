import socket
import threading
import time
import pickle
import cv2
import datetime

HEADER_SIZE = 10
MESSAGE_PACKET_SIZE = 1024
FORMAT = "utf-8"

PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

def handle_client(conn, addr):
    
    print(f"[SERVER] {addr} connected at " + time.strftime("%H:%M:%S"))
    full_msg = b''
    new_msg = True

    while True:
        
        # \todo: disconnections are not handled properly yet
        try:
            msg = conn.recv(MESSAGE_PACKET_SIZE)
        except:
            print(f'[SERVER] Connecion lost.')
            break

        if new_msg is True:
            msg_length = int(msg[:HEADER_SIZE])
            print(f'[SERVER] Length of incoming message: {msg_length}')
            new_msg = False

        full_msg += msg

        if len(full_msg) - HEADER_SIZE >= msg_length:
            frame = pickle.loads(full_msg[HEADER_SIZE:])
            file_name = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")

            cv2.imwrite(f'images/{file_name}.jpg', frame)
            print(f"[SERVER] Message received from {addr}.")

            full_msg = b''
            new_msg = True

        if msg_length == 0:
            break
        
    print(f"[SERVER] {addr} disconnected at " + time.strftime("%H:%M:%S"))
    conn.close()

def start():
    
    server.listen()
    print(f"[SERVER] Listening on {SERVER} at " + time.strftime("%H:%M:%S"))

    while True:

        # \todo: disconnections are not handled properly yet
        try:
            conn, addr = server.accept()
        except:
            print(f'[SERVER] Connecion lost.')
            break

        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[SERVER] Thread count: {threading.active_count() - 1}")


print("[SERVER] Starting...")
start()
