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
# Add boss battles
# Make tutorial
# Create levels
#Extras:
# Add remmappable buttons
# Add option for manual firing
# Joystick/pad support?
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

__version__ = "prerelease 5"
__author__ = "J.T. Johnson"
releaseNotes = file("RELEASE NOTES.txt", 'r').readlines()
cfgFilename = "For The New Lunar Republic.cfg" 

import sys, os
import random
import logging

if "-debug" in sys.argv or "-db" in sys.argv:
    debug = True
else:
    debug = False

if not "-silent" in sys.argv:
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
        "windowedresize":0,
        "windowloc_x":-1,
        "windowloc_y":-1
        },
    "Files":{
        "imagesfolder":"images",
        "musicfolder":"music",
        "fontsfolder":"fonts",
        "logfile":"For The New Lunar Republic.log"
        },
    "Sounds":{
        "musicvolume":100,
        "nosound":0
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
       "logginglevel":"DEBUG",
       "consoleloglevel":"WARNING",
       "clearlogonstartup":1,
       "debug":0
    },
    cfgFilename)

if config.getboolean("DEFAULT", "debug"):
    debug = True
    
# This is for logging, so that the loggers for all files can be given handlers.
otherFiles = ["enemies","bullets","ships","menus","states","levels","cutscenes","hubs"]
    
# Deal with logging.
logfilemode = 'a'
if config.getboolean("DEFAULT", "clearlogonstartup") or "-clearlog" in sys.argv:
    # logfilemode = 'w'
    cfgfile = file(config.get("Files", 'logfile'), 'w')
    cfgfile.write("")
    cfgfile.close()
else:
    logfilemode = 'a'

logLevel = config.get("DEFAULT", "logginglevel").upper()
if "-loglevel" in sys.argv:
    logLevel = sys.argv[sys.argv.index("-loglevel")+1].upper()
    
if debug:
    logLevel = "DEBUG"
    

log = logging.getLogger(__name__)
log.setLevel(getattr(logging, logLevel))

# Make a logger for the console
ch = logging.StreamHandler()
ch.setLevel(getattr(logging, config.get("DEFAULT", 'consoleloglevel').upper()))

# Make a logger for a file
fh = logging.FileHandler(config.get("Files", 'logfile'))
fh.setLevel(getattr(logging, logLevel))

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
cformatter = logging.Formatter('|%(levelname)s| |%(name)s|:  %(message)s')
ch.setFormatter(cformatter)
fh.setFormatter(formatter)

log.addHandler(ch)
log.addHandler(fh)

for f in otherFiles:
    fh = logging.FileHandler(config.get("Files", 'logfile'))
    fh.setLevel(getattr(logging, logLevel))
    fh.setFormatter(formatter)
    
    logging.getLogger(f).setLevel(getattr(logging, logLevel))
    
    logging.getLogger(f).addHandler(ch)
    logging.getLogger(f).addHandler(fh)

log.debug("Logging set up.")
# END LOGGING
    
folders = {"images":config.get("Files",'imagesfolder'),
"music":config.get("Files",'musicfolder'),
"fonts":config.get("Files",'fontsfolder')}

log.info("Number of successful initialized pygame modules: %i Unsuccessful ones: %i"%pygame.init()) # Init pygame now so that other files can use it without having to wait

# Import local modules.
try:
    import ships
    import enemies
    import levels
    import states
    import menus
except ImportError, e:
    log.exception("Failed to import local modules: %s"%e)
    raise
log.debug("Imported files")

if sys.platform == 'win32':
    if config.getint("Display", "windowloc_x") == -1 or config.getint("Display", "windowloc_y") == -1:
        os.environ['SDL_VIDEO_CENTERED'] = '1'
    else:
        os.environ['SDL_VIDEO_WINDOW_POS'] = '%i,%i'%(config.getint("Display", "windowloc_x"),config.getint("Display", "windowloc_y"))
    log.debug("Centered window")

screenRect = Rect(0,0, 1000,500)

videoInfo = pygame.display.Info() # Used primarily to get the user's desktop resolution, but for other things too maybe.
log.debug("Video memory available: %i (If it says 0, that means the system didn't tell me)"%videoInfo.video_mem)
log.debug("Initial resolution: (%i,%i)"%(videoInfo.current_w, videoInfo.current_h))

