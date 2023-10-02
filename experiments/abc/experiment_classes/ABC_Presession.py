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

# Local modules
from classes.Presession import Presession
from experiments.abc.experiment_classes.ABC_Language import ABCLanguage
from experiments.abc.experiment_classes.ABC_StimulusSet import ABCStimulusSet, ABCStimulusSetA, ABCStimulusSetB, ABCStimulusSetPersonalization

#######################
# ABCPresession Class #
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
            if "escape" in keys:
                self.quit()
                raise KeyboardInterrupt
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
    
    #####
    #Change GUI!!!!
    #####
    def identify_participant(self):
        self.minimize_window() # minimze window before gui
        valid = False
        while not valid:
            gui_part_title = self.language["Presession"]["Gui Participant ID"]["Title"]
            gui_part_field1 = self.language["Presession"]["Gui Participant ID"]["Field1"]
            gui_part_field2 = self.language["Presession"]["Gui Participant ID"]["Field2"]
            gui_part_options2 = self.language["Presession"]["Gui Participant ID"]["Options2"]
            participant_info = {gui_part_field1: "",
                                gui_part_field2: gui_part_options2}
            gui.DlgFromDict(dictionary=participant_info, title=gui_part_title)
            if os.path.exists(f"{self.config_path}/{self.experiment_name}_presession_{participant_info[gui_part_field1]}.json"):
                gui_over_title = self.language["Presession"]["Gui Overwrite"]["Title"]
                gui_over_field1 = self.language["Presession"]["Gui Overwrite"]["Field1"]
                options1 = self.language["Presession"]["Gui Overwrite"]["Options1"]
                overwrite = {gui_over_field1: options1}
                gui.DlgFromDict(dictionary=overwrite, title=gui_over_title)
                if overwrite[gui_over_field1] == options1[0]:
                    os.remove(f"{self.config_path}/{self.experiment_name}_presession_{participant_info[gui_part_field1]}.json")
                    valid = True
            else:
                valid = True
        self.data["Participant ID"] = participant_info[gui_part_field1]
        self.data["Sex"] = participant_info[gui_part_field2]
        self.data["Condition"] = "" # Condition is determined at first session
        # Session info
        self.data["Current Session"] = 0
        self.maximize_window() # maximize window after gui

    """
    def identify_participant(self):
        self.minimize_window() # minimize window before gui
        valid = False
        while not valid:
            gui_part_title = self.language["Presession"]["Gui Participant ID"]["Title"]
            gui_part_field1 = self.language["Presession"]["Gui Participant ID"]["Field1"]
            gui_part_field2 = self.language["Presession"]["Gui Participant ID"]["Field2"]
            gui_part_options2 = self.language["Presession"]["Gui Participant ID"]["Options2"]
            participant_info = {gui_part_field1: "",
                                gui_part_field2: gui_part_options2}
            dlg = gui.DlgFromDict(dictionary=participant_info, title=gui_part_title)
            if dlg.OK:
                if len(participant_info[gui_part_field1]) == 6 and participant_info[gui_part_field1].isdigit():
                    if os.path.exists(f"{self.config_path}/{self.experiment_name}_presession_{participant_info[gui_part_field1]}.json"):
                        gui_over_title = self.language["Presession"]["Gui Overwrite"]["Title"]
                        gui_over_field1 = self.language["Presession"]["Gui Overwrite"]["Field1"]
                        options1 = self.language["Presession"]["Gui Overwrite"]["Options1"]
                        overwrite = {gui_over_field1: options1}
                        dlg = gui.DlgFromDict(dictionary=overwrite, title=gui_over_title)
                        if dlg.OK and overwrite[gui_over_field1] == options1[0]:
                            os.remove(f"{self.config_path}/{self.experiment_name}_presession_{participant_info[gui_part_field1]}.json")
                            valid = True
                    else:
                        valid = True
            else:
                break
        if valid:
            self.data["Participant ID"] = participant_info[gui_part_field1]
            self.data["Sex"] = participant_info[gui_part_field2]
            self.data["Condition"] = "" # Condition is determined at first session
            # Session info
            self.data["Current Session"] = 0
            self.maximize_window() # maximize window after gui
        
    
    def identify_participant(self):
        window = tk.Toplevel()
        window.geometry('1920x1080')
        window.configure(bg='black')
        window.attributes('-topmost', True)
        window.after_idle(window.attributes, '-topmost', False)

        def validate_and_save():
            participant_id = id_entry.get()
            gender = gender_combobox.get()

            if len(participant_id) == 6 and participant_id.isdigit():
                file_path = f"{self.config_path}/{self.experiment_name}_presession_{participant_id}.json"

                if os.path.exists(file_path):
                    overwrite_dlg = tk.Toplevel()
                    overwrite_dlg.attributes('-topmost', True)
                    overwrite_dlg.after_idle(overwrite_dlg.attributes, '-topmost', False)
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
                            self.data_update_and_destroy(participant_id, gender)
                        else:
                            overwrite_dlg.destroy()

                    overwrite_submit = tk.Button(overwrite_dlg, text="Submit", command=overwrite)
                    overwrite_submit.pack(pady=10)

                else:
                    window.destroy()
                    self.data_update_and_destroy(participant_id, gender)

            else:
                error_label = tk.Label(window, text="Invalid input, please enter a valid ID and gender", bg='black', fg='red')
                error_label.pack(pady=10)

        title_label = tk.Label(window, text=self.language["Presession"]["Gui Participant ID"]["Title"], bg='black', fg='white')
        title_label.pack(pady=10)

        id_label = tk.Label(window, text=self.language["Presession"]["Gui Participant ID"]["Field1"], bg='black', fg='white')
        id_label.pack(pady=10)

        id_entry = tk.Entry(window)
        id_entry.pack(pady=10)

        gender_label = tk.Label(window, text=self.language["Presession"]["Gui Participant ID"]["Field2"], bg='black', fg='white')
        gender_label.pack(pady=10)

        gender_combobox = ttk.Combobox(window, values=self.language["Presession"]["Gui Participant ID"]["Options2"])
        gender_combobox.pack(pady=10)

        submit_button = tk.Button(window, text="Submit", command=validate_and_save)
        submit_button.pack(pady=20)

        def close_window():
            window.destroy()

        window.bind('<Escape>', close_window)
        window.mainloop()
    """
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
        title = visual.TextStim(self.win, text=title_text, color="white", pos=(0, 0.95), font="Arial", height=0.05)
        continue_text = visual.TextStim(self.win, text=continue_text, color="white", pos=(0, -0.95), font="Arial", height=0.05)
        instruction = visual.TextStim(self.win, text=instruction_text, color="white", pos=(0, 0), font="Arial", height=0.05)
        title.draw()
        instruction.draw()
        continue_text.draw()
        self.win.flip()
        self.wait_keys()  
    
    def imagine_future_screen(self, 
                              imagine_screen_key: str = "Imagine Two Weeks Screen", 
                              imagine_rating_key: str = "Imagine Two Weeks Vividness") -> None:
        title_text = self.language["Presession"][imagine_screen_key]["Title"]
        instruction_text = self.language["Presession"][imagine_screen_key]["Text"]
        continue_text = self.language["Presession"][imagine_screen_key]["Continue"]
        slider_text = self.language["Presession"][imagine_screen_key]["Text 2"]
        slider_labels = self.language["Presession"][imagine_screen_key]["Labels"]
        title = visual.TextStim(self.win, text=title_text, color="white", pos=(0, 0.95), font="Arial", height=0.05)
        instruction = visual.TextStim(self.win, text=instruction_text, color="white", pos=(0, 0.5), font="Arial", height=0.05)
        slider_instruction = visual.TextStim(self.win, text=slider_text, color="white", pos=(0, -0.15), font="Arial", height=0.05)
        continue_text = visual.TextStim(self.win, text=continue_text, color="white", pos=(0, -0.95), font="Arial", height=0.05)
        slider = visual.Slider(self.win,
                                pos=(0, -0.5),
                                ticks=(0, 100),
                                labels=slider_labels,
                                labelHeight=0.05,
                                granularity=1,
                                style="rating",
                                size=(1, 0.05),
                                color="white",
                                flip=False)
        
        timer = core.Clock()
        
        while True:
            #Draw stimuli
            title.draw() 
            instruction.draw()
            slider_instruction.draw()
            slider.draw()
            continue_text.draw()
            self.win.flip()
            rating = slider.getRating()
            keys = event.getKeys()
            
            if "space" in keys and rating is not None:
                if timer > 5: #execution when timer is good #CHANGE BACK LATER
                    self.data["Imagination Ratings"][imagine_rating_key] = rating 
                    break
                else:
                    continue_text = "Please read the text carefully!" #Change to german
                    continue_stim = visual.TextStim(self.win, text=continue_text, color="red", pos=(0, -0.95), font="Arial", height=0.1)
                    instruction.draw()
                    continue_stim.draw()
                    self.win.flip()
                    core.wait(2)
            if "escape" in keys:
                self.quit()

    def imagine_scenario_screen(self) -> None:
        self.data["Imagination Ratings"] = {}
        # Rate Desire Pre Screen
        instruction_text = self.language["Presession"]["Rate Desire Pre Screen"]["Text"]
        continue_text = self.language["Presession"]["Rate Desire Pre Screen"]["Continue"]
        slider_labels = self.language["Presession"]["Rate Desire Pre Screen"]["Labels"]
        instruction = visual.TextStim(self.win, text=instruction_text, color="white", pos=(0, 0), font="Arial", height=0.05)
        continue_stim = visual.TextStim(self.win, text=continue_text, color="white", pos=(0, -0.95), font="Arial", height=0.05)
        slider = visual.Slider(self.win, 
                               pos=(0, -0.5), 
                               ticks=(0, 100), 
                               labels=slider_labels, 
                               labelHeight=0.05,
                               granularity=1, 
                               style="rating", 
                               size=(1, 0.05), 
                               color="white",
                               flip=False)
        
        timer = core.Clock() 
        
        while True:
            slider.draw()
            instruction.draw()
            continue_stim.draw()
            self.win.flip()
            rating = slider.getRating()
            keys = event.getKeys()
            if "space" in keys and rating is not None:
                if timer.getTime() > 5:
                    self.data["Imagination Ratings"]["Desire Pre"] = slider.getRating()
                    break
                else:
                    continue_text = "Please read the text carefully!" #Change to german
                    continue_stim = visual.TextStim(self.win, text=continue_text, color="red", pos=(0, -0.95), font="Arial", height=0.1)
                    instruction.draw()
                    continue_stim.draw()
                    self.win.flip()
                    core.wait(2)
            if "escape" in keys:
                self.quit()
        # Draw imagine instruction
        # get highest rated scenario
        scenarios = self.data["Scenario Rating"].copy()
        scenarios.pop("Custom Text")
        highest_key = sorted(scenarios.items(), key=lambda x: x[1], reverse=True)[0][0]
        if highest_key == "Custom":
            scenario_text = self.data["Scenario Rating"]["Custom Text"]
        else:
            scenario_text = self.language["Experiment"]["Imagine Scenario"]["Scenarios"][highest_key]
    
        title_text = self.language["Presession"]["Imagine Scenario Screen"]["Title"]
        instruction_text = scenario_text
        continue_text = self.language["Presession"]["Imagine Scenario Screen"]["Continue"]
        title = visual.TextStim(self.win, text=title_text, color="white", pos=(0, 0.95), font="Arial", height=0.05)
        instruction = visual.TextStim(self.win, text=instruction_text, color="white", pos=(0, 0), font="Arial", height=0.05)
        continue_text = visual.TextStim(self.win, text=continue_text, color="white", pos=(0, -0.95), font="Arial", height=0.05)
        title.draw()
        instruction.draw()
        continue_text.draw()
        self.win.flip()
        timer = core.Clock()
        while timer.getTime() < 5: #CHANGE BACK
            keys = event.getKeys()
            if "escape" in keys:
                self.quit()

        # Draw close eyes instruction
        instruction_text = self.language["Presession"]["Close Eyes Screen"]["Text"]
        continue_text = self.language["Presession"]["Close Eyes Screen"]["Continue"]
        continue_text = visual.TextStim(self.win, text=continue_text, color="white", pos=(0, -0.95), font="Arial", height=0.05)
        instruction = visual.TextStim(self.win, text=instruction_text, color="white", pos=(0, 0), font="Arial", height=0.05)
        instruction.draw()
        continue_text.draw()
        self.win.flip()
        timer = core.Clock()
        while timer.getTime() < 5: #CHANGE BACK
            keys = event.getKeys()
            if "escape" in keys:
                self.quit()

        # Rate Desire Post Screen
        text_1 = self.language["Presession"]["Rate Desire Post Screen"]["Text 1"]
        slider_labels_1 = self.language["Presession"]["Rate Desire Post Screen"]["Labels 1"]
        text_2 = self.language["Presession"]["Rate Desire Post Screen"]["Text 2"]
        slider_labels_2 = self.language["Presession"]["Rate Desire Post Screen"]["Labels 2"]
        continue_text = self.language["Presession"]["Rate Desire Post Screen"]["Continue"]
        
        instruction_1 = visual.TextStim(self.win, text=text_1, color="white", pos=(0, 0.85), font="Arial", height=0.05)
        instruction_2 = visual.TextStim(self.win, text=text_2, color="white", pos=(0, -0.15), font="Arial", height=0.05)
        continue_stim = visual.TextStim(self.win, text=continue_text, color="white", pos=(0, -0.95), font="Arial", height=0.05)
        slider_1 = visual.Slider(self.win, 
                               pos=(0, 0.5), 
                               ticks=(0, 100), 
                               labels=slider_labels_1, 
                               labelHeight=0.05,
                               granularity=1, 
                               style="rating", 
                               size=(1, 0.05), 
                               color="white", 
                               flip=False)
        slider_2 = visual.Slider(self.win, 
                               pos=(0, -0.5), 
                               ticks=(0, 100), 
                               labels=slider_labels_2, 
                               labelHeight=0.05,
                               granularity=1, 
                               style="rating", 
                               size=(1, 0.05), 
                               color="white", 
                               flip=False)
        
        timer = core.Clock()
        
        while True:
            slider_1.draw()
            slider_2.draw()
            instruction_1.draw()
            instruction_2.draw()
            continue_stim.draw()
            self.win.flip()
            rating_1 = slider_1.getRating()
            rating_2 = slider_2.getRating()
            keys = event.getKeys()
            if "space" in keys and rating_1 is not None and rating_2 is not None:
                if timer.getTime() > 5:
                    self.data["Imagination Ratings"]["Imagination Vividness"] = slider_1.getRating()
                    self.data["Imagination Ratings"]["Desire Post"] = slider_2.getRating()
                    break
                else:
                    continue_text = "Please read the text carefully!" #Change to german
                    continue_stim = visual.TextStim(self.win, text=continue_text, color="red", pos=(0, -0.95), font="Arial", height=0.1)
                    instruction.draw()
                    continue_stim.draw()
                    self.win.flip()
                    core.wait(2)
            if "escape" in keys:
                self.quit()  
        
        # Imagine future screens
        self.imagine_future_screen(imagine_screen_key="Imagine Two Weeks Screen",
                                   imagine_rating_key="Imagine Two Weeks Vividness")
        self.imagine_future_screen(imagine_screen_key="Imagine One Month Screen",
                                   imagine_rating_key="Imagine One Month Vividness")
        self.imagine_future_screen(imagine_screen_key="Imagine Six Months Screen",
                                   imagine_rating_key="Imagine Six Months Vividness")
        self.imagine_future_screen(imagine_screen_key="Imagine One Year Screen",
                                   imagine_rating_key="Imagine One Year Vividness")

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
        end = visual.TextStim(self.win, text=end_text, color="white", pos=(0, 0), font="Arial", height=0.05)
        continue_text = visual.TextStim(self.win, text=continue_text, color="white", pos=(0, -0.95), font="Arial", height=0.05)
        end.draw()
        continue_text.draw()
        self.win.flip()
        timer = core.Clock()
        while timer.getTime() < 5:
            continue
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
        title = visual.TextStim(self.win, text=title_text, color="white", pos=(0, 0.95), font="Arial", height=0.05)
        continue_text = visual.TextStim(self.win, text=continue_text, color="white", pos=(0, -0.9), font="Arial", height=0.05)
        # Create the slider
        slider = visual.Slider(self.win, 
                       pos=slider_pos, 
                       size=(1, 0.05), 
                       ticks=(range(0,11)), 
                       labels=slider_labels, 
                       labelHeight=0.05,
                       granularity=1, 
                       style="rating", 
                       color="white", 
                       flip=False)
        # Create a dictionary to store the ratings
        self.data[rating_name] = {}
        # Loop through the questions
        for question in questions:
            to_draw = []
            slider.reset()
            # Define question text
            if rate_images:
                question_text_stim = visual.TextStim(self.win, text=f"{instruction_text}", color="white", pos=question_pos, height=0.05, font="Arial")
                image = visual.ImageStim(self.win, image=f"{image_path}/{questions[question]}", pos=(0, 0))
                to_draw.append(image)
            else:
                if question == "Custom":
                        question_text = self.add_own_scenario_consequence(rating_dict)
                        self.data[rating_name]["Custom Text"] = question_text
                else:
                    question_text = questions[question]
                question_text_stim = visual.TextStim(self.win, text=f"{instruction_text} {question_text}", color="white", pos=question_pos, height=0.05, font="Arial")

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
                if "escape" in keys:
                    self.quit()
        
        self.win.flip()
        
    def add_own_scenario_consequence(self, rating_dict: dict):
        title_text = rating_dict["Title"]
        instruction_text = rating_dict["Instruction Custom"]
        continue_text = rating_dict["Continue Custom"]
        title = visual.TextStim(self.win, text=title_text, color="white", pos=(0, 0.95), font="Arial", height=0.05)
        instruction = visual.TextStim(self.win, text=instruction_text, color="white", pos=(0, 0.7), font="Arial", height=0.05)
        text_box = visual.TextBox2(self.win, text="", color="white", pos=(0, 0.5), font="Arial", letterHeight=0.05, editable=True, borderColor="white", borderWidth=10, anchor="top")
        continue_ = visual.TextStim(self.win, text=continue_text, color="white", pos=(0, -0.9), font="Arial", height=0.05)
        to_draw = [title, instruction, text_box, continue_]
        while True:
            for item in to_draw:
                item.draw()
            text_box.draw()
            if len(text_box.text) > 150:
                warning_text = visual.TextStim(self.win, text="Maximum character limit reached (150)", color="red", pos=(0, 0.3), font="Arial", height=0.05)
                warning_text.draw()
            self.win.flip()
            if "escape" in event.getKeys():
                if len(text_box.text) > 150:
                    continue
                else:
                    return text_box.text
                
    def img_grid_selection(self, imgs: list, text_dict: dict, required_imgs: int = 5):
        """Creates an interactive grid selection screen to select images"""
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
        shuffle(imgs)

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
        for loc, img in zip(locs, imgs):
            stimulus = visual.ImageStim(self.win, image=img, pos=loc, size = size)
            stimuli.append(stimulus)
        
        # Create title and instruction text
        texts = []
        title_stimulus = visual.TextStim(self.win, text=title_text, pos=(0, 0.95), color="white", font="Arial", height=0.05)
        instruction_stimulus = visual.TextStim(self.win, text=instruction_text, pos=(-0.5, 0.5), color="white", font="Arial", height=0.05, wrapWidth=0.7)
        texts.append(title_stimulus)
        texts.append(instruction_stimulus)

        # Create continue text
        continue_stimulus = visual.TextStim(self.win, text=continue_text, pos=(-0.5, 0.2), color="white", font="Arial", height=0.05, wrapWidth=0.7)

        selected_imgs = []
        while True:
            for stimulus in stimuli:
                stimulus.draw()
            for t in texts:
                t.draw()
            self.win.flip()
        
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
        """Runs through the image selection procedure."""
        # Validate
        if category not in ["alcoholic", "non_alcoholic"]:
            raise ValueError("category must be either alcoholic or non_alcoholic") # must correspond to folder name
        # Initialize category dict
        self.data[category] = {}

        # Minimize window before gui
        self.minimize_window()

        # Rate subcategories
        gui_part_title = text["Gui Title"]
        gui_part_field1 = text["Gui Field1"]
        gui_part_field2 = text["Gui Field2"]
        gui_part_field3 = text["Gui Field3"]
        gui_part_options = [""] + text["Gui Options"]
        
        while True:
            selection = {gui_part_field1: gui_part_options,
                    gui_part_field2: gui_part_options,
                    gui_part_field3: gui_part_options}
            gui.DlgFromDict(dictionary=selection, title=gui_part_title)
            if "" in selection.values() or len(set(selection.values())) < 3:
                continue
            else:
                break
        
        # Maximize window after gui
        self.maximize_window()
        # Load image paths according to rating 
        n_panels = [5, 3, 1]
        for n, subcategory in zip(n_panels, selection.values()):
            subcategory_imgs = [img for img in self.img_set_personalization.images[category][subcategory]] 
            shuffle(subcategory_imgs)
            subcategory_imgs = subcategory_imgs[0:n*9]
            selected_images = []
            for i in range(0, n):
                current_imgs = subcategory_imgs[i*9:(i+1)*9]
                selected_images += self.img_grid_selection(current_imgs, text)          
            self.data[category][f"{subcategory} Selection"] = {str(i+1): img for i, img in enumerate(selected_images)}
            self.win.flip()

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
        # Initialize window
        self.initialize_window()
        # Identify the participant
        self.identify_participant()
        # Instruction screen
        self.instruction_screen()
        self.wait_screen()
        # Rate the scenarios
        text = self.language["Presession"]["Scenario Rating"]
        self.rating_screen(text, "Scenario Rating")
        self.wait_screen()
        # Rate the consequences
        text = self.language["Presession"]["Consequence Rating"]
        self.rating_screen(text, "Consequence Rating")
        self.wait_screen()
        
        # Select non-alcoholic drinks

        #text = self.language["Presession"]["Non-Alcoholic Selection"]
        self.select_images(text=text, category="non_alcoholic")
        self.wait_screen()
        
        # Select alcoholic drinks
        
        #text = self.language["Presession"]["Alcoholic Selection"]
        self.select_images(text=text, category="alcoholic")
        self.wait_screen()
        
        # imagine Scenario
        self.imagine_scenario_screen()
        self.wait_screen()
        # Imagine Consequence
        self.imagine_consequence_screen() #@Ting is this what you wanted to have removed?
        self.wait_screen()
        # Json dump the data
        self.create_config()
        # End screen
        self.end_screen()
        self.wait_screen()
        