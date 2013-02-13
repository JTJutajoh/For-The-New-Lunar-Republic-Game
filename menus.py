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

import ships # This allows the char select buttons to show the ships themselves and their stats
import levels # Same as above, but for levels.

log.debug("Module initialized.")

bm = pygame.time.Clock() # Benchmark clock

class Button(pygame.sprite.Sprite):
    
    def __init__(self, name, pos=(0,0), boundingRect=Rect(0,0,0,0), groups=[]):
        pygame.sprite.Sprite.__init__(self, groups)
        
        self.name = name # Used primarily to see if a button has been clicked.
        
        self.extraFolder = ""
        
        self.boundingRect = boundingRect
        
        self.originalPos = pos[:]
        self.pos = pos
        
        self.state = 0 # 0:inactive 1:hovered 2:clicked 3:selected by keyboard
        # Keyboard is hard-coded to be disabled. It makes the buttons act strangely, so for now there are no keyboard controls for the buttons.
        
        self.hidden = False
        
        self.hovered = False # Used only for checkbuttons for now.
        
    def resetRect(self, boundingRect):
        self.boundingRect = boundingRect
        self.pos = [self.originalPos[0]+self.boundingRect.left, self.originalPos[1]+self.boundingRect.top]
        self.rect.center = self.pos
        
    def loadImages(self, imageName, posOrientation=0):
        # Logically find the other files in the same directory specifically named.
        self.images = [pygame.image.load(os.path.join("images","Buttons",self.extraFolder,imageName+".png")).convert_alpha(),
        pygame.image.load(os.path.join("images","Buttons",self.extraFolder,imageName+" Hovered.png")).convert_alpha(),
        pygame.image.load(os.path.join("images","Buttons",self.extraFolder,imageName+" Clicked.png")).convert_alpha()]
        
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.setPos(self.pos, posOrientation)
        
        self.resetRect(self.boundingRect)
            
    def setPos(self, pos, posOrientation=0):
        self.pos = pos
        
        #Orientation:
        #0:topleft
        #1:center
        #2:topright
        if posOrientation == 0:
            self.rect.topleft = self.pos
        elif posOrientation == 1:
            self.rect.center = self.pos
        elif posOrientation == 2:
            self.rect.topright = self.pos
    
    def update(self, time):
        self.hovered = False
        if self.state == 0:
            self.image = self.images[0].copy()
        elif self.state == 1:
            self.image = self.images[1].copy()
            self.hovered = True
        elif self.state == 2:
            self.image = self.images[2].copy()
        elif self.state == 3:
            self.image = self.images[1].copy()
            
class CharButton(Button):
    
    def __init__(self, ship, shipDrawLoc, name, shipNameFont, imageName, posOrientation, pos=(0,0), boundingRect=Rect(0,0,0,0), groups=[], isRadioButton=True):
        Button.__init__(self, name, pos, boundingRect, groups)
        
        self.isRadioButton = isRadioButton
        
        self.extraFolder = "CharSelectButtons"
        
        self.shipNameFont = shipNameFont
        
        self.name = "SHIP_"+self.name # Add the SHIP_ prefix so that the menu handler can determine that this is a special button without checking instance types.
        
        self.loadImages(imageName, posOrientation)
        
        if not ship == None:
            self.loadShip(ship)
        else:
            self.ship = None
            
        self.shipDrawLoc = shipDrawLoc # Where on the button should the ship be drawn?
        
        # For animating the ship on the button.
        self.shipAltImageInterval = 50.0
        self.shipAltImageCounter = 0.0
        
        self.shipImageState = 0
    
    def setShip(self, ship):
        if not ship is self.ship:
            self.loadShip(ship)
            self.genStatImage()
    
    def loadShip(self, ship):
        self.ship = ship((0,0), Rect(0,0,1,1), None)
        self.shipImages = self.ship.getImages()
        self.shipImage = self.shipImages[0]
        self.genStatImage()
    
    def loadImages(self, imageName, posOrientation=0):
        Button.loadImages(self, imageName, posOrientation)
    
    def genStatImage(self):
        # Pre-generate the stat image in order to improve performance. The stat image should not have any reason to change.
        #even if it does, this function can just be called again.
        self.statImage = pygame.surface.Surface(self.rect.size, SRCALPHA)
        nameSurf = self.shipNameFont.render(self.ship.folderName[self.ship.folderName.index(os.path.sep)+1:], True, (255,255,255))
        nameRect = nameSurf.get_rect()
        nameRect.centerx = self.rect.width/2
        nameRect.top = 98
        self.statImage.blit(nameSurf, nameRect.topleft)
        
        # Put the ship's stats on the button
        # 10 to 135 or 129 for the current button image
        xStart = 10
        xEnd = 135
        yMult = 0
        stats = ['power','frate','shields', 'rrate'] # Choose a specific order.
        # for stat in self.ship.stats.iterkeys():
        for stat in stats:
            amt = self.ship.stats[stat]
            
            lineColor = (81,102,74)
            
            lineLength = amt*129./100.
            lineStart = (xStart, xEnd+(24*yMult))
            lineEnd = (lineLength+xStart, xEnd+(24*yMult))
            pygame.draw.line(self.statImage, lineColor, lineStart, lineEnd, 16)
            
            statText = "%s%s%i"%(stat.upper()[:2], " "*18, amt)
            statSurf = self.shipNameFont.render(statText, True, (255,255,255))
            statRect = nameSurf.get_rect()
            statRect.left = 14
            statRect.top = 125+(24*yMult)
            self.statImage.blit(statSurf, statRect.topleft)
            
            yMult += 1
    
    def update(self, time):
        Button.update(self, time)
        
        if not self.ship == None:
            # Put the ship's image on the button.
            self.shipAltImageCounter += time
            # Animate the ship.
            if self.shipAltImageCounter >= self.shipAltImageInterval:
                self.shipImageState += 1
                if self.shipImageState > self.ship.imageStates-1:
                    self.shipImageState = 0
                self.shipImage = self.shipImages[self.shipImageState]
                
                self.shipAltImageCounter = 0
        
            self.shipImageRect = self.shipImage.get_rect()
            self.shipImageRect.center = self.shipDrawLoc
        
