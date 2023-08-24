from random import randint
from pathlib import *
from psychopy import core, event, gui, visual
from config import *
# Ideally we should minimze imports from here, but there is some overlap between what's on screen and what TPL needs to know.
from eye_tracking_resources import finish_displaying_stimulus, record_event

# These need to be updated throughout the experiment, to send messages about what is being shown on screen
current_display = None
current_display_start_time = None

# A helper method that calls another method specific to the set input type
def check_for_input_on_images(mouse, images, prev_mouse_location):
    if USER_INPUT_DEVICE == 'mouse':
        clicked_image, prev_mouse_location = _check_for_click_on_images(mouse, images, prev_mouse_location)
    elif USER_INPUT_DEVICE == 'touch':
        clicked_image, prev_mouse_location = _check_for_tap_on_images(mouse, images, prev_mouse_location)
    else:
        print("Error: User input device is not set to a valid value (mouse or touch). Quitting...")
        core.quit()
    return clicked_image, prev_mouse_location

# Given a list of images, returns the one that is being clicked (or None)
# Hold for the duration of the click - so that when this function ends, the click is over
def _check_for_click_on_images(mouse, images, prev_mouse_location):
    clicked_image = None
    for image in images:
        if mouse.isPressedIn(image):
            clicked_image = image
            while any(mouse.getPressed()):
                pass
            # Not necessary, but keeps things consistent with the use of checkForTap
            prev_mouse_location = mouse.getPos()
    return clicked_image, prev_mouse_location

# Checks for a single tap on an image
# Does this by asking: has the "mouse" moved? (= yes if a tap was received)
# And: If so, is the "mouse" within the image?
def _check_for_tap_on_images(mouse, images, prev_mouse_location):
    clicked_image = None
    mouse_location = mouse.getPos()
    # If the mouse moved... (check x and y coords)
    if not(mouse_location[0] == prev_mouse_location[0] and mouse_location[1] == prev_mouse_location[1]):
        # If the mouse is within one of the images...
        for image in images:
            if image.contains(mouse):
                clicked_image = image
                prev_mouse_location = mouse_location # Update for the next check
    return clicked_image, prev_mouse_location

# A helper method that calls another method specific to the set input type
def check_for_input_anywhere(mouse, prev_mouse_location):
    if USER_INPUT_DEVICE == 'mouse':
        input_received, prev_mouse_location = _check_for_click_anywhere(mouse, prev_mouse_location)
    elif USER_INPUT_DEVICE == 'touch':
        input_received, prev_mouse_location = _check_for_tap_anywhere(mouse, prev_mouse_location)
    else:
        print("Error: User input device is not set to a valid value (mouse or touch). Quitting...")
        core.quit()
    return input_received, prev_mouse_location

def _check_for_click_anywhere(mouse, prev_mouse_location):
    clicked = False
    if any(mouse.getPressed()):
        clicked = True
        prev_mouse_location = mouse.getPos()
        while any(mouse.getPressed()): # Wait for the click to end before proceeding
            pass
    
    return clicked, prev_mouse_location

def _check_for_tap_anywhere(mouse, prev_mouse_location):
    tapped = False
    mouse_location = mouse.getPos()
    # If the mouse moved... (check x and y coords)
    if not(mouse_location[0] == prev_mouse_location[0] and mouse_location[1] == prev_mouse_location[1]):
        tapped = True

    prev_mouse_location = mouse_location

    return tapped, prev_mouse_location

def clear_clicks_and_events(mouse):
    mouse.clickReset()
    event.clearEvents()

def display_blank_screen(recorder, media_info, main_window):
    if EYETRACKING_ON:
        switch_displays('blank', recorder, media_info)
    main_window.flip()

# Displays a buffer screen with given text, and only proceeds once the user clicks
def display_buffer_screen(recorder, media_info, main_window, mouse, buffer_text, quit_function):
    display_text_screen(recorder, media_info, main_window, buffer_text, "buffer")
    input_received, prev_mouse_location = check_for_input_anywhere(mouse, mouse.getPos())
    while not input_received: # Wait for user input (anywhere on screen)
        listen_for_quit(quit_function) # Allow the user to quit at this stage, too
        input_received, prev_mouse_location = check_for_input_anywhere(mouse, prev_mouse_location)

