import cv2
import mediapipe as mp
import numpy as np
import socket
import pickle
import struct
import threading


class DetectionProgram:
    def __init__(self, host="localhost", port=12345):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            min_detection_confidence=0.5, min_tracking_confidence=0.5
        )

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(1)
        print(f"Waiting for GUI connection on {host}:{port}")
        self.conn = None
        self.addr = None

    def accept_gui(self):
        self.conn, self.addr = self.server_socket.accept()
        print(f"GUI connected from {self.addr}")

    def process_frame(self, frame):
        # Convert the BGR image to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame for hand detection
        hand_results = self.hands.process(rgb_frame)

        # Initialize variables
        x, y, z = None, None, None

        # Draw hand landmarks and get coordinates
        if hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                )

                # Get index finger tip coordinates
                index_finger_tip = hand_landmarks.landmark[
                    self.mp_hands.HandLandmark.INDEX_FINGER_TIP
                ]
                x, y, z = index_finger_tip.x, index_finger_tip.y, index_finger_tip.z
                h, w, _ = frame.shape

                print(f"Index finger tip at: ({x}, {y}, {z})")

                # Check for "air touch"
                if z < -0.05:  # Adjusted threshold for better sensitivity
                    x_pixel, y_pixel = int(x * w), int(y * h)
                    cv2.circle(frame, (x_pixel, y_pixel), 10, (0, 255, 0), -1)
                    print("Air touch detected!")

        # Send coordinates to GUI (even if hand is not detected)
        if self.conn:
            try:
                if x is not None and y is not None and z is not None:
                    gui_x = 1 - x  # Flip x-coordinate for GUI
                    self.conn.sendall(f"{gui_x},{y},{z}".encode())
                else:
                    # Send a special message when no hand is detected
                    self.conn.sendall(b"no_hand")
            except:
                self.conn = None
                self.addr = None
                print("GUI disconnected")

        return frame

    def run(self):
        cap = cv2.VideoCapture(0)
        window_name = "Hand Detection"
        cv2.namedWindow(window_name)

        while True:
            success, frame = cap.read()
            if not success:
                print("Failed to capture frame")
                break

            # Process the frame
            processed_frame = self.process_frame(frame)

            # Display the frame locally
            cv2.imshow(window_name, processed_frame)

            key = cv2.waitKey(1) & 0xFF
            if (
                key == 27
                or cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1
            ):  # Press 'ESC' or close window to exit
                break

        cap.release()
        cv2.destroyAllWindows()
        if self.conn:
            self.conn.close()
        self.server_socket.close()


if __name__ == "__main__":
    detection_program = DetectionProgram()
    threading.Thread(target=detection_program.accept_gui, daemon=True).start()
    detection_program.run()
