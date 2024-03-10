
# Programmer: Luke Korthals, https://github.com/lukekorthals

# The ABCExperiment class is build upon the Experiment class.
# It defines the structure of the ABC Experiment and all required settings.
# ScenarioSection and InstructionSection classes display text on the window. 
# The experiment is run by initializing an ABCExperiment object and 
# executing prepare_experiment() and run_experiment() on it.

###########
# Imports #
###########
# Standard libraries
from datetime import datetime
import json
import random
from psychopy import gui, visual, event
from random import shuffle
from typing import Dict, List
import tkinter as tk
from tkinter import ttk


# Local modules
from classes.Experiment import Experiment
from experiments.abc.experiment_classes.ABC_ExperimentSection import ScenarioSection, InstructionSection, PracticeSection, AssessmentSection, TrainingSection
from experiments.abc.experiment_classes.ABCFeedback import MeterFeedback
from experiments.abc.experiment_classes.ABC_Language import ABCLanguage
from experiments.abc.experiment_classes.ABC_Settings import *
from experiments.abc.experiment_classes.ABC_StimulusSet import ABCStimulusSet, ABCStimulusSetA, ABCStimulusSetB, ABCStimulusSetPersonalization , ABCStimulusSetStandard


#######################
# ABCExperiment Class # 
#######################
class ABCExperiment(Experiment):
    def __init__(self, 
                language = ABCLanguage(),
                config_path = "experiments/abc/settings/participant_configs",
                output_path = "experiments/abc/output",
                experiment_prefix = "ABC",
                settings = ABCSettings(),
                img_set_a: ABCStimulusSet = ABCStimulusSetA(),
                img_set_b: ABCStimulusSet = ABCStimulusSetB(),
                img_set_standard: ABCStimulusSet = ABCStimulusSetStandard()):
        self.settings = settings.settings.copy()
        self.settings_path = settings.settings_path
        self.img_set_a = img_set_a
        self.img_set_b = img_set_b
        self.img_set_standard = img_set_standard
        joy_backend = self.settings["Joystick Backend"]
        win_resolution = self.settings["Window Size"]
        win_color = self.settings["Window Color"]
        self.scenario_attributes = None
        super().__init__(language, config_path, output_path, experiment_prefix, joy_backend, win_resolution, win_color)
    
    # Methods to initialize the experiment
    def set_data(self) -> None:
        """Creates the data file in which each training trial will be put"""
        self.data = { 
                    "ID": None,
                    "Condition": None,
                    "Condition_saved": None,
                    "Scenario": None,
                    "CurrentTime": None,
                    "Studypart": None,
                    "Code": None,
                    "TrialType": None,
                    "Delay": None,
                    "Picture": None,
                    "Trialnumber": 0,
                    "RT": None, 
                    "Stage_number": None,
                    "Stage": None,
                    "Y_coordinate": None,
                    "RespCorrect": None,
                    "Congruency": None
                    }

    def set_sections(self) -> None:
        print("set_sections")
        # Assessment Sections (Congruent = 50%, Non-Alcoholic = 50%)
        assessment_trials = 120
        assessment_feedback_start_perc = 0.5 # Start the meter at 50%
        assessment_feedback_interval = 1 # Feedback after every trial
        assessment_feedback_increment = 1 / assessment_trials # Feedback can go up and down because of incongruent trials, divided by 2 because there are 2 assessment sections
        """CHANGE TRAINING FEEDBACK INTERVAL and INCREMENT ACCORDING TO REINAUTS PLANS!!"""
        # Training Sections (Congruent = 100%, Non-Alcoholic = 50%)
        training_trials = 240 # There are four training sections with this number of trials each
        training_feedback_interval = 10 # Feedback after every 10 trials 
        training_feedback_increment = 1 / training_trials  # Feedback can only go up because only congruent trials, divived by 4 because there are 4 training sections
        
        # Add sections to experiment
        self.sections.extend([
            # Welcome
            InstructionSection(name="WelcomeInstruction", 
                               instruction_text=self.language["Experiment"]["Instructions"]["Welcome Instruction"]),
            # Practice
            PracticeSection(name="Practice", 
                            feedback_interval=1,
                            inbetween_sections={
                                0: [InstructionSection(name="PracticeInstruction", instruction_text=self.language["Experiment"]["Instructions"]["Practice Instruction"])]
                                }),
            # Assessment
            AssessmentSection(name="Assessment",
                              feedback_interval=assessment_feedback_interval, 
                              feedbacks=[MeterFeedback(perc=assessment_feedback_start_perc, increment=assessment_feedback_increment)],
                              # Break after 60 trials
                              inbetween_sections={
                                  0: [InstructionSection(name="AssessmentInstruction", instruction_text=self.language["Experiment"]["Instructions"]["Trial Instruction"])],
                                  60: [InstructionSection(name="AssessmentBreakInstruction",instruction_text=self.language["Experiment"]["Instructions"]["Break Instruction"])]
                                  }),
            # Training
            TrainingSection(name="Training", 
                            feedback_interval=training_feedback_interval, 
                            feedbacks=[MeterFeedback(perc=0, increment=training_feedback_increment)],
                            inbetween_sections={
                                0: [InstructionSection(name="TrainingInstruction", instruction_text=self.language["Experiment"]["Instructions"]["Trial Instruction"]),
                                      ScenarioSection(name="ImagineScenario1_1", delay=120)], # A vs. Placebo
                                60: [ScenarioSection(name="ImagineScenario1_2", delay=30)],
                                120: [InstructionSection(name="TrainingBreakInstruction", instruction_text=self.language["Experiment"]["Instructions"]["Break Instruction"]),
                                        ScenarioSection(name="ImagineScenario2_1", delay=30)],
                                180: [ScenarioSection(name="ImagineScenario2_2", delay=30)],
                                }),
             # A vs. Placebo
            # End
            InstructionSection(name="EndInstruction", 
                               instruction_text=self.language["Experiment"]["Instructions"]["End Instruction"])    
        ])
    

    def set_conditions(self):
        print("set_conditions")
        """Assigns the conditions accoring to the settings file.
        Usually: B=1, B'=2, AB'=3, AB'C=4"""
        self.conditions = self.settings["Condition Codes"]

    def validate_language(self) -> None:
        print("validate_language")
        """Must be an ABC Language object"""
        if not isinstance(self.language, ABCLanguage):
            raise ValueError("language must be a Language object")
        else:
            self.language = self.language.content # The Language object has a content dict containing all text is displayed in the experiment.

    def define_output_file_name(self):
        print("define_output_file_name")
        """Includes Session Number and current time"""
        return f"{self.data['ID']}_{self.data['Session']}_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}"

    # Methods to prepare the experiment
    def assign_condition(self) -> None:
        """Assigns a condition according to gender and current group sizes."""
        #self.presession["Condition"] = "4" ############################################################################################### CHANGE THIS BACK TO RANDOMIZATION
        
        # Current group sizes for participant gender
        if self.presession["Condition_saved"] == "":
            groups = {}
            for condition in settings["Randomization"]:
                groups[condition] = self.settings["Randomization"][condition][self.presession["Sex"]]
            # Assign to group with smallest value
            condition = min(groups, key=groups.get)
            self.presession["Condition"] = min(groups, key=groups.get)
            # Update settings file
            self.settings["Randomization"][self.presession["Condition"]][self.presession["Sex"]] += 1
            with open (self.settings_path, "w") as f:
                json.dump(self.settings, f, indent=4)
            self.presession["Condition_saved"] = condition
            self.update_presession_config()
            
        else:
            self.presession["Condition"] = self.presession["Condition_saved"]
            self.update_presession_config()
        
    def create_pre_post_aat_config(self) -> Dict[str, List[Dict[str, str]]]:
        print("create_pre_post_aat_config")
        """Creates the config lists for the pre and post aat."""
        pre_aat = []
        post_aat = []
        alc_images = []
        non_alc_images = []
        for subcategory in self.img_set_a.images["alcoholic"]:
            # Add set a and b alcoholic images
            alc_images += [img for img in self.img_set_a.images["alcoholic"][subcategory]]
            alc_images += [img for img in self.img_set_b.images["alcoholic"][subcategory]]
        for subcategory in self.img_set_a.images["non_alcoholic"]:
            # Add set a and b non-alcoholic images
            non_alc_images += [img for img in self.img_set_a.images["non_alcoholic"][subcategory]]
            non_alc_images += [img for img in self.img_set_b.images["non_alcoholic"][subcategory]]
        for img in alc_images:
            # Pre AAT
            pre_aat.append({"code": "PREAAT_0_NEG_PUSH_LEFT", "delay": 0, "trialtype": "PUSH", "prime": img}) # congruent avoid
            pre_aat.append({"code": "PREAAT_0_NEG_PULL_RIGHT", "delay": 0, "trialtype": "PULL", "prime": img}) # incongruent approach
            # Post AAT
            post_aat.append({"code": "POSTAAT_0_NEG_PUSH_LEFT", "delay": 0, "trialtype": "PUSH", "prime": img}) # congruent avoid
            post_aat.append({"code": "POSTAAT_0_NEG_PULL_RIGHT", "delay": 0, "trialtype": "PULL", "prime": img}) # incongruent approach
        for img in non_alc_images:
            # Pre AAT
            pre_aat.append({"code": "PREAAT_0_POS_PUSH_LEFT", "delay": 0, "trialtype": "PUSH", "prime": img}) # incongruent avoid
            pre_aat.append({"code": "PREAAT_0_POS_PULL_RIGHT", "delay": 0, "trialtype": "PULL", "prime": img}) # congruent approach
            # Post AAT
            post_aat.append({"code": "POSTAAT_0_POS_PUSH_LEFT", "delay": 0, "trialtype": "PUSH", "prime": img}) # incongruent avoid
            post_aat.append({"code": "POSTAAT_0_POS_PULL_RIGHT", "delay": 0, "trialtype": "PULL", "prime": img}) # congruent approach
        shuffle(pre_aat)
        shuffle(post_aat)
        return {"pre_aat": pre_aat, "post_aat": post_aat}
    
    
    ############################################################################################################################################################################################
    ############################################################################################################################################################################################
    ############################################################################################################################################################################################
    
    
    def create_mini_aat_configs(self, n_configs: int = 4) -> Dict[str, List[Dict[str, str]]]:
        print("create_mini_aat_configs")
        """Creates n mini aat configs."""
        # Validate Condition
        if self.presession["Condition"] not in self.conditions.keys():
            raise ValueError("A valid condition mus be assigned before creating session configs.")
        alc_images = []
        non_alc_images = []
        mini_aat = []
            ### CURRENTLY USING SET B
        for subcategory in self.img_set_b.images["alcoholic"]:
            subcategory_imgs = [img for img in self.img_set_b.images["alcoholic"][subcategory]]
            # select 4 random images from each subcategory
            shuffle(subcategory_imgs)
            alc_images += subcategory_imgs[0:4]
        for subcategory in self.img_set_b.images["non_alcoholic"]:
            subcategory_imgs = [img for img in self.img_set_b.images["non_alcoholic"][subcategory]]
            # select 4 random images from each subcategory
            shuffle(subcategory_imgs)
            non_alc_images += subcategory_imgs[0:4]
        # Create mini aat configs
        for img in alc_images:
            mini_aat.append({"code": "MINIAAT_0_NEG_PUSH_LEFT", "delay": 0, "trialtype": "PUSH", "prime": img}) # congruent avoid
            mini_aat.append({"code": "MINIAAT_0_NEG_PULL_RIGHT", "delay": 0, "trialtype": "PULL", "prime": img}) # incongruent approach
        for img in non_alc_images:
            mini_aat.append({"code": "MINIAAT_0_POS_PUSH_LEFT", "delay": 0, "trialtype": "PUSH", "prime": img}) # incongruent avoid
            mini_aat.append({"code": "MINIAAT_0_POS_PULL_RIGHT", "delay": 0, "trialtype": "PULL", "prime": img}) # congruent approach
        configs = {}
        for i in range(n_configs):
            current_mini_aat = mini_aat.copy()
            shuffle(current_mini_aat)
            configs[f"mini_aat_{i+1}"] = current_mini_aat
        return configs
    
    ############################################################################################################################################################################################
    ############################################################################################################################################################################################
    ############################################################################################################################################################################################
    
    
    def create_training_configs(self, n_configs: int = 6) -> Dict[str, List[Dict[str, str]]]:
        print("create_training_configs")
        """Creates n training configs."""
        # Validate Condition
        if self.presession["Condition"] not in self.conditions.keys():
            raise ValueError("A valid condition mus be assigned before creating session configs.")
        
        alc_images = []
        non_alc_images = []
        training_aat = []
        # Everyone has set b images for training
        for subcategory in self.img_set_b.images["alcoholic"]:
                alc_images += [img for img in self.img_set_b.images["alcoholic"][subcategory]]
        for subcategory in self.img_set_b.images["non_alcoholic"]:
            non_alc_images += [img for img in self.img_set_b.images["non_alcoholic"][subcategory]]

        # Select remaining images according to condition
        if "B'" in self.conditions[self.presession["Condition"]]:
            # Select all personalization images
            for subcategory in self.presession["alcoholic"]:
                alc_images += [img for img in self.presession["alcoholic"][subcategory].values()]
            for subcategory in self.presession["non_alcoholic"]:
                non_alc_images += [img for img in self.presession["non_alcoholic"][subcategory].values()]
        else:
            # Select all standard images
            for subcategory in self.img_set_standard.images["alcoholic"]:
                
                alc_images += [img for img in self.img_set_standard.images["alcoholic"][subcategory]]
                
            for subcategory in self.img_set_standard.images["non_alcoholic"]:
                non_alc_images += [img for img in self.img_set_standard.images["non_alcoholic"][subcategory]]
            
            ##### THIS NEEDS TO BE CHANGED

        # Create training aat configs
        for img in alc_images:
            training_aat.append({"code": "TRAINAAT_0_NEG_PUSH_LEFT", "delay": 0, "trialtype": "PUSH", "prime": img}) # congruent avoid
            training_aat.append({"code": "TRAINAAT_0_NEG_PUSH_LEFT", "delay": 0, "trialtype": "PUSH", "prime": img}) # (do it twice)
        for img in non_alc_images:
            training_aat.append({"code": "TRAINAAT_0_POS_PULL_RIGHT", "delay": 0, "trialtype": "PULL", "prime": img}) # congruent approach
            training_aat.append({"code": "TRAINAAT_0_POS_PULL_RIGHT", "delay": 0, "trialtype": "PULL", "prime": img}) # (do it twice)
        configs = {}
        for i in range(n_configs):
            current_training_aat = training_aat.copy()
            shuffle(current_training_aat)
            configs[f"training_aat_{i+1}"] = current_training_aat
        return configs
    ############################################################################################################################################################################################
    ############################################################################################################################################################################################
    ############################################################################################################################################################################################
    
    def create_session_configs(self):
        print("create_session_configs")
        """Creates all config files for the participant after getting assigned a condition."""
        # Create aat configs
        pre_post_aat = self.create_pre_post_aat_config()
        mini_aats = self.create_mini_aat_configs() # REMOVE THE MINI AAT
        training_aats = self.create_training_configs()

        # Create config for each session
        # Session 1 Practice -> pre AAT -> Training
        session1 = {
            "Participant ID": self.presession["Participant ID"],
            "Session": 1,
            "Assessment": pre_post_aat["pre_aat"],
            "Training": training_aats["training_aat_1"]
        }
        try:
            with open(f"{self.config_path}/{self.presession['Participant ID']}/{self.experiment_prefix}_session1_{self.presession['Participant ID']}.json", "w") as f:
                json.dump(session1, f, indent=4)
        except:
            raise Exception("Could not save session 1 config.")
        # Session 2-5 Practice -> Mini AAT -> Training
        
        for i, mini_aat in enumerate(mini_aats):
            session = {
                "Participant ID": self.presession["Participant ID"],
                "Session": i+2,
                "Assessment": mini_aats[mini_aat],
                "Training": training_aats[f"training_aat_{i+2}"]
            }
            try:
                with open(f"{self.config_path}/{self.presession['Participant ID']}/{self.experiment_prefix}_session{i+2}_{self.presession['Participant ID']}.json", "w") as f:
                    json.dump(session, f, indent=4)
            except:
                raise Exception(f"Could not save session {i+2} config.")
        
        # Session 6 Practice -> post AAT -> Training
        session6 = {
            "Participant ID": self.presession["Participant ID"],
            "Session": 6,
            "Assessment": pre_post_aat["post_aat"],
            "Training": training_aats["training_aat_6"]
        }
        try:
            with open(f"{self.config_path}/{self.presession['Participant ID']}/{self.experiment_prefix}_session6_{self.presession['Participant ID']}.json", "w") as f:
                json.dump(session6, f, indent=4)
        except:
            raise Exception("Could not save session 6 config.")
    ############################################################################################################################################################################################
    ############################################################################################################################################################################################
    ############################################################################################################################################################################################
    def update_session_info(self) -> None:
        print("update_session_info")
        """Updates the session info in the presession file."""
        if self.presession["Current Session"] == 0:
            print("session 0 updadet to 1")
            self.presession["Current Session"] = 1
        self.update_presession_config()
        self.data["Session"] = self.presession["Current Session"]
    
    def update_presession_config(self) -> None:
        print("update_presession_config")
        """Updates the presession config file."""
        try:
            with open (f"{self.config_path}/{self.presession['Participant ID']}/{self.experiment_prefix}_presession_{self.presession['Participant ID']}.json", "w") as f:
                json.dump(self.presession, f, indent=4)
        except:
            raise Exception("Could not update presession config.")
    
    def update_session_number(self) -> None:
        self.presession["Current Session"] += 1
        self.update_presession_config()
        event.waitKeys(keyList=['j'])
        event.waitKeys(keyList=['f'])
    
    def get_expectations(self):
        """Get the expectations of the participant"""
        # Access relevant information from the rating dictionary
        self.win = visual.Window(size=self.settings["Window Size"], color=self.settings["Window Color"], fullscr=True)
        self.win.winHandle.set_fullscreen(True)  # Make the window appear in the foreground and topmost

        instruction_text = (
            "Bitte beschreiben Sie von 0 (gar nicht überzeugt) bis 10 (absolut überzeugt), wie sehr Sie davon überzeugt sind, dass das Anti-Alkohol-Training Ihnen dabei helfen wird, nent zu bleiben."
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

            # Once the space key is pressed, you can retrieve the value from the slider

        current_session = str(self.presession["Current Session"])  # Convert the session number to string to match the dictionary keys
        self.presession["Expectation"][current_session] = value

        self.win.close()

    def additional_settings(self):
        """"""
        
        # Update current session
        self.update_session_info()
        self.update_presession_config()
        # Assign condition ans create session configs in session 1
        if self.presession["Current Session"] == 1:
            self.assign_condition()
            self.create_session_configs()

        
        # Update presession config
        self.update_presession_config()
        """
        if self.presession["Current Session"] == 1 or self.presession["Current Session"] == 6:
            self.get_expectations()
        self.update_presession_config()
        """
        # Identify the scenarios with the highest rating for the participant
        scenario_keys = self.presession["Scenario Rating"].copy() # get all scenario ratings
        if "Custom Text" in self.presession["Scenario Rating"].keys():
            custom_scenario = scenario_keys["Custom Text"] # get custom scenario
            scenario_keys.pop("Custom Text", None) # remove custom scenario from dictionary
        scenario_keys = sorted(scenario_keys.items(), key=lambda x: x[1], reverse=True)[:self.settings["N Scenarios"]] # get 5 highest rated scenarios
        scenario_keys = [key for key, value in scenario_keys]
        scenario_texts = []
        for key in scenario_keys:
            if key == "Custom":
                scenario_texts.append(custom_scenario)
            else:
                scenario_texts.append(self.language["Experiment"]["Imagine Scenario"]["Scenarios"][key])

        # Identify the consequences with the highest rating for the participant
        consequence_keys = self.presession["Consequence Rating"].copy()
        custom_consequence = None  # Initialize to None

        if "Custom Text" in consequence_keys:
            custom_consequence = consequence_keys.pop("Custom Text", None)

        # Sort based on values
        sorted_consequences = sorted(consequence_keys.items(), key=lambda x: x[1], reverse=True)
        # Get the maximum rating
        max_rating = sorted_consequences[0][1]

        # Filter out only the ones with the highest rating
        highest_rated_consequences = [item for item in sorted_consequences if item[1] == max_rating]
        
        # Extract keys
        consequence_keys = [key for key, _ in highest_rated_consequences]
        conequence_texts = []
        for key in consequence_keys:
           
            if key == "Custom":
                conequence_texts.append(custom_consequence)
                
            else:
                conequence_texts.append(self.language["Experiment"]["Consider Consequences"]["Consequences"][key])
                

########################################################################################################################################################################################
        # Screen before scenario selection
        participation_condition = self.conditions[self.presession["Condition"]]
        if "A" in participation_condition:
            win = visual.Window(size=self.settings["Window Size"], color=self.settings["Window Color"], fullscr=True)
            txt = self.language["Experiment"]["Additional Settings"]["Additional Settings Screen"]["Text"]
            continue_txt = self.language["Experiment"]["Additional Settings"]["Additional Settings Screen"]["Continue"]
            visual.TextStim(win, text=txt, color=txt_color, pos=(0, 0), font="Arial", height=txt_height, wrapWidth=1.8, alignText="left").draw()
            visual.TextStim(win, text=continue_txt, color= "blue", pos=(0, txt_height-1+0.1), font="Arial", height=txt_height, wrapWidth=1.8, alignText="center").draw()
            win.flip()
            event.waitKeys(keyList=['space'])
            event.clearEvents()
            win.flip()
            win.winHandle.minimize()
            win.close()

###################################################################################################################################################################################      
        
        if "A" in participation_condition:
            window = tk.Tk()
            window.title("Select Scenario")
            window.geometry('1600x900')
            window.configure(bg='black')
            window.attributes('-topmost', True)  # To ensure the window is on top of others
            window.attributes('-fullscreen', True)

            # Calculate the center coordinates of the screen
            screen_width = window.winfo_screenwidth()
            screen_height = window.winfo_screenheight()
            center_x = screen_width // 2
            center_y = screen_height // 2

            gui_title = self.language["Experiment"]["Additional Settings"]["Select Scenario"]["Title"]
            field_label = self.language["Experiment"]["Additional Settings"]["Select Scenario"]["Field1"]
            select_scenario = {field_label: scenario_texts}
            # Create a label for the title
            title_label = tk.Label(window, text=gui_title, font=("Arial", 24), bg='black', fg='lightgray')
            title_label.place(x=center_x, y=50, anchor="center")  # Center it at the top

            selected_scenario = tk.StringVar(value="")  # Initialized with an empty value

            def select_scenario_callback(scenario_text):
                nonlocal selected_scenario
                selected_scenario.set(scenario_text)
                for btn in scenario_buttons:
                    btn["bg"] = "white"
                    btn["fg"] = "black"
                scenario_button_dict[scenario_text]["bg"] = "lightgray"
                scenario_button_dict[scenario_text]["fg"] = "blue"
                continue_btn["state"] = "normal"  # Enable the continue button once a scenario is selected
                error_msg_label.config(text="")  # Clear the error message if it's displayed

            def continue_callback():
                if not selected_scenario.get():
                    error_msg_label.config(text="Please select a scenario before proceeding!")  # Show the error message
                else:
                    window.destroy()

            scenario_texts = select_scenario[field_label]
            all_scenarios = scenario_texts.copy()  # To keep the original list of scenarios

            if len(scenario_texts) > 5:
                displayed_scenarios = random.sample(scenario_texts, 5)  # These are the scenarios currently displayed
            else:
                displayed_scenarios = scenario_texts

            scenario_button_dict = {}
            scenario_buttons = []

            def show_scenarios(scenarios_list):
                for btn in scenario_buttons:
                    btn.destroy()  # Remove the old buttons
                scenario_buttons.clear()
                scenario_button_dict.clear()

                start_y = center_y - len(scenarios_list) * 60 // 2

                for index, scenario_text in enumerate(scenarios_list):
                    if len(scenario_text) > 50:
                        font_size = 18
                    else:
                        font_size = 20

                    btn = tk.Button(window, text=scenario_text, 
                                    command=lambda text=scenario_text: select_scenario_callback(text), 
                                    anchor="w", bg="white", fg="black", font=("Arial", font_size))
                    btn.place(x=center_x, y=start_y + index * 60, width=1300, height=50, anchor="center")
                    scenario_buttons.append(btn)
                    scenario_button_dict[scenario_text] = btn

            show_scenarios(displayed_scenarios)

            def neue_scenarios_callback():
                global displayed_scenarios
                remaining_scenarios = [scenario for scenario in all_scenarios if scenario not in displayed_scenarios]

                if len(remaining_scenarios) >= 5:
                    new_scenarios = random.sample(remaining_scenarios, 5)
                else:
                    new_scenarios = remaining_scenarios

                displayed_scenarios = new_scenarios
                show_scenarios(new_scenarios)

            # Add the "Neue Scenarios" button only if there are more than 5 scenarios
            if len(all_scenarios) > 5:
                neue_scenarios_btn = tk.Button(window, text="Neue Scenarios", command=neue_scenarios_callback, font=("Arial", 20))
                neue_scenarios_btn.place(x=center_x - 200, y=700)  # Adjust the position as necessary

            continue_btn = tk.Button(window, text="Fortfahren", command=continue_callback, font=("Arial", 20), state="disabled", fg = "blue")  # Initially disable the button
            continue_btn.place(x=center_x, y=700, anchor="center")

            # Label to show the error message
            error_msg_label = tk.Label(window, text="", font=("Arial", 16), bg='black', fg='red')
            error_msg_label.place(x=center_x, y=770, anchor="center")  # Position it above the continue button

            window.mainloop()


            if "A" in participation_condition:
                attributes = {
                    "title_txt": self.language["Experiment"]["Imagine Scenario"]["Title"],
                    "continue_txt": self.language["Experiment"]["Imagine Scenario"]["Continue"],
                    "scenario_txt": selected_scenario.get(),
                    "ID": self.presession["Participant ID"],
                }
            
            self.scenario = selected_scenario.get()
        else:
            attributes = {
                    "title_txt": self.language["Experiment"]["Imagine Scenario"]["Neutral Title"],
                    "continue_txt": self.language["Experiment"]["Imagine Scenario"]["Neutral Continue"],
                    "scenario_txt": self.language["Experiment"]["Imagine Scenario"]["Neutral Text"],
                    "ID": self.presession["Participant ID"],
                }
            
            self.scenario = None

        self.data["Scenario"] = self.language["Experiment"]["Imagine Scenario"]["Neutral Text"]
        
        for section in self.sections:
            print(f"Section: {section}, Type: {section.type}")
            if section.type == "TRAINING":
                # loop through the inbetween_sections of the TrainingSection
                for _, inbetween_section_list in section.inbetween_sections.items():
                    for inbetween_section in inbetween_section_list:
                        if isinstance(inbetween_section, ScenarioSection):
                            print(f"Setting attributes for {inbetween_section.name}")
                            inbetween_section.set_attributes(attributes)
        
###################################################################################################################################################################################                
        if "C" in participation_condition:
            # Enable Feedback for condition C
            gui_title = "Bitte wählen Sie eine Abstinezmotivation mit der MAUS aus. Drücken Sie anschließend auf Fortfahren."
            field_label = ""
            select_scenario = {field_label: conequence_texts}

            # Extract the list of scenarios from select_scenario dictionary
            scenario_texts = select_scenario[field_label]

            # If there are more than 5 scenarios, randomly select 5
            if len(scenario_texts) > 5:
                scenario_texts = random.sample(scenario_texts, 5)

            window = tk.Tk()
            window.title("Select Contexts")
            window.geometry('1600x900')
            window.configure(bg='black')
            window.attributes('-topmost', True)  # To ensure the window is on top of others
            window.attributes('-fullscreen', True)

            # Calculate the center coordinates of the screen
            screen_width = window.winfo_screenwidth()
            screen_height = window.winfo_screenheight()
            center_x = screen_width // 2
            center_y = screen_height // 2

            # Create a label for the title
            title_label = tk.Label(window, text=gui_title, font=("Arial", 24), bg='black', fg='lightgray')
            title_label.place(x=center_x, y=50, anchor="center")  # Center it at the top

            selected_scenario = tk.StringVar(value="")  # Initialized with an empty value

            def select_scenario_callback(scenario_text):
                nonlocal selected_scenario
                selected_scenario.set(scenario_text)
                for btn in scenario_buttons:
                    btn["bg"] = "white"
                    btn["fg"] = "black"
                scenario_button_dict[scenario_text]["bg"] = "lightgray"
                scenario_button_dict[scenario_text]["fg"] = "blue"
                continue_btn["state"] = "normal"  # Enable the continue button once a scenario is selected
                error_msg_label.config(text="")  # Clear the error message if it's displayed

            def continue_callback():
                if not selected_scenario.get():
                    error_msg_label.config(text="Bitte wählen Sie eine Abstinenz Motivation aus!")  # Show the error message
                else:
                    window.destroy()

            scenario_button_dict = {}
            scenario_buttons = []

            # Calculate vertical starting position for scenario buttons
            start_y = center_y - len(scenario_texts) * 60 // 2

            for index, scenario_text in enumerate(scenario_texts):
                btn = tk.Button(window, text=scenario_text, command=lambda text=scenario_text: select_scenario_callback(text), anchor="w", bg="white", fg="black", font=("Arial", 20))
                btn.place(x=center_x, y=start_y + index * 60, width=1300, height=50, anchor="center")
                scenario_buttons.append(btn)
                scenario_button_dict[scenario_text] = btn

            continue_btn = tk.Button(window, text="Fortfahren", command=continue_callback, font=("Arial", 20), state="disabled", fg = "blue")  # Initially disable the button
            continue_btn.place(x=center_x, y=700, anchor="center")

            # Label to show the error message
            error_msg_label = tk.Label(window, text="", font=("Arial", 16), bg='black', fg='red')
            error_msg_label.place(x=center_x, y=770, anchor="center")  # Position it above the continue button

            window.mainloop()
            
            conequence_texts = [selected_scenario.get()]
            current_session = str(self.presession["Current Session"])  # Convert the session number to string to match the dictionary keys
            self.presession["Consequence"][current_session] = conequence_texts
            self.update_presession_config()
            
            for section in self.sections:
                if section.type in ["TRIAL", "PRACTICE", "TRAINING"]: ###
                    section.set_attributes({"give_feedback": True})
                    section.set_attributes({"only_progress": False})
                if section.type == "TRAINING":
                    for feedback in section.feedbacks:
                        feedback.add_consequences(conequence_texts)
            self.data["Consequence"] = str(conequence_texts[0])
        else:
            conequence_texts = ["", ""] 
            for section in self.sections:
                if section.type == "TRAINING":
                    section.set_attributes({"only_progress": True})
                    section.set_attributes({"give_feedback": True})
                    for feedback in section.feedbacks:
                        feedback.add_consequences(conequence_texts)
        self.data["Consequence"] = str(conequence_texts[0])


        # Load session config for current session
        with open(f"{self.config_path}/{self.presession['Participant ID']}/{self.experiment_prefix}_session{self.presession['Current Session']}_{self.presession['Participant ID']}.json", "r") as f:
            self.session_config = json.load(f)
        
        # Add data and trial configs attributes to TrialSections
        practice_trials = [{"code": "PRACTICE_0_NEG_PUSH_LEFT", "delay": 0, "trialtype": "PUSH", "prime": self.session_config["Assessment"][0]["prime"]},
                           {"code": "PRACTICE_0_POS_PULL_RIGHT", "delay": 0, "trialtype": "PULL", "prime": self.session_config["Assessment"][0]["prime"]}]
        for section in self.sections:
            if section.type == "ASSESSMENT":
                section.set_attributes({"trials": self.session_config["Assessment"]})
            elif section.type == "TRAINING":
                section.set_attributes({"trials": self.session_config["Training"]})
            elif section.type == "PRACTICE":
                section.set_attributes({"trials": practice_trials})
            section.set_attributes({"dat": self.data})

            
    def additional_settings1(self):
        self.get_expectations()
        print("Additional Settings")
        # Update current session
        self.update_session_info()
        self.update_presession_config()
        # Assign condition ans create session configs in session 1
        if self.presession["Current Session"] == 1:
            self.assign_condition()
            self.create_session_configs()

        
        # Update presession config
        self.update_presession_config()

        # Identify the scenarios with the highest rating for the participant
        scenario_keys = self.presession["Scenario Rating"].copy() # get all scenario ratings
        if "Custom Text" in self.presession["Scenario Rating"].keys():
            custom_scenario = scenario_keys["Custom Text"] # get custom scenario
            scenario_keys.pop("Custom Text", None) # remove custom scenario from dictionary
        scenario_keys = sorted(scenario_keys.items(), key=lambda x: x[1], reverse=True)[:self.settings["N Scenarios"]] # get 5 highest rated scenarios
        scenario_keys = [key for key, value in scenario_keys]
        scenario_texts = []
        for key in scenario_keys:
            if key == "Custom":
                scenario_texts.append(custom_scenario)
            else:
                scenario_texts.append(self.language["Experiment"]["Imagine Scenario"]["Scenarios"][key])

        # Identify the consequences with the highest rating for the participant
        consequence_keys = self.presession["Consequence Rating"].copy()
        custom_consequence = None  # Initialize to None

        if "Custom Text" in consequence_keys:
            custom_consequence = consequence_keys.pop("Custom Text", None)

        # Sort based on values
        sorted_consequences = sorted(consequence_keys.items(), key=lambda x: x[1], reverse=True)
        
        # Get the maximum rating
        max_rating = sorted_consequences[0][1]

        # Filter out only the ones with the highest rating
        highest_rated_consequences = [item for item in sorted_consequences if item[1] == max_rating]
        
        # Extract keys
        consequence_keys = [key for key, _ in highest_rated_consequences]
        conequence_texts = []
        for key in consequence_keys:
            print(key)
            if key == "Custom":
                conequence_texts.append(custom_consequence)
                print(consequence_keys)
            else:
                conequence_texts.append(self.language["Experiment"]["Consider Consequences"]["Consequences"][key])
                print(consequence_keys)

        
        ############################################################################################
        # Screen before scenario selection
        win = visual.Window(size=self.settings["Window Size"], color=self.settings["Window Color"], fullscr=True)
        txt = self.language["Experiment"]["Additional Settings"]["Additional Settings Screen"]["Text"]
        continue_txt = self.language["Experiment"]["Additional Settings"]["Additional Settings Screen"]["Continue"]
        visual.TextStim(win, text=txt, color=txt_color, pos=(0, 0), font="Arial", height=txt_height, wrapWidth=1.8, alignText="left").draw()
        visual.TextStim(win, text=continue_txt, color=txt_color, pos=(0, txt_height-1+0.1), font="Arial", height=txt_height, wrapWidth=1.8, alignText="left").draw()
        win.flip()
        event.waitKeys(keyList=['space'])
        event.clearEvents()
        win.flip()
        win.winHandle.minimize()
        win.close()

        
        # Let participant select a scenario
        participation_condition = self.conditions[self.presession["Condition"]]
###################################################################################################################################################################################      
        
        if "A" in participation_condition:
            gui_title = self.language["Experiment"]["Additional Settings"]["Select Scenario"]["Title"]
            field_label = self.language["Experiment"]["Additional Settings"]["Select Scenario"]["Field1"]
            select_scenario = {field_label: scenario_texts}

            # Extract the list of scenarios from select_scenario dictionary
            scenario_texts = select_scenario[field_label]

            window = tk.Tk()
            window.title("Select Scenario")
            window.geometry('1600x900')
            window.configure(bg='black')
            window.attributes('-topmost', True)  # To ensure the window is on top of others
            window.attributes('-fullscreen', True)

            # Create a label for the title
            title_label = tk.Label(window, text=gui_title, font=("Arial", 24), bg='black', fg='white')
            title_label.place(x=960, y=50, anchor="center")  # Center it at the top

            selected_scenario = tk.StringVar(value="")  # Initialized with an empty value

            def select_scenario_callback(scenario_text):
                nonlocal selected_scenario
                selected_scenario.set(scenario_text)
                for btn in scenario_buttons:
                    btn["bg"] = "white"
                    btn["fg"] = "black"
                scenario_button_dict[scenario_text]["bg"] = "lightgray"
                scenario_button_dict[scenario_text]["fg"] = "blue"
                continue_btn["state"] = "normal"  # Enable the continue button once a scenario is selected
                error_msg_label.config(text="")  # Clear the error message if it's displayed

            def continue_callback():
                if not selected_scenario.get():
                    error_msg_label.config(text="Please select a scenario before proceeding!")  # Show the error message
                else:
                    window.destroy()

            scenario_button_dict = {}
            scenario_buttons = []

            # Calculate vertical starting position for scenario buttons
            start_y = (1080 - len(scenario_texts) * 60) // 2

            for index, scenario_text in enumerate(scenario_texts):
                btn = tk.Button(window, text=scenario_text, command=lambda text=scenario_text: select_scenario_callback(text), anchor="w", bg="white", fg="black", font=("Arial", 20))
                btn.place(x=760, y=start_y + index * 60, width=1300, height=50, anchor="center")
                scenario_buttons.append(btn)
                scenario_button_dict[scenario_text] = btn

            continue_btn = tk.Button(window, text="Fortfahren", command=continue_callback, font=("Arial", 20), state="disabled")  # Initially disable the button
            continue_btn.place(x=760, y=700)

            # Label to show the error message
            error_msg_label = tk.Label(window, text="", font=("Arial", 16), bg='black', fg='red')
            error_msg_label.place(x=960, y=770, anchor="center")  # Position it above the continue button

            window.mainloop()

            if "A" in participation_condition:
                attributes = {
                    "title_txt": self.language["Experiment"]["Imagine Scenario"]["Title"],
                    "continue_txt": self.language["Experiment"]["Imagine Scenario"]["Continue"],
                    "scenario_txt": selected_scenario.get(),
                    "ID": self.presession["Participant ID"],
                }
            
            self.scenario = select_scenario[field_label]
        else:
            attributes = {
                    "title_txt": self.language["Experiment"]["Imagine Scenario"]["Neutral Title"],
                    "continue_txt": self.language["Experiment"]["Imagine Scenario"]["Neutral Continue"],
                    "scenario_txt": self.language["Experiment"]["Imagine Scenario"]["Neutral Text"],
                    "ID": self.presession["Participant ID"],
                }
            
            self.scenario = None

        self.data["Scenario"] = self.language["Experiment"]["Imagine Scenario"]["Neutral Text"]
        
        for section in self.sections:
            print(f"Section: {section}, Type: {section.type}")
            if section.type == "TRAINING":
                # loop through the inbetween_sections of the TrainingSection
                for _, inbetween_section_list in section.inbetween_sections.items():
                    for inbetween_section in inbetween_section_list:
                        if isinstance(inbetween_section, ScenarioSection):
                            print(f"Setting attributes for {inbetween_section.name}")
                            inbetween_section.set_attributes(attributes)
        
###################################################################################################################################################################################                
        if "C" in participation_condition:
            # Enable Feedback for condition C
            for section in self.sections:
                if section.type in ["TRIAL", "PRACTICE", "TRAINING"]:
                    section.set_attributes({"give_feedback": True})
                    section.set_attributes({"only_progress": False})
                # if the section has a feedback, add the consequence texts
                if section.type == "TRAINING":
                    for feedback in section.feedbacks:
                        feedback.add_consequences(conequence_texts)
        else:
            conequence_texts = ["", ""] 
            for section in self.sections:
                if section.type == "TRAINING":
                    section.set_attributes({"only_progress": True})
                    section.set_attributes({"give_feedback": True})
                    for feedback in section.feedbacks:
                        feedback.add_consequences(conequence_texts)

        # Load session config for current session
        with open(f"{self.config_path}/{self.presession['Participant ID']}/{self.experiment_prefix}_session{self.presession['Current Session']}_{self.presession['Participant ID']}.json", "r") as f:
            self.session_config = json.load(f)
        
        # Add data and trial configs attributes to TrialSections
        practice_trials = [{"code": "PRACTICE_0_NEG_PUSH_LEFT", "delay": 0, "trialtype": "PUSH", "prime": self.session_config["Assessment"][0]["prime"]},
                           {"code": "PRACTICE_0_POS_PULL_RIGHT", "delay": 0, "trialtype": "PULL", "prime": self.session_config["Assessment"][0]["prime"]}]
        for section in self.sections:
            if section.type == "ASSESSMENT":
                section.set_attributes({"trials": self.session_config["Assessment"]})
            elif section.type == "TRAINING":
                section.set_attributes({"trials": self.session_config["Training"]})
            elif section.type == "PRACTICE":
                section.set_attributes({"trials": practice_trials})
            section.set_attributes({"dat": self.data})  
            self.data["consequence"] = conequence_texts
    
    def presession_to_data(self):
        print("presession_to_data")
        """Adds the participant ID, condition and current session to the data dictionary."""
        self.data["ID"] = self.presession["Participant ID"]
        self.data["Condition"] = self.presession["Condition"]
        
    
    
