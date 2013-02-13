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
import math
import logging

log = logging.getLogger(__name__)

log.debug("Module initialized.")

import pygame
from pygame.locals import *

class Projectile(pygame.sprite.Sprite):
    mainFolder = "images"
    
    hasAlpha = False
    
    def __init__(self, boundingRect, pos, power, parent, weaponParent, moveSpeed, target=-1, seeking=False, angle=None, groups=[]):
        pygame.sprite.Sprite.__init__(self, groups)
        self.imageFileName = "Bullet.png"
        
        self.moveSpeed = moveSpeed
        
        self.boundingRect = boundingRect
        
        self.power = power
        
        self.parent = parent
        self.weaponParent = weaponParent
        
        self.target = target
        
        self.seeking = seeking
        
        # self.filePreFix = self.parent.filePreFix
        
        if not angle == None:
            self.angle = angle*1. # If the parent defined the angle for us.
        elif not self.seeking and not self.target in (-1, 1) and angle == None and type(self).isBullet:
            self.dest = self.target.rect.center
            self.dest = (self.dest[0]*1., self.dest[1]*1.) # Make it work in decimals
            
            self.angle = math.degrees(math.atan2((pos[1]-self.dest[1]),(pos[0]-self.dest[0])))+180.
            
        self.imageChangeCounter = 0
        self.imageChangeInterval = 50.0 # Milliseconds
        
        self.imageState = 0
        self.imageStates = 1
        
        self.pos = [pos[0], pos[1]]
        self.initialPos = [pos[0]*1.,pos[1]*1.]
        self.totalDistMoved = 0.
        self.image = None
        # self.image = type(self).images[0]
        # self.rect = self.image.get_rect()
        # self.rect.left = self.pos[0]
        # self.rect.centery = self.pos[1]
        # self.pos = [self.rect.left, self.rect.top]
        # self.origin = self.pos
        
        self.explosionTime = 250
        self.explosionTimer = 0
        self.isExplosion = False
        
    def onImpact(self):
        self.isExplosion = True
        self.kill()
            
    @classmethod    
    def loadImages(cls):
        for i in range(0,cls.imageStates):
            if cls.vectorStyle:
                completeFileName = os.path.join(cls.mainFolder, cls.folderName, cls.filePreFix+"_"+cls.imageFileName+str(i)+" VECTOR STYLE"+".png")
                image = pygame.image.load(completeFileName).convert_alpha()
            else:
                completeFileName = os.path.join(cls.mainFolder, cls.folderName, cls.filePreFix+"_"+cls.imageFileName+str(i)+".png")
                image = pygame.image.load(completeFileName).convert()
                image.set_colorkey((0,255,0))
            cls.images.append(image)
    
    def calcMovement(self, time):
        pass
    
    def update(self, time):
        if self.image == None:
            # If the image hasn't been set yet.
            self.image = type(self).images[0]
            self.rect = self.image.get_rect()
            self.rect.left = self.pos[0]
            self.rect.centery = self.pos[1]
            self.pos = [self.rect.left, self.rect.top]
            self.origin = self.pos
        # distThisFrame = self.moveSpeed*time/1000.
        # if not self.target == -1 and not self.target == 1:
            # This code compares the current location to the original location every frame instead of just adding to last frame's location
            # in an attempt to make it move more accurately along a line. It doesn't seem to be working any better though.
            # self.totalDistMoved += distThisFrame
            # x = self.totalDistMoved*math.cos(math.radians(self.angle))
            # y = self.totalDistMoved*math.sin(math.radians(self.angle))
            
            # self.pos[0] = self.initialPos[0]+x
            # self.pos[1] = self.initialPos[1]+y
        # else:
            # self.pos[0] += self.target*distThisFrame
        self.calcMovement(time)
        
        self.lastRect = self.rect.copy()
        self.rect.center = self.pos
        
        if not self.boundingRect.colliderect(self.rect):
            self.kill()
            
        self.imageChangeCounter += time
        if self.imageChangeCounter >= self.imageChangeInterval:
            self.switchImage()
            
    def switchImage(self):
        if not self.isExplosion:
            self.imageState += 1
            if self.imageState > type(self).imageStates-1:
                self.imageState = 0
                
            self.image = type(self).images[self.imageState]
            self.imageChangeCounter = 0
    

