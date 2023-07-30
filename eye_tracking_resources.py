from psychopy.iohub import launchHubServer
from Titta.titta import Titta
from Titta.titta.TalkToProLab import TalkToProLab
import datetime

participantID = None
tracker = None

def addAOI(ttl, image_id, aoi_name, aoi_color, vertices):
    tag_name = 'test_tag'
    group_name = 'test_group'

    ttl.add_aois_to_image(image_id, aoi_name, aoi_color, vertices, tag_name = tag_name, group_name = group_name)

# Tell TPL what image we're using during a gaze recording
def addImageToRecorder(ttl, media_info, imagePath, imageName):
    media_type = "image"
    media_info.update({imageName: ttl.upload_media(imagePath, media_type)})

    return media_info

def calibrateRecorder(tracker, mainWindow, mouse):
    tracker.calibrate(mainWindow)
    # For some reason, this calibration leaves the mouse invisible. So make it visible again before returning.
    mouse.setVisible(1)

def closeRecorder(ttl):
    # We need to explicitly end the thread that was maintaining the connection
    # Titta is set up to do this in their finalize_recording method, but in this case we are not recording anything yet
    ttl.endConnectionThread()
    ttl.disconnect()

def driftCheck(mainWindow, left, right, top, bottom):
    TIME_BEFORE_RECALIBRATING = 10 # seconds
    TIME_REQUIRED_FOR_FIXATION = 3

    tracker.start_drift_check()
    driftCheckStartTime = datetime.datetime.now()
    driftCheckPassed = False
    # For a given period, wait to see if they are looking at the fixation cross
    while (datetime.datetime.now() - driftCheckStartTime).seconds < TIME_BEFORE_RECALIBRATING and not driftCheckPassed:
        gazePos = tracker.get_gaze_data(mainWindow)
        xGazePos = gazePos[0][0][0] # Using left eye
        yGazePos = gazePos[0][0][1]
        # Check if current gaze position is within the range considered to be on the fixation cross
        gazeOnTarget = False
        if xGazePos > left and xGazePos < right and yGazePos > top and yGazePos < bottom:
            gazeOnTarget = True
            fixationStartTime = datetime.datetime.now()
            # For the target fixation duration, check if they continue to look at the target
            while (datetime.datetime.now() - fixationStartTime).seconds < TIME_REQUIRED_FOR_FIXATION and gazeOnTarget:
                if not (xGazePos > left and xGazePos < right and yGazePos > top and yGazePos < bottom):
                    gazeOnTarget = False

        # If the var is True at this point, then it must have remained True for long enough to consider that a satisfactory fixation!
        if gazeOnTarget:
            driftCheckPassed = True

    tracker.stop_drift_check()
    return driftCheckPassed

# We need to tell TPL when we're doing with the relevant image
def finishDisplayingStimulus(startTime, mediaItem, ttl, recording):
    endTime = int((ttl.get_time_stamp())['timestamp'])
    ttl.send_stimulus_event(recording['recording_id'], start_timestamp = str(startTime), media_id = mediaItem['media_id'], end_timestamp = endTime)
    return endTime

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

    calibrateRecorder(tracker, mainWindow, mouse)

    return proLabConnection

def startRecordingGaze(proLabConnection):
    # Check that Lab is ready to start a recording
    state = proLabConnection.get_state()
    assert state['state'] == 'ready', state['state']

    ## Start recording (Note: you have to click on the Record Tab first!)
    recording = proLabConnection.start_recording("image_viewing", participantID, screen_width=1920, screen_height=1080)

    return recording

def stopRecordingGaze(proLabConnection, recording):
    proLabConnection.stop_recording()
    proLabConnection.finalize_recording(recording['recording_id'])

# **************
# This function is not being used currently - it is for eye-tracking with Tobii directly, rather than via Tobii Pro Lab.
def setUpEyeTracker(mainWindow):
    iohub_config = {'eyetracker.hw.tobii.EyeTracker': {'name': 'tracker', 'calibration': {'type': 'THREE_POINTS'}}}
    io = launchHubServer(window = mainWindow, **iohub_config)
    tracker = io.getDevice('tracker')

    return tracker
# **************
