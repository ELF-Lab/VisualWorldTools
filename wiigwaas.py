from random import randint
from pathlib import *
from psychopy import core, event, monitors, sound, visual
from randomizer import latinSquare
from psychopy_resources import addAOI, addBackgroundImageToRecorder, checkForInputOnImages, closeRecorder, displayBufferScreen, displayFixationCrossScreen, displaySubjIDDialog, displayTextScreen, finishWithTPLImages, listenForQuit, setUpRecorder, startRecordingGaze, stopRecordingGaze

# Global constants - the only variables defined here are those that need to be accessed by many functions
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
USER_INPUT_DEVICE = 'mouse' # 'mouse' or 'touch'
# These two are taken from read_me_TalkToProLab.py
# All I know is that they make the calibration work properly (rather than only calibrating a smaller central subarea of the screen)
SCREEN_WIDTH = 52.5  # cm
VIEWING_DIST = 63 #  # distance from eye to center of screen (cm)
IMAGE_SIZE = 425
IMAGE_OFFSET_FROM_EDGE = 20
NUM_IMAGES = 3 # Order (based on original CSV): agent, patient, distractor

def main():
    # Global vars (to be accessible by all functions)
    global mainWindow
    global mouse
    global outputFile
    global recorder

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
    clearClicksAndEvents() 
    
    # Setting up the gaze recorder takes a few seconds, so let's begin displaying a loading screen here!
    displayTextScreen(mainWindow, WINDOW_WIDTH, WINDOW_HEIGHT, "Setting up...")
    recorder = setUpRecorder(mainWindow, mouse)
    #tracker = setUpEyeTracker(mainWindow)

    # *** BEGIN EXPERIMENT ***
    # Display welcome screen until the user clicks
    displayBufferScreen(mainWindow, mouse, WINDOW_WIDTH, WINDOW_HEIGHT, 'Boozhoo! Biindigen.', USER_INPUT_DEVICE, quitExperiment)
    #calibrate(tracker)

    firstTime = True
    # Run trials!
    for trialNum, itemInfo in enumerate(experimentalItems):
        print(trialNum, itemInfo)
        imageFileNames = [itemInfo[4], itemInfo[5], itemInfo[6]]
        assert(len(imageFileNames) == NUM_IMAGES)
        audioFileName = itemInfo[7]
        print(imageFileNames)
        
        response = trial(imageFileNames, audioFileName, mainWindow, mouse, firstTime)
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

