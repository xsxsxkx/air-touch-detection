import cv2
import numpy as np
import socket
import pickle
import struct
import time

class ViewerApp:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port

    def run(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"Attempting to connect to {self.host}:{self.port}")
        while True:
            try:
                client_socket.connect((self.host, self.port))
                print("Connected to server")
                break
            except ConnectionRefusedError:
                print("Connection failed. Retrying in 5 seconds...")
                time.sleep(5)

        data = b""
        payload_size = struct.calcsize("L")

        while True:
            try:
                while len(data) < payload_size:
                    data += client_socket.recv(4096)

                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack("L", packed_msg_size)[0]

                while len(data) < msg_size:
                    data += client_socket.recv(4096)

                frame_data = data[:msg_size]
                data = data[msg_size:]

                frame = pickle.loads(frame_data)
                cv2.imshow('Viewer', frame)

                if cv2.waitKey(1) & 0xFF == 27:  # Press 'ESC' to exit
                    break
            except:
                print("Connection lost. Exiting...")
                break

        client_socket.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    viewer = ViewerApp()
    viewer.run()
