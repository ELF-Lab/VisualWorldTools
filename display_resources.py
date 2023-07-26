from random import randint
from pathlib import *
from psychopy import core, event, gui, visual
from config import *
# Ideally we should minimze imports from here, but there is some overlap between what's on screen and what TPL needs to know.
from eye_tracking_resources import finishDisplayingStimulus

# These need to be updated throughout the experiment, to send messages about what is being shown on screen
currentDisplay = None
currentDisplayStartTime = None

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

def checkForInputOnImages(mouse, images, prevMouseLocation):
    if USER_INPUT_DEVICE == 'mouse':
        clickedImage, prevMouseLocation = checkForClickOnImages(mouse, images, prevMouseLocation)
    elif USER_INPUT_DEVICE == 'touch':
        clickedImage, prevMouseLocation = checkForTapOnImages(mouse, images, prevMouseLocation)
    else:
        print("Error: User input device is not set to a valid value (mouse or touch). Quitting...")
        core.quit()
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

def checkForClickAnywhere(mouse, prevMouseLocation):
    clicked = False
    if any(mouse.getPressed()):
        clicked = True
        prevMouseLocation = mouse.getPos()
        while any(mouse.getPressed()): # Wait for the click to end before proceeding
            pass
    
    return clicked, prevMouseLocation

def checkForInputAnywhere(mouse, prevMouseLocation):
    if USER_INPUT_DEVICE == 'mouse':
        inputReceived, prevMouseLocation = checkForClickAnywhere(mouse, prevMouseLocation)
    elif USER_INPUT_DEVICE == 'touch':
        inputReceived, prevMouseLocation = checkForTapAnywhere(mouse, prevMouseLocation)
    else:
        print("Error: User input device is not set to a valid value (mouse or touch). Quitting...")
        core.quit()
    return inputReceived, prevMouseLocation

def checkForTapAnywhere(mouse, prevMouseLocation):
    tapped = False
    mouse_location = mouse.getPos()
    # If the mouse moved... (check x and y coords)
    if not(mouse_location[0] == prevMouseLocation[0] and mouse_location[1] == prevMouseLocation[1]):
        tapped = True

    prevMouseLocation = mouse_location

    return tapped, prevMouseLocation

def clearClicksAndEvents(mouse):
    mouse.clickReset()
    event.clearEvents()

def displayBlankScreen(recorder, recording, mediaInfo, mainWindow):
    if EYETRACKING_ON:
        switchDisplays('blank', recorder, recording, mediaInfo)
    mainWindow.flip()

# Displays a buffer screen with given text, and only proceeds once the user clicks
def displayBufferScreen(recorder, recording, mediaInfo, mainWindow, mouse, bufferText, quitFunction):
    displayTextScreen(recorder, recording, mediaInfo, mainWindow, bufferText, "buffer")
    inputReceived, prevMouseLocation = checkForInputAnywhere(mouse, mouse.getPos())
    while not inputReceived: # Wait for user input (anywhere on screen)
        listenForQuit(quitFunction) # Allow the user to quit at this stage, too
        inputReceived, prevMouseLocation = checkForInputAnywhere(mouse, prevMouseLocation)

# Displays a fixation cross on the screen for 1500ms 
def displayFixationCrossScreen(recorder, recording, mediaInfo, mainWindow):
    if EYETRACKING_ON:
        switchDisplays('fixation_cross', recorder, recording, mediaInfo)
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

def displayStimuli(recorder, recording, mediaInfo, stimuli_list, mainWindow):
    if EYETRACKING_ON:
        switchDisplays('stimuli', recorder, recording, mediaInfo)
    for stimulus in stimuli_list:
        stimulus.draw()
    mainWindow.flip()

# Displays a dialog box to get subject number
def displaySubjIDDialog():
    guiBox = gui.Dlg()
    guiBox.addField("Subject ID:")
    guiBox.show()
    subjID = int(guiBox.data[0])
    return subjID

# Displays a screen with given text (how to proceed from this screen is not a part of this function!)
# displayName can be None (if this is not a display for the recording process, e.g. the quitting screen)
def displayTextScreen(recorder, recording, mediaInfo, mainWindow, textToDisplay, displayName):
    if EYETRACKING_ON:
        switchDisplays(displayName, recorder, recording, mediaInfo)
    textScreen = visual.TextStim(
        mainWindow,
        text = textToDisplay,
        pos = (0.0, 0.0),
        height = WINDOW_HEIGHT / 20,
        wrapWidth = WINDOW_WIDTH,
        color = "black")
    textScreen.draw()
    mainWindow.flip()
    
# Get the images to be displayed for the given trial.
def getImages(imageFileNames, imageSize, checkmarkSize, repeatIconSize, mainWindow):
    numberOfImages = len(imageFileNames)

    # Create an ImageStim object for each image stimuli, and a unique check object for each image - even though they're all the same check image, they'll end up having different positions
    images = []
    checks = []
    for i in range(0, numberOfImages):
        images.append(visual.ImageStim(win = mainWindow, image = Path.cwd()/"visualStims"/str(imageFileNames[i]), units = "pix", size = imageSize))
        checks.append(visual.ImageStim(win = mainWindow, image = Path.cwd()/"checkmark.png", units = "pix", size = checkmarkSize))

    repeatIcon = visual.ImageStim(win = mainWindow, image = Path.cwd()/"repeat.png", units = "pix", size = repeatIconSize)
    
    selectionBox = visual.Rect(win = mainWindow, lineWidth = 2.5, lineColor = "#7AC043", fillColor = None, units = "pix", size = imageSize)

    return images, checks, repeatIcon, selectionBox

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

