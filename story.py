# This file is part of For The New Lunar Republic.

# For The New Lunar Republic is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# For The New Lunar Republic is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with For The New Lunar Republic.  If not, see <http://www.gnu.org/licenses/>.

import sys, os
import logging

log = logging.getLogger(__name__)

currentlyLoadedFolder = "story\Alpha Testing"
sys.path.append(currentlyLoadedFolder) #TODO possibly change this.

import pygame
from pygame.locals import *
import elementtree.ElementTree as ET

import dialog
import cutscenes

import everyFrame

log.debug("Module initialized.")


class DialogCutscene(object):
    """These are the cutscenes where characters talk."""
    
    def __init__(self, XMLElement, parent):
        self.XMLElement = XMLElement
        
        self.id = self.XMLElement.attrib["id"]
        
        self.parent = parent
            
        self.onScreen = False
        
        self.currentDialogLineIndex = 0
        self.currentSectionIndex = 0
        
        self.contPromptImage = pygame.image.load(os.path.join("images","Dialog","ContinuePrompt.png")).convert_alpha()
        self.contPromptTimer = 0
        self.contPromptInterval = 250
        self.contPromptShowing = False
        
        self.dialogOutlineImage = pygame.image.load(os.path.join("images","Dialog","Outline.png")).convert_alpha()
        self.dialogRect = self.dialogOutlineImage.get_rect()
        self.dialogRect.centerx = self.parent.boundingRect.centerx
        # self.dialogRect.bottom = self.parent.boundingRect.bottom - 15 # Makes it at the target position
        self.dialogRect.top = self.parent.boundingRect.bottom
        self.dialogPortraitOutlineImage = pygame.image.load(os.path.join("images","Dialog","PortraitOutline.png")).convert_alpha()
        
        self.dialogOffset = [0.,0.]
        self.dialogTargetY = self.parent.boundingRect.bottom - 15 # The bottom of the dialog box
        self.dialogMoveSpeed = 200
        self.dialogAlpha = 0
        self.dialogFadeTime = 1000
        self.dialogFadeTimer = 0
        
        
        self.portraitRect = self.dialogPortraitOutlineImage.get_rect()
        # self.portraitRect.left = self.dialogRect.left The target position.
        self.portraitRect.right = self.parent.boundingRect.left
        self.portraitRect.bottom = self.dialogTargetY-self.dialogRect.height-25
        
        self.portraitOffset = [0.,0.]
        self.portraitTargetX = self.dialogRect.left # The left of the portrait box.
        self.portraitMoveSpeed = 300
        self.portraitAlpha = 0
        self.portraitFadeTime = 1000
        self.portraitFadeTimer = 0
        
        self.piecesMoving = False
        self.movingOff = False
        self.moveToNextSection = False
        
        self.sections = []
        # self.dialogLines = []
        self.backgrounds = {}
        
        # Load the info from the XML file.
        for element in self.XMLElement:
            if element.tag == "background":
                for e in element:
                    if e.tag == "name":
                        id = e.text
                    elif e.tag == "file":
                        filename = e.text
                self.backgrounds[id] = pygame.image.load(os.path.join("story",self.parent.chapter,filename)).convert()
            elif element.tag == "section":
                speakerName = None
                bgName = None
                bgFadeIn = None
                bgFadeOut = None
                for e in element:
                    if e.tag == "id":
                        id = e.text
                    elif e.tag == "speaker":
                        speakerName = e.text
                    elif e.tag == "bg":
                        for elem in e:
                            if elem.tag == "id":
                                bgName = elem.text
                            elif elem.tag == "fadein":
                                bgFadeIn = elem.text
                            elif elem.tag == "fadeout":
                                bgFadeOut = elem.text
                    elif e.tag == "content":
                        # Now the meat of it all. The actual dialog lines.
                        newSection = []
                        lineList = []
                        currentMood = "Normal"
                        i = 0
                        
                        # Get the number of lines that aren't mood adjustments
                        length = 0
                        for l in e:
                            if l.tag == "line":
                                length += 1
                        
                        for line in e:
                            if line.tag == "mood":
                                currentMood = line.text
                            elif line.tag == "line":
                                lineList.append(line.text)
                                if "speed" in line.attrib:
                                    speed = line.attrib["speed"] # The default is used if it's not specified.
                                else:
                                    speed = 1
                                
                                thisbgFadeIn = None
                                thisbgFadeOut = None
                                if i == 0: # If it's the first line
                                    thisbgFadeIn = bgFadeIn
                                if i == length-1: # If it's the last line
                                    thisbgFadeOut = bgFadeOut
                                newLine = dialog.LineObject(self, id, speakerName, currentMood, speed, line.text, self.parent.font, self.parent.boundingRect, bgName, thisbgFadeIn, thisbgFadeOut)
                                newSection.append(newLine)
                                
                                i += 1
                        self.sections.append(newSection)
                
        
        self.skipKey = K_RETURN
        self.skipping = False
        
        self.continueInterval = 1500
        self.continueTimer = 0
        
        self.done = False
            
    def update(self, time, keyEvents, mouseEvents):
        if self.onScreen:
            for e in keyEvents:
                if e.type == KEYDOWN:
                    if e.key == self.skipKey:
                        self.skipping = True
            
            self.section = self.sections[self.currentSectionIndex]
            
            self.section[self.currentDialogLineIndex].update(time, keyEvents, mouseEvents)
            
            self.piecesMoving = False
            
            #TODO Make the dialog pieces fade in and out.
            # Moving on
            if not self.section[self.currentDialogLineIndex].reachedTargetPos and not self.section[self.currentDialogLineIndex].fading:
                self.dialogOffset[1] -= self.dialogMoveSpeed*10*time/1000.
                if self.dialogOffset[1] > self.dialogTargetY:
                    self.dialogOffset[1] = self.dialogTargetY
                self.piecesMoving = True
                
                if self.dialogAlpha < 255:
                    self.dialogFadeTimer += time
                    if not self.dialogFadeTimer >= self.dialogFadeTime:
                        self.dialogAlpha = (self.dialogFadeTimer*1./self.dialogFadeTime*1.*100)*255/100
                    else:
                        self.dialogAlpha = 255
                    if self.dialogAlpha > 255:
                        self.dialogAlpha = 255
            if self.section[self.currentDialogLineIndex].reachedTargetPos and not self.movingOff:
                if -self.dialogOffset[1] > self.parent.boundingRect.bottom-self.dialogTargetY-self.dialogRect.height:
                    self.dialogOffset[1] = -(self.parent.boundingRect.bottom-self.dialogTargetY+self.dialogRect.height)
                
            if not self.section[self.currentDialogLineIndex].portraitReachedTargetPos and not self.section[self.currentDialogLineIndex].fading:
                self.portraitOffset[0] += self.portraitMoveSpeed*10*time/1000.
                if self.portraitOffset[0] > self.portraitTargetX+self.portraitRect.width:
                    self.portraitOffset[0] = self.portraitTargetX+self.portraitRect.width
                self.piecesMoving = True
                
                if self.portraitAlpha < 255:
                    self.portraitFadeTimer += time
                    if not self.portraitFadeTimer >= self.portraitFadeTime:
                        self.portraitAlpha = (self.portraitFadeTimer*1./self.portraitFadeTime*1.*100)*255/100
                    else:
                        self.portraitAlpha = 255
                    if self.portraitAlpha > 255:
                        self.portraitAlpha = 255
            if self.section[self.currentDialogLineIndex].portraitReachedTargetPos and not self.movingOff:
                if self.portraitOffset[0] > self.parent.boundingRect.left+self.portraitTargetX+self.portraitRect.width:
                    self.portraitOffset[0] = self.parent.boundingRect.left+self.portraitTargetX+self.portraitRect.width
                
            # Moving off
            if self.dialogOffset[1] <= 0 and self.movingOff:
                self.dialogOffset[1] += self.dialogMoveSpeed*10*time/1000.
                self.piecesMoving = True
                
            if self.portraitOffset[0] >= 0 and self.movingOff:
                self.portraitOffset[0] -= self.portraitMoveSpeed*10*time/1000.
                self.piecesMoving = True
            
            if self.dialogOffset[1] >= 0 and self.portraitOffset[0] <= 0 and self.movingOff:
                self.movingOff = False
                self.section[self.currentDialogLineIndex].reachedTargetPos = False
                self.section[self.currentDialogLineIndex].portraitReachedTargetPos = False
            
            if self.dialogOffset[1] >= 0 and self.portraitOffset[0] <= 0 and not self.section[self.currentDialogLineIndex].fading:
                self.moveToNextSection = True
            
            # If it's done displaying the text of the line
            if self.section[self.currentDialogLineIndex].done:
                self.contPromptTimer += time # For toggling the showing of the prompt
                if self.contPromptTimer >= self.contPromptInterval:
                    self.contPromptTimer = 0
                    self.contPromptShowing = not self.contPromptShowing
                    
                # Makes you read the whole thing without skipping, but then waits
                self.continueTimer += time
                # Check to see if the line has reached the point where it lets you skip.
                # if self.continueTimer >= self.section[self.currentDialogLineIndex].pauseTime:
                if self.skipping: # Remember that this is true if the user has pressed the skip key (Or I suppose the game could handle it manually later too.)
                    self.continueTimer = 0
                    self.skipping = False
                    if not self.piecesMoving and not self.movingOff:
                        self.currentDialogLineIndex += 1
                # else:
                    # self.contPromptShowing = False # Force the prompt off because the line isn't ready to be skipped.
            else:
                # If it's not done showing all the text yet.
                self.contPromptShowing = False
                self.skipping = False
            
            if self.moveToNextSection:
                self.currentSectionIndex += 1
                    
                if self.currentSectionIndex > len(self.sections)-1: # The end of the dialog.
                    self.done = True
                    self.currentDialogLineIndex -= 1
                else:
                    self.currentDialogLineIndex = 0
                self.moveToNextSection = False
    
            if self.onScreen:
                if self.currentDialogLineIndex > len(self.section)-1: # If we've reached the end of the section   
                    # Move the dialog components back off the screen.
                    if self.dialogOffset[1] <= 0:
                        self.movingOff = True
                        self.currentDialogLineIndex -= 1
                    elif self.portraitOffset[0] >= 0:
                        self.movingOff = True
                        self.currentDialogLineIndex -= 1
                        
            
    def draw(self, surface):
        if self.onScreen:
            # Blit the dialog line's background first.
            currentBGAlpha = self.section[self.currentDialogLineIndex].bg.get_alpha()
            goalAlpha = self.section[self.currentDialogLineIndex].bgAlpha
            if not currentBGAlpha == goalAlpha:
                # It's not done showing yet, so set the alpha of the background to match what the background should be currently
                self.section[self.currentDialogLineIndex].bg.set_alpha(self.section[self.currentDialogLineIndex].bgAlpha)
                
            surface.blit(self.section[self.currentDialogLineIndex].bg, (self.section[self.currentDialogLineIndex].boundingRect.topleft))
            self.section[self.currentDialogLineIndex].draw(surface)
            # If it waits for the user or if it is type two waiting and is done.
            if self.contPromptShowing and self.section[self.currentDialogLineIndex].done:
                surface.blit(self.contPromptImage, (self.parent.boundingRect.left+940+self.dialogOffset[0],self.parent.boundingRect.bottom+175+self.dialogOffset[1]))
            
    def printOut(self):
        for line in self.section:
            sys.stdout.write(line.speakerName+": ")
            for char in line.text:
                sys.stdout.write(char)
                waitTime = int(line.charInterval/line.speedMult)
                pygame.time.delay(waitTime)
            sys.stdout.write("\n\n")
            if line.waitForUser == 1:
                raw_input()
    
