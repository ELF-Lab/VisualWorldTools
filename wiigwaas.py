import os, random, numpy, csv, time
import psychopy.gui
from psychopy import visual, event, core, sound
from randomizer import latinSquare as latin_square
from pathlib import *

# Global constants - the only variables defined here are those that need to be accessed by many functions
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080

def main():
    # Begin with the dialog for inputting subject ID
    subjID = displaySubjIDDialog()

    # *** SET-UP ***
    # Define the main window and mouse objects - these are made global so they can be accessed by all functions
    global mainWindow
    mainWindow = visual.Window([WINDOW_WIDTH, WINDOW_HEIGHT], fullscr = True, allowGUI = True, monitor = 'testMonitor', units = 'pix', color = "white")
    global mouse
    mouse = event.Mouse(visible = True, win = mainWindow)

    outputFile = createOutputFile(subjID)

    experimentalItems = getExperimentalItems(subjID)

    clearClicksAndEvents()

    # *** BEGIN DISPLAY ***
    # Display practice screen until the user clicks
    displayPracticeScreen()

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

    outputFile.close()


# *** Functions used inside main() ***
# Dialog box to get subject number
def displaySubjIDDialog():
    gui = psychopy.gui.Dlg()
    gui.addField("Subject ID:")
    gui.show()
    subjID = int(gui.data[0])
    return subjID

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
    experimentalItems = latin_square(currentList, EXP_ITEMS_FILE_NAME)
    print(experimentalItems)
    return experimentalItems

def clearClicksAndEvents():
    mouse.clickReset()
    event.clearEvents()

def displayPracticeScreen():
    practiceScreen = visual.TextStim(mainWindow, text = 'Boozhoo! Biindigen.', pos = (0.0, 0.0), height = WINDOW_HEIGHT / 20, wrapWidth = WINDOW_WIDTH, color = "black")
    while mouse.getPressed()[0] == 0: # Wait for mouse click before moving on
        practiceScreen.draw()
        mainWindow.flip()


# - Determine the images to be displayed and the audio to be played
# - Set image positions (randomly)
# - Diplay the fixation cross, followed by a short delay
# - Display the images
# - Play the audio
# - Display the images again (?)
# - Await a mouse click in one of the images
# - If such a click is received, also display the checkmark
# - If a click is received in a different image, move the checkmark
# - If a click is received in the checkmark, end the trial
# Stages: set-up, fixation cross, audio/image display, await initial click, await switch or confirmation click

def trial(imageFileNames, audioFileName, mainWindow, mouse):    
    IMAGE_SIZE = 425
    CHECKMARK_SIZE = 100
    WAIT_TIME_BETWEEN_TRIALS = .75 # in seconds
    WAIT_TIME_BETWEEN_FIXATION_AND_STIMULI = .1
    WAIT_TIME_BETWEEN_STIMULI_AND_AUDIO = 4
    
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
    displayBufferScreen()

    # Display point in the center of screen for 1500ms
    displayFixationCrossScreen()
    
    # Pause between displaying the fixation cross and displaying the stimuli
    core.wait(WAIT_TIME_BETWEEN_FIXATION_AND_STIMULI)
    
    # Display the images, and then pause before the audio is played
    drawStimuli([patient, agent, distractor, repeatIcon])
    core.wait(WAIT_TIME_BETWEEN_STIMULI_AND_AUDIO)
          
    # Prepare for clicks, play the audio file, and start the timer - the user may interact starting now!
    clearClicksAndEvents()
    clicks = []
    playSound(audio)
    trialClock.reset()

    # We wait in this loop until we have a first click on one of the 3 images
    while checkForClick([patient, agent, distractor]) == None:
        # Always be listening for a command to quit the program, or repeat the audio          
        listenForQuit()     
        listenForRepeat(repeatIcon, audio, trialClock, clicks)

    # Now, we've received a first click on one of the images
    check = stimuliClicked(agent, patient, distractor, agentCheck, patientCheck, distractorCheck, selectionBox, repeatIcon, trialClock, clicks)

    # Now we wait in this loop until the checkmark is ultimately clicked
    while checkForClick([check]) == None:
        clickReceived = False
        
        # Always be listening for a command to quit the program, or repeat the audio  
        listenForQuit()
        clickReceived = listenForRepeat(repeatIcon, audio, trialClock, clicks)
        
        # Always listening for a click on an image
        if checkForClick([patient, agent, distractor]) != None:
            check = stimuliClicked(agent, patient, distractor, agentCheck, patientCheck, distractorCheck, selectionBox, repeatIcon, trialClock, clicks)
            clickReceived = True

        # The following prevents input from being received over and over (i.e. for the duration of a click)
        # "If we already accounted for this click, just loop here until the click is finished so we don't count it again"
        while any(mouse.getPressed()) and clickReceived:
            pass
           
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

