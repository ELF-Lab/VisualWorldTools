import os, random, numpy, csv, time
import psychopy.gui
from psychopy import visual, monitors, event, core, logging, gui, sound, data
from CSL import latinSquare as latin_square
from pathlib import *

# Where do I find the items?
item_file = open('experimentalItems.csv')

# Number of lists.
number_lists = 4

# Dialog box to get subject number
gui = psychopy.gui.Dlg()
gui.addField("Subject ID:")
gui.show()
subj_id = int(gui.data[0])

#Creating Stimuli and Window
win = visual.Window([1280, 800], fullscr=True, allowGUI=True, monitor='testMonitor', units='deg',color="white")

#Create practice window
practice = visual.TextStim(win, text='Boozhoo! Biindigen.',pos=(0.0, 0.0), height=1.20, color = "black")

#Create trial buffer window
buffer = visual.TextStim(win, text='Tanganan wii-majitaayan mezhinaatebiniwemagak.',pos=(0.0, 0.0), height=1.20, color = "black")

#Create fixation windown
fixation = visual.TextStim(
    win,
    text='+',
    pos=(0.0, 0.0),
    bold=True,
    height=3,
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
#experimental_items = latin_square(current_list, item_file)
experimental_items = item_file
print(experimental_items)

# Clear all stray events and clicks
mouse.clickReset()
event.clearEvents()

def main():
    #Display Practice Screen
    while mouse.getPressed()[0] == 0: #Wait for mouse click to move on
        practice.draw()
        win.flip()

    for trialNum, item in enumerate(experimental_items):
        print("hello")
        print(trialNum, item)
        item_list = item.split(",")
        images = [trialNum,item_list[4],item_list[5],item_list[6],item_list[7].strip()]
        print(images) #prints to the Output window for testing purposes
        
        response = trial(images)
        
        #print(subj_id,trialNum,response) #prints to the Output window for testing purposes
        
        #Record the data from the last trial
        data.write(str(subj_id)+"\t"+str(trialNum)+"\t"+str(item[1])+"\t"+str(item[2])+"\t"+str(response)+"\n")

def trial(images): 
    
    
    #Get the images to be displayed for a given trial. Defined in the items file.
    patient = visual.ImageStim(win=win,image=Path.cwd()/"visualStims"/str(images[2]),units="pix",size=425)
    agent = visual.ImageStim(win=win,image=Path.cwd()/"visualStims"/str(images[1]), units="pix",size=425)
    distractor = visual.ImageStim(win=win,image=Path.cwd()/"visualStims"/str(images[3]), units="pix",size=425)
    
    patientCheck = visual.ImageStim(win=win,image=Path.cwd()/"checkmark.png", units="pix",size=100)
    agentCheck = visual.ImageStim(win=win,image=Path.cwd()/"checkmark.png", units="pix",size=100)
    distractorCheck = visual.ImageStim(win=win,image=Path.cwd()/"checkmark.png", units="pix",size=100)
    
    repeat = visual.ImageStim(win=win,image=Path.cwd()/"repeat.png", units="pix",size=100)
    repeat.setPos([-900,-475])
    
    correct = visual.Rect(win = win,lineWidth=2.5, lineColor="#7AC043",units = "pix", size = 900)
    
    #Get the audio to be played for a given trial.
    audio = sound.Sound(Path.cwd()/"audio"/str(images[4]))
    
    def playSound():
        audio.play()
    
    #Create variable to store the picture that is chosen
    pic = []
    
    #Randomly determining position of agent/patient
    rand = random.randint(0,5)
    if (rand == 1):
        patient.setPos([-550,300])
        patientCheck.setPos([-550,0])
        agent.setPos([550,300])
        agentCheck.setPos([550,0])
        distractor.setPos([0,-300])
        distractorCheck.setPos([0,0])
    elif (rand == 2):
        patient.setPos([550,300])
        patientCheck.setPos([550,0])
        agent.setPos([-550,300])
        agentCheck.setPos([-550,0])
        distractor.setPos([0,-300])
        distractorCheck.setPos([0,0])
    elif (rand == 3):
        patient.setPos([-550,300])
        patientCheck.setPos([-550,0])
        agent.setPos([0,-300])
        agentCheck.setPos([0,0])
        distractor.setPos([550,300])
        distractorCheck.setPos([550,0])
    elif (rand == 4):
        patient.setPos([550,300])
        patientCheck.setPos([550,0])
        agent.setPos([0,-300])
        agentCheck.setPos([0,0])
        distractor.setPos([-550,300])
        distractorCheck.setPos([-550,0])
    elif (rand == 5):
        patient.setPos([0,-300])
        patientCheck.setPos([0,0])
        agent.setPos([-550,300])
        agentCheck.setPos([-550,0])
        distractor.setPos([550,300])
        distractorCheck.setPos([550,0])
    else:
        patient.setPos([0,-300])
        patientCheck.setPos([0,0])
        agent.setPos([550,300])
        agentCheck.setPos([550,0])
        distractor.setPos([-550,300])
        distractorCheck.setPos([-550,0])
    
    agentPOS = agent.pos
    patientPOS = patient.pos
    distractorPOS = distractor.pos
    
    positions = [agentPOS,distractorPOS,patientPOS]
    
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
        repeat.draw()
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

    #Initiate recording, stop given a touch on the screen
    while mouse.isPressedIn(agent) == 0 and mouse.isPressedIn(patient) == 0 and mouse.isPressedIn(distractor) == 0:
        
        
        
        #Draw stimuli
        patient.draw()
        agent.draw()
        distractor.draw()
        repeat.draw()
        win.flip()
        
#        win.getMovieFrame() 
#        win.saveMovieFrames(fileName='trial'+str(images[0])+'.png')
        
        response = []
        
        if mouse.isPressedIn(repeat):
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
        
        
        if mouse.isPressedIn(repeat):
            playSound()
            pic = "replay"
            trialdur = trial_clock.getTime()
            response = [pic,trialdur]
            clicks.append(response)
            
        # Collect which image was pressed
        if mouse.isPressedIn(agent):
            pic = "agent"
            trialdur = trial_clock.getTime()
            correct.setPos(agentPOS)
            check = agentCheck
            response = [pic,trialdur]
            clicks.append(response)
        elif mouse.isPressedIn(patient):
            pic = "patient"
            trialdur = trial_clock.getTime()
            correct.setPos(patientPOS)
            check = patientCheck
            response = [pic,trialdur]
            clicks.append(response)
        elif mouse.isPressedIn(distractor):
            pic = "distractor"
            trialdur = trial_clock.getTime()
            correct.setPos(distractorPOS)
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
        correct.draw()
        check.draw()
        repeat.draw()
        win.flip()
        
    
    #Get response
    return positions,clicks
    #print(clicks)

### Run Experiment ###
main()