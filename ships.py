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

import pygame
from pygame.locals import *

from bullets import *
import enemies

class Ship(pygame.sprite.Sprite):
    """Base Ship class. This class is not to be instantiated directly.
        Functions:
            __init__    initialization function.
                            Parameters:
                                center      Used to align the ship in the starting position.
                                bounds      The bounding rect that this sprite should not pass outside of. Usually the edges of the
                                                screen, sometimes compensating for HUD elements.
                                groups      Passed on to the pygame.sprite.Sprite class.
            loadImages  initialization function, separated for the sake of subclasses.
                            Parameters:
                                center      Used to set the rect of the sprite, should be supplied by the init function.
            update      Called every frame the ship is on screen (hopefully). Handles all keyboard input for controlling the character
                            and performs things like collision.
                            Parameters:
                                pressedKeys All the keys that are currently pressed on the keyboard. This allows the ship to handle its
                                    own input.
                                time        The time in milliseconds of the last frame, used for time-based movement and counters.
            switchImage A function that is called every 50 milliseconds (self.imageChangeInterval) and switches between the two images
                            for the ship's animation.
            fire        Not yet implemented. Will somehow cause the ship to fire its weapon. Called every time the self.fireCounter var
                            reaches the self.fireInterval variable, which is defined from the frate in the self.stats variable."""

    def __init__(self, center, bounds, groups=[], invincible=False):
        pygame.sprite.Sprite.__init__(self, groups)
        self.filePreFix = "RD"
        self.normImgName = "Ship_Normal"
        self.normImgAltName = "Ship_Normal_Alt"
        self.bulletImgFileName = "Bullet"
        self.explosionFileName = "ShipExplosion"
        
        self.bounds = bounds # A bounding rect for the ship to collide with. Usually the edges of the screen.
        
        # Shields: Health
        # Power:   Damage done by weapon
        # Frate:   Firing rate of weapon
        self.stats = {"shields":20, "power":20, "frate":20}
        self.bulletPowerMod = 0 # For powerups and such
        self.damageMod = 0 # For powerups and such (Damage recieved)
        
        self.velocity = [0, 0]
        self.moveSpeed = 250. # Pixels per second
        self.exactPos = [0.0,0.0] # Topleft
        
        self.imageChangeCounter = 0
        self.imageChangeInterval = 50.0 # In milliseconds
        self.imageState = 0 # Either 0 or 1. AKA True or False. This alternates between images for the animation. Possibly expandable to more than two images.
        
        self.fireCounter = 0 # In milliseconds. The fireInterval is calculated in self.calcStats based off of the frate stat.
        
        self.fireSource = 5,6 # Where on the image should the bullets originate from?
        
        self.bulletType = RDBullet # Gets overruled by subclasses. This is just hear to make this class somewhat functional.
        self.bulletGroup = pygame.sprite.Group() # The update function handles this group's updating.
        
        self.alive = True # Use this instead of just self.kill() in order to make the game fade out or something.
        
        # This is for the ship's explosion image and how long it should be on screen.
        self.explosionCounter = 0
        self.explosionTime = 1000 # milliseconds
        self.explosionAlpha = 200
        
        self.invincible = invincible # Defaults to False. This makes it so that health is not depleted when hit if True.
        
    
    def postInit(self, center):
        # Consolidated function to call loadImages and calcStats with a single, convenient function call.
        self.loadImages(center)
        self.calcStats()
        
    def loadImages(self, center):
        # Load the first image of the ship's animation.
        completeFileName = os.path.join("images", self.folderName, self.filePreFix+"_"+self.normImgName+".png")
        self.normImg = pygame.image.load(completeFileName).convert()
        self.normImg.set_colorkey((0,255,0))
        # Load the second image of the ship's animation.
        completeFileName = os.path.join("images", self.folderName, self.filePreFix+"_"+self.normImgAltName+".png")
        self.normImgAlt = pygame.image.load(completeFileName).convert()
        self.normImgAlt.set_colorkey((0,255,0))
        
        # Set the image as the first frame of the animation.
        self.image = self.normImg
        self.rect = self.image.get_rect()
        self.rect.center = center # Center propogates from the __init__ function's arguments.
        self.exactPos = [self.rect.left*1.,self.rect.top*1.] # Convert to decimals so that it runs exactly.
        
        completeFileName = os.path.join("images", self.explosionFileName+".png")
        self.explosionImage = pygame.image.load(completeFileName)
        self.explosionRect = self.explosionImage.get_rect()
        self.explosionImage.set_colorkey((0,255,0))
        self.explosionImage.set_alpha(self.explosionAlpha)
        
    def getImages(self):
        # This function is intended for the character select buttons to call.
        # It returns the two images for the animation. The reason why this function must be called is that the buttons are displayed before the ship class is instantiated.
        # Because the game only creates one instance, and only after the player chooses which one to create.
        # There might be a better way to handle this, I'm open for suggestions.
        images = []
        
        completeImageName = os.path.join("images", self.folderName, self.filePreFix+"_"+self.normImgName+".png")
        images.append(pygame.image.load(completeImageName).convert())
        
        completeImageName = os.path.join("images", self.folderName, self.filePreFix+"_"+self.normImgAltName+".png")
        images.append(pygame.image.load(completeImageName).convert())
        
        for image in images:
            image.set_colorkey((0,255,0))
        return images
        
    def calcStats(self):
        self.fireInterval = 10000.0/self.stats['frate']
        self.maxHealth = 5000.0/self.stats['shields']
        self.health = self.maxHealth
    
    def update(self, pressedKeys, time, bulletGroup=None):
        if self.alive:
            self.imageChangeCounter += time # For the animation
            self.fireCounter += time
            
            if self.imageChangeCounter >= self.imageChangeInterval:
                self.switchImage()
            
            #TODO Make the controls changeable.
            # The reason it's arranged the way it is is so that keys pressed will override the last pressed key. But when it's let up, the first key will kick back in.
            for key in pressedKeys:
                if key == K_s:
                    self.velocity[1] = 1
                elif key == K_w:
                    self.velocity[1] = -1
                    
                if key == K_a:
                    self.velocity[0] = -1.5 # Make the ship move backwards slightly faster than in any other direction.
                elif key == K_d:
                    self.velocity[0] = 1
                    
            if not K_s in pressedKeys and not K_w in pressedKeys:
                self.velocity[1] = 0
            if not K_a in pressedKeys and not K_d in pressedKeys:
                self.velocity[0] = 0
            
            distMovedThisFrame = self.moveSpeed*time/1000.
            if self.velocity[0] != 0:
                self.exactPos[0] += self.velocity[0]*distMovedThisFrame
                
            if self.velocity[1] != 0:
                self.exactPos[1] += self.velocity[1]*distMovedThisFrame
            
            # Make the ship collide with its bounds.
            if self.exactPos[0] < self.bounds.left:
                self.exactPos[0] = self.bounds.left-1
            elif self.exactPos[0]+self.rect.width > self.bounds.right+1:
                self.exactPos[0] = self.bounds.right-self.rect.width
            if self.exactPos[1] < self.bounds.top:
                self.exactPos[1] = self.bounds.top-1
            elif self.exactPos[1]+self.rect.height > self.bounds.bottom+1:
                self.exactPos[1] = self.bounds.bottom-self.rect.height
            
            # Assign the rect to exactPos so that the group draws it in the right place.
            self.rect.topleft = (self.exactPos[0], self.exactPos[1])
            
            # bulletGroup is the group that this ship collides with.
            for bullet in bulletGroup:
                if bullet.rect.colliderect(self.rect):
                    bullet.kill()
                    if not self.invincible:
                        self.health -= bullet.power
                    
            if self.health <= 0:
                self.alive = False
            
            if self.fireCounter >= self.fireInterval:
                self.fire()
        elif not self.alive:
            self.explosionCounter += time
            
            if self.explosionCounter >= self.explosionTime:
                self.kill() # If the explosion has expired, remove self from all groups.
            
            # Make the groups' draw() method use the correct image and rect for the explosion.
            self.image = self.explosionImage
            self.rect = self.explosionRect
            
            self.exactPos[0] -= 100.*time/1000 # Make the explosion move to the left slowly.
            
            self.rect.center = (round(self.exactPos[0]),round(self.exactPos[1]))
        
        self.bulletGroup.update(time) # Wether the ship is alive or not, make the bullet group update. (For multiplayer's sake)
        # problem is that when the explosion expires, the bullet group stops updating.
    
    def switchImage(self):
        if self.imageState == 0:
            self.image = self.normImgAlt
        elif self.imageState == 1:
            self.image = self.normImg
        else:
            self.imageState = 0 # Just in case of bugs, reset the animation in if it gets off somehow
        self.imageChangeCounter = 0
        self.imageState = not self.imageState # Easily change the animation to the other image.
    
    def fire(self):
        self.fireCounter = 0
        
        firePoint = (self.fireSource[0]+self.rect.left,self.fireSource[1]+self.rect.top)
        power = self.stats["power"]+self.bulletPowerMod
        
        self.bulletType(self.bounds, firePoint, power, parent=self, target=1, seeking=False, groups=self.bulletGroup)
        # target=1 makes the bullet move to the right horizontally.
        
