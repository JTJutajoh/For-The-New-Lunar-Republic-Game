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

# main.py in For The New Lunar Republic. This game is created by JT Johnson (AKA DarkFlame).
# Music credits go to their respective artists, as addressed in the CREDITS.txt file. I do not own any of the music files used in this game. If you are the owner of these music files and you do not want them in this game, contact me and I will remove them promptly.
# If you don't like it, tell me what I can improve and I'll do my best. If you just disagree with my style of doing things, then I'll try to adjust, but only to a point.
# Please do not redistribute this game without my permission, I'd like to follow its progress everywhere that it's posted. See the Readme for my email.

#TODO:
#Arcade Mode:
# Make it possible for bullets to move in a direction other than one of the 8 cardinals
# Seeking bullets?
# Add HUD
# Add levels
# Add boss battles
# Make individual levels work.
# Make tutorial
#Extras:
# Add .ini file
# Add working settings screen
# Make menu items other than buttons?
# Co-Op Multiplayer?
# Score leaderboards?
#Story Mode:
# Add hubs
# Add RPG elements
# Add savegames
# Add cutscene states (And make them work!)
# Get ingame dialog working
# MAKE CONTENT!
# Add All Your Base reference...

print "SUP"

import sys, os
import random

sys.path.append(os.path.join("libs"))

import pygame
from pygame.locals import *

pygame.init() # Init pygame now so that other files can use it without having to wait.

import ships
import enemies
import levels
import states
import menus

if sys.platform == 'win32':
        # os.environ['SDL_VIDEO_WINDOW_POS'] = '3,23'
        os.environ['SDL_VIDEO_CENTERED'] = '1'

screenRect = Rect(0,0, 1000,500)
if "-fullscreen" in sys.argv:
    screen = pygame.display.set_mode(screenRect.size, FULLSCREEN | HWSURFACE | DOUBLEBUF)
elif "-noframe" in sys.argv:
    screen = pygame.display.set_mode(screenRect.size, NOFRAME)
elif "-resizable" in sys.argv:
    screen = pygame.display.set_mode(screenRect.size, RESIZABLE)
else:
    screen = pygame.display.set_mode(screenRect.size)
screen.fill((0,0,0))

# pygame.display.set_icon(pygame.image.load(os.path.join("images", "icon.ico")).convert())
pygame.display.set_caption("For The New Lunar Republic")

def blitDebugInfo(fps, currentState, surf, font, pos=(0,0)):
    surf.fill((0,255,0))
    color = (255,255,255)
    if fps < 60: color = (255,100,100)
    
    if "gamemode" in currentState.vars:
        debugString = "FPS: %i STATE: %s MODE: %s"%(fps, currentState.name, currentState.vars['gamemode'])
    else:
        debugString = "FPS: %i STATE: %s"%(fps, currentState.name)
    
    
    surf.blit(font.render(debugString, False, color, (0,0,0)), pos)
debugSurf = pygame.surface.Surface(screenRect.size)
debugSurf.fill((0,255,0))
debugSurf.set_colorkey((0,255,0))
debugFont = pygame.font.Font(os.path.join("fonts","COURBD.TTF"), 12)
if "-debug" in sys.argv or "-db" in sys.argv:
    debug = True
else:
    debug = False
    
def renderText(text, font, color, aa=True):
    surf = font.render(text, aa, color)
    return surf, surf.get_rect()
    
#TODO Make a real working background.
F_BG = pygame.surface.Surface(((screenRect.width*2)*2, screenRect.height), SRCALPHA)
M_BG = pygame.surface.Surface(((screenRect.width*3)*2, screenRect.height), SRCALPHA)
B_BG = pygame.surface.Surface(((screenRect.width*4)*2, screenRect.height), SRCALPHA)
BGs = [F_BG, M_BG, B_BG]

mult = 1
for BG in BGs:
    BG.set_colorkey((0,0,0))
    for i in range(0, 500*mult):
        BG.set_at((random.randint(0, BG.get_rect().width), random.randint(0, BG.get_rect().height)), (255,255,255))
    mult += 1
    
x_offset = 0
#TODO

