from psychopy import visual, core
from typing import List
import random
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
import os


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
# ABCFeedback Class #                                                                                            
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
        """Uses method from superclass."""
        super().add_consequences(consequences)
        self.xmins = [0]  # Since we are displaying only one consequence, this will suffice

    def create_colormap(self):
        colors = [(1, 0, 0), (1, 1, 0), (0, 1, 0)]  # R -> Y -> G
        self.cm = LinearSegmentedColormap.from_list('custom_div_cmap', colors, N=100)

    def draw_meter(self, chosen_consequence: str) -> None:
        # Bar outline
        image = os.path.abspath(os.path.join(os.getcwd(), "experiments", "abc", "images", "Arrow.png"))
        xmin = self.xmins[0]
        outline_xmin = xmin - 0.15
        outline_xmax = xmin + 0.15
        outline_ymax = 0.69
        outline_ymin = -0.69
        outline_ymin = -0.15
        outline_ymax = 0.15
        if not hasattr(self, 'cm') and chosen_consequence != "":
            self.create_colormap()

        if not hasattr(self, 'arrow_image') and chosen_consequence != "":
            self.arrow_image1 = visual.ImageStim(win=self.win, image=image, interpolate=True)
            
            # Adjust position based on your preference
            arrow1_x_position = outline_xmax + 0.1 
            arrow_y_position = 0  
            self.arrow_image1.pos = (arrow1_x_position, arrow_y_position)
            self.arrow_image1.draw()
            


        if self.consequences is None:
            raise ValueError("No consequences added to MeterFeedback object")
        if not isinstance(self.win, visual.Window):
            raise ValueError("No window was added to the MeterFeedback.")

        self.win.color = "black"

        if chosen_consequence != "":
        
                # Bar fill with gradient color
            xmin = self.xmins[0]
            outline_xmin = xmin - 0.15
            outline_xmax = xmin + 0.15
            outline_ymax = 0.69
            outline_ymin = -0.69
            fill_xmin = outline_xmin + 0.002
            fill_xmax = outline_xmax - 0.002
            fill_height = (outline_ymax - outline_ymin) * self.perc
            num_segments = 100
            segment_height = (outline_ymax - outline_ymin) / num_segments
                        
            visual.ShapeStim(win=self.win, vertices=((outline_xmax, outline_ymin), (outline_xmin, outline_ymin), 
                (outline_xmin, outline_ymax), (outline_xmax, outline_ymax)), 
                fillColor="black", lineColor="white").draw()
            visual.TextStim(win=self.win, text=f"Abstinenzmotiv: {chosen_consequence}", pos=(0, 0.8), 
                    color= "white", font="Arial", height= 0.09, wrapWidth=1).draw()
            for i in range(int(num_segments * self.perc)):
                segment_ymin = outline_ymin + i * segment_height
                segment_ymax = outline_ymin + (i + 1) * segment_height

            # Get color from the colormap
            
                color = [c*2-1 for c in self.cm(i/num_segments)[:5]]

                visual.ShapeStim(win=self.win, vertices=((fill_xmax, segment_ymin), (fill_xmin, segment_ymin), 
                                (fill_xmin, segment_ymax), (fill_xmax, segment_ymax)), 
                                fillColor=color, lineColor=None).draw()
                if self.perc < .74:    
                    visual.TextStim(win=self.win, text=f"{self.perc*100:.0f}%", pos=(0,0), 
                                color= "white", font="Arial", height= 0.2, wrapWidth=0.4).draw()
                else:
                    visual.TextStim(win=self.win, text=f"{self.perc*100:.0f}%", pos=(0,0), color= "black", font="Arial", height= 0.2, wrapWidth=0.4).draw()
        else:
            outline_xmin = -0.69
            outline_xmax = 0.69
            outline_ymin = 0 - 0.15
            outline_ymax = 0 + 0.15
            # Draw Bar Outline
            visual.ShapeStim(win=self.win, vertices=((outline_xmax, outline_ymin), (outline_xmin, outline_ymin), 
                            (outline_xmin, outline_ymax), (outline_xmax, outline_ymax)), 
                            fillColor="black", lineColor="white").draw()

            # Bar fill with gradient color
            fill_ymin = outline_ymin + 0.002
            fill_ymax = outline_ymax - 0.002
            fill_width = (outline_xmax - outline_xmin) * self.perc
            num_segments = 100
            segment_width = (outline_xmax - outline_xmin) / num_segments

            for i in range(int(num_segments * self.perc)):
                segment_xmin = outline_xmin + i * segment_width
                segment_xmax = outline_xmin + (i + 1) * segment_width

                color = "grey"
                visual.ShapeStim(win=self.win, vertices=((segment_xmin, fill_ymax), (segment_xmin, fill_ymin), 
                                (segment_xmax, fill_ymin), (segment_xmax, fill_ymax)), 
                                fillColor=color, lineColor=None).draw()
                visual.TextStim(win=self.win, text=f"{self.perc*100:.0f}%", pos=(0,0), 
                                color= "white", font="Arial", height= 0.2, wrapWidth=0.4).draw()
        

        self.win.flip()

    def congratulation(self, chosen_consequence: str):
        def type_text_effect(text_stim, duration=0.05):
            text_content = text_stim.text
            for i in range(len(text_content) + 1):
                text_stim.setText(text_content[:i])
                text_stim.draw()
                self.win.flip()
                core.wait(duration)

        # First part
        text1 = visual.TextStim(win=self.win, text="Herzlichen Glückwunsch!", pos=(0, 0), 
                                color="white", font="Arial", height=0.2, wrapWidth=2.5)
        type_text_effect(text1)
        core.wait(2)

        # Ensure the colormap is created
        if not hasattr(self, 'cm'):
            self.create_colormap()

        text2 = visual.TextStim(win=self.win, text="Sie haben ", pos=(0, 0), 
                                color="white", font="Arial", height=0.2, wrapWidth=2.5)
        percent_text = visual.TextStim(win=self.win, text="100%", pos=(0, 0), 
                                    color="green", font="Arial", height=0.5, wrapWidth=2.5)
        text2_2 = visual.TextStim(win=self.win, text="ihres Ziels für diese Session erreicht", pos=(0, 0), font="Arial", height=0.2, wrapWidth=2.5)

        type_text_effect(text2)
        core.wait(1)

            
        percent_text.draw()
        self.win.flip()
        core.wait(2)

        type_text_effect(text2_2)
        core.wait(2)

        # Third part
        text3 = visual.TextStim(win=self.win, text=f"Sie sind nun etwas näher an {chosen_consequence}!", 
                                pos=(0, 0), color="white", font="Arial", height=0.2, wrapWidth=1.5)
        type_text_effect(text3)
        core.wait(2)


        
    def present_feedback(self, base_n_frames=50) -> None:
        """Presents the meter and updates it for n_frames."""
        # Randomly choose a consequence to display
        chosen_consequence = self.consequences[0]
        old_perc = self.perc
        new_perc = self.perc + (self.increment * self.correct) - (self.increment * self.incorrect)
        if new_perc >= 1:
            new_perc = 1
        elif new_perc <= 0:
            new_perc = 0
        
        perc_diff = abs(new_perc - old_perc)
        
        # Adjust the number of frames based on perc_diff.
        # This is just a basic example, and you may need to fine-tune the formula.
        # The goal is to reduce the number of frames as perc_diff increases.
        n_frames = int(base_n_frames / (1 + 10.2857142857143* self.perc)) # Who ever reads this, DO NOT CHANGE THIS NUMBER OTHERWISE EVERYTHING IS FUCKED NO IDEA WHY BUT THIS IS THE NUMBER
        if n_frames < 1:  # Ensure we have at least one frame.
            n_frames = 1
        
        if new_perc != old_perc:
            update_frame = (new_perc - old_perc) / n_frames
            for f in range(n_frames):
                self.perc += update_frame
                self.draw_meter(chosen_consequence)
            core.wait(1)
            self.perc = new_perc

        if self.perc > 0.99 and chosen_consequence != "":
            self.congratulation(chosen_consequence)

            
