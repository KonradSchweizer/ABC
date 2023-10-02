###########
# Imports #
###########
import json

#####################
# ABCSettings Class #
#####################
class ABCSettings:
    def __init__(self, settings_path: str = "experiments/abc/settings/settings.json") -> None:
        self.settings_path = settings_path
        self.load_settings()

    def load_settings(self):
        with open(self.settings_path, "r") as f:
            self.settings = json.load(f)
        self.settings["Window Size"] = (float(self.settings["Window Size"][0]),
                                        float(self.settings["Window Size"][1]))
        self.settings["Font Size"] = float(self.settings["Font Size"])

###################
# Global Settings #
###################
global txt_height
global txt_color
global win_color
settings = ABCSettings().settings
txt_height = settings["Font Size"]
txt_color = settings["Font Color"]
win_color = settings["Window Color"]