# Initialize menus
menuSurf = pygame.surface.Surface(screenRect.size)
menuSurf.set_colorkey((0,0,0))
menuSurf.set_alpha(255)
# Main menu first
menu = menus.Menu(screenRect, textInfo={
    "Main":{
        "Text":"For The New Lunar Republic",
        "Color":(255,255,255),
        "Loc":(screenRect.centerx,150),
        "Font":pygame.font.Font(os.path.join("fonts","RUSQ.TTF"), 36)
        },
    "Sub":{
        "Text":"Pre-release, pre-alpha, super unstable version",
        "Color":(255,255,255),
        "Loc":(screenRect.centerx,175),
        "Font":pygame.font.Font(os.path.join("fonts","VGAFIX.FON"), 8)
        }
    },
    bgImage=pygame.image.load(os.path.join("images", "MenuBGNewLegal.png")).convert(),
    allowKeys=False)

menu.makeNewButton("Play", "Play", (screenRect.centerx, screenRect.centery-30))
menu.makeNewButton("Settings", "Settings", (screenRect.centerx, screenRect.centery+10))
menu.makeNewButton("Exit", "Exit", (screenRect.centerx, screenRect.centery+50))

# Pause menu next
pauseMenu = menus.Menu(screenRect, textInfo={
    "Main":{
        "Text":"Paused",
        "Color":(255,255,255),
        "Loc":(screenRect.centerx,150),
        "Font":pygame.font.Font(os.path.join("fonts","pf_tempesta_seven.ttf"), 36)
        }
    },
    bgImage=screen.copy(),
    allowKeys=False)

pauseMenu.makeNewButton("Resume", "Resume", (screenRect.centerx, screenRect.centery-30))
pauseMenu.makeNewButton("MainMenu", "MainMenu", (screenRect.centerx, screenRect.centery+10))

# Game mode menu next
gameModeMenu = menus.Menu(screenRect, textInfo={
    "Main":{
        "Text":"Choose a game mode",
        "Color":(255,255,255),
        "Loc":(screenRect.centerx,50),
        "Font":pygame.font.Font(os.path.join("fonts","BEBAS.TTF"), 48)
        }
    },
    bgImage=menu.bgImage,
    allowKeys=False)

gameModeMenu.makeNewButton("Story", "Story", (screenRect.centerx-75, screenRect.centery-10))
gameModeMenu.makeNewButton("Arcade", "Arcade", (screenRect.centerx+75, screenRect.centery-10))
gameModeMenu.makeNewButton("Back", "Back", (screenRect.centerx, screenRect.centery+50))

# Character select menu next
charSelectMenu = menus.Menu(screenRect, textInfo={
    "Main":{
        "Text":"Choose a Character",
        "Color":(255,255,255),
        "Loc":(screenRect.centerx,50),
        "Font":pygame.font.Font(os.path.join("fonts","BEBAS.TTF"), 48)
        }
    },
    bgImage=menu.bgImage,
    allowKeys=False)

charSelectMenu.makeNewButton("SelectChar", "SelectChar", (screenRect.centerx, screenRect.bottom-80), 1)
charSelectMenu.buttons[0].hidden = True
charSelectMenu.makeNewButton("CharSelectBack", "CharSelectBack", (screenRect.centerx, screenRect.bottom-30), 1)
yMult = 0
shipNameFont = pygame.font.Font(os.path.join("fonts","pf_tempesta_seven.ttf"), 10)
for ship in ships.shipTypes.iterkeys():
    charSelectMenu.makeNewCharSelectButton(ships.shipTypes[ship], (75,47), ship, "Button", pos=(25+(160*yMult), screenRect.centery-100), shipNameFont=shipNameFont, posOrientation=0)
    yMult += 1
# End initialize menus

# State initialization code
gameState = states.State("Game", {"level":"TestLevel", "gamemode":"Arcade"})
mainMenuState = states.State("MainMenu")
gameModeSelectState = states.State("GameModeSelect")
charSelectState = states.State("CharSelect")
pauseState = states.State("PauseMenu", {"bgSurf":pygame.surface.Surface(screenRect.size)})

currentState = mainMenuState
# End state initialization code



#TODO Temp enemy init
enemyBulletGroup = pygame.sprite.Group()

enemyGroup = pygame.sprite.RenderUpdates()
enemyGroup.add(enemies.Enemy((screenRect.right,random.randint(0,screenRect.height)), screenRect, enemyBulletGroup))
enemyGroup.sprites()[0].loadImages()
#TODO

    
    
pressedKeys = []