# Displays a fixation cross on the screen for 1500ms 
def display_fixation_cross_screen(recorder, media_info, main_window, mouse):
    if EYETRACKING_ON:
        switch_displays('fixation_cross', recorder, media_info)
    fixation_screen = visual.TextStim(
        main_window,
        text = '+',
        pos = (0.0, 0.0),
        bold = True,
        height = WINDOW_HEIGHT / 10,
        color = "black")
    fixation_screen.draw()
    main_window.flip()

def display_stimuli(recorder, media_info, stimuli_list, main_window):
    if EYETRACKING_ON:
        switch_displays('stimuli', recorder, media_info)
    for stimulus in stimuli_list:
        stimulus.draw()
    main_window.flip()

# Displays a dialog box to get subject number
def display_subj_ID_dialog():
    gui_box = gui.Dlg()
    gui_box.addField("Subject ID:")
    gui_box.show()
    subj_ID = int(gui_box.data[0])
    return subj_ID

# Displays a screen with given text (how to proceed from this screen is not a part of this function!)
# displayName can be None (if this is not a display for the recording process, e.g. the quitting screen)
def display_text_screen(recorder, media_info, main_window, text_to_display, display_name):
    if EYETRACKING_ON:
        switch_displays(display_name, recorder, media_info)
    text_screen = visual.TextStim(
        main_window,
        text = text_to_display,
        pos = (0.0, 0.0),
        height = WINDOW_HEIGHT / 20,
        wrapWidth = WINDOW_WIDTH,
        color = "black")
    text_screen.draw()
    main_window.flip()
    
# Get the images to be displayed for the given trial.
def get_images(image_file_names, image_size, checkmark_size, repeat_icon_size, main_window):
    number_of_images = len(image_file_names)

    # Create an ImageStim object for each image stimuli, and a unique check object for each image - even though they're all the same check image, they'll end up having different positions
    images = []
    checks = []
    for i in range(0, number_of_images):
        images.append(visual.ImageStim(win = main_window, image = Path.cwd()/"visualStims"/str(image_file_names[i]), units = "pix", size = image_size))
        checks.append(visual.ImageStim(win = main_window, image = Path.cwd()/"checkmark.png", units = "pix", size = checkmark_size))

    repeat_icon = visual.ImageStim(win = main_window, image = Path.cwd()/"repeat.png", units = "pix", size = repeat_icon_size)
    
    selection_box = visual.Rect(win = main_window, lineWidth = 2.5, lineColor = "#7AC043", fillColor = None, units = "pix", size = image_size)

    return images, checks, repeat_icon, selection_box

def get_random_image_order(number_of_images):
    # We can think of the images as each having a number index, e.g. with three images, agent = 0, patient = 1, distractor = 2
    # So the images are numbered 0 through numImages - 1. We want a list that tells us their order.
    # So we want to randomize the order of the numbers 0 through numImages - 1.
    ordered_list = list(range(0, number_of_images)) # A list of all the image indexes, but in ascending order
    randomly_ordered_list = []

    for i in range(0, number_of_images):
       random_num = randint(0, len(ordered_list) - 1) # Choose randomly, from however many numbers we have left to choose
       randomly_ordered_list.append(ordered_list.pop(random_num))

    return randomly_ordered_list

def handle_stimuli_click(image_clicked, images, checks, selection_box, repeat_icon, trial_clock, clicks, recorder, media_info, main_window):
    number_of_images = len(images)

    # Determine the names of the images we're dealing with. These name lists match their order in the experimental items input file!
    ONE_IMAGE_NAME = ["agent"]
    TWO_IMAGE_NAMES = ["agent", "patient"]
    THREE_IMAGE_NAMES = ["agent", "patient", "distractor"]
    FOUR_IMAGE_NAMES = ["agent", "patient", "distractorA", "distractorB"]
    NAME_LISTS = {
        1: ONE_IMAGE_NAME,
        2: TWO_IMAGE_NAMES,
        3: THREE_IMAGE_NAMES,
        4: FOUR_IMAGE_NAMES
    }
    assert number_of_images in NAME_LISTS.keys()
    image_names = NAME_LISTS[number_of_images]

    # Figure out which image was clicked
    trial_duration = trial_clock.getTime()
    selection_box.setPos(image_clicked.pos)
    for i, image in enumerate(images):
        if image_clicked == image:
            pic = image_names[i]
            check = checks[i]

    response = [pic, trial_duration]
    clicks.append(response)

    # Re-draw to include the selection box and checkmark
    display_stimuli(recorder, media_info, images + [repeat_icon, selection_box, check], main_window)
    
    return check

