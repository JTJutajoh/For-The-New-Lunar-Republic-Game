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
# Clean up code
# Optimize code
#Arcade Mode:
# Seeking bullets?
# Add HUD
# Add levels
# Add boss battles
# Make individual levels work.
# Make tutorial
#Extras:
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

__version__ = "prerelease 4"
__author__ = "J.T. Johnson"
releaseNotes = file("RELEASE NOTES.txt", 'r').readlines()
cfgFilename = "For The New Lunar Republic.cfg"

import sys, os
import random

if len(sys.argv) > 1:
    for param in sys.argv[1:]:
        print "Parameter: "+param
print "Version %s by %s"%(__version__, __author__)
print
print
print "New in this version:"
print
count = 1
for line in releaseNotes:
    if "\n" in line: line = line[:-2]
    print str(count)+"."+(" "*4)+line
    count += 1
print
print

import pygame
from pygame.locals import *

import inifiles

# Set up the config file.
config = inifiles.main({
    "Display":{
        "maxfps":60,
        "fillcolor_r":0,
        "fillcolor_g":0,
        "fillcolor_b":0,
        "fullscreen":0,
        "fullscaling":0,
        "windowedframe":1,
        "windowedresize":0
        },
    "Files":{
        "imagesfolder":"images",
        "musicfolder":"music",
        "fontsfolder":"fonts"
        },
    "Sounds":{
        "musicvolume":100
        },
    "Menus":{
        "fadeintime":250,
        "fadeouttime":500
        },
    "Fonts":{
        "debugfont":"COURBD.TTF",
        "mainheaderfont":"BEBAS.TTF"
        }
    },
    {
        
    },
    cfgFilename)
    
folders = {"images":config.get("Files",'imagesfolder'),
"music":config.get("Files",'musicfolder'),
"fonts":config.get("Files",'fontsfolder')}

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

videoInfo = pygame.display.Info() # Used primarily to get the user's desktop resolution, but for other things too maybe.

def setWindowedMode():
    screenRect.topleft = (0,0)
    if "-noframe" in sys.argv or not config.getboolean("Display", 'windowedframe'):
        screen = pygame.display.set_mode(screenRect.size, NOFRAME)
    elif "-resizable" in sys.argv or config.getboolean("Display", 'windowedresize'):
        screen = pygame.display.set_mode(screenRect.size, RESIZABLE)
    else:
        screen = pygame.display.set_mode(screenRect.size)
    
    return screen
    
def setFullscreenMode(scaling):
    if not videoInfo.hw:
        print "Your computer does not support hardware accelerated surfaces. The game might run a bit slower than on a platform that might."
    if scaling:
        screen = pygame.display.set_mode(screenRect.size, FULLSCREEN | HWSURFACE | DOUBLEBUF)
    else:
        screen = pygame.display.set_mode((videoInfo.current_w,videoInfo.current_h), FULLSCREEN | HWSURFACE | DOUBLEBUF)
        screenRect.center = screen.get_rect().center
    
    return screen

setWindowedMode()
    
# Decide how to display the window based on the command line arguments and the config file.
if "-fullscreen" in sys.argv or config.getboolean("Display", 'fullscreen') or not videoInfo.wm:
    if not videoInfo.wm:
        print "Your platform does not support windowed mode."
    if not config.getboolean("Display", 'fullscaling') or "-noscale" in sys.argv:
        screen = setFullscreenMode(scaling=False)
    else:
        screen = setFullscreenMode(scaling=True)
    fullscreen = True
else:
    screen = setWindowedMode()
    fullscreen = False
fillColor = (config.getint("Display", 'fillcolor_r'),config.getint("Display", 'fillcolor_g'),config.getint("Display", 'fillcolor_b'))
screen.fill(fillColor)

# pygame.display.set_icon(pygame.image.load(os.path.join(folders['images'], "icon.ico")).convert())
pygame.display.set_caption("For The New Lunar Republic")

