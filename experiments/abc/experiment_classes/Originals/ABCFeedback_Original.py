# Programmer: Luke Korthals, https://github.com/lukekorthals

# The ABCFeedback classes are used for participants in C conditions.
# Participants in these conditions receive feedback to correct and incorrect trials.

###########
# Imports #                                                                                            #
###########
# Standard Libraries
from psychopy import visual, core
from typing import List

# Local Packages
from experiments.abc.experiment_classes.ABC_Settings import ABCSettings

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

#####################
# ABCFeedback Class #                                                                                            #
#####################
class ABCFeedback:
    """Superclass for different feedback types."""
    def __init__(self) -> None:
        self.win = None 
        self.correct = 0
        self.incorrect = 0
        self.consequences = None
    
    def add_win(self, win: visual.Window) -> None:
        """Adds a window to the Feedback object. 
        This should be gathered from the ExperimentSection where this Feedback is used."""
        if not isinstance(win, visual.Window):
            raise TypeError("win must be of type visual.Window")
        self.win = win
    
    def add_consequences(self, consequences: List[str]):
        """Adds a list of consequences to the Feedback.
        These should come from the participants config file."""
        if not isinstance(consequences, list):
            raise TypeError("consequences must be of type list")
        self.consequences = consequences
    
    def reset_correct_incorrect(self):
        self.correct = 0
        self.incorrect = 0   

    def present_feedback(self):
        pass      

class MeterFeedback(ABCFeedback):
    """Displays a meter for each consequence that can be filled between 0 and 100%.
    Correct behavior increases the meters, while incorrect behavior decreases them."""
    def __init__(self, 
                 perc: float = 0.5, # Defines the starting percent for the meter 
                 increment: float = 0.01): # Defines the increment that the meter will change by for each correct and incorrect trial
        super().__init__()
        self.perc = perc
        self.increment = increment
    
    def add_consequences(self, consequences: List[str]):
        """Uses method from superclass and ensures that no more than 5 consequences are used."""
        super().add_consequences(consequences)
        self.xmins = []
        distance = 0.4
        if len(self.consequences) == 1:
                start_xmin = 0
        elif len(self.consequences) == 2:
            start_xmin = -0.2
        elif len(self.consequences) == 3:
            start_xmin = -0.4
        elif len(self.consequences) == 4:
            start_xmin = -0.6
        elif len(self.consequences) == 5:
            start_xmin = -0.8
        else: 
            print("Too many consequences")
        for i, consequence in enumerate(self.consequences):
            self.xmins.append(start_xmin + i * distance)  
    
    def draw_meter(self) -> None:
        """Draws the meter on the window according to the current percent."""
        if self.consequences is None:
            raise("No consequences added to MeterFeedback object")
        if not isinstance(self.win, visual.Window):
            raise("No window was added to the MeterFeedback.")
        
        self.win.color = win_color
    
        for i, consequence in enumerate(self.consequences):
            xmin = self.xmins[i]
            # bar outline
            outline_xmin = xmin
            outline_xmax = xmin + 0.02
            outline_ymin = 0
            outline_ymax = 0.7
            visual.ShapeStim(win=self.win, vertices=((outline_xmax, outline_ymin), (outline_xmin, outline_ymin), (outline_xmin, outline_ymax), (outline_xmax, outline_ymax)), fillColor="black", lineColor="red").draw()
            # bar fill
            fill_xmin = outline_xmin + 0.002
            fill_xmax = outline_xmax - 0.002
            fill_ymin = outline_ymin + 0.005
            fill_ymax = outline_ymax - 0.005
            fill_y = fill_ymin + ((fill_ymax-fill_ymin)) * self.perc
            if self.perc > 0.66:
                fill_col = "green"
            elif self.perc < 0.33:
                fill_col = "red"
            else:
                fill_col = "yellow"
            visual.ShapeStim(win=self.win, vertices=((fill_xmax, fill_ymin), (fill_xmin, fill_ymin), (fill_xmin, fill_y), (fill_xmax, fill_y)), fillColor=fill_col, lineColor="black").draw()
            # text
            txt_x = xmin
            txt_y = outline_ymin - 0.08 
            visual.TextStim(win=self.win, text=f"{self.perc*100:.0f}% {consequence}", pos=(txt_x, txt_y), color=txt_color, font="Arial", height=txt_height, wrapWidth=0.4).draw()
        self.win.flip()

    def present_feedback(self, n_frames = 50) -> None:
        """Presents the meter and updates it for n_frames."""
        old_perc = self.perc
        new_perc = self.perc + (self.increment * self.correct) - (self.increment * self.incorrect)
        if new_perc >= 1:
            new_perc = 1
        elif new_perc <= 0:
            new_perc = 0
        if new_perc != old_perc:
            update_frame = (new_perc - old_perc) / n_frames
            for f in range(n_frames):
                self.perc += update_frame
                self.draw_meter() 
            core.wait(1)
        self.perc = new_perc
        