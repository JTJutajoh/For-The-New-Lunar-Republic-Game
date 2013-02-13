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

log.debug("Module initialized.")


class State(object):
    
    def __init__(self, name="UndefinedState", vars={}):
        self.name = name
        
        self.vars = vars
        
    def __str__(self):
        return "State: %s"%self.name
        
class SubState(object):
    
    def __init__(self, name=None):
        self.name = name
        
    def __str__(self):
        return "SubState: %s"%self.name