import os, random, numpy, csv, time
import psychopy.gui
from psychopy import visual, monitors, event, core, logging, gui, sound, data
from randomizer import latinSquare as latin_square
from pathlib import *

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

# Where do I find the items?
fileName = 'experimentalItems.csv'
item_file = open(fileName)

# Number of lists.
number_lists = 4

# Dialog box to get subject number
gui = psychopy.gui.Dlg()
gui.addField("Subject ID:")
gui.show()
subj_id = int(gui.data[0])

#Creating Stimuli and Window
windowWidth = 1920
windowHeight = 1080
win = visual.Window([windowWidth, windowHeight], fullscr=True, allowGUI=True, monitor='testMonitor', units='pix',color="white")

#Create practice window
practice = visual.TextStim(win, text='Boozhoo! Biindigen.',pos=(0.0, 0.0), height= windowHeight / 20, wrapWidth = windowWidth, color = "black")

#Create trial buffer window
buffer = visual.TextStim(win, text='Tanganan wii-majitaayan\n mezhinaatebiniwemagak.',pos=(0.0, 0.0), height = windowHeight / 20, wrapWidth = windowWidth, color = "black")

#Create fixation windown
fixation = visual.TextStim(
    win,
    text='+',
    pos=(0.0, 0.0),
    bold=True,
    height= windowHeight / 10,
    color = "black")

#Define the mouse and the clock
mouse= event.Mouse(visible = True, win = win)
trial_clock = core.Clock()

# Create output file to save data
data = open("Wiigwaas-Exp-" + str(subj_id) + ".txt", "w")      ## Open output file channel for editing
data.write('subj\ttrial\titem\tcond\tclicks\n')     ## add header


##### INITIALIZE THE EXPERIMENT ###############################################

# Calculate current list based on subject number.
current_list = subj_id % number_lists + \
               ((not subj_id % number_lists) * number_lists)

# Get experimental items and randomize.
experimental_items = latin_square(current_list, fileName)
#experimental_items = item_file
print(experimental_items)

# Clear all stray events and clicks
mouse.clickReset()
event.clearEvents()

def main():
    #Display Practice Screen
    while mouse.getPressed()[0] == 0: #Wait for mouse click to move on
        practice.draw()
        win.flip()

    for trialNum, itemInfo in enumerate(experimental_items):
        print("hello")
        print(trialNum, itemInfo)
        imageFileNames = [itemInfo[4], itemInfo[5], itemInfo[6]]
        audioFileName = itemInfo[7]
        print(imageFileNames) #prints to the Output window for testing purposes
        
        response = trial(imageFileNames, audioFileName)
        
        #print(subj_id,trialNum,response) #prints to the Output window for testing purposes
        
        #Record the data from the last trial
        data.write(str(subj_id)+"\t"+str(trialNum)+"\t"+str(itemInfo[1])+"\t"+str(itemInfo[2])+"\t"+str(response)+"\n")
        data.flush()

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

