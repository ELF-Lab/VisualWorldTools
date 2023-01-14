import os, random, numpy, csv, time
import psychopy.gui
from psychopy import visual, monitors, event, core, logging, gui, sound, data
from randomizer import latinSquare as latin_square
from pathlib import *

# Global constants
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080

def main():
    EXP_ITEMS_FILE_NAME = 'experimentalItems.csv'
    NUMBER_OF_LISTS = 4

    subjID = displaySubjIDDialog()

    # Define the main window and mouse objects - these are made global so they can be accessed by all functions
    global mainWindow
    mainWindow = visual.Window([WINDOW_WIDTH, WINDOW_HEIGHT], fullscr = True, allowGUI = True, monitor = 'testMonitor', units = 'pix', color = "white")
    global mouse
    mouse = event.Mouse(visible = True, win = mainWindow)

    outputFile = createOutputFile(subjID)

    # Calculate current list based on subject number.
    current_list = subjID % NUMBER_OF_LISTS + \
                ((not subjID % NUMBER_OF_LISTS) * NUMBER_OF_LISTS)

    # Get experimental items and randomize.
    experimental_items = latin_square(current_list, EXP_ITEMS_FILE_NAME)
    print(experimental_items)

    # Clear all stray events and clicks
    mouse.clickReset()
    event.clearEvents()

    # Display practice screen
    practiceScreen = visual.TextStim(mainWindow, text = 'Boozhoo! Biindigen.', pos = (0.0, 0.0), height = WINDOW_HEIGHT / 20, wrapWidth = WINDOW_WIDTH, color = "black")
    while mouse.getPressed()[0] == 0: # Wait for mouse click before moving on
        practiceScreen.draw()
        mainWindow.flip()

    # Run trials!
    for trialNum, itemInfo in enumerate(experimental_items):
        print("hello")
        print(trialNum, itemInfo)
        imageFileNames = [itemInfo[4], itemInfo[5], itemInfo[6]]
        audioFileName = itemInfo[7]
        print(imageFileNames) #prints to the Output window for testing purposes
        
        response = trial(imageFileNames, audioFileName, mainWindow, mouse)
        
        #print(subj_id,trialNum,response) #prints to the Output window for testing purposes
        
        #Record the data from the last trial
        outputFile.write(str(subjID)+"\t"+str(trialNum)+"\t"+str(itemInfo[1])+"\t"+str(itemInfo[2])+"\t"+str(response)+"\n")
        outputFile.flush()

    outputFile.close()

# Create output file to save data
def createOutputFile(subjID):
    outputFile = open("Wiigwaas-Exp-" + str(subjID) + ".txt", "w") # Open output file channel for editing
    outputFile.write('subj\ttrial\titem\tcond\tclicks\n') # Add header
    return outputFile

# Dialog box to get subject number
def displaySubjIDDialog():
    gui = psychopy.gui.Dlg()
    gui.addField("Subject ID:")
    gui.show()
    subj_id = int(gui.data[0])
    return subj_id

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

    # Variables to store the picture that is chosen, and all mouse clicks
    pic = []
    clicks = []  

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
    draw_stimuli([patient, agent, distractor, repeatIcon])
    core.wait(WAIT_TIME_BETWEEN_STIMULI_AND_AUDIO)
          
    # Play the audio file, start the timer and prepare for clicks - the user may interact starting now!
    mouse.clickReset()
    event.clearEvents()
    playSound(audio)
    trialClock.reset()


    prev_mouse_location = mouse.getPos()
    #Initiate recording, stop given a touch on the screen
    while mouse.isPressedIn(agent) == 0 and mouse.isPressedIn(patient) == 0 and mouse.isPressedIn(distractor) == 0:   
        draw_stimuli([patient, agent, distractor, repeatIcon])
        
        response = []
    
        quit_check()
        
        repeat_requested, prev_mouse_location = check_for_tap(repeatIcon, prev_mouse_location)
        if repeat_requested:
            playSound(audio)
            pic = "replay"
            trialdur = trialClock.getTime()
            response = [pic,trialdur]
            clicks.append(response)
            
            #This ensures only the initial frame where a mouse is clicked is recorded.
            while any(mouse.getPressed()):
                pass
                
                
    mouse.clickReset()
    event.clearEvents()

    while True:
        quit_check()
        
        if mouse.isPressedIn(repeatIcon):
            playSound(audio)
            pic = "replay"
            trialdur = trialClock.getTime()
            response = [pic,trialdur]
            clicks.append(response)
            
        # Collect which image was pressed
        if mouse.isPressedIn(agent):
            pic = "agent"
            trialdur = trialClock.getTime()
            selectionBox.setPos(agent.pos)
            check = agentCheck
            response = [pic,trialdur]
            clicks.append(response)
        elif mouse.isPressedIn(patient):
            pic = "patient"
            trialdur = trialClock.getTime()
            selectionBox.setPos(patient.pos)
            check = patientCheck
            response = [pic,trialdur]
            clicks.append(response)
        elif mouse.isPressedIn(distractor):
            pic = "distractor"
            trialdur = trialClock.getTime()
            selectionBox.setPos(distractor.pos)
            check = distractorCheck
            response = [pic,trialdur]
            clicks.append(response)
        elif mouse.isPressedIn(check):
            pic = "check"
            trialdur = trialClock.getTime()
            response = [pic,trialdur]
            clicks.append(response)
            
            break
        
        #This ensures only the initial frame where a mouse is clicked is recorded
        while any(mouse.getPressed()):
            pass
            
        draw_stimuli([patient, agent, distractor, repeatIcon, selectionBox, check])
    

    #Get response
    positions = [agent.pos, distractor.pos, patient.pos]
    return positions, clicks
    #print(clicks)

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

def draw_stimuli(stimuli_list):
    for stimulus in stimuli_list:
        stimulus.draw()
    mainWindow.flip()

# Checks for a single tap on an image
# Does this by asking: has the "mouse" moved? (= yes if a tap was received)
# And: If so, is the "mouse" within the image?
def check_for_tap(image, prev_mouse_location):
    tap_received = False
    mouse_location = mouse.getPos()
    # If the mouse moved... (check x and y coords)
    if not(mouse_location[0] == prev_mouse_location[0] and mouse_location[1] == prev_mouse_location[1]):
        # If the mouse is within the image...
        if image.contains(mouse):
            tap_received = True
        prev_mouse_location = mouse.getPos() # Update for the next check
    return tap_received, prev_mouse_location

#Listens for a keyboard shortcut that tells us to quit the experiment
quit_key = 'escape'
def quit_check():
    keys = event.getKeys()
    if quit_key in keys:
        core.quit()


### Run Experiment ###
main()