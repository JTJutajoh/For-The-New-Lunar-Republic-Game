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


class HUD(pygame.sprite.Group):
    
    def __init__(self, rect, boundingRect, level, fonts, *args):
        pygame.sprite.Group.__init__(self, *args)
        
        self.level = level
        
        self.rect = rect
        self.surface = pygame.surface.Surface(self.rect.size)
        self.surface.set_alpha(200)
        
        self.boundingRect = boundingRect
        
        self.fonts = fonts
        
    def load(self):
        self.HPBar = HPBar(self.level.playerGroup.sprites()[0], self) #TODO MULTIPLAYER This will have to change for Multiplayer
        self.fireBar = FireBar(self.level.playerGroup.sprites()[0], self)
        self.fireBar.rect.right = self.rect.right
        self.regenBar = RegenBar(self.level.playerGroup.sprites()[0], self)
        self.regenBar.rect.centerx = self.rect.centerx
        self.add(self.HPBar)
        self.bossBar = BossHPBar(self.level.boss, self)
        self.bossBar.rect.centerx = self.rect.centerx
        self.bossBar.rect.top = 5
        self.add(self.HPBar)
        self.add(self.fireBar)
        self.add(self.regenBar)
        self.add(self.bossBar)
        
    def draw(self, surface):
        self.surface.fill((0,0,0))
        #TODO Had to jury-rig this one.
        self.remove(self.bossBar)
        pygame.sprite.Group.draw(self, self.surface)
        self.add(self.bossBar)
        if self.level.inBoss:
            surface.blit(self.bossBar.image, (self.bossBar.rect.left+self.boundingRect.left,self.boundingRect.top+self.bossBar.rect.top))
        
        health = self.HPBar.ship.health
        if health < 0: health = 0
        textSurf = self.fonts['hp'].render("HP: %i/%i"%(health,self.HPBar.ship.maxHealth), True, (200,200,200))
        textSurf = textSurf.subsurface(textSurf.get_bounding_rect()) # Crop it.
        textRect = textSurf.get_rect()
        textRect.left = self.rect.left+2
        
        self.surface.blit(textSurf, (textRect.left,self.HPBar.rect.bottom+2))
        
        textSurf = self.fonts['hp'].render("FIRE: %i/%i"%(self.HPBar.ship.fireCounter,self.HPBar.ship.fireInterval), True, (200,200,200))
        textSurf = textSurf.subsurface(textSurf.get_bounding_rect()) # Crop it.
        textRect = textSurf.get_rect()
        textRect.right = self.rect.right-2
        
        self.surface.blit(textSurf, (textRect.left,self.fireBar.rect.bottom+2))
        
        textSurf = self.fonts['hp'].render("REGEN: %i/%i"%(self.regenBar.ship.regenCounter/1000,self.regenBar.ship.regenInterval/1000), True, (200,200,200))
        textSurf = textSurf.subsurface(textSurf.get_bounding_rect()) # Crop it.
        textRect = textSurf.get_rect()
        textRect.centerx = self.rect.centerx
        
        self.surface.blit(textSurf, (textRect.left,self.regenBar.rect.bottom+2))
        
        if self.level.inBoss:
            textSurf = self.fonts['bosshp'].render("BOSS: %i/%i"%(self.bossBar.boss.health,self.bossBar.boss.maxHealth), True, (200,200,200))
            textSurf = textSurf.subsurface(textSurf.get_bounding_rect()) # Crop it.
            textRect = textSurf.get_rect()
            textRect.centerx = self.boundingRect.centerx
            
            surface.blit(textSurf, (textRect.left,self.boundingRect.top+self.bossBar.rect.top+6))
        
        # Blit the whole HUD
        surface.blit(self.surface, (self.rect.left+self.boundingRect.left, self.rect.top+self.boundingRect.top))
        
class HUDElement(pygame.sprite.Sprite):

    """Superclass for all HUD elements. Should not be instansiated directly."""
    
    def __init__(self, *args):
        pygame.sprite.Sprite.__init__(self, *args)
        
        self.parent = None

class FireBar(HUDElement):
    
    def __init__(self, ship, parent, *args):
        HUDElement.__init__(self, *args)
        
        self.parent = parent
        
        self.ship = ship
        
        self.origImage = pygame.image.load(os.path.join("images", "HUD", "HPBar.png")).convert_alpha()
        self.rect = self.origImage.get_rect()
        
        self.image = pygame.surface.Surface(self.rect.size)
        self.image.set_colorkey((0,255,0))
        
        self.barWidth = self.rect.width-2
        self.barHeight = self.rect.height-3
        self.fillx = 2 # Where should the fill start?
        self.filly = 1 # Hehe filly...
        
        self.bgFill = (75,75,75)
        
    def fillBar(self):
        self.image.fill(self.bgFill)
        barFillPercent = ((self.ship.fireCounter*1.)/(self.ship.fireInterval))*100.
        barFillAmount = (barFillPercent*self.barWidth)/100.
        
        if barFillAmount <= 0:
            barFillAmount = 0
        else:
            pygame.draw.rect(self.image, (175,125,25), Rect(self.fillx,self.filly, barFillAmount,self.barHeight))
        self.image.blit(self.origImage, (0,0))
        
    def update(self, time):
        HUDElement.update(self, time)
        
        self.fillBar()
        
