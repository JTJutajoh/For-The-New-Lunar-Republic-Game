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
import random
import logging

log = logging.getLogger(__name__)

import pygame
from pygame.locals import *

import bullets

bm = pygame.time.Clock() # Benchmark clock.

class BossTurret(pygame.sprite.Sprite):
    
    fileName = "BossTurret.png"
    
    def __init__(self, bossParent, center, bulletPower, bulletSpeed, bulletGroup, hasImage, *args):
        pygame.sprite.Sprite.__init__(self, *args)
        
        self.hasImage = hasImage
        
        self.parent = bossParent
        self.center = center
        
        self.bulletPower = bulletPower
        self.bulletSpeed = bulletSpeed
        
        if self.hasImage:
            self.originalImage = pygame.image.load(os.path.join("levels",self.parent.folderName,"Boss",type(self).fileName)).convert()
            self.originalImage.set_colorkey((0,255,0))
            self.image = self.originalImage.copy()
        else:
            self.image = pygame.surface.Surface((3,3), SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = self.center
        
        self.bulletGroup = bulletGroup
        
    def update(self, time):
        pass
        
class TrackingBossTurret(BossTurret):

    fileName = "TrackingBossTurret.png"
    bulletType = bullets.EnemyBullet
    bulletSpeed = 400.
    
    def __init__(self, fireInterval, *args):
        BossTurret.__init__(self, *args)
        
        self.fireCounter = 0.
        self.fireInterval = fireInterval #TODO Milliseconds. Make this defined by a file.
        
    def update(self, time):
        self.fireCounter += time
        
        self.targetShip = self.parent.level.playerGroup.sprites()[0]
        self.target = self.targetShip.rect.center
        
        origin = (self.parent.rect.left+self.rect.centerx,self.parent.rect.top+self.rect.centery)
        
        diff = (self.target[0]-origin[0], self.target[1]-origin[1])
        angle = -(math.degrees(math.atan2(diff[1],diff[0]))+180)
        if self.hasImage:
            self.image = pygame.transform.rotate(self.originalImage, angle)
            self.rect = self.image.get_rect()
            self.rect.center = self.center
        
        if self.fireCounter >= self.fireInterval:
            self.fireCounter = 0.
            fireSource = (self.rect.centerx+self.parent.rect.left,self.rect.centery+self.parent.rect.top)
            
            type(self).bulletType(self.parent.boundingRect, fireSource, self.bulletPower, self, None, self.bulletSpeed, self.targetShip, False, None, self.bulletGroup)
        
class FixedBossTurret(BossTurret):
    
    fileName = "FixedBossTurret.png"
    bulletType = bullets.BossBullet
    bulletSpeed = 200.
    
    def __init__(self, id, *args):
        BossTurret.__init__(self, *args)
        
        self.id = id
        
        numBullets = 10
        times = 300
        timeSpacing = 2
        self.bulletAngles = []
        angleRange = [150,210]
        angleDiff = angleRange[1]-angleRange[0]
        anglePlus = angleDiff/numBullets-1
        for i in range(0,times):
            angle = angleRange[0]
            skip = random.randint(0,numBullets)
            for i2 in range(0,numBullets+1):
                angle += anglePlus
                if not i2 == skip:
                    self.bulletAngles.append([i*timeSpacing, angle])
        
        self.fireCounter = 0.
        
        self.loadBulletInfo()
    
    def loadBulletInfo(self):
        fileName = "turret_%i"%self.id
        fullFileName = os.path.join("levels",self.parent.folderName,"Boss",fileName)
        infoFile = file(fullFileName, 'r').readlines()
            
        phaseSections = []
        
        mainLineIndex = 0
        for line in infoFile:
            if line[0] == "#":
                lineIndex = mainLineIndex+1
                phaseSection = []
                while not infoFile[lineIndex].strip() == "}":
                    phaseSection.append(infoFile[lineIndex].strip())
                    lineIndex += 1
                phaseSections.append(phaseSection)
            mainLineIndex += 1
            
        self.phases = []
        self.originalPhases = []
        for section in phaseSections:
            thisPhase = []
            for line in section:
                time = int(line[:line.index(":")])
                angle = int(line[line.index(":")+1:])
                
                thisPhase.append([time,angle])
                
            self.phases.append(thisPhase[:]) # This gets modified every loop.
            self.originalPhases.append(thisPhase[:]) # This stays constant.
               
    
    def update(self, time):
        fireSource = (self.rect.centerx+self.parent.rect.left,self.rect.centery+self.parent.rect.top)
        
        self.fireCounter += time
        
        self.target = self.parent.level.playerGroup.sprites()[0]
        
        #TODO Make this only happen once per loop.
        latestShot = 0
        for shot in self.phases[self.parent.phase]:
            # Find when the last shot in the loop happens, so that we can have it loop at the right amount of time.
            if shot[0] > latestShot:
                latestShot = shot[0]
        self.phaseLoopTime = latestShot
        
        if self.fireCounter >= self.phaseLoopTime:
            self.phases[self.parent.phase] = self.originalPhases[self.parent.phase][:]
            self.fireCounter = 0
            
        for shot in self.phases[self.parent.phase]:
            if self.fireCounter >= shot[0]:
                angle = shot[1]
                type(self).bulletType(self.parent.boundingRect, fireSource, self.bulletPower, self, None, self.bulletSpeed, self.target, False, angle, self.bulletGroup)
                self.phases[self.parent.phase].remove(shot) # So it only fires this shot once.
                
class LazerBossTurret(BossTurret):
    
    fileName = "LazerBossTurret.png"
    
    def __init__(self, lazerWidth, lazerPower, lazerColor, fireInterval, fireTime, damageInterval, *args):
        BossTurret.__init__(self, *args)
    
        self.lazerWidth = lazerWidth # In pixels
        self.lazerPower = lazerPower
        self.lazerColor = lazerColor
        
        self.fireCounter = 0.
        self.fireInterval = fireInterval
        self.firing = False
        self.fireTime = fireTime # How long does each fire last?
        self.damageInterval = damageInterval # The time between damages to targets. Milliseconds
        
    def update(self, time):
        self.fireCounter += time
        
        if not self.firing:
            if self.fireCounter >= self.fireInterval:
                self.fireCounter = 0.
                
                self.firing = True
        else:
            if self.fireCounter >= self.fireTime:
                self.fireCounter = 0.
                
                self.firing = False

class BossGroup(pygame.sprite.GroupSingle):
    
    def __init__(self, *args):
        pygame.sprite.GroupSingle.__init__(self, *args)
        
    def draw(self, surface):
        pygame.sprite.GroupSingle.draw(self, surface)
        self.sprite.draw(surface)
                
class Boss(pygame.sprite.Sprite):
    
    def __init__(self, level, initialCenter, boundingRect, *args):
        self.obType = "Boss"
        pygame.sprite.Sprite.__init__(self, *args)
        
        self.level = level
        self.folderName = level.name
        
        self.boundingRect = boundingRect
        self.initialCenter = initialCenter
        
        self.originalImage = pygame.image.load(os.path.join("levels",self.folderName,"Boss","Boss.png")).convert_alpha()
        # self.originalImage.set_colorkey((0,255,0))
        self.image = self.originalImage.copy()
        self.rect = self.image.get_rect()
        self.rect.left = self.boundingRect.right
        self.rect.centery = self.initialCenter[1]
        
        self.mask = pygame.mask.from_surface(self.originalImage)
        
        self.alive = True
        
        self.phase = 0 #= 1
            
        self.bulletGroup = pygame.sprite.RenderUpdates()
        
        self.turretGroup = pygame.sprite.Group()
        
        self.loadTurretInfoFromFile()
            
        self.loadFromFile()
            
        TrackingBossTurret.bulletType.loadImages()
        FixedBossTurret.bulletType.loadImages()
    
    def loadFromFile(self):
        fileName = "bossInfo"
        fullFileName = os.path.join("levels",self.folderName,"Boss",fileName)
        theFile = file(fullFileName, 'r').readlines()
        
        info = {}
        
        for line in theFile:
            line = line.strip()
            key = line[:line.index(":")]
            value = line[line.index(":")+1:]
            info[key] = value
            
        self.maxHealth = int(info['maxhealth'])
        self.health = self.maxHealth*1
        
        self.numPhases = int(info['numphases'])
        self.phaseTimes = {}
        for line in info.iterkeys():
            if line[:5] == "phase":
                self.phaseTimes[int(line[5])] = float(info[line]) # Because this is a percentage (Of health remaining)
    
    def loadTurretInfoFromFile(self):
        fileName = "turretInfo"
        fullFileName = os.path.join("levels",self.folderName,"Boss",fileName)
        theFile = file(fullFileName, 'r').readlines()
        
        fixedTurretsLines = []
        trackingTurretsLines = []
        lazerTurretsLines = []
        turretLines = [fixedTurretsLines, trackingTurretsLines, lazerTurretsLines]
        
        # Separate out the different turrets detailed in the file.
        mainLineIndex = 0
        for line in theFile:
            if line[0] == "#":
                if line.strip() == "#FIXED{":
                    lineIndex = mainLineIndex+1
                    newList = []
                    while not theFile[lineIndex].strip() == "}":
                        newList.append(theFile[lineIndex].strip())
                        lineIndex += 1
                    fixedTurretsLines.append(newList)
                elif line.strip() == "#TRACKING{":
                    lineIndex = mainLineIndex+1
                    newList = []
                    while not theFile[lineIndex].strip() == "}":
                        newList.append(theFile[lineIndex].strip())
                        lineIndex += 1
                    trackingTurretsLines.append(newList)
                elif line.strip() == "#LAZER{":
                    lineIndex = mainLineIndex+1
                    newList = []
                    while not theFile[lineIndex].strip() == "}":
                        newList.append(theFile[lineIndex].strip())
                        lineIndex += 1
                    lazerTurretsLines.append(newList)
            mainLineIndex += 1
        
        fixedTurrets = []
        trackingTurrets = []
        lazerTurrets = []
        turretsLists = [fixedTurrets, trackingTurrets, lazerTurrets]
        
        # Parse each turret's lines.
        for turretList in turretLines:
            for turret in turretList:
                turretDict = {}
                for line in turret:
                    key = line[:line.index(":")]
                    value = line[line.index(":")+1:]
                    turretDict[key] = value
                turretListIndex = turretLines.index(turretList)
                turretsLists[turretListIndex].append(turretDict)
                
        # 0 is fixed turrets
        # 1 is tracking turrets
        # 2 is lazer turrets
        self.lazerTurrets = []
        self.fixedTurrets = []
        for turret in turretsLists[0]:
            loc = (int(turret["x"]),int(turret["y"]))
            newTurret = FixedBossTurret(int(turret['id']), self, loc, int(turret['bulletPower']), float(turret['bulletSpeed']), self.bulletGroup, int(turret['hasImage']))
            self.turretGroup.add(newTurret)
            self.fixedTurrets.append(newTurret)
        for turret in turretsLists[1]:
            loc = (int(turret["x"]),int(turret["y"]))
            self.turretGroup.add(TrackingBossTurret(int(turret['fireInterval']), self, loc, int(turret['bulletPower']), float(turret['bulletSpeed']), self.bulletGroup, int(turret['hasImage'])))
        for turret in turretsLists[2]:
            loc = (int(turret["x"]),int(turret["y"]))
            lazerColor = (int(turret["r"]), int(turret["g"]), int(turret["b"]))
            newTurret = LazerBossTurret(int(turret["lazerWidth"]), int(turret["lazerPower"]), lazerColor, int(turret["fireInterval"]), int(turret["fireTime"]), int(turret["damageInterval"]), self, loc, 0, None, self.bulletGroup, int(turret['hasImage']))
            self.turretGroup.add(newTurret)
            self.lazerTurrets.append(newTurret)
            
    
    def update(self, time):
        self.image = self.originalImage.copy()
        
        spritesWhichCollide = pygame.sprite.spritecollide(self, self.level.playerGroup.sprites()[0].bulletGroup, False, pygame.sprite.collide_mask)
        for sprite in spritesWhichCollide:
            sprite.onImpact()
        for bullet in spritesWhichCollide:
            self.health -= bullet.power
    
        if self.health <= 0:
            self.alive = False
        
        healthPercent = (self.health*1.)/self.maxHealth*100.
        if self.phase+1 in self.phaseTimes.keys():
            if healthPercent <= self.phaseTimes[self.phase+1]:
                self.phase += 1 # Advance the phase.
                # Completely reset the phase
                for turret in self.fixedTurrets:
                    turret.fireCounter = 0
        
        if not self.initialCenter == None:
            # Make it move toward the initial center
            self.rect.left -= 10    
            if self.rect.centerx <= self.initialCenter[0]:
                self.rect.center = self.initialCenter
                self.initialCenter = None # Stop checking this.
                
        self.turretGroup.update(time)
        self.bulletGroup.update(time)
        self.turretGroup.draw(self.image)
        
        for lazerTurret in self.lazerTurrets:
            if lazerTurret.firing:
                lazerRect = Rect(0, self.rect.top+lazerTurret.rect.centery-(lazerTurret.lazerWidth/2), lazerTurret.rect.centerx+self.rect.left, lazerTurret.lazerWidth)
                self.level.lazerRects.append([lazerRect, lazerTurret.lazerPower, lazerTurret.damageInterval])
        
    def draw(self, surface):
        self.bulletGroup.draw(surface)
        
        for lazerTurret in self.lazerTurrets:
            if lazerTurret.firing:
                pygame.draw.line(surface, lazerTurret.lazerColor, ((0, self.rect.top+lazerTurret.rect.centery)), (self.rect.left+lazerTurret.rect.centerx,self.rect.top+lazerTurret.rect.centery), lazerTurret.lazerWidth)
            else:
                if lazerTurret.fireCounter >= lazerTurret.fireInterval*0.6:
                    pygame.draw.line(surface, lazerTurret.lazerColor, ((0, self.rect.top+lazerTurret.rect.centery)), (self.rect.left+lazerTurret.rect.centerx,self.rect.top+lazerTurret.rect.centery), 1)