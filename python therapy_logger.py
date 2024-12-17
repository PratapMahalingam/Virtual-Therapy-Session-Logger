import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import tkcalendar

# Database setup
def setup_database():
    conn = sqlite3.connect("therapy_sessions.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            contact TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            session_date TEXT,
            notes TEXT,
            duration INTEGER,
            session_type TEXT,
            platform TEXT,
            cost REAL,
            payment_status TEXT,
            rating INTEGER,
            feedback TEXT,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        )
    """)
    conn.commit()
    conn.close()

# GUI Functions
def add_patient():
    name = name_var.get()
    age = age_var.get()
    contact = contact_var.get()

    if not name or not age or not contact:
        messagebox.showerror("Error", "All fields are required!")
        return

    conn = sqlite3.connect("therapy_sessions.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO patients (name, age, contact) VALUES (?, ?, ?)", (name, age, contact))
    conn.commit()
    conn.close()

    messagebox.showinfo("Success", "Patient added successfully!")
    name_var.set("")
    age_var.set("")
    contact_var.set("")
    load_patients()

def load_patients():
    conn = sqlite3.connect("therapy_sessions.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM patients")
    patients = cursor.fetchall()
    conn.close()
    patient_list['values'] = [f"{patient[0]}: {patient[1]}" for patient in patients]

def start_session():
    global session_start_time
    selected = patient_list.get()
    if not selected:
        messagebox.showerror("Error", "Please select a patient to start the session!")
        return

    session_start_time = datetime.now()
    messagebox.showinfo("Info", f"Session started for {selected.split(':')[1].strip()}")

def end_session():
    global session_start_time
    if session_start_time is None:
        messagebox.showerror("Error", "No session in progress!")
        return

    duration = (datetime.now() - session_start_time).seconds // 60
    notes = session_notes.get("1.0", tk.END).strip()
    session_type = session_type_var.get()
    platform = platform_var.get() if session_type == "Online" else None
    cost = cost_var.get()
    payment_status = payment_status_var.get()
    rating = rating_var.get()
    feedback = feedback_notes.get("1.0", tk.END).strip()
    selected = patient_list.get()

    if not notes or not session_type or not cost or not payment_status:
        messagebox.showerror("Error", "Please fill all required fields!")
        return

    patient_id = selected.split(':')[0]

    conn = sqlite3.connect("therapy_sessions.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sessions (patient_id, session_date, notes, duration, session_type, platform, cost, payment_status, rating, feedback)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (patient_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), notes, duration, session_type, platform, cost, payment_status, rating, feedback))
    conn.commit()
    conn.close()

    messagebox.showinfo("Success", f"Session ended. Duration: {duration} minutes.")
    session_notes.delete("1.0", tk.END)
    feedback_notes.delete("1.0", tk.END)
    cost_var.set("")
    payment_status_var.set("")
    rating_var.set("")
    session_start_time = None

def schedule_session():
    selected = patient_list.get()
    if not selected:
        messagebox.showerror("Error", "Please select a patient to schedule a session!")
        return

    patient_id = selected.split(':')[0]
    date = calendar.get_date()
    platform = platform_var.get()
    time = time_entry.get()

    if not time or not platform:
        messagebox.showerror("Error", "Please enter time and platform for the session!")
        return

    conn = sqlite3.connect("therapy_sessions.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sessions (patient_id, session_date, notes, duration, session_type, platform)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (patient_id, f"{date} {time}", f"Scheduled on {platform}", 0, "Online", platform))
    conn.commit()
    conn.close()

    messagebox.showinfo("Success", "Session scheduled successfully!")
    platform_var.set("")
    time_entry.delete(0, tk.END)

def view_sessions():
    selected = patient_list.get()
    if not selected:
        messagebox.showerror("Error", "Please select a patient to view their sessions!")
        return

    patient_id = selected.split(':')[0]
    conn = sqlite3.connect("therapy_sessions.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT session_date, notes, duration, session_type, platform, cost, payment_status, rating, feedback
        FROM sessions WHERE patient_id = ?
    """, (patient_id,))
    sessions = cursor.fetchall()
    conn.close()

    if not sessions:
        messagebox.showinfo("Info", "No sessions found for the selected patient.")
        return

    session_info = "\n".join([
        f"Date: {session[0]}, Type: {session[3]}, Platform: {session[4] or 'N/A'}, Duration: {session[2]} minutes, "
        f"Cost: ${session[5]:.2f}, Payment: {session[6]}, Rating: {session[7]}/5\nFeedback: {session[8]}\nNotes: {session[1]}\n"
        for session in sessions
    ])
    messagebox.showinfo("Session History", session_info)

