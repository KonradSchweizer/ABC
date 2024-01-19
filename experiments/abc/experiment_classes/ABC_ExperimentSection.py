# Programmer: Luke Korthals, https://github.com/lukekorthals

# The ABCExperimentSection classes build upon the ExperimentSection class.
# These sections are used throughout the experiment. 
# ScenarioSection and InstructionSection classes display text on the window. 
# TrialSection classes contain the main trial loop including the joystic interaction and 
# displaying feedback.

###########
# Imports #                                                                                            #
###########
# Standard libraries
from math import ceil
from numpy import random
from psychopy import visual, core, event, data
import time
from typing import List, Dict
import os
import json
import pygame.mixer


# Local modules
from classes.ExperimentSection import ExperimentSection
from experiments.abc.experiment_classes.ABCFeedback import ABCFeedback
from experiments.abc.experiment_classes.ABC_Settings import settings, txt_height, txt_color, win_color

########################
# Text Section Classes #                                                                                 #
########################
class ScenarioSection(ExperimentSection):
    """Section to display a scenario or placebo screen to the participant."""
    def __init__(self,
                 name: str,
                 enabled: bool = True,
                 title_txt: str = "", # Text displayed at the top of the window
                 continue_txt: str = "", # Instruction to continue to the next section, displayed at the bottom of the window
                 scenario_txt: str = "",# Text explaining the scenario, displayed at the center of the window
                 ID: str = "", # ID
                 delay: float = 120,
                 inbetween_sections: Dict[int, List[ExperimentSection]] = {},# Delay until the next section is run
                 space_skip: bool = False) -> None: # Allows to continue to the next section by pressing space
        super().__init__(name, "SCENARIO", enabled)
        self.title_txt = title_txt
        self.continue_txt = continue_txt
        self.scenario_txt = scenario_txt
        self.delay = delay
        self.space_skip = space_skip
        self.inbetween_sections = inbetween_sections
        self.ID = ID


    def validate_attributes(self):
        """Validates that all required attributes of the ExperimentSection object are set."""
        if not isinstance(self.title_txt, str):
            raise ValueError("title_txt must be a string.")
        if len (self.title_txt) == 0:
            raise ValueError("title_txt must not be empty.")
        if not isinstance(self.continue_txt, str):
            raise ValueError("continue_txt must be a string.")
        if len (self.continue_txt) == 0:
            raise ValueError("continue_txt must not be empty.")
        if not isinstance(self.scenario_txt, str):
            raise ValueError("scenario_txt must be a string.")
        if len (self.scenario_txt) == 0:
            raise ValueError("scenario_txt must not be empty.")
        if not isinstance(self.delay, (int, float)):
            raise ValueError("delay must be a number.")
        
    def get_json_data(self, ID):
        # Get the current directory of the script
        current_directory = os.path.dirname(os.path.abspath(__file__))

        # Navigate two directories up to get the equivalent of 'abc-psychopy-mainV2'
        base_directory = os.path.dirname(os.path.dirname(current_directory))

        # Use the provided relative path
        rel_path = r"abc\settings\participant_configs"
        filename = f"ABC_presession_{ID}.json"
        full_path = os.path.join(base_directory, rel_path, ID, filename)

        # Check if the file exists
        if not os.path.exists(full_path):
            print(f"File {filename} does not exist!")
            return None

        # If the file exists, read its content
        with open(full_path, 'r') as file:
            data = json.load(file)
        
        return data
        
    def save_to_json(self, ID, value):
        # Get the current directory of the script
        current_directory = os.path.dirname(os.path.abspath(__file__))
        
        
        # Navigate two directories up to get the equivalent of 'abc-psychopy-mainV2'
        base_directory = os.path.dirname(os.path.dirname(current_directory))
        

        # Use the provided relative path
        rel_path = r"abc\settings\participant_configs"
        filename = f"ABC_presession_{ID}.json"
        full_path = os.path.join(base_directory, rel_path, ID, filename)
        

        # Check if the file exists
        if not os.path.exists(full_path):
            print(f"File {filename} does not exist!")
            return

        # If the file exists, read its content
        with open(full_path, 'r') as file:
            presession = json.load(file)
        session = presession["Current Session"]
        session=str(session)
        # Modify the content
        presession["Training_Vividness"][session] = value

        # Write the updated content back to the file
        with open(full_path, 'w') as file:
            json.dump(presession, file, indent=4)

        print(f"Updated {filename} with value: {value}")
    
    def vividness_rating(self):
        if self.name == "ImagineScenario1_1":
            self.win.flip()
            instruction_text = (
            "Bitte bewerten Sie, wie lebhaft sich Ihre Vorstellung gerade auf einer auf der folgenden Skala: (Gar nicht lebhaft ~ äußerst lebhaft) angefühlt hat. \n\n"
        )
            continue_text = "Drücken Sie die Leertaste um fortzufahren."
            slider_labels = ["gar nicht lebhaft"] + [""] * 9 + ["äußerst lebhaft"]  # for a slider with 11 points

            question = visual.TextStim(self.win, text=instruction_text, color="lightgrey", pos=(0, 0.4), font="Arial", height=0.06, wrapWidth=1.8)
            continue_instr = visual.TextStim(self.win, text=continue_text, color="blue", pos=(0, -0.9), font= "Arial", height=0.06)

            # Create the slider
            slider = visual.Slider(self.win, 
                        pos=(0, -0.2), 
                        size=(1, 0.05), 
                        ticks=(range(0,11)), 
                        labels=slider_labels, 
                        labelHeight=0.05,
                        granularity=1, 
                        style="rating", 
                        color="white", 
                        flip=False,
                        font="Arial")

            # Draw and display all elements
            selection_made = False
            while not selection_made:  # Continue until a selection is made
                question.draw()
                continue_instr.draw()
                slider.draw()
                self.win.flip()
                if event.getKeys(keyList=["space"]):
                    if slider.getRating() is not None:
                        selection_made = True
            value = slider.getRating()
            self.save_to_json(self.ID, value)
           
        else:
            print("Nothing to see here")
    
    def audioImagination(self):
        data = self.get_json_data(ID = self.ID)
        
        condition = data["Condition"]
        session = str(data["Current Session"])
        
        #consequence = str(data["Consequence"][session][0])
        scenario = self.scenario_txt
        
        if condition == "4":
            instruction = visual.TextStim(self.win, text="Bitte setzen Sie ihre Kopfhörer auf und drücken Sie die Leerstaste wenn Sie eine bequeme position gefunden haben", color="white", pos=(0, 0), font="Arial", height=0.05)
            instruction.draw()
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
                audio = os.path.abspath(os.path.join(os.getcwd(), "experiments", "abc", "audio", "Condition4.mp3"))
                pygame.mixer.music.load(audio)
                pygame.mixer.music.play()
                
                play = visual.ImageStim(self.win, image= os.path.abspath(os.path.join(os.getcwd(), "experiments", "abc", "audio", "PlayPause.png")) , pos= (-0.25, -0.4))
                Rewind = visual.ImageStim(self.win, image= os.path.abspath(os.path.join(os.getcwd(), "experiments", "abc", "audio", "Rewind.png")), pos = (0.25, -0.4))

                # Start the clock after starting the audio
                mouse = event.Mouse(win=self.win)
                paused = False

                # Setting two time points and corresponding messages
                time_point1 = 64
                time_point2 = 10000#136
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
                        Text.text = str(scenario)
                        paused = True
                        message1_displayed = True
                        message_displayed = True
                        core.wait(0.5)
                    elif message1_displayed and not message2_displayed and audio_elapsed_time > time_point2:
                        pygame.mixer.music.pause()
                        Text.text = "Discontinuated" #str(consequence)
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
            self.win.flip()
            Text.text = "Discontinued" #str(consequence)
            Text.draw()
            visual.TextStim(self.win, text = "Drücken Sie die Leertaste um fortzufahren", color = "white", pos = (0, -0.9), height = 0.05).draw()
            self.win.flip()
            event.waitKeys(keyList=['space'])
                
            
            
        if condition == "3":
            instruction = visual.TextStim(self.win, text="Bitte setzen Sie ihre Kopfhörer auf und drücken Sie die Leerstaste wenn Sie eine bequeme position gefunden haben", color="white", pos=(0, 0), font="Arial", height=0.05)
            instruction.draw()
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
                audio = os.path.abspath(os.path.join(os.getcwd(), "experiments", "abc", "audio", "Con3.mp3"))
                pygame.mixer.music.load(audio)
                pygame.mixer.music.play()
                
                play = visual.ImageStim(self.win, image= os.path.abspath(os.path.join(os.getcwd(), "experiments", "abc", "audio", "PlayPause.png")) , pos= (-0.25, -0.4))
                Rewind = visual.ImageStim(self.win, image= os.path.abspath(os.path.join(os.getcwd(), "experiments", "abc", "audio", "Rewind.png")), pos = (0.25, -0.4))

                # Start the clock after starting the audio
                mouse = event.Mouse(win=self.win)
                paused = False

                # Setting two time points and corresponding messages
                time_point1 = 63
                
                message1_displayed = False
                
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
                        Text.text = str(scenario)
                        paused = True
                        message1_displayed = True
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
        if condition == "1" or condition == "2":
            instruction = visual.TextStim(self.win, text="Bitte setzen Sie ihre Kopfhörer auf und drücken Sie die Leerstaste wenn Sie eine bequeme position gefunden haben", color="white", pos=(0, 0), font="Arial", height=0.05)
            instruction.draw()
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
                
                message1_displayed = False
                
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
                        message1_displayed = True
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
   
    def run_section(self) -> None:
        # Pass if the section is not enabled
        super().run_section() 
        # Display scenario text
        if self.name == "ImagineScenario1_1":######################################################################################################## change back to 1
            self.audioImagination()
        else: 
            visual.TextStim(self.win, text=self.title_txt, color=txt_color, pos=(0, 1-txt_height-0.1), font="Arial", height=txt_height, wrapWidth=1.8).draw()
            visual.TextStim(self.win, text=self.continue_txt, color=txt_color, pos=(0, txt_height-1+0.1), font="Arial", height=txt_height, wrapWidth=1.8).draw()
            visual.TextStim(self.win, text=self.scenario_txt, color=txt_color, pos=(0, 0), font="Arial", height=txt_height, wrapWidth=1.8).draw()
            self.win.flip()
            # Continue to next section
            timer = core.Clock()
            while timer.getTime() <= self.delay:
                keys = event.getKeys()
                if "space" in keys:
                    break
        self.vividness_rating()
        event.clearEvents()

