# Visual World Tools
#### Experimental Linguistics & Fieldwork (ELF) Lab @ UBC
Director: [Dr. Chris Hammerly](https://github.com/christopherhammerly)  
Author: [Anna Stacey](https://github.com/anna-stacey)

## Introduction
This repo contains the necessary pieces for visual world eye-tracking experiments.  The experimental code is written in Python and run in [PsychoPy](https://www.psychopy.org).  We use a Tobii eyetracker (Tobii Pro Fusion), recording the gaze data in [Tobii Pro Lab](https://www.tobii.com/products/software/behavior-research-software/tobii-pro-lab) (TPL) via the [Titta](https://github.com/marcus-nystrom/Titta/tree/master) package.

The experiment that this code was created for involves a number of pictures being displayed on the screen, audio being played, and the participant selecting one of the images.  This process repeats for the desired number of trials.  However, this code was designed to be reuseable and can be used to create different experimental flows.  For this purpose, the repo is structured into modules (`display_resources.py`, `eye_tracking_resources.py`) which have reuseable functions that can be pieced together as you wish.  Then `wiigwaas.py` provides an example of how to construct an experiment using these pieces.  You may wish to use `wiigwaas.py` as a starting point, and modify it to create the specific experimental flow you're after.

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

### What happens in `wiigwaas.py`?
This example experiment involves a brief set-up stage (including calibration), followed by repeated calls to `trial()`.  The flow of each trial, from the participant perspective, is as follows:
1. Display a blank screen for a brief period.
2. Display a buffer screen until the user clicks/taps.
3. Display a fixation cross and perform a dritft check.
    - If failed, recalibrate.
4. Show the stimuli and play the audio.  At this point, there are a few different options for user input:
    - A click/tap on a stimulus image leads to a box displayed around the selected image and an associated checkmark confirmation button appearing. Only one stimulus can be selected at a time, so a click/tap on a different image will move the box and checkmark.
    - A click/tap on the repeat icon will make the audio replay.
    - A click/tap on a checkmark button will confirm their choice and end this trial.

## `display_resources.py`
This module contains functions related to what shows up on the screen.

#### Input-Related Functions
|Function|Inputs|Outputs|
|---|---|---|
|`check_for_input_on_images`: a general function (works for any input type) to check if the user has selected one of the images.|<ul><li>`mouse`: the PsychoPy event.Mouse object for the whole project</li><li>`images`: a list of ImageStim objects, containing the set of images which you want to check for input on</li><li>`prev_mouse_location`: the list of coordinates (i.e. `[x, y]`) that saves where the mouse was last. This is needed in case you're using touch input, because it's processed as a hovering mouse.</li></ul>|<ul><li>`selected_image`: an ImageStim object which is the image from the given set that was selected. May be `None`.</li><li>`prev_mouse_location`: the updated mouse location to track, expressed as coordinates </li></ul>|
|`_check_for_click_on_images`: a private function (to be called by the more general `check_for_input_on_images`) to check if the user has selected one of the images *via mouse input*.|<ul> <li>`mouse`: the PsychoPy event.Mouse object for the whole project</li><li>`images`: a list of ImageStim objects, containing the set of images which you want to check for input on</li><li>`prev_mouse_location`: the list of coordinates (i.e. `[x, y]`) that saves where the mouse was last. This is needed in case you're using touch input, because it's processed as a hovering mouse.</li></ul>|<ul><li>`clicked_image`: the image from the given set that was selected. May be `None`.</li><li>`prev_mouse_location`: the updated mouse location to track, expressed as coordinates</li></ul>|
|`_check_for_tap_on_images`: a private function (to be called by the more general `check_for_input_on_images`) to check if the user has selected one of the images *via touch input*.|<ul> <li>`mouse`: the PsychoPy event.Mouse object for the whole project</li><li>`images`: a list of ImageStim objects, containing the set of images which you want to check for input on</li><li>`prev_mouse_location`: the list of coordinates (i.e. `[x, y]`) that saves where the mouse was last. This is needed in case you're using touch input, because it's processed as a hovering mouse.</li></ul>|<ul><li>`tapped_image`: the image from the given set that was selected. May be `None`.</li><li>`prev_mouse_location`: the updated mouse location to track, expressed as coordinates</li></ul>|
|`check_for_input_anywhere`: a general function (works for any input type) to check if the user has selected one of the images.|<ul> <li>`mouse`: the PsychoPy event.Mouse object for the whole project</li><li>`prev_mouse_location`: the list of coordinates (i.e. `[x, y]`) that saves where the mouse was last. This is needed in case you're using touch input, because it's processed as a hovering mouse.</li></ul>|<ul><li>`input_received`: a boolean indicating whether or not any input occurred</li><li>`prev_mouse_location`: the updated mouse location to track, expressed as coordinates</li></ul>|
|`_check_for_click_anywhere`: a private function (to be called by the more general `check_for_input_on_images`) to check if the user has selected one of the images *via mouse input*.|<ul> <li>`mouse`: the PsychoPy event.Mouse object for the whole project</li><li>`prev_mouse_location`: the list of coordinates (i.e. `[x, y]`) that saves where the mouse was last. This is needed in case you're using touch input, because it's processed as a hovering mouse.</li></ul>|<ul><li>`clicked`: a boolean indicating whether or not a click was received</li><li>`prev_mouse_location`: the updated mouse location to track, expressed as coordinates</li></ul>|
|`_check_for_tap_anywhere`: a private function (to be called by the more general `check_for_input_on_images`) to check if the user has selected one of the images *via touch input*.|<ul> <li>`mouse`: the PsychoPy event.Mouse object for the whole project</li><li>`prev_mouse_location`: the list of coordinates (i.e. `[x, y]`) that saves where the mouse was last. This is needed in case you're using touch input, because it's processed as a hovering mouse.</li></ul>|<ul><li>`tapped`: a boolean indicating whether or not a tap was received<li><li>`prev_mouse_location`: the updated mouse location to track, expressed as coordinates</li></ul>|
|`clear_clicks_and_events`: a function that resets PsychoPy's tracking of clicks and other events.  Psychopy [recommends](https://psychopy.org/api/event.html#psychopy.event.Mouse.getPressed) this at stimulus onset.|<ul> <li>`mouse`: the PsychoPy event.Mouse object for the whole project</li></ul>||
|`handle_input_on_stimulus`: a function that deals with the user selection of a stimulus.  Given the predetermined selected ImageStim, it draws the selection box around that image and adds the checkmark button to that image.  This function has a lot of input parameters because it involves re-drawing the whole stimuli screen.|<ul><li>`selected_image`: an ImageStim object indicating which image from the given set was selected. This function is only called when an image has been selected, so this should not be None.</li><li>`images`: a list of ImageStim objects, containing the set of stimuli which may have been selected.</li><li> `checkmarks`: a list of ImageStim objects, containing a checkmark associated with each image</li><li>`selection_box`: a PsychoPy Rect object for the box around the selected image. This function will assign it the correct position based on the selected image.</li><li>`repeat_icon`: an ImageStim for the repeat button</li><li>`trial_clock`: a Psychopy core.Clock object associated with the present trial</li><li>`clicks`: a list recording each click. Each item in the list is itself a list containing a) a string identifying what was clicked, and b) a float indicating the time of the click in seconds (based on the `trial_clock`).</li><li>`recorder`: the recorder object, an instance of Titta's `TalkToProLab` class, that is tracking the gaze.  As usual, this is just being passed on for the sake of updating the recorder on what's on screen.</li><li>`main_window`: the Psychopy visual.Window object for the project, whose display will be changed.</li></ul>|<ul><li>`checkmark`: the ImageStim object for the checkmark which is now displayed on-screen, associated with the selected image|

#### Display-Related Functions
|Function|Inputs|Outputs|
|---|---|---|
|`display_blank_screen`: a function that changes the display to just a blank screen.|<ul> <li>`recorder`: the recorder object, an instance of Titta's `TalkToProLab` class, that is tracking the gaze.  This is just being passed on, not used in this function per se, for the sake of updating the recorder on what's on screen.</li><li>`main_window`: the Psychopy visual.Window object for the project, whose display will be changed.</li></ul>||
|`display_buffer_screen`: a function that changes the display to just a buffer screen, where the experiment will remain until user input is received.  The buffer screen is used as a kind of pause in between trials.|<ul> <li>`recorder`: the recorder object, an instance of Titta's `TalkToProLab` class, that is tracking the gaze.  This is just being passed on, not used in this function per se, for the sake of updating the recorder on what's on screen.</li><li>`main_window`: the Psychopy visual.Window object for the project, whose display will be changed.</li><li>`mouse`: the PsychoPy event.Mouse object for the whole project</li><li>`buffer_text`: a string containing the text to be displayed for the duration of the buffer screen</li><li>`quit_function`: the function that will be run if the user quits while the buffer screen is being displayed</li></ul>||
|`display_fixation_cross_screen`: a function that changes the display to a fixation cross.  Note that any drift check is not controlled from here - this function simply changes the display.|<ul> <li>`recorder`: the recorder object, an instance of Titta's `TalkToProLab` class, that is tracking the gaze.  This is just being passed on, not used in this function per se, for the sake of updating the recorder on what's on screen.</li><<li>`main_window`: the Psychopy visual.Window object for the project, whose display will be changed.</li></ul>||
|`display_stimuli_screen`: a function that changes the display to show the stimuli objects|<ul> <li>`recorder`: the recorder object, an instance of Titta's `TalkToProLab` class, that is tracking the gaze.  This is just being passed on, not used in this function per se, for the sake of updating the recorder on what's on screen.</li><li>`main_window`: the Psychopy visual.Window object for the project, whose display will be changed.</li><li>`stimuli_list`: the list of stimuli as ImageStim objects (which should already have their position etc. assigned), each of which will be drawn on screen.</li></ul>||
|`display_text_screen`: a function that changes the display to show some text|<ul> <li>`recorder`: the recorder object, an instance of Titta's `TalkToProLab` class, that is tracking the gaze.  This is just being passed on, not used in this function per se, for the sake of updating the recorder on what's on screen.</li><li>`main_window`: the Psychopy visual.Window object for the project, whose display will be changed.</li><li>`text_to_display`: a string containing the text to be displayed for the duration of the screen</li><li>`display_name`: a string indicating an identifiable name for this screen, to be provided to the recorder</li></ul>||

#### Miscellaneous Functions
|Function|Inputs|Outputs|
|---|---|---|
|`display_subj_ID_dialog`: a function that brings up a GUI input box to enter the participant's ID number in to||<ul><li>`subj_ID`: the provided ID number of the current participant</li></ul>|
|`get_images`: a function that, given the image file names, retrives them and gets them into a PsychoPy-appropriate format|<ul><li>`image_file_names`: a list of strings indicating the name of each stimuli within the `visualStims` folder</li><li>`image_size`: an integer indicating the desired size of each stimulus image in pixels (with the presumption of squares, so that this is both the width and height)</li><li>`checkmark_size`: an integer indicating the desired size of the checkmark image in pixels (again, both the width and height)</li><li>`repeat_icon_size`: an integer indicating the desired size of the repeat button image in pixels (again, both the width and height)</li><li>`main_window`: the Psychopy visual.Window object for the project, where each of these images will eventually be displayed</li></ul>|<ul><li>`images`: a list of the stimuli as ImageStim objects</li>`checkmarks`: a list of the checkmarks as ImageStim objects.  Though they appear identical, we need one checkmark ImageStim for each stimulus image.</li><li>`repeat_icon`: an ImageStim for the repeat button</li><li>`selection_box`: a PsychoPy Rect object for the box around the selected image</li></ul>|
|`get_random_image_order`: a function that gives a random ordering for the given number of stimuli images.  For example, if there are three stimuli to be displayed, it will randomly return one of [0,1,2], [0,2,1], [1,0,2], [1,2,0], [2,0,1] or [2,1,0].|<ul><li>`number_of_images`: an integer indicating how many images we are ordering</li></ul>|<ul><li>`randomly_ordered_list`: a list of length `number_of_images`, containing the integers from 0 to 1 - `number_of_images`, randomly ordered</li></ul>|
|`listen_for_quit`: a  function that checks if the quit button has been pressed.  The idea is that you would have a loop that calls this function repeatedly (maybe along with listening for other inputs). |<ul><li>`quit_function`: a function that will be called if a quit has been requested i.e. one that will cleanly exit the experiment</li></ul>||
|`listen_for_repeat`: a function that checks if the repeat button has been pressed.  The idea is that you would have a loop that calls this function repeatedly (maybe along with listening for other inputs). |<ul><li>`repeat_icon`: an ImageStim for the repeat button</li><li>`prev_mouse_location`: a list of coordinates (i.e. `[x,y]`) that saves where the mouse was last. This is needed in case you're using touch input.</li><li>`audio`: a PsychoPy sound.Sound object indicating the audio that should be played if a repetition was requested</li><li>`trial_clock`: a Psychopy core.Clock object associated with the present trial</li><li>`clicks`: a list recording each click. Each item in the list is itself a list containing a) a string identifying what was clicked, and b) a float indicating the time of the click in seconds (based on the `trial_clock`).  If the record button is used, we need to record that in this list.</li><li>`mouse`: the PsychoPy event.Mouse object for the whole project</li><li>`recorder`: the recorder object, an instance of Titta's `TalkToProLab` class, that is tracking the gaze.</li></ul>|<ul><li>`prev_mouse_location`: a list of coordinates (i.e. `[x,y]`) indicating the updated mouse location -- this needs to be updated for accurate monitoring of touch input|
|`play_sound`: a function for playing audio |<ul><li>`audio`: the PsychoPy sound.Sound object to be played</li><li>`recorder`: the recorder object, an instance of Titta's `TalkToProLab` class, that is tracking the gaze.</li></ul>||
|`set_image_positions`: a function that assigns the appropriate positions on screen for a set of images|<ul><li>`image_size`: an integer indicating the desired size of each stimulus image in pixels (with the presumption of squares, so that this is both the width and height)</li><li>`checkmark_size`: an integer indicating the desired size of the checkmark image in pixels (again, both the width and height)</li><li>`images`: a list of the stimuli as ImageStim objects</li>`checkmarks`: a list of the checkmarks as ImageStim objects.  Though they appear identical, we need one checkmark ImageStim for each stimulus image.</li><li>`repeat_icon`: an ImageStim for the repeat button</li><li>`IMAGE_OFFSET_FROM_EDGE`: an integer constant indicating the amount of space (in pixels) that should be left between images that are "against" the edge of the screen and the edge of the screen</li></ul>|<ul><li>`images`: a list of the stimuli as ImageStim objects, but with their positions set now</li>`checkmarks`: a list of the checkmarks as ImageStim objects, but with their positions set now</li><li>`repeat_icon`: an ImageStim for the repeat button, but with its position set now</li></ul>|
|`switch_displays`: a function for changing the current display content.  This should only be called if `EYE_TRACKING_ON` is `True`.  This function changes the module-level variables that track what the current display is and when it started being displayed.  We track these so that we can update TPL on what is on-screen.|<ul><li>`new_diplay_name`: a string indicating the name for referring to the display we're changing to.  This must be a key of the `media_info` dictionary in `eye_tracking_resources.py`.</li><li>`recorder`: the recorder object, an instance of Titta's `TalkToProLab` class, that is tracking the gaze.</li></ul>||

## `eye_tracking_resources.py`
This module contains functions related to the eye-tracking process, including communication with Titta (and by extension, Tobii Pro Lab).

#### A word on sending images to TPL
In the Analysis tab of TPL, we can play out the gaze recording such that we watch how the gaze moved around the screen.  In order to make this more useful, we can tell TPL about when different displays were being shown.  This is also useful because it will add events to our data export file that indicate whenever the display changed.  However, we should note that TPL only accepts images as occupying the whole display.  For this reason, we do not tell TPL about individual stimulus images, but instead give it images which are essentially screenshots approximating what is shown on screen at different times.  In this example experiment, we took screenshots of the fixation cross screen, an example buffer screen, and an example stimuli screen.  So we have to share these screenshot images with TPL and keep it updated whenever they change.

|Function|Inputs|Outputs|
|---|---|---|
|`add_AOI`: a function that adds an AOI (Area of Interest) to a particular display in TPL. The purpose of this is that it will automatically add columns to the data export file that indicate whether or not the gaze was in this area of the screen at a given time.|<ul><li>`pro_lab_connection`: an instance of Titta's `TalkToProLab` class indicating the connection to TPL that we are using to track the gaze</li><li>`display_name`: a string indicating the name for referring to the display we're adding an AOI to.  This must be a key of the `media_info` dictionary.</li><li>`AOI_name`: a string that will be used to identify the AOI in TPL and the data export file</li><li>`AOI_colour`: a string containing the six-digit hex colour code which will just be used in the visualization of the AOI in TPL's analysis tab</li><li>`vertices`: a tuple indicating the coordinates of the four corners of the AOI.  This is therefore a tuple containing four items, each of which is itself a tuple containing two integers.  The order of the four vertices is upper left, lower left, lower right, upper right.  The coordinates are expressed such that (0,0) is the upper left corner of the display (i.e. all values should be positive).</li></ul>||
|`add_image_to_recorder`: a function that tells TPL about a display image we are using.|<ul><li>`pro_lab_connection`: an instance of Titta's `TalkToProLab` class indicating the connection to TPL that we are using to track the gaze</li><li>`image_path`: a string indicating the filepath where the image is found</li><li>`image_name`: a string that will be used to identify the display in TPL and the data export file.  This will be used as a key in the `media_info` dictionary, for referencing later when we switch displays.</li></ul>||
|`calibrate_recorder`: a function that initiates eyetracker calibration|<ul><li>`main_window`: the Psychopy visual.Window object for the project</li><li>`mouse`: the PsychoPy event.Mouse object for the whole project</li><li>`pro_lab_connection`: an instance of Titta's `TalkToProLab` class indicating the connection to TPL that we are using to track the gaze</li></ul>||
|`close_recorder`: a function that cleanly ends the connection with TPL|<ul><li>`pro_lab_connection`: an instance of Titta's `TalkToProLab` class indicating the connection to TPL that we are using to track the gaze</li></ul>||
|`drift_check`: a function that checks whether there has been a drift in the gaze calibration, requiring recalibration.  Assuming that there is a fixation point being displayed and the participant is looking at it, we want to confirm whether the eyetracker is finding that their gaze is on that point.  We therefore check whether the gaze is within a certain zone on screen for a sufficient amount of time.  If a larger timeframe expires without this happening, then the drift check is failed.|<ul><li>`main_window`: the Psychopy visual.Window object for the project</li></ul>|<ul><li>`drift_check_passed`: a boolean which is `True` if the drift check succeeded i.e. we found the participant's gaze to be on target for enough time, and `False` otherwise|
|`compare_gaze_and_target`: a private method that helps with the drift check.  It accesses the current gaze data and checks whether it's within the target zone.|<ul><li>`main_window`: the Psychopy visual.Window object for the project</li></ul>|<ul><li>`on_target`: a boolean which is `True` if the current gaze was found to be within the target zone, and `False` if not|
|`finish_display`: a function that tells TPL we are finished with the current display|<ul><li>`start_time`: an integer indicating the time when this display began being displayed (in microseconds), as returned by the `TalkToProLab` `get_time_stamp()` function</li><li>`display_name`: a string indicating the name for referring to the display we're finished with for now.  This must be a key of the `media_info` dictionary.</li><li>`pro_lab_connection`: an instance of Titta's `TalkToProLab` class indicating the connection to TPL that we are using to track the gaze</li></ul>|<ul><li>`end_time`: an integer indicating the time when this display finished being displayed (in microseconds), as returned by the `TalkToProLab` `get_time_stamp()` function.  This is returned in case it will be used as the start time for the next display.  This prevents any time gaps between displays from TPL's perspective.</li></ul>|
|`record_event`: a function that tells TPL about any kind of event, in order to have it marked in the data export file (plus in the Analysis tab in TPL, if that's helpful)|<ul><li>`pro_lab_connection`: an instance of Titta's `TalkToProLab` class indicating the connection to TPL that we are using to track the gaze</li><li>`event_description`: a string indicating how you want to identify this event</li></ul>||
|`set_up_recorder`: a function that initializes and saves a connection with TPL|<ul><li>`main_window`: the Psychopy visual.Window object for the project</li><li>`mouse`: the PsychoPy event.Mouse object for the whole project</li><li>`participant_name`: a string indicating how the participant will be referred to in TPL.  Note that though this may be a kind of ID number, it is distinct from the participant ID that TPL generates as a unique identifier.</li></ul>|<ul><li>`pro_lab_connection`: an instance of Titta's `TalkToProLab` class indicating the connection to TPL that we are using to track the gaze</li></ul>|
|`start_recording_gaze`: a function that starts recording via the established connection to TPL|<ul><li>`pro_lab_connection`: an instance of Titta's `TalkToProLab` class indicating the connection to TPL that we are using to track the gaze</li></ul>||
|`stop_recording_gaze`: a function that stops the current recording by the established connection to TPL|<ul><li>`pro_lab_connection`: an instance of Titta's `TalkToProLab` class indicating the connection to TPL that we are using to track the gaze</li></ul>||

## `config.py`
This is where project-level constants are defined.  Various modules are expecting the following values to be defined:

|Constant name|Value|
|---|---|
|`EYE_TRACKING_ON`|a boolean indicating whether you want the experiment to run with or without including the eye-tracking steps.  This essentially allows a test mode where you can check how other parts of the experiment are working without worrying about the eye-tracking side.|
|`WINDOW_WIDTH`|an integer indicating the width of the screen the display will be shown on, in pixels.|
|`WINDOW_HEIGHT`|an integer indicating the height of the screen the display will be shown on, in pixels.|
|`USER_INPUT_DEVICE`|a string indicating the source of user input.  Currently supported values are 'mouse' or 'touch'.|
