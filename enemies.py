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

import ships
import bullets

# Will work similarly to ships.py's classes. I may even make them share a superclass later to mitigate my work. But probably not.

class Enemy(pygame.sprite.Sprite):
    """Base Enemy ship class"""
    def __init__(self, pos, boundingRect, bulletGroup, target, moveSpeed=60., groups=[]):
        pygame.sprite.Sprite.__init__(self, groups)
        
        self.imageFileName = "Enemy"
        self.explosionFileName = "ShipExplosion"
        self.folderName = "Enemy Ships"
        self.filePreFix = "Enemy"
        
        self.pos = pos
        self.exactPos = [self.pos[0]*1., self.pos[1]*1.]
        
        self.moveSpeed = moveSpeed*1.
        
        self.boundingRect = boundingRect
        
        self.health = 200
        
        self.alive = True
        self.explosionCounter = 0
        self.explosionTime = 500 # milliseconds
        
        self.bulletImgFileName = "Bullet"
        self.bulletGroup = bulletGroup
        
        self.fireCounter = 0
        self.fireInterval = 500 # milliseconds
        
        self.bulletPower = 15
        
        self.fireSource = (5,18)
        
        self.target = target

    def loadImages(self):
        self.image = pygame.image.load(os.path.join("images", self.folderName, self.filePreFix+"_"+self.imageFileName+".png"))
        self.image.set_colorkey((0,255,0))
        
        self.explosionImage = pygame.image.load(os.path.join("images", self.explosionFileName+".png"))
        self.explosionRect = self.explosionImage.get_rect()
        self.explosionImage.set_colorkey((0,255,0))
        self.explosionImage.set_alpha(125)
        
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        
    def update(self, time, bulletGroup=None):
    
        if self.alive:
            self.exactPos[0] -= self.moveSpeed*time/1000
            
            self.rect.center = (round(self.exactPos[0]),round(self.exactPos[1]))
            
            self.fireCounter += time
            if self.fireCounter >= self.fireInterval:
                self.fire()
            
            for bullet in bulletGroup.sprites():
                if bullet.rect.colliderect(self.rect):
                    self.health -= bullet.power
                    bullet.kill()
        else:
            self.explosionCounter += time
            
            if self.explosionCounter >= self.explosionTime:
                self.kill()
                
            self.image = self.explosionImage
            self.rect = self.explosionRect
            
            self.exactPos[0] -= 100.*time/1000
            
            self.rect.center = (round(self.exactPos[0]),round(self.exactPos[1]))
            
        if self.health <= 0:
            self.alive = False
            self.explosionRect.center = self.rect.center
        
        if not self.boundingRect.colliderect(self.rect):
            self.kill()
        
    def fire(self):
        self.fireCounter = 0
        
        bullets.EnemyBullet(self.boundingRect, (self.fireSource[0]+self.rect.left,self.fireSource[1]+self.rect.top), self.bulletPower, self, self.target, False, self.bulletGroup)
        
class AlphaEnemy(Enemy):

    def __init__ (self, pos, boundingRect, bulletGroup, target, moveSpeed=60., groups=[]):
        Enemy.__init__(self, pos, boundingRect, bulletGroup, target, moveSpeed, groups)
        
        self.loadImages()