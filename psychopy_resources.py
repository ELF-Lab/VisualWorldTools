from psychopy import core, event, gui, visual

def checkForInput(mouse, images, prevMouseLocation, USING_MOUSE):
    if USING_MOUSE:
        clickedImage, prevMouseLocation = checkForClick(mouse, images, prevMouseLocation)
    else: # Using the touch screen
        clickedImage, prevMouseLocation = checkForTap(mouse, images, prevMouseLocation)
    return clickedImage, prevMouseLocation

# Given a list of images, returns the one that is being clicked (or None)
# Hold for the duration of the click - so that when this function ends, the click is over
def checkForClick(mouse, images, prevMouseLocation):
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
def checkForTap(mouse, images, prevMouseLocation):
    clickedImage = None
    mouse_location = mouse.getPos()
    # If the mouse moved... (check x and y coords)
    if not(mouse_location[0] == prevMouseLocation[0] and mouse_location[1] == prevMouseLocation[1]):
        # If the mouse is within one of the images...
        for image in images:
            if image.contains(mouse):
                clickedImage = image
            prevMouseLocation = mouse.getPos() # Update for the next check
    return clickedImage, prevMouseLocation

# Displays a buffer screen with given text, and only proceeds once the user clicks
def displayBufferScreen(mainWindow, mouse, WINDOW_WIDTH, WINDOW_HEIGHT, bufferText):
    bufferScreen = visual.TextStim(mainWindow, text = bufferText, pos = (0.0, 0.0), height = WINDOW_HEIGHT / 20, wrapWidth = WINDOW_WIDTH, color = "black")
    while mouse.getPressed()[0] == 0: # Wait for mouse click (anywhere)
        bufferScreen.draw()
        mainWindow.flip()  

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

# Listens for a keyboard shortcut that tells us to quit the experiment
def listenForQuit():
    quitKey = 'escape'
    keys = event.getKeys()
    if quitKey in keys:
        core.quit()