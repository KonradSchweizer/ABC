# Programmer: Luke Korthals, https://github.com/lukekorthals

# The Language class is used to supply text snippits to Experiment, and ExperimentSection objects. 
# It must be subsetted for a given experiment and the set_template() method must be overwritten to define the template dict.

####################
# Imports          #                                                                              #
####################
# Standard libraries
import json
import os
from psychopy import gui

####################
# Language class   #                                                                              #
####################
class Language:
    """A template to create different language configs for an experiment.
    Subclass this with a language class for a specific experiment.
    Define the template dict in the define_template() method of the subclass.
    Initialize the class with template_only = True and run the template_to_csv() method to create a csv file from the template.
    Afterwards you can copy the template file and translate the texts to a different language.
    Give the translated file an informative name like 'experiment_prefix_English.json'.

    The resulting class structure should look like this:
    Language
        ExperimentLanguage"""
    def __init__(self, 
                 experiment_prefix: str = None, # Added as a prefix to the template json.
                 json_file_path: str = None): # The path where all json configs should be saved.
        # Attributes set as parameters of the init method.
        self.experiment_prefix = experiment_prefix
        self.json_file_path = json_file_path
        # Attributes set by methods overwritten in subclasses.
        self.template = None
        self.content = None
        self.set_template() # The template should be defined in the ExperimentLanguage class
        #self.validate_template_json() # This makes sure that the template.json exists and matches the template dict.
        self.load_content_from_json() # The content should be defined in each specific Language class of a given experiment (e.g. ExperimentLanguageEN)
        #self.validate_content() # This makes sure that the content contains all the required keys and has no empty values.
        # Make sure that all attributes are set correctly.
        #self.validate_attributes() 

    # Methods to initialize the language
    def set_template(self) -> None:
        """This template defines the structure of keys and subdicts the content must follow. 
        Overwrite this method in subclasses to define the template for a given experiment."""
        raise NotImplementedError(" You need to define a template dict in the define_template() method of your subclass.")
        self.template = {} # A dict that defines the structure of the content dict.
    
    def template_to_json(self) -> None:
        """Saves the template dict as a json file."""
        
        if self.template is None:
            raise ValueError("You need to define a template dict in the define_template() method of your subclass.")
        json.dump(self.template, open(f"{self.json_file_path}/{self.experiment_prefix}_template.json", "w"), indent=4)
    
    def validate_template_json(self) -> None:
        """Validates that a template.json exists at the file path and that it matches the template dict."""
        template_json = os.path.join(self.json_file_path, f"{self.experiment_prefix}_template.json")
        if not os.path.isfile(template_json):
            self.template_to_json()
        else: 
            with open(template_json, "r", encoding="utf-8") as f:
                template = json.load(f)
            if template != self.template:
                self.template_to_json()      
    
    def load_content_from_json(self) -> None:
        """Loads the content_dict from a json file."""
        current_directory = os.path.dirname(os.path.abspath(__file__))
        root_directory = os.path.join(current_directory, "..")
        path = os.path.join(root_directory, "experiments", "abc", "settings", "language_configs","abc_template.json")

        #print(template_json_path)
        #path = r"C:\Users\Konrad Schweizer\OneDrive\Dokumente\University\Master\Major_Research_Project\Code\Python_Task\abc-psychopy-mainV2\abc-psychopy-main\experiments\abc\settings\language_configs\abc_template.json"
        with open(path, "r", encoding="utf-8") as f:
            self.content = json.load(f)

    def validate_content(self) -> None:
        """Checks if the content dict follows the same structure as the template dict and if all values are strings of length > 0."""
        if self.content is None:
            raise ValueError("You need to define a content dict in the define_content() method of your subclass.")
        def check_dict(content: dict, template: dict, level = 1) -> None:
            for (t_key, t_value), (c_key, c_value) in zip(template.items(), content.items()):
                # Check if the keys match
                if c_key != t_key:
                    raise ValueError(f"Level {level}, Key {c_key}: content key {c_key} does not match template key {t_key}")
                # Check if the value types match
                if type(c_value) != type(t_value):
                    raise ValueError(f"Level {level}, Key {c_key}: content value {c_value} type ({type(c_value)}) does not match template value {t_value} type ({type(t_value)}))")
                # If value is list, ...
                if isinstance(c_value, list):
                    # Check if length of lists match
                    if len(c_value) != len(t_value):
                        raise ValueError(f"Level {level}, Key {c_key}: length of content list {c_value} does not match length of template list {t_value}.")
                    # Check if all items in list are strings of length > 0
                    for item in c_value:
                        if not isinstance(item, str):
                            raise ValueError(f"Level {level}, Key {c_key}: content list item {item} is not a string.")
                        if len(item) == 0:
                            raise ValueError(f"Level {level}, Key {c_key}: content list item {item} is an empty string.")
                # If value is string, check that it is of length > 0
                elif isinstance(c_value, str):
                    if len(c_value) == 0:
                        raise ValueError(f"Level {level}, Key {c_key}: content string {c_value} is an empty string.")
                # If value is dict, call this function recursively
                elif isinstance(c_value, dict):
                    check_dict(c_value, t_value, level = level +1)
                # If value is anything else, raise an error
                else:
                    raise ValueError(f"Level {level}, Key {c_key}: content value {c_value} ({type(c_value)}) is not a list, string or dict.")
            print(f" > Level {level} All checks passed.")
        check_dict(self.content, self.template)
        print("Validation successful.")
         

    def validate_attributes(self) -> None:
        """Validates that all attributes are set correctly"""
        if not isinstance(self.experiment_prefix, str):
            raise ValueError("The experiment_prefix attribute must be a string.")
        if not isinstance(self.json_file_path, str):
            raise ValueError("The json_file_path attribute must be a string.")
        if not os.path.isdir(self.json_file_path):
            raise ValueError("The json_file_path attribute must be a valid path.")
        if not isinstance(self.template, dict):
            raise ValueError("The template attribute must be a dict.")
        if not isinstance(self.content, dict):
            raise ValueError("The content attribute must be a dict.")
        