class RegenBar(HUDElement):
    
    def __init__(self, ship, parent, *args):
        HUDElement.__init__(self, *args)
        
        self.parent = parent
        
        self.ship = ship
        
        self.origImage = pygame.image.load(os.path.join("images", "HUD", "HPBar.png")).convert_alpha()
        self.rect = self.origImage.get_rect()
        self.normX = self.rect.right
        self.normY = self.rect.top
        
        self.image = pygame.surface.Surface(self.rect.size)
        self.image.set_colorkey((0,255,0))
        
        self.barWidth = self.rect.width-2
        self.barHeight = self.rect.height-3
        self.fillx = 2 # Where should the fill start?
        self.filly = 1 # Hehe filly...
        
        self.bgFill = (75,75,75)
        
    def fillBar(self):
        self.image.fill(self.bgFill)
        barFillPercent = ((self.ship.regenCounter*1.)/(self.ship.regenInterval))*100.
        barFillAmount = (barFillPercent*self.barWidth)/100.
        
        if barFillAmount <= 0:
            barFillAmount = 0
        else:
            pygame.draw.rect(self.image, (25,10,150), Rect(self.fillx,self.filly, barFillAmount,self.barHeight))
        self.image.blit(self.origImage, (0,0))
        
    def update(self, time):
        HUDElement.update(self, time)
        
        self.fillBar()
        
class HPBar(HUDElement):
    
    def __init__(self, ship, parent, *args):
        HUDElement.__init__(self, *args)
        
        self.parent = parent
        
        self.ship = ship
        
        self.origImage = pygame.image.load(os.path.join("images", "HUD", "HPBar.png")).convert_alpha()
        self.rect = self.origImage.get_rect()
        self.normX = self.rect.right
        self.normY = self.rect.top
        
        self.image = pygame.surface.Surface(self.rect.size)
        self.image.set_colorkey((0,255,0))
        
        self.barWidth = self.rect.width-2
        self.barHeight = self.rect.height-3
        self.fillx = 2 # Where should the fill start?
        self.filly = 1 # Hehe filly...
        
        self.bgFill = (75,75,75)
        
        self.lastHealth = self.ship.health*1
        
    def fillBar(self):
        self.image.fill(self.bgFill)
        barFillPercent = ((self.ship.health*1.)/(self.ship.maxHealth))*100.
        barFillAmount = (barFillPercent*self.barWidth)/100.
        
        if barFillAmount <= 0:
            barFillAmount = 0
        else:
            if barFillPercent < 40:
                barColor = (200,50,50)
            else:
                barColor = (50,200,50)
            if self.lastHealth > self.ship.health: # If the ship took damage
                self.rect.right = self.normX+3
                self.rect.top = self.normY+5
            else: # If the ship did not take damage.
                self.rect.right = self.normX
                self.rect.top = self.normY
            pygame.draw.rect(self.image, barColor, Rect(self.fillx,self.filly, barFillAmount,self.barHeight))
        self.image.blit(self.origImage, (0,0))
        
        self.lastHealth = self.ship.health*1
        
    def update(self, time):
        HUDElement.update(self, time)
        
        self.fillBar()
        
class BossHPBar(HUDElement):
    
    def __init__(self, boss, parent, *args):
        HUDElement.__init__(self, *args)
        
        self.parent = parent
        
        self.boss = boss
        
        self.origImage = pygame.image.load(os.path.join("images", "HUD", "BossHPBar.png")).convert_alpha()
        self.rect = self.origImage.get_rect()
        
        self.blankImage = pygame.surface.Surface(self.rect.size)
        self.blankImage.set_colorkey((0,0,0))
        self.image = self.blankImage.copy()
        self.image.set_colorkey((0,255,0))
        
        self.barWidth = self.rect.width-2
        self.barHeight = self.rect.height-3
        self.fillx = 2 # Where should the fill start?
        self.filly = 1 # Hehe filly...
        
        self.bgFill = (75,75,75)
        
    def fillBar(self):
        self.image.fill(self.bgFill)
        barFillPercent = ((self.boss.health*1.)/(self.boss.maxHealth))*100.
        barFillAmount = (barFillPercent*self.barWidth)/100.
        
        if barFillAmount <= 0:
            barFillAmount = 0
        else:
            barColor = (200,50,50)
            pygame.draw.rect(self.image, barColor, Rect(self.fillx,self.filly, barFillAmount,self.barHeight))
        self.image.blit(self.origImage, (0,0))
        
    def update(self, time):
        HUDElement.update(self, time)
        
        self.fillBar()
        
        if not self.parent.level.inBoss:
            self.image = self.blankImage