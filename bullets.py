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


class Bullet(pygame.sprite.Sprite):
    
    def __init__(self, boundingRect, pos, power, parent, target=-1, seeking=False, groups=[]):
        pygame.sprite.Sprite.__init__(self, groups)
        self.imageFileName = "Bullet.png"
        
        self.moveSpeed = 300.
        
        self.boundingRect = boundingRect
        
        self.power = power
        
        self.parent = parent
        
        self.target = target
        
        self.seeking = seeking
        
        self.filePreFix = self.parent.filePreFix
        
        if not self.seeking and not self.target in [-1, 1]:
            self.dest = self.target.rect.center
            self.dest = (self.dest[0]*1., self.dest[1]*1.) # Make it work in decimals
            
            self.angle = math.degrees(math.atan2((pos[1]-self.dest[1]),(pos[0]-self.dest[0])))+180
            
        
    def loadImages(self, pos):
        self.image = pygame.image.load(os.path.join("images", self.parent.folderName, self.filePreFix+"_"+self.parent.bulletImgFileName+".png")).convert()
        self.image.set_colorkey((0,255,0))
        self.rect = self.image.get_rect()
        self.rect.left = pos[0]
        self.rect.centery = pos[1]
        self.pos = [self.rect.left, self.rect.top]
        self.origin = self.pos
        
    def update(self, time):
        distThisFrame = self.moveSpeed*time/1000.
        if not self.target == -1 and not self.target == 1:
            if self.seeking:
                dest = self.target.rect.center
            else:
                dest = self.dest
            # if (round(self.pos[0]), round(self.pos[1])) == dest:
            
            x = distThisFrame*math.cos(math.radians(self.angle))
            y = distThisFrame*math.sin(math.radians(self.angle))
            movePosThisFrame = (x, y)
            
            self.pos[0] += movePosThisFrame[0]
            self.pos[1] += movePosThisFrame[1]
        else:
            self.pos[0] += self.target*distThisFrame
        
        self.rect.center = self.pos
        
        if not self.boundingRect.colliderect(self.rect):
            self.kill()
        

class RDBullet(Bullet):
    
    def __init__(self, boundingRect, pos, power, parent, target, seeking=False, groups=[]):
        Bullet.__init__(self, boundingRect, pos, power, parent, target, seeking, groups)
        
        self.loadImages(pos)
        
        self.moveSpeed = 400.
    
class PPBullet(Bullet):
    
    def __init__(self, boundingRect, pos, power, parent, target, seeking=False, groups=[]):
        Bullet.__init__(self, boundingRect, pos, power, parent, target, seeking, groups)
        
        self.loadImages(pos)
        
        self.moveSpeed = 400.
        
class EnemyBullet(Bullet):
    
    def __init__(self, boundingRect, pos, power, parent, target, seeking=False, groups=[]):
        Bullet.__init__(self, boundingRect, pos, power, parent, target, seeking, groups)
        
        self.loadImages(pos)