class InstructionSection(ExperimentSection):
    """Section to display some instruction to the participants."""
    def __init__(self, 
                 name: str,  
                 enabled: bool = True,
                 instruction_text: str ="") -> None:
        super().__init__(name, "INSTRUCTION", enabled)
        self.instruction_text = instruction_text
    
    def validate_attributes(self):
        print("validate_attributes")
        """Validates that all required attributes of the ExperimentSection object are set."""
        if not isinstance(self.instruction_text, str):
            raise ValueError("instruction_text must be a string.")
        if len (self.instruction_text) == 0:
            raise ValueError("instruction_text must not be empty.")
        
    
    def explenation_slideshow(self):
        def draw_navigation_hints():
            hints = [
                ("Die linke Pfeiltaste drücken um zurück zu kommen", (-0.6, -0.85)),
                ("Die Rechte Pfeiltaste drücken um nach vorne zu kommen", (0.6, -0.85 ))
            ]
            for text, pos in hints:
                hint_stim = visual.TextStim(self.win, text=text, color="blue", pos=pos, height=0.05, wrapWidth=1.8)
                hint_stim.draw()
        # Pre-loading all images and text stimuli
        joystick_img_paths = {
            "fire": os.path.abspath(os.path.join(os.getcwd(), "experiments", "abc", "images", "Joystick_fire.png")),
            "neutral": os.path.abspath(os.path.join(os.getcwd(), "experiments", "abc", "images", "Neutral.png")),
            "pull": os.path.abspath(os.path.join(os.getcwd(), "experiments", "abc", "images", "Pull.png")),
            "push": os.path.abspath(os.path.join(os.getcwd(), "experiments", "abc", "images", "Push.png"))
        }
        joystick_imgs = {key: visual.ImageStim(self.win, image=path, pos=(0, 0)) for key, path in joystick_img_paths.items()}
        for img in joystick_imgs.values():
            img.size = [i/3 for i in img.size]

        box_img_path = os.path.abspath(os.path.join(os.getcwd(), "experiments", "abc", "images", "WhiteBox.png"))
        box = visual.ImageStim(self.win, image=box_img_path)
        box.size = box.size/2

        common_args = {
            "color": "white",
            "pos": (0, 0),
            "font": "Arial",
            "height": 0.07,
            "wrapWidth": 1.8
        }
        texts = [    "Dies ist eine kleine visuelle Präsentation der Aufgabe", 
                 "Wenn Sie einen schwarzen Bildschirm sehen, drücken Sie den Außlöser auf Ihrem Joystick",
                 "Als Nächstes sehen Sie ein Bild.",
                 "Ziehen Sie den Joystick zu sich heran, wenn das Bild nach rechts geneigt ist",
                 "Ziehen Sie den Joystick zu sich heran", 
                 "Drücken Sie den Joystick von sich weg, wenn das Bild nach links geneigt ist", 
                 "Drücken Sie den Joystick von sich weg",
                 "Lassen Sie uns etwas üben, indem Sie den Auslöser drücken!"]

        text_stimuli = [visual.TextStim(self.win, text=t, **common_args) for t in texts]
        ORIGINAL_ORI = box.ori

        # Define the slide sequence
        slides = [
            lambda: text_stimuli[0].draw(),
            lambda: text_stimuli[1].draw(),
            lambda: joystick_imgs["fire"].draw(),
            lambda: text_stimuli[2].draw(),
            lambda: box.draw(),
            lambda: text_stimuli[3].draw(),
            lambda: (setattr(box, "ori", ORIGINAL_ORI - 6), box.draw())[1],
            lambda: text_stimuli[4].draw(),
            lambda: joystick_imgs["neutral"].draw(),
            lambda: joystick_imgs["pull"].draw(),
            lambda: text_stimuli[5].draw(),
            lambda: (setattr(box, "ori", ORIGINAL_ORI), box.draw())[1],
            lambda: (setattr(box, "ori", box.ori + 6), box.draw())[1],
            lambda: text_stimuli[6].draw(),
            lambda: joystick_imgs["neutral"].draw(),
            lambda: joystick_imgs["push"].draw(),
            lambda: text_stimuli[7].draw()
        ]

        index = 0
        timer = core.Clock()

        while index < len(slides):
            # Draw slide
            slides[index]()
            draw_navigation_hints()

            # Check elapsed time
            if timer.getTime() >= 5:
                visual.TextStim(self.win, text="Drücken Sie die Leertaste um fortzufahren", color="blue", pos=(0, 0.9), font="Arial", height=0.06, wrapWidth=1.8).draw()

            self.win.flip()

            # Non-blocking check for user input
            keys = event.getKeys()
            if 'space' in keys:
                action = 'next'
            elif 'left' in keys:  # Assuming 'left' arrow for previous
                action = 'previous'
            elif 'right' in keys:  # Assuming 'right' arrow for next/skip
                action = 'next'
            else:
                action = None

            # Handle navigation based on action
            if action == 'next' or action == 'skip':
                index += 1
                timer.reset()
            elif action == 'previous':
                index = max(0, index - 1)
                timer.reset()

            # Short delay to prevent the loop from running too fast
            core.wait(0.1)
             
                
    def get_expectations(self):
        def get_value(self):
            """Get the expectations of the participant"""
            instruction_text = (
                "Bitte beschreiben Sie von 0 (gar nicht überzeugt) bis 10 (absolut überzeugt), wie sehr Sie davon überzeugt sind, dass das Anti-Alkohol-Training Ihnen dabei helfen wird, abstinent zu bleiben."
            )
            continue_text = "Bitte drücken Sie die LEERTASTE, um fortzufahren."
            slider_labels = ["gar nicht überzeugt"] + [""] * 9 + ["absolut überzeugt"]  # for a slider with 11 points

            question = visual.TextStim(self.win, text=instruction_text, color="white", pos=(0, 0.4), font="Arial", height=0.06, wrapWidth=1.8)
            continue_instr = visual.TextStim(self.win, text=continue_text, color="blue", pos=(0, -0.9), font="Arial", height=0.06)

            # Create the slider
            slider = visual.Slider(self.win,
                                pos=(0, -0.2),
                                size=(1, 0.05),
                                ticks=(range(0, 11)),
                                labels=slider_labels,
                                labelHeight=0.06,
                                granularity=1,
                                style="rating",
                                color="white",
                                flip=False,
                                font="Arial")

            # Draw and display all elements
            selection_made = False
            while not selection_made:  # Continue until a selection is made
                self.win.winHandle.activate()  # Bring the window to the foreground
                question.draw()
                continue_instr.draw()
                slider.draw()
                self.win.flip()
                if event.getKeys(keyList=["space"]):
                    if slider.getRating() is not None:
                        selection_made = True
            value = slider.getRating()
            return value
        
        def get_json_data(self, ID):
            # Get the current directory of the script
            current_directory = os.path.dirname(os.path.abspath(__file__))

            # Navigate two directories up to get the equivalent of 'abc-psychopy-mainV2'
            base_directory = os.path.dirname(os.path.dirname(current_directory))

            # Use the provided relative path
            rel_path = r"abc\settings\participant_configs"
            filename = f"ABC_presession_{ID}.json"
            full_path = os.path.join(base_directory, rel_path, ID, filename)

            # Check if the file exists
            if not os.path.exists(full_path):
                print(f"File {filename} does not exist!")
                return None

            # If the file exists, read its content
            with open(full_path, 'r') as file:
                data = json.load(file)
            
            return data
        
        def save_to_json(self, ID, value):
            # Get the current directory of the script
            current_directory = os.path.dirname(os.path.abspath(__file__))
            
            
            # Navigate two directories up to get the equivalent of 'abc-psychopy-mainV2'
            base_directory = os.path.dirname(os.path.dirname(current_directory))
            

            # Use the provided relative path
            rel_path = r"abc\settings\participant_configs"
            filename = f"ABC_presession_{ID}.json"
            full_path = os.path.join(base_directory, rel_path, ID, filename)
            

            # Check if the file exists
            if not os.path.exists(full_path):
                print(f"File {filename} does not exist!")
                return

            # If the file exists, read its content
            with open(full_path, 'r') as file:
                presession = json.load(file)
            session = presession["Current Session"]
            session=str(session)
            # Modify the content
            presession["Expectation"][session] = value

            # Write the updated content back to the file
            with open(full_path, 'w') as file:
                json.dump(presession, file, indent=4)

            print(f"Updated {filename} with value: {value}, in session {session})")
            print(get_json_data(self, ID = "123456"))


                # Once the space key is pressed, you can retrieve the value from the slider
        ID = self.dat["ID"] 
        value = get_value(self)       
        get_json_data(self, ID)
        save_to_json(self, ID, value)
        

    def run_section(self) -> None:
        print("run_section")
        if self.name == "EndInstruction": #EndInstruction
            self.get_expectations()
            
        # Pass if the section is not enabled
        super().run_section() 
        # Display instruction text
        self.win.color = win_color
        visual.TextStim(self.win, text=self.instruction_text, color=txt_color, pos=(0, 0), font="Arial", height=txt_height, wrapWidth=1.8, alignText="left").draw()
        visual.TextStim(self.win, text= "Bitte drücken Sie die LEERTASTE, um fortzufahren.", color="blue", pos=(0, -0.9), font="Arial", height=txt_height, wrapWidth=1.8, alignText="center").draw()
        self.win.flip()
        # Continue to next section
        event.waitKeys(keyList=['space'])
        event.clearEvents()
        self.win.flip()
        if self.name == "PracticeInstruction":
            self.explenation_slideshow()

