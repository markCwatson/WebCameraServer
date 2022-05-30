import socket
import threading
import time
import pickle
import cv2
import datetime
import face_recognition as fr
import os
import json

class Server(object):

    def __init__(self) -> None:
        
        self.HEADER_SIZE = 10
        self.MESSAGE_PACKET_SIZE = 1024
        self.FORMAT = "utf-8"

        with open('server.json', 'r') as json_file:
            server_data = json.load(json_file)

        self.PORT = server_data['port']
        self.SERVER = server_data['ip']
        # or for loaclhost connection
        # self.SERVER = socket.gethostbyname(socket.gethostname())
        self.ADDR = (self.SERVER, self.PORT)

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(self.ADDR)

        self.KNOWN_FACES_DIR = "people"
        self.TOLERANCE = 0.55

        # Histogram of Oriented Gradients (HOG) features combined with a linear classifier (SVM)
        self.MODEL = "hog"

        self.known_faces = []
        self.known_names = []

    def trainNeuralNetwork(self):

        print(f"[SERVER] Loading data for face recognition ...")

        for name in os.listdir(self.KNOWN_FACES_DIR):
            for filename in os.listdir(f'{self.KNOWN_FACES_DIR}/{name}'):
                image = fr.load_image_file(f'{self.KNOWN_FACES_DIR}/{name}/{filename}')
                try:
                    encoding = fr.face_encodings(image)[0]
                    self.known_faces.append(encoding)
                    self.known_names.append(name)
                except:
                    continue
            print(f"[SERVER] Loaded data for \"{name}\"")

        print(f"[SERVER] Face recognition preparation complete!")

    def handleClient(self, conn, addr):
        
        print(f"[SERVER] {addr} connected at " + time.strftime("%H:%M:%S"))
        full_msg = b''
        new_msg = True

        while True:
            
            try:
                msg = conn.recv(self.MESSAGE_PACKET_SIZE)
            except:
                continue

            if new_msg is True:
                try:
                    msg_length = int(msg[:self.HEADER_SIZE])
                except:
                    continue

                print(f'[SERVER] Length of incoming message: {msg_length}')
                new_msg = False

            full_msg += msg

            if len(full_msg) - self.HEADER_SIZE >= msg_length:
                print(f"[SERVER] Image received from {addr}.")
                frame = pickle.loads(full_msg[self.HEADER_SIZE:])
                file_name = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")

                cv2.imwrite(f'images/{file_name}.jpg', frame)

                self.processImage(file_name)

                full_msg = b''
                new_msg = True

                response = "ready"
                response = bytes(f'{len(response):<{self.HEADER_SIZE}}' + response, self.FORMAT)
                conn.send(bytes(response))

            if msg_length == 0:
                break
            
        print(f"[SERVER] {addr} disconnected at " + time.strftime("%H:%M:%S"))
        conn.close()

    def processImage(self, file):

        print(f"[SERVER] Performing face recognition on {file}.jpg.")
        image = fr.load_image_file(f'images/{file}.jpg')

        locations = fr.face_locations(image, model=self.MODEL)
        encodings = fr.face_encodings(image, locations)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        for face_encoding, face_location in zip(encodings, locations):
            results = fr.compare_faces(self.known_faces, face_encoding, self.TOLERANCE)
            match = None
            if True in results:
                match = self.known_names[results.index(True)]
                print(f"[SERVER] Decected {match}.")

                top_left = (face_location[3], face_location[0])
                bottom_right = (face_location[1], face_location[2])
                color = [100, 200, 0]
                cv2.rectangle(image, top_left, bottom_right, color, 2)
                top_left = (face_location[3], face_location[2])
                bottom_right = (face_location[1], face_location[2]+22)
                cv2.rectangle(image, top_left, bottom_right, color, cv2.FILLED)
                cv2.putText(image, match, (face_location[3]+10, face_location[2]+15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                cv2.imwrite(f'images/{file}-{match}.jpg', image)
            else:
                print(f"[SERVER] No match found.")

        cv2.imshow(file, image)
        cv2.waitKey(2000)
        cv2.destroyWindow(file)

    def start(self):
        
        print("[SERVER] Starting...")
        self.server_socket.listen()
        print(f"[SERVER] Listening on {self.SERVER} at " + time.strftime("%H:%M:%S"))

        while True:

            try:
                conn, addr = self.server_socket.accept()
            except:
                print(f'[SERVER] Connecion lost.')
                break

            thread = threading.Thread(target=self.handleClient, args=(conn, addr))
            thread.start()
            print(f"[SERVER] Thread count: {threading.active_count() - 1}")


if __name__ == "__main__":
    
    server = Server()
    server.trainNeuralNetwork()
    server.start()