class InGameDialogSequence(DialogCutscene):
    pass

class CutAwayDialogSequence(DialogCutscene):
    pass

class Story(object):
    
    def __init__(self, chapter, dialogFont, boundingRect, cutsceneVolume, cutsceneInfoFont, sound):
        self.currentlyLoadedFolder = "story\Alpha Testing"
        self.font = dialogFont
        self.boundingRect = boundingRect
        self.changeChapter(chapter)
        
        self.cutsceneVolume = cutsceneVolume
        self.cutsceneInfoFont = cutsceneInfoFont
        self.sound = sound
        
        self.cutscenes = []
        
        self.currentlyPlayingCutscene = None
        self.currentlyPlayingDialogSequence = None
        self.needsToFade = False # Used by main.py. Main.py also sets it back to false.
        
    def changeChapter(self, chapter):
        self.flags = {}
        
        self.chapter = chapter
        self.folder = os.path.join("story",self.chapter)
        self.reloadFolder(self.folder)
        
        self.loadFlags()
        self.loadDialogSequences()

    def reloadFolder(self, newFolder):
        sys.path[sys.path.index(self.currentlyLoadedFolder)] = newFolder
        self.currentlyLoadedFolder = newFolder
        reload(everyFrame)
        
    def loadFlags(self):
        fileName = os.path.join(self.folder, "InitialFlags")
        theFile = file(fileName, 'r').readlines()
        
        for line in theFile:
            key = line[:line.index(":")]
            value = line[line.index(":")+1:]
            try:
                value = float(value)
            except ValueError:
                pass
            self.flags[key] = value
            
    def loadCutscene(self, name):
        folderName = os.path.join(self.folder, "cutscenes")
        
        newCS = cutscenes.Cutscene(self, name, self.cutsceneVolume, self.boundingRect, self.cutsceneInfoFont, self.sound)
        newCS.load()
        
        self.cutscenes.append(newCS)
        
    def playCutscene(self, name):
        for c in self.cutscenes:
            if c.name == name:
                self.currentlyPlayingCutscene = c
                break
                
    def findCutscene(self, name):
        for c in self.cutscenes:
            if c.name == name:
                return c
        return None # If it can't be found.
            
    def loadDialogSequences(self):
        fileName = os.path.join(self.folder, "Dialog.xml")
        tree = ET.parse(fileName)
        root = tree.getroot()
        
        self.dialogSequences = []
        
        for dialogSequence in root:
            newScene = CutAwayDialogSequence(dialogSequence, self)
            self.dialogSequences.append(newScene)
    
    def playDialogSequence(self, id):
        for dialogSequence in self.dialogSequences:
            if dialogSequence.id == id:
                dialogSequence.onScreen = True
                self.currentlyPlayingDialogSequence = dialogSequence
                
    def findDialogSequence(self, id):
        for dialogSequence in self.dialogSequences:
            if dialogSequence.id == id:
                return dialogSequence
        return None # If it can't be found.
    
    def update(self, time, keyEvents, mouseEvents, subState, currentState, currentLevel):
        everyFrame.main(time, keyEvents, mouseEvents, self, subState, currentState, currentLevel)
        
        if not self.currentlyPlayingCutscene == None:
            if not self.currentlyPlayingCutscene.done: # If there's a cutscene playing.
                self.currentlyPlayingCutscene.update(time, keyEvents)
            else:
                self.currentlyPlayingCutscene = None
                self.needsToFade = True
            
        if not self.currentlyPlayingDialogSequence == None:
            if not self.currentlyPlayingDialogSequence.done == True:
                self.currentlyPlayingDialogSequence.update(time, keyEvents, mouseEvents)
            else:
                self.currentlyPlayingDialogSequence = None
                self.needsToFade = True
            
        # if (not self.currentlyPlayingCutscene == None and not self.currentlyPlayingCutscene == None) and (not self.currentlyPlayingDialogSequence == None and not self.currentlyPlayingDialogSequence.done == True):
            # self.needsToFade = True
            # print "Both are done so fading."
            
    def draw(self, surface):
        for dialogSequence in self.dialogSequences:
            dialogSequence.draw(surface)
            
        if not self.currentlyPlayingCutscene == None:
            self.currentlyPlayingCutscene.draw(surface)