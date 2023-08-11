from psychopy.iohub import launchHubServer
from Titta.titta import Titta
from Titta.titta.TalkToProLab import TalkToProLab
import datetime
from config import WINDOW_HEIGHT, WINDOW_WIDTH

participantID = None
recordingID = None
tracker = None

# All measurements in pixels
FIXATION_ZONE_SIZE = 40 # How far from the centre the gaze can be, either direction along both axes
LEFT_FIXATION_BOUNDARY = WINDOW_WIDTH / 2 - FIXATION_ZONE_SIZE
RIGHT_FIXATION_BOUNDARY = WINDOW_WIDTH / 2 + FIXATION_ZONE_SIZE
TOP_FIXATION_BOUNDARY = WINDOW_HEIGHT / 2 - FIXATION_ZONE_SIZE
BOTTOM_FIXATION_BOUNDARY = WINDOW_HEIGHT / 2 + FIXATION_ZONE_SIZE

def addAOI(proLabConnection, image_id, aoi_name, aoi_color, vertices):
    tag_name = 'test_tag'
    group_name = 'test_group'

    proLabConnection.add_aois_to_image(image_id, aoi_name, aoi_color, vertices, tag_name = tag_name, group_name = group_name)

# Tell TPL what image we're using during a gaze recording
def addImageToRecorder(proLabConnection, media_info, imagePath, imageName):
    media_type = "image"
    media_info.update({imageName: proLabConnection.upload_media(imagePath, media_type)})

    return media_info

def calibrateRecorder(mainWindow, mouse, proLabConnection):
    recordEvent(proLabConnection, "CalibrationStart")
    tracker.calibrate(mainWindow)
    # For some reason, this calibration leaves the mouse invisible. So make it visible again before returning.
    mouse.setVisible(1)

def closeRecorder(proLabConnection):
    # We need to explicitly end the thread that was maintaining the connection
    # Titta is set up to do this in their finalize_recording method, but in this case we are not recording anything yet
    proLabConnection.endConnectionThread()
    proLabConnection.disconnect()

def driftCheck(mainWindow):
    TIME_BEFORE_RECALIBRATING = 10 # seconds
    TIME_REQUIRED_FOR_FIXATION = 0.8

    tracker.start_drift_check()
    driftCheckStartTime = datetime.datetime.now()
    driftCheckPassed = False
    # For a given period, wait to see if they are looking at the fixation cross
    while (datetime.datetime.now() - driftCheckStartTime).seconds < TIME_BEFORE_RECALIBRATING and not driftCheckPassed:
        # Check if current gaze position is within the range considered to be on the fixation cross
        gazeOnTarget = _compareGazeAndTarget(mainWindow)
        if gazeOnTarget:
            fixationStartTime = datetime.datetime.now()
            # For the target fixation duration, check if they continue to look at the target
            # (While still checking that the overall drift check time allotment isn't up!)
            while (datetime.datetime.now() - fixationStartTime).seconds < TIME_REQUIRED_FOR_FIXATION and gazeOnTarget and (datetime.datetime.now() - driftCheckStartTime).seconds < TIME_BEFORE_RECALIBRATING:
                gazeOnTarget = _compareGazeAndTarget(mainWindow)

        # If the var is True at this point, then it must have remained True for long enough to consider that a satisfactory fixation!
        if gazeOnTarget:
            driftCheckPassed = True

    tracker.stop_drift_check()

    return driftCheckPassed

# Private method to help with gaze calculations
def _compareGazeAndTarget(mainWindow):
    onTarget = False

    gazePos = tracker.get_gaze_data(mainWindow)
    xGazePosLeft = gazePos[0][0][0]
    yGazePosLeft = gazePos[0][0][1]
    xGazePosRight = gazePos[1][0][0]
    yGazePosRight = gazePos[1][0][1]

    if ((xGazePosLeft > LEFT_FIXATION_BOUNDARY and xGazePosLeft < RIGHT_FIXATION_BOUNDARY and yGazePosLeft > TOP_FIXATION_BOUNDARY and yGazePosLeft < BOTTOM_FIXATION_BOUNDARY) and
       (xGazePosRight > LEFT_FIXATION_BOUNDARY and xGazePosRight < RIGHT_FIXATION_BOUNDARY and yGazePosRight > TOP_FIXATION_BOUNDARY and yGazePosRight < BOTTOM_FIXATION_BOUNDARY)):
        onTarget = True

    return onTarget

# We need to tell TPL when we're doing with the relevant image
def finishDisplayingStimulus(startTime, mediaItem, proLabConnection):
    endTime = int((proLabConnection.get_time_stamp())['timestamp'])
    proLabConnection.send_stimulus_event(recordingID, start_timestamp = str(startTime), media_id = mediaItem['media_id'], end_timestamp = endTime)
    return endTime

def recordEvent(proLabConnection, eventDesc):
    if proLabConnection and recordingID: # Only if we've actually started recording etc.
        proLabConnection.send_custom_event(recordingID, eventDesc)

# Note that participantName should be a string
def setUpRecorder(mainWindow, mouse, participantName):
    global participantID
    global tracker

    # Specify the kind of eyetracker we are using, and an identifier for the participant
    settings = Titta.get_defaults("Tobii Pro Fusion")
    settings.FILENAME = participantName

    # Create the eyetracker object (doesn't actually interact with the eyetracker itself here, just preparing for TPL)
    tracker = Titta.Connect(settings)
    tracker.init()

    # Create the connection with TPL
    proLabConnection = TalkToProLab(project_name = None, dummy_mode = False)
    participantID = (proLabConnection.add_participant(participantName))['participant_id']

    calibrateRecorder(mainWindow, mouse, proLabConnection)

    return proLabConnection

def startRecordingGaze(proLabConnection):
    global recordingID
    # Check that Lab is ready to start a recording
    state = proLabConnection.get_state()
    assert state['state'] == 'ready', state['state']

    ## Start recording (Note: you have to click on the Record Tab first!)
    recording = proLabConnection.start_recording("image_viewing", participantID, screen_width=1920, screen_height=1080)
    recordingID = recording["recording_id"]

def stopRecordingGaze(proLabConnection):
    proLabConnection.stop_recording()
    proLabConnection.finalize_recording(recordingID)

# **************
# This function is not being used currently - it is for eye-tracking with Tobii directly, rather than via Tobii Pro Lab.
def setUpEyeTracker(mainWindow):
    iohub_config = {'eyetracker.hw.tobii.EyeTracker': {'name': 'tracker', 'calibration': {'type': 'THREE_POINTS'}}}
    io = launchHubServer(window = mainWindow, **iohub_config)
    eyeTracker = io.getDevice('tracker')

    return eyeTracker
# **************
