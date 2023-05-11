from psychopy import core, event, gui, visual
from psychopy.iohub import launchHubServer
from titta import Titta
from titta.TalkToProLab import TalkToProLab

def calibrate(tracker):
    # Run calibration
    result = tracker.runSetupProcedure()
    print("Calibration returned: ", result)

    # Print 1s worth of data, just to see what it looks like
    tracker.setRecordingState(True)
    startTime = core.getTime()
    while core.getTime() - startTime < 1.0:
        for event in tracker.getEvents():
            print(event)

def setUpRecorder():
    # Specify the kind of eyetracker we are using, and an identifier for the participant
    settings = Titta.get_defaults("Tobii Pro Fusion")
    settings.FILENAME = 'anything'
    participantID = settings.FILENAME

    # Create the eyetracker object (doesn't actually interact with the eyetracker itself here, just preparing for TPL)
    tracker = Titta.Connect(settings)
    tracker.init()

    # Create the connection with TPL
    ttl = TalkToProLab(project_name = None, dummy_mode = False)

    return ttl

def closeRecorder(ttl):
    # We need to explicitly end the thread that was maintaining the connection
    # Titta is set up to do this in their finalize_recording method, but in this case we are not recording anything yet
    ttl.endConnectionThread()
    ttl.disconnect()

def checkForInputOnImages(mouse, images, prevMouseLocation, USER_INPUT_DEVICE):
    if USER_INPUT_DEVICE == 'mouse':
        clickedImage, prevMouseLocation = checkForClickOnImages(mouse, images, prevMouseLocation)
    elif USER_INPUT_DEVICE == 'touch':
        clickedImage, prevMouseLocation = checkForTapOnImages(mouse, images, prevMouseLocation)
    else:
        print("Error: User input device is not set to a valid value (mouse or touch). Quitting...")
        core.quit()
    return clickedImage, prevMouseLocation

# Given a list of images, returns the one that is being clicked (or None)
# Hold for the duration of the click - so that when this function ends, the click is over
def checkForClickOnImages(mouse, images, prevMouseLocation):
    clickedImage = None
    for image in images:
        if mouse.isPressedIn(image):
            clickedImage = image
            while any(mouse.getPressed()):
                pass
            # Not necessary, but keeps things consistent with the use of checkForTap
            prevMouseLocation = mouse.getPos()
    return clickedImage, prevMouseLocation

# Checks for a single tap on an image
# Does this by asking: has the "mouse" moved? (= yes if a tap was received)
# And: If so, is the "mouse" within the image?
def checkForTapOnImages(mouse, images, prevMouseLocation):
    clickedImage = None
    mouse_location = mouse.getPos()
    # If the mouse moved... (check x and y coords)
    if not(mouse_location[0] == prevMouseLocation[0] and mouse_location[1] == prevMouseLocation[1]):
        # If the mouse is within one of the images...
        for image in images:
            if image.contains(mouse):
                clickedImage = image
                prevMouseLocation = mouse_location # Update for the next check
    return clickedImage, prevMouseLocation

def checkForTapAnywhere(mouse, prevMouseLocation):
    tapped = False
    mouse_location = mouse.getPos()
    # If the mouse moved... (check x and y coords)
    if not(mouse_location[0] == prevMouseLocation[0] and mouse_location[1] == prevMouseLocation[1]):
        tapped = True
    
    prevMouseLocation = mouse_location

    return tapped, prevMouseLocation

def checkForClickAnywhere(mouse, prevMouseLocation):
    clicked = False
    if any(mouse.getPressed()):
        clicked = True
        prevMouseLocation = mouse.getPos()
        while any(mouse.getPressed()): # Wait for the click to end before proceeding
            pass
    
    return clicked, prevMouseLocation

def checkForInputAnywhere(mouse, prevMouseLocation, USER_INPUT_DEVICE):
    if USER_INPUT_DEVICE == 'mouse':
        inputReceived, prevMouseLocation = checkForClickAnywhere(mouse, prevMouseLocation)
    elif USER_INPUT_DEVICE == 'touch':
        inputReceived, prevMouseLocation = checkForTapAnywhere(mouse, prevMouseLocation)
    else:
        print("Error: User input device is not set to a valid value (mouse or touch). Quitting...")
        core.quit()
    return inputReceived, prevMouseLocation

# Displays a buffer screen with given text, and only proceeds once the user clicks
def displayBufferScreen(mainWindow, mouse, WINDOW_WIDTH, WINDOW_HEIGHT, bufferText, USER_INPUT_DEVICE, quitFunction):
    displayTextScreen(mainWindow, WINDOW_WIDTH, WINDOW_HEIGHT, bufferText)
    inputReceived, prevMouseLocation = checkForInputAnywhere(mouse, mouse.getPos(), USER_INPUT_DEVICE)
    while not inputReceived: # Wait for user input (anywhere on screen)
        listenForQuit(quitFunction) # Allow the user to quit at this stage, too
        inputReceived, prevMouseLocation = checkForInputAnywhere(mouse, prevMouseLocation, USER_INPUT_DEVICE)

# Displays a fixation cross on the screen for 1500ms 
def displayFixationCrossScreen(mainWindow, WINDOW_HEIGHT):
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

# Displays a dialog box to get subject number
def displaySubjIDDialog():
    guiBox = gui.Dlg()
    guiBox.addField("Subject ID:")
    guiBox.show()
    subjID = int(guiBox.data[0])
    return subjID

# Displays a screen with given text (how to proceed from this screen is not a part of this function!)
def displayTextScreen(mainWindow, WINDOW_WIDTH, WINDOW_HEIGHT, waitText):
    textScreen = visual.TextStim(
        mainWindow,
        text = waitText,
        pos = (0.0, 0.0),
        height = WINDOW_HEIGHT / 20,
        wrapWidth = WINDOW_WIDTH,
        color = "black")
    textScreen.draw()
    mainWindow.flip()

# Listens for a keyboard shortcut that tells us to quit the experiment - if detected, it runs the given quit routine
def listenForQuit(quitFunction):
    quitKey = 'escape'
    keys = event.getKeys()
    if quitKey in keys:
        quitFunction()
    

def setUpEyeTracker(mainWindow):
    iohub_config = {'eyetracker.hw.tobii.EyeTracker': {'name': 'tracker', 'calibration': {'type': 'THREE_POINTS'}}}
    io = launchHubServer(window = mainWindow, **iohub_config)
    tracker = io.getDevice('tracker')

    return tracker
