import tkinter as tk
from tkinter import filedialog
from psychopy import event, core, visual, gui, data, monitors, logging	

# Create a function to close the Tkinter window
def close_window():
    root.destroy()

# Create a function to handle the "Submit" button click event
def submit_action():
    # You can add your code to process the submitted data here
    pass

# Create a function to handle the "Save" button click event
def save_action():
    # You can add your code to save the data or image here
    file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
    if file_path:
        # You can add code to save the image to the selected file
        pass

# Create the main Tkinter window
root = tk.Tk()
root.geometry("800x600")
root.title("Imagination Instruction")

# Create a label with the imagination instruction
instruction_label = tk.Label(root, text="Imagine yourself on a beach, listening to the waves and feeling the warm sun on your skin.")
instruction_label.pack(pady=50)

# Create a canvas to display the image
canvas = tk.Canvas(root, width=200, height=200)
canvas.create_rectangle(0, 0, 200, 200, fill="white")  # Placeholder for the image
canvas.place(relx=0.5, rely=0.6, anchor="center")

# Create a function to handle the "Submit" button click event
def submit_action():
    print("Submit button clicked")

# Create a "Submit" button
submit_button = tk.Button(root, text="Submit", command=submit_action)
submit_button.pack(pady=10)

# Create a function to handle the "Save" button click event
def save_action():
    print("Save button clicked")

# Create a "Save" button
save_button = tk.Button(root, text="Save Image", command=save_action)
save_button.pack(pady=10)

# Bind the Enter key to the "Submit" action
root.bind('<Return>', lambda event=None: submit_action())

# Run the Tkinter main loop
root.mainloop()