def blitDebugInfo(fps, currentState, fullscreen, surf, font, maxfps, pos=(0,0)):
    surf.fill((0,255,0))
    color = (255,255,255)
    if fps < maxfps: color = (255,100,100)
    
    debugString = "FPS: %i STATE: %s"%(fps, currentState.name)
    
    if "gamemode" in currentState.vars:
        debugString = debugString + " MODE: %s"%(fps, currentState.name, currentState.vars['gamemode'])
    
    if fullscreen:
        debugString = debugString + " FULLSCREEN"
    
    surf.blit(font.render(debugString, False, color, (0,0,0)), pos)
debugSurf = pygame.surface.Surface(screenRect.size)
debugSurf.fill((0,255,0))
debugSurf.set_colorkey((0,255,0))
debugFont = pygame.font.Font(os.path.join(folders['fonts'],config.get("Fonts",'debugfont')), 12)
if "-debug" in sys.argv or "-db" in sys.argv:
    debug = True
else:
    debug = False
    
def renderText(text, font, color, aa=True):
    surf = font.render(text, aa, color)
    return surf, surf.get_rect()
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

# Menu fonts
mainHeaderFont = pygame.font.Font(os.path.join(folders['fonts'],config.get("Fonts",'mainheaderfont')), 48)

menuSurf = pygame.surface.Surface(screen.get_rect().size, HWSURFACE)
menuSurf.set_colorkey((0,0,0))
menuSurf.set_alpha(255)
# Main menu first
menu = menus.Menu(screenRect, textInfo={
    "Main":{
        "Text":"For The New Lunar Republic",
        "Color":(255,255,255),
        "Loc":(screenRect.centerx,screenRect.top+50),
        "Font":mainHeaderFont
        },
    "Sub":{
        "Text":"Version %s by %s"%(__version__, __author__),
        "Color":(255,255,255),
        "Loc":(screenRect.centerx,screenRect.top+100),
        "Font":pygame.font.Font(os.path.join(folders['fonts'],"VGAFIX.FON"), 8)
        }
    },
    bgImage=pygame.image.load(os.path.join(folders['images'], "MenuBGNewLegal.png")).convert(),
    allowKeys=False)

menu.makeNewButton("Play", "Play", (screenRect.centerx, screenRect.centery-30))
menu.makeNewButton("Settings", "Settings", (screenRect.centerx, screenRect.centery+10))
menu.makeNewButton("Exit", "Exit", (screenRect.centerx, screenRect.centery+50))

# Pause menu next
pauseMenu = menus.Menu(screenRect, textInfo={
    "Main":{
        "Text":"Paused",
        "Color":(255,255,255),
        "Loc":(screenRect.centerx, screenRect.top+50),
        "Font":mainHeaderFont
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
        "Loc":(screenRect.centerx, screenRect.top+50),
        "Font":mainHeaderFont
        }
    },
    bgImage=menu.bgImage,
    allowKeys=False)

gameModeMenu.makeNewButton("Story", "Story", (screenRect.centerx-75, screenRect.centery-10))
gameModeMenu.makeNewButton("Arcade", "Arcade", (screenRect.centerx+75, screenRect.centery-10))
gameModeMenu.makeNewButton("Back", "Back", (screenRect.centerx, screenRect.centery+50))

# Settings Menu
settingsMenu = menus.Menu(screenRect, textInfo={
    "Main":{
        "Text":"Settings",
        "Color":(255,255,255),
        "Loc":(screenRect.centerx, screenRect.top+50),
        "Font":mainHeaderFont
        }
    },
    bgImage=menu.bgImage,
    allowKeys=False)

settingsMenu.makeNewButton("Back", "Back", (screenRect.centerx, screenRect.bottom-30))

# Character select menu next
charSelectMenu = menus.Menu(screenRect, textInfo={
    "Main":{
        "Text":"Choose a Character",
        "Color":(255,255,255),
        "Loc":(screenRect.centerx, screenRect.top+50),
        "Font":mainHeaderFont
        }
    },
    bgImage=menu.bgImage,
    allowKeys=False)

charSelectMenu.makeNewButton("SelectChar", "SelectChar", (screenRect.centerx, screenRect.bottom-80), 1)
charSelectMenu.buttons[0].hidden = True
charSelectMenu.makeNewButton("CharSelectBack", "CharSelectBack", (screenRect.centerx, screenRect.bottom-30), 1)
xMult = 0
shipNameFont = pygame.font.Font(os.path.join(folders['fonts'],"pf_tempesta_seven.ttf"), 10)
for ship in ships.shipTypes.iterkeys():
    charSelectMenu.makeNewCharSelectButton(ships.shipTypes[ship], (75,47), ship, "Button", pos=(screenRect.left+25+(160*xMult), screenRect.centery-100), shipNameFont=shipNameFont, posOrientation=0)
    xMult += 1