# App setup
setup_database()

root = tk.Tk()
root.title("Virtual Therapy Session Logger")

# Patient Registration
tk.Label(root, text="Add Patient", font=("Arial", 16)).grid(row=0, column=0, columnspan=2, pady=10)

tk.Label(root, text="Name:").grid(row=1, column=0, sticky="e")
tk.Label(root, text="Age:").grid(row=2, column=0, sticky="e")
tk.Label(root, text="Contact:").grid(row=3, column=0, sticky="e")

name_var = tk.StringVar()
age_var = tk.StringVar()
contact_var = tk.StringVar()

tk.Entry(root, textvariable=name_var).grid(row=1, column=1)
tk.Entry(root, textvariable=age_var).grid(row=2, column=1)
tk.Entry(root, textvariable=contact_var).grid(row=3, column=1)

tk.Button(root, text="Add Patient", command=add_patient).grid(row=4, column=0, columnspan=2, pady=10)

# Session Management
tk.Label(root, text="Manage Sessions", font=("Arial", 16)).grid(row=5, column=0, columnspan=2, pady=10)

tk.Label(root, text="Select Patient:").grid(row=6, column=0, sticky="e")

patient_list = ttk.Combobox(root, state="readonly", width=30)
patient_list.grid(row=6, column=1)
load_patients()

session_type_var = tk.StringVar()
tk.Label(root, text="Session Type:").grid(row=7, column=0, sticky="e")
session_type_dropdown = ttk.Combobox(root, textvariable=session_type_var, state="readonly", values=["In-person", "Online"])
session_type_dropdown.grid(row=7, column=1)

tk.Label(root, text="Platform (for Online):").grid(row=8, column=0, sticky="e")
platform_var = tk.StringVar()
platform_dropdown = ttk.Combobox(root, textvariable=platform_var, state="readonly", values=["Zoom", "Google Meet", "Teams"])
platform_dropdown.grid(row=8, column=1)

tk.Label(root, text="Cost ($):").grid(row=9, column=0, sticky="e")
cost_var = tk.StringVar()
tk.Entry(root, textvariable=cost_var).grid(row=9, column=1)

tk.Label(root, text="Payment Status:").grid(row=10, column=0, sticky="e")
payment_status_var = tk.StringVar()
payment_status_dropdown = ttk.Combobox(root, textvariable=payment_status_var, state="readonly", values=["Paid", "Pending", "Overdue"])
payment_status_dropdown.grid(row=10, column=1)

tk.Label(root, text="Session Notes:").grid(row=11, column=0, sticky="ne")
session_notes = tk.Text(root, width=40, height=5)
session_notes.grid(row=11, column=1)

tk.Label(root, text="Rating (1-5):").grid(row=12, column=0, sticky="e")
rating_var = tk.IntVar()
tk.Spinbox(root, from_=1, to=5, textvariable=rating_var).grid(row=12, column=1)

tk.Label(root, text="Feedback:").grid(row=13, column=0, sticky="ne")
feedback_notes = tk.Text(root, width=40, height=3)
feedback_notes.grid(row=13, column=1)

tk.Button(root, text="Start Session", command=start_session).grid(row=14, column=0, columnspan=2, pady=5)
tk.Button(root, text="End Session", command=end_session).grid(row=15, column=0, columnspan=2, pady=5)
tk.Button(root, text="View Sessions", command=view_sessions).grid(row=16, column=0, columnspan=2, pady=5)

# Scheduling Feature
tk.Label(root, text="Schedule Session", font=("Arial", 16)).grid(row=17, column=0, columnspan=2, pady=10)

tk.Label(root, text="Date:").grid(row=18, column=0, sticky="e")
calendar = tkcalendar.Calendar(root)
calendar.grid(row=18, column=1)

tk.Label(root, text="Time (HH:MM):").grid(row=19, column=0, sticky="e")
time_entry = tk.Entry(root)
time_entry.grid(row=19, column=1)

tk.Button(root, text="Schedule Session", command=schedule_session).grid(row=20, column=0, columnspan=2, pady=10)

root.mainloop()
