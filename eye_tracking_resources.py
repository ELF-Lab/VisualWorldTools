from psychopy.iohub import launchHubServer
from Titta.titta import Titta
from Titta.titta.TalkToProLab import TalkToProLab
import datetime
from config import WINDOW_HEIGHT, WINDOW_WIDTH

participant_ID = None
recording_ID = None
tracker = None
# Dictionary containing key-value pairs of screen names and media IDS, e.g. {"buffer": 8273891}
media_info = None

# Drift-check related constants, for specifying the acceptable fixation zone
# These are not defined in-function, because it is called over and over
# All measurements in pixels
FIXATION_ZONE_SIZE = 40 # How far from the centre the gaze can be, either direction along both axes
LEFT_FIXATION_BOUNDARY = WINDOW_WIDTH / 2 - FIXATION_ZONE_SIZE
RIGHT_FIXATION_BOUNDARY = WINDOW_WIDTH / 2 + FIXATION_ZONE_SIZE
TOP_FIXATION_BOUNDARY = WINDOW_HEIGHT / 2 - FIXATION_ZONE_SIZE
BOTTOM_FIXATION_BOUNDARY = WINDOW_HEIGHT / 2 + FIXATION_ZONE_SIZE

def add_AOI(pro_lab_conection, display_name, AOI_name, AOI_colour, vertices):
    tag_name = 'test_tag'
    group_name = 'test_group'

    pro_lab_conection.add_aois_to_image(media_info[display_name]['media_id'], AOI_name, AOI_colour, vertices, tag_name = tag_name, group_name = group_name)

# Tell TPL what image we're using during a gaze recording
def add_image_to_recorder(pro_lab_conection, image_path, image_name):
    global media_info
    media_type = "image"
    media_info.update({image_name: pro_lab_conection.upload_media(image_path, media_type)})

def calibrate_recorder(main_window, mouse, pro_lab_conection):
    record_event(pro_lab_conection, "CalibrationStart")
    tracker.calibrate(main_window)
    # For some reason, this calibration leaves the mouse invisible. So make it visible again before returning.
    mouse.setVisible(1)

def close_recorder(pro_lab_conection):
    # We need to explicitly end the thread that was maintaining the connection
    # Titta is set up to do this in their finalize_recording method, but in this case we are not recording anything yet
    pro_lab_conection.endConnectionThread()
    pro_lab_conection.disconnect()

def drift_check(main_window):
    TIME_BEFORE_RECALIBRATING = 10 # seconds
    TIME_REQUIRED_FOR_FIXATION = 0.8

    tracker.start_drift_check()
    drift_check_start_time = datetime.datetime.now()
    drift_check_passed = False
    # For a given period, wait to see if they are looking at the fixation cross
    while (datetime.datetime.now() - drift_check_start_time).seconds < TIME_BEFORE_RECALIBRATING and not drift_check_passed:
        # Check if current gaze position is within the range considered to be on the fixation cross
        gaze_on_target = _compare_gaze_and_target(main_window)
        if gaze_on_target:
            fixation_start_time = datetime.datetime.now()
            # For the target fixation duration, check if they continue to look at the target
            # (While still checking that the overall drift check time allotment isn't up!)
            while (datetime.datetime.now() - fixation_start_time).seconds < TIME_REQUIRED_FOR_FIXATION and gaze_on_target and (datetime.datetime.now() - drift_check_start_time).seconds < TIME_BEFORE_RECALIBRATING:
                gaze_on_target = _compare_gaze_and_target(main_window)

        # If the var is True at this point, then it must have remained True for long enough to consider that a satisfactory fixation!
        if gaze_on_target:
            drift_check_passed = True

    tracker.stop_drift_check()

    return drift_check_passed

# Private method to help with gaze calculations
def _compare_gaze_and_target(main_window):
    on_target = False

    gazePos = tracker.get_gaze_data(main_window)
    x_gaze_pos_left = gazePos[0][0][0]
    y_gaze_pos_left = gazePos[0][0][1]
    x_gaze_pos_right = gazePos[1][0][0]
    y_gaze_pos_right = gazePos[1][0][1]

    if ((x_gaze_pos_left > LEFT_FIXATION_BOUNDARY and x_gaze_pos_left < RIGHT_FIXATION_BOUNDARY and y_gaze_pos_left > TOP_FIXATION_BOUNDARY and y_gaze_pos_left < BOTTOM_FIXATION_BOUNDARY) and
       (x_gaze_pos_right > LEFT_FIXATION_BOUNDARY and x_gaze_pos_right < RIGHT_FIXATION_BOUNDARY and y_gaze_pos_right > TOP_FIXATION_BOUNDARY and y_gaze_pos_right < BOTTOM_FIXATION_BOUNDARY)):
        on_target = True

    return on_target

# We need to tell TPL when we're done with the relevant display
def finish_display(start_time, display_name, pro_lab_conection):
    end_time = int((pro_lab_conection.get_time_stamp())['timestamp'])
    if recording_ID: # If there's a relevant recording!
        pro_lab_conection.send_stimulus_event(recording_ID, start_timestamp = str(start_time), media_id = media_info[display_name]['media_id'], end_timestamp = end_time)
    return end_time

def record_event(pro_lab_conection, event_description):
    if pro_lab_conection and recording_ID: # Only if we've actually started recording etc.
        pro_lab_conection.send_custom_event(recording_ID, event_description)

# Note that participant_name should be a string
def set_up_recorder(main_window, mouse, participant_name):
    global participant_ID
    global tracker
    global media_info

    # Specify the kind of eyetracker we are using, and an identifier for the participant
    settings = Titta.get_defaults("Tobii Pro Fusion")
    settings.FILENAME = participant_name

    # Create the eyetracker object (doesn't actually interact with the eyetracker itself here, just preparing for TPL)
    tracker = Titta.Connect(settings)
    tracker.init()

    # Create the connection with TPL
    pro_lab_conection = TalkToProLab(project_name = None, dummy_mode = False)
    participant_ID = (pro_lab_conection.add_participant(participant_name))['participant_id']

    calibrate_recorder(main_window, mouse, pro_lab_conection)

    media_info = {}

    return pro_lab_conection

def start_recording_gaze(pro_lab_conection):
    global recording_ID
    # Check that Lab is ready to start a recording
    state = pro_lab_conection.get_state()
    assert state['state'] == 'ready', state['state']

    ## Start recording (Note: you have to click on the Record Tab first!)
    recording = pro_lab_conection.start_recording("image_viewing", participant_ID, screen_width=1920, screen_height=1080)
    recording_ID = recording["recording_id"]

def stop_recording_gaze(pro_lab_conection):
    pro_lab_conection.stop_recording()
    pro_lab_conection.finalize_recording(recording_ID)

# **************
# This function is not being used currently - it is for eye-tracking with Tobii directly, rather than via Tobii Pro Lab.
def set_up_eye_tracker(main_window):
    iohub_config = {'eyetracker.hw.tobii.EyeTracker': {'name': 'tracker', 'calibration': {'type': 'THREE_POINTS'}}}
    io = launchHubServer(window = main_window, **iohub_config)
    eye_tracker = io.getDevice('tracker')

    return eye_tracker
# **************
