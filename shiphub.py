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

class ShipHub(object):
    
    def __init__(self, boundingRect):
        self.boundingRect = boundingRect
        
        self.mainBG = pygame.image.load(os.path.join("images","ShipHub","Background Digital Mockup.png")).convert()
        
    def update(self, time, keyEvents, mouseEvents):
        pass
        
    def draw(self, surface):
        surface.blit(self.mainBG, self.boundingRect.topleft)
        
class ShipRoom(object):
    """This is meant to only be a superclass"""
    
    def __init__(self, parent, boundingRect):
        self.parent = parent
        
        self.boundingRect = boundingRect