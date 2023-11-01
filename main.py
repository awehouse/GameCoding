'''
A PORTION OF THIS CODE WAS GENERATED AND CLEANED UP BY THE FOLLOWING GENERATIVE AI(S):
Replit AI

'''
# IMPORTS
import pygame as pg
import os

from maps.testroom import room as testroom

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

# PLAYER CLASS
class Player(pg.sprite.Sprite):

    def __init__(self,spriteimgdir,roomobj):
        pg.sprite.Sprite.__init__(self)
        #PLAYER SPRITE
        self.image, self.rect = load_image(spriteimgdir,60,90,True)
        self.xpos = X_POS_MAX/2 #spawn location, movement is controled by the self.rect object
        self.xmove = 0
        self.ypos = 500 #spawn location
        self.ymove = 0
        self.roomdir = roomobj
        
        self.area = pg.display.get_surface().get_rect() # creates a rect object to control player sprite
        self.rect.x = self.xpos
        self.rect.y = self.ypos # positional coordinates.
        self.maxspeed = 7
           
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
                print(str(obst.teleportx) + " " + str(obst.teleporty))
                print(str(self.rect.x) + " " + str(self.rect.y))

    def handle_portal_collision(self):
        portalhits = pg.sprite.spritecollide(self, portals, False)
        for portal in portalhits:
            pass

    


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
    def __init__(self, spriteimgdir, xscale, yscale, absscale, x, y, damage=0, teleport=False, teleportx=None, teleporty=None):
        super().__init__()
        self.image, self.rect = load_image(
            spriteimgdir, xscale, yscale, absscale)
        self.xpos = x
        self.ypos = y

        # creates a rect object to render portal sprite
        self.area = pg.display.get_surface().get_rect()
        self.rect.x = self.xpos
        self.rect.y = self.ypos  # positional coordinates.


platforms = pg.sprite.Group()
obstacles = pg.sprite.Group()
portals = pg.sprite.Group()

i=0 # ADD EACH PLATFORM INTO THE platforms SPRITE GROUP
for plat in testroom['platlist']:    
    pt = Platform(testroom['platlist'][i]['dir'], testroom['platlist'][i]['xscale'],
                testroom['platlist'][i]['yscale'], testroom['platlist'][i]['absscale'],
                testroom['platlist'][i]['xpos'], testroom['platlist'][i]['ypos'])
    platforms.add(pt)
    i+=1

i = 0  # ADD EACH PLATFORM INTO THE obstacles SPRITE GROUP
for obst in testroom['obstlist']:
    obst = Obstacle(testroom['obstlist'][i]['dir'], testroom['obstlist'][i]['xscale'], testroom['obstlist'][i]['yscale'],
                testroom['obstlist'][i]['absscale'], testroom['obstlist'][i]['xpos'], testroom['obstlist'][i]['ypos'], 
                testroom['obstlist'][i]['damage'], testroom['obstlist'][i]['teleport'], testroom['obstlist'][i]['teleportx'],
                testroom['obstlist'][i]['teleporty'])
    obstacles.add(obst)
    i+=1

i = 0  # ADD EACH PLATFORM INTO THE portals SPRITE GROUP
for port in testroom['portallist']:
    port = Portal(testroom['portallist'][i]['dir'], testroom['portallist'][i]['xscale'],
                testroom['portallist'][i]['yscale'], testroom['portallist'][i]['absscale'], 
                  testroom['portallist'][i]['xpos'], testroom['portallist'][i]['ypos'], testroom['portallist'][i]['linkdir'])

player = Player('sprites/testing/purple.webp',testroom)


allsprites = pg.sprite.RenderPlain([player,platforms,obstacles])

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