class RainbowDash(Ship):
    
    def __init__(self, center, bounds, groups=[], invincible=False):
        Ship.__init__(self, center, bounds, groups, invincible)
        self.stats = {"shields":20, "power":40, "frate":55}
        self.folderName = os.path.join("Player Ships","Rainbow Dash")
        self.filePreFix = "RD"
        self.postInit(center)
        
        self.fireSource = ((self.rect.width/2), (self.rect.height/2+4))
        
        self.bulletType = RDBullet
    
class PinkiePie(Ship):
    
    def __init__(self, center, bounds, groups=[], invincible=False):
        Ship.__init__(self, center, bounds, groups, invincible)
        self.stats = {"shields":60, "power":40, "frate":15}
        self.folderName = os.path.join("Player Ships","Pinkie Pie")
        self.filePreFix = "PP"
        self.postInit(center)
        
        self.fireSource = (30, 2)
        
        self.bulletType = PPBullet

class TwilightSparkle(Ship):
    
    def __init__(self, center, bounds, groups=[], invincible=False):
        Ship.__init__(self, center, bounds, groups, invincible)
        self.folderName = os.path.join("Player Ships","Twilight Sparkle")
        self.filePreFix = "TS"
        self.postInit(center)
    
class Fluttershy(Ship):
        
    def __init__(self, center, bounds, groups=[], invincible=False):
        Ship.__init__(self, center, bounds, groups, invincible)
        self.folderName = os.path.join("Player Ships","Fluttershy")
        self.filePreFix = "FS"
        self.postInit(center)
    
class Applejack(Ship):
        
    def __init__(self, center, bounds, groups=[], invincible=False):
        Ship.__init__(self, center, bounds, groups, invincible)
        self.folderName = os.path.join("Player Ships","Applejack")
        self.filePreFix = "AJ"
        self.postInit(center)
    
class Rarity(Ship):
        
    def __init__(self, center, bounds, groups=[], invincible=False):
        Ship.__init__(self, center, bounds, groups, invincible)
        self.folderName = os.path.join("Player Ships","Rarity")
        self.filePreFix = "R"
        self.postInit(center)
        
shipTypes = {"PinkiePie":PinkiePie, "RainbowDash":RainbowDash, "Fluttershy":Fluttershy, "Applejack":Applejack, "Rarity":Rarity, "TwilightSparkle":TwilightSparkle}