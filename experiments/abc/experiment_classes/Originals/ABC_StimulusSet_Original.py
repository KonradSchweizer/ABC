import json
import os
from typing import List


class ABCStimulusSet:
    """A set of image paths"""
    def __init__(self, name: str = None, 
                 folder_path: str = "experiments/abc/images", 
                 intialize_from_folders: bool = False) -> None:
        self.name = name
        self.folder_path = folder_path
        self.initialize_from_folders = intialize_from_folders
        self.images = {}
        self.initialize_images()
        self.validate_images()

    def validate_inputs(self) -> None:
        """Vaidates that a name and folder path are provided."""
        if self.name is None:
            raise ValueError("A name must be provided.")
        if self.folder_path is None:
            raise ValueError("A folder path must be provided.")
        if type(self.name) != str:
            raise TypeError("Name must be a string.")
        if type(self.folder_path) != str:
            raise TypeError("Folder path must be a string.")
        if self.name == "":
            raise ValueError("Name cannot be empty.")
        if self.folder_path == "":
            raise ValueError("Folder path cannot be empty.")
        if not os.path.exists(self.folder_path):
            raise FileNotFoundError("Folder path does not exist.")
    
    def initialize_images_from_folders(self) -> None:
        """Initializes the images from folders."""
        categories = os.listdir(self.folder_path)
        for category in categories:
            self.images[category] = {}
            for subcategory in os.listdir(f"{self.folder_path}/{category}"):
                self.images[category][subcategory] = [f"{self.folder_path}/{category}/{subcategory}/{image}" for image in os.listdir(f"{self.folder_path}/{category}/{subcategory}")]        
    
    def initilize_images_hardcoded(self) -> None:
        """A dict of images"""
        raise NotImplementedError

    def initialize_images(self) -> None:
        """Initializes the images."""
        if self.initialize_from_folders:
            self.initialize_images_from_folders()
        else:
            self.initilize_images_hardcoded()

    def validate_images(self) -> None:
        """Validates that all images exist."""
        for image in self.images:
            if not os.path.exists(f"{self.folder_path}/{image}"):
                raise FileNotFoundError(f"{self.name}: Image {f'{self.folder_path}/{image}'} does not exist.")
        print(f"{self.name}: All images validated.")

    def create_json(self, path) -> None:
        """Creates a JSON file of the images."""
        with open(f"{path}/abc_stim_{self.name}.json", "w") as f:
            json.dump(self.images, f)


class ABCStimulusSetA(ABCStimulusSet):
    """A set of 30 images used for the pre/post AAT"""
    def __init__(self, name: str = None, 
                 folder_path: str = "experiments/abc/images/set_a", 
                 intialize_from_folders: bool = True) -> None:
        super().__init__(name, folder_path, intialize_from_folders)
    
    def initilize_images_hardcoded(self) -> None:
        """Initializes the images."""
        print("Initialize_Images_Hardcoded", "IF YOU SEE THIS SOMETHING IS KONDA BAD")
        self.images["Beer"] = ["b_01_1_a.jpg",
                               "b_02_1_a.jpg",
                               "b_03_1_a.jpg",
                               "b_04_1_a.jpg",
                               "b_05_1_a.jpg"]
        self.images["Liquor"] = ["l_1_1_a.jpg",
                                 "l_2_1_a.jpg",
                                 "l_3_1_a.jpg",
                                 "l_4_1_a.jpg",
                                 "l_5_1_a.jpg"]
        self.images["Wine"] = ["w_01_1_1_a.jpg",
                               "w_02_1_1_a.jpg",
                               "w_03_1_1_a.jpg",
                               "w_04_1_1_a.jpg",
                               "w_05_1_2_a.jpg"]
        self.images["Water"] = ["wa_1_1_1_a.jpg",
                                "wa_2_1_1_a.jpg",
                                "wa_3_1_1_a.jpg",
                                "wa_4_1_1_a.jpg",
                                "wa_5_1_1_a.jpg"]
        self.images["Sparkling"] = ["s_1_1_a.jpg",
                                    "s_2_1_a.jpg",
                                    "s_3_1_a.jpg",
                                    "s_4_1_a.jpg",
                                    "s_5_1_a.jpg"]
        self.images["Non-Sparkling"] = ["ns_1_1_a.jpg",
                                        "ns_2_1_a.jpg",
                                        "ns_3_1_a.jpg",
                                        "ns_4_1_a.jpg",
                                        "ns_5_1_a.jpg"]


class ABCStimulusSetB(ABCStimulusSet):
    """A Set of 30 images used for the pre/post AAT and Training in B conditions"""
    print("Initialize_Images_Hardcoded", "IF YOU SEE THIS SOMETHING IS KONDA BAD")
    def __init__(self, name: str = None, 
                 folder_path: str = "experiments/abc/images/set_b", 
                 intialize_from_folders: bool = True) -> None:
        super().__init__(name, folder_path, intialize_from_folders)
    
    def initilize_images_hardcoded(self) -> None:
        self.images["Beer"] = ["b_06_1_t.jpg",
                                "b_07_1_t.jpg",
                                "b_08_1_t.jpg",
                                "b_09_1_t.jpg",
                                "b_10_1_t.jpg"]
        self.images["Liquor"] = ["l_6_1_t.jpg",
                                "l_7_1_t.jpg",
                                "l_8_1_t.jpg",
                                "l_9_1_t.jpg",
                                "l_10_1_t.jpg"]
        self.images["Wine"] = ["w_06_1_2_t.jpg",
                                "w_07_1_2_t.jpg",
                                "w_08_1_2_t.jpg",
                                "w_09_1_3_t.jpg",
                                "w_10_1_3_t.jpg"]
        self.images["Water"] = ["wa_6_1_1_t.jpg",
                                "wa_7_1_1_t.jpg",
                                "wa_8_1_1_t.jpg",
                                "wa_9_1_1_t.jpg",
                                "wa_10_1_1_t.jpg"]
        self.images["Sparkling"] = ["s_6_1_t.jpg",
                                    "s_7_1_t.jpg",
                                    "s_8_1_t.jpg",
                                    "s_9_1_t.jpg",
                                    "s_10_1_t.jpg"]
        self.images["Non-Sparkling"] = ["ns_6_1_t.jpg",
                                        "ns_7_1_t.jpg",
                                        "ns_8_1_t.jpg",
                                        "ns_9_1_t.jpg",
                                        "ns_10_1_t.jpg"]
    
class ABCStimulusSetPersonalization(ABCStimulusSet):
    """A set of 270 images used for personalization during the presession"""

    def __init__(self, name: str = None, 
                 folder_path: str = "experiments/abc/images/set_personalization", 
                 intialize_from_folders: bool = True) -> None:
        super().__init__(name, folder_path, intialize_from_folders)
    
class ABCStimulusSetStandard(ABCStimulusSet):
    """A set of 90 images making up the standard set"""
    
    def __init__(self, name: str = None, folder_path: str = "experiments/abc/images/set_standard", intialize_from_folders: bool = False) -> None:
        super().__init__(name, folder_path, intialize_from_folders)