# Listens for a keyboard shortcut that tells us to quit the experiment - if detected, it runs the given quit routine
def listen_for_quit(quit_function):
    quit_key = 'escape'
    keys = event.getKeys()
    if quit_key in keys:
        quit_function()

def listen_for_repeat(repeat_icon, prev_mouse_location, audio, trial_clock, clicks, mouse, recorder):
    repeat_clicked, prev_mouse_location = check_for_input_on_images(mouse, [repeat_icon], prev_mouse_location)
    if repeat_clicked:
        if EYETRACKING_ON:
            record_event(recorder, "RepeatPressed")
        play_sound(audio, recorder)
        pic = "replay"
        trial_duration = trial_clock.getTime()
        response = [pic, trial_duration]
        clicks.append(response)

    return prev_mouse_location

def play_sound(audio, recorder):
    if EYETRACKING_ON:
        record_event(recorder, "AudioStart")
    audio.play()

    # Note that setPos defines the position of the image's /centre/, and screen positions are determined based on the /centre/ of the screen being (0,0)
def set_image_positions(image_size, checkmark_size, images, checkmarks, repeat_icon, IMAGE_OFFSET_FROM_EDGE):
    number_of_images = len(images)

    # The repeat button's position is always the same, no randomization needed
    buffer_size = min(WINDOW_WIDTH, WINDOW_HEIGHT) / 15
    repeat_icon.setPos([-WINDOW_WIDTH / 2 + buffer_size,-WINDOW_HEIGHT / 2 + buffer_size])

    # Calculate positions for the images relative to the window
    x_spacing = (WINDOW_WIDTH / 2) - (image_size / 2) #i.e. distance from centre of screen to centre of image in order for the image to be against one side of the screen
    y_spacing = (WINDOW_HEIGHT / 2) - (image_size / 2)
    left = -x_spacing + IMAGE_OFFSET_FROM_EDGE
    right = x_spacing - IMAGE_OFFSET_FROM_EDGE
    bottom = -y_spacing + IMAGE_OFFSET_FROM_EDGE
    top = y_spacing - IMAGE_OFFSET_FROM_EDGE
    centre = 0
    # Position the checkmarks just above/below the image. This offset should be added/subtracted from the corresponding image's position.
    checkmark_offset = image_size / 2 + checkmark_size / 2

    # Randomly determine the images' order (and therfore, positions)
    random_ordering_of_images = get_random_image_order(number_of_images)

    # Determine the image positions we'll be using, based on the # of images
    ONE_POSITION = [[centre, centre]]
    TWO_POSITIONS = [[left, centre], [right, centre]]
    THREE_POSITIONS = [[left, top], [right, top], [centre, bottom]]
    FOUR_POSITIONS = [[left, top], [right, top], [left, bottom], [right, bottom]]
    POSITION_LISTS = {
        1: ONE_POSITION,
        2: TWO_POSITIONS,
        3: THREE_POSITIONS,
        4: FOUR_POSITIONS
    }
    assert number_of_images in POSITION_LISTS.keys()
    image_positions = POSITION_LISTS[number_of_images]

    # Now set their positions based on that random order!
    for i, image_position in enumerate(image_positions):
        images[random_ordering_of_images[i]].setPos(image_position)
        # Put the check below the image UNLESS the image is already at the bottom of the screen, in which case put the check above the image
        checkmarks[random_ordering_of_images[i]].setPos([image_position[0], image_position[1] - checkmark_offset if image_position[1] != bottom else image_position[1] + checkmark_offset])

    return images, checkmarks, repeat_icon

# Either the new or current display can be None, indicating this is the last or first display
# If new_display_name = None, we only finish with the previous display, we don't add a new one
# If current_display = None, we do not finish any previous display (because we're saying there isn't one!), we merely note the start time of this new screen
# If both are None, we are neither beginning nor finishing with a screen (i.e. this is a dummy call - we don't want TPL to know about this display at all)
def switch_displays(new_display_name, recorder, media_info):
    global current_display
    global current_display_start_time
    # Store the start time for the new display (and finish with the old one, if there was one).
    if current_display == None and new_display_name == None: # No switch at all
        pass
    elif current_display == None: # No previous display, but we're starting a new one
        current_display_start_time = int((recorder.get_time_stamp())['timestamp'])
    else: # We are finishing with a previous display
        current_display_start_time = finish_displaying_stimulus(current_display_start_time, media_info[current_display], recorder)
    current_display = new_display_name # Update the current display
