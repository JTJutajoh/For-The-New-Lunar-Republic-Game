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

import pygame
from pygame.locals import *

log.debug("Module initialized.")

bm = pygame.time.Clock()

class TextObject(object):
    
    def __init__(self, text, font, location, color, times, fadeTimes, letterRate, letterFadeRate, parent):
        self.parent = parent
        
        self.letterRate = letterRate
        self.letterFadeRate = letterFadeRate
        self.counter = 0
        self.currentLetterIndex = 0
        
        self.imageList = []
    
        self.origText = text
        self.text = ""
        self.font = font
        self.metrics = self.font.metrics(self.origText)
        self.pos = location
        self.color = color
        
        if not self.letterRate == 0:
            self.stringList = []
            i = 0
            for char in self.origText:
                self.stringList.append([char, 0, self.metrics[i][1], self.metrics[i][3], self.metrics[i][4]])
                i+=1
        
        self.blendColor = (100,100,100)
        if not self.letterRate == 0:
            self.image = pygame.surface.Surface(self.font.render(self.origText, True, self.color, self.blendColor).get_rect().size)#.convert()
        else:
            self.image = self.font.render(self.origText, True, self.color, self.blendColor)#.convert()
        self.image.set_colorkey(self.blendColor)
        self.rect = self.font.render(self.origText, True, self.color, self.blendColor).get_rect()
        self.rect.topleft = self.pos
        
        self.startTime = times[0]*1000
        self.endTime = times[1]*1000
        
        self.fadeInTime = fadeTimes[0]
        self.fadeOutTime = fadeTimes[1]
        
        if self.letterRate == 0:
            self.opacity = 0
        else:
            self.opacity = 255
        
    def update(self, time, timer):
        if not self.letterRate == 0 and timer >= self.startTime and timer < self.endTime:
            if not len(self.text) == len(self.origText):
                self.counter += time
                if self.counter >= self.letterRate:
                    self.counter = 0
                    self.text = self.text + self.origText[self.currentLetterIndex]
                    
                    self.stringList[self.currentLetterIndex][1] = 1
                    
                    self.currentLetterIndex += 1
                
            self.image.fill(self.blendColor)
            self.imageList = []
            x = 0
            for letter in self.stringList:
                if letter[1] > 0: # 1 == alpha
                    letter[1] += self.letterFadeRate*100*time/1000. # *100 just so that it doesn't have to be an absurdly large number.
                    if letter[1] > 255: letter[1] = 255
                    letterSurf = self.font.render(letter[0], True, self.color, self.blendColor)
                    letterSurf.set_colorkey(self.blendColor)
                    letterSurf.set_alpha(letter[1])
                    self.imageList.append([letterSurf, x])
                    # self.image.blit(letterSurf, (x,0))
                    x+=letter[4] # Offset the letter by the font's metrics.
                # self.image = self.font.render(self.text, True, self.color, self.blendColor)
                # self.image.set_colorkey(self.blendColor)
        elif timer >= self.endTime:
            for letter in self.imageList:
                if letter[1] < 255:
                    letter[1] = 255
        
        # if self.letterRate == 0:
        if timer >= self.startTime and timer < self.endTime:
            if timer >= self.endTime-self.fadeOutTime:
                curFadeTime = self.endTime-timer
                percentage = 100.*(curFadeTime/self.fadeOutTime)
                self.opacity = percentage*255/100.
            elif self.opacity < 255 and self.letterRate == 0:
                if timer > self.startTime+self.fadeInTime: # If it's already supposed to be 100% opaque.
                    self.opacity = 255
                else:
                    curFadeTime = timer-self.startTime
                    percentage = 100.*(curFadeTime/self.fadeInTime)
                    self.opacity = percentage*255/100.
                
            self.image.set_alpha(self.opacity)
            
            