def trial(imageFileNames, audioFileName):    
    imageSize = 425
    checkmarkSize = 100

    # Get the images to be displayed for the given trial.
    def getImages(imageFileNames, imageSize, checkmarkSize):    
        patient = visual.ImageStim(win = win, image = Path.cwd()/"visualStims"/str(imageFileNames[1]), units = "pix", size = imageSize)
        agent = visual.ImageStim(win = win, image = Path.cwd()/"visualStims"/str(imageFileNames[0]), units = "pix", size = imageSize)
        distractor = visual.ImageStim(win = win, image = Path.cwd()/"visualStims"/str(imageFileNames[2]), units = "pix", size = imageSize)
        
        patientCheck = visual.ImageStim(win = win, image = Path.cwd()/"checkmark.png", units = "pix", size = checkmarkSize)
        agentCheck = visual.ImageStim(win = win, image = Path.cwd()/"checkmark.png", units = "pix", size = checkmarkSize)
        distractorCheck = visual.ImageStim(win = win, image = Path.cwd()/"checkmark.png", units = "pix", size = checkmarkSize)
        
        repeatIcon = visual.ImageStim(win = win, image = Path.cwd()/"repeat.png", units = "pix", size = 100)
        bufferSize = min(windowWidth, windowHeight) / 15
        repeatIcon.setPos([-windowWidth / 2 + bufferSize,-windowHeight / 2 + bufferSize])
        
        selectionBox = visual.Rect(win = win, lineWidth = 2.5, lineColor = "#7AC043", fillColor = None, units = "pix", size = imageSize)
    
        return patient, agent, distractor, patientCheck, agentCheck, distractorCheck, repeatIcon, selectionBox

    def setImagePositions():
        # Randomly determine position of agent/patient
        rand = random.randint(0,5)

        # Calculate positions for each image relative to the window
        xSpacing = (windowWidth / 2) - (imageSize / 2)
        ySpacing = (windowHeight / 2) - (imageSize / 2)
        offset = 20
        left = -xSpacing + offset
        right = xSpacing - offset
        bottom = -ySpacing + offset
        top = ySpacing - offset
        centre = 0
        # Position the checkmarks just above/below the image
        checkBottom = bottom + imageSize / 2 + checkmarkSize / 2
        checkTop = top - imageSize / 2 - checkmarkSize / 2
        
        if (rand == 1):
            patient.setPos([left,top])
            patientCheck.setPos([left,checkTop])
            agent.setPos([right,top])
            agentCheck.setPos([right,checkTop])
            distractor.setPos([centre,bottom])
            distractorCheck.setPos([centre,checkBottom])
        elif (rand == 2):
            patient.setPos([right,top])
            patientCheck.setPos([right,checkTop])
            agent.setPos([left,top])
            agentCheck.setPos([left,checkTop])
            distractor.setPos([centre,bottom])
            distractorCheck.setPos([centre,checkBottom])
        elif (rand == 3):
            patient.setPos([left,top])
            patientCheck.setPos([left,checkTop])
            agent.setPos([centre,bottom])
            agentCheck.setPos([centre,checkBottom])
            distractor.setPos([right,top])
            distractorCheck.setPos([right,checkTop])
        elif (rand == 4):
            patient.setPos([right,top])
            patientCheck.setPos([right,checkTop])
            agent.setPos([centre,bottom])
            agentCheck.setPos([centre,checkBottom])
            distractor.setPos([left,top])
            distractorCheck.setPos([left,checkTop])
        elif (rand == 5):
            patient.setPos([centre,bottom])
            patientCheck.setPos([centre,checkBottom])
            agent.setPos([left,top])
            agentCheck.setPos([left,checkTop])
            distractor.setPos([right,top])
            distractorCheck.setPos([right,checkTop])
        else:
            patient.setPos([centre,bottom])
            patientCheck.setPos([centre,checkBottom])
            agent.setPos([right,top])
            agentCheck.setPos([right,checkTop])
            distractor.setPos([left,top])
            distractorCheck.setPos([left,checkTop])

        return patient, agent, distractor, patientCheck, agentCheck, distractorCheck

    def playSound():
        audio.play()

    # Get the relevant images
    patient, agent, distractor, patientCheck, agentCheck, distractorCheck, repeatIcon, selectionBox = getImages(imageFileNames, imageSize, checkmarkSize)

    # Get the audio to be played for the given trial.
    audio = sound.Sound(Path.cwd()/"audio"/str(audioFileName))
    
    # Create variable to store the picture that is chosen
    pic = []

    # Determine the position of each image
    patient, agent, distractor, patientCheck, agentCheck, distractorCheck = setImagePositions()
    
    mouse.clickReset()
    event.clearEvents()
    
    win.flip()
    core.wait(.75)
    
    #Buffer screen between trials so participant can indicate when ready
    while mouse.getPressed()[0] == 0:
        buffer.draw()
        win.flip()

    #Fixation point in the center of screen for 1500ms
    fixation.draw()
    win.flip()
    core.wait(1.5)
    
    #Some extra time so the stimulus appears 100ms after the fixation
    win.flip()
    core.wait(.1)
    
    # timeout variable can be omitted, if you use specific value in the while condition
    timeout = 4   # [seconds]
    timeout_start = time.time()

    while time.time() < timeout_start + timeout:
        
        
        
        #Draw stimuli
        patient.draw()
        agent.draw()
        distractor.draw()
        repeatIcon.draw()
        win.flip()
        
    
    #Clear out all of the stuff
    mouse.clickReset()
    event.clearEvents()
    
    #Play audio file
    playSound()
    
    #RT linked to when audio starts
    trial_clock.reset()
    
    #for storing all mouse clicks
    clicks = []

    prev_mouse_location = mouse.getPos()
    #Initiate recording, stop given a touch on the screen
    while mouse.isPressedIn(agent) == 0 and mouse.isPressedIn(patient) == 0 and mouse.isPressedIn(distractor) == 0:
        
        
        
        #Draw stimuli
        patient.draw()
        agent.draw()
        distractor.draw()
        repeatIcon.draw()
        win.flip()
        
        response = []
    
        quit_check()
        
        repeat_requested, prev_mouse_location = check_for_tap(repeatIcon, prev_mouse_location)
        if repeat_requested:
            playSound()
            pic = "replay"
            trialdur = trial_clock.getTime()
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
            playSound()
            pic = "replay"
            trialdur = trial_clock.getTime()
            response = [pic,trialdur]
            clicks.append(response)
            
        # Collect which image was pressed
        if mouse.isPressedIn(agent):
            pic = "agent"
            trialdur = trial_clock.getTime()
            selectionBox.setPos(agent.pos)
            check = agentCheck
            response = [pic,trialdur]
            clicks.append(response)
        elif mouse.isPressedIn(patient):
            pic = "patient"
            trialdur = trial_clock.getTime()
            selectionBox.setPos(patient.pos)
            check = patientCheck
            response = [pic,trialdur]
            clicks.append(response)
        elif mouse.isPressedIn(distractor):
            pic = "distractor"
            trialdur = trial_clock.getTime()
            selectionBox.setPos(distractor.pos)
            check = distractorCheck
            response = [pic,trialdur]
            clicks.append(response)
        elif mouse.isPressedIn(check):
            pic = "check"
            trialdur = trial_clock.getTime()
            response = [pic,trialdur]
            clicks.append(response)
            
            break
        
        #This ensures only the initial frame where a mouse is clicked is recorded
        while any(mouse.getPressed()):
            pass
            
        patient.draw()
        agent.draw()
        distractor.draw()
        selectionBox.draw()
        check.draw()
        repeatIcon.draw()
        win.flip()
        
    
    #Get response
    positions = [agent.pos, distractor.pos, patient.pos]
    return positions, clicks
    #print(clicks)

### Run Experiment ###
main()