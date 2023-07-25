from psychopy.iohub import launchHubServer
from Titta.titta import Titta
from Titta.titta.TalkToProLab import TalkToProLab

def addAOI(ttl, image_id, aoi_name, aoi_color, vertices):
    tag_name = 'test_tag'
    group_name = 'test_group'

    ttl.add_aois_to_image(image_id, aoi_name, aoi_color, vertices, tag_name = tag_name, group_name = group_name)

# Tell TPL what image we're using during a gaze recording
def addImageToRecorder(ttl, media_info, imagePath, imageName):
    media_type = "image"
    media_info.update({imageName: ttl.upload_media(imagePath, media_type)})

    return media_info

def calibrate(tracker, mainWindow, mouse):
    tracker.calibrate(mainWindow)
    # For some reason, this calibration leaves the mouse invisible. So make it visible again before returning.
    mouse.setVisible(1)

def closeRecorder(ttl):
    # We need to explicitly end the thread that was maintaining the connection
    # Titta is set up to do this in their finalize_recording method, but in this case we are not recording anything yet
    ttl.endConnectionThread()
    ttl.disconnect()

# We need to tell TPL when we're doing with the relevant image
def finishDisplayingStimulus(startTime, mediaItem, ttl, recording):
    endTime = int((ttl.get_time_stamp())['timestamp'])
    ttl.send_stimulus_event(recording['recording_id'], start_timestamp = str(startTime), media_id = mediaItem['media_id'], end_timestamp = endTime)
    return endTime

def setUpEyeTracker(mainWindow):
    iohub_config = {'eyetracker.hw.tobii.EyeTracker': {'name': 'tracker', 'calibration': {'type': 'THREE_POINTS'}}}
    io = launchHubServer(window = mainWindow, **iohub_config)
    tracker = io.getDevice('tracker')

    return tracker

def setUpRecorder(mainWindow, mouse):
    # Specify the kind of eyetracker we are using, and an identifier for the participant
    settings = Titta.get_defaults("Tobii Pro Fusion")
    settings.FILENAME = 'another_test'
    participantID = settings.FILENAME

    # Create the eyetracker object (doesn't actually interact with the eyetracker itself here, just preparing for TPL)
    tracker = Titta.Connect(settings)
    tracker.init()

    # Create the connection with TPL
    proLabConnection = TalkToProLab(project_name = None, dummy_mode = False)
    proLabConnection.add_participant('another_test')

    calibrate(tracker, mainWindow, mouse)

    return proLabConnection

def startRecordingGaze(proLabConnection):
    # Check that Lab is ready to start a recording
    state = proLabConnection.get_state()
    assert state['state'] == 'ready', state['state']

    ## Start recording (Note: you have to click on the Record Tab first!)
    participants = proLabConnection.list_participants()['participant_list']
    assert(len(participants) == 1)
    participantID = (participants[0])['participant_id']
    recording = proLabConnection.start_recording("image_viewing", participantID, screen_width=1920, screen_height=1080)

    return recording

def stopRecordingGaze(proLabConnection, recording):
    proLabConnection.stop_recording()
    proLabConnection.finalize_recording(recording['recording_id'])
