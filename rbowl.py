import libtcod.libtcodpy as libtcod
from random import randint

SCREEN_WIDTH = 24
SCREEN_HEIGHT = 14
LIMIT_FPS = 20

libtcod.console_set_custom_font('consolas_unicode_12x12.png', libtcod.FONT_LAYOUT_ASCII_INROW | libtcod.FONT_TYPE_GREYSCALE, nb_char_horiz=32, nb_char_vertic=64)

libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'rbowl', False)
libtcod.sys_set_fps(LIMIT_FPS)


class Mob:
    def __init__(self, x=None, y=None, char=None, color=None):
        """
        Fill with defaults
        """
        self.x = x or 0
        self.y = y or 0
        self.char = char or '?'
        self.color = color or libtcod.white
       
    def display(self):
        # TODO: change background to default
        libtcod.console_put_char_ex(0, self.x, self.y, self.char, self.color, libtcod.black)

    def move(self, dx, dy):
        if 0 <= self.x + dx < SCREEN_WIDTH:
            self.x += dx
        if 0 <= self.y + dy < SCREEN_HEIGHT:
            self.y += dy
        
player = Mob(x=SCREEN_WIDTH/2, y=SCREEN_HEIGHT/2, char='@')
ai = Mob(x=randint(0,SCREEN_WIDTH-1), y=randint(0,SCREEN_HEIGHT-1), char='g', color=libtcod.green)

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
    
libtcod.console_set_default_foreground(0, libtcod.white)
while not libtcod.console_is_window_closed():
    libtcod.console_clear(0)

    player.display()
    ai.display()
 
    libtcod.console_flush()
 
    #handle keys and exit game if needed
    exit = handle_keys()
    if exit:
        break
