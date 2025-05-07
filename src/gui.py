import tkinter as tk
import socket
import threading
import math


class GUIApp:
    def __init__(self, master, host="localhost", port=12345):
        self.master = master
        master.title("Air Touch GUI")
        master.geometry("600x400")

        self.canvas = tk.Canvas(master, width=600, height=400)
        self.canvas.pack()

        self.button = self.canvas.create_rectangle(
            250, 300, 350, 350, fill="lightblue", outline="black"
        )
        self.button_text = self.canvas.create_text(300, 325, text="button")

        self.cursor = self.canvas.create_oval(0, 0, 20, 20, fill="red")

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))

        self.last_x, self.last_y = None, None
        self.last_z = None
        self.button_pressed = False
        self.over_button = False

        threading.Thread(target=self.receive_coordinates, daemon=True).start()

    def receive_coordinates(self):
        while True:
            try:
                data = self.client_socket.recv(1024).decode()
                if not data:
                    break
                if data == "no_hand":
                    self.update_cursor(None, None, None)
                else:
                    x, y, z = map(float, data.split(","))
                    self.update_cursor(x, y, z)
            except:
                break

    def update_cursor(self, x, y, z):
        if x is None or y is None or z is None:
            return

        # Increase movement range by adjusting the multiplier (e.g., 1.5)
        canvas_x = x * self.canvas.winfo_width() * 1.5
        canvas_y = y * self.canvas.winfo_height() * 1.5

        # Clamp the cursor position to stay within the canvas
        canvas_x = max(10, min(canvas_x, self.canvas.winfo_width() - 10))
        canvas_y = max(10, min(canvas_y, self.canvas.winfo_height() - 10))

        # Smooth movement
        if self.last_x is not None and self.last_y is not None:
            canvas_x = self.last_x * 0.7 + canvas_x * 0.3
            canvas_y = self.last_y * 0.7 + canvas_y * 0.3

        self.last_x, self.last_y = canvas_x, canvas_y

        self.canvas.coords(
            self.cursor, canvas_x - 10, canvas_y - 10, canvas_x + 10, canvas_y + 10
        )

        button_coords = self.canvas.coords(self.button)
        self.over_button = (
            button_coords[0] <= canvas_x <= button_coords[2]
            and button_coords[1] <= canvas_y <= button_coords[3]
        )

        if self.over_button:
            if self.last_z is not None:
                z_change = z - self.last_z
                if z_change < -0.05:  # Adjusted threshold for button press
                    self.canvas.itemconfig(self.button, fill="red")
                    self.canvas.itemconfig(self.button_text, text="pushed")
                    self.button_pressed = True
                elif z_change > 0.05:  # Threshold for button release
                    self.canvas.itemconfig(self.button, fill="lightblue")
                    self.canvas.itemconfig(self.button_text, text="button")
                    self.button_pressed = False
        else:
            self.canvas.itemconfig(self.button, fill="lightblue")
            self.canvas.itemconfig(self.button_text, text="button")
            self.button_pressed = False

        self.last_z = z

        # Update cursor color based on z-coordinate using a trigonometric function
        r = int(127.5 * (math.sin(z * math.pi) + 1))  # r varies from 0 to 255
        g = int(
            127.5 * (math.sin(z * math.pi + 2 * math.pi / 3) + 1)
        )  # g varies from 0 to 255
        b = int(
            127.5 * (math.sin(z * math.pi + 4 * math.pi / 3) + 1)
        )  # b varies from 0 to 255
        color = f"#{r:02x}{g:02x}{b:02x}"
        self.canvas.itemconfig(self.cursor, fill=color)


if __name__ == "__main__":
    root = tk.Tk()
    app = GUIApp(root)
    root.mainloop()
