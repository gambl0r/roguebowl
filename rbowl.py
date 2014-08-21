import libtcod.libtcodpy as libtcod
from random import randint

SCREEN_WIDTH = 40
SCREEN_HEIGHT = 20
LIMIT_FPS = 20

MAP_WIDTH = 80
MAP_HEIGHT = 45

ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 10
MAX_ROOMS = 30

MAX_ROOM_MONSTERS = 3

FOV_ALGO = libtcod.FOV_SHADOW
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 8

void_color = libtcod.Color(0, 0, 0)
color_pairs = {
    "void": (libtcod.Color(0, 0, 0), libtcod.Color(0, 0, 0)),
    "bg_wall": (libtcod.Color(25, 25, 25), libtcod.Color(50, 50, 25)),
    "fg_wall": (libtcod.Color(50, 50, 50), libtcod.Color(75, 75, 50)),
    "bg_floor": (libtcod.Color(50, 50, 50), libtcod.Color(75, 75, 50)),  
    "fg_floor": (libtcod.Color(75, 75, 75), libtcod.Color(100, 100, 75)),
    "fg_stairs": (libtcod.Color(100, 100, 75), libtcod.Color(125, 125, 75)),
    }
    

libtcod.console_set_custom_font('consolas_unicode_12x12.png', libtcod.FONT_LAYOUT_ASCII_INROW | libtcod.FONT_TYPE_GREYSCALE, nb_char_horiz=32, nb_char_vertic=64)

libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'rbowl', False)
libtcod.sys_set_fps(LIMIT_FPS)

class Game:
    def __init__(self):
        self.state = 'playing'
        self.player_action = None

        self.map = Map()
        self.player = Object(self.map, 
                             self.map.start_x,
                             self.map.start_y, 
                             '@', 'player', blocks=True)
        self.screen = Screen(self.map)
        self.screen.move(self.map.start_x - SCREEN_WIDTH/2,
                         self.map.start_y - SCREEN_HEIGHT/2)

        self.fov_recompute = True
    
    
        self.con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.libtcod.console_set_default_foreground(self.con, libtcod.white)
        self.pressed = set()
        
    def run():
        while not libtcod.console_is_window_closed():
            self.screen.display(self.con)
    
            for obj in self.map.objects:
                obj.clear()
   
            #handle keys and exit game if needed
            action = self.handle_keys()
            if action == 'exit':
                break
            
            if action is not None:
                pass
                
    def handle_keys(self):
        key = libtcod.console_check_for_keypress(libtcod.KEY_PRESSED | libtcod.KEY_RELEASED)
    
        if key.vk == libtcod.KEY_ESCAPE:
            return 'exit'
        elif key.vk == libtcod.KEY_CHAR:
            if key.pressed:
                self.pressed.add(key.c)
            else:
                try:
                    self.pressed.remove(key.c)
                except KeyError:
                    pass
        
        if ord('w') in self.pressed:
            self.screen.move(0, -1)
        elif ord('s') in self.pressed:
            self.screen.move(0, 1)
        elif ord('a') in self.pressed:
            self.screen.move(-1, 0)
        elif ord('d') in self.pressed:
            self.screen.move(1, 0)
        
        if self.state == 'playing':
            if libtcod.console_is_key_pressed(libtcod.KEY_UP):
                self.player.move(0, -1)
                self.fov_recompute = True
            elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
                self.player.move(0, 1)
                self.fov_recompute = True
            elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
                self.player.move(-1, 0)
                self.fov_recompute = True
            elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
                self.player.move(1, 0)
                self.fov_recompute = True
            else:
                return None
        return 'action'
        
        
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
        
class TileType:
    "Types for tiles of the map, and its properties"
    def __init__(self, char, fg_color_pair, bg_color_pair, blocked, block_sight=None):
        self.char = char
        self.fg_color, self.fg_color_lit = fg_color_pair
        self.bg_color, self.bg_color_lit = bg_color_pair
        self.blocked = blocked
        self.block_sight = block_sight or blocked

tiletypes = {
    'void':        TileType(' ', color_pairs["void"],      color_pairs["void"],     True),
    'floor':       TileType('.', color_pairs["fg_floor"],  color_pairs["bg_floor"], False),
    'wall':        TileType('#', color_pairs["fg_wall"],   color_pairs["bg_wall"],  True),
    'up_stairs':   TileType('<', color_pairs["fg_stairs"], color_pairs["bg_floor"], False),
    'down_stairs': TileType('>', color_pairs["fg_stairs"], color_pairs["bg_floor"], False),
    }
    
class Tile:
    "Tile of the map, and its properties"
    def __init__(self, type):
        self.type = tiletypes[type]
        self.explored = False
        
