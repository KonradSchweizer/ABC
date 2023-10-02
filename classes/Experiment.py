# Programmer: Luke Korthals, https://github.com/lukekorthals

# The Experiment class builds the basis for all experiments. 
# It contains all basic methods to setup an experiment with all required settings. 
# Further methods defining the procedures of the experiment are defined in subclasses.

####################
# Imports          #                                                                              #
####################
# Standard libraries
from datetime import datetime
import json
import os
from psychopy import visual, gui
from psychopy.hardware import joystick
from typing import Tuple

# Local modules
from classes.ExperimentSection import ExperimentSection
from classes.Language import Language

####################
# Experiment class #                                                                                 #
####################
class Experiment:
    """ 
    The Experiment class builds the basis for all experiments.
    """
    def __init__(self, 
                 language: Language = None, # Language object that contains all text that is displayed in the experiment.
                 config_path: str = None, # Path to the folder where participant configs are stored.
                 output_path: str = None, # Path to the folder where the output csv is stored.
                 experiment_prefix: str = None, # Added as a prefix to the output csv.
                 joy_backend: str = "pyglet", # Joystick backend that is used to connect to the joystick.
                 win_resolution: Tuple[float] = (1280.0, 720.0),
                 win_color: str = "black"): # Resolution of the window that is used to display the experiment.
        # Attributes set as parameters of the init method.
        self.language = language
        self.validate_language()
        self.config_path = config_path 
        self.output_path = output_path 
        self.experiment_prefix = experiment_prefix
        self.joy_backend = joy_backend
        self.win_resolution = win_resolution
        self.win_color = win_color
        # Attributes set by methods overwritten in subclasses.
        self.data = None 
        self.sections = []
        self.conditions = []
        self.set_data() # Structure of the output data is defined in the set_data() method of subclasses.
        self.set_sections() # Sections are defined in the set_sections() method of subclasses.
        self.set_conditions() # Conditions are defined in the set_conditions() method of subclasses.
        # Make sure that all attributes are set correctly.
        self.validate_attributes() 
    
    # Methods to initialize the experiment
    def set_data(self) -> None:
        """Overwrite this method in subclasses to define the data that is written into the output csv."""
        raise NotImplementedError("You need to define the data the set_data() method of your subclass.")
        self.data = { # This is an example. Define the required output data structure as a dict. Keys are the column names.
            "ID": None,
            "Age": None,
        } 

    def set_sections(self):
        """A list of ExperimentSections to define the experiment.
        This needs to be overwritten by subclasses."""
        raise NotImplementedError("set_sections needs to be overwritten by subclasses")
        self.sections.extend([]) # Add ExperimentSection objects to the list.
    
    def set_conditions(self):
        """A dict of conditions and their code to define the experiment.
        This needs to be overwritten by subclasses."""
        raise NotImplementedError("set_conditions needs to be overwritten by subclasses")
        self.conditions = {1: "Control"} # Add conditions and their coding. Keys should be code, values should be clear text (e.g. {1: "Control"})
    
    def set_window_and_joystick(self): 
        """Setup window and joystick."""
        self.win = None
        self.joy = None
        joystick.backend = self.joy_backend
        self.win = visual.Window(size=self.win_resolution, 
                                 monitor="testMonitor", 
                                 color=self.win_color,
                                 winType=joystick.backend,
                                 allowGUI=True,
                                 fullscr=True)
        self.joy = joystick.Joystick(0)

    def validate_language(self) -> None:
        """The Language object is subclassed for a given experiment and this method should be adjusted to ensure that the correct Language object is used."""
        if not isinstance(self.language, Language):
            raise ValueError("language must be a Language object")
        else:
            self.language = self.language.content # The Language object has a content dict containing all text is displayed in the experiment.

    def validate_attributes(self) -> None:
        """Makes sure that all required attributes are set."""
        if self.config_path is None:
            raise ValueError("config_path must be specified")
        if not os.path.isdir(self.config_path):
            raise ValueError(f"config_path {self.config_path} does not exist")
        if self.output_path is None:
            raise ValueError("output_path must be specified")
        if not os.path.isdir(self.output_path):
            raise ValueError(f"output_path {self.output_path} does not exist")
        if self.experiment_prefix is None:
            raise ValueError("experiment_prefix must be specified")
        if self.joy_backend not in ["pyglet", "pygame"]:
            raise ValueError("joy_backend must be pyglet or pygame")
        if not isinstance(self.win_resolution, tuple):
            raise ValueError("win_resolution must be a tuple of two floats indicating the width and height of the window")
        if len(self.win_resolution) != 2:
            raise ValueError("win_resolution must have two floats indicating the width and height of the window")
        if not isinstance(self.win_resolution[0], float) or not isinstance(self.win_resolution[1], float):
            raise ValueError("win_resolution must have two floats indicating the width and height of the window")
        if not isinstance(self.data, dict):
            raise ValueError("data must be a dict and defined in the set_data() method of your subclass")
        if not isinstance(self.sections, list):
            raise ValueError("sections must be a list of ExperimentSection objects and defined in the set_sections() method of your subclass")
        for section in self.sections:
            if not isinstance(section, ExperimentSection):
                raise ValueError("sections must be a list of ExperimentSection objects and defined in the set_sections() method of your subclass")
        if not isinstance(self.conditions, dict):
            raise ValueError("conditions must be a dict of conditions and their codes and defined in the set_conditions() method of your subclass")
        if len(self.conditions) == 0:
            raise ValueError("Add at least one condition")
        
    # Methods to prepare the experiment
    def load_presession(self):
        """Loads the presession file according to a participant ID from the config_path."""
        gui_title = self.language["Experiment"]["Load Presession"]["Title"]
        field_label = self.language["Experiment"]["Load Presession"]["Field1"]
        participant = {field_label: ""}
        gui.DlgFromDict(dictionary=participant, title=gui_title)
        with open(f"{self.config_path}/{participant['Participant ID']}/{self.experiment_prefix}_presession_{participant['Participant ID']}.json", "r", encoding="utf-8") as f:
            self.presession = json.load(f)
    
    def additional_settings(self):
        """If the experiments requires additional settings, they can be added here.
        This needs to be overwritten by subclasses."""
        pass

    def presession_to_data(self):
        """If info (e.g., participant id) from the presession file needs to be added to the data dictionary, this can be done here.
        This needs to be overwritten by subclasses."""
        pass

    def define_output_file_name(self):
        """Can be overwritten by subclasses to define the output file name."""
        return f"{self.data['ID']}_{datetime.now().strftime('%Y_%m_%d')}"

    def create_output_file(self):
        """Creates the output file."""
        # Check if folder for ID exits, if not create it
        if not os.path.isdir(f"{self.output_path}/{self.data['ID']}"):
            os.mkdir(f"{self.output_path}/{self.data['ID']}")
        filename = f"{self.output_path}/{self.data['ID']}/{self.define_output_file_name()}.txt"
        # check if file already exists add number to filename until it doesn't
        i = 1
        while os.path.exists(filename):
            filename = f"{filename[:-4]}_{str(i)}{filename[-4:]}"
            i += 1
        column_names = [str(key) for key in self.data.keys()]  # dict.keys = column names
        with open(filename, "w") as f:
            f.write("\t".join(column_names) + "\n")
        self.output_path = filename
    
    def prepare_experiment(self) -> None:
        self.load_presession()
        self.presession_to_data()
        self.additional_settings()
        self.create_output_file()
        self.set_window_and_joystick()
        attributes = {
            "win": self.win,
            "joy": self.joy,
            "output_path": self.output_path
        }
        for section in self.sections:
            section.set_attributes(attributes) # All sections use the same window, joystick, and output path
            section.initialize_section()

    # Methods for running the experiment
    def run_experiment(self) -> None:
        for section in self.sections:
            print(f"Running section {section.name}")
            section.run_section()
    
    # Other Methods
    def minimize_window(self) -> None:
        """Minimizes the window before showing gui."""
        self.win.winHandle.set_fullscreen(False)
        self.win.winHandle.minimize()
        self.win.flip()
    
    def maximize_window(self) -> None:
        """Maximizes the window after showing gui."""
        self.set_window_and_joystick() # no idea why, but the maximizing method used in presession doesnt work here...
