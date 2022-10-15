# WebCameraServer

Run Server.py and wait for the machine learning model to finish loading the data for face recognition and establish a connection over the localhost.

Run CameraClient.py with a USB camera connected (tested using Logitech C920).

CameraClient.py will detect the presence of a face on camera then send an image to the server. The server will then perform facial recognition to try and identify the people in the image.

The model is trained by placing images of known people in the ./people folder in subdirectories that include the person's name (ex. C:\Users\mark\Documents\WebCameraServer\people\mark)

# Dependencies
Need 64-bit python 3.8 and cmake via Visual Studio C++ installed for face_recongition module.
Then run 'pip3 install face_recognition'.

Face Recognition docs: https://face-recognition.readthedocs.io/en/latest/index.htmldgfdg

A file named "server.json" should be included in root that contains IP address and port of server (I did it like this so I can have multiple computers, some on wifi/some on ethernet, connected to server).