fadeSurf = pygame.surface.Surface(screenRect.size) # Used to fade out.
fadeSurf.set_alpha(255)
#TODO Add this to an .ini file.
fadeTime = 500 # Time in milliseconds to fade to black
fadeInTime = 250 # It's unnatural feeling for fade ins to last as long as fade outs.

clock = pygame.time.Clock()
if "-nomaxfps" in sys.argv:
    maxfps = 0
else:
    maxfps = 60 #TODO add this to an .ini file

if "-nosound" in sys.argv:
    sound = False
else: sound = True

#TODO move the fade code to these functions
def fadeIn():
    pass

def fadeOut():
    pass
    
def fadeAlpha():
    pass

done = False
while not done:
    time = clock.tick(maxfps)
    fps = clock.get_fps()
    screen.fill((0,0,0))
    
    mouseEvents = []
    
    for e in pygame.event.get():
        if e.type == QUIT:
            done = True
            
        elif e.type == KEYDOWN:
            pressedKeys.append(e.key)
            if e.key == K_UP:
                maxfps += 5
            elif e.key == K_DOWN:
                maxfps -= 5
            if maxfps < 0: maxfps = 0
            elif maxfps > 60: maxfps = 60
        elif e.type == KEYUP:
            if e.key in pressedKeys:
                pressedKeys.remove(e.key)
                
        elif e.type == MOUSEBUTTONDOWN:
            mouseEvents.append(e)
    
    
    if currentState == gameState:
        # For now, this is the best way to check to see if the game was just faded into.
        if fadeSurf.get_alpha() > 0:
            ship = ships.shipTypes[currentState.vars['Ship']](center=(75,screenRect.centery), bounds=screenRect)
            playerGroup = pygame.sprite.RenderUpdates(ship)        
        x_offset += 1 #TODO
        
        #TODO BG stuff.
        mult = 1
        for BG in BGs:
            screen.blit(BG, (-x_offset*mult,0))
            mult += 1
        #TODO
        
        playerGroup.update(pressedKeys, time, enemyBulletGroup)
        if len(playerGroup.sprites()) == 0:
            currentState = mainMenuState
            alpha = 0
            curTime = 0
            origSurf = screen.copy()
            while curTime < fadeTime:
                screen.blit(origSurf, (0,0))
                curTime += clock.tick(maxfps)
                alpha = (curTime*1./fadeTime*1.*100)*255/100 # Convert the percent of time passed to the 255 scale
                fadeSurf.set_alpha(alpha)
                screen.blit(fadeSurf, (0,0))
                pygame.display.update()
        else:
            enemyGroup.update(time, playerGroup.sprites()[0].bulletGroup) # Will have to be modified for MULTIPLAYER (keyword)
            enemyGroup.draw(screen)
            playerGroup.draw(screen)
            enemyBulletGroup.update(time)
            enemyBulletGroup.draw(screen)
            for ship in playerGroup.sprites():
                ship.bulletGroup.draw(screen)
            
            
        # Figure out if the game was just faded into and if so, fade into the game.
        if fadeSurf.get_alpha() > 0:
            ship = ships.shipTypes[currentState.vars['Ship']](center=(75,screenRect.centery), bounds=screenRect)
            playerGroup = pygame.sprite.RenderUpdates(ship)
            curTime = fadeInTime
            origSurf = screen.copy()
            while curTime > 0:
                screen.blit(origSurf, (0,0))
                curTime -= clock.tick(maxfps)
                alpha = (curTime*1./fadeInTime*1.*100)*255/100 # Convert the percent of time passed to the 255 scale
                fadeSurf.set_alpha(alpha)
                screen.blit(fadeSurf, (0,0))
                pygame.display.update()
            pygame.mixer.music.load(os.path.join("music", "For The New Lunar Republic.mp3"))
            if sound:
                pygame.mixer.music.play(-1)
            
            
        if K_ESCAPE in pressedKeys:
            currentState = pauseState
            currentState.vars['bgSurf'] = screen.copy()
            pressedKeys.remove(K_ESCAPE)
            
            if sound:
                pygame.mixer.music.pause()
    elif currentState == mainMenuState:
        menu.everyFrame(pressedKeys, mouseEvents)
        menu.update(time)
        menu.draw(menuSurf)
        
        screen.blit(menuSurf, (0,0))
            
        # Figure out if the menu was just faded into and if so, fade into the menu.
        if menuSurf.get_alpha() < 255:
            alpha = 0
            curTime = 0
            origSurf = menu.bgImage
            while curTime < fadeTime:
                screen.blit(origSurf, (0,0))
                curTime += clock.tick(maxfps)
                alpha = (curTime*1./fadeInTime*1.*100)*255/100 # Convert the percent of time passed to the 255 scale
                menuSurf.set_alpha(alpha)
                screen.blit(menuSurf, (0,0))
                pygame.display.update()
        if fadeSurf.get_alpha() > 0:
            pygame.mixer.music.load(os.path.join("music", "Luna Deos.mp3"))
            if sound:
                pygame.mixer.music.play(-1)
            alpha = 255
            curTime = fadeInTime
            origSurf = screen.copy()
            while curTime > 0:
                screen.blit(origSurf, (0,0))
                curTime -= clock.tick(maxfps)
                alpha = (curTime*1./fadeInTime*1.*100)*255/100 # Convert the percent of time passed to the 255 scale
                fadeSurf.set_alpha(alpha)
                screen.blit(fadeSurf, (0,0))
                pygame.display.update()
                
        if menu.pressedButton == "Play":
            # Fade to the next menu
            alpha = 255
            curTime = fadeTime
            origSurf = menu.bgImage
            while curTime > 0:
                screen.blit(origSurf, (0,0))
                curTime -= clock.tick(maxfps)
                alpha = (curTime*1./fadeTime*1.*100)*255/100 # Convert the percent of time passed to the 255 scale
                menuSurf.set_alpha(alpha)
                screen.blit(menuSurf, (0,0))
                pygame.display.update()
            
            clock.tick(maxfps) # If you don't do this, it messes up the first stuff in the game.
            currentState = gameModeSelectState
            
            menu.reinit()
        elif menu.pressedButton == "Exit":
            alpha = 0
            curTime = 0
            origSurf = screen.copy()
            pygame.mixer.music.fadeout(fadeTime)
            while curTime < fadeTime:
                screen.blit(origSurf, (0,0))
                curTime += clock.tick(maxfps)
                alpha = (curTime*1./fadeTime*1.*100)*255/100 # Convert the percent of time passed to the 255 scale
                fadeSurf.set_alpha(alpha)
                screen.blit(fadeSurf, (0,0))
                pygame.display.update()
            done = True
        elif menu.pressedButton == "Settings":
            menu.reinit()
            print "Not implemented"
    elif currentState == gameModeSelectState:
        gameModeMenu.everyFrame(pressedKeys, mouseEvents)
        gameModeMenu.update(time)
        gameModeMenu.draw(menuSurf)
        
        screen.blit(menuSurf, (0,0))
        
        # Figure out if the game was just faded into and if so, fade into the menu.
        if menuSurf.get_alpha() <= 0:
            alpha = 0
            curTime = 0
            origSurf = charSelectMenu.bgImage
            while curTime < fadeInTime:
                screen.blit(origSurf, (0,0))
                curTime += clock.tick(maxfps)
                alpha = (curTime*1./fadeInTime*1.*100)*255/100 # Convert the percent of time passed to the 255 scale
                menuSurf.set_alpha(alpha)
                screen.blit(menuSurf, (0,0))
                pygame.display.update()
                
        if gameModeMenu.pressedButton == "Arcade":
            # Fade to the next menu
            alpha = 255
            curTime = fadeTime
            origSurf = menu.bgImage
            while curTime > 0:
                screen.blit(origSurf, (0,0))
                curTime -= clock.tick(maxfps)
                alpha = (curTime*1./fadeTime*1.*100)*255/100 # Convert the percent of time passed to the 255 scale
                menuSurf.set_alpha(alpha)
                screen.blit(menuSurf, (0,0))
                pygame.display.update()
            
            clock.tick(maxfps) # If you don't do this, it messes up the first stuff in the game.
            currentState = charSelectState
            currentState.vars["gamemode"] = "Arcade"
            
            gameModeMenu.reinit()
        elif gameModeMenu.pressedButton == "Story":
            gameModeMenu.reinit()
            print "Not implemented"
        elif gameModeMenu.pressedButton == "Back":
            currentState = mainMenuState
            alpha = 255
            curTime = fadeTime
            origSurf = menu.bgImage
            while curTime > 0:
                screen.blit(origSurf, (0,0))
                curTime -= clock.tick(maxfps)
                alpha = (curTime*1./fadeTime*1.*100)*255/100 # Convert the percent of time passed to the 255 scale
                menuSurf.set_alpha(alpha)
                screen.blit(menuSurf, (0,0))
                pygame.display.update()
            gameModeMenu.reinit()        
    elif currentState == charSelectState:
        charSelectMenu.everyFrame(pressedKeys, mouseEvents)
        charSelectMenu.update(time)
        charSelectMenu.draw(menuSurf)
        
        if charSelectMenu.pressedShipButton != None:
            charSelectMenu.buttons[0].hidden = False
            
        screen.blit(menuSurf, (0,0))
        
        # Figure out if the game was just faded into and if so, fade into the menu.
        if menuSurf.get_alpha() <= 0:
            alpha = 0
            curTime = 0
            origSurf = charSelectMenu.bgImage
            while curTime < fadeInTime:
                screen.blit(origSurf, (0,0))
                curTime += clock.tick(maxfps)
                alpha = (curTime*1./fadeInTime*1.*100)*255/100 # Convert the percent of time passed to the 255 scale
                menuSurf.set_alpha(alpha)
                screen.blit(menuSurf, (0,0))
                pygame.display.update()
        
        if charSelectMenu.pressedButton == "SelectChar":
            if not charSelectMenu.pressedShipButton == None: # Make sure the user has actually selected a ship first
                currentState = gameState
                currentState.vars["Ship"] = charSelectMenu.pressedShipButton[5:]
                if sound:
                    pygame.mixer.music.stop()
                alpha = 0
                curTime = 0
                origSurf = screen.copy()
                pygame.mixer.music.fadeout(fadeTime)
                while curTime < fadeTime:
                    screen.blit(origSurf, (0,0))
                    curTime += clock.tick(maxfps)
                    alpha = (curTime*1./fadeTime*1.*100)*255/100 # Convert the percent of time passed to the 255 scale
                    fadeSurf.set_alpha(alpha)
                    screen.blit(fadeSurf, (0,0))
                    pygame.display.update()
                charSelectMenu.reinit()
            else:
                charSelectMenu.reinit()
        
        elif charSelectMenu.pressedButton == "CharSelectBack":
            currentState = gameModeSelectState
            alpha = 255
            curTime = fadeTime
            origSurf = menu.bgImage
            while curTime > 0:
                screen.blit(origSurf, (0,0))
                curTime -= clock.tick(maxfps)
                alpha = (curTime*1./fadeTime*1.*100)*255/100 # Convert the percent of time passed to the 255 scale
                menuSurf.set_alpha(alpha)
                screen.blit(menuSurf, (0,0))
                pygame.display.update()
            charSelectMenu.reinit()        
    elif currentState == pauseState:
        # screen.blit(currentState.vars['bgSurf'], (0,0))
        pauseMenu.bgImage = currentState.vars['bgSurf']
        
        pauseMenu.everyFrame(pressedKeys, mouseEvents)
        pauseMenu.update(time)
        pauseMenu.draw(screen)
        
        if K_ESCAPE in pressedKeys or pauseMenu.pressedButton == "Resume":
            currentState = gameState
            if K_ESCAPE in pressedKeys:
                pressedKeys.remove(K_ESCAPE)
            
            if sound:
                pygame.mixer.music.unpause()
            pauseMenu.reinit()
        elif pauseMenu.pressedButton == "MainMenu":
            currentState = mainMenuState
            alpha = 0
            curTime = 0
            origSurf = screen.copy()
            while curTime < fadeTime:
                screen.blit(origSurf, (0,0))
                curTime += clock.tick(maxfps)
                alpha = (curTime*1./fadeTime*1.*100)*255/100 # Convert the percent of time passed to the 255 scale
                fadeSurf.set_alpha(alpha)
                screen.blit(fadeSurf, (0,0))
                pygame.display.update()
            pauseMenu.reinit()
            
            if sound:
                pygame.mixer.music.stop()
        
    else:
        print "Oops, something went wrong. The current state was assigned to an unhandled instance (%s). Most likely programming error."%currentState.name
        print "Resetting you to the main menu... Sorry for any progress lost."
        currentState = mainMenuState
    
    
    blitDebugInfo(clock.get_fps(), currentState, debugSurf, debugFont)
    if debug:
        screen.blit(debugSurf, (0,0))
    
    pygame.display.update()