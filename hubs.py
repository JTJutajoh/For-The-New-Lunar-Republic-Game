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

# This file might not ever end up being anything. But if it is, it will be the main hubs for the player to upgrade their ships and progress the story.
# In some ways, it will work similarly to levels, in that there can be dialogs and cutscenes associated with them. In other ways, they will be advanced menus for buying and upgrading stuff.

log.debug("Module initialized.")