class Rocket(Projectile):

    isBullet = False

    firedImages = []
    deadImages = []
    
    firedImageStates = 2
    deadImageStates = 1
    
    folderName = os.path.join("Bullets")
    filePreFix = ""
    imageFileName = "Rocket 1"
    
    vectorStyle = True
    
    def __init__(self, *args):
        Projectile.__init__(self, *args)
        
        self.power = type(self.weaponParent).power
        
        self.velocity = type(self.weaponParent).launchPower # Units Per Second
        self.velAngle = self.weaponParent.fireAngle
        
        self.maxVelocity = type(self.weaponParent).maxVelocity
        
        self.acceleration = 5 # Units Per Second Per Second
        self.accelAngle = 0
        if self.velAngle == 90:
            self.accelAngle = 270
        elif self.velAngle == 270:
            self.accelAngle = 90
        
        self.timeOut = 0
        self.fireTime = type(self.weaponParent).fireTime
        
        self.explosionTime = 250
        self.explosionTimer = 0
        self.isExplosion = False
        
        self.isFired = False
        
        self.currentOrigImage = type(self).deadImages[0]
        self.image = self.currentOrigImage.copy()
        self.rect = self.image.get_rect()
        self.rect.left = self.pos[0]
        self.rect.centery = self.pos[1]
        self.pos = [self.rect.left, self.rect.top]
        self.origin = self.pos
        
    @classmethod    
    def loadImages(cls):
        for i in range(0,cls.firedImageStates):
            if cls.vectorStyle:
                completeFileName = os.path.join(cls.mainFolder, cls.folderName, cls.filePreFix+cls.imageFileName+" Fired"+str(i)+".png")
                image = pygame.image.load(completeFileName).convert_alpha()
            else:
                completeFileName = os.path.join(cls.mainFolder, cls.folderName, cls.filePreFix+cls.imageFileName+" Fired"+str(i)+".png")
                image = pygame.image.load(completeFileName).convert()
                image.set_colorkey((0,255,0))
            cls.firedImages.append(image)
        for i in range(0,cls.deadImageStates):
            if cls.vectorStyle:
                completeFileName = os.path.join(cls.mainFolder, cls.folderName, cls.filePreFix+cls.imageFileName+" Dead"+str(i)+".png")
                image = pygame.image.load(completeFileName).convert_alpha()
            else:
                completeFileName = os.path.join(cls.mainFolder, cls.folderName, cls.filePreFix+cls.imageFileName+" Dead"+str(i)+".png")
                image = pygame.image.load(completeFileName).convert()
                image.set_colorkey((0,255,0))
            cls.deadImages.append(image)
        
    def onImpact(self):
        self.isExplosion = True
        
        self.image = pygame.image.load(os.path.join("images", "RocketImpactImage.png")).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
    
    def everyFrameOnceFired(self, time):
        pass # This is a function meant for subclasses.
    
    def calcMovement(self, time):
        # A function called by the update function of the superclass every frame
        if not self.isExplosion:
            self.timeOut += time
            
            # if self.timeOut >= self.fireTime:
                # self.isFired = True
                # self.accelAngle = 0
                # self.acceleration = 75  
            
            if self.velocity <= 150 and not self.isFired:
                self.isFired = True
                self.accelAngle = 0
                self.acceleration = 75
                self.velAngle = 0
            
            
                
            if self.isFired:
                self.everyFrameOnceFired(time)
            
            velX = self.velocity*math.cos(math.radians(self.velAngle))
            velY = self.velocity*math.sin(math.radians(self.velAngle))
            
            accelX = self.acceleration*math.cos(math.radians(self.accelAngle))
            accelY = self.acceleration*math.sin(math.radians(self.accelAngle))
            
            velX += accelX
            velY += accelY
            
            self.velocity = math.sqrt(velX**2 + velY**2)
            if self.isFired:
                self.velAngle = math.degrees(math.atan2(velY, velX))
        
            if self.velocity > self.maxVelocity:
                self.velocity = self.maxVelocity*1
        
            distThisFrame = self.velocity*time/1000.
            
            thisFrameX = distThisFrame*math.cos(math.radians(self.velAngle))
            thisFrameY = distThisFrame*math.sin(math.radians(self.velAngle))
            
            self.pos[0] += thisFrameX
            self.pos[1] += thisFrameY
        else:
            self.explosionTimer += time
            
            if self.explosionTimer >= self.explosionTime:
                self.kill()
                
    def switchImage(self):
        if not self.isExplosion:
            if not self.isFired:
                imageStates = type(self).deadImageStates
                imageList = type(self).deadImages
            else:
                imageStates = type(self).firedImageStates
                imageList = type(self).firedImages
            
            self.imageState += 1
            if self.imageState > imageStates-1:
                self.imageState = 0
            
            self.currentOrigImage = imageList[self.imageState]
            self.image = self.currentOrigImage.copy()
            self.imageChangeCounter = 0
            
            if self.isFired:
                self.image = pygame.transform.rotate(self.currentOrigImage.copy(), -self.velAngle)
            
