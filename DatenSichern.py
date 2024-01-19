import os
import ctypes
import datetime
import shutil
import tkinter as tk

# Function to get all available drives
def get_drives():
    drives = []
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        if bitmask & 1:
            drives.append(letter)
        bitmask >>= 1
    return drives

# Function to find the first available removable drive (USB stick)
def find_usb_drive():
    DRIVE_REMOVABLE = 2
    for drive in get_drives():
        if ctypes.windll.kernel32.GetDriveTypeW(f"{drive}:/") == DRIVE_REMOVABLE:
            return f"{drive}:/"
    return None

# Define the fixed external drive and create a folder with the current date and time
external_drive = "R:\\ABC-Saves"
current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
current_datetime_folder = os.path.join(external_drive, f"AATsave_{current_datetime}")

# Create the folder if it doesn't exist
if not os.path.exists(current_datetime_folder):
    os.makedirs(current_datetime_folder)

# Define the paths to the source directories
config_path = os.path.abspath(os.path.join(os.getcwd(), "experiments", "abc", "settings", "participant_configs"))
output_path = os.path.abspath(os.path.join(os.getcwd(), "experiments", "abc", "output"))

# Copy the directories to the current date and time folder on the fixed external drive
destination_config_path = os.path.join(current_datetime_folder, "participant_configs")
destination_output_path = os.path.join(current_datetime_folder, "output")

if not os.path.exists(destination_config_path):
    shutil.copytree(config_path, destination_config_path)

if not os.path.exists(destination_output_path):
    shutil.copytree(output_path, destination_output_path)

# Find the first available USB drive
usb_drive = find_usb_drive()

# Create a simple GUI window to display information
root = tk.Tk()
root.title("Daten gespeichert")

# Function to update the GUI with information
def update_gui(text):
    label = tk.Label(root, text=text, wraplength=300)
    label.pack()
    
def check_token_exists(usb_drive):
    if usb_drive is not None:
        token_path = os.path.join(usb_drive, "token.txt")
        if os.path.exists(token_path):
            with open(token_path, 'r') as file:
                content = file.read()
                if content == "ABC as easy as 123":
                    return True
        else:
            return False
    return False

# Display information about the saved data
if usb_drive is not None and check_token_exists(usb_drive):
    usb_datetime_folder = os.path.join(usb_drive, f"AATsave_{current_datetime}")

    # Check if directories exist on the USB drive, and if not, create and copy them
    usb_destination_config_path = os.path.join(usb_datetime_folder, "participant_configs")
    usb_destination_output_path = os.path.join(usb_datetime_folder, "output")

    if not os.path.exists(usb_datetime_folder):
        os.makedirs(usb_datetime_folder)

    if not os.path.exists(usb_destination_config_path):
        shutil.copytree(config_path, usb_destination_config_path)

    if not os.path.exists(usb_destination_output_path):
        shutil.copytree(output_path, usb_destination_output_path)

    update_gui(f"Daten auf externer Festplatte gespeichert")
    update_gui(f"Daten wurden auch auf dem USB-Laufwerk gespeichert")
else:
    update_gui(f"Daten nur auf externer Festplatte gespeichert")

root.mainloop()