def clearClicksAndEvents():
    mouse.clickReset()
    event.clearEvents()

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
    images, checks, repeatIcon, selectionBox = getImages(imageFileNames, IMAGE_SIZE, CHECKMARK_SIZE)
    # Determine the position of each image
    images, checks, repeatIcon = setImagePositions(IMAGE_SIZE, CHECKMARK_SIZE, images, checks, repeatIcon)

    # *** BEGIN TRIAL ***
    # Add a wait time before the start of each new trial, with a blank screen
    mainWindow.flip()
    core.wait(WAIT_TIME_BETWEEN_TRIALS)
    
    # Display screen between trials so participant can indicate when ready
    displayBufferScreen(mainWindow, mouse, WINDOW_WIDTH, WINDOW_HEIGHT, BUFFER_TEXT, USER_INPUT_DEVICE, quitExperiment)

    # Display point in the center of screen for 1500ms
    displayFixationCrossScreen(mainWindow, WINDOW_HEIGHT)
    
    # Pause between displaying the fixation cross and displaying the stimuli
    core.wait(WAIT_TIME_BETWEEN_FIXATION_AND_STIMULI)
    
    # Display the images, and then pause before the audio is played
    drawStimuli(images + [repeatIcon])
    if firstTime:
        mediaInfo = addImagesToRecorder()
        recording = startRecordingGaze(recorder)
        startTime = int((recorder.get_time_stamp())['timestamp'])
    else:
        core.wait(WAIT_TIME_BETWEEN_STIMULI_AND_AUDIO)
          
    # Prepare for clicks, play the audio file, and start the timer - the user may interact starting now!
    clearClicksAndEvents()
    clicks = []
    imageClicked = None
    prevMouseLocation = mouse.getPos()
    playSound(audio)
    trialClock.reset()

    # We wait in this loop until we have a first click on one of the 3 images
    while not imageClicked:
        # Always be listening for a command to quit the program, or repeat the audio          
        listenForQuit(quitExperiment)
        prevMouseLocation = listenForRepeat(repeatIcon, prevMouseLocation, audio, trialClock, clicks)
        imageClicked, prevMouseLocation = checkForInputOnImages(mouse, images, prevMouseLocation, USER_INPUT_DEVICE)

    # Now, we've received a first click on one of the images
    check = handleStimuliClick(imageClicked,images, checks, selectionBox, repeatIcon, trialClock, clicks)

    # Now we wait in this loop until the checkmark is ultimately clicked
    checkmarkClicked = False
    while not checkmarkClicked:
        
        # Always be listening for a command to quit the program, or repeat the audio  
        listenForQuit(quitExperiment)
        prevMouseLocation = listenForRepeat(repeatIcon, prevMouseLocation, audio, trialClock, clicks)
        
        # Always listening for a click on an image
        imageClicked, prevMouseLocation = checkForInputOnImages(mouse, images, prevMouseLocation, USER_INPUT_DEVICE)
        if imageClicked:
            check = handleStimuliClick(imageClicked, images, checks, selectionBox, repeatIcon, trialClock, clicks)

        # Always listening for a click on the checkmark
        checkmarkClicked, prevMouseLocation = checkForInputOnImages(mouse, [check], prevMouseLocation, USER_INPUT_DEVICE)
           
    # Once we reach here, the check has been clicked (i.e. the trial is over)
    if firstTime:
        finishWithTPLImages(startTime, mediaInfo, recorder, recording)
        stopRecordingGaze(recorder, recording)
    trialDur = trialClock.getTime()
    response = ["check", trialDur]
    clicks.append(response)

    positions = [images[0].pos, images[2].pos, images[1].pos]
    return positions, clicks


# *** Functions used inside trial() ***

# Give the recorder info about what images are on the screen, so that we can track gazes within those image areas
def addImagesToRecorder():
    # Add an overall background image (at present this is really just a placeholder)
    image_for_recorder_path = "C:\\Users\\Anna\\Documents\\Wiigwaas\\sample_trial_screen.jpeg"
    mediaInfo = addBackgroundImageToRecorder(recorder, image_for_recorder_path)

    # Add an AOI (area of interest) for each image
    AOI_SIZE = IMAGE_SIZE + IMAGE_OFFSET_FROM_EDGE
    LEFT_EDGE = 0
    RIGHT_EDGE = WINDOW_WIDTH
    X_MIDPOINT = WINDOW_WIDTH/2
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

# Get the images to be displayed for the given trial.
def getImages(imageFileNames, imageSize, checkmarkSize):    
    # Create an ImageStim object for each image stimuli
    agent = patient = distractor = None
    images = [agent, patient, distractor]
    for i, image in enumerate(images):
        images[i] = visual.ImageStim(win = mainWindow, image = Path.cwd()/"visualStims"/str(imageFileNames[i]), units = "pix", size = imageSize)
    
    # Create a unique check object for each image - even though they're all the same check image, they'll end up having different positions
    agentCheck = patientCheck = distractorCheck = None
    checks = [patientCheck, agentCheck, distractorCheck]
    for i, check in enumerate(checks):
        checks[i] = visual.ImageStim(win = mainWindow, image = Path.cwd()/"checkmark.png", units = "pix", size = checkmarkSize)
    
    repeatIcon = visual.ImageStim(win = mainWindow, image = Path.cwd()/"repeat.png", units = "pix", size = 100)
    
    selectionBox = visual.Rect(win = mainWindow, lineWidth = 2.5, lineColor = "#7AC043", fillColor = None, units = "pix", size = imageSize)

    return images, checks, repeatIcon, selectionBox

