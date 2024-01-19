import tkinter as tk
import os

def submit_action():
    entered_id = id_entry.get()
    if len(entered_id) == 6 and entered_id.isdigit():
        config_path = "experiments/abc/settings/participant_configs"
        file_path = f"{config_path}/{entered_id}"  # e.g. experiments/abc/settings/participant_configs/123456
        if not os.path.exists(file_path):
            window.destroy()
            from experiments.abc.experiment_classes.ABC_Presession import ABCPresession
            ABCPresession().run()
            
        else:
            window.destroy()
            from experiments.abc.experiment_classes.ABC_Experiment import ABCExperiment
            exp = ABCExperiment() 
            exp.prepare_experiment() 
            exp.run_experiment()
    else:
        # Display an error message if the ID is not valid
        error_label.config(text="Ungültige Fallnummer", fg="red")

def close_window(event):
    window.destroy()

window = tk.Tk()
window.geometry('1920x1080')
window.configure(bg='black')
window.attributes('-topmost', True)
window.after_idle(window.attributes, '-topmost', False)

window.bind("<Escape>", close_window)

title_label = tk.Label(window, text="Anti-Alkohol Training", bg='black', fg='white', font=("Arial", 30))
title_label.pack(pady=50)

id_label = tk.Label(window, text="Fallnummer", bg='black', fg='white', font=("Arial", 24))
id_label.pack(pady=20)

id_entry = tk.Entry(window, font=("Arial", 24))
id_entry.pack(pady=20)

submit_button = tk.Button(window, text="Fortfahren", bg='blue', fg='white', font=("Arial", 20), command=submit_action)
submit_button.config(width=10)  # Set the width of the button
submit_button.pack(pady=20)

error_label = tk.Label(window, text="", bg='black', fg='black', font=("Arial", 16))  # Set the text color to black
error_label.pack()

window.mainloop()
submit_button.pack(pady=20)

error_label = tk.Label(window, text="", bg='black', fg='black', font=("Arial", 16))  # Set the text color to black
error_label.pack()

window.mainloop()
