import csv
from random import shuffle
from pathlib import *
from psychopy import core, event, monitors, sound, visual
from randomizer import latin_square
from config import *
from display_resources import check_for_input_on_images, clear_clicks_and_events, display_blank_screen, display_buffer_screen, display_fixation_cross_screen, display_subj_ID_dialog, display_text_screen,get_images, handle_input_on_stimulus, display_stimuli_screen, listen_for_quit, listen_for_repeat, play_sound, set_image_positions
from eye_tracking_resources import add_AOI, add_image_to_recorder, calibrate_recorder, close_recorder, drift_check, set_up_recorder, start_recording_gaze, stop_recording_gaze

# Global constants - the only variables defined here are those that need to be accessed by many functions
# These two are taken from read_me_TalkToProLab.py
# All I know is that they make the calibration work properly (rather than only calibrating a smaller central subarea of the screen)
SCREEN_WIDTH = 52.5  # cm
VIEWING_DIST = 63 #  # distance from eye to center of screen (cm)
IMAGE_SIZE = 425
REPEAT_ICON_SIZE = 100
IMAGE_OFFSET_FROM_EDGE = 20
SUPPORTED_IMAGE_NUMBERS = [1, 2, 3, 4] # Different numbers of images = different on-screen arrangements, so we only want quantities that we are prepared to arrange.


def main():
    # Global vars (to be accessible by all functions)
    global main_window
    global mouse
    global output_file
    global recorder

    # Begin with the dialog for inputting subject ID
    subjID = display_subj_ID_dialog()

    # *** SET-UP ***
    # Define objects for the main screen, mouse, output file and list of experimental items. Plus, start with a blank slate for clicks and events.
    monitor = monitors.Monitor('myMonitor')
    monitor.setWidth(SCREEN_WIDTH)
    monitor.setDistance(VIEWING_DIST)
    monitor.setSizePix([WINDOW_WIDTH, WINDOW_HEIGHT])
    main_window = visual.Window([WINDOW_WIDTH, WINDOW_HEIGHT], fullscr = True, allowGUI = True, monitor = monitor, units = 'pix', color = "white")
    mouse = event.Mouse(visible = True, win = main_window)
    output_file = create_output_file(subjID)
    experimental_items = get_experimental_items(subjID)
    clear_clicks_and_events(mouse)
    
    # Setting up the gaze recorder takes a few seconds, so let's begin displaying a loading screen here!
    display_text_screen(None, main_window, "Setting up...", None)
    if EYETRACKING_ON:
        recorder = set_up_recorder(main_window, mouse, str(subjID))
        add_images_to_recorder()
        start_recording_gaze(recorder)
    else:
        recorder = None

    # *** BEGIN EXPERIMENT ***
    # Display welcome screen until the user clicks
    display_buffer_screen(recorder, main_window, mouse, 'Boozhoo! Biindigen.', quit_experiment)

    # Run trials!
    practice_complete = False
    for trial_number, item_info in enumerate(experimental_items):
        print("\nTrial number:", trial_number, "\nTrial info:", item_info)

        # At the end of the practice session, notify the participant
        if not(practice_complete) and item_info["item_type"] != "Practice":
            practice_complete = True
            display_buffer_screen(recorder, main_window, mouse, 'Here is my end-of-practice text.', quit_experiment)

        # Reading from all .csv columns that start with "image" means we auto-detect different numbers of images
        image_file_names = [item_info[key] for key in item_info.keys() if key.startswith("image")]
        # Check that the number of images provided is supported
        if len(image_file_names) not in SUPPORTED_IMAGE_NUMBERS:
            print(f"\nERROR: Unsupported number of images ({len(image_file_names)}).  Supported numbers are {SUPPORTED_IMAGE_NUMBERS}.\n")
            quit_experiment()
        audio_file_name = item_info["audio"]
        print("Trial images:", image_file_names)
        
        response = trial(image_file_names, audio_file_name, main_window, mouse)
                
        # Record the data from the last trial
        output_line_contents = [str(subjID), str(trial_number), str(item_info["item_number"]), str(item_info["condition_number"]), str(response) + "\n"]
        output_file.write("\t".join(output_line_contents))
        output_file.flush()

    quit_experiment()