# Note that setPos defines the position of the image's /centre/, and screen positions are determined based on the /centre/ of the screen being (0,0)
def setImagePositions(imageSize, checkmarkSize, images, checks, repeatIcon):
    # The repeat button's position is always the same, no randomization needed
    bufferSize = min(WINDOW_WIDTH, WINDOW_HEIGHT) / 15
    repeatIcon.setPos([-WINDOW_WIDTH / 2 + bufferSize,-WINDOW_HEIGHT / 2 + bufferSize])

    # Calculate positions for the images relative to the window
    xSpacing = (WINDOW_WIDTH / 2) - (imageSize / 2) #i.e. distance from centre of screen to centre of image in order for the image to be against one side of the screen
    ySpacing = (WINDOW_HEIGHT / 2) - (imageSize / 2)
    left = -xSpacing + IMAGE_OFFSET_FROM_EDGE
    right = xSpacing - IMAGE_OFFSET_FROM_EDGE
    bottom = -ySpacing + IMAGE_OFFSET_FROM_EDGE
    top = ySpacing - IMAGE_OFFSET_FROM_EDGE
    centre = 0
    # Position the checkmarks just above/below the image
    checkBottom = bottom + imageSize / 2 + checkmarkSize / 2
    checkTop = top - imageSize / 2 - checkmarkSize / 2

    # Randomly determine the images' order (and therfore, positions)
    numberOfImages = 3
    random_ordering_of_images = getRandomImageOrder(numberOfImages)\
    # This is spelt out for readability, but can of course be simplified in future to suit varaible numbers of images
    # One of these will be the number 0, one will be 1, and the other will be 2
    firstImageIndex = random_ordering_of_images[0]
    secondImageIndex = random_ordering_of_images[1]
    thirdImageIndex = random_ordering_of_images[2]

    # Now set their positions based on that random order!
    images[firstImageIndex].setPos([left, top])
    checks[firstImageIndex].setPos([left, checkTop])
    images[secondImageIndex].setPos([right, top])
    checks[secondImageIndex].setPos([right, checkTop])
    images[thirdImageIndex].setPos([centre, bottom])
    checks[thirdImageIndex].setPos([centre, checkBottom])

    return images, checks, repeatIcon

def getRandomImageOrder(numImages):
    # We can think of the images as each having a number index, e.g. with three images, agent = 0, patient = 1, distractor = 2
    # So the images are numbered 0 through numImages - 1. We want a list that tells us their order.
    # So we want to randomize the order of the numbers 0 through numImages - 1.
    ordered_list = list(range(0, numImages)) # A list of all the image indexes, but in ascending order
    randomly_ordered_list = []

    for i in range(0, numImages):
       random_num = randint(0, len(ordered_list) - 1) # Choose randomly, from however many numbers we have left to choose
       randomly_ordered_list.append(ordered_list.pop(random_num))

    return randomly_ordered_list

def playSound(audio):
    audio.play()

def drawStimuli(stimuli_list):
    for stimulus in stimuli_list:
        stimulus.draw()
    mainWindow.flip()

def listenForRepeat(repeatIcon, prevMouseLocation, audio, trialClock, clicks):
    repeatClicked, prevMouseLocation = checkForInputOnImages(mouse, [repeatIcon], prevMouseLocation, USER_INPUT_DEVICE)
    if repeatClicked:
        playSound(audio)
        pic = "replay"
        trialDur = trialClock.getTime()
        response = [pic, trialDur]
        clicks.append(response)

    return prevMouseLocation

def handleStimuliClick(imageClicked, images, checks, selectionBox, repeatIcon, trialClock, clicks):
    trialDur = trialClock.getTime()
    selectionBox.setPos(imageClicked.pos)
    if imageClicked == images[0]:
        pic = "agent"
        check = checks[0]
    elif imageClicked == images[1]:
        pic = "patient"
        check = checks[1]
    elif imageClicked == images[2]:
        pic = "distractor"
        check = checks[2]
    response = [pic, trialDur]
    clicks.append(response)

    # Re-draw to include the selection box and checkmark
    drawStimuli(images + [repeatIcon, selectionBox, check])
    
    return check

# This is used inside both main and trial (as the user may quit during a trial)
def quitExperiment():
    displayTextScreen(mainWindow, WINDOW_WIDTH, WINDOW_HEIGHT, "Quitting...")
    
    # Quit gracefully
    closeRecorder(recorder)
    outputFile.close()
    core.quit()

### Run Experiment ###
main()
