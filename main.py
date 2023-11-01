'''
A PORTION OF THIS CODE WAS GENERATED AND CLEANED UP BY THE FOLLOWING GENERATIVE AI(S):
Replit AI

'''
# IMPORTS
import pygame as pg
import os
import time

from maps import list_of_rooms

# INITIALIZATION
# Initialize variables
X_POS_MAX = 1280
Y_POS_MAX = 720
GRAVITY = 1.4
MAX_GRAV = 20
ACCELERATION = 1
MAX_SPEED = 8

# Initialize pygame and create the screen
pg.init()
screen = pg.display.set_mode((X_POS_MAX, Y_POS_MAX))
clock = pg.time.Clock()

# BACKGROUND IMAGE
bg = pg.image.load(os.path.abspath(".") + '/assets/backgrounds/green.jpeg',).convert()
bg = pg.transform.scale(bg, (X_POS_MAX, Y_POS_MAX))
screen.blit(bg, (0, 0))

# FUNCTION THAT LOADS IMAGES
def load_image(dir, xscale=1, yscale=1, absscale=False):
    fullname = os.path.abspath(".") + '/assets/' + dir
    image = pg.image.load(fullname)

    if absscale == False:
        size = image.get_size()
        size = (size[0] * xscale, size[1] * yscale)
    elif absscale == True:
        size = (xscale, yscale)
    else:
        print("unable to load image file for "+fullname)
    image = pg.transform.scale(image, size)

    image = image.convert()
    return image, image.get_rect()

# FUNCTION THAT CHANGES THE ROOM
def change_room(player, room_id):
    global allsprites, platforms, obstacles, portals
    # Clear existing sprites
    platforms.empty()
    obstacles.empty()
    portals.empty()
    allsprites.empty()
    # Add platforms from the new room
    for plat in list_of_rooms[room_id]['platlist']:
        pt = Platform(plat['dir'], plat['xscale'], plat['yscale'], plat['absscale'], plat['xpos'], plat['ypos'])
        platforms.add(pt)

    # Add obstacles from the new room
    for obst in list_of_rooms[room_id]['obstlist']:
        obstacle = Obstacle(obst['dir'], obst['xscale'], obst['yscale'], obst['absscale'], obst['xpos'], obst['ypos'], obst['damage'], obst['teleport'], obst['teleportx'], obst['teleporty'])
        obstacles.add(obstacle)

    # Add portals from the new room
    for port in list_of_rooms[room_id]['portallist']:
        portal = Portal(port['dir'], port['xscale'], port['yscale'], port['absscale'], port['xpos'], port['ypos'], port['linkdir'], port['spawnx'], port['spawny'])
        portals.add(portal)

    # Add ladders from the new room
    for ladd in list_of_rooms[room_id]['ladderlist']:    
            ladder = Ladder(ladd['dir'], ladd['xscale'],
                ladd['yscale'], ladd['absscale'],
                ladd['xpos'], ladd['ypos'], ladd['topcapped'])
    ladders.add(ladder)

    # Update player's room id
    player.roomid = room_id

    # Add player and other sprites to the allsprites group
    allsprites.add(player, platforms, obstacles, portals, ladders)

