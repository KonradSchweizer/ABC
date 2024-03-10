# Programmer: Luke Korthals, https://github.com/lukekorthals

# The ABCPresession class builds upon the Presession class.
# Each participant has to run a presession before the first experimental session. 
# During the presession, participants rate scenarios, consequences, and images of drinks. 
# As a result a config is created for their participant ID, which determines the scenarios, 
# consequences, and images available to the participant (given their condition includes A B', or C). 

###########
# Imports #
###########
# Standard libraries
import json
from math import ceil
import os
from psychopy import gui, visual, event, core
from random import shuffle, choice
from typing import Tuple, List, Dict
import tkinter as tk
from tkinter import ttk
from psychopy.visual import ImageStim
import random 
from random import shuffle
import pygame.mixer
import time
# Local modules
from classes.Presession import Presession
from experiments.abc.experiment_classes.ABC_Language import ABCLanguage
from experiments.abc.experiment_classes.ABC_StimulusSet import ABCStimulusSet, ABCStimulusSetA, ABCStimulusSetB, ABCStimulusSetPersonalization, ABCStimulusSetStandard
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning) #Fuck them warnings

#######################
# ABCPresession Class 
#######################
class ABCPresession(Presession):
    """The presession for the ABC experiment"""
    
    def __init__(self, 
                 language = ABCLanguage(), 
                 config_path = "experiments/abc/settings/participant_configs", 
                 experiment_name = "ABC",
                 images_path = "experiments/abc/images/Stimuli_V2",
                 non_alc_images_path = "experiments/abc/images/non_alcoholic_images",
                 alc_images_path = "experiments/abc/images/alcoholic_images",
                 img_set_a: ABCStimulusSet = ABCStimulusSetA(),
                 img_set_b: ABCStimulusSet = ABCStimulusSetB(),
                 img_set_standard: ABCStimulusSet = ABCStimulusSetStandard(),
                 img_set_personalization: ABCStimulusSet = ABCStimulusSetPersonalization()) -> None:
        self.images_path = images_path # DEPRECATED (now using Stimulus Sets)
        non_alc_images_path = non_alc_images_path # DEPRECATED (used for image rating) 
        alc_images_path = alc_images_path # DEPRECATED (used for image rating) 
        self.img_set_a = img_set_a
        self.img_set_b = img_set_b
        self.img_set_personalization = img_set_personalization
        super().__init__(language, config_path, experiment_name)

    def validate_language(self) -> None:
        """Language must be ABCLanguage"""
        if not isinstance(self.language, ABCLanguage):
            raise ValueError("language must be a ABCLanguage object")
        
    def quit(self) -> None:
        self.win.close()
        core.quit()

    def wait_keys(self) -> None:
        while True:
            keys = event.getKeys()
            if "space" in keys:
                break
        event.clearEvents()

    def initialize_window(self) -> None:
        self.win = visual.Window([1920, 1080], monitor="testMonitor", color="black", fullscr=True, allowGUI=True)

    def minimize_window(self) -> None:
        """Minimizes the window before showing gui."""
        self.win.winHandle.set_fullscreen(False)
        self.win.winHandle.minimize()
        self.win.flip()
    
    def maximize_window(self) -> None:
        """Maximizes the window after showing gui."""
        self.win.winHandle.maximize()
        self.win.winHandle.activate()
        self.win.winHandle.set_fullscreen(True)
        self.win.flip()

    def data_update_and_destroy(self, participant_id):
        if os.path.exists(f"{self.config_path}/{self.experiment_name}_presession_{participant_id}.json"):
            gui_over_title = self.language["Presession"]["Gui Overwrite"]["Title"]
            gui_over_field1 = self.language["Presession"]["Gui Overwrite"]["Field1"]
            options1 = self.language["Presession"]["Gui Overwrite"]["Options1"]
            overwrite = {gui_over_field1: options1}
            gui.DlgFromDict(dictionary=overwrite, title=gui_over_title)
            if overwrite[gui_over_field1] == options1[0]:
                os.remove(f"{self.config_path}/{self.experiment_name}_presession_{participant_id}.json")
                pass
            
    def identify_participant(self):
        window = tk.Tk()
        window.geometry('1600x900')
        window.configure(bg='black')
        window.attributes('-topmost', True)
        window.after_idle(window.attributes, '-topmost', False)
        # Error label defined here but packed only if error occurs
        error_label = tk.Label(window, text="", bg='black', fg='red', font=("Arial", 24))
        
        def validate_and_save():
            participant_id = id_entry.get()
            gender = gender_combobox.get()
            self.data["Participant ID"] = participant_id
            self.data["Sex"] = gender
            self.data["Condition"] = "" # Condition is determined at first session
            self.data["Condition_saved"] = ""
            self.data["Expectation"] = {}
            self.data["Training_Vividness"] = {} 
            self.data["Consequence"] = {}          
            self.data["Current Session"] = 0
            self.data["non_alcoholic"] = {}
            self.data["alcoholic"] = {}
            if len(participant_id) == 6 and participant_id.isdigit() and gender in self.language["Presession"]["Gui Participant ID"]["Options2"]:
                file_path = f"{self.config_path}/{self.experiment_name}_presession_{participant_id}.json"

                if os.path.exists(file_path):
                    overwrite_dlg = tk.Toplevel(window)
                    overwrite_dlg.attributes('-topmost', True)
                    overwrite_label = tk.Label(overwrite_dlg, text=self.language["Presession"]["Gui Overwrite"]["Field1"])
                    overwrite_label.pack(pady=10)

                    option = tk.StringVar(value=self.language["Presession"]["Gui Overwrite"]["Options1"][0])

                    for val in self.language["Presession"]["Gui Overwrite"]["Options1"]:
                        tk.Radiobutton(overwrite_dlg, text=val, variable=option, value=val).pack()

                    def overwrite():
                        if option.get() == self.language["Presession"]["Gui Overwrite"]["Options1"][0]:
                            os.remove(file_path)
                            overwrite_dlg.destroy()
                            window.destroy()
                            self.data_update_and_destroy(participant_id)
                        else:
                            overwrite_dlg.destroy()

                    overwrite_submit = tk.Button(overwrite_dlg, text="Bestätigen", command=overwrite)
                    overwrite_submit.pack(pady=10)

                else:
                    window.destroy()
                    self.data_update_and_destroy(participant_id)

            else:
                error_label.config(text="Ungültige Eingabe, bitte geben Sie eine gültige Fallnummer (6-stellig) \n und ein Geschlecht aus dem Dropdown-Menü ein")
                error_label.pack(pady=10)
        
        title_label = tk.Label(window, text=self.language["Presession"]["Gui Participant ID"]["Title"], bg='black', fg='white', font=("Arial", 30))
        title_label.pack(pady=50)

        id_label = tk.Label(window, text=self.language["Presession"]["Gui Participant ID"]["Field1"], bg='black', fg='white', font=("Arial", 24))
        id_label.pack(pady=20)

        id_entry = tk.Entry(window, font=("Arial", 24))
        id_entry.pack(pady=20)

        gender_label = tk.Label(window, text=self.language["Presession"]["Gui Participant ID"]["Field2"], bg='black', fg='white', font=("Arial", 24))
        gender_label.pack(pady=20)

        gender_combobox = ttk.Combobox(window, values=self.language["Presession"]["Gui Participant ID"]["Options2"], font=("Arial", 24))
        gender_combobox.pack(pady=20)

        submit_button = tk.Button(window, text="Fortfahren", bg='blue', fg='white', font=("Arial", 20), command= validate_and_save)
        submit_button.pack(pady=50)
        window.mainloop()
    
    def wait_screen(self) -> None:
        """Screen that asks participants to wait because sometimes it takes a while to 
        load the next screen and repeatedly pressing buttons breaks the program"""
        instruction_text = self.language["Presession"]["Wait Screen"]["Text"]
        instruction = visual.TextStim(self.win, text=instruction_text, color="white", pos=(0,0), font="Arial", height=0.05)
        instruction.draw()
        self.win.flip()

    def instruction_screen(self) -> None:
        title_text = self.language["Presession"]["Instruction Screen"]["Title"]
        instruction_text = self.language["Presession"]["Instruction Screen"]["Text"]
        continue_text = self.language["Presession"]["Instruction Screen"]["Continue"]
        title = visual.TextStim(self.win, text=title_text, color="lightgrey", pos=(0, 0.9), font="Arial", height=0.07, wrapWidth= 1.6)
        continue_text = visual.TextStim(self.win, text=continue_text, color="blue", pos=(0, -0.95), font="Arial", height=0.07)
        instruction = visual.TextStim(self.win, text=instruction_text, color="white", pos=(0, 0), font="Arial", height=0.06, alignText='left', wrapWidth= 1.6)
        title.draw()
        instruction.draw()
        continue_text.draw()
        self.win.flip()
        self.wait_keys()  

    def imagine_scenario_screen(self) -> None:
        self.data["Imagination Ratings"] = {}
        # Rate Desire Pre Screen
        instruction_text = self.language["Presession"]["Rate Desire Pre Screen"]["Text"]
        continue_text = self.language["Presession"]["Rate Desire Pre Screen"]["Continue"]
        slider_labels = self.language["Presession"]["Rate Desire Pre Screen"]["Labels"]
        instruction = visual.TextStim(self.win, text=instruction_text, color="white", pos=(0, 0), font="Arial", height=0.06)
        continue_stim = visual.TextStim(self.win, text=continue_text, color="blue", pos=(0, -0.95), font="Arial", height=0.06)
        slider = visual.Slider(self.win, 
                               pos=(0, -0.5), 
                               ticks=(0, 100), 
                               labels=slider_labels, 
                               labelHeight=0.05,
                               granularity=1, 
                               style="rating", 
                               size=(1, 0.05), 
                               color="white",
                               flip=False,
                               font = "Arial")
        
        timer = core.Clock() 
        
        while True:
            slider.draw()
            instruction.draw()
            continue_stim.draw()
            self.win.flip()
            rating = slider.getRating()
            keys = event.getKeys()
            if "space" in keys and rating is not None:
                if timer.getTime() > 1:
                    self.data["Imagination Ratings"]["Desire Pre"] = slider.getRating()
                    break

        self.audio_imagination_screen()
        # Rate Desire Post Screen
        text_1 = self.language["Presession"]["Rate Desire Post Screen"]["Text 1"]
        slider_labels_1 = self.language["Presession"]["Rate Desire Post Screen"]["Labels 1"]
        #text_2 = self.language["Presession"]["Rate Desire Post Screen"]["Text 2"]
        #slider_labels_2 = self.language["Presession"]["Rate Desire Post Screen"]["Labels 2"]
        continue_text = self.language["Presession"]["Rate Desire Post Screen"]["Continue"]
        
        instruction_1 = visual.TextStim(self.win, text=text_1, color="white", pos=(0, 0.25), font="Arial", height=0.05)
        #instruction_2 = visual.TextStim(self.win, text=text_2, color="white", pos=(0, -0.15), font="Arial", height=0.05)
        continue_stim = visual.TextStim(self.win, text=continue_text, color="blue", pos=(0, -0.95), font="Arial", height=0.06)
        slider_1 = visual.Slider(self.win, 
                               pos=(0, 0), 
                               ticks=(0, 100), 
                               labels=slider_labels_1, 
                               labelHeight=0.05,
                               granularity=1, 
                               style="rating", 
                               size=(1, 0.05), 
                               color="white", 
                               flip=False,
                               font = "Arial")
    
        timer = core.Clock()
        
        while True:
            slider_1.draw()
            #slider_2.draw()
            instruction_1.draw()
            #instruction_2.draw()
            continue_stim.draw()
            self.win.flip()
            rating_1 = slider_1.getRating()
            #rating_2 = slider_2.getRating()
            keys = event.getKeys()
            if "space" in keys and rating_1 is not None:
                if timer.getTime() > 1:
                    self.data["Imagination Ratings"]["Imagination Vividness"] = slider_1.getRating()
                    #self.data["Imagination Ratings"]["Desire Post"] = slider_2.getRating()
                    break
            
    def audio_imagination_screen(self):

        # Display instruction text
        instruction = visual.TextStim(self.win, text="Bitte setzen Sie ihre Kopfhörer auf und drücken Sie die Leerstaste wenn Sie eine bequeme position gefunden haben", color="white", pos=(0, 0), font="Arial", height=0.06)
        instruction.draw()
        visual.TextStim(self.win, text="Bitte drücken Sie die LEERTASTE, um fortzufahren.", color="Blue", pos=(0, -0.95), font="Arial", height=0.06).draw()
        visual.TextStim(self.win, text="Vorstellungsübung", color="Grey", pos=(0, 0.95), font="Arial", height=0.06).draw()
        self.win.flip()
        keys = event.waitKeys(keyList=['space'])

        # Create buttons and labels
        pause_button = visual.Rect(self.win, width=0.28, height=0.1, pos=(-0.25, -0.55), fillColor="grey")
        pause_label = visual.TextStim(self.win, text="Pause", color="white", pos=pause_button.pos)

        restart_button = visual.Rect(self.win, width=0.28, height=0.1, pos=(0.25, -0.55), fillColor="grey")
        restart_label = visual.TextStim(self.win, text="Restart", color="white", pos=restart_button.pos)

        picture_path = os.path.abspath(os.path.join(os.getcwd(), "experiments", "abc", "audio", "NiceHospital.png"))
        picture = visual.ImageStim(self.win, image= picture_path , pos=(0, 0))
        
        Text = visual.TextStim(self.win, text = "", color = "white", pos = (0,0), height = 0.1)

        if "space" in keys:
            # Load and play the audio
            pygame.mixer.init()
            audio = os.path.abspath(os.path.join(os.getcwd(), "experiments", "abc", "audio", "Con12.mp3"))
            pygame.mixer.music.load(audio)
            pygame.mixer.music.play()
            
            play = visual.ImageStim(self.win, image= os.path.abspath(os.path.join(os.getcwd(), "experiments", "abc", "audio", "PlayPause.png")) , pos= (-0.25, -0.4))
            Rewind = visual.ImageStim(self.win, image= os.path.abspath(os.path.join(os.getcwd(), "experiments", "abc", "audio", "Rewind.png")), pos = (0.25, -0.4))

            # Start the clock after starting the audio
            mouse = event.Mouse(win=self.win)
            paused = False

            # Setting two time points and corresponding messages
            time_point1 = 54
            time_point2 = 10000
            message1_displayed = False
            message2_displayed = False
            message_displayed = False 
            playing = True  # Set the initial state to True as audio starts

            while playing:
                # Get the audio elapsed time in seconds
                audio_elapsed_time = pygame.mixer.music.get_pos() / 1000.0  # Convert ms to seconds

                # Check for audio completion
                if not pygame.mixer.music.get_busy() and not paused:
                    playing = False
                    break

                # Handle message pauses
                if not message1_displayed and audio_elapsed_time > time_point1:
                    pygame.mixer.music.pause()
                    Text.text = "Denken Sie daran wie Sie sich die Zähne putzen"
                    paused = True
                    pause_label.text = "Abspielen"
                    message1_displayed = True
                    message_displayed = True
                    core.wait(0.5)
                elif message1_displayed and not message2_displayed and audio_elapsed_time > time_point2:
                    pygame.mixer.music.pause()
                    Text.text = "Second message after 10 seconds."
                    paused = True
                    message2_displayed = True
                    message_displayed = True
                    core.wait(0.5)

                # Handle user interactions
                if mouse.isPressedIn(pause_button) or mouse.isPressedIn(play):
                    if paused:
                        pygame.mixer.music.unpause()
                        pause_label.text = "Pause"
                        paused = False
                        message_displayed = False  # Hide the message
                    else:
                        pygame.mixer.music.pause()
                        pause_label.text = "Abspielen"
                        paused = True
                    core.wait(0.5)
                elif mouse.isPressedIn(restart_button) or mouse.isPressedIn(Rewind):
                    pygame.mixer.music.stop()
                    pygame.mixer.music.play()
                    pause_label.text = "Pause"

                    # Reset the message flags
                    message1_displayed = False
                    message2_displayed = False
                    message_displayed = False
                    core.wait(0.5)

                # Draw components
                play.draw()
                Rewind.draw()
                pause_button.draw()
                pause_label.draw()
                restart_button.draw()
                restart_label.draw()
                if message_displayed:
                    Text.draw()
                self.win.flip()

            core.wait(0.01)
    
    def end_screen(self) -> None:
        end_text = self.language["Presession"]["End Screen"]["Text"]
        continue_text = self.language["Presession"]["End Screen"]["Continue"]
        end = visual.TextStim(self.win, text=end_text, color="white", pos=(0, 0), font="Arial", height=0.07)
        continue_text = visual.TextStim(self.win, text=continue_text, color="blue", pos=(0, -0.95), font="Arial", height=0.05)
        end.draw()
        continue_text.draw()
        self.win.flip()
        timer = core.Clock()
        while timer.getTime() < 5:
            continue
        self.win.flip()
        event.waitKeys(keyList=['j'])
        event.waitKeys(keyList=['f'])
        self.quit()

    def rating_screen(self, rating_dict: dict, rating_name: str, rate_images = False, image_path: str = None):
        """A screen with a slider to rate a given question."""
        # Access relevant information from the rating dictionary
        title_text = rating_dict["Title"]
        instruction_text = rating_dict["Instruction"]
        continue_text = rating_dict["Continue"]
        slider_labels = rating_dict["Labels"]
        
        questions = rating_dict["Questions"]
        
        items = list(questions.items())
        random.shuffle(items)
        questions = dict(items)
        
        
        slider_pos = (0, -0.2)
        question_pos = (0, 0.2)
        
        title = visual.TextStim(self.win, text=title_text, color="lightgrey", pos=(0, 0.95), font= "Arial", height=0.07)
        continue_text = visual.TextStim(self.win, text=continue_text, color="blue", pos=(0, -0.9), font= "Arial", height=0.07)
        # Create the slider
        slider = visual.Slider(self.win, 
                       pos=slider_pos, 
                       size=(1, 0.05), 
                       ticks=(range(0,11)), 
                       labels=slider_labels, 
                       labelHeight=0.07,
                       granularity=1, 
                       style="rating", 
                       color="white", 
                       flip=False,
                       font = "Arial")
        # Create a dictionary to store the ratings
        self.data[rating_name] = {}
        # Loop through the questions
        for question in questions:
            to_draw = []
            slider.reset()
            # Define question text

            if rating_dict["Title"] == "Frühere Trinksituationen":
                question_text = f'wenn ich {question_text}'
                self.data[rating_name]["Custom Text"] = question_text
            else:
                question_text = questions[question]
                question_text_stim = visual.TextStim(self.win, text=f"{instruction_text}\n{question_text}", color="white", pos=question_pos, height=0.07, font="Arial", wrapWidth= 1.5)
            # Draw the screen    
            to_draw += [title, question_text_stim, slider, continue_text]
            timer = core.Clock()
            while True:
                for item in to_draw:
                    item.draw()
                self.win.flip()
                rating = slider.getRating()
                keys = event.getKeys()
                if "space" in keys and rating is not None:
                    if timer.getTime() > 0: ############### Slow down participants set to 1
                        self.data[rating_name][question] = slider.getRating()
                        break
                if "space" in keys and rating is None:
                    visual.TextStim(self.win, text="Bitte beantworten Sie zuerst die Frage in dem Sie auf die Skala klicken.", color="red", pos=(0, 0), height=0.07, font="Arial", wrapWidth= 1.5).draw()
                    self.win.flip()
                    core.wait(3)
        self.win.flip()

    def img_grid_selection(self, panels, directory, type):
        win = self.win
        
        #loading screen
        loading_message = visual.TextStim(win, text="Bitte warten Sie einen Moment, während die Bilder geladen werden. Dieser Prozess kann einige Sekunden in Anspruch nehmen.",
                                      pos=(0, 0), height=0.1, color='white')
        loading_message.draw()
        win.flip()  # Show the loading message on the screen

        # Constants for grid layout
        rows, cols = 3, 5
        height = 0.6  # Height is used for scaling the image

        # Debounce settings
        debounce_time = 0  # Time in seconds to debounce mouse clicks #0.2
        last_click_time = 0 # Timestamp of the last registered click

        # Get a sample image to calculate size ratio
        sample_stimulus = visual.ImageStim(win, image=panels[0][0])
        size_perc = height / sample_stimulus.size[1]
        size = (size_perc * sample_stimulus.size[0], size_perc * sample_stimulus.size[1])

        # Preload images
        preloaded_images = [[visual.ImageStim(win, image=img, size=size) for img in panel] for panel in panels]
        
        # Initialize frames based on preloaded_images
        preloaded_frames = [[visual.Rect(win, width=image_stim.size[0], height=image_stim.size[1], pos=(0,0), lineColor='blue', fillColor=None, lineWidth=4) for image_stim in panel] for panel in preloaded_images]
        # Dictionary to track selected images for each panel
        selected_images = {i: set() for i in range(len(panels))}

        # Adjust the locations for a 5x3 grid based on the size
        locs = []
        for row in range(rows):
            for col in range(cols):
                x_pos = (col + 1) * size[0] * 1.01 - 0.1  # Move to the right
                y_pos = (2 - row) * size[1] * 1.01 - 0.7  # Move down
                locs.append((x_pos, y_pos))

        # Define clickable numbers for panel selection
        panel_selectors = [visual.TextStim(win, text=str(i + 1), pos=(i * 0.1 + 0.1, 0.9), height=0.1, color='white') for i in range(len(panels))]
        selector_boxes = [visual.Rect(win, width=0.09, height=0.178 , pos=selector.pos, lineColor=None, fillColor=None) for selector in panel_selectors]
        # New: Text stimuli for selected image counts
        selected_count_texts = [visual.TextStim(win, text="", pos=(selector.pos[0] - 0.02, selector.pos[1] - 0.07), height=0.05, color='green') for selector in panel_selectors]
        
    # Function to draw a specific panel
        def draw_panel(panel_index, panel_changed):
            if panel_changed:
                for i, (img_stim, frame_stim) in enumerate(zip(preloaded_images[panel_index], preloaded_frames[panel_index])):
                    is_selected = i in selected_images[panel_index]

                    if is_selected:
                        img_stim.opacity = 0.5
                    else:
                        img_stim.opacity = 1

                    img_stim.pos = locs[i]
                    img_stim.draw()

        # Main loop for panel selection and display
        current_panel, last_panel = 0, -1
        mouse = event.Mouse(win=win)
        visited_panels = set()

        # Draw static elements outside the loop
        forward = visual.Rect(win, width=0.2, height=0.1, pos=(-0.2, -0.75), fillColor="grey", lineColor="blue", lineWidth=1)
        forward_text = visual.TextStim(win, text="Vorwärts", pos=(-0.2, -0.75), color='white', height=0.05,font="Arial")

        backward = visual.Rect(win, width=0.2, height=0.1, pos=(-0.8, -0.75), fillColor="grey", lineColor="blue", lineWidth=1)
        backward_text = visual.TextStim(win, text="Zurück", pos=(-0.8, -0.75), color='white', height=0.05,font="Arial")

        instructions = visual.TextStim(win, text="Klicken Sie einmal, um ein Getränk auszuwählen.\n\nKlicken Sie erneut, um die Auswahl wieder aufzuheben.",
                                    pos=(-0.5, 0.65), font="Arial", height=0.06, wrapWidth=0.8, color='white', alignText='left')
        
        new_pictures_indices = {panel_idx: set() for panel_idx in range(len(panels))}
        
        while True:
            win.flip()
            panel_changed = current_panel != last_panel
            if panel_changed:
                draw_panel(current_panel, panel_changed)
            last_panel = current_panel
            
            for img_stim in preloaded_images[current_panel]:
                img_stim.draw()
                
                    
            # Update visited panels
            visited_panels.add(current_panel)

            # Draw and handle panel selectors
            for i, (selector, selector_box, count_text) in enumerate(zip(panel_selectors, selector_boxes, selected_count_texts)):
                if panel_changed or i == current_panel or i in visited_panels:
                    selector.color = 'black' if i == current_panel else 'white' if i in visited_panels else 'red'
                    selector_box.lineColor = 'white' if i == current_panel else None
                    selector_box.fillColor = 'white' if i == current_panel else None
                    

                selector_box.draw()
                selector.draw()

                # Update count text only if necessary
                self_selected_count = len(selected_images[i]) - len(new_pictures_indices[i])

                if self_selected_count > 0:
                    count_text.text = str(self_selected_count)
                    count_text.color = 'green'
                    count_text.draw() 
                # Debounce mechanism for panel selection
                if time.time() - last_click_time > debounce_time and mouse.isPressedIn(selector_box):
                    current_panel = i
                    last_click_time = time.time()
                    break

            # Draw navigation buttons
            forward.draw()
            forward_text.draw()
            backward.draw()
            backward_text.draw()    
            
            #Draw instructions
            instructions.draw()
            # Handle key presses for panel navigation
            keys = event.getKeys()
            if 'left' in keys or mouse.isPressedIn(backward):
                current_panel = (current_panel - 1) % len(panels)
                core.wait(0.2)
            elif 'right' in keys or mouse.isPressedIn(forward):
                current_panel = (current_panel + 1) % len(panels)
                core.wait(0.2)
                
            # Draw the counter for selected images
            total_selected = sum(len(v) for v in selected_images.values())
            counter_stimulus = visual.TextStim(win, text=f"Ausgewählte Getränke: {total_selected}/45", pos=(-0.5, 0.35), height=0.1, color='red' if total_selected < 20 or total_selected > 45 else  'Green')
            counter_stimulus.draw()


        # Check for image selection with debounce
            if mouse.getPressed()[0] == 1:
                if time.time() - last_click_time > debounce_time:
                    for i, img_stim in enumerate(preloaded_images[current_panel]):
                        if mouse.isPressedIn(img_stim):
                            selected_images[current_panel].symmetric_difference_update([i])
                            img_stim.opacity = 0.5 if i in selected_images[current_panel] else 1
                            if i in new_pictures_indices[current_panel]:
                                    new_pictures_indices[current_panel].remove(i)
                                    img_stim.opacity = 1
                            last_click_time = time.time()
                            break
                while True:
                        if mouse.getPressed()[0] == 0:
                            break

            # Update reminder text
            unseen_panels = len(panels) - len(visited_panels)
            if len(visited_panels) < len(panels):
                text = f"Gucken Sie sich bitte die verbleibenden {unseen_panels} Seiten an"
                if total_selected > 45:
                    text += " und entfernen Sie Getränke, bis Sie 45 Getränke ausgewählt haben"
            elif total_selected > 45:
                text = "Sie haben zu viele Getränke ausgewählt. Bitte entfernen Sie Getränke, bis Sie 45 Getränke ausgewählt haben"
            else:
                text = ""

            Reminder = visual.TextStim(win, text=text, pos=(-0.5, 0), height=0.07, wrapWidth=0.8, color='red', alignText='left')
            Reminder.draw()

            # Continue button
                
            if total_selected >= 20 and not len(visited_panels) < len(panels) and total_selected <= 45:
                
                picsLeft = 45 - total_selected
                if total_selected != 45:
                    AIREPLACE = visual.ButtonStim(win, text=f"Weitere Getränke automatisch auswählen und Fortfahren", pos=(-0.5, -0.25), color='white', fillColor="blue", borderColor=None, size=(0.4, 0.15), font="Arial")
                    AIREPLACE.draw()
                if total_selected == 45:
                    AIREPLACE = visual.ButtonStim(win, text=f"Fortfahren", pos=(-0.5, -0.25), color='white', fillColor="blue", borderColor=None, size=(0.4, 0.15), font="Arial")
                    AIREPLACE.draw()
                if mouse.isPressedIn(AIREPLACE):
                    loading_message = visual.TextStim(win, text="Bitte warten Sie einen Moment, während ihre Auswahl verarbeitet wird. Dieser Prozess kann einige Sekunden in Anspruch nehmen.",
                                      pos=(0, 0), height=0.1, color='white',font="Arial")
                    loading_message.draw()
                    win.flip()  # Show the loading message on the screen

                    selected_image_paths = {panel_idx: [panels[panel_idx][img_idx] for img_idx in img_indices]
                                            for panel_idx, img_indices in selected_images.items()}

                    # Get the new pictures selected by the AI
                    new_pictures = self.AiReplace(selected_image_paths, directory, type)

                    # Initialize new_pictures_indices as a dictionary
                    new_pictures_indices = {panel_idx: set() for panel_idx in range(len(panels))}
                    for pic in new_pictures:
                        for panel_idx, panel in enumerate(panels):
                            if pic in panel:
                                img_idx = panel.index(pic)
                                selected_images[panel_idx].add(img_idx)
                                new_pictures_indices[panel_idx].add(img_idx)
                                
                    selected_image_paths = {panel_idx: [panels[panel_idx][img_idx] for img_idx in img_indices]
                                                for panel_idx, img_indices in selected_images.items()}
                    new_pictures_indices_paths = {panel_idx: [panels[panel_idx][img_idx] for img_idx in img_indices]
                                for panel_idx, img_indices in new_pictures_indices.items()}
                    return selected_image_paths, new_pictures_indices_paths
                    
            
            else:
                AIREPLACE = visual.ButtonStim(win, text=f"Weitere Getränke automatisch auswählen und Fortfahren", pos=(-0.5, -0.25), color='white', fillColor="Grey", borderColor=None, size=(0.4, 0.15), font="Arial")
                AIREPLACE.draw()
                if mouse.isPressedIn(AIREPLACE):
                    if total_selected < 20:
                        text1 = "Sie müssen mindestens 20 Getränke auswählen, bevor Sie die automatische Auswahl verwenden können"
                    if total_selected > 45:
                        text1 = "Bitte entfernen Sie Getränke, um die automatische Auswahl verwenden zu können"
                    if len(visited_panels) < len(panels):
                        text1 = "\nBitte schauen Sie sich alle Seiten an, um die automatische Auswahl verwenden zu können"
                    
                    warning = visual.TextStim(win, text=text1, pos=(-0.5, -0.5), height=0.07, wrapWidth=0.8, color='red', alignText='left')
                    warning.draw()
                    win.flip()
                    core.wait(3)
                
                        
            event.clearEvents(eventType='mouse')
            # Clear only mouse events

    def AiReplace(self, selected_images, directory, type):
        new_ai_images = self.balance_dictionary_to_45(selected_images, directory, type)
        
        return new_ai_images

    def count_drink_types(self, dictionary):
        beer_sum = 0
        liquor_sum = 0
        wine_sum = 0

        for key, values in dictionary.items():
            if 0 <= key <= 2:  # Keys 0 to 2 are beers
                beer_sum += len(values)
            elif 3 <= key <= 5:  # Keys 3 to 5 are liquors
                liquor_sum += len(values)
            elif 6 <= key <= 8:  # Keys 6 to 8 are wines
                wine_sum += len(values)

        return beer_sum, liquor_sum, wine_sum   

    def count_and_proportion_drink_types(self, dictionary):
        total_count = sum(len(values) for values in dictionary.values())
        beer_count, liquor_count, wine_count = self.count_drink_types(dictionary)

        beer_prop = beer_count / total_count if total_count > 0 else 0
        liquor_prop = liquor_count / total_count if total_count > 0 else 0
        wine_prop = wine_count / total_count if total_count > 0 else 0

        return beer_count, liquor_count, wine_count, beer_prop, liquor_prop, wine_prop

    def pick_additional_pictures(self, category, number_of_pictures, all_pictures, new_dict, directory):
        pics = new_dict.copy()  
        image_directory = directory
        all_pictures = self.list_picture_files(image_directory)
        pics = new_dict.copy()  
        initial_pictures = [item for sublist in pics.values() for item in sublist]
        available_pictures1 = [pic for pic in all_pictures if pic not in initial_pictures]
        category_specifiv_pictures = [pic for pic in available_pictures1 if category in str(pic)]
        # Randomly select the required number of pictures
        selected_pictures = random.sample(category_specifiv_pictures, min(number_of_pictures, len(category_specifiv_pictures)))
        return selected_pictures

    def balance_dictionary_to_45(self, dictionary, directory, type):
        target_total = 45
        new_dict = dictionary.copy()
        replaced = target_total - len(self.flatten_dictionary(dictionary))
        image_directory = directory
        all_pictures = self.list_picture_files(image_directory)
        ai_selected_images = []
        if type == "alcoholic":
            beer_count, liquor_count, wine_count, beer_prop, liquor_prop, wine_prop = self.count_and_proportion_drink_types(dictionary)

            additional_beer = round((target_total * beer_prop) - beer_count)
            additional_liquor = round((target_total * liquor_prop) - liquor_count)
            additional_wine = round((target_total * wine_prop) - wine_count)

              # Store the new images selected by AI
            options = []
            if additional_beer > 0:
                ai_selected_images.extend(self.pick_additional_pictures('Beer', additional_beer, all_pictures, new_dict, directory))
                options.append("Beer")
            if additional_liquor > 0:
                ai_selected_images.extend(self.pick_additional_pictures('Liquor', additional_liquor, all_pictures, new_dict, directory))
                options.append("Liquor")
            if additional_wine > 0:
                ai_selected_images.extend(self.pick_additional_pictures('Wine', additional_wine, all_pictures, new_dict, directory))
                options.append("Wine")
        if type == "non_alcoholic":
            water_count, juice_count, soda_count, water_prop, juice_prop, soda_prop = self.count_and_proportion_drink_types(dictionary)

            additional_water = round((target_total * water_prop) - water_count)
            additional_juice = round((target_total * juice_prop) - juice_count)
            additional_soda = round((target_total * soda_prop) - soda_count)

            # Store the new images selected by AI
            options = []
            if additional_water > 0:
                ai_selected_images.extend(self.pick_additional_pictures('Water', additional_water, all_pictures, new_dict, directory))
                options.append("Water")
            if additional_juice > 0:
                ai_selected_images.extend(self.pick_additional_pictures('Non-Sparkling', additional_juice, all_pictures, new_dict, directory))
                options.append("Non-Sparkling")
            if additional_soda > 0:
                ai_selected_images.extend(self.pick_additional_pictures('Sparkling', additional_soda, all_pictures, new_dict, directory))
                options.append("Sparkling")
                
        if len(ai_selected_images) > 25:
            print("ALARM: AI selected more than 25 images")
            random.shuffle(ai_selected_images)
            ai_selected_images = ai_selected_images[:target_total - len(new_dict)]
        if len(ai_selected_images) < replaced:
            print("ALARM: AI selected less than the required number of images")
            ai_selected_images.extend(self.pick_additional_pictures(random.choice(options), replaced - len(ai_selected_images), all_pictures, new_dict, directory))
        return ai_selected_images

    def flatten_dictionary(self,dictionary):
        flattened_list = []
        for key, value_list in dictionary.items():
            flattened_list.extend(value_list)
        return flattened_list
    
    def list_picture_files(self, directory):
        picture_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(('.jpg', '.png')):
                    full_path = os.path.join(root, file)
                    picture_files.append(full_path)

        return picture_files
    def trim_path_up_to_experiments(self, full_path):
        # Split the path at "experiments/" and keep the part after it
        parts = full_path.split("experiments/")
        # If the split operation found "experiments/", return the part after it, ensuring to prepend "experiments/" back
        if len(parts) > 1:
            return "experiments/" + parts[1]
        else:
            # If "experiments/" is not found, return the original path (or handle as deemed appropriate)
            return full_path
    def categorize_selections(self, selected_image_paths, type):
        # Define the category labels for each type
        categories = {
            "non_alcoholic": ["Sparkling Selection", "Non-Sparkling Selection", "Water Selection"],
            "alcoholic": ["Beer Selection", "Wine Selection", "Liquor Selection"]
        }

        # Initialize a structure to hold the categorized selections
        categorized_selections = {}
        
        # Get the category labels for the current type
        category_labels = categories[type]
        
        # Sort the set IDs to ensure proper order
        sorted_set_ids = sorted(selected_image_paths.keys())
        
        # Temporary storage for current category compilation
        current_category_compilation = {}
        current_category_index = -1

        for i, set_id in enumerate(sorted_set_ids):
            # Determine the category based on the set index
            category_index = i // 3  
            
            # Check if moving to a new category or if it's the first iteration
            if category_index != current_category_index:
                # If not the first iteration, store the previous category compilation
                if current_category_index != -1:
                    category_label = category_labels[current_category_index]
                    categorized_selections[category_label] = current_category_compilation
                # Reset for the new category
                current_category_compilation = {}
                current_category_index = category_index
            
            # Check to avoid index error
            if category_index < len(category_labels):
                # Flatten the set of paths into the current category compilation with continuous numbering
                for path_index, path in selected_image_paths[set_id].items():
                    new_index = len(current_category_compilation) + 1
                    current_category_compilation[new_index] = path

        # Store the last category compilation
        if current_category_compilation:
            category_label = category_labels[current_category_index]
            categorized_selections[category_label] = current_category_compilation

        return categorized_selections

    def image_selection(self,type: str):
        print(type)
        
        script_directory = os.path.dirname(os.path.abspath(__file__))
        parent_directory = os.path.dirname(script_directory)

        if type == "alcoholic":
            directory = os.path.join(parent_directory, "images","set_personalization", "alcoholic")
            directory = directory.replace("\\", "/")
        if type == "non_alcoholic":
            directory = os.path.join(parent_directory, "images","set_personalization", "non_alcoholic")
            directory = directory.replace("\\", "/")

        def list_of_lists(picture_files):
            pictures = picture_files.copy()                          
            #random.shuffle(pictures) #Random or not
            
            # Splitting the list into smaller lists of 15 pictures each
            panels = [pictures[i:i + 15] for i in range(0, len(pictures), 15)]
            
            return panels

        
        files = self.list_picture_files(directory)
        panels = list_of_lists(files)
        selected_image_paths, new_pictures_indices_paths = self.img_grid_selection(panels, directory, type)
        
        for set_id, paths in selected_image_paths.items():
            # Initialize a new dictionary for the trimmed paths with sequence numbers
            numbered_and_trimmed_paths = {}
            # Enumerate through paths, starting index at 1
            for i, path in enumerate(paths, start=1):
                # Trim the path and assign it with a sequence number in the new dictionary
                trimmed_path = self.trim_path_up_to_experiments(path)
                numbered_and_trimmed_paths[i] = trimmed_path
            # Update the set with the new dictionary of numbered, trimmed paths
            selected_image_paths[set_id] = numbered_and_trimmed_paths
        
        for set_id, paths in new_pictures_indices_paths.items():
            # Initialize a new dictionary for the trimmed paths with sequence numbers
            numbered_and_trimmed_paths = {}
            # Enumerate through paths, starting index at 1
            for i, path in enumerate(paths, start=1):
                # Trim the path and assign it with a sequence number in the new dictionary
                trimmed_path = self.trim_path_up_to_experiments(path)
                numbered_and_trimmed_paths[i] = trimmed_path
            # Update the set with the new dictionary of numbered, trimmed paths
            new_pictures_indices_paths[set_id] = numbered_and_trimmed_paths
        
        
        categorized_selections = self.categorize_selections(selected_image_paths, type)
        categorized_automatic_selections = self.categorize_selections(new_pictures_indices_paths, type)
        # Store the categorized selections
        self.data[type] = categorized_selections
        if type == "non_alcoholic":
            self.data["Automatic_Selection_non_alcoholic"] = categorized_automatic_selections
        if type == "alcoholic":
            self.data["Automatic_Selection_alcoholic"] = categorized_automatic_selections
        self.win.flip()

    def pre_scenario(self):
        visual.TextStim(self.win, pos=(0, 0.9), text = "Früheren Trinksituationen", color="lightgrey", height = 0.07, font="Arial").draw()
        visual.TextStim(self.win, text = "Hier finden Sie Situationen, in denen Menschen Alkohol trinken.\n\nBitte geben Sie an, wie häufig Sie in jeder dieser Situationen im letzten Jahr Alkohol getrunken haben.\n\nVerwenden Sie dafür die Maus.\n\nKlicken Sie auf den Strich auf der Skala, der am besten anzeigt, wie häufig Sie in dieser Situation im letzten Jahr getrunken haben.\n\nDrücken Sie die Leertaste, wenn Sie mit Ihrer Entscheidung zufrieden sind.", color="white", pos=(0, 0), font="Arial", height=0.06, alignText='left', wrapWidth= 1.6).draw()
        visual.TextStim(self.win, pos=(0, -0.95), text = "Bitte drücken Sie die LEERTASTE, um fortzufahren.", color="blue", height = 0.07,  font="Arial").draw()
        self.win.flip()
        event.waitKeys(keyList=['space'])
    def pre_consequence(self):
        visual.TextStim(self.win, pos=(0, 0.9), text = "Meine Abstinenzmotive", color="lightgrey", height = 0.07, font="Arial").draw()
        visual.TextStim(self.win, text = "Im Folgenden werden Sie zu Ihren Abstinenzmotiven befragt.\n\nBitte bewerten Sie auf der Skala, wie wichtig die aufgeführten Ziele für Ihre Abstinenz sind.\n\nKlicken Sie dafür mit der Maus auf einen Strich auf der Skala.\n\nWenn Sie mit Ihrer Auswahl zufrieden sind, drücken Sie die Leertaste, um fortzufahren.", color="white", pos=(0, 0), font="Arial", height=0.06, alignText='left', wrapWidth= 1.6).draw()
        visual.TextStim(self.win, pos=(0, -0.95), text = "Bitte drücken Sie die LEERTASTE, um fortzufahren.", color="blue", height = 0.07,  font="Arial").draw()
        self.win.flip()
        event.waitKeys(keyList=['space'])
    def pre_nonalc(self):
        visual.TextStim(self.win, pos=(0, 0.9), text = "Lieblingsgetränke", color="lightgrey", height = 0.07, font="Arial").draw()
        visual.TextStim(self.win, text = "Bitte ordnen sie die gezeigten drei alkoholfreien Getränkegruppen danach ein, wie gern Sie diese trinken.\n\nDer erste Platz steht für die Getränke, die Sie am liebsten und der dritte für jene, die Sie am wenigsten gern trinken würden.\n\nBitte stellen Sie sicher, dass Sie für jede Getränkegruppe einen Platz ausgewählt haben.\nFalls sie sich nicht zwischen den Getränkegruppen entscheiden können, wählen sie den ersten Platz danach aus, was sie am ehesten als Alternative zu Ihrem früheren Alkoholkonsum trinken würden.\n\nBitte klicken Sie mit Ihrer Maus auf die Symbole entsprechend Ihrer Vorlieben. Klicken Sie erneut wenn Sie Ihre Auswahl aufheben möchten, oder drücken Sie „Auswahl zurücksetzen“. Wenn Sie mit Ihrer Auswahl zufrieden sind, klicken Sie mit der Maus auf `Auswahl bestätigen´", color="white", pos=(0, 0), font="Arial", height=0.06, alignText='left', wrapWidth= 1.6).draw()
        visual.TextStim(self.win, pos=(0, -0.95), text = "Bitte drücken Sie die LEERTASTE, um fortzufahren.", color="blue", height = 0.07,  font="Arial").draw()
        self.win.flip()
        event.waitKeys(keyList=['space'])
    def pre_alc(self):
        self.win.flip()
        visual.TextStim(self.win, pos=(0, 0.9), text = "Lieblingsgetränke", color="lightgrey", height = 0.07, font="Arial").draw()
        visual.TextStim(self.win, text = "Bitte ordnen Sie die drei aufgeführten Arten von alkoholischen Getränken danach, wie häufig Sie diese im letzten Jahr getrunken haben.\n\nDer erste Platz steht für die Getränke, die Sie am liebsten und der dritte für jene, die Sie am wenigsten gern trinken würden.\n\nFalls sie sich nicht zwischen den Getränkegruppen entscheiden können, wählen sie den ersten Platz danach aus, was sie am ehesten als Alternative zu Ihrem früheren Alkoholkonsum trinken würden. Bitte stellen Sie sicher, dass Sie für jede Getränkegruppe einen Platz ausgewählt haben.\n\nBitte klicken Sie mit Ihrer Maus auf die Symbole entsprechend Ihrer Vorlieben. Klicken Sie erneut wenn Sie Ihre Auswahl aufheben möchten, oder drücken Sie „Auswahl zurücksetzen“. Wenn Sie mit Ihrer Auswahl zufrieden sind, klicken Sie mit der Maus auf ´Auswahl bestätigen´" , color="white", pos=(0, 0), font="Arial", height=0.06, alignText='left', wrapWidth= 1.6).draw()
        visual.TextStim(self.win, pos=(0, -0.95), text = "Bitte drücken Sie die LEERTASTE, um fortzufahren.", color="blue", height = 0.07,  font="Arial").draw()
        self.win.flip()
        event.waitKeys(keyList=['space'])        
    def create_config(self):
        # Create folder if it doesnt exist
        folder_path = f"{self.config_path}/{self.data['Participant ID']}"
        if not os.path.isdir(folder_path):
            os.mkdir(folder_path)
        # Create config
        try:
            with open(f"{folder_path}/{self.experiment_name}_presession_{self.data['Participant ID']}.json", "w") as f:
                json.dump(self.data, f, indent=4)  
        except:
            raise Exception("Could not save general config.")        
        
    def run(self):       
    # Identify the participant
        self.identify_participant()
        #make sure that participant is registered before pre-session is started
        if self.data["Participant ID"] == "":
            self.win.close()
            return
        
        # Initialize the window
        self.initialize_window()
       
        # Instruction screen
        self.instruction_screen()
        
        # Rate the scenarios
        
        self.pre_scenario()
        text = self.language["Presession"]["Scenario Rating"]
        self.rating_screen(text, "Scenario Rating")
        
        # Rate the consequences
        self.pre_consequence()
        text = self.language["Presession"]["Consequence Rating"]
        self.rating_screen(text, "Consequence Rating")
       
        # Select non-alcoholic drinks
        self.pre_nonalc()
        self.image_selection(type ="non_alcoholic")
        #Select alcoholic drinks
        self.pre_alc()
        self.image_selection(type ="alcoholic")
      
        #imagine Scenario
        self.imagine_scenario_screen()
        # Imagine Consequence
    
        # Json dump the data
        self.create_config()
        # End screen
        self.end_screen()
        self.wait_screen()
        