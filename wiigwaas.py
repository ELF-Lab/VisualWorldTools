from random import randint
from pathlib import *
from psychopy import core, event, monitors, sound, visual
from randomizer import latinSquare
from display_resources import checkForInputOnImages, clearClicksAndEvents, displayBufferScreen, displayFixationCrossScreen, displaySubjIDDialog, displayTextScreen,getImages, handleStimuliClick, drawStimuli, listenForQuit, listenForRepeat, playSound, setImagePositions
from eye_tracking_resources import addAOI, addImageToRecorder, closeRecorder, finishDisplayingStimulus, setUpRecorder, startRecordingGaze, stopRecordingGaze

EYETRACKING_ON = True # Turn this off if you just want to test the experimental flow sans any eyetracking

# Global constants - the only variables defined here are those that need to be accessed by many functions
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
USER_INPUT_DEVICE = 'mouse' # 'mouse' or 'touch'
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
    global mainWindow
    global mediaInfo
    global mouse
    global outputFile
    global recorder
    global recording

    # Begin with the dialog for inputting subject ID
    subjID = displaySubjIDDialog()

    # *** SET-UP ***
    # Define objects for the main screen, mouse, output file and list of experimental items. Plus, start with a blank slate for clicks and events.
    monitor = monitors.Monitor('myMonitor')
    monitor.setWidth(SCREEN_WIDTH)
    monitor.setDistance(VIEWING_DIST)
    monitor.setSizePix([WINDOW_WIDTH, WINDOW_HEIGHT])
    mainWindow = visual.Window([WINDOW_WIDTH, WINDOW_HEIGHT], fullscr = True, allowGUI = True, monitor = monitor, units = 'pix', color = "white")
    mouse = event.Mouse(visible = True, win = mainWindow)
    outputFile = createOutputFile(subjID)
    experimentalItems = getExperimentalItems(subjID)
    clearClicksAndEvents(mouse)
    
    # Setting up the gaze recorder takes a few seconds, so let's begin displaying a loading screen here!
    displayTextScreen(mainWindow, WINDOW_WIDTH, WINDOW_HEIGHT, "Setting up...")
    if EYETRACKING_ON:
        recorder = setUpRecorder(mainWindow, mouse)
        mediaInfo = addImagesToRecorder()
        recording = startRecordingGaze(recorder)
    #tracker = setUpEyeTracker(mainWindow)

    # *** BEGIN EXPERIMENT ***
    # Display welcome screen until the user clicks
    displayBufferScreen(mainWindow, mouse, WINDOW_WIDTH, WINDOW_HEIGHT, 'Boozhoo! Biindigen.', USER_INPUT_DEVICE, quitExperiment)
    #calibrate(tracker)

    firstTime = EYETRACKING_ON
    # Run trials!
    for trialNum, itemInfo in enumerate(experimentalItems):
        print(trialNum, itemInfo)
        # By specifying the image file names, you also specify how many images we're using!
        imageFileNames = [itemInfo[4], itemInfo[5], itemInfo[6]]
        # Check that the number of images provided is supported
        if len(imageFileNames) not in SUPPORTED_IMAGE_NUMBERS:
            print(f"\nERROR: Unsupported number of images ({len(imageFileNames)}).  Supported numbers are {SUPPORTED_IMAGE_NUMBERS}.\n")
            quitExperiment()
        audioFileName = itemInfo[7]
        print(imageFileNames)
        
        response = trial(imageFileNames, audioFileName, mainWindow, mouse, firstTime)
        if firstTime:
            stopRecordingGaze(recorder, recording)
        firstTime = False
                
        #Record the data from the last trial
        outputFile.write(str(subjID)+"\t"+str(trialNum)+"\t"+str(itemInfo[1])+"\t"+str(itemInfo[2])+"\t"+str(response)+"\n")
        outputFile.flush()

    quitExperiment()


# *** Functions used inside main() ***

# Create output file to save data
def createOutputFile(subjID):
    outputFile = open("Wiigwaas-Exp-" + str(subjID) + ".txt", "w") # Open output file channel for editing
    outputFile.write('subj\ttrial\titem\tcond\tclicks\n') # Add header
    return outputFile

