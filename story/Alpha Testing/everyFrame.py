# This is a file that gets run every frame by the story object.
# It is given access to the flags dictionary. It can modify this dictionary and check it as much as it wants to.
# This function can even create dialog instances.
# If can also gain access to the player ship and the current level's boss if the player is in gameplay.

isAlpha = "YES I AM ALPHA"

def main(time, keyEvents, mouseEvents, storyObject, subState, currentState, currentLevel):
    if subState.name == "cutscene":
        if not storyObject.flags["OpeningCutsceneHasPlayed"]:
            storyObject.loadCutscene("Opening Cutscene")
            storyObject.playCutscene("Opening Cutscene")
            
            storyObject.flags["OpeningCutsceneHasPlayed"] = True
        openingCutscene = storyObject.findCutscene("Opening Cutscene")
        
        if not openingCutscene == None:
            if storyObject.findCutscene("Opening Cutscene").done:
                subState.name = "dialog"
        else:
            subState.name = "dialog" # Can't find the cutscene, so skip ahead to dialog to keep it going.
    elif subState.name == "dialog":
        if not storyObject.flags["OpeningDialogHasPlayed"]:
            if not storyObject.findDialogSequence("Opening") == None:
                if storyObject.findDialogSequence("Opening").done:
                    storyObject.flags["OpeningDialogHasPlayed"] = 1
                    currentState.vars["Level"] = "Test Story"
                    currentState.vars["Ship"] = "RainbowDash"
                else:
                    storyObject.playDialogSequence("Opening")
        else:
            storyObject.needsToFade = True
        
        if not storyObject.flags["PlaceHolderPlayed"]:
            if not storyObject.findDialogSequence("PlaceHolder") == None:
                if storyObject.findDialogSequence("PlaceHolder").done:
                    storyObject.flags["PlaceHolderPlayed"] = 1
                    currentState.vars["Level"] = "Test Story"
                    currentState.vars["Ship"] = "RainbowDash"
                else:
                    storyObject.playDialogSequence("PlaceHolder")
    elif subState.name == "level":
        if not currentLevel == None:
            if currentLevel.waitingForBoss:
                if storyObject.flags["AlertedToBoss"] == 0:
                    storyObject.playDialogSequence("InGamePlaceholder")
                    storyObject.flags["AlertedToBoss"] = 1
                if storyObject.currentlyPlayingDialogSequence == None and storyObject.flags["AlertedToBoss"] == 1:
                    currentLevel.readyForBoss = True