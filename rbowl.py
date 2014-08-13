import libtcod.libtcodpy as libtcod
from random import randint

SCREEN_WIDTH = 24
SCREEN_HEIGHT = 16
LIMIT_FPS = 20

MAP_WIDTH = 80
MAP_HEIGHT = 45

ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 10
MAX_ROOMS = 30

bg_colors = {
    "void": libtcod.Color(0, 0, 0),
    "dark_wall": libtcod.Color(25, 25, 25),
    "dark_ground": libtcod.Color(50, 50, 50),
    }
    
fg_colors = {
    "void": libtcod.Color(200, 200, 200),
    "dark_wall": libtcod.Color(50, 50, 50),
    "dark_ground": libtcod.Color(75, 75, 75),
    "dark_stairs": libtcod.Color(100, 100, 75),
    }
    

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
        
    def center(self):
        center_x = (self.x1 + self.x2) / 2
        center_y = (self.y1 + self.y2) / 2
        return (center_x, center_y)
        
    def intersect(self, other):
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)
        
class Tile:
    "Tile of the map, and its properties"
    def __init__(self, blocked, block_sight=None):
        self.blocked = blocked
        self.block_sight = block_sight or blocked

class Map:
    def __init__(self, width=MAP_WIDTH, height=MAP_HEIGHT):
        self.width = width
        self.height = height
        self.tiles = [[Tile(True)
                        for y in range(self.height)]
                            for x in range(self.width)]
        self.objects = []                            
        self.rooms = []
        self.num_rooms = 0
        
        for r in range(MAX_ROOMS):
            w = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
            h = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
            x = libtcod.random_get_int(0, 0, MAP_WIDTH - w - 1)
            y = libtcod.random_get_int(0, 0, MAP_HEIGHT - h - 1)
            
            new_room = Rect(x, y, w, h)
            
            failed = False
            for other_room in self.rooms:
                if new_room.intersect(other_room):
                    failed = True
                    break
            
            if not failed:
                self.create_room(new_room)
                (new_x, new_y) = new_room.center()
                
                if self.num_rooms == 0:
                    self.start_x = new_x
                    self.start_y = new_y
                else:
                    self.join_rooms(new_room, self.rooms[-1])
                self.end_x = new_x
                self.end_y = new_y
                
                self.rooms.append(new_room)
                self.num_rooms += 1
    
    def add_object(self, obj):
        self.objects.append(obj)
    
    def remove_object(self, obj):
        self.objects.remove(obj)
    
    def in_bounds(self, x, y):
        return ((0 <= x < self.width) and (0 <= y < self.height))
    
    def is_blocked(self, x, y):
        if not self.in_bounds(x, y):
            return True
        return self.tiles[x][y].blocked
        
    def is_sightblocked(self, x, y):
        if not self.in_bounds(x, y):
            return True
        return self.tiles[x][y].block_sight
        
    def create_room(self, room):
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                if self.in_bounds(x, y):
                    self.tiles[x][y].blocked = False
                    self.tiles[x][y].block_sight = False

    def join_rooms(self, room1, room2):
        cx1, cy1 = room1.center()
        cx2, cy2 = room2.center()
        if libtcod.random_get_int(0, 0, 1) == 1:
            self.create_h_tunnel(cx1, cx2, cy1)
            self.create_v_tunnel(cx2, cy1, cy2)
        else:
            self.create_v_tunnel(cx1, cy1, cy2)
            self.create_h_tunnel(cx1, cx2, cy2)
                    
    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            if self.in_bounds(x, y):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False

    def create_v_tunnel(self, x, y1, y2):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if self.in_bounds(x, y):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False
                
    def find_clear_space(self):
        if len(self.rooms) == 0:
            return (libtcod.random_get_int(0, 0, map.width - 1),
                    libtcod.random_get_int(0, 0, map.height - 1))
        room = self.rooms[libtcod.random_get_int(0, 0, len(self.rooms) - 1)]
        return (libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1),
                libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1))

