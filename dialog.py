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

import sys, os, random
import logging

log = logging.getLogger(__name__)

import pygame
from pygame.locals import *
import elementtree.ElementTree as ET

class PauseObject(object):
    
    def __init__(self, parent, length, skipable, boundingRect, bgName, bgFade, bgFadeTime=None):
        self.length = int(length)
        self.skipable = int(skipable)
        
        self.parent = parent
        
        self.bg = self.parent.backgrounds[bgName]
        
        self.bgFade = bgFade
        if not bgFadeTime == None:
            self.bgFadeTime = int(bgFadeTime)
        else:
            self.bgFadeTime = None
        self.fadeTimer = 0
        if self.bgFade == "in":
            self.bgAlpha = 0
        elif self.bgFade == "out" or self.bgFade == "none":
            self.bgAlpha = 255
        
        if not self.bg == None:
            self.bg.set_alpha(self.bgAlpha)
        
        self.boundingRect = boundingRect
        
        self.timer = 0
        
        self.done = False
        
        self.dialogType = "pause"
        
    def update(self, time, keyEvents, mouseEvents):
        if self.bgFade == "in" and self.bgAlpha < 255:
            self.fadeTimer += time
            self.bgAlpha = (self.fadeTimer*1./self.bgFadeTime*1.*100)*255/100
        elif self.bgFade == "out" and self.bgAlpha > 0:
            if self.fadeTimer == 0 and not self.bgAlpha == 0:
                self.fadeTimer = self.bgFadeTime
            self.fadeTimer -= time
            self.bgAlpha = (self.fadeTimer*1./self.bgFadeTime*1.*100)*255/100
        elif self.bgFade == "none" and not self.bgAlpha == 255:
            self.bgAlpha = 255
    
        self.bg.set_alpha(self.bgAlpha)
        self.timer += time
        
        if self.timer >= self.length:
            self.done = True
            
    def draw(self, surface):
        pass
        # surface.blit(self.bg, (self.boundingRect.left,self.boundingRect.top))

