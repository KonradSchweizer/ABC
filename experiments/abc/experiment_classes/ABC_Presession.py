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
        
        # Main GUI layout with bigger font size and centered
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

        # Bind the "escape" key to quit the entire experiment
        
        
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
            
    def imagery_exercise_screen(self) -> None:
        
        
        # List of imagery exercises
        exercises = [
            {
                "title": None,
                "text": "Prepare yourself for a brief journey of imagination. Ensure you're in a comfortable position, either seated or lying down. Take a deep breath."
            },
            {
                "title": None,
                "text": "Imagine you're slowly awakening in a serene clinic. As your eyes flutter open, you feel a warm ray of sunlight on your face. You glance to the side, noticing the sun gleaming through the window."
            },
            {
                "title": None,
                "text": "Close your eyes for a moment and let that sunlight wash over you."
            },
            {
                "title": None,
                "text": "Feel the urge to explore. Imagine yourself gently rising from the bed and gracefully walking towards the window. You're curious about the world outside."
            },
            {
                "title": None,
                "text": "Close your eyes and picture the scene outside the window."
            },
            {
                "title": None,
                "text": "What do you see? Tall buildings touching the sky, a lush green forest, children playing, or perhaps birds soaring high? Engage with the scenery, feel the connection."
            }
        ]
        space_continue_text = "Press space to continue."

        def wait_for_keys(keys: list) -> str:
            """Waits for specific keys and returns the pressed key."""
            while True:
                pressed_keys = event.getKeys()
                for key in pressed_keys:
                    if key in keys:
                        return key

        def show_text_and_wait(text: str, position: tuple, color: str = "white", height: float = 0.1) -> None:
            """Displays the text and waits for the space key or the escape key."""
            text_stim = visual.TextStim(self.win, text=text, color=color, pos=position, font="Arial", height=height)
            text_stim.draw()
            self.win.flip()
            core.wait(5)

            continue_stim = visual.TextStim(self.win, text=space_continue_text, color="white", pos=(0, -0.95), font="Arial", height=0.05)
            continue_stim.draw()
            text_stim.draw()
            self.win.flip()

            key = wait_for_keys(["space"])
            

        def display_exercise(text, is_intro=False, is_first=False):
            show_text_and_wait(text, (0, 0))

            if is_intro:
                return


        try:
            display_exercise(exercises[0]["text"], is_intro=True)

            display_exercise(exercises[1]["text"], is_first=True)

            for exercise in exercises[2:]:
                display_exercise(exercise["text"])
        except Exception as e:
            print(f"An error occurred: {e}")
            self.quit()
            

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

    def imagine_consequence_screen(self) -> None:
        title_text = self.language["Presession"]["Imagine Consequence Screen"]["Title"]
        instruction_text = self.language["Presession"]["Imagine Consequence Screen"]["Text"]
        continue_text = self.language["Presession"]["Imagine Consequence Screen"]["Continue"]
        title = visual.TextStim(self.win, text=title_text, color="white", pos=(0, 0.95), font="Arial", height=0.05)
        continue_text = visual.TextStim(self.win, text=continue_text, color="white", pos=(0, -0.95), font="Arial", height=0.05)
        instruction = visual.TextStim(self.win, text=instruction_text, color="white", pos=(0, 0), font="Arial", height=0.05)
        title.draw()
        instruction.draw()
        continue_text.draw()
        self.win.flip()
        self.wait_keys() 
    
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
        if rate_images:
            image_names = os.listdir(image_path)
            questions = {image_names[i]: image_names[i] for i in range(0, len(image_names))}
            slider_pos = (0, -0.5)
            question_pos = (0, 0.7)
        else:
            questions = rating_dict["Questions"]
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
            if rate_images:
                question_text_stim = visual.TextStim(self.win, text=f"{instruction_text}", color="white", pos=question_pos, height=0.07, font="Arial")
                image = visual.ImageStim(self.win, image=f"{image_path}/{questions[question]}", pos=(0, 0))
                to_draw.append(image)
            
            
            
            else:
                if question == "Custom1": # Custom1 is chosen to remove the custum question from the list if you want it back change it to "Custom"
                        question_text = self.add_own_scenario_consequence(rating_dict)
                        if not question_text.strip():
                            continue
                        else:
                            if rating_dict["Title"] == "Frühere Trinksituationen":
                                question_text = f'wenn ich {question_text}'
                                self.data[rating_name]["Custom Text"] = question_text
                            else:
                                question_text = question_text
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
                    visual.TextStim(self.win, text="Bitte bewerten Sie die Frage in dem Sie auf die Skala klicken.", color="red", pos=(0, 0), height=0.07, font="Arial", wrapWidth= 1.5).draw()
                    self.win.flip()
                    core.wait(3)
                
        
        self.win.flip()
        
    def add_own_scenario_consequence(self, rating_dict: dict):
        
        if rating_dict["Title"] == "Meine Trinksituationen":
            title_text = rating_dict["Title"]
            instruction_text = rating_dict["Instruction Custom"]
            
            title = visual.TextStim(self.win, text=title_text, color="white", pos=(0, 0.95), font="lightgrey", height=0.07)
            instruction = visual.TextStim(self.win, text=instruction_text, color="white", pos=(0, 0.35), font="Arial", height=0.06, wrapWidth= 1.5, alignText= "left")
            sentence_y_pos = -0.45

            # Width of the text box
            text_box_width = 1.2

            # Since sentence_part1 is aligned right, it should end where the text_box starts. 
            # So, its x-position is -half of the text_box width.
            sentence_part1_x_pos = -text_box_width / 2

            # Similarly, since sentence_part2 is aligned left, it should start where the text_box ends.
            # So, its x-position is half of the text_box width.
            sentence_part2_x_pos = text_box_width / 2

            sentence_part1 = visual.TextStim(self.win, text="Im vergangenen Jahr habe ich oft Alkohol getrunken wenn ich: ", color="white", pos=(0, -0.35), font="Arial", height=0.06, alignHoriz="center")

            sentence_part2 = visual.TextStim(self.win, text=".", color="white", pos=(sentence_part2_x_pos, sentence_y_pos), font="Arial", height=0.05, alignHoriz="left")
            # Adjust size and position of the text box and set color of the text
            text_box = visual.TextBox2(self.win, text="", color="white", pos=(0, sentence_y_pos), font="Arial", letterHeight=0.05, editable=True, borderColor="white", borderWidth=1, size=(1.25, 0.07), anchor="center")

            # Move the buttons closer below the text box
            submit_button = visual.Rect(self.win, width=0.25, height=0.1, fillColor="blue", pos=(-0.15, -0.8))
            submit_text = visual.TextStim(self.win, text="Fortfahren", color="white", pos=submit_button.pos, font="Arial", height=0.05)
            idk_button = visual.Rect(self.win, width=0.25, height=0.1, fillColor="red", pos=(0.15, -0.8 ))
            idk_text = visual.TextStim(self.win, text="Keine Angabe", color="white", pos=idk_button.pos, font="Arial", height=0.05)

            to_draw = [title, instruction, sentence_part1, text_box, sentence_part2, submit_button, submit_text, idk_button, idk_text]
            mouse = event.Mouse()
            
            
            while True:
                for item in to_draw:
                    item.draw()
                    
                    
                
                if len(text_box.text) > 100:
                    warning_text = visual.TextStim(self.win, text="Bitte bleiben sie unter 100 Buchstaben!", color="red", pos=(0, 0.3), font="Arial", height=0.05)
                    warning_text.draw()
                
                self.win.flip()
                
                # Check for mouse click on the submit button
                if mouse.isPressedIn(submit_button):
                    if len(text_box.text) <= 100:
                        return text_box.text
                if mouse.isPressedIn(idk_button):
                    return ""
                
              
        else:
            title_text = rating_dict["Title"]
            instruction_text = rating_dict["Instruction Custom"]

            title = visual.TextStim(self.win, text=title_text, color="lightgrey", pos=(0, 0.95), font="Arial", height=0.07)
            instruction = visual.TextStim(self.win, text=instruction_text, color="white", pos=(0, 0.6), font="Arial", height=0.06, wrapWidth= 1.5, alignText= "left")
            sentence_y_pos = 0

            # Width of the text box
            text_box_width = 0.35

            # Since sentence_part1 is aligned right, it should end where the text_box starts. 
            # So, its x-position is -half of the text_box width.
            sentence_part1_x_pos = -text_box_width / 2

            # Similarly, since sentence_part2 is aligned left, it should start where the text_box ends.
            # So, its x-position is half of the text_box width.
            sentence_part2_x_pos = text_box_width / 2

            sentence_part1 = visual.TextStim(self.win, text="Ein wichtiger Grund abstinent zu bleiben ist: ", color="white", pos=(sentence_part1_x_pos, sentence_y_pos), font="Arial", height=0.06, alignHoriz="right")

            sentence_part2 = visual.TextStim(self.win, text=".", color="white", pos=(sentence_part2_x_pos, sentence_y_pos), font="Arial", height=0.07, alignHoriz="left")
            # Adjust size and position of the text box and set color of the text
            text_box = visual.TextBox2(self.win, text="", color="white", pos=(0, sentence_y_pos), font="Arial", letterHeight=0.05, editable=True, borderColor="white", borderWidth=1, size=(0.35, 0.07), anchor="center")

            # Move the buttons closer below the text box
            submit_button = visual.Rect(self.win, width=0.2, height=0.1, fillColor="blue", pos=(-0.15, -0.8))
            submit_text = visual.TextStim(self.win, text="Fortfahren", color="white", pos=submit_button.pos, font="Arial", height=0.05)
            idk_button = visual.Rect(self.win, width=0.2, height=0.1, fillColor="red", pos=(0.15, -0.8))
            idk_text = visual.TextStim(self.win, text="Keine Angabe", color="white", pos=idk_button.pos, font="Arial", height=0.05)

            to_draw = [title, instruction, sentence_part1, text_box, sentence_part2, submit_button, submit_text, idk_button, idk_text]
            mouse = event.Mouse()

            while True:
                for item in to_draw:
                    item.draw()

                num_words = len(text_box.text.split())

                if len(text_box.text) > 60 or num_words > 3:
                    warning_text = visual.TextStim(self.win, text="Maximal 3 wörter oder 60 Buchstaben", color="red", pos=(0, 0.3), font="Arial", height=0.05)
                    warning_text.draw()

                self.win.flip()
                
                if mouse.isPressedIn(submit_button):
                    if len(text_box.text) <= 60:
                        return text_box.text

                if mouse.isPressedIn(idk_button):
                    return ""

    
            

    def explain_img_grid_selection(self):
        self.win.flip()
        def get_user_input():
            """
            Waits for the user to press a key and returns an action based on the key pressed.
            """
            keys = event.waitKeys(keyList=['space', 'left', 'right'])
            if 'space' in keys:
                return 'next'
            elif 'left' in keys:
                return 'previous'
            elif 'right' in keys:
                return 'skip'
            return None

        def draw_navigation_hints():
            """
            Draws hints on the screen to guide the user on how to navigate.
            """
            hints = [
                ("Drücken Sie die Leertaste um fortzufahren", (0, -0.9)),
                ("Die linke Pfeiltaste drücken um zurück zu kommen", (-0.5, -0.8)),
                ("Die Rechte Pfeiltaste drücken um nach vorne zu kommen", (0.5, -0.8))
            ]
            for text, pos in hints:
                hint_stim = visual.TextStim(self.win, text=text, color="blue", pos=pos, height=0.06, wrapWidth=1.8)
                hint_stim.draw()

        # Create a window for displaying everything
        
        # Pre-loading all images and text stimuli.
        # Replace these paths with the appropriate image paths on your machine.
        img_paths = {
            "1": os.path.join(os.getcwd(), "experiments", "abc", "images", "1.png"),
            "2": os.path.join(os.getcwd(), "experiments", "abc", "images", "2.png"),
            "3": os.path.join(os.getcwd(), "experiments", "abc", "images", "3.png"),
            "3.2": os.path.join(os.getcwd(), "experiments", "abc", "images", "3.2.png"),
            "4": os.path.join(os.getcwd(), "experiments", "abc", "images", "4.png")
        }
        imgs = {key: visual.ImageStim(self.win, image=path, pos=(0, 0)) for key, path in img_paths.items()}
        for img in imgs.values():
            img.size = [i/1.5 for i in img.size]

        # Define text prompts for the user. Modify these as needed.
            texts = [
            "Dies ist eine kurze visuelle Erklärung für die folgende Bildauswahl-Aufgabe.",
            "Die nächsten Bilder auf dem Bildschirm sind Fotos, Sie können mit ihnen NICHT interagieren",
            "Zuerst sehen Sie ein Raster von Bildern auf der linken Seite",
            "Sie können mit der Maus auf die Bilder klicken, um sie auszuwählen",
            "Sie können bis zu 5 Bilder gleichzeitig auswählen",
            "Wenn Sie ein Bild aus Ihrer Auswahl entfernen möchten, können Sie es erneut anklicken",
            "Wenn Sie 5 Bilder gefunden haben, die Ihnen gefallen, können Sie die Leertaste drücken um Forzufahren",
            "Wenn Ihnen keines der Bilder gefällt, oder wenn Sie nur einige mögen, drücken Sie den Button auf der rechten Seite, um Ihre Auswahl zu speichern und die restlichen Bilder auszutauschen",
            "Wiederholen Sie diesen Vorgang, bis Sie 5 Bilder ausgewählt haben.",
            "Wenn Sie diese erklärung Verstanden haben drücken Sie bitte die Leertaste um fortzufahren, wenn nicht können Sie die linke Pfeiltaste drücken um die vorherigen Folien zu sehen"

            ]
        text_stimuli = [visual.TextStim(self.win, text=t, color="white", pos=(0, 0), font="Arial", height=0.07, wrapWidth=1.8) for t in texts]
        
        # Define the sequence in which to show the images and text prompts.
        slides = [
                lambda: text_stimuli[0].draw(),
                lambda: text_stimuli[1].draw(),
                lambda: text_stimuli[2].draw(),
                lambda: imgs["1"].draw(),
                lambda: text_stimuli[3].draw(),
                lambda: text_stimuli[4].draw(),
                lambda: imgs["2"].draw(),
                lambda: text_stimuli[5].draw(),
                lambda: imgs["3"].draw(),
                lambda: text_stimuli[6].draw(),
                lambda: text_stimuli[7].draw(),
                lambda: imgs["3.2"].draw(),
                lambda: imgs["4"].draw(),
                lambda: text_stimuli[8].draw(),
                lambda: text_stimuli[9].draw()
            ]

        index = 0
        while index < len(slides):
            # Draw slide
            slides[index]()
            draw_navigation_hints()
            self.win.flip()

            # Wait for user input and handle navigation
            action = get_user_input()
            if action == 'next':
                index += 1
            elif action == 'previous':
                index = max(0, index - 1)
            elif action == 'skip':
                index += 1


    def img_grid_selection(self, imgs: list, text_dict: dict, completed_panels: int, panels: int, required_imgs: int = 5, selected_imgs: list = []):
        completed_panels = completed_panels
        panels = panels
        # Assertion
        if len(imgs) > 9:
            raise AssertionError("A maximum of nine images can be displayed in the grid.")
        if len(imgs) < 1:
            raise AssertionError("At least one image is required.")
        
        # Text
        title_text = text_dict["Title"]
        instruction_text = text_dict["Instruction"]
        continue_text = text_dict["Continue"]

        # Mouse
        mouse = event.Mouse(win=self.win)
    
        # Randomise images
        #shuffle(imgs)

        # Get the scaled size
        height = 0.6
        stimulus = visual.ImageStim(self.win, image=imgs[0])
        size_perc = height/stimulus.size[1]
        size = (size_perc * stimulus.size[0], size_perc * stimulus.size[1])

        # Set locations according to size
        locs = [
            # Row 1
            (1-4*size[0], size[1]),
            (1-3*size[0], size[1]), 
            (1-2*size[0], size[1]), 
            # Row 2
            (1-4*size[0], 0), 
            (1-3*size[0], 0), 
            (1-2*size[0], 0),
            # Row 3
            (1-4*size[0], 0-size[1]), 
            (1-3*size[0], 0-size[1]), 
            (1-2*size[0], 0-size[1])
            ]
    
        
        # Create images
        stimuli = []
        selected_imgs = selected_imgs
        for loc, img in zip(locs, imgs):
            stimulus = visual.ImageStim(self.win, image=img, pos=loc, size = size)
            stimuli.append(stimulus)
            if img in selected_imgs:
                stimulus.opacity = 0.5
        # Create title and instruction text
        texts = []
        title_stimulus = visual.TextStim(self.win, text=title_text, pos=(0, 0.95), color="grey", font="Arial", height=0.06)
        instruction_stimulus = visual.TextStim(self.win, text=instruction_text, pos=(-0.4 , 0.4), color="white", font="Arial", height=0.05, wrapWidth=1, alignText="left")
        texts.append(title_stimulus)
        texts.append(instruction_stimulus)
        reshuffle_btn = visual.Rect(self.win, width=0.65, height=0.15, pos=(-0.5, -0.6), lineColor='blue', fillColor=[0.5, 0.5, 0.5, 0.5])
        reshuffle_text = visual.TextStim(self.win, text="Auswahl speichern und andere Bilder neu mischen", font="Arial", height=0.05, pos=reshuffle_btn.pos, color="white")
        progress = visual.TextStim(self.win, text=f"Panel {completed_panels} von {panels}", pos=(0, -0.95), color="Blue", font="Arial", height=0.06)
        # Create continue text
        continue_stimulus = visual.TextStim(self.win, text=continue_text, pos=(-0.5, -0.3), color="blue", font="Arial", height=0.05, wrapWidth=0.7)

        
        
        while True:
            for stimulus in stimuli:
                stimulus.draw()
            for t in texts:
                t.draw()
            self.win.flip()
            reshuffle_btn.draw()
            reshuffle_text.draw()
            progress.draw()
            
            # Check if left mouse is pressed
            if mouse.getPressed()[0] == 1:
                for i, stimulus in enumerate(stimuli):
                    # Check which image was clicked
                    if mouse.isPressedIn(stimulus):
                        # Add image
                        if stimulus.image not in selected_imgs and len(selected_imgs) < required_imgs:
                            selected_imgs.append(stimulus.image)
                            stimuli[i].opacity = 0.5
                        elif stimulus.image in selected_imgs:
                            # Remove image
                            selected_imgs.remove(stimulus.image)
                            stimuli[i].opacity = 1
                        else:
                            continue  
                    if mouse.isPressedIn(reshuffle_btn):
                        
                        return selected_imgs
                
                # Prevent multiple clicks registered
                while True:
                    if mouse.getPressed()[0] == 0:
                        break

            # Wait until n imgs are selected
            allow_continue = False
            if len(selected_imgs) == required_imgs:
                texts.append(continue_stimulus)
                allow_continue = True
            elif continue_stimulus in texts:
                texts.remove(continue_stimulus)
            
            # Check if space is pressed
            if allow_continue:
                if event.getKeys(keyList=["space"]):
                    break
            
            # Clear events and flip window
            event.clearEvents()
        return selected_imgs
    
    def select_images(self, text: dict, category: str):
        self.win.flip()
        # Validate
        if category not in ["alcoholic", "non_alcoholic"]:
            raise ValueError("category must be either alcoholic or non_alcoholic")

        # Initialize category dict
        self.data[category] = {}

        # The previous window minimization logic can be placed here if needed
        self.maximize_window()

        # Window initialization

        # Determine the path to the script's directory
        script_directory = os.path.dirname(os.path.abspath(__file__))
        parent_directory = os.path.dirname(script_directory)
        
        # Define the relative path to the images folder
        image_folder_name = "Selection"
        image_path = os.path.join(parent_directory, "images", image_folder_name)

        # Positions and items dict
        positions = {
                    'Sparkling': [-0.6, 0],
                    'Non-Sparkling': [0, 0],
                    'Water': [0.6, 0],
                    'Beer': [-0.6, 0],
                    'Wine': [0, 0],
                    'Liquor': [0.6, 0]
                }
        # Randomize order for new iteration
        shuffled_names = list(positions.keys())
        random.shuffle(shuffled_names)
        shuffled_positions = {name: positions[name] for name in shuffled_names}

        # Drink descriptions (You can modify this accordingly)
        drink_descriptions = {
            'Sparkling':"Kohlensäure haltige Soft-Drinks (z. B. Cola, Fanta, Sprite, deren Alternativen, sprudelnde Eistees und Limonaden)",
            'Non-Sparkling': 'Nicht kohlensäurige haltige Getränke (z. B. Kaffee, Tee, Tee-Mixgetränke, Frucht- und Gemüsesäfte, Milch und heiße Schokolade).',
            'Water': 'Wasser aller Arten; sprudelnd, still oder aromatisiert',
            'Beer': 'Bier aus Gläsern, Flaschen oder Dosen unterschiedlicher Marken.',
            'Wine': 'Rotwein, Weißwein, Rose Wein, Sekt, Wein-Mischgetränke.',
            'Liquor': 'Vodka, Rum, Whiskey, Brandy, Gin, Liköre.'
        }

        items = {
                    name: {
                        'stim': visual.ImageStim(
                            self.win,
                            image=os.path.join(image_path, f"{name.lower().replace('-', '_')}.png"),
                            pos=position,
                            size=(0.35, 0.60)   # Reduce the size to maintain proportion
                        ),
                         'order': None,
                            'text': drink_descriptions[name],
                            'selected': False  # Add an attribute to check if an item has been selected
                    }
                    for name, position in shuffled_positions.items() if (category == "alcoholic" and name in ["Beer", "Wine", "Liquor"]) or (category == "non_alcoholic" and name in ["Sparkling", "Non-Sparkling", "Water"])
                }

        orders = ['1', '2', '3']
        mouse = event.Mouse(win= self.win)
        clicked_items = []
        if category == "alcoholic":
            instruction_text = ("Bitte ordnen Sie die drei Arten von alkoholischen Getränken nach der Häufigkeit (1 ist am häufigsten), mit der Sie sie im letzten Jahr konsumiert haben.\n"
                                "\n- Ein Klick auf das Bild vergibt eine Platzierung (1 bis 3)."
                                "\n- Ein klick auf ein bereits plaziertes Bild oder ein Klick auf 'Auswahl zurücksetzen' entfernt die Platzierung."
                                "\n- Ein Klick auf 'Auswahl bestätigen' speichert Ihre Auswahl."
                                "\n- Klicken sie auf ein Bild um zu beginnen.")
        else:
            instruction_text = ("Bitte ordnen Sie die drei gezeigten alkoholfreien Getränke nach Ihrer Vorliebe (1 ist die größte Vorliebe).\n"
                                "\n- Ein Klick auf das Bild vergibt eine Platzierung (1 bis 3)."
                                "\n- Ein klick auf ein bereits plaziertes Bild oder ein Klick auf 'Auswahl zurücksetzen' entfernt die Platzierung."
                                "\n- Ein Klick auf 'Auswahl bestätigen' speichert Ihre Auswahl."
                                "\n- Klicken sie auf ein Bild um zu beginnen.")
        instruction = visual.TextStim(self.win, text=instruction_text, font='Arial', pos=[0, 0.7], height=0.06, color='white', wrapWidth=1.6, alignText='left')

        while True:
            mouse_clicked = mouse.getPressed()[0]

            for item_name, item_data in items.items():
                if mouse_clicked and mouse.isPressedIn(item_data['stim']) and item_name not in clicked_items:
                    clicked_items.append(item_name)
                    item_data['selected'] = not item_data['selected']  # Toggle selection status
                    if item_data['order']:
                        orders.append(item_data['order'])
                        orders.sort()
                        item_data['order'] = None
                    else:
                        order_to_assign = orders[0]
                        item_data['order'] = order_to_assign
                        orders.remove(order_to_assign)

            if not mouse_clicked:
                clicked_items = []

            self.win.flip()
            
            for item_name, item_data in items.items():
                if item_data['selected']:
                    item_data['stim'].setOpacity(0.3)  # Halve the opacity if the item is selected
                else:
                    item_data['stim'].setOpacity(1.0)  # Reset opacity if the item is deselected
                item_data['stim'].draw()

            
            for item_name, item_data in items.items(): #text under the icons
                item_data['stim'].draw()
                text_stim = visual.TextStim(self.win, text=item_data['text'], font='Arial', pos=(item_data['stim'].pos[0], item_data['stim'].pos[1] - 0.4), height=0.05, color='white', wrapWidth=0.5)
                text_stim.draw()
                if item_data['order']:
                    order_stim = visual.TextStim(self.win, text=item_data['order'], font='Arial', pos=item_data['stim'].pos, height=0.5, color=(1, 1, 1, 0.9), wrapWidth=200)
                    order_stim.draw()

            instruction.draw()

            reset_button = visual.Rect(self.win, width=0.35, height=0.15, pos=[-0.25, -0.65], lineColor='red', fillColor=[1, 0, 0, 0.5])
            reset_button_text = visual.TextStim(self.win, text="Auswahl zurücksetzen", font='Arial', pos=[-0.25, -0.65], height=0.05, color='white')
            reset_button.draw()
            reset_button_text.draw()
            if mouse.isPressedIn(reset_button):
                for item_name, item_data in items.items():
                    if item_data['order']:
                        orders.append(item_data['order'])
                        item_data['order'] = None
                orders.sort()
            if all([item_data['order'] for item_name, item_data in items.items()]):
                confirm_button = visual.Rect(self.win, width=0.35, height=0.15, pos=[0.25, -0.65], lineColor='blue', fillColor=[0, 1, 0, 0.5])
                confirm = visual.TextStim(self.win, text="Auswahl bestätigen", pos=[0.25, -0.65], font='Arial', height=0.05, color='white')              
                confirm_button.draw()
                confirm.draw()
                
            else:
                confirm_button = visual.Rect(self.win, width=0.35, height=0.15, pos=[0.25, -0.65], lineColor='lightblue', fillColor=[0, 1, 0, 0.3])
                confirm = visual.TextStim(self.win, text="Auswahl bestätigen", pos=[0.25, -0.65], font='Arial', height=0.05, color='white')
                confirm_button.draw()
                confirm.draw()
                
            if mouse.isPressedIn(confirm_button) and all([item_data['order'] for item_name, item_data in items.items()]):
                
                # Construct the ordered selection manually
                temp_selection = {item_data['order']: item_name for item_name, item_data in items.items() if item_data['order']}
                
                selection = {
                    '1st': temp_selection.get('1'),
                    '2nd': temp_selection.get('2'),
                    '3rd': temp_selection.get('3')
                }

                print(selection)
                return selection



        
        
    def personalization(self, selection: dict, category: str, text: dict):
        panel_counts = [5, 3, 1]
        #self.data[category] = {}
        
        for panels, subcategory in zip(panel_counts, selection.values()):
            unseen_imgs = self.img_set_personalization.images[category][subcategory].copy()
            print(unseen_imgs)
            selected_images = []
            completed_panels = 0
            shuffle(unseen_imgs)

            while completed_panels < panels:  # Fill current_panel to have 9 images
                current_panel = [None] * 9
                proceed_with_current_panel = True
                liked_imgs = []
                while proceed_with_current_panel:
                    

                    # Check how many more images are needed
                    empty_slots = 9 - sum(1 for img in current_panel if img is not None)

                    # Fill the empty slots in current_panel
                    for idx in range(empty_slots):
                        if unseen_imgs:
                            current_panel[current_panel.index(None)] = unseen_imgs.pop(0)

                    # Get liked images from current set
                    liked_imgs = self.img_grid_selection(current_panel, text, selected_imgs= liked_imgs, completed_panels = completed_panels, panels = panels)
                    

                    # If 5 liked images aren't obtained, keep the liked ones for the next iteration and only replace the unliked ones.
                    if len(liked_imgs) < 5:
                        for idx in range(len(current_panel)):
                            # If an image in the current_panel is not liked, mark it as None to be replaced in the next iteration
                            if current_panel[idx] not in liked_imgs:
                                current_panel[idx] = None
                    else:
                        selected_images += liked_imgs[:5]
                        completed_panels += 1
                        proceed_with_current_panel = False

                    # Check if we need to refill unseen_imgs or move to the next panel
                    if not unseen_imgs or completed_panels == panels:
                        proceed_with_current_panel = False

                    # Refill unseen_imgs if exhausted, excluding currently selected ones.
                    if len(unseen_imgs) < 9 and completed_panels < panels:
                        unseen_imgs = [img for img in self.img_set_personalization.images[category][subcategory] if img not in (selected_images + current_panel)]
            
            self.data[category][f"{subcategory} Selection"] = {str(i+1): img for i, img in enumerate(selected_images)}
    
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
        
        self.initialize_window()
    
        # Instruction screen
        """
        self.instruction_screen()
        
        # Rate the scenarios
        
        self.pre_scenario()
        text = self.language["Presession"]["Scenario Rating"]
        self.rating_screen(text, "Scenario Rating")
        
        # Rate the consequences
        self.pre_consequence()
        text = self.language["Presession"]["Consequence Rating"]
        self.rating_screen(text, "Consequence Rating")
        """
        # Select non-alcoholic drinks
        self.pre_nonalc()
        text = self.language["Presession"]["Non-Alcoholic Selection"]
        selection = self.select_images(text = text, category="non_alcoholic")
        #self.explain_img_grid_selection()#Change image Paths! or remove when testing on the server
        self.personalization(selection = selection, category= "non_alcoholic", text=text)
        
        # Select alcoholic drinks
        self.pre_alc()
        text = self.language["Presession"]["Alcoholic Selection"]
        selection = selection = self.select_images(text = text, category="alcoholic")
        self.personalization(selection = selection, category="alcoholic", text=text) 
        
        #imagine Scenario
        self.imagine_scenario_screen()
        # Imagine Consequence
    
        # Json dump the data
        self.create_config()
        # End screen
        self.end_screen()
        self.wait_screen()
        