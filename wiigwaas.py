import random
from pathlib import *
from psychopy import visual, event, core, sound
from randomizer import latinSquare
from psychopy_resources import calibrate, checkForInputOnImages, closeRecorder, displayBufferScreen, displayFixationCrossScreen, displaySubjIDDialog, displayTextScreen, listenForQuit, setUpEyeTracker, setUpRecorder

# Global constants - the only variables defined here are those that need to be accessed by many functions
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
USER_INPUT_DEVICE = 'mouse' # 'mouse' or 'touch'

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
    mainWindow = visual.Window([WINDOW_WIDTH, WINDOW_HEIGHT], fullscr = True, allowGUI = True, monitor = 'testMonitor', units = 'pix', color = "white")
    mouse = event.Mouse(visible = True, win = mainWindow)
    outputFile = createOutputFile(subjID)
    experimentalItems = getExperimentalItems(subjID)
    clearClicksAndEvents() 
    
    # Setting up the gaze recorder takes a few seconds, so let's begin displaying a loading screen here!
    displayTextScreen(mainWindow, WINDOW_WIDTH, WINDOW_HEIGHT, "Setting up...")
    recorder = setUpRecorder()

    # *** BEGIN EXPERIMENT ***
    # Display welcome screen until the user clicks
    displayBufferScreen(mainWindow, mouse, WINDOW_WIDTH, WINDOW_HEIGHT, 'Boozhoo! Biindigen.', USER_INPUT_DEVICE, quitExperiment)
    #tracker = setUpEyeTracker(mainWindow)
    #calibrate(tracker)

    # Run trials!
    for trialNum, itemInfo in enumerate(experimentalItems):
        print(trialNum, itemInfo)
        imageFileNames = [itemInfo[4], itemInfo[5], itemInfo[6]]
        audioFileName = itemInfo[7]
        print(imageFileNames)
        
        response = trial(imageFileNames, audioFileName, mainWindow, mouse)
                
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
def trial(imageFileNames, audioFileName, mainWindow, mouse):    
    IMAGE_SIZE = 425
    CHECKMARK_SIZE = 100
    WAIT_TIME_BETWEEN_TRIALS = .75 # in seconds
    WAIT_TIME_BETWEEN_FIXATION_AND_STIMULI = .1
    WAIT_TIME_BETWEEN_STIMULI_AND_AUDIO = 4
    BUFFER_TEXT = 'Tanganan wii-majitaayan\n mezhinaatebiniwemagak.'
    
    trialClock = core.Clock()

    # Get the audio to be played for the given trial.
    audio = sound.Sound(Path.cwd()/"audio"/str(audioFileName))

    # Get the relevant images
    patient, agent, distractor, patientCheck, agentCheck, distractorCheck, repeatIcon, selectionBox = getImages(imageFileNames, IMAGE_SIZE, CHECKMARK_SIZE)
    # Determine the position of each image
    patient, agent, distractor, patientCheck, agentCheck, distractorCheck = setImagePositions(IMAGE_SIZE, CHECKMARK_SIZE, patient, agent, distractor, patientCheck, agentCheck, distractorCheck)

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
    drawStimuli([patient, agent, distractor, repeatIcon])
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
        imageClicked, prevMouseLocation = checkForInputOnImages(mouse, [patient, agent, distractor], prevMouseLocation, USER_INPUT_DEVICE)

    # Now, we've received a first click on one of the images
    check = handleStimuliClick(imageClicked, agent, patient, distractor, agentCheck, patientCheck, distractorCheck, selectionBox, repeatIcon, trialClock, clicks)

    # Now we wait in this loop until the checkmark is ultimately clicked
    checkmarkClicked = False
    while not checkmarkClicked:
        
        # Always be listening for a command to quit the program, or repeat the audio  
        listenForQuit(quitExperiment)
        prevMouseLocation = listenForRepeat(repeatIcon, prevMouseLocation, audio, trialClock, clicks)
        
        # Always listening for a click on an image
        imageClicked, prevMouseLocation = checkForInputOnImages(mouse, [patient, agent, distractor], prevMouseLocation, USER_INPUT_DEVICE)
        if imageClicked:
            check = handleStimuliClick(imageClicked, agent, patient, distractor, agentCheck, patientCheck, distractorCheck, selectionBox, repeatIcon, trialClock, clicks)

        # Always listening for a click on the checkmark
        checkmarkClicked, prevMouseLocation = checkForInputOnImages(mouse, [check], prevMouseLocation, USER_INPUT_DEVICE)
           
    # Once we reach here, the check has been clicked (i.e. the trial is over)
    trialDur = trialClock.getTime()
    response = ["check", trialDur]
    clicks.append(response)

    positions = [agent.pos, distractor.pos, patient.pos]
    return positions, clicks


# *** Functions used inside trial() ***

