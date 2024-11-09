import tkinter as tk
from tkinter import messagebox
from tkinter import font
from datetime import datetime
from plyer import notification
import json
import os
import subprocess
import time
from threading import Thread

# File to store reminders
REMINDER_FILE = "reminders.json"

# Function to load reminders from the file
def load_reminders():
    try:
        with open(REMINDER_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Function to save reminders to the file
def save_reminders(reminders):
    with open(REMINDER_FILE, 'w') as file:
        json.dump(reminders, file)

# Function to display notifications for due reminders
def check_due_reminders():
    reminders = load_reminders()
    current_time = datetime.now()
    due_reminders = [r for r in reminders if datetime.strptime(r['time'], "%Y-%m-%d %H:%M") <= current_time]

    # Show notifications for each due reminder
    for reminder in due_reminders:
        notification.notify(
            title="Reminder",
            message=f"Reminder: {reminder['title']}",
            timeout=10
        )

    # Remove due reminders from the list and save the updated list
    reminders = [r for r in reminders if r not in due_reminders]
    save_reminders(reminders)

# Function to add a new reminder
def add_reminder():
    title = entry_title.get()
    time_str = entry_time.get()

    try:
        reminder_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
        reminders = load_reminders()
        reminders.append({"title": title, "time": time_str})
        save_reminders(reminders)
        messagebox.showinfo("Reminder Added", f"Reminder '{title}' set for {time_str}")
        entry_title.delete(0, tk.END)
        entry_time.delete(0, tk.END)
    except ValueError:
        messagebox.showerror("Invalid Time Format", "Please enter time in YYYY-MM-DD HH:MM format.")

# Function to schedule the task in Windows Task Scheduler
def schedule_task():
    python_executable = os.path.abspath(os.path.join(os.path.dirname(__file__), "venv/Scripts/python.exe"))  # Path to Python executable
    script_path = os.path.abspath(__file__)  # Path to this script

    task_name = "PythonReminderApp"
    # Command to add the task in Task Scheduler
    command = f'schtasks /create /tn "{task_name}" /tr "{python_executable} {script_path}" /sc MINUTE /mo 1 /f'
    
    try:
        subprocess.run(command, shell=True, check=True)
        messagebox.showinfo("Scheduler", "Task has been scheduled in Windows Task Scheduler.")
    except subprocess.CalledProcessError:
        messagebox.showerror("Scheduler Error", "Failed to schedule the task in Windows Task Scheduler.")

# Function to start the reminder check periodically using threading
def start_reminder_check():
    def check_periodically():
        while True:
            check_due_reminders()
            time.sleep(60)  # Check every 60 seconds
    
    # Start the background thread for periodic check
    reminder_thread = Thread(target=check_periodically, daemon=True)
    reminder_thread.start()

# Setting up the GUI
root = tk.Tk()
root.title("Reminder Application")
root.geometry("500x400")

# Set a background color
root.config(bg="#f0f8ff")

# Set custom font for labels and buttons
label_font = font.Font(family="Arial", size=12, weight="bold")
button_font = font.Font(family="Arial", size=10, weight="bold")

# Title label and entry
label_title = tk.Label(root, text="Reminder Title:", font=label_font, bg="#f0f8ff", anchor="w")
label_title.pack(pady=5, padx=20, fill='x')
entry_title = tk.Entry(root, width=30, font=("Arial", 12))
entry_title.pack(pady=5)

# Time label and entry
label_time = tk.Label(root, text="Reminder Time (YYYY-MM-DD HH:MM):", font=label_font, bg="#f0f8ff", anchor="w")
label_time.pack(pady=5, padx=20, fill='x')
entry_time = tk.Entry(root, width=30, font=("Arial", 12))
entry_time.pack(pady=5)

# Add reminder button with custom styles
btn_add = tk.Button(root, text="Add Reminder", command=add_reminder, font=button_font, bg="#4CAF50", fg="white", relief="raised", width=15)
btn_add.pack(pady=10)

# Schedule task button with custom styles
btn_schedule = tk.Button(root, text="Schedule Reminder Check", command=schedule_task, font=button_font, bg="#2196F3", fg="white", relief="raised", width=20)
btn_schedule.pack(pady=10)

# Start periodic reminder check button
btn_start_check = tk.Button(root, text="Start Periodic Reminder Check", command=start_reminder_check, font=button_font, bg="#FF9800", fg="white", relief="raised", width=25)
btn_start_check.pack(pady=10)

# Run the GUI main loop
root.mainloop()
