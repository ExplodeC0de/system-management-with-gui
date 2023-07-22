import os
import shutil
import psutil
import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class FileManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Management GUI")

        self.menu = tk.Menu(root)
        self.root.config(menu=self.menu)

        self.file_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Create File", command=self.create_file)
        self.file_menu.add_command(label="Read File", command=self.read_file)
        self.file_menu.add_command(label="Write to File", command=self.write_file)
        self.file_menu.add_command(label="Delete File", command=self.delete_file)
        self.file_menu.add_command(label="Organize Files", command=self.organize_files)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.on_exit)

        self.stats_label = tk.Label(root, text="", font=("Arial", 12))
        self.stats_label.pack(pady=10)

        self.plot_stats()

        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)

def create_file():
    """Create a new file."""
    filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if filename: 
        try:
            with open(filename, 'w'):
                messagebox.showinfo("Success", f"File '{filename}' created successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Error creating the file: {e}")

def read_file():
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

def write_file():
    """Write content to an existing file or create a new file if it doesn't exist."""
    filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if filename:
        content = simple_editor()
        if content:
            try:
                with open(filename, 'w') as file:
                    file.write(content)
                    messagebox.showinfo("Success", f"Content written to '{filename}' successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Error writing to the file: {e}")

def delete_file():
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

def simple_editor():
    """A simple text editor for writing content."""
    editor_window = tk.Toplevel(root)
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

def organize_files():
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

def get_system_stats():
    """Get real-time memory and CPU stats."""
    mem_usage = psutil.virtual_memory().percent
    cpu_usage = psutil.cpu_percent()

    stats_label.config(text=f"Memory Usage: {mem_usage:.2f}%\nCPU Usage: {cpu_usage:.2f}%")
    root.after(1000, get_system_stats)  # Update stats every second

def plot_stats():
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.set_title("CPU and Memory Usage")
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Usage (%)")

    memory_usage = []
    cpu_usage = []
    time = []

    def update_plot():
        time.append(len(time))
        memory_usage.append(psutil.virtual_memory().percent)
        cpu_usage.append(psutil.cpu_percent())

        ax.clear()
        ax.plot(time, memory_usage, label="Memory Usage", color="blue")
        ax.plot(time, cpu_usage, label="CPU Usage", color="red")

        ax.legend()
        ax.set_xlabel("Time (seconds)")
        ax.set_ylabel("Usage (%)")
        fig.tight_layout()

        canvas.draw()
        root.after(1000, update_plot)  # Update plot every second

    update_plot()

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack(pady=10)

def on_exit():
    if messagebox.askokcancel("Exit", "Do you want to exit?"):
        root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("File Management GUI")

    menu = tk.Menu(root)
    root.config(menu=menu)

    file_menu = tk.Menu(menu)
    menu.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Create File", command=create_file)
    file_menu.add_command(label="Read File", command=read_file)
    file_menu.add_command(label="Write to File", command=write_file)
    file_menu.add_command(label="Delete File", command=delete_file)
    file_menu.add_command(label="Organize Files", command=organize_files)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=on_exit)

    stats_label = tk.Label(root, text="", font=("Arial", 12))
    stats_label.pack(pady=10)

    plot_stats()

    root.protocol("WM_DELETE_WINDOW", on_exit)

    root.mainloop()
