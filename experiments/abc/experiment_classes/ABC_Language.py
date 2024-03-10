# Programmer: Luke Korthals, https://github.com/lukekorthals

# The ABCLanguage class is used to supply text snippits to the ABCExperiment, and ABCExperimentSection objects.
# The template defines the structure that all language json files must follow.
# The template json file can be copied and translated to a different language to be used for the abc experiment. 

###########
# Imports #                                                                              #
###########
# Local modules
from classes.Language import Language

#######################
# ABC Language class  #                                                                              #
#######################
class ABCLanguage(Language):
    """Template to create language configs for the ABC experiment"""
    def __init__(self,
                 experiment_prefix: str = "abc",
                 json_file_path: str = "experiments/abc/settings/language_configs/abc/abc_template.json"):
        super().__init__(experiment_prefix, json_file_path)
    
    def set_template(self) -> None:
        """The content dict defined in all languages of the ABC experiment must follow this structure."""
        # Example in english language is provided here.
        # Run template_to_json() to create a json file from this template. 
        self.template = {
                        # Everything happening in the presession
                        "Presession": {
                            # Wait screen to prevent participants from mashing buttons
                            "Wait Screen": {
                                "Text": "Bilschwirm lädt...\n Bitte keine Tasten drücken!"
                            },
                            # The Instruction Screen at the beginning of the presession
                            "Instruction Screen": {
                                "Title": "Welcome to the ABC Presession (ADD TITLE TEXT)",
                                "Text": "In the following you will answer some rating scales, and select some pictures (ADD INSTRUCTION TEXT USE \\n FOR NEW LINE)",
                                "Continue": "Press space to continue."
                            },
                            # Screen to indicate desire before imagination
                            "Rate Desire Pre Screen": {
                                "Text":"Please indicate how much you want to drink alcohol right now.",
                                "Labels": ["not at all", "extremely"],
                                "Continue": "Press space to continue."
                            }, 
                            # The Scenario Imagine Screen at the and of the presession
                            "Imagine Scenario Screen": {
                                "Title": "Please imagine you are in the following scenario:",
                                "Continue": "After 60 seconds the next screen will appear automatically."
                            },
                            # Screen to close eyes and imagine
                            "Close Eyes Screen": {
                                "Text": "Please close your eyes and imagine you are in this situation.",
                                "Continue": "After 30 seconds the next screen will appear automatically."
                            },
                            # Screen to indicate desire after imagination
                            "Rate Desire Post Screen": {
                                "Text 1": "Please indicate how vivid your imagination was.",
                                #"Labels 1": ["not vivid at all"] + [" "] * 98 + ["very vivid"],
                                "Labels 1": ["not vivid at all", "very vivid"],
                                "Text 2": "Please indicate how much you want to drink alcohol right now.",
                                #"Labels 2": ["not at all"] + [" "] * 98 + ["extremely"],
                                "Labels 2": ["not at all", "extremely"],
                                "Continue": "Press space to continue."
                            },
                            "Imagine Two Weeks Screen": {
                                "Title": "Imagine what will happen in two weeks.",
                                "Text": "Imagine and carefully describe in detail a positive, specific, and vivid future events (big or small) which your are looking forward to. ",
                                "Continue": "Press space to continue.",
                                "Text 2": "Please indicate how vivid your imagination was.",
                                "Labels": ["not vivid at all", "very vivid"],
                            },
                            "Imagine One Month Screen": {
                                "Title": "Imagine what will happen in one month.",
                                "Text": "Imagine and carefully describe in detail a positive, specific, and vivid future events (big or small) which your are looking forward to. ",
                                "Continue": "Press space to continue.",
                                "Text 2": "Please indicate how vivid your imagination was.",
                                "Labels": ["not vivid at all", "very vivid"],
                            },
                            "Imagine Six Months Screen": {
                                "Title": "Imagine what will happen in six months.",
                                "Text": "Imagine and carefully describe in detail a positive, specific, and vivid future events (big or small) which your are looking forward to. ",
                                "Continue": "Press space to continue.",
                                "Text 2": "Please indicate how vivid your imagination was.",
                                "Labels": ["not vivid at all", "very vivid"],
                            },
                            "Imagine One Year Screen": {
                                "Title": "Imagine what will happen in one year.",
                                "Text": "Imagine and carefully describe in detail a positive, specific, and vivid future events (big or small) which your are looking forward to. ",
                                "Continue": "Press space to continue.",
                                "Text 2": "Please indicate how vivid your imagination was.",
                                "Labels": ["not vivid at all", "very vivid"],
                            },
                            # The Consequence Imagine Screen at the end of the presession
                            "Imagine Consequence Screen": {
                                "Title": "SOME TITLE (CONSEQUENCE Imagine Screen))",
                                "Text": "SOME TEXT",
                                "Continue": "Press space to continue."
                            },
                            "End Screen": {
                                "Text": "Thank you for completing the presession.",
                                "Continue": "The window will close automatically after a few seconds."
                            },
                            # The GUI that asks for the participant ID
                            "Gui Participant ID": { 
                                # Title of the gui window
                                "Title": "Enter the Participant ID",
                                # Label of the input field
                                "Field1": "Participant ID",
                                # Label of the second input field
                                "Field2": "Sex",
                                # Options for the second input field
                                "Options2": ["male", "female", "other", "prefer not to say"]
                            },
                            # If the ID already exists, this GUI asks what to do
                            "Gui Overwrite": { 
                                # Title of the gui window
                                "Title": "Participant ID already exists.", 
                                # Label of the input field
                                "Field1": "What to do?", 
                                # Options for the input field
                                "Options1": ["Overwrite", "Enter different ID"] 
                            },
                            # The window in which participants rate scenarios
                            "Scenario Rating": { 
                                # Title of the window
                                "Title": "1/4 Rating Scenarios", 
                                # General instruction
                                "Instruction": "Back when you were still drinking alcohol.\nHow often did you drink alcohol when", 
                                # Instruction to add a custom scenario
                                "Instruction Custom": "Add a custom scenario to complete the following sentece:\n\nBack when you were still drinking alcohol.\nHow often did you drink alcohol when...",
                                # Instruction to continue
                                "Continue": "After selecting a value, click 'space' to continue.",
                                # Instructio to continue when adding a custom scenario
                                "Continue Custom": "After entering your scenario, press 'escape' to continue.",
                                # Labels of the rating scale
                                "Labels": ["never", "always"],
                                # Scenario texts. These will be appended to the general instruction.
                                "Questions": {
                                    "Withdrawl": "you were suffering from not drinking alcohol or experiencing withdrawl symptoms.",
                                    "Headache": "you had a headache.",
                                    "Sad": "you felt sad.",
                                    "Holiday": "you were on holiday and wanted to relax.",
                                    "Worrying": "you were worrying about someone.",
                                    "Concerned": "you were very concerned about something.",
                                    "Desire": "you had a strong desire to drink alcohol to see what would happen.",
                                    "Social": "someone offered you alcohol in a social situation.",
                                    "Phantasy": "you phantasized about drinking alcohol.",
                                    "Control": "you wanted to test your ability to control your drinking.",
                                    "Craving": "you were physically desiring or craving alcohol.",
                                    "Exhausted": "you were physically exhausted.",
                                    "Pain": "you were in physical pain or had an injury.",
                                    "Anger": "you were so angry you felt you could explode.",
                                    "Watching": "you were watching someone else drinking alcohol at a bar or in a social setting.",
                                    "Wrong": "you felt everything was going wrong for you.",
                                    "Friends": "people you were drinking with before were encouraging you to drink alcohol.",
                                    "Irritated": "you felt irritated.",
                                    "Surprised": "you were surprised by the desire to drink alcohol.",
                                    "Party": "you were feeling well or partying with others.",
                                    # When this key is included, participants can enter a custom scenario
                                    "Custom": "Custom"
                                }
                            },
                            # The window in which participants rate consequences
                            "Consequence Rating": {
                                # Title of the window
                                "Title": "2/4 Rating Consequences",
                                # General instruction
                                "Instruction": "As a motivation to stop drinking, how important is it to you to",
                                # Instruction to add custom motivation
                                "Instruction Custom": "Describe a motivation to stop drinking that is very important to you.",
                                # Instruction to continue
                                "Continue": "After selecting a value, click 'space' to continue.",
                                # Instruction to continue when adding a custom motivation
                                "Continue Custom": "After entering your motivation, press 'escape' to continue.",
                                # Labels of the rating scale
                                "Labels": ["not at all important", "very important"],
                                # Consequence texts. These will be appended to the general instruction.
                                "Questions": {
                                    "Family": "improve your relationship with your family?",
                                    "Career": "be more successful in your career?",
                                    "Custom": "Custom"
                                }
                            },
                            # The window in which participants rate non-alcoholic drinks
                            "Non-Alcoholic Rating": {
                                # Title of the window
                                "Title": "3/4 Rating Non-Alcoholic Drinks",
                                # General instruction
                                "Instruction": "Rate how much you like this non-alcoholic drink.",
                                # Instruction to continue
                                "Continue": "After selecting a value, click 'space' to continue.",
                                # Labels of the rating scale
                                "Labels": ["not at all", "very much"],
                            },
                            # The window in which participants rate non-alcoholic drinks
                            "Non-Alcoholic Selection": {
                                # Gui for ranking
                                # Gui Title
                                "Gui Title": "Which type of non-alcoholic drinks do you prefer?",
                                # Gui Fields
                                "Gui Field1": "1) First preference",
                                "Gui Field2": "2) Second preference",
                                "Gui Field3": "3) Third preference",
                                # Options for Gui fields
                                "Gui Options": ["Water", "Sparkling", "Non-Sparkling"],
                                # Grid Selection
                                "Title": "3/4 Selecting Non-Alcoholic Drinks",
                                # General instruction
                                "Instruction": "Select the 5 drinks you like best by clicking on them",
                                # Instruction to continue
                                "Continue": "If you are happy with your selection, press 'space' to continue.",
                            },
                            # The window in which participants rate alcoholic drinks
                            "Alcoholic Rating": {
                                # Title of the window
                                "Title": "4/4 Rating Alcoholic Drinks",
                                # General instruction
                                "Instruction": "Back when you were still drinking alcohol.\nRate how often you drank alcoholic drinks like this.",
                                # Instruction to continue
                                "Continue": "After selecting a value, click 'space' to continue.",
                                # Labels of the rating scale
                                "Labels": ["never", "always"],  
                            },
                            # The window in which participants select alcoholic drinks
                            "Alcoholic Selection": {
                                # Gui for ranking
                                # Gui Title
                                "Gui Title": "Which type of alcoholic drinks did you drink most frequently?",
                                # Gui Fields
                                "Gui Field1": "1) Most frequently",
                                "Gui Field2": "2) Second most frequently",
                                "Gui Field3": "3) Least frequently",
                                # Options for Gui fields
                                "Gui Options": ["Beer", "Wine", "Liquor"], # The folder names of the stimuli have to correspond to this!!!
                                # Grid Selection
                                # Title of the window
                                "Title": "4/4 Selecting Alcoholic Drinks",
                                # General instruction
                                "Instruction": "Select the 5 drinks that most closely resemble drinks you frequently had before quitting alcohol.",
                                # Instruction to continue
                                "Continue": "If you are happy with your selection, press 'space' to continue.",  
                            }
                        },
                        # Everything happening in the main session
                        "Experiment": { 
                            # Gui to identify participant
                            "Load Presession": {
                                # Title of the gui window
                                "Title": "Enter the Participant ID",
                                # Label of the input field
                                "Field1": "Participant ID"
                            },
                            # All additional settings
                            "Additional Settings":{
                                # Additional Settings Screen
                                "Additional Settings Screen": {
                                    # Text
                                    "Text": "This is the screen before scenario selection. Text needs to be determined.",
                                    "Continue": "Press space to continue."
                                },
                                # Gui where participants choose a scenario for the current session
                                "Select Scenario": {
                                    # Title of the gui window
                                    "Title": "Select a scenario for this session",
                                    # Label of the input field
                                    "Field1": "Scenario",
                                }
                            },
                            # The window in which participants have to imagine the selected scenario
                            "Imagine Scenario": {
                                # Title of the window
                                "Title": "Imagine the following scenario:",
                                # Instruction to continue on first screen
                                "Continue": "Take your time and really try to imagine you are in this situation.\nAfter some time the next window will appear.",
                                # Scenarios
                                "Scenarios": {
                                    "Withdrawl": "Imagine you are suffering from not drinking alcohol or experiencing withdrawl symptoms.",
                                    "Headache": "Imagine you have a headache.",
                                    "Sad": "Imagine you feel sad.",
                                    "Holiday": "Imagine you are on holiday and want to relax.",
                                    "Worrying": "Imagine you are worrying about someone.",
                                    "Concerned": "Imagine you are very concerned about something.",
                                    "Desire": "Imagine you have a strong desire to drink alcohol to see what would happen.",
                                    "Social": "Imagine someone offers you alcohol in a social situation.",
                                    "Phantasy": "Imagine you are phantasizing about drinking alcohol.",
                                    "Control": "Imagine you want to test your ability to control your drinking.",
                                    "Craving": "Imagine you are physically desiring or craving alcohol.",
                                    "Exhausted": "Imagine you are physically exhausted.",
                                    "Pain": "Imagine you are in physical pain or have an injury.",
                                    "Anger": "Imagine you are so angry you feel you could explode.",
                                    "Watching": "Imagine you are watching someone else drinking alcohol at a bar or in a social setting.",
                                    "Wrong": "Imagine you feel everything is going wrong for you.",
                                    "Friends": "Imagine people you were drinking with before are encouraging you to drink alcohol.",
                                    "Irritated": "Imagine you feel irritated.",
                                    "Surprised": "Imagine you are surprised by the desire to drink alcohol.",
                                    "Party": "Imagine you are feeling well or are partying with others."
                                },
                            # Everything for participants who are not in an A condition
                            "Neutral Title": "Here we need to add a title for the neutral screen",
                            "Neutral Continue": "Here we need to add a continue text for the neutral screen",
                            "Neutral Text": "Here we need to add text for the neutral screen."
                            },
                            # The consequences participants in condition C will see
                            "Consider Consequences": {
                                "Consequences": {
                                    "Family": "Relationship with your family",
                                    "Career": "Success in your career",
                                }
                            }, 
                            # Text for instruction screens
                            "Instructions": {
                            "Welcome Instruction": "In dieser Session werden Sie Bilder von verschiedenen Getränken sehen. Jedes Bild wird leicht nach rechts oder links geneigt sein.\n\nIhre Aufgabe ist es, den Joystick entsprechend der Rotation zu bewegen:\n> Wenn das Bild nach links zeigt, schieben Sie den Joystick von sich weg.\n> Wenn das Bild nach rechts gedreht ist, ziehen Sie den Joystick zu sich heran.\n\nDas Bild verschwindet in dem Moment, in dem Sie den Joystick vollständig in die richtige Richtung bewegt haben. Bewegen Sie den Joystick zurück in die Mittelposition und drücken Sie den Auslöser mit Ihrem Zeigefinger, um das nächste Bild erscheinen zu lassen. \n\nVersuchen Sie, den Joystick so schnell wie möglich zu bewegen, ohne Fehler zu machen!\n\nDrücken Sie die Leertaste, um fortzufahren.",
                            "Practice Instruction": "Jetzt sehen Sie einige Übungsbilder.\n\nVergessen Sie nicht:\n> Bild nach LINKS geneigt = Schieben Sie es von sich weg.\n> Bild nach RECHTS geneigt = Ziehen Sie es zu sich heran.\n\nDrücken Sie die Leertaste, um zu starten.",
                            "Trial Instruction": "Jetzt werden Sie zusätzliche Bilder sehen.\n\nVergessen Sie nicht:\n> Bild nach LINKS geneigt = Schieben Sie es von sich weg.\n> Bild nach RECHTS geneigt = Ziehen Sie es zu sich heran.\n\nReagieren Sie SO SCHNELL WIE MÖGLICH OHNE FEHLER ZU MACHEN!\n\nDrücken Sie die Leertaste, um zu starten.",
                            "Break Instruction": "Sie haben eine Pause verdient.\n\nWenn Sie bereit sind, drücken Sie die Leertaste, um fortzufahren.",
                            "End Instruction": "Die Session ist nun beendet.\n\nVielen Dank für Ihre Teilnahme!\n\nDrücken Sie die Leertaste."
                            }
                    }
        }
