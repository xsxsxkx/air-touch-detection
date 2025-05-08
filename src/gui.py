import tkinter as tk
import socket
import threading
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import queue


class WindowManager:
    def __init__(self, host="localhost", port=12345):
        self.root = tk.Tk()
        self.root.title("Air Touch System")

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))

        self.x, self.y, self.z = None, None, None
        self.last_z = None

        self.main_gui = MainGUI(self.root, self)
        self.graph_gui = GraphGUI(tk.Toplevel(self.root), self)

        self.coordinate_queue = queue.Queue()
        threading.Thread(target=self.receive_coordinates, daemon=True).start()

    def receive_coordinates(self):
        while True:
            try:
                data = self.client_socket.recv(1024).decode()
                if not data:
                    break
                if data == "no_hand":
                    # print("No hand detected")  # Debug print
                    self.coordinate_queue.put(
                        (float("nan"), float("nan"), float("nan"))
                    )
                else:
                    x, y, z = map(float, data.split(","))
                    self.coordinate_queue.put((x, y, z))
            except Exception as e:
                # print(f"Error in receive_coordinates: {e}")  # Debug print
                break

    def update_coordinates(self):
        try:
            while not self.coordinate_queue.empty():
                x, y, z = self.coordinate_queue.get_nowait()
                self.x, self.y, self.z = x, y, z
                self.main_gui.update_cursor(x, y, z)
                self.graph_gui.queue_update(z)
        except queue.Empty:
            pass
        finally:
            self.root.after(10, self.update_coordinates)

    def run(self):
        self.root.after(0, self.update_coordinates)
        self.root.mainloop()


class MainGUI:
    def __init__(self, master, manager):
        self.master = master
        self.manager = manager
        self.master.geometry("600x400")

        self.canvas = tk.Canvas(self.master, width=600, height=400)
        self.canvas.pack()

        self.button = self.canvas.create_rectangle(
            250, 300, 350, 350, fill="lightblue", outline="black"
        )
        self.button_text = self.canvas.create_text(300, 325, text="button")

        self.cursor = self.canvas.create_oval(0, 0, 20, 20, fill="red")

        self.last_x, self.last_y = None, None
        self.button_pressed = False
        self.over_button = False

    def update_cursor(self, x, y, z):
        if math.isnan(x) or math.isnan(y) or math.isnan(z):
            self.canvas.itemconfig(self.cursor, state="hidden")
            return
        else:
            self.canvas.itemconfig(self.cursor, state="normal")

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
            if self.manager.last_z is not None and not math.isnan(self.manager.last_z):
                z_change = z - self.manager.last_z
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

        self.manager.last_z = z

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


class GraphGUI:
    def __init__(self, master, manager):
        self.master = master
        self.manager = manager
        self.master.title("Depth Graph")
        self.master.geometry("400x300")

        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.depth_data = []
        self.time_data = []
        self.start_time = time.time()
        self.last_update = 0

    def queue_update(self, z):
        current_time = time.time() - self.start_time
        self.depth_data.append(z)
        self.time_data.append(current_time)

        # Keep only the last 100 data points
        if len(self.depth_data) > 100:
            self.depth_data = self.depth_data[-100:]
            self.time_data = self.time_data[-100:]

        # Update graph every 100ms to reduce CPU usage
        if current_time - self.last_update > 0.1:
            self.update_graph()
            self.last_update = current_time

    def update_graph(self):
        self.ax.clear()
        self.ax.plot(self.time_data, self.depth_data)
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Depth")
        self.ax.set_title("Finger Depth Over Time")
        self.ax.set_ylim(-1, 1)  # Set fixed y-axis limits
        self.canvas.draw()


if __name__ == "__main__":
    manager = WindowManager()
    manager.run()