class Map:
    def __init__(self, width=MAP_WIDTH, height=MAP_HEIGHT):
        self.width = width
        self.height = height
        self.tiles = [[Tile('wall')
                        for y in range(self.height)]
                            for x in range(self.width)]
        self.fov_map = libtcod.map_new(self.width, self.height)
                
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
                self.generate_room_objects(new_room)
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
                
        self.tiles[self.start_x][self.start_y].type = tiletypes['up_stairs']
        self.tiles[self.end_x][self.end_y].type = tiletypes['down_stairs']
        
        for y in range(self.height):
            for x in range(self.width):
                libtcod.map_set_properties(self.fov_map, 
                                           x, y, 
                                           not self.tiles[x][y].type.block_sight, 
                                           not self.tiles[x][y].type.blocked)

    
    def add_object(self, obj):
        self.objects.append(obj)
    
    def remove_object(self, obj):
        self.objects.remove(obj)
    
    def generate_room_objects(self, room):
        num_monsters = libtcod.random_get_int(0, 0, MAX_ROOM_MONSTERS)
 
        for i in range(num_monsters):
            x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
            y = libtcod.random_get_int(0, room.y1+1, room.y2-1)
            
            if self.is_blocked(x, y):
                continue
 
            pick = libtcod.random_get_int(0, 0, 100)
            if  pick < 50:  
                monster = Object(self, x, y, 'g', 'goblin', color=libtcod.green, blocks=True)
            if pick < 80:  
                monster = Object(self, x, y, 'o', 'orc', color=libtcod.desaturated_green, blocks=True)
            else:
                monster = Object(self, x, y, 'T', 'troll', color=libtcod.darker_green, blocks=True)
 
            self.objects.append(monster)
    
    def in_bounds(self, x, y):
        return ((0 <= x < self.width) and (0 <= y < self.height))
    
    def is_blocked(self, x, y):
        if not self.in_bounds(x, y):
            return True
            
        if self.tiles[x][y].type.blocked:
            return True
            
        for object in self.objects:
            if object.blocks and object.x == x and object.y == y:
                return True
            
        return False
        
    def is_sightblocked(self, x, y):
        if not self.in_bounds(x, y):
            return True
        return self.tiles[x][y].type.block_sight
        
    def create_room(self, room):
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                if self.in_bounds(x, y):
                    self.tiles[x][y].type = tiletypes['floor']

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
                self.tiles[x][y].type = tiletypes['floor']
                
    def create_v_tunnel(self, x, y1, y2):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if self.in_bounds(x, y):
                self.tiles[x][y].type = tiletypes['floor']
                
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
        global player, fov_recompute
        if fov_recompute:
            #recompute FOV if needed (the player moved or something)
            fov_recompute = False
            libtcod.map_compute_fov(self.map.fov_map, player.x, player.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)

        for y in range(self.height):
            for x in range(self.width):
                map_x, map_y = x + self.x_offset, y + self.y_offset 
                if map.in_bounds(map_x, map_y):
                    visible = libtcod.map_is_in_fov(self.map.fov_map, map_x, map_y)
                    tt = map.tiles[map_x][map_y].type
                    
                    if visible:
                        libtcod.console_set_char_background(con, x, y, tt.bg_color_lit, libtcod.BKGND_SET)
                        libtcod.console_set_default_foreground(con, tt.fg_color_lit)
                        libtcod.console_put_char(con, x, y, tt.char, libtcod.BKGND_NONE)
                            
                        # TODO: Doing this here bugs it if the player's light radius is not on screen
                        self.map.tiles[map_x][map_y].explored = True
                    elif self.map.tiles[map_x][map_y].explored:
                        libtcod.console_set_char_background(con, x, y, tt.bg_color, libtcod.BKGND_SET)
                        libtcod.console_set_default_foreground(con, tt.fg_color)
                        libtcod.console_put_char(con, x, y, tt.char, libtcod.BKGND_NONE)

                    else:
                        libtcod.console_set_char_background(con, x, y, void_color, libtcod.BKGND_SET)
                        libtcod.console_put_char(con, x, y, ' ', libtcod.BKGND_NONE)

                else:
                    libtcod.console_set_char_background(con, x, y, void_color, libtcod.BKGND_SET)
                    libtcod.console_put_char(con, x, y, ' ', libtcod.BKGND_NONE)
                
        for object in map.objects:
            object.draw(con, self.x_offset, self.y_offset)
        
        libtcod.console_blit(con, 0, 0, self.width, self.height, 0, 0, 0)
        libtcod.console_flush()
        
class Object:
    def __init__(self, map, x, y, char, name, blocks=False, color=None):
        """
        Fill with defaults
        """
        self.map = map
        self.name = name        
        map.add_object(self)
        self.x = x
        self.y = y
        self.char = char
        self.color = color or libtcod.white
        self.blocks = blocks
       
    def draw(self, con, x_off, y_off):
        if libtcod.map_is_in_fov(self.map.fov_map, self.x, self.y):
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
        