def getExperimentalItems(subjID):
    EXP_ITEMS_FILE_NAME = 'experimentalItems.csv'
    NUMBER_OF_LISTS = 4
    
    # Calculate current list based on subject number.
    currentList = subjID % NUMBER_OF_LISTS + ((not subjID % NUMBER_OF_LISTS) * NUMBER_OF_LISTS)

    # Get experimental items and randomize.
    experimentalItems = latinSquare(currentList, EXP_ITEMS_FILE_NAME)
    print(experimentalItems)
    return experimentalItems

# What happens in a trial?
# - Determine the images to be displayed and the audio to be played
# - Set image positions (randomly)
# - Diplay the buffer and fixation cross screens
# - Display the images
# - Play the audio
# - Await a mouse click in one of the images
# - If such a click is received, also display the checkmark/box
# - If a click is then received in a different image, move the checkmark/box
# - If a click is then received in the checkmark, end the trial
def trial(imageFileNames, audioFileName, mainWindow, mouse, firstTime):
    CHECKMARK_SIZE = 100
    WAIT_TIME_BETWEEN_TRIALS = .75 # in seconds
    WAIT_TIME_BETWEEN_FIXATION_AND_STIMULI = .1
    WAIT_TIME_BETWEEN_STIMULI_AND_AUDIO = 4
    BUFFER_TEXT = 'Tanganan wii-majitaayan\n mezhinaatebiniwemagak.'
    
    trialClock = core.Clock()

    # Get the audio to be played for the given trial.
    audio = sound.Sound(Path.cwd()/"audio"/str(audioFileName))

    # Get the relevant images
    images, checks, repeatIcon, selectionBox = getImages(imageFileNames, IMAGE_SIZE, CHECKMARK_SIZE, REPEAT_ICON_SIZE, mainWindow)
    # Determine the position of each image
    images, checks, repeatIcon = setImagePositions(IMAGE_SIZE, CHECKMARK_SIZE, images, checks, repeatIcon, WINDOW_WIDTH, WINDOW_HEIGHT, IMAGE_OFFSET_FROM_EDGE)

    # *** BEGIN TRIAL ***
    # Add a wait time before the start of each new trial, with a blank screen
    mainWindow.flip()
    core.wait(WAIT_TIME_BETWEEN_TRIALS)
    
    # Display screen between trials so participant can indicate when ready
    if firstTime:
        startTime = int((recorder.get_time_stamp())['timestamp'])
    displayBufferScreen(mainWindow, mouse, WINDOW_WIDTH, WINDOW_HEIGHT, BUFFER_TEXT, USER_INPUT_DEVICE, quitExperiment)

    if firstTime:
        displayTransitionTime = finishDisplayingStimulus(startTime, mediaInfo[2], recorder, recording)

    # Display point in the center of screen for 1500ms
    displayFixationCrossScreen(mainWindow, WINDOW_HEIGHT)
    
    # Pause between displaying the fixation cross and displaying the stimuli
    core.wait(WAIT_TIME_BETWEEN_FIXATION_AND_STIMULI)
    
    if firstTime:
        displayTransitionTime = finishDisplayingStimulus(displayTransitionTime, mediaInfo[1], recorder, recording)

    # Display the images, and then pause before the audio is played
    drawStimuli(images + [repeatIcon], mainWindow)
    # core.wait(WAIT_TIME_BETWEEN_STIMULI_AND_AUDIO)
          
    # Prepare for clicks, play the audio file, and start the timer - the user may interact starting now!
    clearClicksAndEvents(mouse)
    clicks = []
    imageClicked = None
    prevMouseLocation = mouse.getPos()
    playSound(audio)
    trialClock.reset()

    # We wait in this loop until we have a first click on one of the 3 images
    while not imageClicked:
        # Always be listening for a command to quit the program, or repeat the audio          
        listenForQuit(quitExperiment)
        prevMouseLocation = listenForRepeat(repeatIcon, prevMouseLocation, audio, trialClock, clicks, mouse, USER_INPUT_DEVICE)
        imageClicked, prevMouseLocation = checkForInputOnImages(mouse, images, prevMouseLocation, USER_INPUT_DEVICE)

    # Now, we've received a first click on one of the images
    check = handleStimuliClick(imageClicked,images, checks, selectionBox, repeatIcon, trialClock, clicks, mainWindow)

    # Now we wait in this loop until the checkmark is ultimately clicked
    checkmarkClicked = False
    while not checkmarkClicked:
        
        # Always be listening for a command to quit the program, or repeat the audio  
        listenForQuit(quitExperiment)
        prevMouseLocation = listenForRepeat(repeatIcon, prevMouseLocation, audio, trialClock, clicks, mouse, USER_INPUT_DEVICE)
        
        # Always listening for a click on an image
        imageClicked, prevMouseLocation = checkForInputOnImages(mouse, images, prevMouseLocation, USER_INPUT_DEVICE)
        if imageClicked:
            check = handleStimuliClick(imageClicked, images, checks, selectionBox, repeatIcon, trialClock, clicks, mainWindow)

        # Always listening for a click on the checkmark
        checkmarkClicked, prevMouseLocation = checkForInputOnImages(mouse, [check], prevMouseLocation, USER_INPUT_DEVICE)
           
    # Once we reach here, the check has been clicked (i.e. the trial is over)
    if firstTime:
        finishDisplayingStimulus(displayTransitionTime, mediaInfo[0], recorder, recording)
    trialDur = trialClock.getTime()
    response = ["check", trialDur]
    clicks.append(response)

    positions = [image.pos for image in images]
    return positions, clicks