#########################
# Trial Section Classes #                                                                                 #
#########################
class TrialSection(ExperimentSection): 
    """Section to run trials."""
    def __init__(self,
                 name: str, 
                 type: str, 
                 enabled: bool = True,
                 non_alc_images: List[str]=[], 
                 alc_images: List[str]=[], 
                 delays=[0], 
                 n_trials: int=40, 
                 feedbacks: List[ABCFeedback]=[], 
                 feedback_interval: int=1,  
                 inbetween_sections: Dict[int, List[ExperimentSection]] = {},
                 perc_congruent: float=0.5, 
                 perc_positive: float=0.5
                 ) -> None:
        super().__init__(name, type, enabled)
        self.non_alc_images = non_alc_images
        self.alc_images = alc_images
        self.perc_congruent = perc_congruent
        self.perc_positive = perc_positive
        self.n_trials = n_trials
        self.delays = delays
        self.give_feedback = False
        self.feedbacks = feedbacks
        self.feedback_interval = feedback_interval
        self.inbetween_sections = inbetween_sections
    
    def initialize_feedbacks(self) -> None:
        print("initialize_feedbacks")
        for feedback in self.feedbacks:
            feedback.add_win(self.win)

        
    def add_feedback(self, feedback: ABCFeedback, i: int = -1) -> None:
        print("add_feedback")
        self.feedbacks.insert(i, feedback)
    
    def append_output_file(self) -> None: # TRIALSECTION ONLY
        
        """Appends the output file according to the global variable output_file_name.

        Keyword arguments:
        dat -- dictionary containing the data to be written to the output file.
        """
        column_values = [str(value) for value in self.dat.values()]  # dict.values = column values
        with open(self.output_path, "a") as f:
            f.write("\t".join(column_values) + "\n")

    def create_trial_config(self):
            print("create_trial_config")
            # Create a list of all the trials in the experiment  
            pos_push = ["POS_PULL"] * ceil(self.n_trials * self.perc_positive * self.perc_congruent)
            neg_push = ["NEG_PUSH"] * ceil(self.n_trials * (1-self.perc_positive) * self.perc_congruent)
            pos_pull = ["POS_PUSH"] * ceil(self.n_trials * self.perc_positive * (1-self.perc_congruent))
            neg_pull = ["NEG_PULL"] * ceil(self.n_trials * (1-self.perc_positive) * (1-self.perc_congruent))
            all_trials = pos_push + neg_push + pos_pull + neg_pull
            if len(all_trials) > self.n_trials:
                all_trials = all_trials[:self.n_trials]
            # Remove path in front of image name
            self.non_alc_images = [image.split("/")[-1] for image in self.non_alc_images]
            self.alc_images = [image.split("/")[-1] for image in self.alc_images]
            # Copy images
            pos_images_copy = self.non_alc_images.copy()
            neg_images_copy = self.alc_images.copy()
            # Create trials
            trials = []
            for trial in all_trials:
                # Select a random delay from the delay list
                delay = random.choice(self.delays)
                # Extrct the prime type from the trial name
                primetype = trial.split("_")[0]
                # Extract the trial type from the trial name
                trialtype = trial.split("_")[1]
                # Determine rotation
                if trialtype == "PULL":
                    rotation = "RIGHT"
                else:
                    rotation = "LEFT"
                # Select random image
                if primetype == "POS":
                    prime = random.choice(self.non_alc_images)
                else:
                    prime = random.choice(self.alc_images)
                # Generate Code
                code = f"{self.type}_{delay}_{primetype}_{trialtype}_{rotation}"
                # Add the trial to the trial config file
                trials.append({
                    "code": code,
                    "delay": delay,
                    "trialtype": trialtype,
                    "prime": prime
                })
                # Refresh empty image lists
                if len(pos_images_copy) == 0:
                    pos_images_copy = self.non_alc_images.copy()
                if len(neg_images_copy) == 0:
                    neg_images_copy = self.alc_images.copy()
            # Randomize trials
            random.shuffle(trials)
            self.trials = trials 

    def initialize_section(self) -> None:
        #self.create_trial_config() # DEPRECATED
        self.trial_handler = data.TrialHandler(self.trials, 1, method="sequential")
        self.initialize_feedbacks()
    
    #-----------------------Picture Functions-----------------------#
    def rotate_pic(self, degrees: float, picture: visual.ImageStim):
        """Rotates the given picture by the given degrees in the direction of the given trial type.

        Keyword arguments:
        degrees -- the degrees to rotate the picture by
        picture -- the picture to rotate
        dat -- the data dictionary of the current trial
        """
        core.wait(self.dat["Delay"])
        if self.dat["TrialType"] == "PUSH":
            picture.ori -= degrees
        elif self.dat["TrialType"] == "PULL":
            picture.ori += degrees
        return picture

    def zoom_pic(self, picture: visual.ImageStim, base_size: List[float]):
        """Zooms and draws the picture according to the joystick y position."""
        joy_y = self.joy.getY()
        picture.size = [dimension * (1 + joy_y) for dimension in base_size]
        picture.draw()
    #-----------------------Joystick Functions-----------------------#
   
    def wait_for_click(self):
        timer = core.Clock()
        click = False
        button_was_pressed = True 
        while not click:
            self.win.flip()
            if self.joy.getY() < 0.095 and self.joy.getY() > -0.095:
                if not self.joy.getButton(0):
                    button_was_pressed = False
                elif not button_was_pressed:
                    self.win.color = win_color
                    self.win.flip()
                    click = True
                    break 
            if timer.getTime() > 5:
                if self.joy.getY() < 0.095 and self.joy.getY() > -0.095:
                    visual.TextStim(self.win, text="Joystick ist in einer neutrale Position.", color="green", pos=(0, 0.1), font="Arial", height=(txt_height*1.5), wrapWidth=1.8).draw()
                else:
                    visual.TextStim(self.win, text="Bitte bringen Sie den Joystick in eine neutrale Position.", color="White", pos=(0, 0.1), font="Arial", height=(txt_height*1.5), wrapWidth=1.8).draw()
                if self.joy.getButton(0):
                    visual.TextStim(self.win, text="Auslöser ist gedrückt.", color="green", pos=(0, -0.1), font="Arial", height=(txt_height*1.5), wrapWidth=1.8).draw()
                else:
                    visual.TextStim(self.win, text="Bitte drücken Sie auf den Auslöser.", color="White", pos=(0, -0.1), font="Arial", height=(txt_height*1.5), wrapWidth=1.8).draw()
   
    #-----------------------Data Functions-----------------------#
    def check_congruency(self):
        """Checks if the given trial is congruent or incongruent.

        Keyword arguments: 
        dat -- the data dictionary of the current trial
        """
        if "POS_PULL" in self.dat["Code"] or "NEG_PUSH" in self.dat["Code"]:
            return "congruent"
        else:
            return "incongruent"
    
    def check_trial(self):
        """Checks if the given trial is correct and changes the screen color accordingly.

        Keyword arguments:
        dat -- the data dictionary of the current trial
        """
        if self.give_feedback:
            # If the joystick is moved in the wrong direction, the screen turns red
            if ((self.dat["TrialType"] == "PUSH" and self.dat["Y_coordinate"] > 0.2) or
                (self.dat["TrialType"] == "PULL" and self.dat["Y_coordinate"] < -0.2)):
                if not self.only_progress:
                    self.win.color = "red"
            # If the joystick is moved in the right direction, the screen turns black
            if ((self.dat["TrialType"] == "PUSH" and self.dat["Y_coordinate"] < -0.2) or
                (self.dat["TrialType"] == "PULL" and self.dat["Y_coordinate"] > 0.2)):
                self.win.color = win_color

        # Checks if the trial is correct
        if (
            # always correct during practice
            #(self.dat["Studypart"] == "PRACTICE") or
            # PUSH trials are correct if the joystick is pushed down
            (self.dat["TrialType"] == 'PUSH' and self.dat["Y_coordinate"] < -0.8) or 
            # pull trials are correct if the joystick is pulled up
            (self.dat["TrialType"] == 'PULL' and self.dat["Y_coordinate"] > 0.8)
        ):
            if self.give_feedback and not self.only_progress:
                visual.TextStim(self.win, text= "Abstinenzmotiv:", color="white", pos=(0, 0.5), font="Arial", height=(txt_height*1.5), wrapWidth= 0.5 ).draw()
                visual.TextStim(self.win, text= self.dat['Consequence'], color="green", pos=(0, 0), font="Arial", height=(txt_height*1.5), wrapWidth= 0.5 ).draw()
                self.win.flip()
                core.wait(0.15)
            return 1  # correct   

        return 0  # incorrect

    def stage_pass(self, which_stage: str, clock: core.Clock, stage_increment=1):
        """Adds the given stage to the data dictionary and appends the data dictionary to the output file.

        Keyword arguments:
        which_stage -- the stage to add to the data dictionary
        clock -- the clock to get the RT from
        dat -- the data dictionary to add the stage to
        stage_increment -- the number to increment the stage number by
        """
        self.dat["RT"] = clock.getTime()
        self.dat["Stage_number"] =self. dat["Stage_number"] + stage_increment
        self.dat["Stage"] = which_stage
        self.dat["Y_coordinate"] = round(self.joy.getY(), 5)
        self.dat["RespCorrect"] = self.check_trial()
        self.append_output_file()

        
    def trial_loop(self, loop_threshhold: float, threshhold_greater: bool, picture: visual.ImageStim):
        """Runs the trial loop for the given trial.

        Keyword arguments:
        loop_threshhold -- the threshhold to loop the trial until
        threshhold_greater -- whether the threshhold is greater than or less than the joystick position
        dat -- the data dictionary of the current trial
        picture -- the picture to draw on the screen
        """
        self.dat["Stage_number"] = 0
        self.dat["CurrentTime"] = time.strftime("%Y-%m-%d/%H:%M:%S", time.localtime())

        # Threshholds
        pull1 = False
        pull2 = False
        pull3 = False
        pull4 = False
        push1 = False
        push2 = False
        push3 = False
        push4 = False
        baseline = False

        # Picture
        # # drawing the picture on the screen
        self.win.flip()  # redraw the buffer
        picture = self.rotate_pic(settings["Rotation Degrees"], picture)
        #picture.size = picture.size/1.5
        picture.draw() # delay is now inbuilt
        pic_size = picture.size
        

        # directly placing both drawing functions after each other will put both image objects after each other in each trial.

        # Start Joy Loop
        clock = core.Clock()
        # wait for space
        while ((threshhold_greater and self.joy.getY() < loop_threshhold) or  # pull condition
            (not threshhold_greater and self.joy.getY() > loop_threshhold)):  # push condition
            self.zoom_pic(picture, pic_size)
            # Baseline stage
            if self.joy.getY() > -0.1 and self.joy.getY() < 0.1 and baseline == False:
                baseline = True
                push1 = False
                pull1 = False
                self.stage_pass("baseline", clock)
                pull2 = False

            # pull stages here
            if self.joy.getY() > 0.1 and self.joy.getY() < 0.3 and pull1 == False:
                pull1 = True
                baseline = False
                self.stage_pass("pull1", clock)
            if self.joy.getY() > 0.3 and self.joy.getY() < 0.5 and pull2 == False:
                pull2 = True
                pull1 = False
                pull3 = False
                self.stage_pass("pull2", clock)
            if self.joy.getY() > 0.5 and self.joy.getY() < 0.7 and pull3 == False:
                pull3 = True
                pull2 = False
                pull4 = False
                self.stage_pass("pull3", clock)
            if self.joy.getY() > 0.7 and self.joy.getY() < 0.9 and pull4 == False:
                pull4 = True
                pull3 = False
                self.stage_pass("pull4", clock)

            # push stages here
            if self.joy.getY() < -0.1 and self.joy.getY() > -0.3 and push1 == False:
                push1 = True
                baseline = False
                self.stage_pass("push1", clock)
            if self.joy.getY() < -0.3 and self.joy.getY() > -0.5 and push2 == False:
                push2 = True
                push1 = False
                push3 = False
                self.stage_pass("push2", clock)
            if self.joy.getY() < -0.5 and self.joy.getY() > -0.7 and push3 == False:
                push3 = True
                push2 = False
                push4 = False
                self.stage_pass("push3", clock)
            if self.joy.getY() < -0.7 and self.joy.getY() > -0.9 and push4 == False:
                push4 = True
                push3 = False
                self.stage_pass("push4", clock)
            elif event.getKeys(['escape']):
                core.quit()

            event.clearEvents()  # do this each frame to avoid a backlog of mouse events
            picture.draw()
            self.win.flip()  # redraw the buffer
            
            if event.getKeys(['escape']):
                core.quit()
        self.stage_pass("stage_final", clock, stage_increment=0)  # stage increment 0
        
    def load_stimulus(self, trial):
        """Loads the current Image. This is overwritten in the PracticeSection class."""
        stimulus = visual.ImageStim(self.win, image=trial["prime"], interpolate=True)
        original_pic_size = stimulus.size
        stimulus.size = [dimension / 1.4 for dimension in original_pic_size]
        return stimulus
    
    def run_section(self):
        super().run_section() # passes if not enabled
        # Add attributes to inbetweensections
        attributes = {
            "win": self.win,
            "joy": self.joy,
            "dat": self.dat,
            "output_path": self.output_path
        }
        for key in self.inbetween_sections:
            for section in self.inbetween_sections[key]:
                section.set_attributes(attributes)

                
                
        # Run inbetween section before first trial
        if 0 in self.inbetween_sections.keys():
                for section in self.inbetween_sections[0]: 
                    print(f"Running inbetween section {section.name}")
                    section.run_section()

        # Go through all trials
        feedback_counter = 0
        for trial_counter, trial in enumerate(self.trial_handler):
            # Counters
            trial_counter += 1
            feedback_counter += 1

            # Run inbetween sections
            if trial_counter in self.inbetween_sections.keys():
                for section in self.inbetween_sections[trial_counter]: 
                    print(f"Running inbetween section {section.name}")
                    section.run_section()

            # Update Dat
            self.dat["Trialnumber"] = self.dat["Trialnumber"] + 1  # check if correct
            self.dat["Delay"] = trial["delay"]
            self.dat["Code"] = trial["code"]
            self.dat["TrialType"] = trial["trialtype"]
            self.dat["Picture"] = trial["prime"]
            self.dat["Congruency"] = self.check_congruency()
            self.dat["Studypart"] = self.type

            # Show Picture
            stimulus = self.load_stimulus(trial)
            self.wait_for_click()

            # Run Trial
            if self.dat["TrialType"] == "PUSH":
                self.trial_loop(-0.95, False, stimulus)  # -1 = push loop
            elif self.dat["TrialType"] == "PULL":
                self.trial_loop(0.95, True, stimulus)  # 1 = pull loop
            
            # Give feedback
            if self.give_feedback:
                if self.dat["Congruency"] == "congruent":
                    for feedback in self.feedbacks:
                        feedback.correct += 1
                elif self.dat["TrialType"] == "PULL" and self.dat["Congruency"] == "incongruent":
                    for feedback in self.feedbacks:
                        feedback.incorrect += 1
                else: 
                    pass
                if feedback_counter == self.feedback_interval:
                    for feedback in self.feedbacks:
                        feedback.present_feedback()
                        feedback.reset_correct_incorrect()
                    feedback_counter = 0