# PLAYER CLASS
class Player(pg.sprite.Sprite):

    def __init__(self,spriteimgdir,roomid):
        pg.sprite.Sprite.__init__(self)
        #PLAYER SPRITE
        self.image, self.rect = load_image(spriteimgdir,60,90,True)
        self.xpos = X_POS_MAX/2 #spawn location, movement is controled by the self.rect object
        self.xmove = 0
        self.ypos = 500 #spawn location
        self.ymove = 0
        self.roomid = roomid
        self.climbing = False
        
        self.area = pg.display.get_surface().get_rect() # creates a rect object to control player sprite
        self.rect.x = self.xpos
        self.rect.y = self.ypos # positional coordinates.
        self.maxspeed = 7
        self.last_room_change_time = time.time()
           
    def update(self):
        self.gravity() # apply gravity
        # print(player.xmove)

        # COLLISION
        self.handle_platform_collision()
        self.handle_obstacle_collision()
        self.handle_portal_collision()
        
        # MOVE THE SPRITE
        self.rect.x = round(self.rect.x + self.xmove) # moves player by xmove in the X axis
        self.rect.y = round(self.rect.y + self.ymove) # moves player by ymove in the Y axis

    def gravity(self):
        if self.ymove < MAX_GRAV:
            self.ymove += GRAVITY
        else:
            self.ymove = MAX_GRAV

        if self.rect.bottom >= Y_POS_MAX and self.ymove >= 0:
            self.ymove = 0
            self.rect.bottom = Y_POS_MAX

    def walk(self , left = False , right = False):
        if left and self.rect.left != 0:
            while self.xmove >= -self.maxspeed:
                self.xmove -= ACCELERATION # accelerate towards the left
            else:
                self.xmove = -self.maxspeed # maximum speed
            if self.rect.left <= 0 and self.xmove <= 0: # stop at the left side of the screen
                self.xmove = 0
                self.rect.left = 0

        if right and self.rect.right != X_POS_MAX:
            while self.xmove <= self.maxspeed:
                self.xmove += ACCELERATION
            else:
                self.xmove = self.maxspeed
            if self.rect.right >= X_POS_MAX and self.xmove >= 0:
                self.xmove = 0
                self.rect.right = X_POS_MAX

        if not left and not right:
            if self.xmove > 0:
                self.xmove -= ACCELERATION
            if self.xmove < 0:
                self.xmove += ACCELERATION
            else:
                self.xmove = 0
    
    def jump(self, spacebar = False):
        if spacebar:
            while self.ymove == 0 :
                self.ymove += -17

    def handle_platform_collision(self):
        hits = pg.sprite.spritecollide(self, platforms, False)
        for plat in hits:
            if (self.rect.right >= plat.rect.left > self.rect.left) and (self.rect.bottom > plat.rect.top + 20) and (self.xmove >= 0):
                self.xmove = 0
                self.rect.right = plat.rect.left
            elif (self.rect.left <= plat.rect.right < self.rect.right) and (self.rect.bottom > plat.rect.top + 20) and (self.xmove <= 0):
                self.xmove = 0
                self.rect.left = plat.rect.right
            elif (plat.rect.bottom > self.rect.bottom >= plat.rect.top) and (self.rect.right >= plat.rect.left-2) and (self.rect.left <= plat.rect.right+2):
                self.rect.bottom = plat.rect.top
                self.ymove = 0

    def handle_obstacle_collision(self):
        obsthits = pg.sprite.spritecollide(self, obstacles, False)
        for obst in obsthits:
            if obst.teleport:
                self.rect.x = obst.teleportx
                self.rect.y = obst.teleporty
                self.xmove = 0
                self.ymove = 0

    def handle_portal_collision(self):
        portalhits = pg.sprite.spritecollide(self, portals, False)
        for portal in portalhits:
            if pg.key.get_pressed()[pg.K_UP] and time.time() - self.last_room_change_time >= 2:
                change_room(self, portal.roomid)
                print(portal.roomid)
                self.rect.x = portal.spawnx
                self.rect.y = portal.spawny
                self.xmove = 0
                self.ymove = 0
                self.last_room_change_time = time.time()
            
    def handle_ladder_collision(self):
        ladderhits = pg.sprite.spritecollide(self, ladders, False)
        platformhits = pg.sprite.spritecollide(self, platforms, False) 
        if climbing == False:
            for ladder in ladderhits:
                if pg.key.getpressed()[pg.K_UP] and (ladder.right >= self.right >= ladder.left or ladder.right >= self.left >= ladder.left):
                self.climbing = True
                print(self.climbing)

        elif climbing == True:
            for ladder in ladderhits:
                if pg.key.getpressed()[pg.K_UP] and (ladder.right >= self.right >= ladder.left or ladder.right >= self.left >= ladder.left):
                self.climbing = True
                print(self.climbing)
                for platform in platformhits: # hitting the top of a platform will dismount the character
                    if self.climbing == True and self.bottom-10 <=platform.top <= self.bottom:
                        self.climbing = False
                        print(self.climbing)
            

class Platform(pg.sprite.Sprite):
    def __init__(self, spriteimgdir, xscale, yscale, absscale, x, y):
        super().__init__()
        self.image, self.rect = load_image(spriteimgdir, xscale, yscale, absscale)
        self.xpos = x
        self.ypos = y
        
        self.area = pg.display.get_surface().get_rect() # creates a rect object to render platform sprite
        self.rect.x = self.xpos
        self.rect.y = self.ypos  # positional coordinates.