class FrameObject(object):

    def __init__(self, times, fadeTimes, number, parent):
        self.parent = parent
    
        self.startTime = times[0]*1000
        self.endTime = times[1]*1000
        self.fadeInTime = fadeTimes[0]
        self.fadeOutTime = fadeTimes[1]
        self.number = number
        
        self.image = pygame.image.load(os.path.join(self.parent.folderName,"Frame%i.png"%self.number)).convert()
        
        self.opacity = 0
        
    def update(self, time, timer):
        if timer > self.startTime and timer < self.endTime:
            if timer >= self.endTime-self.fadeOutTime:
                curFadeTime = self.endTime-timer
                percentage = 100.*(curFadeTime/self.fadeOutTime)
                self.opacity = percentage*255/100.
            elif self.opacity < 255:
                if timer > self.startTime+self.fadeInTime: # If it's already supposed to be 100% opaque.
                    self.opacity = 255
                else:
                    curFadeTime = timer-self.startTime
                    percentage = 100.*(curFadeTime/self.fadeInTime)
                    self.opacity = percentage*255/100.
                
            self.image.set_alpha(self.opacity)

class Cutscene(object):
    
    def __init__(self, storyParent, name, volume, rect, infoFont, sound=True, demo=False):
        self.demo = demo
    
        self.name = name
        
        self.rect = rect
            
        self.storyParent = storyParent
        
        if not self.demo:
            self.volume = volume
            self.sound = sound
            
            self.done = False
            
            self.infoFont = infoFont
            
            self.skipWaitTime = 2500
            self.skipWaiting = True
            self.skipWaitTimer = self.skipWaitTime-1000
    
    def loadTextInfo(self):
        infoFile = file(os.path.join(self.folderName, "textInfo"), 'r').readlines()
        self.textElements = []
        
        sections = []
        
        mainLineIndex = 0
        for line in infoFile:
            if line.strip() == "{":
                newList = []
                lineIndex = mainLineIndex+1
                while not infoFile[lineIndex].strip() == "}":
                    newList.append(infoFile[lineIndex].strip())
                    lineIndex += 1
                sections.append(newList)
            mainLineIndex += 1
            
        self.textObjects = []
        textInfos = []
            
        for textObject in sections:
            newTextInfo = {}
            for item in textObject:
                key = item[:item.index(":")]
                value = item[item.index(":")+1:]
                newTextInfo[key] = value
            textInfos.append(newTextInfo)
                
        for textInfo in textInfos:
            times = [0,0]
            color = [0,0,0]
            location = [0,0]
            fadeTimes = [0,0]
            letterRate = 0
            letterFadeRate = 25
            for key in textInfo.iterkeys():
                if key == "text":
                    text = textInfo[key]
                elif key == "starttime":
                   times[0] = float(textInfo[key])
                elif key == "endtime":
                    times[1] = float(textInfo[key])
                elif key == "x":
                    location[0] = int(textInfo[key])
                elif key == "y":
                    location[1] = int(textInfo[key])
                elif key == "font":
                    font = self.fonts[textInfo[key]]
                elif key == "r":
                    color[0] = int(textInfo[key])
                elif key == "g":
                    color[1] = int(textInfo[key])
                elif key == "b":
                    color[2] = int(textInfo[key])
                elif key == "fadeInTime":
                    fadeTimes[0] = int(textInfo[key])
                elif key == "fadeOutTime":
                    fadeTimes[1] = int(textInfo[key])
                elif key == "letterRate":
                    letterRate = int(textInfo[key])
                elif key == "letterFadeRate":
                    letterFadeRate = int(textInfo[key])
            newTextObject = TextObject(text, font, location, color, times, fadeTimes, letterRate, letterFadeRate, self)
            self.textObjects.append(newTextObject)
            
    def loadFrameInfo(self):
        theFile = file(os.path.join(self.folderName, "frameInfo"), 'r').readlines()
        
        self.frames = []
        self.currentFrame = 0
        
        for line in theFile:
            thisLine = []
            thisIndex = 0
            lastIndex = 0
            for char in line:
                if char == ":":
                    thisLine.append(line[lastIndex:thisIndex])
                    
                    lastIndex = thisIndex+1
                thisIndex += 1
            times = (float(thisLine[1]),float(thisLine[2]))
            number = int(thisLine[0])
            fadeTimes = [int(thisLine[3]),int(thisLine[4])]
            self.frames.append(FrameObject(times, fadeTimes, number, self))
    
    def load(self):
        # First parse the general info file.
        if self.demo:
            self.folderName = os.path.join("story", self.storyParent, "cutscenes", self.name)
        else:
            self.folderName = os.path.join("story", self.storyParent.chapter, "cutscenes", self.name)
        infoFile = file(os.path.join(self.folderName, "info"), 'r').readlines()
        self.info = {}
        
        for line in infoFile:
            key = line[:line.index(":")].strip()
            value = line[line.index(":")+1:].strip()
            
            self.info[key] = value
        
        self.fonts = {}
        for item in self.info.iterkeys():
            if item == "music":
                self.song = os.path.join("music", self.info[item])
                pygame.mixer.music.load(self.song)
            elif item == "time":
                self.time = int(self.info[item])*1000. # Convert to milliseconds
                self.timer = 0
            else: # If it's a font
                fontFileName = self.info[item][:self.info[item].index(":")]
                self.fonts[item] = pygame.font.Font(os.path.join("fonts",fontFileName),int(self.info[item][self.info[item].index(":")+1:]))
                
                
        self.loadTextInfo()
        self.loadFrameInfo()
        
        # Load images
        self.surface = pygame.surface.Surface(self.rect.size)
        
        self.escapeKeyImage = pygame.image.load(os.path.join("images", "EscapeImage.png")).convert_alpha()
        
        log.info("Cutscene %s loaded."%self.name)
    
    def update(self, time, keyEvents):
        self.timer += time
        
        if self.timer >= self.time:
            self.done = True
            pygame.mixer.music.stop()
            log.info("Cutscene \"%s\" completed."%self.name)
        
        if not pygame.mixer.music.get_busy():
            if self.sound:
                log.debug("Started music for cutscene \"%s.\""%self.name)
                pygame.mixer.music.play()
            
        for e in keyEvents:
            if e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    if not self.skipWaiting:
                        self.skipWaiting = True
                        self.skipWaitTimer = 0
                    else:
                        self.done = True
                        pygame.mixer.music.stop()
                        log.info("User skipped cutscene \"%s\""%self.name)
        
        for textObject in self.textObjects:
            textObject.update(time, self.timer)
            
        for frame in self.frames:
            frame.update(time, self.timer)
                
        if self.skipWaiting:
            self.skipWaitTimer += time
            if self.skipWaitTimer >= self.skipWaitTime:
                self.skipWaiting = False
        
    def draw(self, surface):
        surface.fill((0,0,0))
        
        for frame in self.frames:
            if self.timer > frame.startTime and self.timer < frame.endTime:
                frameRect = frame.image.get_rect()
                frameRect.center = self.rect.center
                surface.blit(frame.image,frameRect.topleft)
        
        for textObject in self.textObjects:
            if self.timer > textObject.startTime and self.timer < textObject.endTime:
                for letter in textObject.imageList:
                    if textObject.opacity < 255:
                        letter[0].set_alpha(textObject.opacity)
                    surface.blit(letter[0], (textObject.rect.left+self.rect.left+letter[1], textObject.rect.top+self.rect.top))
                # surface.blit(textObject.image, (textObject.rect.left+self.rect.left, textObject.rect.top+self.rect.top))
        
        if self.skipWaiting:
            surface.blit(self.escapeKeyImage, (self.rect.left+10,self.rect.top+10))
            surface.blit(self.infoFont.render("To skip", True, (200,200,200)), (self.rect.left+70,self.rect.top+24))