def displayBufferScreen():
    bufferScreen = visual.TextStim(mainWindow, text = 'Tanganan wii-majitaayan\n mezhinaatebiniwemagak.', pos = (0.0, 0.0), height = WINDOW_HEIGHT / 20, wrapWidth = WINDOW_WIDTH, color = "black")
    while mouse.getPressed()[0] == 0:
        bufferScreen.draw()
        mainWindow.flip()

def displayFixationCrossScreen():
    fixationScreen = visual.TextStim(
        mainWindow,
        text = '+',
        pos = (0.0, 0.0),
        bold = True,
        height = WINDOW_HEIGHT / 10,
        color = "black")

    fixationScreen.draw()
    mainWindow.flip()
    core.wait(1.5) # 1500ms
    mainWindow.flip()     

def playSound(audio):
    audio.play()

def drawStimuli(stimuli_list):
    for stimulus in stimuli_list:
        stimulus.draw()
    mainWindow.flip()

# Checks for a single tap on an image
# Does this by asking: has the "mouse" moved? (= yes if a tap was received)
# And: If so, is the "mouse" within the image?
def checkForTap(image, prevMouseLocation):
    tapReceived = False
    mouse_location = mouse.getPos()
    # If the mouse moved... (check x and y coords)
    if not(mouse_location[0] == prevMouseLocation[0] and mouse_location[1] == prevMouseLocation[1]):
        # If the mouse is within the image...
        if image.contains(mouse):
            tapReceived = True
        prevMouseLocation = mouse.getPos() # Update for the next check
    return tapReceived, prevMouseLocation

# Returns None if no image clicked, otherwise returns the clicked image
def checkForClick(images):
    clickedImage = None
    for image in images:
        if mouse.isPressedIn(image):
            clickedImage = image
    return clickedImage

#Listens for a keyboard shortcut that tells us to quit the experiment
def listenForQuit():
    quitKey = 'escape'
    keys = event.getKeys()
    if quitKey in keys:
        core.quit()

def listenForRepeat(repeatIcon, audio, trialClock, clicks):
    clickReceived = False
    if checkForClick([repeatIcon]) != None:
        playSound(audio)
        pic = "replay"
        trialDur = trialClock.getTime()
        response = [pic, trialDur]
        clicks.append(response)
        clickReceived = True
    
    return clickReceived

    # repeat_requested, prevMouseLocation = checkForTap(repeatIcon, prevMouseLocation)
    # if repeat_requested:
    #     playSound(audio)
    #     pic = "replay"
    #     trialDur = trialClock.getTime()
    #     response = [pic,trialDur]
    #     clicks.append(response)

def stimuliClicked(agent, patient, distractor, agentCheck, patientCheck, distractorCheck, selectionBox, repeatIcon, trialClock, clicks):
    # We received a click on a stimulus! Which one?
    clickedImage = checkForClick([patient, agent, distractor])
    trialDur = trialClock.getTime()
    selectionBox.setPos(clickedImage.pos)
    if clickedImage == agent:
        pic = "agent"
        check = agentCheck
    elif clickedImage == patient:
        pic = "patient"
        check = patientCheck
    elif clickedImage == distractor:
        pic = "distractor"
        check = distractorCheck
    response = [pic, trialDur]
    clicks.append(response)

    # Re-draw to include the selection box and checkmark
    drawStimuli([patient, agent, distractor, repeatIcon, selectionBox, check])
    
    return check


### Run Experiment ###
main()