def setWindowedMode():
    log.info("Setting mode to windowed")
    screenRect.topleft = (0,0)
    if "-noframe" in sys.argv or not config.getboolean("Display", 'windowedframe'):
        screen = pygame.display.set_mode(screenRect.size, NOFRAME)
        log.debug("No frame")
    elif "-resizable" in sys.argv or config.getboolean("Display", 'windowedresize'):
        screen = pygame.display.set_mode(screenRect.size, RESIZABLE)
        log.debug("Resizable")
    else:
        screen = pygame.display.set_mode(screenRect.size)
    
    return screen
    
def setFullscreenMode(scaling):
    log.info("Setting mode to fullscreen")
    if not videoInfo.hw:
        log.warning("Hardware acceleration not supported. The game will still work, just maybe slower.")
    if scaling:
        log.info("Scaling turned on")
        screen = pygame.display.set_mode(screenRect.size, FULLSCREEN | HWSURFACE | DOUBLEBUF)
    else:
        screen = pygame.display.set_mode((videoInfo.current_w,videoInfo.current_h), FULLSCREEN | HWSURFACE | DOUBLEBUF)
        screenRect.center = screen.get_rect().center
        #TODO Noscaling is broken.
    
    return screen
    
# Decide how to display the window based on the command line arguments and the config file.
if "-fullscreen" in sys.argv or config.getboolean("Display", 'fullscreen') or not videoInfo.wm:
    if not videoInfo.wm:
        log.warning("Your platform does not support windowed mode.")
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

levels.initModule() # Now that the video mode has been set.

def blitDebugInfo(fps, currentState, fullscreen, surf, font, maxfps, pos=(0,0)):
    surf.fill((0,255,0))
    color = (255,255,255)
    if fps < maxfps: color = (255,100,100)
    
    debugString = "FPS: %i STATE: %s"%(fps, currentState.name)
    
    if "gamemode" in currentState.vars:
        debugString = debugString + " |MODE: %s"%currentState.vars['gamemode']
        
    if "Ship" in currentState.vars:
        debugString = debugString + " |SHIP: %s"%currentState.vars['Ship']
    
    if "level" in currentState.vars:
        debugString = debugString + " |LEVEL: %s"%currentState.vars['Level']
    
    if fullscreen:
        debugString = debugString + " |FULLSCREEN"
    
    surf.blit(font.render(debugString, False, color, (0,0,0)), pos)
debugSurf = pygame.surface.Surface(screenRect.size)
debugSurf.fill((0,255,0))
debugSurf.set_colorkey((0,255,0))
try:
    debugFont = pygame.font.Font(os.path.join(folders['fonts'],config.get("Fonts",'debugfont')), 12)
except IOError, e:
    log.exception("Couldn't load debug font file. Missing file or corrupt config file (Try deleting your .cfg file)")
    sys.exit()
log.debug("Created and prepared debug surface and font.")
    
def renderText(text, font, color, aa=True):
    surf = font.render(text, aa, color)
    return surf, surf.get_rect()
    
if "-nomaxfps" in sys.argv:
    maxfps = 0
    log.info("Maximum FPS is turned off.")
else:
    maxfps = config.getint("Display", "maxfps")
    log.debug("Maximum FPS is %i"%maxfps)

if "-nosound" in sys.argv or config.getboolean("Sounds", "nosound"):
    sound = False
    log.info("Sound is turned off")
else:
    sound = True

invincible = False
if "-invincible" in sys.argv:
    invincible = True
    log.warning("Player is set to be invincible!")

stressTest = False
if "-stresstest" in sys.argv:
    stressTest = True
    debug = True
    ch.setLevel(logging.DEBUG)
    invincible = True
    maxfps = 0
    if "-binterval" in sys.argv:
        STBulletInterval = int(sys.argv[sys.argv.index("-binterval")+1])
    else:
        STBulletInterval = 100
    if "-einterval" in sys.argv:
        STEnemyInterval = int(sys.argv[sys.argv.index("-einterval")+1])
    else:
        STEnemyInterval = 100
    log.warning("Running a stress test. BInt: %i EInt: %i"%(STBulletInterval, STEnemyInterval))
    
#TODO Make the BGs added by levels.
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
log.debug("Initializing menus")
# Menu fonts
try:
    mainHeaderFont = pygame.font.Font(os.path.join(folders['fonts'],config.get("Fonts",'mainheaderfont')), 48)
