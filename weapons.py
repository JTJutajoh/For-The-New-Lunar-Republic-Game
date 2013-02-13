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

import bullets

log.debug("Module initialized.")


class Weapon(object):

    name = "UNDEFINEDWEAPONTYPE"
    
    projectileType = bullets.RDBullet
    
    fireInterval = 200 # Milliseconds
    
    def __init__(self, parent, fireSource):
        self.parent = parent
        
        self.bulletGroup = self.parent.bulletGroup
        
        self.fireSource = fireSource
        
        self.fireCounter = 0
        
        self.load()
        
    def load(self):
        pass
        
    def update(self, time):
        self.fireCounter += time
        
        if (self.parent.firing and self.fireCounter >= type(self).fireInterval) or not self.parent.manualFiring:
            self.fire()
        elif not self.parent.firing and self.fireCounter > type(self).fireInterval:
            self.fireCounter = type(self).fireInterval
        
    def draw(self, surface):
        pass
        
    def fire(self):
        self.fireCounter = 0
        
        firePoint = (self.fireSource[0]+self.parent.rect.left,self.fireSource[1]+self.parent.rect.top)
        power = type(self.parent).stats["power"]+self.parent.bulletPowerMod
        
        type(self).projectileType(self.parent.bounds, firePoint, power, self.parent, self, type(self.parent).bulletSpeed, 1, False, None, self.bulletGroup)
        # target=1 makes the bullet move to the right horizontally.
        
class RDDefaultWeapon(Weapon):
    
    name = "RD Default Weapon Level 1"
    
    projectileType = bullets.RDBullet
    
    fireInterval = 500
    
class RDDefaultWeapon2(Weapon):
    
    name = "RD Default Weapon Level 2"
    
    projectileType = bullets.RDBullet
    
    fireInterval = 350
    
class RocketLauncher1(Weapon):
    
    name = "Rocket Launcher Level 1"
    
    projectileType = bullets.Rocket
    
    fireInterval = 1500
    
    launchPower = 300
    
    fireTime = 400
    
    maxVelocity = 1000
    
    power = 25
    
    def __init__(self, fireAngle, *args):
        Weapon.__init__(self, *args)
        
        self.fireAngle = fireAngle
        
class RocketLauncher2(Weapon):
    
    name = "Rocket Launcher Level 2"
    
    projectileType = bullets.Rocket
    
    fireInterval = 1250
    
    launchPower = 200
    
    fireTime = 300
    
    maxVelocity = 1200
    
    power = 50
    
    def __init__(self, fireAngle, *args):
        Weapon.__init__(self, *args)
        
        self.fireAngle = fireAngle
        
class SeekingMissileLauncher1(Weapon):
    
    name = "Seeking Missile Launcher Level 1"
    
    projectileType = bullets.SeekingMissile
    
    fireInterval = 250
    
    launchPower = 200
    
    fireTime = 500
    
    maxVelocity = 100
    
    power = 30
    
    turnRate = 50
    
    seekingAngle = 180
    
    def __init__(self, fireAngle, *args):
        Weapon.__init__(self, *args)
        
        self.fireAngle = fireAngle