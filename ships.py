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

log.debug("Module initialized.")

import pygame
from pygame.locals import *

from bullets import *
import enemies
import weapons

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

    def __init__(self, center, bounds, parent, controls={}, manualFiring=False, groups=[], invincible=False):
        self.obType = "Player"
        pygame.sprite.Sprite.__init__(self, groups)
        self.filePreFix = "RD"
        self.bulletImgFileName = "Bullet"
        self.explosionFileName = "ShipExplosion"
        
        self.parent = parent
        
        self.imageStates = 2
        self.images = []
        
        self.bounds = bounds # A bounding rect for the ship to collide with. Usually the edges of the screen.
        
        # Shields: Health
        # Power:   Damage done by weapon
        # Frate:   Firing rate of weapon
        self.stats = {"shields":20, "power":20, "frate":20, "rrate":40}
        self.bulletPowerMod = 0 # For powerups and such
        self.damageMod = 0 # For powerups and such (Damage recieved)
        
        self.manualFiring = manualFiring
        self.firing = False
        
        self.controls = controls
        
        self.velocity = [0, 0]
        self.moveSpeed = 250. # Pixels per second
        self.exactPos = [0.0,0.0] # Topleft
        
        self.imageChangeCounter = 0
        self.imageChangeInterval = 50.0 # In milliseconds
        self.imageState = 0 # Either 0 or 1. AKA True or False. This alternates between images for the animation. Possibly expandable to more than two images.
        
        self.regenCounter = 0
        
        self.fireCounter = 0 # In milliseconds. The fireInterval is calculated in self.calcStats based off of the frate stat.
        
        self.fireSource = 5,6 # Where on the image should the bullets originate from?
        
        self.lazerDamageCounter = -1 # A counter to make the player take a certain amount of damage per second.
        
        self.bulletType = RDBullet # Gets overruled by subclasses. This is just hear to make this class somewhat functional.
        self.bulletGroup = pygame.sprite.Group() # The update function handles this group's updating.
        
        self.alive = True # Use this instead of just self.kill() in order to make the game fade out or something.
        
        # This is for the ship's explosion image and how long it should be on screen.
        self.explosionCounter = 0
        self.explosionTime = 1000 # milliseconds
        self.explosionAlpha = 200
        
        self.weapons = [] # A list containing all the weapon objects on the ship currently. TODO Make this with slots for the upgrading stuff later
        
        self.invincible = invincible # Defaults to False. This makes it so that health is not depleted when hit if True.
        
        self.calcStats()
        
        self.center = center
        
    
    def postInit(self, center):
        # Consolidated function to call loadImages and calcStats with a single, convenient function call.
        self.loadImages(center)
        self.calcStats()
        
    def loadImages(self):
        # Load the first image of the ship's animation.
        for i in range(0,self.imageStates):
            if type(self).vectorStyle:
                completeFileName = os.path.join("images", type(self).folderName, type(self).filePreFix+str(i)+" VECTOR STYLE"+".png")
                image = pygame.image.load(completeFileName).convert_alpha()
            else:
                completeFileName = os.path.join("images", type(self).folderName, type(self).filePreFix+str(i)+".png")
                image = pygame.image.load(completeFileName).convert()
                image.set_colorkey((0,255,0))
            # image = image.subsurface(image.get_bounding_rect())
            type(self).images.append(image)
        
        # Set the image as the first frame of the animation.
        self.image = type(self).images[0]
        self.rect = self.image.get_rect()
        self.rect.center = self.center # Center propogates from the __init__ function's arguments.
        self.exactPos = [self.rect.left*1.,self.rect.top*1.] # Convert to decimals so that it runs exactly.
        
        completeFileName = os.path.join("images", self.explosionFileName+".png")
        self.explosionImage = pygame.image.load(completeFileName)
        self.explosionImage.set_colorkey((0,255,0))
        self.explosionImage.set_alpha(self.explosionAlpha)
        self.explosionRect = self.explosionImage.get_rect()
        self.explosionRect.center = self.rect.center
        
    def getImages(self):
        # This function is intended for the character select buttons to call.
        # It returns the two images for the animation. The reason why this function must be called is that the buttons are displayed before the ship class is instantiated.
        # Because the game only creates one instance, and only after the player chooses which one to create.
        # There might be a better way to handle this, I'm open for suggestions.
        images = []
        for i in range(0,self.imageStates):
            if type(self).vectorStyle:
                completeFileName = os.path.join("images", type(self).folderName, type(self).filePreFix+str(i)+" VECTOR STYLE"+".png")
                image = pygame.image.load(completeFileName).convert_alpha()
            else:
                completeFileName = os.path.join("images", type(self).folderName, type(self).filePreFix+str(i)+".png")
                image = pygame.image.load(completeFileName).convert()
                image.set_colorkey((0,255,0))
            # image = image.subsurface(image.get_bounding_rect())
            images.append(image)
        return images
        
    def calcStats(self):
        #TODO Work on balancing.
        self.fireInterval = 10000.0/type(self).stats['frate']
        self.maxHealth = 10*type(self).stats['shields']
        self.health = self.maxHealth
        if type(self).stats['rrate'] == 0:
            self.regenInterval = -1
        else:
            self.regenInterval = ((125-type(self).stats['rrate'])/2)*1000
        self.regenAmount = 1. # Percent.
        self.otherCollisionDamage = 5
    
    def update(self, pressedKeys, time, bulletGroup=None, otherCollisions=[], lazers=[]):
        if self.alive:
            self.imageChangeCounter += time # For the animation
            self.fireCounter += time
            self.regenCounter += time
            
            if self.imageChangeCounter >= self.imageChangeInterval:
                self.switchImage()
            
            # The reason it's arranged the way it is is so that keys pressed will override the last pressed key. But when it's let up, the first key will kick back in.
            for key in pressedKeys:
                if key == self.controls['downkey']:
                    self.velocity[1] = 1
                elif key == self.controls['upkey']:
                    self.velocity[1] = -1
                    
                if key == self.controls['leftkey']:
                    self.velocity[0] = -1.5 # Make the ship move backwards slightly faster than in any other direction.
                elif key == self.controls['rightkey']:
                    self.velocity[0] = 1
                    
            if not self.controls['downkey'] in pressedKeys and not self.controls['upkey'] in pressedKeys:
                self.velocity[1] = 0
            if not self.controls['leftkey'] in pressedKeys and not self.controls['rightkey'] in pressedKeys:
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
            
            # Check for manual firing.
            if self.controls['fire'] in pressedKeys:
                self.firing = True
            else:
                self.firing = False
            
            # bulletGroup is the group that this ship collides with.
            collided = pygame.sprite.spritecollide(self, bulletGroup, True, pygame.sprite.collide_mask)
            for bullet in collided:
                if not self.invincible:
                    self.health -= bullet.power
                    
            for other in otherCollisions:
                if other.rect.colliderect(self.rect):
                    if not self.invincible:
                        self.health -= self.otherCollisionDamage
            lazerCollisions = False
            for other in lazers:
                if other[0].colliderect(self.rect):
                    self.lazerDamageCounter += time
                    if self.lazerDamageCounter >= other[2] or self.lazerDamageCounter == -1:
                        self.lazerDamageCounter = 0.
                        if not self.invincible:
                            self.health -= other[1]
                    lazerCollisions = True
            if not lazerCollisions:
                self.lazerDamageCounter = -1 # Negative one means that it's not taking damage and that it should take damage immediately once it hits a lazer.
                        
            if self.regenCounter >= self.regenInterval:
                if not self.regenInterval < -1:
                    self.health += self.maxHealth/self.regenAmount
                self.regenCounter = 0
                    
            if self.health <= 0:
                self.alive = False
                
            if self.health > self.maxHealth:
                self.health = self.maxHealth
            
            # if not self.manualFiring or self.firing: # If it's automatically firing or if the player is manually firing right now.
                # if self.fireCounter >= self.fireInterval:
                    # self.fire()
            # elif not self.firing and self.fireCounter > self.fireInterval:
                # self.fireCounter = self.fireInterval
            
            for weapon in self.weapons:
                weapon.update(time)
                    
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
        self.imageState += 1
        if self.imageState > self.imageStates-1:
            self.imageState = 0
            
        self.image = type(self).images[self.imageState]
        self.imageChangeCounter = 0
    
    def fire(self):
        self.fireCounter = 0
        
        # firePoint = (self.fireSource[0]+self.rect.left,self.fireSource[1]+self.rect.top)
        # power = self.stats["power"]+self.bulletPowerMod  
        firePoint = (type(self).fireSource[0]+self.rect.left,type(self).fireSource[1]+self.rect.top)
        power = type(self).stats["power"]+self.bulletPowerMod
        
        type(self).bulletType(self.bounds, firePoint, power, self, type(self).bulletSpeed, 1, False, None, self.bulletGroup)
        # target=1 makes the bullet move to the right horizontally.
        
