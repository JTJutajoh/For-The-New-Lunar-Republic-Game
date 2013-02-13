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
# Give player ship other types of weapons like shotgun and lazer
# Seeking bullets
# Create levels
# Balance
# Powerups
# Add level complete screen
#Technical stuff:
# Fix fullscreen scaling
# Add remmappable buttons
#Extras:
# Joystick/pad support?
# Co-Op Multiplayer?
# Score leaderboards?
#Story Mode:
# Add RPG elements
# Add savegames
# Add All Your Base reference
# Flesh out hubs
# MAKE CONTENT!

__version__ = "prerelease 6"
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
        },
    "Controls":{
        "manualfiring":0,
        "upkey":K_w,
        "rightkey":K_d,
        "downkey":K_s,
        "leftkey":K_a,
        "firekey":K_SPACE
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
    import bosses
    import levels
    import states
    import menus
    import hud
    import cutscenes
    import story
    import dialog
    import shiphub as shipHubModule
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

# screenRect = Rect(0,0, 1000,500)
screenRect = Rect(0,0, 1280,720)

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
    
    return screen

# Decide how to display the window based on the command line arguments and the config file.
if "-fullscreen" in sys.argv or config.getboolean("Display", 'fullscreen') or not videoInfo.wm:
    if not videoInfo.wm:
        log.warning("Your platform does not support windowed mode.")
    if not config.getboolean("Display", 'fullscaling') or "-noscale" in sys.argv:
        screen = setFullscreenMode(scaling=False)
        scaling = False
    else:
        screen = setFullscreenMode(scaling=True)
        scaling = True
    fullscreen = True
else:
    screen = setWindowedMode()
    fullscreen = False
fillColor = (config.getint("Display", 'fillcolor_r'),config.getint("Display", 'fillcolor_g'),config.getint("Display", 'fillcolor_b'))
screen.fill(fillColor)

# pygame.display.set_icon(pygame.image.load(os.path.join(folders['images'], "icon.ico")).convert())
pygame.display.set_caption("For The New Lunar Republic")

levels.initModule() # Now that the video mode has been set.

def blitDebugInfo(fps, currentState, subState, fullscreen, surf, font, maxfps, pos=(0,0)):
    surf.fill((0,0,0,0))
    color = (255,255,255)
    if fps < maxfps: color = (255,100,100)
    
    if not currentState == None:
        debugString = "FPS: %i STATE: %s"%(fps, currentState.name)
        
        if "gamemode" in currentState.vars:
            debugString = debugString + " |MODE: %s"%currentState.vars['gamemode']
            
        if "Ship" in currentState.vars:
            debugString = debugString + " |SHIP: %s"%currentState.vars['Ship']
        
        if "Level" in currentState.vars:
            debugString = debugString + " |LEVEL: %s"%currentState.vars['Level']
            
        if not subState.name == None:
            debugString = debugString + " |SUBSTATE: %s"%subState.name
    else:
        debugString = "FPS: %i |FADING"%fps
        
    if fullscreen:
        debugString = debugString + " |FULLSCREEN"
    
    textSurf = font.render(debugString, False, color, (0,0,0,150))
    textSurf.set_alpha(150)
    surf.blit(textSurf, pos)
debugSurf = pygame.surface.Surface(screenRect.size, SRCALPHA)
debugSurf.fill((0,0,0))
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
    
if "-story-enable" in sys.argv:
    storyEnabled = True
    log.info("Story mode enabled")
else:
    storyEnabled = False
    log.info("Story mode is disabled in this version.")

# Initialize menus
log.debug("Initializing menus")
# Menu fonts
try:
    mainHeaderFont = pygame.font.Font(os.path.join(folders['fonts'],config.get("Fonts",'mainheaderfont')), 48)
except IOError, e:
    log.exception("Couldn't load main header font file. Missing file or corrupt config file (Try deleting your .cfg file)")
    sys.exit()

menuSurf = pygame.surface.Surface(screen.get_rect().size, HWSURFACE)
menuSurf.set_colorkey((0,0,255))
menuSurf.fill((0,0,255))
menuSurf.set_alpha(255)
menuList = []
# Main menu first
menu = menus.Menu(screenRect, textInfo={
    "Main":{
        "Text":"For The New Lunar Republic",
        "Color":(255,255,255),
        "Loc":(screenRect.width/2,50),
        "Font":mainHeaderFont
        },
    "Sub":{
        "Text":"Version %s by %s"%(__version__, __author__),
        "Color":(255,255,255),
        "Loc":(screenRect.width/2,100),
        "Font":pygame.font.Font(os.path.join(folders['fonts'],"VGAFIX.FON"), 8)
        }
    },
    # bgImage=pygame.image.load(os.path.join(folders['images'], "MenuBGNewLegal720p.png")).convert(),
    bgImage=pygame.image.load(os.path.join(folders['images'], config.get("Display", 'menubgimage'))).convert(),
    allowKeys=False)

menu.makeNewButton("Story", "Story", (screenRect.width/2-75, screenRect.height/2-30))
menu.makeNewButton("Arcade", "Arcade", (screenRect.width/2+75, screenRect.height/2-30))
# menu.makeNewButton("Play", "Play", (screenRect.width/2, screenRect.height/2-30))
menu.makeNewButton("Settings", "Settings", (screenRect.width/2, screenRect.height/2+10))
menu.makeNewButton("Exit", "Exit", (screenRect.width/2, screenRect.height/2+50))
log.debug("Main Menu initialized")
menuList.append(menu)

# Pause menu next
pauseMenu = menus.Menu(screenRect, textInfo={
    "Main":{
        "Text":"Paused",
        "Color":(255,255,255),
        "Loc":(screenRect.width/2, 50),
        "Font":mainHeaderFont
        }
    },
    bgImage=screen.copy(),
    allowKeys=False)

pauseMenu.makeNewButton("Resume", "Resume", (screenRect.width/2, screenRect.height/2-30))
pauseMenu.makeNewButton("Settings", "Settings", (screenRect.width/2, screenRect.height/2+10))
pauseMenu.makeNewButton("MainMenu", "MainMenu", (screenRect.width/2, screenRect.height/2+50))
log.debug("Pause Menu initialized")
menuList.append(pauseMenu)

# Settings Menu
settingsMenu = menus.Menu(screenRect, textInfo={
    "Main":{
        "Text":"Settings",
        "Color":(255,255,255),
        "Loc":(screenRect.width/2, 50),
        "Font":mainHeaderFont
        }
    },
    bgImage=menu.bgImage,
    allowKeys=False)

settingsMenu.makeNewButton("Back", "Back", (screenRect.width/2, screenRect.height/2+100))
settingsMenu.makeNewCheckButton("Fullscreen", "Fullscreen", (screenRect.width/2, screenRect.height/2-40), fullscreen)
settingsMenu.makeNewCheckButton("Sound", "Sound", (screenRect.width/2, screenRect.height/2), sound)
settingsMenu.makeNewCheckButton("ManualFiring", "ManualFiring", (screenRect.width/2, screenRect.height/2+40), config.getboolean("Controls","manualfiring"))
log.debug("Settings Menu initialized")
menuList.append(settingsMenu)

# The arcade settings menu next
arcadeSettingsMenu = menus.Menu(screenRect, textInfo={
    "Main":{
        "Text":"Arcade Mode",
        "Color":(255,255,255),
        "Loc":(screenRect.width/2, 50),
        "Font":mainHeaderFont
        },
    "Ship":{
        "Text":"CHARACTER",
        "Color":(255,255,255),
        "Loc":(screenRect.width/2-100,125),
        "Font":pygame.font.Font(os.path.join(folders['fonts'],"VGAFIX.FON"), 8)
        },
    "Level":{
        "Text":"LEVEL",
        "Color":(255,255,255),
        "Loc":(screenRect.width/2+100,125),
        "Font":pygame.font.Font(os.path.join(folders['fonts'],"VGAFIX.FON"), 8)
        },
    "Sub":{
        "Text":"Choose your Character and Level",
        "Color":(255,255,255),
        "Loc":(screenRect.width/2,100),
        "Font":pygame.font.Font(os.path.join(folders['fonts'],"VGAFIX.FON"), 8)
        }
    },
    bgImage=menu.bgImage,
    allowKeys=False)
shipNameFont = pygame.font.Font(os.path.join(folders['fonts'],"pf_tempesta_seven.ttf"), 10)
levelNameFont = pygame.font.Font(os.path.join(folders['fonts'],"pf_tempesta_seven.ttf"), 10)
arcadeSettingsMenu.makeNewCharSelectButton(ships.shipTypes["RainbowDash"], (75,47), "ShipSelectMenuButton", "Button", (screenRect.width/2-100, screenRect.height/2), shipNameFont, 1, False)
initialLevel = levels.arcadeLevels[0]
arcadeSettingsMenu.makeNewLevelSelectButton(initialLevel, "LevelSelectMenuButton", (75,47), "Button", (screenRect.width/2+100, screenRect.height/2), levelNameFont, 1, False)
arcadeSettingsMenu.makeNewButton("Back", "Back", (screenRect.width/2-100, screenRect.height-75), 1)
arcadeSettingsMenu.makeNewButton("Play", "Play", (screenRect.width/2+100, screenRect.height-75), 1)
menuList.append(arcadeSettingsMenu)

# Character select menu next
charSelectMenu = menus.Menu(screenRect, textInfo={
    "Main":{
        "Text":"Choose a Character",
        "Color":(255,255,255),
        "Loc":(screenRect.width/2, 50),
        "Font":mainHeaderFont
        }
    },
    bgImage=menu.bgImage,
    allowKeys=False)

charSelectMenu.makeNewButton("CharSelectBack", "CharSelectBack", (screenRect.width/2, screenRect.height-30), 1) #TODO change to back instead of charselectback
xMult = 0
for ship in ships.shipTypes.iterkeys():
    charSelectMenu.makeNewCharSelectButton(ships.shipTypes[ship], (75,47), ship, "Button", pos=(75+(150*xMult), screenRect.height/2-25), shipNameFont=shipNameFont, posOrientation=0)
    xMult += 1
log.debug("Character Select Menu initialized")
menuList.append(charSelectMenu)

# Level select menu next
levelSelectMenu = menus.Menu(screenRect, textInfo={
    "Main":{
        "Text":"Choose a Level",
        "Color":(255,255,255),
        "Loc":(screenRect.width/2, 50),
        "Font":mainHeaderFont
        }
    },
    bgImage=menu.bgImage,
    allowKeys=False)

levelSelectMenu.makeNewButton("Back", "Back", (screenRect.width/2, screenRect.height-30), 1)
xMult = 0
for level in levels.arcadeLevels:
    levelSelectMenu.makeNewLevelSelectButton(level, level.name, (75,47), "Button", pos=(75+(150*xMult), screenRect.height/2-25), levelNameFont=levelNameFont, posOrientation=0)
    xMult += 1
log.debug("Level Select Menu initialized")
menuList.append(levelSelectMenu)

# Story menu for selecting things like new game, save game, etc.
storyMenu = menus.Menu(screenRect, textInfo={ #TODO Maybe remove this from this screen.
    "Main":{
        "Text":"Story Mode",
        "Color":(255,255,255),
        "Loc":(screenRect.width/2, -150),
        "Font":mainHeaderFont
        }
    },
    bgImage=menu.bgImage,
    allowKeys=False)

storyMenu.makeNewButton("New Game", "New Game", (screenRect.width/2, screenRect.height/2-30))
storyMenu.makeNewButton("Back", "Back", (screenRect.width/2, screenRect.height/2+10))
menuList.append(storyMenu)

# Game Over Menu
gameOverMenu = menus.Menu(screenRect, textInfo={
    "Main":{
        "Text":"GAME OVER",
        "Color":(255,255,255),
        "Loc":(screenRect.width/2, 150),
        "Font":mainHeaderFont
        }
    },
    bgImage=menu.bgImage,
    allowKeys=False)
#TODO Flesh this out.
gameOverMenu.makeNewButton("Back", "Back", (screenRect.width/2, screenRect.height/2+25))
menuList.append(gameOverMenu)

errorMessageMenu = menus.Menu(screenRect, textInfo={
    "Main":{
        "Text":"ERROR",
        "Color":(255,255,255),
        "Loc":(screenRect.width/2, screenRect.height/2-150),
        "Font":mainHeaderFont
        },
    "Sub":{
        "Text":"An Error Occurred",
        "Color":(255,255,255),
        "Loc":(screenRect.width/2,screenRect.height/2-50),
        "Font":pygame.font.Font(os.path.join(folders['fonts'],"VGAFIX.FON"), 8)
        },
    "Message":{
        "Text":"Unknown error",
        "Color":(255,255,255),
        "Loc":(screenRect.width/2,screenRect.height/2-35),
        "Font":pygame.font.Font(os.path.join(folders['fonts'],"VGAFIX.FON"), 8)
        }
    },
    bgImage=menu.bgImage,
    allowKeys=False)

errorMessageMenu.makeNewButton("Back", "Back", (screenRect.width/2, screenRect.height/2))
errorMessageMenu.buttons[0].hidden = True
errorMessageMenu.makeNewButton("MainMenu", "MainMenu", (screenRect.width/2, screenRect.height/2+40))
errorMessageMenu.buttons[1].hidden = True
errorMessageMenu.makeNewButton("Exit", "Exit", (screenRect.width/2, screenRect.height/2+80))
errorMessageMenu.buttons[2].hidden = True
menuList.append(errorMessageMenu)
# End initialize menus

# State initialization code
log.debug("Initializing states")
gameState = states.State("Game", {"Level":"Test Level", "Ship":"RainbowDash", "gamemode":"Arcade"})
cutsceneState = states.State("Cutscene", {"cutsceneName":"OpeningCutscene"})
mainMenuState = states.State("MainMenu")
arcadeSettingsState = states.State("ArcadeSettings")
charSelectState = states.State("CharSelect")
levelSelectState = states.State("LevelSelect")
storyMenuState = states.State("StoryMenu")
settingsState = states.State("Settings")
pauseState = states.State("PauseMenu", {"bgSurf":pygame.surface.Surface(screenRect.size)})
gameOverState = states.State("GameOver", {"score":0})
errorMessageState = states.State("ErrorMessage", {"Message":"Unknown Error", "lastState":None, "lastStateIsMenu":True, "errorLevel":0}) # errorLevel determines what buttons to show.

currentState = mainMenuState

subState = states.SubState()
if "-instant-arcade" in sys.argv:
    currentState = gameState
    subState.name = "level"
# End state initialization code

# Initialize the story objects
story = story.Story("Alpha Testing", pygame.font.Font(os.path.join(folders['fonts'],"pf_tempesta_seven.TTF"), 12), screenRect, config.getint("Sounds", 'musicvolume')/100., pygame.font.Font(os.path.join("fonts","pf_tempesta_seven.ttf"), 10), sound)
# End story initialization



# TODO PLACEHOLDER


shipHub = shipHubModule.ShipHub(screenRect)


# TODO PLACEHOLDER



controls = {"upkey":config.getint("Controls",'upkey'),
"downkey":config.getint("Controls",'downkey'),
"rightkey":config.getint("Controls",'rightkey'),
"leftkey":config.getint("Controls",'leftkey'),
"fire":config.getint("Controls",'firekey')
}

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
        screen.blit(fadeSurf, screenRect.topleft)
        blitDebugInfo(fps, None, None, fullscreen, debugSurf, debugFont, maxfps)
        if debug:
            screen.blit(debugSurf, screenRect.topleft)
        pygame.display.update(screenRect)

def fadeToBlack(origSurf):
    alpha = 0
    curTime = 0
    while curTime < fadeTime:
        pygame.event.pump()
        screen.blit(origSurf, (0,0))
        curTime += clock.tick(maxfps)
        alpha = (curTime*1./fadeTime*1.*100)*255/100 # Convert the percent of time passed to the 255 scale
        fadeSurf.set_alpha(alpha)
        screen.blit(fadeSurf, screenRect.topleft)
        blitDebugInfo(fps, None, None, fullscreen, debugSurf, debugFont, maxfps)
        if debug:
            screen.blit(debugSurf, screenRect.topleft)
        pygame.display.update(screenRect)

def fadeOutMenu(origSurf):
    alpha = 255
    curTime = fadeTime
    origSurfRect = origSurf.get_rect()
    origSurfRect.center = screenRect.center
    while curTime > 0:
        pygame.event.pump()
        screen.blit(origSurf, origSurfRect.topleft)
        curTime -= clock.tick(maxfps)
        alpha = (curTime*1./fadeTime*1.*100)*255/100 # Convert the percent of time passed to the 255 scale
        menuSurf.set_alpha(alpha)
        screen.blit(menuSurf, (0,0))
        blitDebugInfo(fps, None, None, fullscreen, debugSurf, debugFont, maxfps)
        if debug:
            screen.blit(debugSurf, screenRect.topleft)
        pygame.display.update(screenRect)
        
def fadeInMenu(origSurf):
    alpha = 0
    curTime = 0
    origSurfRect = origSurf.get_rect()
    origSurfRect.center = screenRect.center
    while curTime < fadeInTime:
        pygame.event.pump()
        screen.blit(origSurf, origSurfRect.topleft)
        curTime += clock.tick(maxfps)
        alpha = (curTime*1./fadeInTime*1.*100)*255/100 # Convert the percent of time passed to the 255 scale
        menuSurf.set_alpha(alpha)
        screen.blit(menuSurf, (0,0))
        blitDebugInfo(fps, None, None, fullscreen, debugSurf, debugFont, maxfps)
        if debug:
            screen.blit(debugSurf, screenRect.topleft)
        pygame.display.update(screenRect)
    
done = False

runtime = 0

reInitGame = True # This is to determine if the game needs to be reset once returning from something like the settings menu or the main menu even.

pygame.mouse.set_visible(False)

bm = pygame.time.Clock()
log.info("Starting mainloop.")
while not done:
    time = clock.tick(maxfps)
    runtime += time
    fps = clock.get_fps()
    if fps < maxfps/2:
        if fps > 0:
            log.info("FPS has dipped below 1/2 of the maximum. Possibly due to the window being moved. (%i/%i)"%(fps,maxfps))
    screen.fill(fillColor)
    
    mouseEvents = []
    keyEvents = []
    
    for e in pygame.event.get():
        if e.type == QUIT:
            runtime += clock.tick()
            log.info("Quitting (QUIT event). Run time: %f seconds."%(runtime/1000.))
            done = True
            
        elif e.type == KEYDOWN:
            keyEvents.append(e)
            pressedKeys.append(e.key)
        elif e.type == KEYUP:
            keyEvents.append(e)
            if e.key in pressedKeys:
                pressedKeys.remove(e.key)
                
        elif e.type == MOUSEBUTTONDOWN:
            mouseEvents.append(e)
            
        elif e.type == ACTIVEEVENT:
            if e.state == 2:
                log.debug("Lost focus")
                if currentState == gameState and subState.name == "level":
                    currentState = pauseState
                    log.info("STATE CHANGE: %s"%currentState.name)
            
                    if sound:
                        pygame.mixer.music.pause()
            elif e.state == 6:
                log.debug("Gained focus")
    
    if currentState is gameState:
        # Figure out if the game was just faded into and if so, fade into the game.
        if fadeSurf.get_alpha() > 0:
            fadeFromBlack(screen.copy())
            if subState.name == "level":
                if reInitGame:
                    log.debug("Initializing game state")
                    
                    if currentState.vars["gamemode"] == "Arcade":
                        level = levels.ArcadeLevel(currentState.vars["Level"])
                    elif currentState.vars["gamemode"] == "Story":
                        level = levels.StoryLevel(currentState.vars["Level"])
                    center = (75,screenRect.centery)
                    boundingRect = Rect(screenRect.left,screenRect.top, screenRect.width,screenRect.height-20)
                    ship = ships.shipTypes[currentState.vars['Ship']](center, boundingRect, level, controls, config.getboolean("Controls", 'manualfiring'), [], invincible)                
                    level.load(boundingRect, ship, folders, pygame.font.Font(os.path.join(folders['fonts'],"BEBAS.TTF"), 48))
                    
                    hudFonts = {
                        'hp':pygame.font.Font(os.path.join(folders['fonts'],"pf_tempesta_seven.TTF"), 8),
                        'bosshp':pygame.font.Font(os.path.join(folders['fonts'],"pf_tempesta_seven.TTF"), 14)
                    }
                    
                    hudRect = Rect(0,screenRect.height-20, screenRect.width,20)
                    levelhud = hud.HUD(hudRect, screenRect, level, hudFonts)
                    levelhud.load()
                    pygame.mixer.music.set_volume(config.getint("Sounds", 'musicvolume')/100.)
                    if sound:
                        pygame.mixer.music.play(-1)
                else:
                    level = None
            # elif subState.name == "cutscene":
                # pygame.mouse.set_visible(False)
                # fadeFromBlack(screen.copy())
                
                # cutscene = cutscenes.Cutscene(story, currentState.vars["cutsceneName"], config.getint("Sounds", 'musicvolume')/100., screenRect, pygame.font.Font(os.path.join("fonts","pf_tempesta_seven.ttf"), 10), sound)
                # cutscene.load()
                # log.info("Starting cutscene \"%s\"..."%currentState.vars["cutsceneName"])
        
        if gameState.vars['gamemode'] == "Story":
            story.update(time, keyEvents, mouseEvents, subState, currentState, level)
            story.draw(screen)
        
        if subState.name == "level":
            pygame.mouse.set_visible(False)
            level.update(pressedKeys, time)
            level.draw(screen)
            
            levelhud.update(time)
            levelhud.draw(screen)
            
            if level.done:
                if gameState.vars['gamemode'] == "Arcade":
                    currentState = arcadeSettingsState
                else:
                    currentState = mainMenuState
                reInitGame = True
                log.info("STATE CHANGE: %s"%currentState.name)
                fadeToBlack(screen.copy())
                pygame.mixer.stop()
                # pygame.mixer.music.load(os.path.join(folders['music'], currentSong+".wav"))
                # pygame.mixer.music.set_volume(config.getint("Sounds", 'musicvolume')/100.)
                # if sound:
                    # pygame.mixer.music.play(-1)
                    
            if level.gameOver:
                log.info("Game Over.")
                currentState = gameOverState
                if gameState.vars['gamemode'] == "Arcade":
                    currentState.vars['score'] = 9001
                else:
                    currentState.vars['score'] = None
                log.info("STATE CHANGE: %s"%currentState.name)
                fadeToBlack(screen.copy())
                
            if K_ESCAPE in pressedKeys:
                currentState = pauseState
                log.info("STATE CHANGE: %s"%currentState.name)
                currentState.vars['bgSurf'] = screen.copy()
                pressedKeys.remove(K_ESCAPE)
                
                if sound:
                    pygame.mixer.music.pause()
        
        elif subState.name == "ship":
            pygame.mouse.set_visible(True)
            
            shipHub.update(time, keyEvents, mouseEvents)
            shipHub.draw(screen)
        
        elif subState.name == "dialog":
            pygame.mouse.set_visible(False)
            if story.needsToFade:
                fadeToBlack(screen.copy())
                story.needsToFade = False
                subState.name = "ship"
            
        
        # if gameState.vars['gamemode'] == "Story":
            # story.draw(screen)
        elif subState.name == "cutscene":
            pygame.mouse.set_visible(False)
            if story.needsToFade:
                fadeToBlack(screen.copy())
                story.needsToFade = False
            # cutscene.update(time, keyEvents)
            # cutscene.draw(screen)
            
            # if cutscene.done:
                # fadeToBlack(screen.copy())
    # elif currentState is cutsceneState:
        
    elif currentState is gameOverState:
        gameOverMenu.update(pressedKeys, mouseEvents, time)
        gameOverMenu.draw(screen)
        
        if fadeSurf.get_alpha() > 0:
            fadeFromBlack(screen.copy())
            pygame.mouse.set_visible(True)
            pygame.mixer.music.stop()
            
        if gameOverMenu.pressedButton == "Back":
            currentState = mainMenuState #TODO make this more flexible
            log.info("STATE CHANGE: %s"%currentState.name)
            gameOverMenu.draw(menuSurf)
            fadeOutMenu(gameOverMenu.bgImage)
            gameOverMenu.reinit()
    elif currentState is mainMenuState:
        menu.update(pressedKeys, mouseEvents, time)
        menu.draw(screen)
            
        # Figure out if the menu was just faded into and if so, fade into the menu.
        if menuSurf.get_alpha() < 255:
            menu.draw(menuSurf)
            fadeInMenu(menu.bgImage)
        if fadeSurf.get_alpha() > 0:
            pygame.mixer.music.load(os.path.join(folders['music'], currentSong+".mp3"))
            pygame.mixer.music.set_volume(config.getint("Sounds", 'musicvolume')/100.)
            if sound:
                pygame.mixer.music.play(-1)
            fadeFromBlack(screen.copy())
            pygame.mouse.set_visible(True)
                
        if menu.pressedButton == "Arcade":
            log.debug("Arcade button pushed")
            menu.draw(menuSurf)
            fadeOutMenu(menu.bgImage)
            # currentState = charSelectState
            currentState = arcadeSettingsState
            log.info("STATE CHANGE: %s"%currentState.name)
            currentState.vars["gamemode"] = "Arcade"
            
            menu.reinit()
        elif menu.pressedButton == "Story":
            log.debug("Story button pushed")
            if not storyEnabled:
                log.warning("Story not implemented.")
                menu.draw(menuSurf)
                fadeOutMenu(menu.bgImage)
                # fadeInMenu(gameModeMenu.bgImage)
                currentState = errorMessageState
                currentState.vars['Message'] = "Story mode not implemented yet. Sorry!"
                currentState.vars['errorLevel'] = 0
                currentState.vars['lastState'] = mainMenuState
                currentState.vars['lastStateIsMenu'] = True
                menu.reinit()
            else:
                log.warning("Beginning story mode. From now on the game WILL be buggy and glitchy.")
                menu.draw(menuSurf)
                fadeOutMenu(menu.bgImage)
                currentState = storyMenuState
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
    elif currentState is settingsState:
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
                for m in menuList:
                    m.resetRects(screenRect)
                config.set("Display", "fullscreen", "1")
                changedSettings = True
                fullscreen = True
                menuSurf = pygame.surface.Surface(screen.get_rect().size, HWSURFACE)
                menuSurf.set_colorkey((0,0,255))
                menuSurf.fill((0,0,255))
                menuSurf.set_alpha(255)
                settingsMenu.reinit()
        else:
            if fullscreen:
                setWindowedMode()
                for m in menuList:
                    m.resetRects(screenRect)
                config.set("Display", "fullscreen", "0")
                changedSettings = True
                fullscreen = False
                menuSurf = pygame.surface.Surface(screen.get_rect().size, HWSURFACE)
                menuSurf.set_colorkey((0,0,255))
                menuSurf.fill((0,0,255))
                menuSurf.set_alpha(255)
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
                
        if "ManualFiring" in settingsMenu.checkedButtons:
            if not config.getboolean("Controls", 'manualfiring'):
                config.set("Controls", 'manualfiring', "1")
                changedSettings = True
                if currentState.vars['lastState'] == pauseState: # If we're going to return to the game after this.
                    level.ship.manualFiring = True
        else:
            if config.getboolean("Controls", 'manualfiring'):
                config.set("Controls", 'manualfiring', "0")
                changedSettings = True
                if currentState.vars['lastState'] == pauseState: # If we're going to return to the game after this.
                    level.ship.manualFiring = False
                
        
        
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
    elif currentState is storyMenuState:
        storyMenu.update(pressedKeys, mouseEvents, time)
        storyMenu.draw(screen)
        
        if menuSurf.get_alpha() < 255:
            storyMenu.draw(menuSurf)
            fadeInMenu(storyMenu.bgImage)
        if fadeSurf.get_alpha() > 0:
            currentSong = "Luna Deos"
            if fadeSurf.get_alpha() > 0:
                pygame.mixer.music.load(os.path.join(folders['music'], currentSong+".mp3"))
                pygame.mixer.music.set_volume(config.getint("Sounds", 'musicvolume')/100.)
                if sound:
                    pygame.mixer.music.play(-1)
                fadeFromBlack(screen.copy())
            pygame.mouse.set_visible(True)
                
        if storyMenu.pressedButton == "Back":
            currentState = mainMenuState
            log.info("STATE CHANGE: %s"%currentState.name)
            storyMenu.draw(menuSurf)
            fadeOutMenu(storyMenu.bgImage)
            storyMenu.reinit()
        elif storyMenu.pressedButton == "New Game":
            # currentState = cutsceneState
            gameState.vars['gamemode'] = "Story"
            currentState = gameState
            log.info("STATE CHANGE: %s"%currentState.name)
            storyMenu.draw(menuSurf)
            fadeToBlack(screen.copy())
            storyMenu.reinit()
            currentState.vars["cutsceneName"] = "Opening Cutscene"
            pygame.mixer.music.stop()
            subState.name = "cutscene"
    elif currentState is arcadeSettingsState:
        arcadeSettingsMenu.update(pressedKeys, mouseEvents, time)
        arcadeSettingsMenu.draw(screen)
        
        if "Ship" in currentState.vars.keys():
            arcadeSettingsMenu.shipButtons[0].setShip(ships.shipTypes[currentState.vars["Ship"]])
        else:
            for shipType in ships.shipTypes.iteritems():
                if type(arcadeSettingsMenu.shipButtons[0].ship) is shipType[1]:
                    name = shipType[0]
            currentState.vars["Ship"] = name
        if "Level" in currentState.vars.keys():
            for l in levels.arcadeLevels:
                if l.name == currentState.vars["Level"]:
                    arcadeSettingsMenu.levelButtons[0].setLevel(l)
        else:
            currentState.vars["Level"] = arcadeSettingsMenu.levelButtons[0].level.name
            
        if menuSurf.get_alpha() < 255:
            arcadeSettingsMenu.draw(menuSurf)
            fadeInMenu(arcadeSettingsMenu.bgImage)
        if fadeSurf.get_alpha() > 0:
            currentSong = "Luna Deos"
            if fadeSurf.get_alpha() > 0:
                pygame.mixer.music.load(os.path.join(folders['music'], currentSong+".mp3"))
                pygame.mixer.music.set_volume(config.getint("Sounds", 'musicvolume')/100.)
                if sound:
                    pygame.mixer.music.play(-1)
                fadeFromBlack(screen.copy())
            pygame.mouse.set_visible(True)
        
        if arcadeSettingsMenu.pressedButton == "SHIP_ShipSelectMenuButton":
            arcadeSettingsMenu.draw(menuSurf)
            fadeOutMenu(arcadeSettingsMenu.bgImage)
            currentState = charSelectState
            for shipType in ships.shipTypes.iteritems():
                if type(arcadeSettingsMenu.shipButtons[0].ship) is shipType[1]:
                    name = shipType[0]
            currentState.vars["Ship"] = name
            log.info("STATE CHANGE: %s"%currentState.name)
            
            arcadeSettingsMenu.reinit()
        elif arcadeSettingsMenu.pressedButton == "LEVEL_LevelSelectMenuButton":
            arcadeSettingsMenu.draw(menuSurf)
            fadeOutMenu(arcadeSettingsMenu.bgImage)
            currentState = levelSelectState
            currentState.vars["Level"] = arcadeSettingsMenu.levelButtons[0].level.name
            log.info("STATE CHANGE: %s"%currentState.name)
            
            arcadeSettingsMenu.reinit()
        elif arcadeSettingsMenu.pressedButton == "Back":
            currentState = mainMenuState
            log.info("STATE CHANGE: %s"%currentState.name)
            arcadeSettingsMenu.draw(menuSurf)
            fadeOutMenu(arcadeSettingsMenu.bgImage)
            arcadeSettingsMenu.reinit()
        elif arcadeSettingsMenu.pressedButton == "Play":
            currentState = gameState
            log.info("STATE CHANGE: %s"%currentState.name)
            currentState.vars["Ship"] = arcadeSettingsState.vars["Ship"]
            currentState.vars["Level"] = arcadeSettingsState.vars["Level"]
            subState.name = "level"
            currentLevel = currentState.vars["Level"]
            if sound:
                pygame.mixer.music.stop()
            fadeToBlack(screen.copy())
            arcadeSettingsMenu.reinit()
            reInitGame = True #TODO This might be moved later.
    elif currentState is charSelectState:
        charSelectMenu.update(pressedKeys, mouseEvents, time)
        charSelectMenu.draw(screen)
        
        # Figure out if the game was just faded into and if so, fade into the menu.
        if menuSurf.get_alpha() <= 0:
            if "Ship" in currentState.vars.keys():
                charSelectMenu.pressedShipButton = "SHIP_"+currentState.vars["Ship"]
                
            charSelectMenu.draw(menuSurf)
            fadeInMenu(charSelectMenu.bgImage)
        
        if charSelectMenu.pressedButton == "CharSelectBack":
            currentState = arcadeSettingsState
            currentState.vars["Ship"] = charSelectMenu.pressedShipButton[5:]
            log.info("STATE CHANGE: %s"%currentState.name)
            charSelectMenu.draw(menuSurf)
            fadeOutMenu(charSelectMenu.bgImage)
            charSelectMenu.reinit()
    elif currentState is levelSelectState:
        levelSelectMenu.update(pressedKeys, mouseEvents, time)
        levelSelectMenu.draw(screen)
        
        # Figure out if the game was just faded into and if so, fade into the menu.
        if menuSurf.get_alpha() <= 0:
            if "Level" in currentState.vars.keys():
                levelSelectMenu.pressedLevelButton = "LEVEL_"+currentState.vars["Level"]
                
            levelSelectMenu.draw(menuSurf)
            fadeInMenu(charSelectMenu.bgImage)
            
        if levelSelectMenu.pressedButton == "Back":
            log.info("Player chose level %s."%levelSelectMenu.pressedLevelButton)
            currentState = arcadeSettingsState
            currentState.vars["Level"] = levelSelectMenu.pressedLevelButton[6:]
            log.info("STATE CHANGE: %s"%currentState.name)
            levelSelectMenu.draw(menuSurf)
            fadeOutMenu(charSelectMenu.bgImage)
            levelSelectMenu.reinit()
    elif currentState is pauseState:
        pygame.mouse.set_visible(True)
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
    elif currentState is errorMessageState:
        initMenu = False
        if menuSurf.get_alpha() < 255 or fadeSurf.get_alpha() > 0:
            pygame.mouse.set_visible(True)
            initMenu = True
            
        if initMenu:
            errorMessageMenu.textInfo["Message"]["Text"] = currentState.vars['Message']
            errorLevel = currentState.vars["errorLevel"]
            if errorLevel == 0:
                for button in errorMessageMenu.buttons:
                    button.hidden = False
                errorMessageMenu.buttons[0].setPos((screenRect.centerx, screenRect.centery), 1)
                errorMessageMenu.buttons[1].setPos((screenRect.centerx, screenRect.centery+40), 1)
                errorMessageMenu.buttons[2].setPos((screenRect.centerx, screenRect.centery+80), 1)
            elif errorLevel == 1:
                errorMessageMenu.textInfo["Message"]["Text"] = "Serious Error: "+errorMessageMenu.textInfo["Message"]["Text"]
                for button in errorMessageMenu.buttons[1:]:
                    button.hidden = False
                errorMessageMenu.buttons[1].setPos((screenRect.centerx, screenRect.centery), 1)
                errorMessageMenu.buttons[2].setPos((screenRect.centerx, screenRect.centery+40), 1)
            elif errorLevel == 2:
                errorMessageMenu.textInfo["Message"]["Text"] = "CRITICAL ERROR: "+errorMessageMenu.textInfo["Message"]["Text"]
                errorMessageMenu.buttons[2].hidden = False
                errorMessageMenu.buttons[2].setPos((screenRect.centerx, screenRect.centery), 1)
        
        errorMessageMenu.update(pressedKeys, mouseEvents, time)
        errorMessageMenu.draw(screen)        
               
        if menuSurf.get_alpha() < 255:
            errorMessageMenu.draw(menuSurf)
            fadeInMenu(errorMessageMenu.bgImage)
            initMenu = True
            
        if fadeSurf.get_alpha() > 0:
            fadeFromBlack(screen.copy())
            initMenu = True
        
        if errorMessageMenu.pressedButton == "Back":
            if currentState.vars['lastState'] != None:
                if currentState.vars['lastStateIsMenu']:
                    fadeOutMenu(errorMessageMenu.bgImage)
                else:
                    fadeToBlack(screen.copy())
                currentState = currentState.vars['lastState']
            errorMessageMenu.reinit()
        elif errorMessageMenu.pressedButton == "Exit":
            pygame.mixer.music.fadeout(fadeTime)
            fadeToBlack(screen.copy())
            runtime += clock.tick()
            log.info("Quitting (Exit button from error screen). Run time: %f seconds."%(runtime/1000.))
            done = True
            errorMessageMenu.reinit()
        elif errorMessageMenu.pressedButton == "MainMenu":
            currentState = mainMenuState
            log.info("STATE CHANGE: %s"%currentState.name)
            errorMessageMenu.draw(menuSurf)
            fadeOutMenu(errorMessageMenu.bgImage)
            errorMessageMenu.reinit()
        
    else:
        log.warning("currentState is set to unhandled object (%s). Resetting to main menu state. The game may be unstable now."%currentState)
        
        currentState = errorMessageState
        currentState.vars['Message'] = "Unhandled state type. Most likely a typo or incomplete section of the game. Contact the programmer."
        currentState.vars['errorLevel'] = 0
        currentState.vars['lastState'] = mainMenuState
        currentState.vars['lastStateIsMenu'] = True
    
    blitDebugInfo(fps, currentState, subState, fullscreen, debugSurf, debugFont, maxfps)
    if debug:
        screen.blit(debugSurf, screenRect.topleft)
    
    pygame.display.update(screenRect)

log.debug("Ending logging cleanly.")
logging.shutdown()
fh.close() # Close the log file.
sys.exit()