def trial(image_file_names, audio_file_name, main_window, mouse):
    CHECKMARK_SIZE = 100
    WAIT_TIME_BETWEEN_TRIALS = .75 # in seconds
    WAIT_TIME_BETWEEN_FIXATION_AND_STIMULI = .1
    WAIT_TIME_BEFORE_RECALIBRATING = 3
    WAIT_TIME_BETWEEN_STIMULI_AND_AUDIO = 4
    BUFFER_TEXT = 'Tanganan wii-majitaayan\n mezhinaatebiniwemagak.'
    
    trial_clock = core.Clock()

    # Get the audio to be played for the given trial.
    audio = sound.Sound(Path.cwd()/"audio"/str(audio_file_name))

    # Get the relevant images
    images, checkmarks, repeat_icon, selection_box = get_images(image_file_names, IMAGE_SIZE, CHECKMARK_SIZE, REPEAT_ICON_SIZE, main_window)
    # Determine the position of each image
    images, checkmarks, repeat_icon = set_image_positions(IMAGE_SIZE, CHECKMARK_SIZE, images, checkmarks, repeat_icon, IMAGE_OFFSET_FROM_EDGE)

    # *** BEGIN TRIAL ***
    # Add a wait time before the start of each new trial, with a blank screen
    display_blank_screen(recorder, main_window)
    core.wait(WAIT_TIME_BETWEEN_TRIALS)
    
    # Display screen between trials so participant can indicate when ready
    display_buffer_screen(recorder, main_window, mouse, BUFFER_TEXT, quit_experiment)

    # Drift check sequence
    if EYETRACKING_ON:
        display_fixation_cross_screen(recorder, main_window)
        if not drift_check(main_window):
            display_text_screen(recorder, main_window, "Re-calibration needed. Entering calibration...", "buffer")
            core.wait(WAIT_TIME_BEFORE_RECALIBRATING)
            calibrate_recorder(main_window, mouse, recorder)
        # Pause between displaying the fixation cross and displaying the stimuli
        core.wait(WAIT_TIME_BETWEEN_FIXATION_AND_STIMULI)
    
    # Display the images, and then pause before the audio is played
    display_stimuli_screen(recorder, main_window, images + [repeat_icon])
    # core.wait(WAIT_TIME_BETWEEN_STIMULI_AND_AUDIO)
          
    # Prepare for clicks, play the audio file, and start the timer - the user may interact starting now!
    clear_clicks_and_events(mouse)
    clicks = []
    image_clicked = None
    prev_mouse_location = mouse.getPos()
    play_sound(audio, recorder)
    trial_clock.reset()

    # We wait in this loop until we have a first click on one of the 3 images
    while not image_clicked:
        # Always be listening for a command to quit the program, or repeat the audio          
        listen_for_quit(quit_experiment)
        prev_mouse_location = listen_for_repeat(repeat_icon, prev_mouse_location, audio, trial_clock, clicks, mouse, recorder)
        image_clicked, prev_mouse_location = check_for_input_on_images(mouse, images, prev_mouse_location)

    # Now, we've received a first click on one of the images
    checkmark = handle_input_on_stimulus(image_clicked, images, checkmarks, selection_box, repeat_icon, trial_clock, clicks, recorder, main_window)

    # Now we wait in this loop until the checkmark is ultimately clicked
    checkmark_clicked = False
    while not checkmark_clicked:
        
        # Always be listening for a command to quit the program, or repeat the audio  
        listen_for_quit(quit_experiment)
        prev_mouse_location = listen_for_repeat(repeat_icon, prev_mouse_location, audio, trial_clock, clicks, mouse, recorder)
        
        # Always listening for a click on an image
        image_clicked, prev_mouse_location = check_for_input_on_images(mouse, images, prev_mouse_location)
        if image_clicked:
            checkmark = handle_input_on_stimulus(image_clicked, images, checkmarks, selection_box, repeat_icon, trial_clock, clicks, recorder, main_window)

        # Always listening for a click on the checkmark
        checkmark_clicked, prev_mouse_location = check_for_input_on_images(mouse, [checkmark], prev_mouse_location)
           
    # Once we reach here, the check has been clicked (i.e. the trial is over)
    trial_duration = trial_clock.getTime()
    response = ["checkmark", trial_duration]
    clicks.append(response)

    positions = [image.pos for image in images]
    return positions, clicks

# *** Functions used inside main() ***

# Create output file to save data
def create_output_file(subj_ID):
    output_file = open("Wiigwaas-Exp-" + str(subj_ID) + ".txt", "w") # Open output file channel for editing
    output_file.write('subj\ttrial\titem\tcond\tclicks\n') # Add header
    return output_file