# End initialize menus

# State initialization code
gameState = states.State("Game", {"level":"TestLevel", "gamemode":"Arcade"})
mainMenuState = states.State("MainMenu")
gameModeSelectState = states.State("GameModeSelect")
charSelectState = states.State("CharSelect")
settingsState = states.State("Settings")
pauseState = states.State("PauseMenu", {"bgSurf":pygame.surface.Surface(screenRect.size)})

currentState = mainMenuState
# End state initialization code  
    
pressedKeys = []

fadeSurf = pygame.surface.Surface(screen.get_rect().size) # Used to fade in and out.
fadeSurf.set_alpha(255)
fadeTime = config.getint("Menus", 'fadeouttime') # Time in milliseconds to fade.
fadeInTime = config.getint("Menus", 'fadeintime')
# Make sure the user hasn't set the fade time to some ridiculous amount of time.

clock = pygame.time.Clock()
if "-nomaxfps" in sys.argv:
    maxfps = 0
else:
    maxfps = config.getint("Display", "maxfps")

if "-nosound" in sys.argv:
    sound = False
else: sound = True

invincible = False
if "-invincible" in sys.argv:
    invincible = True

stressTest = False
if "-stresstest" in sys.argv:
    stressTest = True
    debug = True
    maxfps = 0
    if "-binterval" in sys.argv:
        STBulletInterval = int(sys.argv[sys.argv.index("-binterval")+1])
    else:
        STBulletInterval = 100
    if "-einterval" in sys.argv:
        STEnemyInterval = int(sys.argv[sys.argv.index("-einterval")+1])
    else:
        STEnemyInterval = 100

def fadeFromBlack(origSurf):
    alpha = 255
    curTime = fadeInTime
    while curTime > 0:
        screen.blit(origSurf, (0,0))
        curTime -= clock.tick(maxfps)
        alpha = (curTime*1./fadeInTime*1.*100)*255/100 # Convert the percent of time passed to the 255 scale
        fadeSurf.set_alpha(alpha)
        screen.blit(fadeSurf, (0,0))
        pygame.display.update()

def fadeToBlack(origSurf):
    alpha = 0
    curTime = 0
    while curTime < fadeTime:
        screen.blit(origSurf, (0,0))
        curTime += clock.tick(maxfps)
        alpha = (curTime*1./fadeTime*1.*100)*255/100 # Convert the percent of time passed to the 255 scale
        fadeSurf.set_alpha(alpha)
        screen.blit(fadeSurf, (0,0))
        pygame.display.update()

def fadeOutMenu(origSurf):
    alpha = 255
    curTime = fadeTime
    while curTime > 0:
        screen.blit(origSurf, screenRect.topleft)
        curTime -= clock.tick(maxfps)
        alpha = (curTime*1./fadeTime*1.*100)*255/100 # Convert the percent of time passed to the 255 scale
        menuSurf.set_alpha(alpha)
        screen.blit(menuSurf, (0,0))
        pygame.display.update()
        
def fadeInMenu(origSurf):
    alpha = 0
    curTime = 0
    while curTime < fadeInTime:
        screen.blit(origSurf, screenRect.topleft)
        curTime += clock.tick(maxfps)
        alpha = (curTime*1./fadeInTime*1.*100)*255/100 # Convert the percent of time passed to the 255 scale
        menuSurf.set_alpha(alpha)
        screen.blit(menuSurf, (0,0))
        pygame.display.update()
    
done = False