class RainbowDash(Ship):

    stats = {"shields":20, "power":40, "frate":55, "rrate":20}
    folderName = os.path.join("Player Ships","Rainbow Dash")
    filePreFix = "RD"
    imageStates = 2
    vectorStyle = True
    
    fireSource = (48, 17)
    
    bulletType = RDBullet
    bulletSpeed = 600.
    
    images = []
    
    def __init__(self, *args):
        Ship.__init__(self, *args)
        
        self.weapons.append(weapons.RDDefaultWeapon(self, (48,25)))
        self.weapons.append(weapons.RDDefaultWeapon2(self, (48,36)))
        self.weapons.append(weapons.RDDefaultWeapon2(self, (48,14)))
        
        Rocket.loadImages()
        
        self.weapons.append(weapons.RocketLauncher1(270, self, (20, 36)))
        self.weapons.append(weapons.RocketLauncher1(90, self, (20, 36)))
        self.weapons.append(weapons.RocketLauncher2(270, self, (20, 36)))
        self.weapons.append(weapons.RocketLauncher2(90, self, (20, 36)))
        self.weapons.append(weapons.SeekingMissileLauncher1(90, self, (32, 36)))
    
class PinkiePie(Ship):
    
    stats = {"shields":60, "power":40, "frate":15, "rrate":20}
    folderName = os.path.join("Player Ships","Pinkie Pie")
    filePreFix = "PP"
    imageStates = 2
    vectorStyle = False
    
    fireSource = (30, 2)
    
    bulletType = PPBullet
    bulletSpeed = 300.
    
    images = []
    
class Fluttershy(Ship):
    
    stats = {"shields":15, "power":10, "frate":60, "rrate":100}
    folderName = os.path.join("Player Ships","Fluttershy")
    filePreFix = "FS"
    imageStates = 4
    vectorStyle = False
    
    fireSource = (60, 10)
    
    bulletType = FSBullet
    bulletSpeed = 300.
    
    images = []

#TODO fully implement these ones
class TwilightSparkle(Ship):
    pass
    
class Applejack(Ship):
    pass
    
class Rarity(Ship):
    pass
        
shipTypes = {"PinkiePie":PinkiePie, "RainbowDash":RainbowDash, "Fluttershy":Fluttershy}#, "Applejack":Applejack, "Rarity":Rarity, "TwilightSparkle":TwilightSparkle}