class Screen:
    def __init__(self, map, width=SCREEN_WIDTH, height=SCREEN_HEIGHT):
        self.map = map
        self.width = width
        self.height = height
        self.x_offset = 0
        self.y_offset = 0
        
    def move(self, dx, dy):
        new_x = self.x_offset + dx
        new_y = self.y_offset + dy
        half_width = self.width/2
        half_height = self.height/2
        if -half_width < new_x < self.map.width - half_width:
            self.x_offset = new_x
        if -half_height < new_y < self.map.height - half_height:
            self.y_offset = new_y
        
    def display(self, con):
        for y in range(self.height):
            for x in range(self.width):
                map_x, map_y = x + self.x_offset, y + self.y_offset 
                if map.in_bounds(map_x, map_y):
                    wall = map.is_sightblocked(map_x, map_y)
                    
                    if wall:
                        libtcod.console_set_char_background(con, x, y, bg_colors["dark_wall"], libtcod.BKGND_SET)
                        libtcod.console_set_default_foreground(con, fg_colors["dark_wall"])
                        libtcod.console_put_char(con, x, y, '#', libtcod.BKGND_NONE)
                    elif map_x == map.start_x and map_y == map.start_y:
                        libtcod.console_set_char_background(con, x, y, bg_colors["dark_ground"], libtcod.BKGND_SET)
                        libtcod.console_set_default_foreground(con, fg_colors["dark_stairs"])
                        libtcod.console_put_char(con, x, y, '<', libtcod.BKGND_NONE)
                    elif map_x == map.end_x and map_y == map.end_y:
                        libtcod.console_set_char_background(con, x, y, bg_colors["dark_ground"], libtcod.BKGND_SET)
                        libtcod.console_set_default_foreground(con, fg_colors["dark_stairs"])
                        libtcod.console_put_char(con, x, y, '>', libtcod.BKGND_NONE)                    
                    else:
                        libtcod.console_set_char_background(con, x, y, bg_colors["dark_ground"], libtcod.BKGND_SET)
                        libtcod.console_set_default_foreground(con, fg_colors["dark_ground"])
                        libtcod.console_put_char(con, x, y, '.', libtcod.BKGND_NONE)
                else:
                    libtcod.console_set_char_background(con, x, y, bg_colors["void"], libtcod.BKGND_SET)
                    libtcod.console_put_char(con, x, y, ' ', libtcod.BKGND_NONE)
                
        for object in map.objects:
            object.draw(con, self.x_offset, self.y_offset)
        
        libtcod.console_blit(con, 0, 0, self.width, self.height, 0, 0, 0)
        libtcod.console_flush()
        
class Object:
    def __init__(self, map, xy=None, x=None, y=None, char=None, color=None):
        """
        Fill with defaults
        """
        self.map = map
        map.add_object(self)
        if xy is not None:
            x, y = xy
        self.x = x or 0
        self.y = y or 0
        self.char = char or '?'
        self.color = color or libtcod.white
       
    def draw(self, con, x_off, y_off):
        libtcod.console_set_default_foreground(con, self.color)
        libtcod.console_put_char(con, self.x - x_off, self.y - y_off, self.char, libtcod.BKGND_NONE)

    def move(self, dx, dy):
        if map.is_blocked(self.x + dx, self.y + dy):
            return
        if 0 <= self.x + dx < MAP_WIDTH:
            self.x += dx
        if 0 <= self.y + dy < MAP_HEIGHT:
            self.y += dy
        
    def clear(self):
        libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)
        
map = Map()
player = Object(map, xy=(map.start_x, map.start_y), char='@')
ai = Object(map, xy=map.find_clear_space(), char='g', color=libtcod.green)
screen = Screen(map)
screen.move(map.start_x - SCREEN_WIDTH/2, map.start_y - SCREEN_HEIGHT/2)

def handle_keys():
    global player
    
    key = libtcod.console_check_for_keypress(libtcod.KEY_PRESSED | libtcod.KEY_RELEASED)
    
    if key.vk == libtcod.KEY_ESCAPE:
        return True
    elif key.c == ord('w'):
        screen.move(0, -1)
    elif key.c == ord('s'):
        screen.move(0, 1)
    elif key.c == ord('a'):
        screen.move(-1, 0)
    elif key.c == ord('d'):
        screen.move(1, 0)
        
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
    screen.display(con)
    
    for obj in map.objects:
        obj.clear()
   
    #handle keys and exit game if needed
    exit = handle_keys()
    if exit:
        break
        
