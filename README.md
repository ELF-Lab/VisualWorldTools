# Wiigwaas
#### Experimental Linguistics & Fieldwork (ELF) Lab @ UBC
Director: Dr. Chris Hammerly  
Author: Anna Stacey  

## Introduction
Wiigwaas contains the necessary pieces for visual world eye-tracking experiments.  The experimental code is written in Python and run in [PsychoPy](https://www.psychopy.org).  We use a Tobii eyetracker (Tobii Pro Fusion), recording the gaze data in [Tobii Pro Lab](https://www.tobii.com/products/software/behavior-research-software/tobii-pro-lab) via the [Titta](https://github.com/marcus-nystrom/Titta/tree/master) package.

The experiment that this code was created for involves a number of pictures being displayed on the screen, audio being played, and the participant selecting one of the images.  This process repeats for the desired number of trials.  However, this code can be used as a starting point and can be modified to work with different experimental flows.

Currently, the code is designed to work with input from either a mouse or touch screen (tested using X monitor).  The code could be modified to work with other input sources, and indeed we are planning on adding Cedrus support in future.

## `wiigwaas.py`
This is the code that manages the overall experimental flow.  It is specific to our example experiment, but provides an example of how to make use of the various functionality provided by the other modules.

It's the control centre from which each trial is structured, but it doesn't contain any reuseable functions.

### Running the Experiment

Open up `wiigwaas.py` in the Coder window of PsychoPy.  Hit the play button to run it.  If you're including the eye-tracking component (you can turn this off [here](#configpy)), you'll need to use Tobii Pro Lab for recording.

#### Setting Up Tobii Pro Lab
As noted in the Titta docs, if you want to record in Tobii Pro Lab, there are a few steps involved to get the software ready.
1. Open Tobii Pro Lab.
2. Create New Project > External Presenter Project
    - You can name the project whatever; we just stick with the default numbered names.
3. Switch to the Record tab.  
4. Now you can run the experiment from PsychoPy.
5. When the experiment is done, swtich to the Analyze tab to view the recording.

Note that if you are not changing the participant number each time you run the experiment, you will need to always be creating a new project or Tobii Pro Lab will complain that that participant already exists in the current project.

## `display_resources.py`
This module contains functions related to what shows up on the screen.
|Function|Inputs|Outputs|
|---|---|---|
|`checkForInputOnImages`: A general function (works for any input type) to check if the user has selected one of the images.|<ul> <li>`mouse`: the mouse object in the project</li><li>`images`: the set of images which you want to check for input on</li><li>`prevMouseLocation`: the variable that tracks where the mouse was last. This is needed in case you're using touch input, because it's processed as a hovering mouse.</li></ul>|<ul><li>`clickedImage`: the image from the given set that was selected. May be `None`.</li><li>`prevMouseLocation`: the updated mouse location to track</li></ul>|


## `eye_tracking_resources.py`
This module contains functions related to the eye-tracking process, including communication with Titta (and by extension, Tobii Pro Lab).

## `config.py`
This is where project-level constants are defined.  Various modules are expecting the following values to be defined:

|Constant name|Value|
|---|---|
|`EYE_TRACKING_ON`|A boolean indicating whether you want the experiment to run with or without including the eye-tracking steps.  This essentially allows a test mode where you can check how other parts of the experiment are working without worrying about the eye-tracking side.|
|`WINDOW_WIDTH`|An integer indicating the width of the screen the display will be shown on, in pixels.|
|`WINDOW_HEIGHT`|An integer indicating the height of the screen the display will be shown on, in pixels.|
|`USER_INPUT_DEVICE`|A string indicating the source of user input.  Currently supported values are 'mouse' or 'touch'.|
