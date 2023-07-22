import os
import shutil
import psutil
import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pyautogui
import threading

# System management

class SystemManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Custom System Manager GUI")
        self.current_theme = "light"  # Default theme is light mode

        self.menu = tk.Menu(root)
        self.root.config(menu=self.menu)

        self.afk_window = None
        self.afk_enabled = False
        self.afk_thread = None

        self.file_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Create File", command=self.create_file)
        self.file_menu.add_command(label="Read File", command=self.read_file)
        self.file_menu.add_command(label="Write to File", command=self.write_file)
        self.file_menu.add_command(label="Delete File", command=self.delete_file)
        self.file_menu.add_command(label="Organize Files", command=self.organize_files)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.on_exit)

        self.view_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="View", menu=self.view_menu)
        self.view_menu.add_command(label="Light Mode", command=self.light_mode)
        self.view_menu.add_command(label="Dark Mode", command=self.dark_mode)

        self.system_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="System", menu=self.system_menu)
        self.system_menu.add_command(label="Power Off", command=self.power_off)
        self.system_menu.add_command(label="Restart", command=self.restart)
        self.system_menu.add_command(label="Sleep", command=self.sleep)
        self.system_menu.add_separator()
        self.afk_menu = tk.Menu(self.system_menu, tearoff=0)
        self.system_menu.add_cascade(label="AFK", menu=self.afk_menu)
        self.afk_menu.add_command(label="Start AFK", command=self.start_afk)
        self.afk_menu.add_command(label="Stop AFK", command=self.stop_afk)

        self.stats_label = tk.Label(root, text="", font=("Arial", 12))
        self.stats_label.pack(pady=10)

        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.ax.set_title("CPU and Memory Usage")
        self.ax.set_xlabel("Time (seconds)")
        self.ax.set_ylabel("Usage (%)")

        self.memory_usage = []
        self.cpu_usage = []
        self.time = []

        self.canvas = FigureCanvasTkAgg(self.fig, master=root)  # Create the canvas
        self.canvas.get_tk_widget().pack()  # Pack the canvas into the root window

        self.update_plot()  # Call the initial plot

        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.afk_thread = threading.Thread(target=self.move_mouse_afk)
        self.afk_thread.daemon = True
        self.afk_enabled = False

    def light_mode(self):
        """Change the theme to light mode."""
        if self.current_theme != "light":
            self.current_theme = "light"
            self.apply_theme()

    def dark_mode(self):
        """Change the theme to dark mode."""
        if self.current_theme != "dark":
            self.current_theme = "dark"
            self.apply_theme()

    def apply_theme(self):
        """Apply the selected theme."""
        if self.current_theme == "light":
            self.root.config(bg="white")
            self.stats_label.config(bg="white", fg="black")
            self.ax.set_facecolor("white")  # Set the graph background color to white
            self.ax.tick_params(axis='x', colors='black')  # Set x-axis tick color to black
            self.ax.tick_params(axis='y', colors='black')  # Set y-axis tick color to black
            self.ax.yaxis.label.set_color('black')  # Set y-axis label color to black
        elif self.current_theme == "dark":
            self.root.config(bg="#333")
            self.stats_label.config(bg="#333", fg="white")
            self.ax.set_facecolor("black")  # Set the graph background color to black
            self.ax.tick_params(axis='x', colors='black')  # Set x-axis tick color to white
            self.ax.tick_params(axis='y', colors='black')  # Set y-axis tick color to white
            self.ax.yaxis.label.set_color('white')  # Set y-axis label color to white

        self.update_plot()  # Update the plot with the current theme

    def create_file(self):
        """Create a new file."""
        filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if filename: 
            try:
                with open(filename, 'w'):
                    messagebox.showinfo("Success", f"File '{filename}' created successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Error creating the file: {e}")

    def read_file(self):
        """Read the contents of a file and display them."""
        filename = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if filename:
            try:
                with open(filename, 'r') as file:
                    contents = file.read()
                    messagebox.showinfo(f"Contents of '{filename}'", contents)
            except FileNotFoundError:
                messagebox.showerror("Error", f"File '{filename}' not found.")
            except Exception as e:
                messagebox.showerror("Error", f"Error reading the file: {e}")

    def write_file(self):
        """Write content to an existing file or create a new file if it doesn't exist."""
        filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if filename:
            content = self.simple_editor()
            if content:
                try:
                    with open(filename, 'w') as file:
                        file.write(content)
                        messagebox.showinfo("Success", f"Content written to '{filename}' successfully.")
                except Exception as e:
                    messagebox.showerror("Error", f"Error writing to the file: {e}")

    def delete_file(self):
        """Delete a file."""
        filename = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if filename:
            try:
                os.remove(filename)
                messagebox.showinfo("Success", f"File '{filename}' deleted successfully.")
            except FileNotFoundError:
                messagebox.showerror("Error", f"File '{filename}' not found.")
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting the file: {e}")

    def simple_editor(self):
        """A simple text editor for writing content."""
        editor_window = tk.Toplevel(self.root)
        editor_window.title("Text Editor")
        editor_window.geometry("500x300")

        text = tk.Text(editor_window)
        text.pack(fill=tk.BOTH, expand=True)

        def save_and_close():
            content = text.get("1.0", tk.END)
            editor_window.destroy()
            return content

        save_button = tk.Button(editor_window, text="Save", command=save_and_close)
        save_button.pack()

        editor_window.mainloop()

    def organize_files(self):
        """Organize files into folders based on their extensions."""
        src_directory = filedialog.askdirectory(title="Select a directory to organize files from:")
        if src_directory:
            try:
                for filename in os.listdir(src_directory):
                    if os.path.isfile(os.path.join(src_directory, filename)):
                        file_extension = filename.split(".")[-1]
                        dst_directory = os.path.join(src_directory, file_extension.upper())
                        if not os.path.exists(dst_directory):
                            os.makedirs(dst_directory)
                        shutil.move(os.path.join(src_directory, filename), os.path.join(dst_directory, filename))
                messagebox.showinfo("Success", "Files organized successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Error organizing files: {e}")

    def get_system_stats(self):
        """Get real-time memory and CPU stats."""
        mem_usage = psutil.virtual_memory().percent
        cpu_usage = psutil.cpu_percent()

        self.stats_label.config(text=f"Memory Usage: {mem_usage:.2f}%\nCPU Usage: {cpu_usage:.2f}%")
        self.root.after(1000, self.get_system_stats)  # Update stats every second

    def update_plot(self):
        self.time.append(len(self.time))
        self.memory_usage.append(psutil.virtual_memory().percent)
        self.cpu_usage.append(psutil.cpu_percent())

        self.ax.clear()
        if self.current_theme == "light":
            self.ax.plot(self.time, self.memory_usage, label="Memory Usage", color="blue")
            self.ax.plot(self.time, self.cpu_usage, label="CPU Usage", color="red")
        elif self.current_theme == "dark":
            self.ax.plot(self.time, self.memory_usage, label="Memory Usage", color="red")
            self.ax.plot(self.time, self.cpu_usage, label="CPU Usage", color="lime")

        self.ax.legend()
        self.ax.set_xlabel("Time (seconds)")
        self.ax.set_ylabel("Usage (%)")
        self.fig.tight_layout()

        if self.canvas:
            self.canvas.draw()  # Update the plot canvas if it exists

        self.root.after(1000, self.update_plot)  # Update plot every second

    def power_off(self):
        """Power off the system."""
        if messagebox.askokcancel("Power Off", "Do you want to power off the system?"):
            os.system("shutdown /s /t 0")

    def restart(self):
        """Restart the system."""
        if messagebox.askokcancel("Restart", "Do you want to restart the system?"):
            os.system("shutdown /r /t 0")

    def sleep(self):
        """Put the system to sleep."""
        if messagebox.askokcancel("Sleep", "Do you want to put the system to sleep?"):
            
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

    def move_mouse_afk(self):
        if self.afk_enabled:
            pyautogui.move(10, 0, duration=0.1)
            pyautogui.move(-10, 0, duration=0.1)
            # Call move_mouse_afk after 10 seconds
            self.root.after(10000, self.move_mouse_afk)

    def start_afk(self):
        """Start the AFK feature."""
        if not self.afk_enabled:
            self.afk_enabled = True
            self.move_mouse_afk()
            self.afk_thread = threading.Thread(target=self.move_mouse_afk)
            self.afk_thread.daemon = True
            self.afk_thread.start()
            self.create_afk_window()

    def stop_afk(self):
        """Stop the AFK feature."""
        if self.afk_enabled:
            self.afk_enabled = False
            if self.afk_window:
                self.afk_window.destroy()


    def create_afk_window(self):
        """Create the AFK window with a 'Disable AFK' button."""
        if self.afk_window:
            self.afk_window.destroy()

        self.afk_window = tk.Toplevel(self.root)
        self.afk_window.title("AFK Feature")
        self.afk_window.geometry("250x100")

        afk_label = tk.Label(self.afk_window, text="AFK Feature Enabled", font=("Arial", 14))
        afk_label.pack(pady=10)

        disable_button = tk.Button(self.afk_window, text="Disable AFK", command=self.stop_afk)
        disable_button.pack()                 

    def on_exit(self):
        if messagebox.askokcancel("Exit", "Do you want to exit?"):
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SystemManagementApp(root)
    app.get_system_stats()  # Call the method to start updating the stats

    root.mainloop()