except IOError, e:
    log.exception("Couldn't load main header font file. Missing file or corrupt config file (Try deleting your .cfg file)")
    sys.exit()

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
log.debug("Main Menu initialized")

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
pauseMenu.makeNewButton("Settings", "Settings", (screenRect.centerx, screenRect.centery+10))
pauseMenu.makeNewButton("MainMenu", "MainMenu", (screenRect.centerx, screenRect.centery+50))
log.debug("Pause Menu initialized")

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
log.debug("Game Mode Select Menu initialized")

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
settingsMenu.makeNewCheckButton("Fullscreen", "Fullscreen", (screenRect.centerx, screenRect.centery-40), fullscreen)
settingsMenu.makeNewCheckButton("Sound", "Sound", (screenRect.centerx, screenRect.centery), sound)
log.debug("Settings Menu initialized")

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
charSelectMenu.makeNewButton("CharSelectBack", "CharSelectBack", (screenRect.centerx, screenRect.bottom-30), 1) #TODO change to back instead of charselectback
xMult = 0
shipNameFont = pygame.font.Font(os.path.join(folders['fonts'],"pf_tempesta_seven.ttf"), 10)
for ship in ships.shipTypes.iterkeys():
    charSelectMenu.makeNewCharSelectButton(ships.shipTypes[ship], (75,47), ship, "Button", pos=(screenRect.left+25+(160*xMult), screenRect.centery-100), shipNameFont=shipNameFont, posOrientation=0)
    xMult += 1
log.debug("Character Select Menu initialized")

# Level select menu next
levelSelectMenu = menus.Menu(screenRect, textInfo={
    "Main":{
        "Text":"Choose a Level",
        "Color":(255,255,255),
        "Loc":(screenRect.centerx, screenRect.top+50),
        "Font":mainHeaderFont
        }
    },
    bgImage=menu.bgImage,
    allowKeys=False)

levelSelectMenu.makeNewButton("SelectLevel", "SelectLevel", (screenRect.centerx, screenRect.bottom-80), 1)
levelSelectMenu.buttons[0].hidden = True
levelSelectMenu.makeNewButton("Back", "Back", (screenRect.centerx, screenRect.bottom-30), 1)
xMult = 0
levelNameFont = pygame.font.Font(os.path.join(folders['fonts'],"pf_tempesta_seven.ttf"), 10)
for level in levels.arcadeLevels:
    levelSelectMenu.makeNewLevelSelectButton(level, level.name, (75,47), "Button", pos=(screenRect.left+25+(160*xMult), screenRect.centery-100), levelNameFont=levelNameFont, posOrientation=0)
    xMult += 1
log.debug("Character Select Menu initialized")
# End initialize menus

# State initialization code
log.debug("Initializing states")
gameState = states.State("Game", {"level":"TestLevel", "gamemode":"Arcade"})
mainMenuState = states.State("MainMenu")
gameModeSelectState = states.State("GameModeSelect")
charSelectState = states.State("CharSelect")
levelSelectState = states.State("LevelSelect")
settingsState = states.State("Settings")
pauseState = states.State("PauseMenu", {"bgSurf":pygame.surface.Surface(screenRect.size)})

currentState = mainMenuState
# End state initialization code  

currentSong = "Luna Deos"
    
pressedKeys = []

fadeSurf = pygame.surface.Surface(screen.get_rect().size) # Used to fade in and out.
fadeSurf.set_alpha(255)
fadeTime = config.getint("Menus", 'fadeouttime') # Time in milliseconds to fade.
fadeInTime = config.getint("Menus", 'fadeintime')
# Make sure the user hasn't set the fade time to some ridiculous amount of time.

clock = pygame.time.Clock()

def fadeFromBlack(origSurf):
    alpha = 255
    curTime = fadeInTime
    while curTime > 0:
        pygame.event.pump()
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
        pygame.event.pump()
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
        pygame.event.pump()
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
        pygame.event.pump()
        screen.blit(origSurf, screenRect.topleft)
        curTime += clock.tick(maxfps)
        alpha = (curTime*1./fadeInTime*1.*100)*255/100 # Convert the percent of time passed to the 255 scale
        menuSurf.set_alpha(alpha)
        screen.blit(menuSurf, (0,0))
        pygame.display.update()
    
done = False

runtime = 0

