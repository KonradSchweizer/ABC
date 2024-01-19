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
from psychopy import gui, visual, event
from random import shuffle
from typing import Dict, List


# Local modules
from classes.Experiment import Experiment
from experiments.abc.experiment_classes.ABC_ExperimentSection import ScenarioSection, InstructionSection, PracticeSection, AssessmentSection, TrainingSection
from experiments.abc.experiment_classes.ABCFeedback import MeterFeedback
from experiments.abc.experiment_classes.ABC_Language import ABCLanguage
from experiments.abc.experiment_classes.ABC_Settings import *
from experiments.abc.experiment_classes.ABC_StimulusSet import ABCStimulusSet, ABCStimulusSetA, ABCStimulusSetB, ABCStimulusSetPersonalization


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
                img_set_b: ABCStimulusSet = ABCStimulusSetB()):
        self.settings = settings.settings.copy()
        self.settings_path = settings.settings_path
        self.img_set_a = img_set_a
        self.img_set_b = img_set_b
        joy_backend = self.settings["Joystick Backend"]
        win_resolution = self.settings["Window Size"]
        win_color = self.settings["Window Color"]
        super().__init__(language, config_path, output_path, experiment_prefix, joy_backend, win_resolution, win_color)
    
    # Methods to initialize the experiment
    def set_data(self) -> None:
        self.data = { 
                    "ID": None,
                    "Condition": None,
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
        # Assessment Sections (Congruent = 50%, Non-Alcoholic = 50%)
        assessment_trials = 120
        assessment_feedback_start_perc = 0.5 # Start the meter at 50%
        assessment_feedback_interval = 1 # Feedback after every trial
        assessment_feedback_increment = 1 / assessment_trials # Feedback can go up and down because of incongruent trials, divided by 2 because there are 2 assessment sections

        # Training Sections (Congruent = 100%, Non-Alcoholic = 50%)
        training_trials = 240 # There are four training sections with this number of trials each
        training_feedback_interval = 5 # Feedback after every 5 trials
        training_feedback_increment = 1 / training_trials / 4 # Feedback can only go up because only congruent trials, divived by 4 because there are 4 training sections
        
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
        print(self.sections[1].inbetween_sections)

    def set_conditions(self):
        """Assigns the conditions accoring to the settings file.
        Usually: B=1, B'=2, AB'=3, AB'C=4"""
        self.conditions = self.settings["Condition Codes"]

    def validate_language(self) -> None:
        """Must be an ABC Language object"""
        if not isinstance(self.language, ABCLanguage):
            raise ValueError("language must be a Language object")
        else:
            self.language = self.language.content # The Language object has a content dict containing all text is displayed in the experiment.

    def define_output_file_name(self):
        """Includes Session Number"""
        return f"{self.data['ID']}_{self.data['Session']}_{datetime.now().strftime('%Y_%m_%d')}"

    # Methods to prepare the experiment
    def assign_condition(self) -> None:
        """Assigns a condition according to gender and current group sizes."""
        # Current group sizes for participant gender
        groups = {}
        for condition in settings["Randomization"]:
            groups[condition] = self.settings["Randomization"][condition][self.presession["Sex"]]
        # Assign to group with smalles value
        self.presession["Condition"] = min(groups, key=groups.get)
        # Update settings file
        self.settings["Randomization"][self.presession["Condition"]][self.presession["Sex"]] += 1
        with open (self.settings_path, "w") as f:
            json.dump(self.settings, f, indent=4)

    def create_pre_post_aat_config(self) -> Dict[str, List[Dict[str, str]]]:
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

    def create_mini_aat_configs(self, n_configs: int = 4) -> Dict[str, List[Dict[str, str]]]:
        """Creates n mini aat configs."""
        # Validate Condition
        if self.presession["Condition"] not in self.conditions.keys():
            raise ValueError("A valid condition mus be assigned before creating session configs.")
        
        alc_images = []
        non_alc_images = []
        mini_aat = []
        # Select images according to condition
        if "B'" in self.conditions[self.presession["Condition"]]:
            #### CURRENTLY USING PERSONALIZED IMAGES
            #### HAVE ITS OWN SET
            #### - Each Image 1x congruent 1x incongruent
            #### - Not different for different conditions
            for subcategory in self.presession["alcoholic"]:
                subcategory_imgs = [img for img in self.presession["alcoholic"][subcategory]]
                # select 4 random images from each subcategory
                shuffle(subcategory_imgs)
                alc_images += subcategory_imgs[0:4]
            for subcategory in self.presession["non_alcoholic"]:
                subcategory_imgs = [img for img in self.presession["non_alcoholic"][subcategory]]
                # select 4 random images from each subcategory
                shuffle(subcategory_imgs)
                non_alc_images += subcategory_imgs[0:4]
        else:
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
    
    def create_training_configs(self, n_configs: int = 6) -> Dict[str, List[Dict[str, str]]]:
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
            #raise NotImplementedError("Unclear which images to use for Training for B conditions!!!")
             # Select all personalization images --> THIS IS INCORRECT FOR NON B' CONDITIONS

             ##### THIS NEEEDS TO BE CHANGED
            for subcategory in self.presession["alcoholic"]:
                alc_images += [img for img in self.presession["alcoholic"][subcategory].values()]
            for subcategory in self.presession["non_alcoholic"]:
                non_alc_images += [img for img in self.presession["non_alcoholic"][subcategory].values()]
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

    def create_session_configs(self):
        """Creates all config files for the participant after getting assigned a condition."""
        # Create aat configs
        pre_post_aat = self.create_pre_post_aat_config()
        mini_aats = self.create_mini_aat_configs()
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
    
    def update_session_info(self) -> None:
        """Updates the session info in the presession file."""
        self.presession["Current Session"] += 1
        self.data["Session"] = self.presession["Current Session"]
    
    def update_presession_config(self) -> None:
        """Updates the presession config file."""
        try:
            with open (f"{self.config_path}/{self.presession['Participant ID']}/{self.experiment_prefix}_presession_{self.presession['Participant ID']}.json", "w") as f:
                json.dump(self.presession, f, indent=4)
        except:
            raise Exception("Could not update presession config.")

    def additional_settings(self):
        print("Additional Settings")
        # Update current session
        self.update_session_info()
        print(self.presession["Current Session"])
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

        # Identify the 2 consequences with the highest rating for the participant
        consequence_keys = self.presession["Consequence Rating"].copy()
        if "Custom Text" in self.presession["Consequence Rating"].keys():
            custom_consequence = consequence_keys["Custom Text"]
            consequence_keys.pop("Custom Text", None)
        consequence_keys = sorted(consequence_keys.items(), key=lambda x: x[1], reverse=True)[:self.settings["N Consequences"]]
        consequence_keys = [key for key, value in consequence_keys]
        consequence_texts = []
        for key in consequence_keys:
            if key == "Custom":
                consequence_texts.append(custom_consequence)
            else:
                consequence_texts.append(self.language["Experiment"]["Consider Consequences"]["Consequences"][key])

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
        if "A" in participation_condition:
            gui_title = self.language["Experiment"]["Additional Settings"]["Select Scenario"]["Title"]
            field_label = self.language["Experiment"]["Additional Settings"]["Select Scenario"]["Field1"]
            select_scenario = {field_label: scenario_texts}
            gui.DlgFromDict(dictionary=select_scenario, title=gui_title)
            # enable all scenario sections (type=="SCENARIO") and add selected scenario
            attributes = {
                    "title_txt": self.language["Experiment"]["Imagine Scenario"]["Title"],
                    "continue_txt": self.language["Experiment"]["Imagine Scenario"]["Continue"],
                    "scenario_txt": select_scenario[field_label]
                }
            self.scenario = select_scenario[field_label]
        else:
            attributes = {
                    "title_txt": self.language["Experiment"]["Imagine Scenario"]["Neutral Title"],
                    "continue_txt": self.language["Experiment"]["Imagine Scenario"]["Neutral Continue"],
                    "scenario_txt": self.language["Experiment"]["Imagine Scenario"]["Neutral Text"]
                } 
            self.scenario = None     
        self.data["Scenario"] = self.scenario
        for section in self.sections:
                if section.type == "SCENARIO":
                    section.set_attributes(attributes)
        
        if "C" in participation_condition:
            self.consequence_1 = consequence_texts[0]
            self.consequence_2 = consequence_texts[1]
            self.data["Consequence_1"] = self.consequence_1
            self.data["Consequence_2"] = self.consequence_2
            # Enable Feedback for condition C
            for section in self.sections:
                if section.type in ["TRIAL", "PRACTICE", "ASSESSMENT", "TRAINING"]:
                    section.set_attributes({"give_feedback": True})
                # if the section has a feedback, add the consequence texts
                if section.type == "ASSESSMENT" or section.type == "TRAINING":
                    for feedback in section.feedbacks:
                        feedback.add_consequences([self.consequence_1, self.consequence_2])
        
        
        # DEPRECATED
        """# Identify highest rated alcoholic and non-alcoholic images
        non_alc_images = sorted(self.presession["Non-Alcoholic Rating"].items(), key=lambda x: x[1], reverse=True)[:self.settings["N Non-Alcoholic Images"]]
        non_alc_images = [key for key, value in non_alc_images]
        alc_images = sorted(self.presession["Alcoholic Rating"].items(), key=lambda x: x[1], reverse=True)[:self.settings["N Alcoholic Images"]]
        alc_images = [key for key, value in alc_images]"""

        # Load session config for current session
        with open(f"{self.config_path}/{self.presession['Participant ID']}/{self.experiment_prefix}_session{self.presession['Current Session']}_{self.presession['Participant ID']}.json", "r") as f:
            self.session_config = json.load(f)
        
        # Add data and trial configs attributes to TrialSections
        print(self.session_config["Assessment"][0]["prime"])
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
    
    def presession_to_data(self):
        """Adds the participant ID, condition and current session to the data dictionary."""
        self.data["ID"] = self.presession["Participant ID"]
        self.data["Condition"] = self.presession["Condition"]
    
    
