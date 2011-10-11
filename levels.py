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

# It's planned that this file will contain the meat of the content for the game. The rest will be in the cutscenes file, which this file will heavily reference.

import sys, os
import random
import logging

log = logging.getLogger(__name__)

import pygame
from pygame.locals import *

import enemies
import bullets

log.debug("Module initialized.")

bm = pygame.time.Clock()

class LevelBackground(pygame.sprite.Sprite):
    
    def __init__(self, boundingRect, timeRemaining, image, moveSpeed=0, groups=[], initialx=0):
        pygame.sprite.Sprite.__init__(self, groups)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.left = initialx
        
        self.boundingRect = boundingRect
        
        self.distance = self.rect.width-boundingRect.width
        self.timeRemaining = timeRemaining
        
        if moveSpeed == 0:
            self.moveSpeed = self.distance/(self.timeRemaining/1000.)
        else:
            self.moveSpeed = moveSpeed
        
        self.x = initialx
        
        self.repeated = False
        
    def update(self, time):
        self.x -= self.moveSpeed*time/1000.
        self.rect.left = self.x
        if self.rect.right <= self.boundingRect.right and not self.repeated:
            self.groups()[0].add(LevelBackground(self.boundingRect, self.timeRemaining, self.image, self.moveSpeed, initialx=self.rect.right))
            self.repeated = True # Make sure it only spawns a new image ONCE.
        if self.rect.right < self.boundingRect.left:
            self.kill()

