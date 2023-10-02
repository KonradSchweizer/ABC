# Programmer: Luke Korthals, https://github.com/lukekorthals

# The Presession class is used as a base class for experiment presessions. 
# It is supposed to be subclassed for a given experiment to determine the correct procedure. 
# Importantly, a Presession object relies on a Language object to determine the text snippets it uses. 
# A presesession is used to collect damographic data of participants and create a config file for each participant.
# The config files determine the behaviour of the experiment. 

###########
# Imports #
###########
# Standard libraries
import os

# Local modules
from classes.Language import Language

####################
# Presession class #
####################
class Presession:
    """During participant demographics and experiment settings are collected"""
    def __init__(self, 
                 language: Language = None, 
                 config_path: str = None, 
                 experiment_name: str = None) -> None:
        self.language = language
        self.config_path = config_path # Here participant configs are stored.
        self.experiment_name = experiment_name
        self.data = {}
        self.validate_inputs()
        self.language = self.language.content.copy()

    def validate_language(self) -> None:
        """To be overwritten by subclasses"""
        if not isinstance(self.language, Language):
            raise ValueError("language must be a Language object")

    def validate_inputs(self) -> None:
        """Makes sure that all required inputs are set."""
        self.validate_language()
        if self.config_path is None:
            raise ValueError("config_path must be specified")
        if not os.path.isdir(self.config_path):
            raise ValueError(f"config_path {self.config_path} does not exist")
        if self.experiment_name is None:
            raise ValueError("experiment_name must be specified")

    def run(self):
        """To be overwritten by subclasses"""
        raise NotImplementedError("run must be overwritten by subclass")