# Get the images to be displayed for the given trial.
def getImages(imageFileNames, imageSize, checkmarkSize):    
    patient = visual.ImageStim(win = mainWindow, image = Path.cwd()/"visualStims"/str(imageFileNames[1]), units = "pix", size = imageSize)
    agent = visual.ImageStim(win = mainWindow, image = Path.cwd()/"visualStims"/str(imageFileNames[0]), units = "pix", size = imageSize)
    distractor = visual.ImageStim(win = mainWindow, image = Path.cwd()/"visualStims"/str(imageFileNames[2]), units = "pix", size = imageSize)
    
    patientCheck = visual.ImageStim(win = mainWindow, image = Path.cwd()/"checkmark.png", units = "pix", size = checkmarkSize)
    agentCheck = visual.ImageStim(win = mainWindow, image = Path.cwd()/"checkmark.png", units = "pix", size = checkmarkSize)
    distractorCheck = visual.ImageStim(win = mainWindow, image = Path.cwd()/"checkmark.png", units = "pix", size = checkmarkSize)
    
    repeatIcon = visual.ImageStim(win = mainWindow, image = Path.cwd()/"repeat.png", units = "pix", size = 100)
    bufferSize = min(WINDOW_WIDTH, WINDOW_HEIGHT) / 15
    repeatIcon.setPos([-WINDOW_WIDTH / 2 + bufferSize,-WINDOW_HEIGHT / 2 + bufferSize])
    
    selectionBox = visual.Rect(win = mainWindow, lineWidth = 2.5, lineColor = "#7AC043", fillColor = None, units = "pix", size = imageSize)

    return patient, agent, distractor, patientCheck, agentCheck, distractorCheck, repeatIcon, selectionBox

def setImagePositions(imageSize, checkmarkSize, patient, agent, distractor, patientCheck, agentCheck, distractorCheck):
    # Randomly determine position of agent/patient
    rand = random.randint(0,5)

    # Calculate positions for each image relative to the window
    xSpacing = (WINDOW_WIDTH / 2) - (imageSize / 2)
    ySpacing = (WINDOW_HEIGHT / 2) - (imageSize / 2)
    OFFSET_FROM_EDGE = 20
    left = -xSpacing + OFFSET_FROM_EDGE
    right = xSpacing - OFFSET_FROM_EDGE
    bottom = -ySpacing + OFFSET_FROM_EDGE
    top = ySpacing - OFFSET_FROM_EDGE
    centre = 0
    # Position the checkmarks just above/below the image
    checkBottom = bottom + imageSize / 2 + checkmarkSize / 2
    checkTop = top - imageSize / 2 - checkmarkSize / 2
    
    if (rand == 1):
        patient.setPos([left, top])
        patientCheck.setPos([left, checkTop])
        agent.setPos([right, top])
        agentCheck.setPos([right, checkTop])
        distractor.setPos([centre, bottom])
        distractorCheck.setPos([centre, checkBottom])
    elif (rand == 2):
        patient.setPos([right, top])
        patientCheck.setPos([right, checkTop])
        agent.setPos([left, top])
        agentCheck.setPos([left, checkTop])
        distractor.setPos([centre, bottom])
        distractorCheck.setPos([centre, checkBottom])
    elif (rand == 3):
        patient.setPos([left, top])
        patientCheck.setPos([left, checkTop])
        agent.setPos([centre, bottom])
        agentCheck.setPos([centre, checkBottom])
        distractor.setPos([right, top])
        distractorCheck.setPos([right, checkTop])
    elif (rand == 4):
        patient.setPos([right, top])
        patientCheck.setPos([right, checkTop])
        agent.setPos([centre, bottom])
        agentCheck.setPos([centre, checkBottom])
        distractor.setPos([left, top])
        distractorCheck.setPos([left, checkTop])
    elif (rand == 5):
        patient.setPos([centre, bottom])
        patientCheck.setPos([centre, checkBottom])
        agent.setPos([left, top])
        agentCheck.setPos([left, checkTop])
        distractor.setPos([right, top])
        distractorCheck.setPos([right, checkTop])
    else:
        patient.setPos([centre, bottom])
        patientCheck.setPos([centre, checkBottom])
        agent.setPos([right, top])
        agentCheck.setPos([right, checkTop])
        distractor.setPos([left, top])
        distractorCheck.setPos([left, checkTop])

    return patient, agent, distractor, patientCheck, agentCheck, distractorCheck  

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

def handleStimuliClick(imageClicked, agent, patient, distractor, agentCheck, patientCheck, distractorCheck, selectionBox, repeatIcon, trialClock, clicks):
    trialDur = trialClock.getTime()
    selectionBox.setPos(imageClicked.pos)
    if imageClicked == agent:
        pic = "agent"
        check = agentCheck
    elif imageClicked == patient:
        pic = "patient"
        check = patientCheck
    elif imageClicked == distractor:
        pic = "distractor"
        check = distractorCheck
    response = [pic, trialDur]
    clicks.append(response)

    # Re-draw to include the selection box and checkmark
    drawStimuli([patient, agent, distractor, repeatIcon, selectionBox, check])
    
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