# *** Functions used inside trial() ***

# Give the recorder info about what images are on the screen, so that we can track gazes within those image areas
def addImagesToRecorder():
    # Add an overall background image (at present this is really just a placeholder)
    stimuli_image_path = "C:\\Users\\Anna\\Documents\\Wiigwaas\\sample_trial_screen.jpeg"
    fixation_cross_image_path = "C:\\Users\\Anna\\Documents\\Wiigwaas\\fixation_cross.jpeg"
    buffer_image_path = "C:\\Users\\Anna\\Documents\\Wiigwaas\\buffer_screen.jpeg"
    media_info = []
    mediaInfo = addImageToRecorder(recorder, media_info, stimuli_image_path)
    mediaInfo = addImageToRecorder(recorder, media_info, fixation_cross_image_path)
    mediaInfo = addImageToRecorder(recorder, media_info, buffer_image_path)
    # Need a better management system than just 0 = stimuli, 1 = fixation cross

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
    addAOI(recorder, mediaInfo[0]['media_id'], aoi_name, aoi_color, vertices)

    aoi_name = 'upper_right'
    aoi_color = '00AA00'
    vertices = ((RIGHT_EDGE - AOI_SIZE, TOP_EDGE), (RIGHT_EDGE - AOI_SIZE, TOP_EDGE + AOI_SIZE), (RIGHT_EDGE, TOP_EDGE + AOI_SIZE), (RIGHT_EDGE, TOP_EDGE))
    addAOI(recorder, mediaInfo[0]['media_id'], aoi_name, aoi_color, vertices)

    aoi_name = 'lower_middle'
    aoi_color = '0000AA'
    vertices = ((X_MIDPOINT - AOI_SIZE/2,  BOTTOM_EDGE - AOI_SIZE), (X_MIDPOINT - AOI_SIZE/2, BOTTOM_EDGE), (X_MIDPOINT + AOI_SIZE/2, BOTTOM_EDGE), (X_MIDPOINT + AOI_SIZE/2, BOTTOM_EDGE - AOI_SIZE))
    addAOI(recorder, mediaInfo[0]['media_id'], aoi_name, aoi_color, vertices)

    return mediaInfo

# This is used inside both main and trial (as the user may quit during a trial)
def quitExperiment():
    displayTextScreen(mainWindow, WINDOW_WIDTH, WINDOW_HEIGHT, "Quitting...")
    
    # Quit gracefully
    if EYETRACKING_ON:
        closeRecorder(recorder)
    outputFile.close()
    core.quit()

### Run Experiment ###
main()