def get_experimental_items(subjID):
    EXP_ITEMS_FILE_NAME = './experimental_items/experimental_items_small.csv'
    NUMBER_OF_CONDITIONS = 4

    # Use subject number to get a sort-of random offset used to determine the conditions for each experimental item.
    current_offset = subjID % NUMBER_OF_CONDITIONS + ((not subjID % NUMBER_OF_CONDITIONS) * NUMBER_OF_CONDITIONS)
	
    # Load experimental_items file (store its contents as a list of rows-as-dictionaries)
    with open(EXP_ITEMS_FILE_NAME) as csv_file: 
        stim_file = csv.DictReader(csv_file)
        stim_list = [item for item in stim_file]
    
    experimental_items = []
    # First, get practice items to the beginning
    stim_list_sans_practice = []
    for stim in stim_list:
        stim_type = stim["item_type"]
        if stim_type == "Practice":
            experimental_items.append(stim)
        else: # Filler and real experimental items
            stim_list_sans_practice.append(stim)
    shuffle(experimental_items) # Randomize order of practice trials

    # Randomize the filler/experimental items
    experimental_items.extend(latin_square(current_offset, stim_list_sans_practice))
    print("All trials:", experimental_items)
    return experimental_items

# *** Functions used inside trial() ***

# Give the recorder info about what images are on the screen, so that we can track gazes within those image areas
def add_images_to_recorder():
    # Add an overall background image (at present this is really just a placeholder)
    stimuli_image_path = "C:\\Users\\Anna\\Documents\\Wiigwaas\\screen_images\\sample_trial_screen.jpeg"
    fixation_cross_image_path = "C:\\Users\\Anna\\Documents\\Wiigwaas\\screen_images\\fixation_cross_screen.jpeg"
    buffer_image_path = "C:\\Users\\Anna\\Documents\\Wiigwaas\\screen_images\\buffer_screen.jpeg"
    blank_image_path = "C:\\Users\\Anna\\Documents\\Wiigwaas\\screen_images\\blank_screen.jpeg"
    add_image_to_recorder(recorder, stimuli_image_path, "stimuli")
    add_image_to_recorder(recorder, fixation_cross_image_path, "fixation_cross")
    add_image_to_recorder(recorder, buffer_image_path, "buffer")
    add_image_to_recorder(recorder, blank_image_path, "blank")

    # Add an AOI (area of interest) for each image
    AOI_SIZE = IMAGE_SIZE + IMAGE_OFFSET_FROM_EDGE
    LEFT_EDGE = 0
    RIGHT_EDGE = WINDOW_WIDTH
    X_MIDPOINT = WINDOW_WIDTH / 2
    TOP_EDGE = 0
    BOTTOM_EDGE = WINDOW_HEIGHT

    aoi_name = 'upper_left'
    aoi_color =  'AA0000'
    vertices = ((LEFT_EDGE, TOP_EDGE), (LEFT_EDGE, AOI_SIZE), (LEFT_EDGE + AOI_SIZE, AOI_SIZE), (LEFT_EDGE + AOI_SIZE, TOP_EDGE))
    add_AOI(recorder, 'stimuli', aoi_name, aoi_color, vertices)

    aoi_name = 'upper_right'
    aoi_color = '00AA00'
    vertices = ((RIGHT_EDGE - AOI_SIZE, TOP_EDGE), (RIGHT_EDGE - AOI_SIZE, TOP_EDGE + AOI_SIZE), (RIGHT_EDGE, TOP_EDGE + AOI_SIZE), (RIGHT_EDGE, TOP_EDGE))
    add_AOI(recorder, 'stimuli', aoi_name, aoi_color, vertices)

    aoi_name = 'lower_middle'
    aoi_color = '0000AA'
    vertices = ((X_MIDPOINT - AOI_SIZE/2,  BOTTOM_EDGE - AOI_SIZE), (X_MIDPOINT - AOI_SIZE/2, BOTTOM_EDGE), (X_MIDPOINT + AOI_SIZE/2, BOTTOM_EDGE), (X_MIDPOINT + AOI_SIZE/2, BOTTOM_EDGE - AOI_SIZE))
    add_AOI(recorder, 'stimuli', aoi_name, aoi_color, vertices)

# This is used inside both main and trial (as the user may quit during a trial)
def quit_experiment():
    display_text_screen(recorder, main_window, "Quitting...", None)
    
    # Quit gracefully
    if EYETRACKING_ON:
        stop_recording_gaze(recorder)
        close_recorder(recorder)
    output_file.close()
    core.quit()

### Run Experiment ###
main()