class LevelButton(Button):
    
    def __init__(self, level, name, thumbDrawLoc, levelNameFont, imageName, posOrientation, pos=(0,0), boundingRect=Rect(0,0,0,0), groups=[], isRadioButton=True):
        Button.__init__(self, name, pos, boundingRect, groups)
        
        self.isRadioButton = isRadioButton
        
        self.levelNameFont = levelNameFont
        
        self.extraFolder = "LevelSelectButtons"
        
        self.name = "LEVEL_"+self.name # Add the SHIP_ prefix so that the menu handler can determine that this is a special button without checking instance types.
        
        self.loadImages(imageName, posOrientation)
        
        if not level == None:
            self.setLevel(level)
        else:
            self.level = None
        self.thumbDrawLoc = thumbDrawLoc # Where on the button should the thumb be drawn?
    
    def setLevel(self, level):
        self.level = level
        self.thumbImage = self.level.thumbnail
        self.genDescripImage()
    
    def loadImages(self, imageName, posOrientation=0):
        Button.loadImages(self, imageName, posOrientation)
    
    def genDescripImage(self):
        # Pre-generate the stat image in order to improve performance. The stat image should not have any reason to change.
        #even if it does, this function can just be called again.
        self.descripImage = pygame.surface.Surface(self.rect.size, SRCALPHA)
        nameSurf = self.levelNameFont.render(self.level.name, True, (255,255,255))
        nameRect = nameSurf.get_rect()
        nameRect.centerx = self.rect.width/2
        nameRect.top = 98
        self.descripImage.blit(nameSurf, nameRect.topleft)
        
        # self.descripImage = pygame.surface.Surface(self.rect.size, SRCALPHA)
        description = self.level.description[0]
        descripRect = Rect(7,100, 136,95)
        descripList = [] # Break it up into separate lines.
        # pygame.draw.rect(self.image, (0,255,0), descripRect)
        
        if self.levelNameFont.size(description)[0] > descripRect.width:
            words = description.split(" ")
            accumulatedLine = " "*2 # Indent the first line.
            for word in words:
                line = accumulatedLine+word+" "
                if self.levelNameFont.size(line)[0] > descripRect.width:
                    descripList.append(accumulatedLine)
                    accumulatedLine = word+" "
                else:
                    accumulatedLine = line
            descripList.append(accumulatedLine)
        else:
            descripList.append(description)
        
        y = descripRect.top
        for line in descripList:
            nameSurf = self.levelNameFont.render(line, True, (255,255,255))
            nameRect = nameSurf.get_rect()
            nameRect.left = descripRect.left+2
            y += self.levelNameFont.get_height()-4
            self.descripImage.blit(nameSurf, (nameRect.left, y))
    
    def update(self, time):
        Button.update(self, time)
        
        if not self.level == None:
            self.thumbImageRect = self.thumbImage.get_rect()
            self.thumbImageRect.center = self.thumbDrawLoc
             