class LineObject(object):
    
    def __init__(self, parent, id, speaker, mood, speedMult, text, font, boundingRect, bgName=None, bgFadeIn=None, bgFadeOut=None):
        self.parent = parent
        self.id = id
        
        self.speakerName = speaker
        self.mood = mood
        self.speedMult = float(speedMult)
        
        self.boundingRect = boundingRect
        if not bgName == None:
            self.bg = self.parent.backgrounds[bgName]
        else:
            self.bg = None
        
        self.bgFadeIn = bgFadeIn
        self.bgFadeOut = bgFadeOut
        self.fadeTimer = 0
            
        self.fading = False
        self.fadingOut = False
        
        if self.bgFadeIn == None: # If it doesn't fade in
            self.bgAlpha = 255
        else:
            self.bgAlpha = 0
            self.fading = True
            self.bgFadeIn = int(self.bgFadeIn)
        if not self.bgFadeOut == None:
            self.bgFadeOut = int(self.bgFadeOut)
        
        if not self.bg == None:
            self.bg.set_alpha(self.bgAlpha)
        
        self.text = text
        self.currentlyOnScreenText = "" # For text scrolling
        self.currentIndex = 0
        
        self.font = font
        
        self.charInterval = 10 # This is the base speed of how long it takes for a character to appear. Speedmult is multiplied by this.
        
        self.timer = 0.
        
        self.done = False
        self.reachedTargetPos = False
        self.portraitReachedTargetPos = False
        
        if not self.speakerName == None:
            self.portraitImage = pygame.image.load(os.path.join("images","dialog",self.speakerName,self.mood+".png")).convert_alpha()
        
        self.textSurf = pygame.surface.Surface(self.parent.dialogRect.size, SRCALPHA)
        
    def update(self, time, keyEvents, mouseEvents):
        self.fading = False
        
        if self.parent.skipping:
            self.fadingOut = True
        else:
            self.fadingOut = False
        if not self.bgFadeIn == None and self.bgAlpha < 255: # If it's supposed to fade in and hasn't already
            self.fadeTimer += time
            self.bgAlpha = (self.fadeTimer*1./self.bgFadeIn*1.*100)*255/100
            self.fading = True
        elif not self.bgFadeOut == None and self.bgAlpha > 0 and self.fadingOut: # If it's supposed to fade out and hasn't already
            if self.fadeTimer == 0 and not self.bgAlpha == 0:
                self.fadeTimer = self.bgFadeOut
            self.fadeTimer -= time
            self.bgAlpha = (self.fadeTimer*1./self.bgFadeOut*1.*100)*255/100
            self.fading = True
        elif not self.bgAlpha == 255:
            self.bgAlpha = 255
    
        self.bg.set_alpha(self.bgAlpha)
        if not self.fading:
            self.timer += time
        
            if self.timer >= self.charInterval/self.speedMult:
                self.currentlyOnScreenText = self.text[:self.currentIndex]
                self.currentIndex += 1
                self.timer = 0
                
                if self.currentIndex+1 >= len(self.text):
                    self.done = True
        
        if self.parent.dialogOffset[1]+self.boundingRect.height <= self.parent.dialogTargetY-self.parent.dialogRect.height:
            self.reachedTargetPos = True
        if self.parent.portraitOffset[0] >= self.parent.portraitTargetX+self.parent.portraitRect.width:
            self.portraitReachedTargetPos = True
        
    def draw(self, surface):
        self.textSurf.fill((0,0,0, 0))
        if not self.fading:
            self.parent.dialogOutlineImage.set_alpha(self.parent.dialogAlpha)
            surface.blit(self.parent.dialogOutlineImage, self.parent.dialogRect.move(self.parent.dialogOffset).topleft)
        
        # Word-wrapping
        lines = []
    
        if self.font.size(self.currentlyOnScreenText)[0] > self.parent.dialogRect.inflate(-14,-14).width:
            words = self.currentlyOnScreenText.split(" ")
            accumulatedLine = ""
            for word in words:
                line = accumulatedLine+word+" "
                if self.font.size(line)[0] > self.parent.dialogRect.inflate(-14,-14).width:
                    lines.append(accumulatedLine)
                    accumulatedLine = word+" "
                else:
                    accumulatedLine = line
            lines.append(accumulatedLine)
        else:
            lines.append(self.currentlyOnScreenText)
        
        y = self.parent.dialogRect.inflate(-14,-14).top
        for line in lines:
            textSurf = self.font.render(line, True, (255,255,255))
            textRect = textSurf.get_rect()
            textRect.left = self.parent.dialogRect.inflate(-14,-14).left
            self.textSurf.blit(textSurf, (0, y-self.parent.dialogRect.inflate(-14,-14).top))
            y += self.font.get_height()
        # End word-wrapping
            
        if not self.fading:    
            # Draw the name of the speaker.
            name = self.speakerName
            if self.speakerName == "Mystery":
                name = "  ?"
            textSurf = self.font.render(name, True, (255,255,255))
            textRect = textSurf.get_rect()
            textRect.left = self.parent.dialogRect.left+2
            textRect.top = self.parent.portraitRect.bottom
            textSurf.set_alpha(self.parent.dialogAlpha)
            surface.blit(textSurf, textRect.topleft)
            
            self.textSurf.set_alpha(self.parent.dialogAlpha)
            surface.blit(self.textSurf, self.parent.dialogRect.move(self.parent.dialogOffset).inflate(-14,-14).topleft)
            
        
        if not self.fading:
            if not self.speakerName == None:
                surface.blit(self.parent.dialogPortraitOutlineImage, self.parent.portraitRect.move(self.parent.portraitOffset).topleft)
                surface.blit(self.portraitImage, (self.parent.portraitRect.left+1+self.parent.portraitOffset[0],self.parent.portraitRect.top+1+self.parent.portraitOffset[1]))
        
    def finish(self):
        # If the player presses the button to make it finish this dialog.
        self.currentlyOnScreenText = self.text
        self.currentIndex = len(self.text)-1
        
