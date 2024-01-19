import pytest
from psychopy import visual
from experiment_classes.ABCFeedback import MeterFeedback

@pytest.fixture
def meter_feedback():
    # Create a MeterFeedback object with some consequences
    feedback = MeterFeedback()
    feedback.add_consequence("A", 0.2)
    feedback.add_consequence("B", 0.5)
    feedback.add_consequence("C", 0.8)
    return feedback

def test_draw_meter(meter_feedback):
    # Create a window to draw the meter on
    win = visual.Window(size=(800, 600), units="pix", fullscr=False)
    meter_feedback.win = win

    # Test that the function raises an error if no consequences are added
    feedback = MeterFeedback()
    with pytest.raises(ValueError):
        feedback.draw_meter("A")

    # Test that the function raises an error if no window is added
    feedback = MeterFeedback()
    feedback.add_consequence("A", 0.2)
    with pytest.raises(ValueError):
        feedback.draw_meter("A")

    # Test that the function draws the meter correctly for each consequence
    for consequence, perc in meter_feedback.consequences.items():
        meter_feedback.perc = perc
        meter_feedback.draw_meter(consequence)
        win.flip()
        # You can add more specific tests here to check that the meter is drawn correctly
        # For example, you can check that the text is displayed correctly
        # You can also use the window's screenshot method to save a screenshot of the meter
        # and manually check that it looks correct