class CheckButton(Button):
    # Intended for the settings screen.
    
    def __init__(self, name, pos=(0,0), boundingRect=Rect(0,0,0,0), initialState=False, groups=[]):
        Button.__init__(self, name, pos, boundingRect, groups)
        
        self.extraFolder = "SettingsButtons"
        
        # This button has an extra state: 4
        # State 4 means that the button is in checked mode.
        # There's also a self.checked variable too.
        self.checked = initialState
        
        self.name = "CHECK_"+self.name # Add the CHECK_ prefix so that the menu handler can determine that this is a special button without checking instance types.
    
    def loadImages(self, imageName, posOrientation=0):
        Button.loadImages(self, imageName, posOrientation)
        self.images.append(pygame.image.load(os.path.join("images","Buttons",self.extraFolder,imageName+" Checked.png")).convert_alpha())
        self.images.append(pygame.image.load(os.path.join("images","Buttons",self.extraFolder,imageName+" Hovered Checked.png")).convert_alpha())
    
    def update(self, time):
        Button.update(self, time)
        if self.checked:
            if self.hovered:
                self.image = self.images[4].copy()
            else:
                self.image = self.images[3].copy()
  
    
class Menu(pygame.sprite.Group):
    
    def __init__(self, rect, allowKeys=True, textInfo={"Main":{"Text":"Main Header","Color":(255,255,255),"Loc":(300,0),"Font":pygame.font.SysFont("Arial", 36)}, "Sub":{"Text":"Sub Header","Color":(255,255,255),"Loc":(300,50),"Font":pygame.font.SysFont("Arial", 12)}}, bgImage=None, sprites=[]):
        pygame.sprite.Group.__init__(self, [])
        
        self.buttons = []
        
        self.checkedButtons = []
        
        self.allowKeys = allowKeys
            
        self.rect = rect
        
        if not bgImage == None:
            self.bgImage = bgImage
            
            self.bgRect = self.bgImage.get_rect()
            self.bgRect.center = self.rect.center
        
        self.textInfo = textInfo
        
        self.shipButtons = []
        self.levelButtons = []
        
        self.reinit()
    
    def reinit(self):
        self.pressedButton = None
        self.pressedShipButton = None # This is for selecting ships on the ship select screen only. It allows the ship select buttons to work independently from the other button(s)
        self.pressedLevelButton = None
        
        for button in self.buttons:
            button.state = 0
        self.selectedButton = 0 # -1 means that no selection has been made.
    
    def resetRects(self, boundingRect):
        self.rect = boundingRect
        for button in self.sprites():
            button.resetRect(boundingRect)
    
    def makeNewButton(self, name, images, pos, posOrientation=1, type=Button):
        newButton = type(name, pos, self.rect, self)
        newButton.loadImages(images, posOrientation)
        self.buttons.append(newButton)
        
    def makeNewLevelSelectButton(self, level, name, thumbDrawLoc, images, pos, levelNameFont, posOrientation=1, radioButton=True):
        newButton = LevelButton(level, name, thumbDrawLoc, levelNameFont, images, posOrientation, pos, self.rect, self, radioButton)
        # newButton.loadImages(images, posOrientation)
        self.buttons.append(newButton)
        self.levelButtons.append(newButton)
        
    def makeNewCharSelectButton(self, ship, shipDrawLoc, name, images, pos, shipNameFont, posOrientation=1, radioButton=True):
        newButton = CharButton(ship, shipDrawLoc, name, shipNameFont, images, posOrientation, pos, self.rect, self, radioButton)
        # newButton.loadImages(images, posOrientation)
        self.buttons.append(newButton)
        self.shipButtons.append(newButton)
        
    def makeNewCheckButton(self, name, images, pos, initialState, posOrientation=1):
        newButton = CheckButton(name, pos, self.rect, initialState, self)
        newButton.loadImages(images, posOrientation)
        self.buttons.append(newButton)
    
    def update(self, pressedKeys, mouseEvents, time):
        pygame.sprite.Group.update(self, time)
        
        mPos = pygame.mouse.get_pos()
        
        for button in self.buttons:
            if not button.hidden:
                if not button in self.sprites():
                    self.add(button)
                if not button.state == 2:
                    if button.rect.collidepoint(mPos):
                        button.state = 1
                        self.selectedButton = self.buttons.index(button)
                    elif not button.state == 3:
                        button.state = 0
                    
                    # Make the menu work with the keyboard (Currently not working right)
                    #TODO
                    if self.allowKeys:
                        if K_w in pressedKeys:
                            self.selectedButton -= 1
                        elif K_s in pressedKeys:
                            self.selectedButton += 1
                       
                        #TODO make menus repeat (Only relevant to keyboard input.)
                        if self.selectedButton > len(self.buttons)-1:
                            self.selectedButton = len(self.buttons)-1
                        elif self.selectedButton < 0:
                            self.selectedButton = 0
                        
                        self.buttons[self.selectedButton].state = 1
                    
                    # Check for mouse clicks and act accordingly.
                    for e in mouseEvents:
                        if e.button == 1:
                            if button.state == 1 or button.state == 3:
                                if "CHECK_" in button.name:
                                    if button.checked:
                                        button.checked = False
                                        # if button.name[6:] in self.checkedButtons:
                                            # self.checkedButtons.remove(button.name[6:])
                                    else:
                                        button.checked = True
                                        # self.checkedButtons.append(button.name[6:])
                                    button.state = 4
                                elif "LEVEL_" in button.name:
                                    button.state = 2
                                    self.pressedLevelButton = button.name
                                elif "SHIP_" in button.name:
                                    button.state = 2
                                    self.pressedShipButton = button.name
                                else:
                                    button.state = 2
                    
                    if "CHECK_" in button.name:
                        if button.checked:
                            if not button.name[6:] in self.checkedButtons:
                                self.checkedButtons.append(button.name[6:])
                        else:
                            if button.name[6:] in self.checkedButtons:
                                self.checkedButtons.remove(button.name[6:])
                        
                        if K_RETURN in pressedKeys:
                            if button.state == 1 or button.state == 3:
                                button.state = 2
                    
                    # If the mainloop is manually choosing a character button or level button, then make it work right.
                    if not self.pressedShipButton == None:
                        for button in self.buttons:
                            if button.name == self.pressedShipButton:
                                button.state = 2
                    if not self.pressedLevelButton == None:
                        for button in self.buttons:
                            if button.name == self.pressedLevelButton:
                                button.state = 2
                                
                if button.state == 2:
                    if not "SHIP_" in button.name and not "CHECK_" in button.name and not "LEVEL_" in button.name:
                        self.pressedButton = button.name
                    elif "CHECK_" in button.name:
                        pass
                    elif "LEVEL_" in button.name:
                        if button.isRadioButton:
                            if not button.name == self.pressedLevelButton:
                                button.state = 0
                        else:
                            self.pressedButton = button.name
                    elif "SHIP_" in button.name:
                        if button.isRadioButton:
                            if not button.name == self.pressedShipButton:
                                button.state = 0
                        else:
                            self.pressedButton = button.name
            else:
                self.remove(button) # If the button is set to be hidden.
                
    def draw(self, surf):
        surf.blit(self.bgImage, self.bgRect.topleft)
        pygame.sprite.Group.draw(self, surf)
        # Put the button's ship and stat info on the button
        for button in self.buttons:
            if "SHIP_" in button.name:
                if not button.ship == None:
                    surf.blit(button.statImage, button.rect.topleft)
                    shipLoc = button.shipImageRect.topleft
                    surf.blit(button.shipImage, (shipLoc[0]+button.rect.left, shipLoc[1]+button.rect.top))
                    # Blit them directly to surf so that the game will run faster in case surf is the display surface.
            elif "LEVEL_" in button.name:
                if not button.level == None:
                    surf.blit(button.descripImage, button.rect.topleft)
                    thumbLoc = button.thumbImageRect.topleft
                    surf.blit(button.thumbImage, (thumbLoc[0]+button.rect.left, thumbLoc[1]+button.rect.top))
        
        # Blit all the header text
        for header in self.textInfo.iterkeys():
            textSurf = self.textInfo[header]["Font"].render(self.textInfo[header]["Text"], True, self.textInfo[header]["Color"])
            textRect = textSurf.get_rect()
            textRect.center = self.textInfo[header]["Loc"] # Assumes all header text is centered #TODO maybe make this more flexible
        
            surf.blit(textSurf, (textRect.left+self.rect.left, textRect.top+self.rect.top))
 