bm = pygame.time.Clock()
while not done:
    time = clock.tick(maxfps)
    fps = clock.get_fps()
    screen.fill(fillColor)
    
    mouseEvents = []
    
    for e in pygame.event.get():
        if e.type == QUIT:
            done = True
            
        elif e.type == KEYDOWN:
            pressedKeys.append(e.key)
        elif e.type == KEYUP:
            if e.key in pressedKeys:
                pressedKeys.remove(e.key)
                
        elif e.type == MOUSEBUTTONDOWN:
            mouseEvents.append(e)
    
    
    if currentState == gameState:
        # For now, this is the best way to check to see if the game was just faded into.
        if fadeSurf.get_alpha() > 0:
            ship = ships.shipTypes[currentState.vars['Ship']](center=(screenRect.left+75,screenRect.centery), bounds=screenRect)
            playerGroup = pygame.sprite.RenderUpdates(ship)        
        x_offset += 1 #TODO
        
        #TODO BG stuff.
        mult = 1
        for BG in BGs:
            screen.blit(BG, (screenRect.left-x_offset*mult,screenRect.top))
            mult += 1
        #TODO
        
        # Figure out if the game was just faded into and if so, fade into the game.
        if fadeSurf.get_alpha() > 0:
            ship = ships.shipTypes[currentState.vars['Ship']](center=(75,screenRect.centery), bounds=screenRect, invincible=invincible)
            playerGroup = pygame.sprite.RenderUpdates(ship)
             
            enemyBulletGroup = pygame.sprite.Group()
            
            enemyAddInterval = 5000
            if stressTest:
                enemyAddInterval = STEnemyInterval
            enemyAddTimer = enemyAddInterval
            
            enemyGroup = pygame.sprite.RenderUpdates()

            fadeFromBlack(screen.copy())
            pygame.mixer.music.load(os.path.join(folders['music'], "For The New Lunar Republic.mp3"))
            pygame.mixer.music.set_volume(config.getint("Sounds", 'musicvolume')/100.)
            if sound:
                pygame.mixer.music.play(-1)
        
        enemyBulletGroup.update(time)
        playerGroup.update(pressedKeys, time, enemyBulletGroup)
        if stressTest:
            print "Bullets on screen: %i"%len(enemyBulletGroup)
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
            enemyAddTimer += time
            if enemyAddTimer >= enemyAddInterval:
                addedEnemy = enemies.AlphaEnemy((screenRect.right,random.randint(screenRect.top,screenRect.bottom)), screenRect, enemyBulletGroup, playerGroup.sprites()[0])
                if stressTest:
                    addedEnemy.fireInterval = STBulletInterval
                enemyGroup.add(addedEnemy)
                enemyAddTimer = 0
            
            enemyGroup.update(time, playerGroup.sprites()[0].bulletGroup) # Will have to be modified for MULTIPLAYER (keyword)
            enemyGroup.draw(screen)
            playerGroup.draw(screen)
            enemyBulletGroup.update(time)
            enemyBulletGroup.draw(screen)
            for ship in playerGroup.sprites():
                ship.bulletGroup.draw(screen)
            
        if K_ESCAPE in pressedKeys:
            currentState = pauseState
            currentState.vars['bgSurf'] = screen.copy()
            pressedKeys.remove(K_ESCAPE)
            
            if sound:
                pygame.mixer.music.pause()
    elif currentState == mainMenuState:
        menu.everyFrame(pressedKeys, mouseEvents)
        menu.update(time)
        menu.draw(screen)
            
        # Figure out if the menu was just faded into and if so, fade into the menu.
        if menuSurf.get_alpha() < 255:
            menu.draw(menuSurf)
            fadeInMenu(menu.bgImage)
        if fadeSurf.get_alpha() > 0:
            pygame.mixer.music.load(os.path.join(folders['music'], "Luna Deos.mp3"))
            pygame.mixer.music.set_volume(config.getint("Sounds", 'musicvolume')/100.)
            if sound:
                pygame.mixer.music.play(-1)
            fadeFromBlack(screen.copy())
                
        if menu.pressedButton == "Play":
            menu.draw(menuSurf)
            fadeOutMenu(menu.bgImage)
            currentState = gameModeSelectState
            
            menu.reinit()
        elif menu.pressedButton == "Exit":
            pygame.mixer.music.fadeout(fadeTime)
            fadeToBlack(screen.copy())
            done = True
        elif menu.pressedButton == "Settings":
            menu.draw(menuSurf)
            fadeOutMenu(menu.bgImage)
            currentState = settingsState
            menu.reinit()
    elif currentState == settingsState:
        settingsMenu.everyFrame(pressedKeys, mouseEvents)
        settingsMenu.update(time)
        settingsMenu.draw(screen)
            
        # Figure out if the menu was just faded into and if so, fade into the menu.
        if menuSurf.get_alpha() < 255:
            settingsMenu.draw(menuSurf)
            fadeInMenu(settingsMenu.bgImage)
        
        if K_ESCAPE in pressedKeys:
            if fullscreen:
                setWindowedMode()
                fullscreen = False
                settingsMenu.reinit()
            else:
                setFullscreenMode(config.getboolean("Display", 'fullscaling'))
                fullscreen = True
                settingsMenu.reinit()
        
        if settingsMenu.pressedButton == "Back" or K_b in pressedKeys:
            currentState = mainMenuState
            settingsMenu.draw(menuSurf)
            fadeOutMenu(settingsMenu.bgImage)
            settingsMenu.reinit()   
    elif currentState == gameModeSelectState:
        gameModeMenu.everyFrame(pressedKeys, mouseEvents)
        gameModeMenu.update(time)
        gameModeMenu.draw(screen)
        
        # Figure out if the game was just faded into and if so, fade into the menu.
        if menuSurf.get_alpha() < 255:
            gameModeMenu.draw(menuSurf)
            fadeInMenu(gameModeMenu.bgImage)
                
        if gameModeMenu.pressedButton == "Arcade":
            gameModeMenu.draw(menuSurf)
            fadeOutMenu(gameModeMenu.bgImage)
            currentState = charSelectState
            currentState.vars["gamemode"] = "Arcade"
            
            gameModeMenu.reinit()
        elif gameModeMenu.pressedButton == "Story":
            gameModeMenu.draw(menuSurf)
            fadeOutMenu(gameModeMenu.bgImage)
            fadeInMenu(gameModeMenu.bgImage)
            gameModeMenu.reinit()
            print "Not implemented"
        elif gameModeMenu.pressedButton == "Back":
            currentState = mainMenuState
            gameModeMenu.draw(menuSurf)
            fadeOutMenu(gameModeMenu.bgImage)
            gameModeMenu.reinit()        
    elif currentState == charSelectState:
        charSelectMenu.everyFrame(pressedKeys, mouseEvents)
        charSelectMenu.update(time)
        charSelectMenu.draw(screen)
        
        if charSelectMenu.pressedShipButton != None:
            charSelectMenu.buttons[0].hidden = False
        
        # Figure out if the game was just faded into and if so, fade into the menu.
        if menuSurf.get_alpha() <= 0:
            charSelectMenu.draw(menuSurf)
            fadeInMenu(charSelectMenu.bgImage)
        
        if charSelectMenu.pressedButton == "SelectChar":
            if not charSelectMenu.pressedShipButton == None: # Make sure the user has actually selected a ship first
                currentState = gameState
                currentState.vars["Ship"] = charSelectMenu.pressedShipButton[5:]
                if sound:
                    pygame.mixer.music.stop()
                fadeToBlack(screen.copy())
                charSelectMenu.reinit()
            else:
                charSelectMenu.reinit()
        
        elif charSelectMenu.pressedButton == "CharSelectBack":
            currentState = gameModeSelectState
            charSelectMenu.draw(menuSurf)
            fadeOutMenu(charSelectMenu.bgImage)
            charSelectMenu.reinit()        
    elif currentState == pauseState:
        pauseMenu.bgImage = pygame.surface.Surface(screenRect.size)
        pauseMenu.bgImage.set_colorkey((0,0,0))
        screen.blit(currentState.vars['bgSurf'], (0,0))
        
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
            fadeToBlack(screen.copy())
            pauseMenu.reinit()
            
            if sound:
                pygame.mixer.music.stop()
        
    else:
        print "Oops, something went wrong. The current state was assigned to an unhandled instance (%s). Most likely programming error."%currentState.name
        print "Resetting you to the main menu... Sorry for any progress lost."
        currentState = mainMenuState
    
    
    blitDebugInfo(clock.get_fps(), currentState, fullscreen, debugSurf, debugFont, maxfps)
    if debug:
        screen.blit(debugSurf, screenRect.topleft)
    
    pygame.display.update()