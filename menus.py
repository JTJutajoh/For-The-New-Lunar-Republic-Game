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

import pygame
from pygame.locals import *

import ships # This allows the char select buttons to show the ships themselves and their stats

bm = pygame.time.Clock() # Benchmark clock

class Button(pygame.sprite.Sprite):
    
    def __init__(self, name, pos=(0,0), groups=[]):
        pygame.sprite.Sprite.__init__(self, groups)
        
        self.name = name # Used primarily to see if a button has been clicked.
        
        self.extraFolder = ""
        
        self.pos = pos
        
        self.state = 0 # 0:inactive 1:hovered 2:clicked 3:selected by keyboard
        # Keyboard is hard-coded to be disabled. It makes the buttons act strangely, so for now there are no keyboard controls for the buttons.
        
        self.hidden = False
        
    def loadImages(self, imageName, posOrientation=0):
        # Logically find the other files in the same directory specifically named.
        self.images = [pygame.image.load(os.path.join("images","Buttons",self.extraFolder,imageName+".png")).convert_alpha(),
        pygame.image.load(os.path.join("images","Buttons",self.extraFolder,imageName+" Hovered.png")).convert_alpha(),
        pygame.image.load(os.path.join("images","Buttons",self.extraFolder,imageName+" Clicked.png")).convert_alpha()]
        
        self.image = self.images[0]
        self.rect = self.image.get_rect()
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
        if self.state == 0:
            self.image = self.images[0].copy()
        elif self.state == 1:
            self.image = self.images[1].copy()
        elif self.state == 2:
            self.image = self.images[2].copy()
        elif self.state == 3:
            self.image = self.images[1].copy()
            
class CharButton(Button):
    
    def __init__(self, ship, shipDrawLoc, name, shipNameFont, pos=(0,0), groups=[]):
        Button.__init__(self, name, pos, groups)
        
        self.ship = ship((0,0), Rect(0,0,1,1))
        self.shipDrawLoc = shipDrawLoc # Where on the button should the ship be drawn?
        
        # For animating the ship on the button.
        self.shipAltImageInterval = 50.0
        self.shipAltImageCounter = 0.0
        
        self.shipImageState = 0
        self.shipImages = self.ship.getImages()
        self.shipImage = self.shipImages[0]
        
        self.shipNameFont = shipNameFont
        
        self.extraFolder = "CharSelectButtons"
        
        self.name = "SHIP_"+self.name # Add the SHIP_ prefix so that the menu handler can determine that this is a special button without checking instance types.
        
    def loadImages(self, imageName, posOrientation=0):
        Button.loadImages(self, imageName, posOrientation)
            
        self.genStatImage()
    
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
        for stat in self.ship.stats.iterkeys():
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
        
        # Put the ship's image on the button.
        self.shipAltImageCounter += time
        # Animate the ship.
        if self.shipAltImageCounter >= self.shipAltImageInterval:
            if self.shipImageState == 0:
                self.shipImage = self.shipImages[1]
            elif self.shipImageState == 1:
                self.shipImage = self.shipImages[0]
            self.shipAltImageCounter = 0
            self.shipImageState = not self.shipImageState
        
        self.shipImageRect = self.shipImage.get_rect()
        self.shipImageRect.center = self.shipDrawLoc
             
class CheckButton(Button):
    # Intended for the settings screen.
    
    def __init__(self, name, pos=(0,0), groups=[]):
        Button.__init__(self, name, pos, groups)
  
    
class Menu(pygame.sprite.Group):
    
    def __init__(self, rect, allowKeys=True, textInfo={"Main":{"Text":"Main Header","Color":(255,255,255),"Loc":(300,0),"Font":pygame.font.SysFont("Arial", 36)}, "Sub":{"Text":"Sub Header","Color":(255,255,255),"Loc":(300,50),"Font":pygame.font.SysFont("Arial", 12)}}, bgImage=None, sprites=[]):
        pygame.sprite.Group.__init__(self, [])
        
        self.buttons = []
        
        self.allowKeys = allowKeys
        
        if not bgImage == None:
            self.bgImage = bgImage
            
        self.rect = rect
        
        self.textInfo = textInfo
        
        self.reinit()
    
    def reinit(self):
        self.pressedButton = None
        self.pressedShipButton = None # This is for selecting ships on the ship select screen only. It allows the ship select buttons to work independently from the other button(s)
        for button in self.buttons:
            button.state = 0
        self.selectedButton = 0 # -1 means that no selection has been made.
    
    def makeNewButton(self, name, images, pos, posOrientation=1, type=Button):
        newButton = type(name, pos, self)
        newButton.loadImages(images, posOrientation)
        self.buttons.append(newButton)
        
    def makeNewCharSelectButton(self, ship, shipDrawLoc, name, images, pos, shipNameFont, posOrientation=1):
        newButton = CharButton(ship, shipDrawLoc, name, shipNameFont, pos, self)
        newButton.loadImages(images, posOrientation)
        self.buttons.append(newButton)
        
    def everyFrame(self, pressedKeys, mouseEvents):
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
                    
                    if self.allowKeys:
                        if K_w in pressedKeys:
                            self.selectedButton -= 1
                        elif K_s in pressedKeys:
                            self.selectedButton += 1
                       
                    #TODO make menus repeat
                    if self.selectedButton > len(self.buttons)-1:
                        self.selectedButton = len(self.buttons)-1
                    elif self.selectedButton < 0:
                        self.selectedButton = 0
                    
                    if self.allowKeys:
                        self.buttons[self.selectedButton].state = 1
                    
                    for e in mouseEvents:
                        if e.button == 1:
                            if button.state == 1 or button.state == 3:
                                if not "SHIP_" in button.name:
                                    button.state = 2
                                else:
                                    button.state = 2
                                    self.pressedShipButton = button.name
                                
                    if K_RETURN in pressedKeys:
                        if button.state == 1 or button.state == 3:
                            button.state = 2
                                
                                
                if button.state == 2:
                    if not "SHIP_" in button.name:
                        self.pressedButton = button.name
                    else:
                        if not button.name == self.pressedShipButton:
                            button.state = 0
            else:
                self.remove(button) # If the button is set to be hidden.
                
                
    def draw(self, surf):
        surf.blit(self.bgImage, self.rect.topleft)
        pygame.sprite.Group.draw(self, surf)
        # Put the button's ship and stat info on the button
        for button in self.buttons:
            if "SHIP_" in button.name:
                surf.blit(button.statImage, button.rect.topleft)
                shipLoc = button.shipImageRect.topleft
                surf.blit(button.shipImage, (shipLoc[0]+button.rect.left, shipLoc[1]+button.rect.top))
                # Blit them directly to surf so that the game will run faster in case surf is the display surface.
        
        # Blit all the header text
        for header in self.textInfo.iterkeys():
            textSurf = self.textInfo[header]["Font"].render(self.textInfo[header]["Text"], True, self.textInfo[header]["Color"])
            textRect = textSurf.get_rect()
            textRect.center = self.textInfo[header]["Loc"] # Assumes all header text is centered #TODO maybe make this more flexible
        
            surf.blit(textSurf, textRect.topleft)
 