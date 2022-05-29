import cv2
import time
import threading
import queue
import socket
import pickle

class CameraClient(object):

    def __init__(self) -> None:

        self.cap = cv2.VideoCapture(0)

        if not self.cap.isOpened():
            print("[CAMERA_CLIENT] Cannot open camera")
            exit()

        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

        self.HEADER_SIZE = 10
        self.FORMAT = "utf-8"
        self.PORT = 5050
        self.SERVER = socket.gethostbyname(socket.gethostname())
        self.ADDR = (self.SERVER, self.PORT)

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(self.ADDR)

    def cameraThread(self, frame, faces):
        
        print("[CAMERA_CLIENT] Running clientThread")
        
        for (x, y, width, height) in faces:
            cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 255, 0), 2)

        message = pickle.dumps(frame)
        message = bytes(f'{len(message):<{self.HEADER_SIZE}}', self.FORMAT) + message
        self.client.send(message)

        time.sleep(5)

    def handleFaceDetection(self, frame, faces):

        # Start thread to handle connection with server to send frame
        if threading.active_count() <= 2:
            clientThread = threading.Thread(target=self.cameraThread, args=(frame,faces))
            clientThread.start()

    def main(self):

        while True:
            
            if (inputQueue.qsize() > 0):
                print("[CAMERA_CLIENT] Keyboard char entered. Exiting ...")
                break

            ret, frame = self.cap.read()

            if not ret:
                print("[CAMERA_CLIENT] Can't receive frame. Exiting ...")
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 5)

            if len(faces) > 0:
                self.handleFaceDetection(frame, faces)


def keyboardThread(inputQueue):

    while (True):
        input_char = input()
        inputQueue.put(input_char)

if __name__ == "__main__":

    camera = CameraClient()

    inputQueue = queue.Queue()
    inputThread = threading.Thread(target=keyboardThread, args=(inputQueue,), daemon=True)
    inputThread.start()

    camera.main()
    camera.cap.release()
    cv2.destroyAllWindows()