class PracticeSection(TrialSection):
    def __init__(self, 
                 name: str, 
                 enabled: bool = True,
                 pos_images: List[str]=[], 
                 neg_images: List[str]=[], 
                 feedbacks: List[ABCFeedback]=[], 
                 n_trials: int=2, 
                 feedback_interval: int=1, 
                 inbetween_sections: Dict[int, List[ExperimentSection]] = {},
                 delays: List[int]=[0]
                 ):
        super().__init__(name, "PRACTICE", enabled, pos_images, neg_images, delays, n_trials, feedbacks, feedback_interval, inbetween_sections)
        # Standard settings for the practice section
        self.perc_congruent = 1
        self.perc_positive = 0.5
        self.give_feedback = False
        self.only_progress = False
        
       
    def load_stimulus(self, trial):
        """Instead of loading an image, displays a white rectangle."""     
        stimulus = visual.ImageStim(self.win, image=trial["prime"])
        stimulus = visual.Rect(self.win, width=stimulus.width, height=stimulus.height, fillColor="white", lineColor="black")
        stimulus.size = stimulus.size/1.4
        return stimulus

class AssessmentSection(TrialSection):
    def __init__(self, 
                 name: str, 
                 enabled: bool = True, 
                 pos_images: List[str]=[], 
                 neg_images: List[str]=[], 
                 feedbacks: List[ABCFeedback]=[], 
                 n_trials: int=40, 
                 feedback_interval: int=1, 
                 inbetween_sections: Dict[int, List[ExperimentSection]] = {},
                 delays: List[int]=[0]):
        super().__init__(name, "ASSESSMENT", enabled, pos_images, neg_images, delays, n_trials, feedbacks, feedback_interval, inbetween_sections)
        # Standard settings for the assessment section
        self.perc_congruent = 0.5
        self.perc_positive = 0.5
        self.give_feedback = False
        self.only_progress = False

class TrainingSection(TrialSection):
   def __init__(self, name: str, 
                enabled: bool = True,
                pos_images: List[str]=[], 
                neg_images: List[str]=[], 
                feedbacks: List[ABCFeedback]=[], 
                n_trials: int=100, 
                feedback_interval: int=5,
                inbetween_sections: Dict[int, List[ExperimentSection]] = {}, 
                delays: List[int]=[0]):
        super().__init__(name, "TRAINING", enabled, pos_images, neg_images, delays, n_trials, feedbacks, feedback_interval, inbetween_sections)
          # Standard settings for the training section
        self.perc_congruent = 1
        self.perc_positive = 0.5
        self.give_feedback = False
        self.only_progress = False
        print(self.only_progress, "self.only_progress")

