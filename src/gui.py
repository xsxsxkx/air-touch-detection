import tkinter as tk
import socket
import threading

class GUIApp:
    def __init__(self, master, host='localhost', port=12345):
        self.master = master
        master.title("Air Touch GUI")
        master.geometry("400x300")

        self.canvas = tk.Canvas(master, width=400, height=200)
        self.canvas.pack()

        self.button = tk.Button(master, text="Air Touch Button", width=20, height=2)
        self.button.pack(pady=20)

        self.cursor = self.canvas.create_oval(0, 0, 10, 10, fill="red")

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))

        threading.Thread(target=self.receive_coordinates, daemon=True).start()

    def receive_coordinates(self):
        while True:
            try:
                data = self.client_socket.recv(1024).decode()
                if not data:
                    break
                x, y, z = map(float, data.split(','))
                self.update_cursor(x, y, z)
            except:
                break

    def update_cursor(self, x, y, z):
        canvas_x = x * self.canvas.winfo_width()
        canvas_y = y * self.canvas.winfo_height()
        self.canvas.coords(self.cursor, canvas_x-5, canvas_y-5, canvas_x+5, canvas_y+5)

        button_bbox = self.button.winfo_rootx(), self.button.winfo_rooty(), \
                      self.button.winfo_rootx() + self.button.winfo_width(), \
                      self.button.winfo_rooty() + self.button.winfo_height()

        if button_bbox[0] <= canvas_x <= button_bbox[2] and button_bbox[1] <= canvas_y <= button_bbox[3]:
            if z < -0.1:  # Air touch threshold
                self.button.config(relief=tk.SUNKEN)
            else:
                self.button.config(relief=tk.RAISED)
        else:
            self.button.config(relief=tk.RAISED)

if __name__ == "__main__":
    root = tk.Tk()
    app = GUIApp(root)
    root.mainloop()
