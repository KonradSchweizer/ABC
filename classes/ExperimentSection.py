# Programmer: Luke Korthals, https://github.com/lukekorthals

# The ExperimentSection class builds the basis for all experiment sections.
# In the beginning of an experiment, the experiment sections are initialized by calling the initialize_section() method of each ExperimentSection object.
# During an experiment, a loop over all ExperimentSection objects is performed and the run_section() method of each object is called.

###########################
# ExperimentSection class #                                                                                 #
###########################
class ExperimentSection:
    def __init__(self, 
                 name: str, 
                 type: str, 
                 enabled: bool = True) -> None:
        self.name = name
        self.type = type
        self.enabled = enabled

    def set_attributes(self, attribute_dict: dict = None) -> None:
        """Sets the attributes of the ExperimentSection object."""
        for key, value in attribute_dict.items():
            setattr(self, key, value) 

    def validate_attributes(self) -> None:
        """Validates that all required attributes of the ExperimentSection object are set.
        This method should be overwritten by subclasses."""
        raise NotImplementedError
    
    def additional_settings(self) -> None:
        """If the section requires additional settings, define them here.
        This method should be overwritten by subclasses."""
        pass 

    def initialize_section(self) -> None:
        """Initializes the ExperimentSection by running additional_settings() and validate_attributes()."""
        self.additional_settings()
        self.validate_attributes()

    def run_section(self) -> None:
        """Runs the ExperimentSection object.
        This method should be extended by subclasses."""
        if not self.enabled:
            pass
