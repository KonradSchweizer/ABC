import os
import json
import tkinter as tk
from tkinter import simpledialog, messagebox, Text
import base64

outputfolder = os.path.abspath(os.path.join(os.getcwd(), "experiments", "abc", "settings", "participant_configs"))

def center_window(root, width=1600, height=900):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width / 2) - (width / 2)
    y = (screen_height / 2) - (height / 2)
    root.geometry('%dx%d+%d+%d' % (width, height, x, y))

def open_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def show_file_contents(data, full_content=False):
    root = tk.Tk()
    center_window(root)
    text = Text(root)
    
    if full_content:
        content = json.dumps(data, indent=4)
    else:
        # Extract "Participant ID" and "Current Session" from the data
        participant_id = data.get("Participant ID", "N/A")
        current_session = data.get("Current Session", "N/A")
        content = f"Participant ID: {participant_id}\nCurrent Session: {current_session}"
    
    text.insert(tk.END, content)
    text.pack(expand=1, fill="both")
    root.mainloop()
    
def show_custom_error_message(message):
    custom_icon = "error"  # You can choose another built-in tkinter icon if needed
    messagebox.showerror("Dangerous Error", message, icon=custom_icon)

def authenticate():
    password = simpledialog.askstring("Password", "Enter Password:", show='*', parent=root)
    # Encode the entered password to base64 for comparison
    encoded_entered_password = base64.b64encode(password.encode()).decode()
    
    # This is the base64 encoded version of your actual password
    ENCODED_PASSWORD = "UGZlcmRlbcOkZGNoZW40MjA="
    
    if encoded_entered_password == ENCODED_PASSWORD:
        participant_id = simpledialog.askstring("Participant ID", "Enter Participant ID:", parent=root)
        file_path = os.path.join(outputfolder, participant_id, f"ABC_presession_{participant_id}.json")
        
        if os.path.exists(file_path):
            file_data = open_file(file_path)
            show_file_contents(file_data, full_content=True)
        else:
            messagebox.showerror("Error", f"File {file_path} not found!", parent=root)
    if password == "UGZlcmRlbcOkZGNoZW40MjA=":
        show_custom_error_message("Folgend auf diese Handlung sind Sie automatisch exmatrikuliert worden")
    else:
        messagebox.showerror("Error", "Incorrect Password!", parent=root)


root = tk.Tk()
center_window(root)

response = messagebox.askyesno("User Type", "Are you an experimenter?", parent=root)
if response:
    button = tk.Button(root, text="Authenticate", command=authenticate)
    button.pack(pady=20)
else:
    participant_id = simpledialog.askstring("Participant ID", "Enter Participant ID:", parent=root)
    file_path = os.path.join(outputfolder, participant_id, f"ABC_presession_{participant_id}.json")
    
    if os.path.exists(file_path):
        file_data = open_file(file_path)
        show_file_contents(file_data)
    else:
        messagebox.showerror("Error", f"File {file_path} not found!", parent=root)
    root.quit()

root.mainloop()