class SeekingMissile(Rocket):
    
    def __init__(self, *args):
        Rocket.__init__(self, *args)
        
        self.lostLock = False
        
        self.getTarget()
        
    def getDistance(self, loc):
        x = self.pos[0] - loc[0]
        y = self.pos[1] - loc[1]
        
        distance = math.sqrt(x**2 + 7**2)
        
        return distance
        
    def getAngle(self, loc):
        x = self.pos[0] - loc[0]
        y = self.pos[1] - loc[1]
        
        angle = math.degrees(math.atan2(y,x))
        
        return angle
        
    def getTarget(self):
        # Figure out if this is fired by the player or by an enemy. Then figure out what to target accordingly.
        firer = self.weaponParent.parent
        
        if firer.obType == "Player":
            options = {}
            for enemy in self.parent.parent.enemyGroup.sprites():
                options[self.getDistance(enemy.rect.center)] = enemy
                
            # Check if in boss, if so add the boss as well.
            if self.parent.parent.inBoss:
                options[self.getDistance(self.parent.parent.boss.rect.center)] = self.parent.parent.boss
            
            currentBest = None
            for dist in options.iterkeys():
                if currentBest == None or dist < currentBest:
                    currentBest = dist
                    
            if not currentBest == None:
                self.target = options[currentBest]
            else:
                self.target = None
        elif firer.obType == "Enemy" or firer.obType == "Boss":
            pass #TODO
        
    def everyFrameOnceFired(self, time):
        if not self.target == None and self.target.alive:
            angleToTarget = self.getAngle(self.target.rect.center)
            accelAngle = self.accelAngle+180
            velAngle = self.velAngle+180
            
            diff = (angleToTarget-velAngle)
            
            if diff <= -360:
                diff += 360
            if diff >= 360:
                diff -=360
            
            if not self.lostLock:
                if diff < -270 and diff > -361:
                    self.accelAngle += type(self.weaponParent).turnRate*time/1000.
                elif diff > -type(self.weaponParent).seekingAngle/2 and diff < 0:
                    self.accelAngle -= type(self.weaponParent).turnRate*time/1000.
                else:
                    self.lostLock = True
            
            # if angleToTarget < accelAngle:
                # self.accelAngle -= type(self.weaponParent).turnRate*time/1000.
                # if accelAngle < angleToTarget:
                    # self.accelAngle = angleToTarget-180 # If we overshot it, then make it aim directly at the target.
            # elif angleToTarget > accelAngle:
                # self.accelAngle += type(self.weaponParent).turnRate*time/1000.
                # if accelAngle > angleToTarget:
                    # self.accelAngle = angleToTarget-180 # If we overshot it, then make it aim directly at the target.
                    
            if self.lostLock:
                if self.velocity <= 25:
                    self.onImpact()
                self.acceleration = -0.75
        else:
            self.getTarget()
        
        
class Bullet(Projectile):
    
    isBullet = True

    def __init__(self, *args):
        Projectile.__init__(self, *args)
        
    def calcMovement(self, time):
        distThisFrame = self.moveSpeed*time/1000.
        
        if not self.target == -1 and not self.target == 1:
            # This code compares the current location to the original location every frame instead of just adding to last frame's location
            #in an attempt to make it move more accurately along a line. It doesn't seem to be working any better though.
            self.totalDistMoved += distThisFrame
            x = self.totalDistMoved*math.cos(math.radians(self.angle))
            y = self.totalDistMoved*math.sin(math.radians(self.angle))
            
            self.pos[0] = self.initialPos[0]+x
            self.pos[1] = self.initialPos[1]+y
        else:
            self.pos[0] += self.target*distThisFrame
        
    def update(self, time):
        Projectile.update(self, time)
    

class RDBullet(Bullet):
    
    images = []
    
    imageStates = 6
    
    folderName = os.path.join("Player Ships", "Rainbow Dash")
    filePreFix = "RD"
    imageFileName = "Bullet"
    
    vectorStyle = True
    
class PPBullet(Bullet):
    
    images = []
    
    imageStates = 6
    
    folderName = os.path.join("Player Ships", "Pinkie Pie")
    filePreFix = "PP"
    imageFileName = "Bullet"
    
    vectorStyle = False
        
class FSBullet(Bullet):
    
    images = []
    
    imageStates = 4
    
    folderName = os.path.join("Player Ships", "Fluttershy")
    filePreFix = "FS"
    imageFileName = "Bullet"
    
    vectorStyle = False
        
class EnemyBullet(Bullet):
    
    images = []
    
    imageStates = 1
    
    folderName = "Enemy Ships"
    filePreFix = "Enemy"
    imageFileName = "Bullet"
    
    vectorStyle = False
    
class BossBullet(Bullet):
    
    images = []
    
    imageStates = 1
    
    mainFolder = "levels"
    folderName = os.path.join("Test Level","Boss")
    filePreFix = "Boss"
    imageFileName = "Bullet"
    
    vectorStyle = True