class Obstacle(pg.sprite.Sprite):
    def __init__(self, spriteimgdir, xscale, yscale, absscale, x, y, damage=0, teleport=False, teleportx=None, teleporty=None):
        super().__init__()
        self.image, self.rect = load_image(
            spriteimgdir, xscale, yscale, absscale)
        self.xpos = x
        self.ypos = y
        self.teleport = teleport
        self.teleportx = teleportx
        self.teleporty = teleporty

        # creates a rect object to render obstacle sprite
        self.area = pg.display.get_surface().get_rect()
        self.rect.x = self.xpos
        self.rect.y = self.ypos  # positional coordinates.

class Portal(pg.sprite.Sprite):
    def __init__(self, spriteimgdir, xscale, yscale, absscale, x, y, roomid, spawnx, spawny):
        super().__init__()
        self.image, self.rect = load_image(spriteimgdir, xscale, yscale, absscale)
        self.xpos = x
        self.ypos = y
        self.roomid = roomid
        self.spawnx = spawnx
        self.spawny = spawny

        # creates a rect object to render portal sprite
        self.area = pg.display.get_surface().get_rect()
        self.rect.x = self.xpos
        self.rect.y = self.ypos  # positional coordinates.

class Ladder(pg.sprite.Sprite):
    def __init__(self, spriteimgdir, xscale, yscale, absscale, x, y, topcapped=False):
        super().__init__()
        self.image, self.rect = load_image(spriteimgdir, xscale, yscale, absscale)
        self.xpos = x
        self.ypos = y
        self.topcapped = topcapped
        
        self.area = pg.display.get_surface().get_rect() # creates a rect object to render platform sprite
        self.rect.x = self.xpos
        self.rect.y = self.ypos  # positional coordinates.


platforms = pg.sprite.Group()
obstacles = pg.sprite.Group()
portals = pg.sprite.Group()
ladders = pg.sprite.Group()

# ADD EACH PLATFORM INTO THE platforms SPRITE GROUP
for plat in list_of_rooms[0]['platlist']:    
    ptf = Platform(plat['dir'], plat['xscale'],
                plat['yscale'], plat['absscale'],
                plat['xpos'], plat['ypos'])
    platforms.add(ptf)

# ADD EACH OBSTACLE INTO THE obstacles SPRITE GROUP
for obstacle in list_of_rooms[0]['obstlist']:
    obst = Obstacle(obstacle['dir'], obstacle['xscale'], obstacle['yscale'],
                obstacle['absscale'], obstacle['xpos'], obstacle['ypos'], 
                obstacle['damage'], obstacle['teleport'], obstacle['teleportx'],
                obstacle['teleporty'])
    obstacles.add(obst)

# ADD EACH PORTAL INTO THE portals SPRITE GROUP
for portal in list_of_rooms[0]['portallist']:
    port = Portal(portal['dir'], portal['xscale'],
                portal['yscale'], portal['absscale'], 
                portal['xpos'], portal['ypos'], portal['linkdir'],
                portal['spawnx'], portal['spawny'])
    portals.add(port)

# ADD EACH LADDER INTO THE ladders SPRITE GROUP
for ladder in list_of_rooms[0]['ladderlist']:    
    ladd = Ladder(ladd['dir'], ladd['xscale'],
                ladd['yscale'], ladd['absscale'],
                ladd['xpos'], ladd['ypos'])
    platforms.add(ladds)

player = Player('sprites/testing/purple.webp',list_of_rooms[0])
allsprites = pg.sprite.RenderPlain([player,platforms,obstacles,portals,ladders])

running = True
# GAME LOOP
while running:
    screen.blit(bg, (0, 0)) # clears the screen by bliting the background on top of everything
    allsprites.draw(screen)
    pg.display.flip()

    # Input handling
    keys = pg.key.get_pressed()
    player.jump(keys[pg.K_SPACE])
    player.walk(keys[pg.K_LEFT], keys[pg.K_RIGHT])

    

    # EVENT CHECK                # pg.event.get() returns a list of events
    for event in pg.event.get():
        if event.type == pg.QUIT:  # closes the program when user closes the window
            running = False

    allsprites.update()
    
    clock.tick(30)  # locks the game to 30 frames/second


# CLEANUP
pg.quit()