class DialogObject(object):
    
    def __init__(self, parent, speaker, mood, speedMult, waitForUser, pauseTime, text, font, boundingRect, bgName=None, bgFade=None, bgFadeTime=None):
        self.parent = parent
        
        self.speakerName = speaker
        self.mood = mood
        self.speedMult = float(speedMult)
        self.waitForUser = int(waitForUser)
        self.pauseTime = int(pauseTime)
        
        self.boundingRect = boundingRect
        if not bgName == None:
            self.bg = self.parent.backgrounds[bgName]
        else:
            self.bg = None
        
        self.bgFade = bgFade
        if not bgFadeTime == None:
            self.bgFadeTime = int(bgFadeTime)
        else:
            self.bgFadeTime = None
        self.fadeTimer = 0
        if self.bgFade == "in":
            self.bgAlpha = 0
        elif self.bgFade == "out" or self.bgFade == "none":
            self.bgAlpha = 255
        
        if not self.bg == None:
            self.bg.set_alpha(self.bgAlpha)
        
        self.text = text
        self.currentlyOnScreenText = ""
        self.currentIndex = 0
        
        self.font = font
        
        self.charInterval = 5
        
        self.timer = 0.
        
        self.done = False
        
        if not self.speakerName == None:
            self.portraitImage = pygame.image.load(os.path.join("images","dialog",self.speakerName,self.mood+".png")).convert_alpha()
        
        self.textSurf = pygame.surface.Surface(self.parent.dialogRect.size, SRCALPHA)
        
        self.dialogType = "text"
        
    def update(self, time, keyEvents, mouseEvents):
        if self.bgFade == "in" and self.bgAlpha < 255:
            self.fadeTimer += time
            self.bgAlpha = (self.fadeTimer*1./self.bgFadeTime*1.*100)*255/100
        elif self.bgFade == "out" and self.bgAlpha > 0:
            if self.fadeTimer == 0 and not self.bgAlpha == 0:
                self.fadeTimer = self.bgFadeTime
            self.fadeTimer -= time
            self.bgAlpha = (self.fadeTimer*1./self.bgFadeTime*1.*100)*255/100
        elif self.bgFade == "none" and not self.bgAlpha == 255:
            self.bgAlpha = 255
    
        self.bg.set_alpha(self.bgAlpha)
        self.timer += time
        
        if self.timer >= self.charInterval/self.speedMult:
            self.currentlyOnScreenText = self.text[:self.currentIndex]
            self.currentIndex += 1
            self.timer = 0
            
            if self.currentIndex+1 >= len(self.text):
                self.done = True
        
    def draw(self, surface):
        self.textSurf.fill((0,0,0, 0))
        # if not self.bg == None:
            # surface.blit(self.bg, (self.boundingRect.left,self.boundingRect.top))
        
        surface.blit(self.parent.dialogOutlineImage, self.parent.dialogRect.topleft)
        
        # Word-wrapping
        lines = []
    
        if self.font.size(self.currentlyOnScreenText)[0] > self.parent.dialogRect.inflate(-14,-14).width:
            words = self.currentlyOnScreenText.split(" ")
            accumulatedLine = ""
            for word in words:
                line = accumulatedLine+word+" "
                if self.font.size(line)[0] > self.parent.dialogRect.inflate(-14,-14).width:
                    lines.append(accumulatedLine)
                    accumulatedLine = word+" "
                else:
                    accumulatedLine = line
            lines.append(accumulatedLine)
        else:
            lines.append(self.currentlyOnScreenText)
        
        y = self.parent.dialogRect.inflate(-14,-14).top
        for line in lines:
            textSurf = self.font.render(line, True, (255,255,255))
            textRect = textSurf.get_rect()
            textRect.left = self.parent.dialogRect.inflate(-14,-14).left
            self.textSurf.blit(textSurf, (0, y-self.parent.dialogRect.inflate(-14,-14).top))
            y += self.font.get_height()
            
        surface.blit(self.textSurf, self.parent.dialogRect.inflate(-14,-14).topleft)
        # End word-wrapping
        
        if not self.speakerName == None:
            surface.blit(self.parent.dialogPortraitOutlineImage, self.parent.portraitRect.topleft)
            surface.blit(self.portraitImage, (self.parent.portraitRect.left+5,self.parent.portraitRect.top+5))
        
    def finish(self):
        # If the player presses the button to make it finish this dialog.
        self.currentlyOnScreenText = self.text
        self.currentIndex = len(self.text)-1