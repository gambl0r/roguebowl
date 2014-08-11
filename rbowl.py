import libtcod.libtcodpy as libtcod
from random import randint

SCREEN_WIDTH = 24
SCREEN_HEIGHT = 14
LIMIT_FPS = 20

MAP_WIDTH = 80
MAP_HEIGHT = 45

color_dark_wall = libtcod.Color(25, 25, 25)
color_dark_wall_f = libtcod.Color(50, 50, 50)
color_dark_ground = libtcod.Color(50, 50, 50)
color_dark_ground_f = libtcod.Color(75, 75, 75)

libtcod.console_set_custom_font('consolas_unicode_12x12.png', libtcod.FONT_LAYOUT_ASCII_INROW | libtcod.FONT_TYPE_GREYSCALE, nb_char_horiz=32, nb_char_vertic=64)

libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'rbowl', False)
libtcod.sys_set_fps(LIMIT_FPS)

class Rect:
    "A rectangle on the map."
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x+w
        self.y2 = y+h

class Tile:
    "Tile of the map, and its properties"
    def __init__(self, blocked, block_sight=None):
        self.blocked = blocked
        self.block_sight = block_sight or blocked

def make_map():
    map = [[Tile(False)
            for y in range(MAP_HEIGHT)]
                for x in range(MAP_WIDTH)]
    map[13][12].blocked = True
    map[13][12].block_sight = True
    map[5][12].blocked = True
    map[5][12].block_sight = True
    return map
    
def render_all(con, objects, map):
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            wall = map[x][y].block_sight
            
            if wall:
                libtcod.console_set_char_background(con, x, y, color_dark_wall, libtcod.BKGND_SET)
                libtcod.console_set_default_foreground(con, color_dark_wall_f)
                libtcod.console_put_char(con, x, y, '#', libtcod.BKGND_NONE)
            else:
                libtcod.console_set_char_background(con, x, y, color_dark_ground, libtcod.BKGND_SET)
                libtcod.console_set_default_foreground(con, color_dark_ground_f)
                libtcod.console_put_char(con, x, y, '.', libtcod.BKGND_NONE)
    for object in objects:
        object.draw(con)
        
    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
    libtcod.console_flush()
        
class Object:
    def __init__(self, map, x=None, y=None, char=None, color=None):
        """
        Fill with defaults
        """
        self.map = map
        self.x = x or 0
        self.y = y or 0
        self.char = char or '?'
        self.color = color or libtcod.white
       
    def draw(self, con):
        libtcod.console_set_default_foreground(con, self.color)
        libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)

    def move(self, dx, dy):
        if map[self.x + dx][self.y + dy].blocked:
            return
        if 0 <= self.x + dx < MAP_WIDTH:
            self.x += dx
        if 0 <= self.y + dy < MAP_HEIGHT:
            self.y += dy
        
            
    def clear(self):
        libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)

map = make_map()
player = Object(map, x=SCREEN_WIDTH/2, y=SCREEN_HEIGHT/2, char='@')
ai = Object(map, x=randint(0,SCREEN_WIDTH-1), y=randint(0,SCREEN_HEIGHT-1), char='g', color=libtcod.green)
objects = [ai, player]

def handle_keys():
    global player
    
    key = libtcod.console_check_for_keypress()
    if key.vk == libtcod.KEY_ESCAPE:
        return True
    
    if libtcod.console_is_key_pressed(libtcod.KEY_UP):
        player.move(0, -1)
    elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
        player.move(0, 1)
    elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
        player.move(-1, 0)
    elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
        player.move(1, 0)
    
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
libtcod.console_set_default_foreground(con, libtcod.white)
while not libtcod.console_is_window_closed():
    #libtcod.console_clear(con)
    render_all(con, objects, map)
    
    for obj in objects:
        obj.clear()
   
    #handle keys and exit game if needed
    exit = handle_keys()
    if exit:
        break
        
