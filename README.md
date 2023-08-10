# Wiigwaas
#### Experimental Linguistics & Fieldwork (ELF) Lab @ UBC

### Introduction
Wiigwaas contains the necessary pieces for visual world eye-tracking experiments.  The experimental code is written in Python and run in [PsychoPy](https://www.psychopy.org).  We use a Tobii eyetracker (Tobii Pro Fusion), recording the gaze data in [Tobii Pro Lab](https://www.tobii.com/products/software/behavior-research-software/tobii-pro-lab) via the [Titta](https://github.com/marcus-nystrom/Titta/tree/master) package.

The experiment that this code was created for involves a number of pictures being displayed on the screen, audio being played, and the participant selecting one of the images.  This process repeats for the desired number of trials.  However, this code can be used as a starting point and can be modified to work with different experimental flows.

Currently, the code is designed to work with input from either a mouse or touch screen (tested using X monitor).  The code could be modified to work with other input sources, and indeed we are planning on adding Cedrus support in future.

### `wiigwaas.py`
This is the code that manages the overall experimental flow.  It is specific to our example experiment, but provides an example of how to make use of the various functionality provided by the other modules.

It's the control centre from which each trial is structured, but it doesn't contain any reuseable functions.

### `display_resources.py`
This module contains functions related to what shows up on the screen.

### `eye_tracking_resources.py`
This module contains functions related to the eye-tracking process, including communication with Titta (and by extension, Tobii Pro Lab).