class Level(object):
    """Information a level class (or object) needs to have:
    Background image(s)
    Background music
    Enemy info (location, time, type, etc.)
    Dialog information for story mode. (Or tutorial)
    Opening and closing cutscene info. (Optional for levels)"""
    # Current vision for structure:
    # A list of levels is created from the LEVELS file
    # This module loads that list
    # The menu looks through that list and lists all the ARCADE labelled levels.
    # The menu can get objects from any item in the list
    # The list stores strings which are the names of levels, the names of levels are the same as the folders they reside in.
    # The Level class looks in that folder and loads all the necessary files that way.
    # (This comment block is a brainstorm)
    
    # Separate expensive things like loading images from the init function. This way the menu can get the info it needs without having to use too much memory for unneeded stuff.
    
    def __init__(self, name):
        self.name = name
        
        self.thumbnail = pygame.image.load(os.path.join("levels",self.name,"Thumbnail.png")).convert()
        
        descripFileName = os.path.join("levels",self.name,"description.txt")
        self.description = file(descripFileName, 'r').readlines()
    
    def parseInfoFile(self):
        # I'm choosing to comment this function heavily since it took me hours to write and I still barely understood it once I finally had it working
        #so I'm making sure that I can figure it out again if I ever need to change it or something.
        # So forgive the comments explaining the obvious.
        levelInfoFile = file(os.path.join("levels",self.name,"levelInfo"), 'r').readlines()
        self.levelInfo = {"GeneralInfo":{}} # For some reason it gives a keyerror if I don't define GeneralInfo now.
        # levelIinfo DOES NOT contain background info. That goes into the dictionary bgInfo (Defined later).
        
        # First, break the file up into sections
        sections = [] # Sections stored in text
        sectionIndices = [] # The indices of the section headers in the level info file
        for line in levelInfoFile:
            if line[0] == "#": # If the line is a section header
                sections.append(line[1:].strip()) # Make sure to get just the name of the section, no extra whitespace or the #.
                sectionIndices.append(levelInfoFile.index(line)) # Add the index of this section header in the level info file to the list.
                # We have to handle the background info separately.
                if line.strip() == "#BackgroundInfo": # Then this is the section dedicated to the backgrounds.
                    sections.remove(line[1:].strip()) # We want to handle this separately, not along with the other sections. It's differently formatted in the file.
                    # sectionIndices.remove(levelInfoFile.index(line))
                    bgIndex = levelInfoFile.index(line) # The index of the header that separates the background section from the rest.
        
        for i in sectionIndices: # I chose to use the indices for some reason. It doesn't really matter too much.
            # Get the range of lines that this section contains
            lastIndex = i+1 # The first index is the section's position in the list plus one.
            if sectionIndices.index(i) == len(sectionIndices)-1: # if the current header is the last header in the file (INCLUDING the backgroundInfo header)
                nextIndex = len(sectionIndices) # If so, then define the end of the range to be the end of something. (I THINK THIS LINE IS BROKEN BUT ALSO UNNESSECARY)
                # I'll leave it for now...
            else:
                nextIndex = sectionIndices[sectionIndices.index(i)+1]-1 # The last index is the next section's position minus one.
            
            for line in levelInfoFile[lastIndex:nextIndex]: # Iterate through the lines this section contains.
                s = sections[sectionIndices.index(i)] # The section we're working in.
                key = line[:line.index(":")] # Get the text before the colon.
                value = line[line.index(":")+1:].strip() # Get the text after the colon.
                self.levelInfo[s][key] = value
                
        log.info("Level Info: %s"%self.levelInfo) # Debugging purposes.
        
        
        
        # Now work on getting the backgrounds working.
        self.timeRemaining = int(self.levelInfo["GeneralInfo"]['time'])*1000. # I choose to define this now, but I suppose it could wait until after parsing the background info.
        self.totalTime = self.timeRemaining
        self.runTimeSoFar = 0.
        
        bgIndices = [] # Indices of the headers that define each individual background within the file.
        bgs = [] # The number of the background (0, then 1, etc.)
        self.bgInfo = {} # A dict that contains all the info for each bg. It will later contain dictionaries for each bg.
        lastIndex = len(levelInfoFile)-1 # Get the end of the file. (Unfortunately, I decided to use sensible names for the index variables here, but not before. I might clean it up later.)
        for line in levelInfoFile[bgIndex:lastIndex]: # Remember bgIndex? It was defined as the index of the header that contains the background info overall.
            # Separate out the individual backgrounds within the background info section.
            if line[0] == "-":
                bgs.append(line[1:].strip()) # This will result in adding the number of the bg (0, 1, etc.) to the bgs list.
                self.bgInfo[line[1:].strip()] = {} # Create an empty dictionary for the background.
                bgIndices.append(levelInfoFile.index(line)) # Add the index of this header to the list.
        for i in bgIndices: # Again, I chose to use indices. Mostly for consistency's sake since it really doesn't matter.
            lastIndex = i+1 # The info starts one line after the header line.
            if bgIndices.index(i) == len(bgIndices)-1: # If this is the last header.
                nextIndex = len(levelInfoFile) # The reason I think that other line is broken is because it's different from this, and this works. But the fact that it doesn't give an error means that we don't have to worry about it.
            else:
                nextIndex = bgIndices[bgIndices.index(i)+1] # The last index of this section's info is the next header minus one.
            
            # Get the info for each individual background
            for line in levelInfoFile[lastIndex:nextIndex]: # Oh look, I switched the variables again... How wonderfully inconsistent of me! Discord must have gotten to me while I wrote this.
                bg = bgs[bgIndices.index(i)] # Current BG we're working on.
                key = line[:line.index(":")] # Get the text before the colon.
                value = line[line.index(":")+1:].strip() # Get the text after the colon.
                self.bgInfo[bg][key] = value
        
        self.bgGroup = pygame.sprite.OrderedUpdates()
        for i in range(0,int(self.levelInfo["GeneralInfo"]['bglevels'])):
            fileName = os.path.join("levels",self.name,"Background-%i.png"%(i))
            self.backgroundImages.append(pygame.image.load(fileName).convert_alpha())
    
    def parseEnemyFile(self):
        fileName = os.path.join("levels",self.name,"enemies")
        enemiesFile = file(fileName, 'r').readlines()
        
        self.enemies = []
        
        for line in enemiesFile:
            line = line.strip()
            sepLocs = []
            curIndex = 0
            for char in line:
                if ":" == char:
                    sepLocs.append(curIndex)
                curIndex += 1
            
            time = float(line[:sepLocs[0]])
            initialy = int(line[sepLocs[0]+1:sepLocs[1]])
            name = line[sepLocs[1]+1:]
            self.enemies.append([time,initialy,name])
    
    def load(self, boundingRect, ship, folders):
        self.boundingRect = boundingRect
        
        self.backgroundImages = []
        
        self.parseInfoFile()
        self.parseEnemyFile()
        
        for i in self.backgroundImages:
            info = self.bgInfo[str(self.backgroundImages.index(i))]
            moveSpeed = int(info["moveSpeed"])
            LevelBackground(self.boundingRect, self.timeRemaining, i, moveSpeed, self.bgGroup)
        self.backgroundSurface = pygame.surface.Surface(self.boundingRect.size)
        
        self.done = False
        self.gameOver = False
        
              
        self.ship = ship
        self.playerGroup = pygame.sprite.RenderUpdates(self.ship)
         
        self.enemyBulletGroup = pygame.sprite.Group()
        
        self.enemyAddInterval = 5000
        # if stressTest:
            # enemyAddInterval = STEnemyInterval
        self.enemyAddTimer = self.enemyAddInterval
        
        self.enemyGroup = pygame.sprite.RenderUpdates()
        
        currentSong = self.levelInfo["GeneralInfo"]['song']
        pygame.mixer.music.load(os.path.join(folders['music'], currentSong+".mp3"))
            
    def update(self, pressedKeys, time):
        #TODO take all management from the mainloop and put it here.
        # Handle backgrounds and such
        self.timeRemaining -= time
        self.runTimeSoFar += time
        
        if self.timeRemaining <= 0:
            self.done = True #TODO make boss battles instead.
        
        self.backgroundSurface.fill((0,0,0))
        self.bgGroup.update(time)
        
        # Handle game logic.
        self.enemyBulletGroup.update(time)
        self.playerGroup.update(pressedKeys, time, self.enemyBulletGroup)
        
        if len(self.playerGroup.sprites()) == 0:
            self.gameOver = True
        else:
            for enemy in self.enemies:
                if self.runTimeSoFar/1000. >= enemy[0]:
                    log.debug("Adding enemy of type %s at %i y."%(enemy[2],enemy[1]))
                    center = (self.boundingRect.right, enemy[1])
                    addedEnemy = enemies.enemyTypes[enemy[2]](center, self.boundingRect, self.enemyBulletGroup, self.playerGroup.sprites()[0])
                    self.enemyGroup.add(addedEnemy)
                    self.enemies.remove(enemy)
            
            self.enemyGroup.update(time, self.playerGroup.sprites()[0].bulletGroup) # Will have to be modified for MULTIPLAYER (keyword)
        self.enemyBulletGroup.update(time)
            
    def draw(self, surface):
        self.bgGroup.draw(surface)
        
        self.enemyGroup.draw(surface)
        self.playerGroup.draw(surface)
        self.enemyBulletGroup.draw(surface)
        for ship in self.playerGroup.sprites():
            ship.bulletGroup.draw(surface)
            
        
class ArcadeLevel(Level):
    
    def __init__(self, name):
        Level.__init__(self, name)
        
class StoryLevel(Level):
    
    def __init__(self, name):
        Level.__init__(self, name)
        

levelInfoFile = file(os.path.join("Levels","LEVELS.txt"), 'r')
levels = levelInfoFile.readlines()
arcadeLevels = []
storyLevels = []

# This function is so that some of the initialization can be performed after certain variables are defined (Which depend on variables defined in above lines)
def initModule():
    for L in levels:
        if "[ARCADE]" in L:
            levelName = L[8:].strip()
            arcadeLevels.append(ArcadeLevel(levelName))
        elif "[STORY]" in L:
            levelName = L[7:].strip()
            storyLevels.append(StoryLevel(levelName))
        else:
            log.error("Got a corrupt level name (\"%s\")"%name)
            sys.exit()