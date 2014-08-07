import libtcod.libtcodpy as libtcod

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 25
LIMIT_FPS = 20

libtcod.console_set_custom_font('consolas_unicode_10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)

libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'rbowl', False)
libtcod.sys_set_fps(LIMIT_FPS)

while not libtcod.console_is_window_closed():
	break