reInitGame = True # This is to determine if the game needs to be reset once returning from something like the settings menu or the main menu even.

bm = pygame.time.Clock()
while not done:
    time = clock.tick(maxfps)
    runtime += time
    fps = clock.get_fps()
    # if fps < maxfps/2:
        # if fps > 0:
            # log.warning("FPS has dipped below 1/2 of the maximum. Possibly due to the window being moved. (%i/%i)"%(fps,maxfps))
    screen.fill(fillColor)
    
    mouseEvents = []
    
    for e in pygame.event.get():
        if e.type == QUIT:
            runtime += clock.tick()
            log.info("Quitting (QUIT event). Run time: %f seconds."%(runtime/1000.))
            done = True
            
        elif e.type == KEYDOWN:
            pressedKeys.append(e.key)
        elif e.type == KEYUP:
            if e.key in pressedKeys:
                pressedKeys.remove(e.key)
                
        elif e.type == MOUSEBUTTONDOWN:
            mouseEvents.append(e)
            
        elif e.type == ACTIVEEVENT:
            if e.state == 2:
                log.debug("Lost focus")
                if currentState == gameState:
                    currentState = pauseState
                    log.info("STATE CHANGE: %s"%currentState.name)
            
                    if sound:
                        pygame.mixer.music.pause()
            elif e.state == 6:
                log.debug("Gained focus")
                
    
    
    if currentState == gameState:
        # Figure out if the game was just faded into and if so, fade into the game.
        if fadeSurf.get_alpha() > 0:
            fadeFromBlack(screen.copy())
            if reInitGame:
                log.debug("Initializing game state")
                
                #TODO Building level code. Other code in this block is temporary.
                if currentState.vars["gamemode"] == "Arcade":
                    level = levels.ArcadeLevel(currentState.vars["Level"])
                elif currentState.vars["gamemode"] == "Story":
                    level = levels.StoryLevel(currentState.vars["Level"])
                
                ship = ships.shipTypes[currentState.vars['Ship']](center=(75,screenRect.centery), bounds=screenRect, invincible=invincible)                
                level.load(screenRect, ship, folders)
                pygame.mixer.music.set_volume(config.getint("Sounds", 'musicvolume')/100.)
                if sound:
                    pygame.mixer.music.play(-1)
                #TODO           
        
        level.update(pressedKeys, time)
        level.draw(screen)
        if level.done:
            log.info("Level has ended. Returning to level select menu")
            currentState = levelSelectState
            log.info("STATE CHANGE: %s"%currentState.name)
            fadeToBlack(screen.copy())
        
        # if stressTest:
            # log.debug("Bullets: %i|Enemies: %i|FPS: %i"%(len(enemyBulletGroup),len(enemyGroup),fps))
        if level.gameOver:
            log.info("Player 1 has died, returning to main menu")
            currentState = mainMenuState
            log.info("STATE CHANGE: %s"%currentState.name)
            fadeToBlack(screen.copy())
        
        pauseState.vars['bgSurf'] = screen.copy()
        
        if K_ESCAPE in pressedKeys:
            currentState = pauseState
            log.info("STATE CHANGE: %s"%currentState.name)
            currentState.vars['bgSurf'] = screen.copy()
            pressedKeys.remove(K_ESCAPE)
            
            if sound:
                pygame.mixer.music.pause()
    elif currentState == mainMenuState:
        menu.update(pressedKeys, mouseEvents, time)
        menu.draw(screen)
            
        # Figure out if the menu was just faded into and if so, fade into the menu.
        if menuSurf.get_alpha() < 255:
            menu.draw(menuSurf)
            fadeInMenu(menu.bgImage)
        if fadeSurf.get_alpha() > 0:
            pygame.mixer.music.load(os.path.join(folders['music'], currentSong+".wav"))
            pygame.mixer.music.set_volume(config.getint("Sounds", 'musicvolume')/100.)
            if sound:
                pygame.mixer.music.play(-1)
            fadeFromBlack(screen.copy())
                
        if menu.pressedButton == "Play":
            menu.draw(menuSurf)
            fadeOutMenu(menu.bgImage)
            currentState = gameModeSelectState
            log.info("STATE CHANGE: %s"%currentState.name)
            
            menu.reinit()
        elif menu.pressedButton == "Exit":
            pygame.mixer.music.fadeout(fadeTime)
            fadeToBlack(screen.copy())
            runtime += clock.tick()
            log.info("Quitting (Exit button from main menu). Run time: %f seconds."%(runtime/1000.))
            done = True
        elif menu.pressedButton == "Settings":
            menu.draw(menuSurf)
            fadeOutMenu(menu.bgImage)
            currentState = settingsState
            log.info("STATE CHANGE: %s"%currentState.name)
            menu.reinit()
            currentState.vars['lastState'] = mainMenuState
    elif currentState == settingsState:
        settingsMenu.update(pressedKeys, mouseEvents, time)
        settingsMenu.draw(screen)
            
        # Figure out if the menu was just faded into and if so, fade into the menu.
        if menuSurf.get_alpha() < 255:
            settingsMenu.draw(menuSurf)
            fadeInMenu(settingsMenu.bgImage)
            changedSettings = False
        if fadeSurf.get_alpha() > 0:
            fadeFromBlack(screen.copy())
        
        if "Fullscreen" in settingsMenu.checkedButtons:
            if not fullscreen:
                setFullscreenMode(config.getboolean("Display", 'fullscaling'))
                config.set("Display", "fullscreen", "1")
                changedSettings = True
                fullscreen = True
                settingsMenu.reinit()
        else:
            if fullscreen:
                setWindowedMode()
                config.set("Display", "fullscreen", "0")
                changedSettings = True
                fullscreen = False
                settingsMenu.reinit()
        
        if "Sound" in settingsMenu.checkedButtons:
            if not sound:
                sound = True
                changedSettings = True
                pygame.mixer.music.play(-1)
                config.set("Sounds", 'nosound', "0")
        else:
            if sound:
                sound = False
                changedSettings = True
                pygame.mixer.music.fadeout(fadeTime)
                config.set("Sounds", 'nosound', "1")
        
        
        if settingsMenu.pressedButton == "Back":
            if changedSettings:
                config.write(file(cfgFilename, 'w'))
            currentState = currentState.vars['lastState']
            log.info("STATE CHANGE: %s"%currentState.name)
            settingsMenu.draw(menuSurf)
            if currentState == pauseState:
                fadeToBlack(screen.copy())
                reInitGame = False
            else:
                fadeOutMenu(settingsMenu.bgImage)
            settingsMenu.reinit()   
    elif currentState == gameModeSelectState:
        gameModeMenu.update(pressedKeys, mouseEvents, time)
        gameModeMenu.draw(screen)
        
        # Figure out if the game was just faded into and if so, fade into the menu.
        if menuSurf.get_alpha() < 255:
            gameModeMenu.draw(menuSurf)
            fadeInMenu(gameModeMenu.bgImage)
                
        if gameModeMenu.pressedButton == "Arcade":
            log.debug("Arcade button pushed")
            gameModeMenu.draw(menuSurf)
            fadeOutMenu(gameModeMenu.bgImage)
            currentState = charSelectState
            log.info("STATE CHANGE: %s"%currentState.name)
            currentState.vars["gamemode"] = "Arcade"
            
            gameModeMenu.reinit()
        elif gameModeMenu.pressedButton == "Story":
            log.debug("Story button pushed")
            log.warning("Story not implemented.")
            gameModeMenu.draw(menuSurf)
            fadeOutMenu(gameModeMenu.bgImage)
            fadeInMenu(gameModeMenu.bgImage)
            gameModeMenu.reinit()
        elif gameModeMenu.pressedButton == "Back":
            currentState = mainMenuState
            log.info("STATE CHANGE: %s"%currentState.name)
            gameModeMenu.draw(menuSurf)
            fadeOutMenu(gameModeMenu.bgImage)
            gameModeMenu.reinit()        
    elif currentState == charSelectState:
        charSelectMenu.update(pressedKeys, mouseEvents, time)
        charSelectMenu.draw(screen)
        
        if charSelectMenu.pressedShipButton != None:
            charSelectMenu.buttons[0].hidden = False
        
        # Figure out if the game was just faded into and if so, fade into the menu.
        if menuSurf.get_alpha() <= 0:
            charSelectMenu.draw(menuSurf)
            fadeInMenu(charSelectMenu.bgImage)
        
        if charSelectMenu.pressedButton == "SelectChar":
            if not charSelectMenu.pressedShipButton == None: # Make sure the user has actually selected a ship first
                log.info("Player chose %s character"%charSelectMenu.pressedShipButton)
                currentState.vars["Ship"] = charSelectMenu.pressedShipButton[5:]
                currentState = levelSelectState
                log.info("STATE CHANGE: %s"%currentState.name)
                fadeOutMenu(charSelectMenu.bgImage)
                charSelectMenu.reinit()
            else:
                charSelectMenu.reinit()
                log.warning("No character selected. How did this happen? The button should not display until a character is selected.")
        
        elif charSelectMenu.pressedButton == "CharSelectBack":
            currentState = gameModeSelectState
            log.info("STATE CHANGE: %s"%currentState.name)
            charSelectMenu.draw(menuSurf)
            fadeOutMenu(charSelectMenu.bgImage)
            charSelectMenu.reinit()
    elif currentState == levelSelectState:
        levelSelectMenu.update(pressedKeys, mouseEvents, time)
        levelSelectMenu.draw(screen)
        
        if levelSelectMenu.pressedLevelButton != None:
            levelSelectMenu.buttons[0].hidden = False
        
        # Figure out if the game was just faded into and if so, fade into the menu.
        if menuSurf.get_alpha() <= 0:
            levelSelectMenu.draw(menuSurf)
            fadeInMenu(charSelectMenu.bgImage)
        
        if levelSelectMenu.pressedButton == "SelectLevel":
            if not levelSelectMenu.pressedLevelButton == None:
                log.info("Player chose level %s."%levelSelectMenu.pressedLevelButton)
                currentState = gameState
                log.info("STATE CHANGE: %s"%currentState.name)
                currentState.vars["Ship"] = charSelectState.vars["Ship"]
                currentState.vars["Level"] = levelSelectMenu.pressedLevelButton[6:]
                currentLevel = currentState.vars["Level"]
                if sound:
                    pygame.mixer.music.stop()
                fadeToBlack(screen.copy())
                levelSelectMenu.reinit()
                reInitGame = True #TODO This might be moved later.
            else:
                levelSelectMenu.reinit()
                log.warning("No level selected. How did this happen? The button should not display until a level is selected.")
            
        elif levelSelectMenu.pressedButton == "Back":
            currentState = charSelectState
            log.info("STATE CHANGE: %s"%currentState.name)
            levelSelectMenu.draw(menuSurf)
            fadeOutMenu(charSelectMenu.bgImage)
            levelSelectMenu.reinit()
    elif currentState == pauseState:
        if fadeSurf.get_alpha() > 0:
            fadeFromBlack(screen.copy())
        pauseMenu.bgImage = pygame.surface.Surface(screenRect.size)
        pauseMenu.bgImage.set_colorkey((0,0,0))
        screen.blit(currentState.vars['bgSurf'], (0,0))
        
        pauseMenu.update(pressedKeys, mouseEvents, time)
        pauseMenu.draw(screen)
        
        if K_ESCAPE in pressedKeys or pauseMenu.pressedButton == "Resume":
            reInitGame = False # Just to make sure, in case the user went to a settings menu or something.
            currentState = gameState
            log.info("STATE CHANGE: %s"%currentState.name)
            if K_ESCAPE in pressedKeys:
                pressedKeys.remove(K_ESCAPE)
            
            if sound:
                pygame.mixer.music.unpause()
            pauseMenu.reinit()
        elif pauseMenu.pressedButton == "Settings":
            currentState = settingsState
            log.info("STATE CHANGE: %s"%currentState.name)
            fadeToBlack(screen.copy())
            pauseMenu.reinit()
            changedSettings = False
            currentState.vars['lastState'] = pauseState
        elif pauseMenu.pressedButton == "MainMenu":
            currentState = mainMenuState
            log.info("STATE CHANGE: %s"%currentState.name)
            fadeToBlack(screen.copy())
            pauseMenu.reinit()
            
            if sound:
                pygame.mixer.music.stop()
        
    else:
        log.warning("currentState is set to unhandled object (%s). Resetting to main menu state. The game may be unstable now."%currentState)
        currentState = mainMenuState
    
    
    blitDebugInfo(fps, currentState, fullscreen, debugSurf, debugFont, maxfps)
    if debug:
        screen.blit(debugSurf, screenRect.topleft)
    
    pygame.display.update()

log.debug("Ending logging cleanly.")
logging.shutdown()
fh.close() # Close the log file.