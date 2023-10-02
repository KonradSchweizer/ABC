import tkinter as tk
from tkinter import ttk

class MyApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.data = {}
        self.identify_participant()

    def identify_participant(self):
        self.geometry('1920x1080')  # Set your preferred dimensions
        self.configure(bg='black')

        title_label = tk.Label(self, text="Enter Participant Details", bg='black', fg='white')
        title_label.pack(pady=10)

        id_label = tk.Label(self, text="Participant ID (6 digits only):", bg='black', fg='white')
        id_label.pack(pady=10)

        self.id_entry = tk.Entry(self)
        self.id_entry.pack(pady=10)

        gender_label = tk.Label(self, text="Gender:", bg='black', fg='white')
        gender_label.pack(pady=10)

        self.gender_combobox = ttk.Combobox(self, values=["Male", "Female", "Other"])
        self.gender_combobox.pack(pady=10)

        submit_button = tk.Button(self, text="Submit", command=self.validate_and_save)
        submit_button.pack(pady=20)

        # Binding the 'Escape' key to close the window
        self.bind('<Escape>', lambda event=None: self.destroy())

    def validate_and_save(self):
        participant_id = self.id_entry.get()
        gender = self.gender_combobox.get()

        if len(participant_id) == 6 and participant_id.isdigit() and gender in ["Male", "Female", "Other"]:
            self.data["Participant ID"] = participant_id
            self.data["Sex"] = gender
            self.data["Condition"] = ""
            self.data["Current Session"] = 0
            self.destroy()  # Close the window after successful input
        else:
            error_label = tk.Label(self, text="Invalid input, please enter a valid ID and gender", bg='black', fg='red')
            error_label.pack(pady=10)


if __name__ == "__main__":
    app = MyApplication()
    app.mainloop()