def handleStimuliClick(imageClicked, images, checks, selectionBox, repeatIcon, trialClock, clicks, recorder, recording, mediaInfo, mainWindow):
    numberOfImages = len(images)

    # Determine the names of the images we're dealing with. These name lists match their order in the experimental items input file!
    ONE_IMAGE_NAME = ["agent"]
    TWO_IMAGE_NAMES = ["agent", "patient"]
    THREE_IMAGE_NAMES = ["agent", "patient", "distractor"]
    FOUR_IMAGE_NAMES = ["agent", "patient", "distractorA", "distractorB"]
    NAME_LISTS = {
        1: ONE_IMAGE_NAME,
        2: TWO_IMAGE_NAMES,
        3: THREE_IMAGE_NAMES,
        4: FOUR_IMAGE_NAMES
    }
    assert numberOfImages in NAME_LISTS.keys()
    imageNames = NAME_LISTS[numberOfImages]

    # Figure out which image was clicked
    trialDur = trialClock.getTime()
    selectionBox.setPos(imageClicked.pos)
    for i, image in enumerate(images):
        if imageClicked == image:
            pic = imageNames[i]
            check = checks[i]

    response = [pic, trialDur]
    clicks.append(response)

    # Re-draw to include the selection box and checkmark
    displayStimuli(recorder, recording, mediaInfo, images + [repeatIcon, selectionBox, check], mainWindow)
    
    return check

# Listens for a keyboard shortcut that tells us to quit the experiment - if detected, it runs the given quit routine
def listenForQuit(quitFunction):
    quitKey = 'escape'
    keys = event.getKeys()
    if quitKey in keys:
        quitFunction()

def listenForRepeat(repeatIcon, prevMouseLocation, audio, trialClock, clicks, mouse):
    repeatClicked, prevMouseLocation = checkForInputOnImages(mouse, [repeatIcon], prevMouseLocation)
    if repeatClicked:
        playSound(audio)
        pic = "replay"
        trialDur = trialClock.getTime()
        response = [pic, trialDur]
        clicks.append(response)

    return prevMouseLocation

def playSound(audio):
    audio.play()

    # Note that setPos defines the position of the image's /centre/, and screen positions are determined based on the /centre/ of the screen being (0,0)
def setImagePositions(imageSize, checkmarkSize, images, checks, repeatIcon, IMAGE_OFFSET_FROM_EDGE):
    numberOfImages = len(images)

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
    # Position the checkmarks just above/below the image. This offset should be added/subtracted from the corresponding image's position.
    checkOffset = imageSize / 2 + checkmarkSize / 2

    # Randomly determine the images' order (and therfore, positions)
    random_ordering_of_images = getRandomImageOrder(numberOfImages)

    # Determine the image positions we'll be using, based on the # of images
    ONE_POSITION = [[centre, centre]]
    TWO_POSITIONS = [[left, centre], [right, centre]]
    THREE_POSITIONS = [[left, top], [right, top], [centre, bottom]]
    FOUR_POSITIONS = [[left, top], [right, top], [left, bottom], [right, bottom]]
    POSITION_LISTS = {
        1: ONE_POSITION,
        2: TWO_POSITIONS,
        3: THREE_POSITIONS,
        4: FOUR_POSITIONS
    }
    assert numberOfImages in POSITION_LISTS.keys()
    imagePositions = POSITION_LISTS[numberOfImages]

    # Now set their positions based on that random order!
    for i, imagePosition in enumerate(imagePositions):
        images[random_ordering_of_images[i]].setPos(imagePosition)
        # Put the check below the image UNLESS the image is already at the bottom of the screen, in which case put the check above the image
        checks[random_ordering_of_images[i]].setPos([imagePosition[0], imagePosition[1] - checkOffset if imagePosition[1] != bottom else imagePosition[1] + checkOffset])

    return images, checks, repeatIcon

# Either the new or current display can be None, indicating this is the last or first display
# If newDisplayName = None, we only finish with the previous display, we don't add a new one
# If currentDisplay = None, we do not finish any previous display (because we're saying there isn't one!), we merely note the start time of this new screen
# If both are None, we are neither beginning nor finishing with a screen (i.e. this is a dummy call - we don't want TPL to know about this display at all)
def switchDisplays(newDisplayName, recorder, recording, mediaInfo):
    global currentDisplay
    global currentDisplayStartTime
    # Store the start time for the new display (and finish with the old one, if there was one).
    if currentDisplay == None and newDisplayName == None: # No switch at all
        pass
    elif currentDisplay == None: # No previous display, but we're starting a new one
        currentDisplayStartTime = int((recorder.get_time_stamp())['timestamp'])
    else: # We are finishing with a previous display
        currentDisplayStartTime = finishDisplayingStimulus(currentDisplayStartTime, mediaInfo[currentDisplay], recorder, recording)
    currentDisplay = newDisplayName # Update the current display
