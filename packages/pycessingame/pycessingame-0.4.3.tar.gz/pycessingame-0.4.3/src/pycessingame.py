# -----------------------------------------------------------------------------
# This is free and unencumbered software released into the public domain.
#
# Anyone is free to copy, modify, publish, use, compile, sell, or distribute
# this software, either in source code form or as a compiled binary, for any
# purpose, commercial or non-commercial, and by any means.
#
# In jurisdictions that recognize copyright laws, the author or authors of this
# software dedicate any and all copyright interest in the software to the
# public domain. We make this dedication for the benefit of the public at large
# and to the detriment of our heirs and successors. We intend this dedication
# to be an overt act of relinquishment in perpetuity of all present and future
# rights to this software under copyright law.
#
# OPTIONAL ATTRIBUTION:
# Credit to E. Luttmann is appreciated but not required.
#
# For more information, please refer to <https://unlicense.org>
# -----------------------------------------------------------------------------
"""
pycessingame.py

V0.4.3

PROCESSING like API implemented for PYTHON only using pygame.

Features:
  - implementing lots of the processing API (already)
  - camelCase/snake_case support for variables and functions
  - getPressed(<key>) / get_pressed(<key>) function to query any <key> at any time
  - as color values now strings with web-style-hexcodes "#ff5802" or "#f00" are accepted
  - furthermore named colors can be used (https://www.w3.org/TR/SVG11/types.html#ColorKeywords)
    as constant or string - e.g. RED, DARKBLUE  
  - the processing function get() & set() are renamed to
    getPixel() and setPixel() to prevent name conflict.
    
FIXME:
  #todo: name conflict with function random and a module named random
  #todo: name conflict with function set and python type set
  #todo: is exit() also a name conflict?
  #todo: implement _blend_mode, _shape_mode
  #todo: why is _P.surface.blit(surf, rect.topleft) at the end of text(
  
Prerequisites:
  - pygame must be installed (in case it is missing: "pip install pygame")

Usage:
    import pycessingame 

    def setup():
        size(640, 480)
        frameRate(60)

    def draw():
        background(30, 120, 200)
        fill(255, 200, 0)
        stroke(255)
        strokeWeight(4)
        ellipse(width/2, height/2, 150, 150)

    run()
"""

# -------------------------- Imports --------------------------

import sys
import colorsys
import time
import math
import __main__
import re
import datetime
import threading
import functools
import pygame
import random as _pyrandom
import types
import builtins
import numbers

# -------------------------- Constants --------------------------

_CONSTANTS = {
    'LEFT' : 'LEFT',
    'RIGHT' : 'RIGHT',
    'CENTER' : 'CENTER',
    'TOP' : 'TOP',
    'BOTTOM': 'BOTTOM',
    'BASELINE': 'BASELINE',
    'PI' : math.pi,
    'TWO_PI' : 2*math.pi,
    'TAU' : 2*math.pi,
    'HALF_PI' : math.pi/2,
    'QUARTER_PI' : math.pi/4,
    'DEGREES' : 180.0 / math.pi,
    'RADIANS' : math.pi / 180.0,
    'CORNER' : 'CORNER',
    'RADIUS' : 'RADIUS',
    'CORNERS' : 'CORNERS',
    'RGB' : 'RGB',
    'HSB' : 'HSB',
    'BLEND': 'BLEND',
    'ADD': 'ADD',
    'MULTIPLY': 'MULTIPLY',
    'SCREEN': 'SCREEN',
}

ARROW = "ARROW"
CROSS = "CROSS"
HAND = "HAND"
MOVE = "MOVE"
WAIT = "WAIT"
_CURSOR_CONSTANTS = {ARROW, CROSS, HAND, MOVE, WAIT}

_keycode_map = {
    pygame.K_LEFT:      "LEFT",
    pygame.K_RIGHT:     "RIGHT",
    pygame.K_UP:        "UP",
    pygame.K_DOWN:      "DOWN",

    pygame.K_RETURN:    "ENTER",
    pygame.K_KP_ENTER:  "ENTER",
    pygame.K_BACKSPACE: "BACKSPACE",
    pygame.K_TAB:       "TAB",
    pygame.K_ESCAPE:    "ESC",
    pygame.K_DELETE:    "DELETE",
    pygame.K_HOME:      "HOME",
    pygame.K_END:       "END",
    pygame.K_PAGEUP:    "PAGE_UP",
    pygame.K_PAGEDOWN:  "PAGE_DOWN",
    pygame.K_CAPSLOCK: "CAPSLOCK",
    pygame.K_INSERT:   "INSERT",
    
    pygame.K_LSHIFT:    "SHIFT",
    pygame.K_RSHIFT:    "SHIFT",
    pygame.K_LCTRL:     "CONTROL",
    pygame.K_RCTRL:     "CONTROL",
    pygame.K_LALT:      "ALT",
    pygame.K_RALT:      "ALT",

    pygame.K_F1: "F1",  pygame.K_F2: "F2",  pygame.K_F3: "F3",
    pygame.K_F4: "F4",  pygame.K_F5: "F5",  pygame.K_F6: "F6",
    pygame.K_F7: "F7",  pygame.K_F8: "F8",  pygame.K_F9: "F9",
    pygame.K_F10:"F10", pygame.K_F11:"F11", pygame.K_F12:"F12",
}


_PROCESSING_KEY_CONSTANTS = {
    "LEFT", "RIGHT", "UP", "DOWN",
    "ENTER", "RETURN", "BACKSPACE", "TAB", "ESC", "DELETE",
    "SHIFT", "CONTROL", "ALT",
    "HOME", "END", "PAGE_UP", "PAGE_DOWN",
    "F1","F2","F3","F4","F5","F6",
    "F7","F8","F9","F10","F11","F12"
}

_NAMED_COLORS = {
    "ALICEBLUE":[240,248,255,255],"ANTIQUEWHITE":[250,235,215,255],"AQUA":[0,255,255,255],
    "AQUAMARINE":[127,255,212,255],"AZURE":[240,255,255,255],"BEIGE":[245,245,220,255],
    "BISQUE":[255,228,196,255],"BLACK":[0,0,0,255],"BLANCHEDALMOND":[255,235,205,255],
    "BLUE":[0,0,255,255],"BLUEVIOLET":[138,43,226,255],"BROWN":[165,42,42,255],
    "BURLYWOOD":[222,184,135,255],"CADETBLUE":[95,158,160,255],"CHARTREUSE":[127,255,0,255],
    "CHOCOLATE":[210,105,30,255],"CORAL":[255,127,80,255],"CORNFLOWERBLUE":[100,149,237,255],
    "CORNSILK":[255,248,220,255],"CRIMSON":[220,20,60,255],"CYAN":[0,255,255,255],
    "DARKBLUE":[0,0,139,255],"DARKCYAN":[0,139,139,255],"DARKGOLDENROD":[184,134,11,255],
    "DARKGRAY":[169,169,169,255],"DARKGREEN":[0,100,0,255],"DARKGREY":[169,169,169,255],
    "DARKKHAKI":[189,183,107,255],"DARKMAGENTA":[139,0,139,255],"DARKOLIVEGREEN":[85,107,47,255],
    "DARKORANGE":[255,140,0,255],"DARKORCHID":[153,50,204,255],"DARKRED":[139,0,0,255],
    "DARKSALMON":[233,150,122,255],"DARKSEAGREEN":[143,188,143,255],"DARKSLATEBLUE":[72,61,139,255],
    "DARKSLATEGRAY":[47,79,79,255],"DARKSLATEGREY":[47,79,79,255],"DARKTURQUOISE":[0,206,209,255],
    "DARKVIOLET":[148,0,211,255],"DEEPPINK":[255,20,147,255],"DEEPSKYBLUE":[0,191,255,255],
    "DIMGRAY":[105,105,105,255],"DIMGREY":[105,105,105,255],"DODGERBLUE":[30,144,255,255],
    "FIREBRICK":[178,34,34,255],"FLORALWHITE":[255,250,240,255],"FORESTGREEN":[34,139,34,255],
    "FUCHSIA":[255,0,255,255],"GAINSBORO":[220,220,220,255],"GHOSTWHITE":[248,248,255,255],
    "GOLD":[255,215,0,255],"GOLDENROD":[218,165,32,255],"GRAY":[128,128,128,255],
    "GREY":[128,128,128,255],"GREEN":[0,128,0,255],"GREENYELLOW":[173,255,47,255],
    "HONEYDEW":[240,255,240,255],"HOTPINK":[255,105,180,255],"INDIANRED":[205,92,92,255],
    "INDIGO":[75,0,130,255],"IVORY":[255,255,240,255],"KHAKI":[240,230,140,255],
    "LAVENDER":[230,230,250,255],"LAVENDERBLUSH":[255,240,245,255],"LAWNGREEN":[124,252,0,255],
    "LEMONCHIFFON":[255,250,205,255],"LIGHTBLUE":[173,216,230,255],"LIGHTCORAL":[240,128,128,255],
    "LIGHTCYAN":[224,255,255,255],"LIGHTGOLDENRODYELLOW":[250,250,210,255],"LIGHTGRAY":[211,211,211,255],
    "LIGHTGREEN":[144,238,144,255],"LIGHTGREY":[211,211,211,255],"LIGHTPINK":[255,182,193,255],
    "LIGHTSALMON":[255,160,122,255],"LIGHTSEAGREEN":[32,178,170,255],"LIGHTSKYBLUE":[135,206,250,255],
    "LIGHTSLATEGRAY":[119,136,153,255],"LIGHTSLATEGREY":[119,136,153,255],"LIGHTSTEELBLUE":[176,196,222,255],
    "LIGHTYELLOW":[255,255,224,255],"LIME":[0,255,0,255],"LIMEGREEN":[50,205,50,255],
    "LINEN":[250,240,230,255],"MAGENTA":[255,0,255,255],"MAROON":[128,0,0,255],
    "MEDIUMAQUAMARINE":[102,205,170,255],"MEDIUMBLUE":[0,0,205,255],"MEDIUMORCHID":[186,85,211,255],
    "MEDIUMPURPLE":[147,112,219,255],"MEDIUMSEAGREEN":[60,179,113,255],"MEDIUMSLATEBLUE":[123,104,238,255],
    "MEDIUMSPRINGGREEN":[0,250,154,255],"MEDIUMTURQUOISE":[72,209,204,255],"MEDIUMVIOLETRED":[199,21,133,255],
    "MIDNIGHTBLUE":[25,25,112,255],"MINTCREAM":[245,255,250,255],"MISTYROSE":[255,228,225,255],
    "MOCCASIN":[255,228,181,255],"NAVAJOWHITE":[255,222,173,255],"NAVY":[0,0,128,255],
    "OLDLACE":[253,245,230,255],"OLIVE":[128,128,0,255],"OLIVEDRAB":[107,142,35,255],
    "ORANGE":[255,165,0,255],"ORANGERED":[255,69,0,255],"ORCHID":[218,112,214,255],
    "PALEGOLDENROD":[238,232,170,255],"PALEGREEN":[152,251,152,255],"PALETURQUOISE":[175,238,238,255],
    "PALEVIOLETRED":[219,112,147,255],"PAPAYAWHIP":[255,239,213,255],"PEACHPUFF":[255,218,185,255],
    "PERU":[205,133,63,255],"PINK":[255,192,203,255],"PLUM":[221,160,221,255],
    "POWDERBLUE":[176,224,230,255],"PURPLE":[128,0,128,255],"RED":[255,0,0,255],
    "ROSYBROWN":[188,143,143,255],"ROYALBLUE":[65,105,225,255],"SADDLEBROWN":[139,69,19,255],
    "SALMON":[250,128,114,255],"SANDYBROWN":[244,164,96,255],"SEAGREEN":[46,139,87,255],
    "SEASHELL":[255,245,238,255],"SIENNA":[160,82,45,255],"SILVER":[192,192,192,255],
    "SKYBLUE":[135,206,235,255],"SLATEBLUE":[106,90,205,255],"SLATEGRAY":[112,128,144,255],
    "SLATEGREY":[112,128,144,255],"SNOW":[255,250,250,255],"SPRINGGREEN":[0,255,127,255],
    "STEELBLUE":[70,130,180,255],"TAN":[210,180,140,255],"TEAL":[0,128,128,255],
    "THISTLE":[216,191,216,255],"TOMATO":[255,99,71,255],"TURQUOISE":[64,224,208,255],
    "VIOLET":[238,130,238,255],"WHEAT":[245,222,179,255],"WHITE":[255,255,255,255],
    "WHITESMOKE":[245,245,245,255],"YELLOW":[255,255,0,255],"YELLOWGREEN":[154,205,50,255]
}


# ------- Function Handle for overloaded function -----------

_python_map = builtins.map

# ------- decorations -----------

DEBUG_THREADS = True

def _mainthread_only(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        if DEBUG_THREADS:
            if threading.current_thread() is not threading.main_thread():
                raise RuntimeError(
                    f"{fn.__name__}() must not be called from thread()"
                )
        return fn(*args, **kwargs)
    return wrapper

# -------------------------- API Functions --------------------------

def exit():
    """
    Stops the sketch immediately.

    Equivalent to Processing exit().
    Terminates the main loop and closes the window.
    """
    _P._running = False

def map(*args):
    """
    Maps a value from one range to another.

    Usage:
        map(value, start1, stop1, start2, stop2)

    Returns:
        float: Mapped value.

    Notes:
        - If called with other arguments, behaves like Python's map().
    """
    if len(args) == 5 and all(isinstance(x, numbers.Real) for x in args):
        value, start1, stop1, start2, stop2 = args
        if start1 == stop1:
            raise ValueError("map() input range must not be zero")
        return start2 + (stop2 - start2) * ((value - start1) / (stop1 - start1))

    return _python_map(*args)

def getPressed(key=None):
    """
    Checks whether a key is currently pressed.

    Parameters:
        key (optional):
            - None: checks if any key is pressed
            - str: character or special key constant

    Returns:
        bool: True if the key is pressed.
    """
    # Any key?
    if key is None:
        return bool(_P._keys_down)

    # Normalize
    if isinstance(key, str):
        key = key.upper() if len(key) > 1 else key

    return key in _P._keys_down

@_mainthread_only
def noLoop():
    """
    Stops automatic execution of draw().

    draw() will only be executed again via redraw().
    """
    _P._looping = False

@_mainthread_only
def loop():
    """
    Resumes automatic execution of draw().

    Notes:
        - Has no effect if draw() is not defined.
    """
    if _P._draw_exists:
        _P._looping = True

def delay(ms):
    """
    Pauses the sketch for a given amount of time.

    Processing-compatible delay().

    Parameters:
        ms (int or float):
            Time to pause in milliseconds.

    Notes:
        - Blocks execution of draw() and event handling logic.
        - The window remains responsive during the delay.
        - delay() should be used sparingly, as it freezes animation.
    """
    end = time.time() + ms / 1000.0
    while time.time() < end and _P._running:
        pygame.event.pump()   # Fenster bleibt responsive
        time.sleep(0.001)

def thread(target, *args, **kwargs):
    """
    Runs a function in a separate thread.

    Processing-compatible thread(), extended for Python.

    Parameters:
        target (str or callable):
            - str      : name of a global function (Processing style)
            - callable : function object (Python style)
        *args:
            Positional arguments passed to the function.
        **kwargs:
            Keyword arguments passed to the function.

    Notes:
        - The function is executed asynchronously.
        - The return value is ignored.
        - Drawing functions MUST NOT be called from within the thread.
        - Threads are started as daemon threads and cannot be joined.
    """
    # --------------------------------------------------
    # Resolve function
    # --------------------------------------------------
    if isinstance(target, str):
        fn = getattr(__main__, target, None)
        if fn is None or not callable(fn):
            raise ValueError(f"thread(): function '{target}' not found")

    elif callable(target):
        fn = target

    else:
        raise TypeError(
            "thread(): target must be a function or function name (str)"
        )

    # --------------------------------------------------
    # Start thread
    # --------------------------------------------------
    t = threading.Thread(
        target=_thread_wrapper,
        args=(fn, args, kwargs),
        daemon=True
    )
    t.start()

@_mainthread_only
def redraw():
    """
    Forces draw() to run once.

    Notes:
        - Works even if noLoop() is active.
    """
    if _P._draw_exists:
        _P._draw_next_frame = True
    
def random(*args):
    """
    Processing-compatible random() function.

    Usage:
    random() -> float 0..1
    random(high) -> float 0..high
    random(low, high) -> float low..high
    """
    if len(args) == 0:
        # Processing: random() without args → returns a float between 0 and 1
        return _pyrandom.random()

    if len(args) == 1:
        high = args[0]
        return _pyrandom.random() * high

    if len(args) == 2:
        low, high = args
        return low + _pyrandom.random() * (high - low)

    raise TypeError("random() takes 0, 1 or 2 arguments")

def randomSeed(v):
    """
    Sets the seed for the random number generator.

    Parameters:
        v (int): Seed value.
    """
    _pyrandom.seed(v)
    
def randomGaussian():
    """
    Returns a normally distributed random number.

    Returns:
        float:
            Gaussian-distributed value with mean 0
            and standard deviation 1.
    """
    u1 = 1.0 - _pyrandom.random()
    u2 = 1.0 - _pyrandom.random()
    return ( (-2 * math.log(u1)) ** 0.5 ) * math.cos(2 * math.pi * u2 )

def millis():
    """
    Returns the number of milliseconds since the sketch started.

    Returns:
        int: Milliseconds since run() was called.
    """
    if _P._last_time_global is None:
        return 0
    return int((time.time() - _P._last_time_global) * 1000)

def second():
    """Return current second 0–59."""
    return datetime.datetime.now().second

def minute():
    """Return current minute 0–59."""
    return datetime.datetime.now().minute

def hour():
    """Return current hour 0–23."""
    return datetime.datetime.now().hour

def day():
    """Return day of month 1–31."""
    return datetime.datetime.now().day

def month():
    """Return month 1–12."""
    return datetime.datetime.now().month

def year():
    """Return full year (e.g. 2025)."""
    return datetime.datetime.now().year

def weekday():
    """
    Monday=1 ... Sunday=7
    (Processing hat das nicht, aber viele wollen es)
    """
    return datetime.datetime.now().isoweekday()

def timestamp():
    """
    Returns UNIX timestamp as int.
    (Zusatzfunktion – optional)
    """
    return int(time.time())

@_mainthread_only
def textAlign(h, v='BASELINE'):
    """
    Sets horizontal and vertical text alignment.

    Parameters:
        h (str):
            Horizontal alignment:
            'LEFT', 'CENTER', or 'RIGHT'
        v (str, optional):
            Vertical alignment:
            'TOP', 'CENTER', 'BOTTOM', or 'BASELINE'

    Notes:
        - Affects subsequent text() calls.
        - BASELINE aligns text using the font ascent.
    """
    h = h.upper()
    v = v.upper()

    if h not in ('LEFT', 'CENTER', 'RIGHT'):
        raise ValueError("textAlign(): invalid horizontal alignment")

    if v not in ('TOP', 'CENTER', 'BOTTOM', 'BASELINE'):
        raise ValueError("textAlign(): invalid vertical alignment")

    _P._text_align_x,_P._text_align_y  = h, v

@_mainthread_only
def textLeading(leading):
    """
    Sets the spacing between lines of multi-line text.

    Parameters:
        leading (int or float):
            Distance in pixels between text lines.

    Notes:
        - Only affects multi-line text (with '\\n').
        - If not set, the font's default line height is used.
    """
    _P._text_leading = int(leading)

@_mainthread_only
def textFont(font, size=None):
    """
    Sets the current font for text rendering.

    Parameters:
        font:
            - PFont object
            - Font name (str)
            - pygame.font.Font instance
        size (int or float, optional):
            Font size in pixels.

    Notes:
        - If size is omitted, the font's default size is used.
        - The font is cached internally for performance.
    """
    if isinstance(font, PFont):
        _P._font_source = font.source
    elif isinstance(font, pygame.font.Font):
        _P._font_source = font
    elif isinstance(font, str):
        _P._font_source = font
    else:
        _P._font_source = pygame.font.get_default_font()
    if size is not None:
        _P._font_size = int(size)

def createFont(name, size=16, smooth=True):
    """
    Creates a font descriptor.

    Parameters:
        name (str):
            Font name or path to a .ttf/.otf file.
        size (int):
            Default font size.
        smooth (bool):
            Ignored (pygame always renders anti-aliased fonts).

    Returns:
        PFont:
            A Processing-compatible font object.
    """
    if not isinstance(name, str):
        raise TypeError("createFont(): name must be a string")

    return PFont(name, size)

def loadFont(path):
    """
    Loads a font from a file.

    Parameters:
        path (str):
            Path to a .ttf or .otf font file.

    Returns:
        PFont:
            A font descriptor usable with textFont().
    """
    if not isinstance(path, str):
        raise TypeError("loadFont(): path must be a string")

    return PFont(path)

@_mainthread_only
def text(txt, x, y):
    """
    Draws text to the canvas.

    Parameters:
        txt: Text to display. Will be converted to string.
        x, y: Position of the text anchor.

    Notes:
        - Multi-line text is supported using '\\n'.
        - Text rendering uses the current fill color.
        - Text is affected by translate(), rotate(), and scale().
        - Alignment is controlled via textAlign().
        - Text is not drawn if noFill() is active.
    """
    if not _P._use_fill:
        return

    font = _P._get_font()
    lines = str(txt).split('\n')

    h_align, v_align = _P._text_align_x, _P._text_align_y
    
#    leading = _P._text_leading , font.get_height()
    leading = _P._text_leading if not _P._text_leading == None else font.get_height()

    for i, line in enumerate(lines):
        color = _P._fill_color[:3] if getattr(_P, "_fill_color", None) else (255, 255, 255)
        text_surf = font.render(line, True, color)  

        w, h = text_surf.get_size()

        # Alignment
        ox = 0
        if h_align == 'CENTER':
            ox = -w / 2
        elif h_align == 'RIGHT':
            ox = -w

        oy = i * leading
        if v_align == 'CENTER':
            oy -= (len(lines) - 1) * leading / 2
        elif v_align == 'BOTTOM':
            oy -= (len(lines) - 1) * leading
        elif v_align == 'BASELINE':
            oy -= font.get_ascent()

        # === Transformation ===
        # Lokaler Ursprung
        px, py = _transform_point(_P._matrix, x + ox, y + oy)

        # Rotation + Scale aus Matrix extrahieren
        angle, scale = _extract_rotation_scale(_P._matrix)

        surf = text_surf
    #        surf = pygame.Surface((w, h), pygame.SRCALPHA)
    #        surf.fill((0,0,0,0))  # komplett transparent
    #        surf.blit(text_surf, (0,0))
        if scale != 1:
            surf = pygame.transform.scale(
                surf,
                (max(1, int(w * scale)), max(1, int(h * scale)))
            )

        if angle != 0:
            surf = pygame.transform.rotate(surf, -math.degrees(angle))

        rect = surf.get_rect()
        rect.center = (px, py)
#        _P.surface.blit(surf, rect.topleft)
        _P.surface.blit(surf, (px, py))

def textAscent():
    """
    Returns the ascent of the current font.

    Returns:
        int:
            The distance from baseline to the top of the tallest glyph.
    """
    return _P._get_font().get_ascent()

def textDescent():
    """
    Returns the descent of the current font.

    Returns:
        int:
            The distance from baseline to the bottom of the lowest glyph.
    """
    return abs(_P._get_font().get_descent())

@_mainthread_only
def textWidth(txt):
    """
    Returns the width of a text string in pixels.

    Parameters:
        txt: Text to measure.

    Returns:
        int:
            Width of the rendered text using the current font.
    """
    font = _P._get_font()
    return font.size(str(txt))[0]

@_mainthread_only
def textSize(size=None):
    """
    Sets or resets the current text size.

    Parameters:
        size (int or float, optional):
            Font size in pixels.
            If None, resets text leading to font default.

    Notes:
        - Changing the size clears the internal font cache.
        - Also updates textLeading() automatically.
    """
    if size:
        _P._font_size = int(size)
    #FIXME    _P._font = _P._get_font()
        _P._font = None
        _P._text_leading = int(size * 1.2)
    else:
        _P._text_leading = None

@_mainthread_only
def size(w, h):
    """
    Sets the size of the sketch window.

    Parameters:
        w, h: Width and height in pixels.

    Notes:
        - Must be called before drawing.
        - Recreates the drawing surface.
    """
    _P.width = int(w)
    _P.height = int(h)
    if not pygame.get_init():
        _init()
    else:
        pygame.display.set_mode((_P.width, _P.height))
        _P.surface = pygame.Surface((_P.width,_P.height), pygame.SRCALPHA)
        background(_P._background_color)

@_mainthread_only
def windowTitle(title):
    """
    Sets the window title.

    Parameters:
        title (str): Title text.
    """
    _P._window_title = str(title)
    try:
        pygame.display.set_caption(_P._window_title)
    except Exception:
        pass

@_mainthread_only
def smooth():
    """Enable anti-aliasing where supported."""
    _P._smooth = True

@_mainthread_only
def noSmooth():
    """Disable all anti-aliasing."""
    _P._smooth = False

@_mainthread_only
def noCursor():
    """
    Hides the mouse cursor.
    """
    _P._cursor_visible = False
    _P._cursor_image = None
    _P._cursor_mode = None
    try:
        pygame.mouse.set_visible(False)
    except Exception:
        pass

@_mainthread_only
def cursor(mode_or_img=None, x=None, y=None):
    """
    Sets the mouse cursor.

    Parameters:
        mode_or_img:
            - None: default arrow cursor
            - str: cursor mode (ARROW, HAND, etc.)
            - pygame.Surface: custom cursor image
        x, y: Hotspot for custom cursor.
    """
    # ------------------------------
    # CASE 1: cursor()  → default arrow
    # ------------------------------
    if mode_or_img is None:
        _P._cursor_visible = True
        _P._cursor_mode = ARROW
        _P._cursor_image = None

        try:
            pygame.mouse.set_visible(True)
            pygame.mouse.set_cursor(pygame.Cursor(pygame.SYSTEM_CURSOR_ARROW))
        except Exception:
            pass

        return

    # ------------------------------
    # CASE 2: cursor(img, x, y) → custom image
    # (img = pygame.Surface)
    # ------------------------------
    if isinstance(mode_or_img, pygame.Surface):
        img = mode_or_img
        hx = int(x or 0)
        hy = int(y or 0)

        _P._cursor_visible = True
        _P._cursor_image = img
        _P._cursor_hotspot = (hx, hy)
        _P._cursor_mode = None  # disable system cursor modes

        try:
            pygame.mouse.set_visible(True)
            # Pygame cannot use ARGB images as real cursors → so fake minimal cursor
            pygame.mouse.set_cursor(
                pygame.Cursor(
                    (img.get_width(), img.get_height()),
                    (hx, hy),
                    pygame.cursors.compile(['X'], black='X')
                )
            )
        except Exception:
            pass

        return

    # ------------------------------
    # CASE 3: cursor(MODE)
    # mode is a string: ARROW, CROSS, HAND, MOVE, WAIT
    # ------------------------------
    if isinstance(mode_or_img, str):
        mode = mode_or_img.upper()

        if mode not in _CURSOR_CONSTANTS:
            raise ValueError(f"cursor(): unknown mode '{mode}'")

        _P._cursor_visible = True
        _P._cursor_mode = mode
        _P._cursor_image = None  # disable custom img cursor

        pygame_cursor_map = {
            ARROW: pygame.SYSTEM_CURSOR_ARROW,
            CROSS: pygame.SYSTEM_CURSOR_CROSSHAIR,
            HAND: pygame.SYSTEM_CURSOR_HAND,
            MOVE: pygame.SYSTEM_CURSOR_SIZEALL,
            WAIT: pygame.SYSTEM_CURSOR_WAIT,
        }

        try:
            pygame.mouse.set_visible(True)
            pygame.mouse.set_cursor(pygame.Cursor(pygame_cursor_map[mode]))
        except Exception:
            pass

        return

    # ------------------------------
    # Anything else is invalid
    # ------------------------------
    raise TypeError("cursor(): expected None, str mode, or pygame.Surface image")

@_mainthread_only
def frameRate(f):
    """
    Sets the target frame rate.

    Parameters:
        f (float): Desired frames per second.

    Notes:
        - This sets the target, not the measured frame rate.
        - The actual frameRate variable reflects measured FPS.
    """
    try:
        f = float(f)
    except (TypeError, ValueError):
        return

    if f <= 0:
        return

    _P._target_fps = f

@_mainthread_only
def colorMode(mode, *args):
    mode = mode.upper()
    if mode not in (_CONSTANTS['RGB'], _CONSTANTS['HSB']):
        raise ValueError("colorMode(): invalid mode")

    _P._color_mode = mode

    # --- Defaults ---
    if not args:
        _P._color_max = (
            [255,255,255,255] if mode == _CONSTANTS['RGB']
            else [360,100,100,100]
        )
        return

    # --- colorMode(mode, max) ---
    if len(args) == 1:
        m = args[0]
        _P._color_max = [m, m, m, m]
        return

    # --- colorMode(mode, x, y, z) ---
    if len(args) == 3:
        _P._color_max = [args[0], args[1], args[2], 255]
        return

    # --- colorMode(mode, x, y, z, a) ---
    if len(args) == 4:
        _P._color_max = list(args)
        return

    raise TypeError("colorMode() accepts 1, 2, 4 or 5 arguments")

def color(*args):
    """
    Processing-konforme color() Funktion.
    - RGB oder HSB, abhängig von _P._color_mode
    - Graustufen unterstützung
    - Alpha optional
    - HSB: Hue wird gewrappt
    """
    # Unpack single tuple/list
    while len(args) == 1 and isinstance(args[0], (tuple, list)):
        args = tuple(args[0])

    n = len(args)

    if n == 1:
        if isinstance(args[0], str):
            comps = stringToColor(args[0])
        else:
            comps = [args[0], args[0], args[0], _P._color_max[3]]
    elif n == 2:
        comps = [args[0], args[0], args[0], args[1]]
    elif n == 3:
        comps = [args[0], args[1], args[2], _P._color_max[3]]
    elif n == 4:
        comps = list(args)
    else:
        raise TypeError("color() accepts 1–4 arguments")

    # --- normalize via colorMode scales ---
    max_vals = _P._color_max
    norm = [0 if maxv == 0 else comps[i]/max_vals[i] for i, maxv in enumerate(max_vals)]

    if _P._color_mode == _CONSTANTS['HSB']:
        # Hue wrap-around wie Processing: Hue % 1.0
        h = norm[0] % 1.0
        s = min(max(norm[1], 0), 1)
        v = min(max(norm[2], 0), 1)

        r, g, b = [int(c*255) for c in colorsys.hsv_to_rgb(h, s, v)]
    else:
        r, g, b = [min(max(int(n*255), 0), 255) for n in norm[:3]]

    a = min(max(int(norm[3]*255), 0), 255)
    return (r, g, b, a)

def stringToColor(c):
    c = c.upper()
    if c in _NAMED_COLORS:
        return _NAMED_COLORS[c]
    hexPattern = re.compile(r'^#([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})$')
    m = re.match(hexPattern, c) 
    if m:
        return [int(m.group(1),16), int(m.group(2),16), int(m.group(3),16),255]
    else:
        hexPattern = re.compile(r'^#([0-9a-fA-F])([0-9a-fA-F])([0-9a-fA-F])$')
        m = re.match(hexPattern, c)
        if m:
            return [17*int(m.group(1),16), 17*int(m.group(2),16), 17*int(m.group(3),16),255]
    raise ValueError("string_to_color(): Unknown color '"+c+"'. Use format '#6398f3' or '#f27' or see https://www.w3.org/TR/SVG11/types.html#ColorKeywords for named colors.")

def alpha(c):
    return _as_rgba(c)[3]

def red(c):
    return _as_rgba(c)[0]

def green(c):
    return _as_rgba(c)[1]

def blue(c):
    return _as_rgba(c)[2]


def hue(c):
    r, g, b, _ = _as_rgba(c)
    h, _, _ = _rgb_to_hsb_scaled(r, g, b)
    return h

def saturation(c):
    r, g, b, _ = _as_rgba(c)
    _, s, _ = _rgb_to_hsb_scaled(r, g, b)
    return s

def brightness(c):
    r, g, b, _ = _as_rgba(c)
    _, _, v = _rgb_to_hsb_scaled(r, g, b)
    return v

def lerpColor(c1, c2, amt):
    """
    Linearly interpolates between two colors.
    Processing-compatible implementation.

    Parameters:
        c1, c2 : color tuples (r, g, b) or (r, g, b, a)
        amt    : interpolation amount (float)

    Returns:
        (r, g, b, a) tuple
    """
    if _P._color_mode == _CONSTANTS['HSB']:
        max_h, max_s, max_b = _P._color_max[:3]
        h1, s1, b1 = _rgb_to_hsb_scaled(*_as_rgba(c1)[:3])
        h2, s2, b2 = _rgb_to_hsb_scaled(*_as_rgba(c2)[:3])

        def _lerp_hue(h1, h2, t, max_h):
            """Interpolate hue on a circle (0..max_h) correctly."""
            delta = (h2 - h1) % max_h
            if delta > max_h / 2:
                delta -= max_h  # take shorter path
            h = (h1 + delta * t) % max_h
            return h

        h = _lerp_hue(h1, h2, amt, max_h)
        s = s1 + (s2 - s1) * amt
        b = b1 + (b2 - b1) * amt

        return color(h, s, b)
    else:    
        if c1 is None or c2 is None:
            raise ValueError("lerpColor(): colors must not be None")

        # Normalize colors to RGBA
        if len(c1) == 3:
            r1, g1, b1 = c1
            a1 = 255
        elif len(c1) == 4:
            r1, g1, b1, a1 = c1
        else:
            raise ValueError("lerpColor(): invalid color c1")

        if len(c2) == 3:
            r2, g2, b2 = c2
            a2 = 255
        elif len(c2) == 4:
            r2, g2, b2, a2 = c2
        else:
            raise ValueError("lerpColor(): invalid color c2")

        def lerp(a, b, t):
            return a + (b - a) * t

        r = int(lerp(r1, r2, amt))
        g = int(lerp(g1, g2, amt))
        b = int(lerp(b1, b2, amt))
        a = int(lerp(a1, a2, amt))

        # Clamp like Processing's internal color storage
        def clamp(v):
            return max(0, min(255, v))

        return (clamp(r), clamp(g), clamp(b), clamp(a),)

@_mainthread_only
def background(*args):
    """
    Sets the background color of the sketch window.

    Parameters:
        args: Same arguments as color()
              - gray
              - gray, alpha
              - r, g, b
              - r, g, b, a

    Notes:
        - Clears the entire drawing surface.
        - Alpha values < 255 allow transparent backgrounds.
        - Must be called after size().
    """
    col4 = color(*args)
    if _P.surface is None:
        return
    if col4[3]<255:
        tmp = pygame.Surface((_P.width,_P.height), pygame.SRCALPHA)
        tmp.fill(col4)
        _P.surface.blit(tmp,(0,0))
    else:
        _P.surface.fill(col4[:3])

@_mainthread_only
def clear():
    """
    Clears the drawing surface to full transparency.

    Equivalent to Processing clear().
    Only affects the offscreen surface, not the window itself.
    """
    if _P.surface:
        _P.surface.fill((0,0,0,0))

@_mainthread_only
def fill(*args):
    """
    Sets the fill color for shapes.

    Parameters:
        args: Same arguments as color().

    Notes:
        - Affects all subsequent shapes.
        - Can be disabled using noFill().
    """
    if len(args)==0:
        return
    _P._fill_color = color(*args)
    _P._use_fill = True

@_mainthread_only
def noFill():
    """
    Disables filling geometry.

    Shapes will only be drawn with stroke (if enabled).
    """
    _P._use_fill = False

@_mainthread_only
def stroke(*args):
    """
    Sets the stroke (outline) color for shapes.

    Parameters:
        args: Same arguments as color().

    Notes:
        - Affects lines, outlines, and points.
        - Can be disabled using noStroke().
    """
    if len(args)==0:
        return
    _P._stroke_color = color(*args)
    _P._use_stroke = True

@_mainthread_only
def noStroke():
    """
    Disables drawing of strokes (outlines).

    Shapes will only be filled (if fill is enabled).
    """
    _P._use_stroke = False

@_mainthread_only
def strokeWeight(w):
    """
    Sets the thickness of strokes.

    Parameters:
        w (int or float): Stroke thickness in pixels.
                          Minimum is 1 pixel.
    """
    _P._stroke_weight = max(1,int(w))
    
@_mainthread_only
def rectMode(mode):
    """
    Setzt den Rechteckmodus.
    Optionen: 'CORNER', 'CORNERS', 'CENTER', 'RADIUS'
    """
    mode = mode.upper()
    if mode not in ('CORNER', 'CORNERS', 'CENTER', 'RADIUS'):
        raise ValueError(f"rectMode(): unknown mode '{mode}'")
    _P._rect_mode = mode

@_mainthread_only
def ellipseMode(mode):
    """
    Setzt den Ellipsenmodus.
    Optionen: 'CORNER', 'CORNERS', 'CENTER', 'RADIUS'
    """
    mode = mode.upper()
    if mode not in ('CORNER', 'CORNERS', 'CENTER', 'RADIUS'):
        raise ValueError(f"ellipseMode(): unknown mode '{mode}'")
    _P._ellipse_mode = mode
        
@_mainthread_only
def rect(x, y, w, h):
    """
    Draws a rectangle.

    Parameters:
        x, y: Position (interpreted according to rectMode()).
        w, h: Width and height.

    Notes:
        - Supports transformations (translate, rotate, scale).
        - Fill and stroke depend on current style settings.
    """
    x, y, w, h = float(x), float(y), float(w), float(h)

    if _P._rect_mode == 'CORNER':
        rx, ry, rw, rh = x, y, w, h
    elif _P._rect_mode == 'CORNERS':
        rx, ry = min(x, w), min(y, h)
        rw, rh = abs(w - x), abs(h - y)
    elif _P._rect_mode == 'CENTER':
        rx = x - w/2
        ry = y - h/2
        rw, rh = w, h
    elif _P._rect_mode == 'RADIUS':
        rx = x - w
        ry = y - h
        rw, rh = w*2, h*2
    else:
        raise ValueError(f"Invalid rectMode: {_P._rect_mode}")

    # Transformiere die Eckpunkte
    x1, y1 = _transform_point(_P._matrix, rx, ry)
    x2, y2 = _transform_point(_P._matrix, rx + w, ry + h)
    rx, ry = min(x1, x2), min(y1, y2)
    rw, rh = abs(x2 - x1), abs(y2 - y1)
    
    r = pygame.Rect(int(rx), int(ry), int(rw), int(rh))
    _apply_fill(_P.surface, pygame.draw.rect, r)
    _apply_stroke(_P.surface, pygame.draw.rect, r)

@_mainthread_only
def ellipse(x, y, w, h):
    """
    Draws an ellipse or circle.

    Parameters:
        x, y: Position (interpreted according to ellipseMode()).
        w, h: Width and height.

    Notes:
        - Use circle() for equal width and height.
        - Supports transformations.
    """
    x, y, w, h = float(x), float(y), float(w), float(h)

    # Transformiere Mittelpunkt
    x, y = _transform_point(_P._matrix, x, y)

    if _P._ellipse_mode == 'CENTER':
        rx, ry = x - w/2, y - h/2
        rw, rh = w, h
    elif _P._ellipse_mode == 'RADIUS':
        rx, ry = x - w, y - h
        rw, rh = w*2, h*2
    elif _P._ellipse_mode == 'CORNER':
        rx, ry, rw, rh = x, y, w, h
    elif _P._ellipse_mode == 'CORNERS':
        rx, ry = min(x, w), min(y, h)
        rw, rh = abs(w - x), abs(h - y)
    else:
        raise ValueError(f"Invalid ellipseMode: {_P._ellipse_mode}")

    rect_ = pygame.Rect(int(rx), int(ry), int(rw), int(rh))
    _apply_fill(_P.surface, pygame.draw.ellipse, rect_)
    _apply_stroke(_P.surface, pygame.draw.ellipse, rect_)

@_mainthread_only
def line(x1, y1, x2, y2):
    """
    Draws a line between two points.

    Parameters:
        x1, y1: Start point.
        x2, y2: End point.

    Notes:
        - Uses stroke color and strokeWeight().
        - Anti-aliased when smooth() is enabled and weight == 1.
    """
    if not _P._use_stroke:
        return

    x1, y1, x2, y2 = _python_map(int, (x1, y1, x2, y2))
    color = _P._stroke_color[:3]

    if _P._smooth and _P._stroke_weight == 1:
        # aaline: Antialias, nur 1px
        pygame.draw.aaline(_P.surface, color, (x1, y1), (x2, y2))
    else:
        # normale Linie, Breite beachten
        pygame.draw.line(_P.surface, color, (x1, y1), (x2, y2), _P._stroke_weight)     

@_mainthread_only
def point(x, y):
    """
    Draws a single point.

    Parameters:
        x, y: Position of the point.

    Notes:
        - Uses the current stroke color.
        - The size of the point depends on strokeWeight().
        - Supports transformations.
    """
    if _P._use_stroke:
        x, y = _transform_point(_P._matrix, x, y)
        pygame.draw.circle(_P.surface,_P._stroke_color[:3],(int(x),int(y)),max(1,_P._stroke_weight)//2)

def circle(cx, cy, r):
    """
    Draws a circle.

    Parameters:
        cx, cy: Center position.
        r: Radius of the circle.

    Notes:
        - Equivalent to ellipse(cx, cy, r*2, r*2).
        - Affected by ellipseMode().
    """
    ellipse(cx,cy,r*2,r*2)
    
@_mainthread_only
def triangle(x1, y1, x2, y2, x3, y3):
    """
    Draws a triangle defined by three points.

    Parameters:
        x1, y1: First vertex.
        x2, y2: Second vertex.
        x3, y3: Third vertex.

    Notes:
        - Supports fill and stroke.
        - Vertices are affected by the current transformation matrix.
    """
    pts = [_transform_point(_P._matrix, *p) for p in [(x1, y1), (x2, y2), (x3, y3)]]
    _apply_fill(_P.surface,pygame.draw.polygon,pts)
    _apply_stroke(_P.surface,pygame.draw.polygon,pts)

def pushStyle():
    """
    Saves the current drawing style.

    Includes:
        - fill / stroke settings
        - colorMode
        - font and text settings
        - shape modes
    """
    _P._style_stack.append({
        "fill_color": _P._fill_color,
        "stroke_color": _P._stroke_color,
        "use_fill": _P._use_fill,
        "use_stroke": _P._use_stroke,
        "stroke_weight": _P._stroke_weight,
        "color_mode": _P._color_mode,
        "color_max": list(_P._color_max),
        "rect_mode": _P._rect_mode,
        "ellipse_mode": _P._ellipse_mode,
#        "font_path": _P._font_path,
        "font_size": _P._font_size,
#        "font": _P._font,
        "font_source": _P._font_source,
        "text_leading": _P._text_leading,
        "text_align_x": _P._text_align_x,
        "text_align_y": _P._text_align_y,
        "smooth": _P._smooth,
        "image_mode": _P._image_mode,
        "tint": _P._tint,
        "blend_mode": _P._blend_mode,
    })
    
def popStyle():
    """
    Restores the most recently saved drawing style.

    Notes:
        - If no style is saved, nothing happens.
    """
    if not _P._style_stack:
        return  # Processing: popStyle() auf leerem Stack → kein Fehler

    s = _P._style_stack.pop()

    _P._fill_color   = s["fill_color"]
    _P._stroke_color = s["stroke_color"]
    _P._use_fill     = s["use_fill"]
    _P._use_stroke   = s["use_stroke"]
    _P._stroke_weight = s["stroke_weight"]
    _P._color_mode   = s["color_mode"]
    _P._color_max    = s["color_max"]
    _P._rect_mode     = s["rect_mode"]
    _P._ellipse_mode  = s["ellipse_mode"]
#    _P._font_path = s['font_path']
    _P._font_size    = s['font_size']
    _P._font_source  = s['font_source']
#    _P._font = s['font']
    _P._text_leading = s['text_leading']
    _P._text_align_x = s["text_align_x"]
    _P._text_align_y = s["text_align_y"]
    _P._smooth       = s["smooth"]
    _P._image_mode   = s["image_mode"]
    _P._tint         = s["tint"]
    _P._blend_mode   = s["blend_mode"]

@_mainthread_only
def pushMatrix():
    """
    Saves the current transformation matrix.

    Must be paired with popMatrix().
    """
    _P._matrix_stack.append([row[:] for row in _P._matrix])

@_mainthread_only
def popMatrix():
    """
    Restores the last saved transformation matrix.

    Notes:
        - If the stack is empty, nothing happens.
    """
    if _P._matrix_stack:
        _P._matrix = _P._matrix_stack.pop()

@_mainthread_only
def translate(tx, ty):
    """
    Translates the coordinate system.

    Parameters:
        tx, ty: Translation offsets.

    Notes:
        - Affects all subsequent drawing operations.
        - Transformations are cumulative.
    """
    m = [[1,0,tx],[0,1,ty],[0,0,1]]
    _P._matrix = _matmul(_P._matrix, m)

@_mainthread_only
def rotate(a):
    """
    Rotates the coordinate system.

    Parameters:
        a (float): Rotation angle in radians.

    Notes:
        - Rotation is applied around the current origin.
    """
    c, s = math.cos(a), math.sin(a)
    m = [[c,-s,0],[s,c,0],[0,0,1]]
    _P._matrix = _matmul(_P._matrix, m)

@_mainthread_only
def scale(sx, sy=None):
    """
    Scales the coordinate system.

    Parameters:
        sx: Horizontal scale factor.
        sy (optional): Vertical scale factor.
            If omitted, sx is used for both axes.
    """
    if sy is None: sy = sx
    m = [[sx,0,0],[0,sy,0],[0,0,1]]
    _P._matrix = _matmul(_P._matrix, m)
 
@_mainthread_only
def arc(x, y, w, h, start, stop):
    """
    Draws an arc (portion of an ellipse).

    Parameters:
        x, y: Center position.
        w, h: Width and height of the ellipse.
        start: Start angle (radians).
        stop: End angle (radians).

    Notes:
        - Angles are specified in radians.
        - Arc is approximated using line segments.
        - Supports fill and stroke.
    """
    steps = max(12, int(abs(stop-start)*20))
    pts = []
    for i in range(steps+1):
        a = start + (stop-start)*i/steps
        px = x + math.cos(a)*w/2
        py = y + math.sin(a)*h/2
        pts.append(_transform_point(_P._matrix, px, py))

    if _P._use_fill:
        pygame.draw.polygon(_P.surface, _P._fill_color[:3], pts)
    if _P._use_stroke:
        pygame.draw.lines(_P.surface, _P._stroke_color[:3], False, pts, _P._stroke_weight)

@_mainthread_only
def quad(x1, y1, x2, y2, x3, y3, x4, y4):
    """
    Draws a quadrilateral defined by four vertices.

    Parameters:
        x1, y1 ... x4, y4: The four corner points.

    Notes:
        - Vertices are connected in the given order.
        - Shape is automatically closed.
        - Supports fill and stroke.
    """
    pts = [_transform_point(_P._matrix,*p) for p in [(x1,y1),(x2,y2),(x3,y3),(x4,y4)]]
    _apply_fill(_P.surface, pygame.draw.polygon, pts)
    _apply_stroke(_P.surface, pygame.draw.polygon, pts)

def square(x, y, s):
    """
    Draws a square.

    Parameters:
        x, y: Position (interpreted by rectMode()).
        s: Side length.

    Notes:
        - Equivalent to rect(x, y, s, s).
    """
    rect(x,y,s,s)

@_mainthread_only
def beginShape(mode=None):
    """
    Begins recording vertices for a custom shape.

    Parameters:
        mode: Optional shape mode (currently unused).

    Notes:
        - Must be followed by one or more vertex() calls.
        - Shape is finalized with endShape().
    """
    _P._shape_vertices = []
    _P._shape_mode = mode

@_mainthread_only
def vertex(x, y):
    """
    Adds a vertex to the current custom shape.

    Parameters:
        x, y: Vertex position.

    Notes:
        - Only valid between beginShape() and endShape().
        - Vertex coordinates are transformed by the current matrix.
    """
    _P._shape_vertices.append(_transform_point(_P._matrix, x, y))

@_mainthread_only
def endShape(close=False):
    """
    Finishes and draws the current custom shape.

    Parameters:
        close (bool): If True, closes the shape.

    Notes:
        - Uses the collected vertices since beginShape().
        - Supports fill and stroke.
        - If fewer than two vertices exist, nothing is drawn.
    """
    pts = _P._shape_vertices
    if len(pts) < 2: return
    if _P._use_fill:
        pygame.draw.polygon(_P.surface, _P._fill_color[:3], pts)
    if _P._use_stroke:
        pygame.draw.lines(_P.surface, _P._stroke_color[:3], close, pts, _P._stroke_weight)

@_mainthread_only
def bezier(x1, y1, x2, y2, x3, y3, x4, y4):
    """
    Draws a cubic Bézier curve.

    Parameters:
        x1, y1: First anchor point.
        x2, y2: First control point.
        x3, y3: Second control point.
        x4, y4: Second anchor point.

    Notes:
        - Curve is approximated using line segments.
        - Uses stroke color and strokeWeight().
        - Fill is not applied.
    """
    pts=[]
    for i in range(30):
        t=i/29
        x = (1-t)**3*x1 + 3*(1-t)**2*t*x2 + 3*(1-t)*t*t*x3 + t**3*x4
        y = (1-t)**3*y1 + 3*(1-t)**2*t*y2 + 3*(1-t)*t*t*y3 + t**3*y4
        pts.append(_transform_point(_P._matrix,x,y))
    pygame.draw.lines(_P.surface,_P._stroke_color[:3],False,pts,_P._stroke_weight)

def loadImage(path):
    """
    Loads an image from disk.

    Parameters:
        path (str): Path to the image file.

    Returns:
        PImage or None:
            A PImage object if loading succeeded,
            None if the image could not be loaded.

    Notes:
        - Supported formats depend on pygame (png, jpg, bmp, gif).
        - The image is loaded with alpha support.
    """
    try:
        surf = pygame.image.load(path)
    except Exception as e:
        print(f"loadImage(): could not load '{path}'")
        return None

    return PImage(surf)

@_mainthread_only
def imageMode(mode):
    """
    Sets the image drawing mode.

    Parameters:
        mode (str):
            - 'CORNER'  : x, y specify the top-left corner (default)
            - 'CENTER'  : x, y specify the image center
            - 'CORNERS' : x, y and w, h specify opposite corners

    Notes:
        - Affects all subsequent image() calls.
    """
    mode = mode.upper()
    if mode not in ('CORNER', 'CORNERS', 'CENTER'):
        raise ValueError("imageMode(): invalid mode")
    _P._image_mode = mode

@_mainthread_only
def tint(*args):
    """
    Applies a color tint to images.

    Parameters:
        args: Same arguments as color():
              - gray
              - gray, alpha
              - r, g, b
              - r, g, b, a

    Notes:
        - Affects all subsequent image() calls.
        - Implemented using multiplicative blending.
    """
    _P._tint = color(*args)

@_mainthread_only
def noTint():
    """
    Disables image tinting.

    Subsequent images will be drawn without color modification.
    """
    _P._tint = None

@_mainthread_only
def image(img, x, y, w=None, h=None):
    """
    Draws an image to the canvas.

    Parameters:
        img (PImage): Image to draw.
        x, y: Position (interpreted by imageMode()).
        w, h (optional): Width and height for scaling.

    Notes:
        - If w and h are provided, the image is scaled.
        - The image is affected by the current transformation matrix.
        - Tinting is applied if tint() is active.
    """
    if img is None or not isinstance(img, PImage):
        return
    if _P.surface is None:
        return

    surf = img.surface

    # Scaling
    if w is not None and h is not None:
        surf = pygame.transform.smoothscale(
            surf, (int(w), int(h))
        )

    iw, ih = surf.get_width(), surf.get_height()

    # imageMode handling
    if _P._image_mode == 'CENTER':
        x -= iw / 2
        y -= ih / 2
    elif _P._image_mode == 'CORNERS':
        iw = w - x
        ih = h - y
        surf = pygame.transform.smoothscale(
            surf, (int(iw), int(ih))
        )

    x, y = _transform_point(_P._matrix, x, y)

    # Tint
    if _P._tint:
        r, g, b, a = _P._tint
        tinted = surf.copy()
        tinted.fill((r, g, b, a), special_flags=pygame.BLEND_RGBA_MULT)
        surf = tinted

    _P.surface.blit(surf, (int(x), int(y)))

@_mainthread_only
def blendMode(mode):
    """
    Sets the image blend mode.

    Parameters:
        mode (str): Blend mode name.

    Notes:
        - Currently stored but not yet implemented.
        - Present for Processing API compatibility.
    """
    mode = mode.upper()
    _P._blend_mode = mode

def getPixel(x, y):
    """
    Returns the color of a pixel on the canvas.

    Parameters:
        x, y: Pixel coordinates.

    Returns:
        (r, g, b, a) tuple or None:
            The color at the given position,
            or None if out of bounds.
    """
    try:
        return _P.surface.get_at((int(x), int(y)))
    except:
        return None

def setPixel(x, y, c):
    """
    Sets the color of a pixel on the canvas.

    Parameters:
        x, y: Pixel coordinates.
        c: Color (any format accepted by color()).

    Notes:
        - Coordinates outside the canvas are ignored.
    """
    try:
        _P.surface.set_at((int(x), int(y)), color(c))
    except:
        pass

def createImage(w, h, mode=None):
    """
    Creates a new empty image.

    Parameters:
        w, h: Width and height of the image.
        mode: Currently unused (kept for Processing compatibility).

    Returns:
        PImage:
            A new transparent image.
    """
    surf = pygame.Surface((int(w), int(h)), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    return PImage(surf)

def copyImage(src):
    """
    Creates a copy of an image.

    Parameters:
        src (PImage): Source image.

    Returns:
        PImage or None:
            A copy of the image, or None if src is invalid.
    """
    if not isinstance(src, PImage):
        return None
    return PImage(src.surface.copy())

def mask(img, mask_img):
    """
    Applies an alpha mask to an image.

    Parameters:
        img (PImage): Target image.
        mask_img (PImage): Mask image.

    Notes:
        - The mask image is scaled to match the target size.
        - Masking is applied using multiplicative alpha blending.
        - The operation modifies the target image in place.
    """
    if not isinstance(img, PImage) or not isinstance(mask_img, PImage):
        return

    m = pygame.transform.smoothscale(mask_img.surface, img.surface.get_size())
    img.surface.blit(m, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

# -------------------------- Helpers --------------------------
def _thread_wrapper(fn, args, kwargs):
    """
    Internal wrapper for thread() execution.

    Ensures that exceptions inside threads do not crash the sketch.
    """
    try:
        fn(*args, **kwargs)
    except Exception as e:
        print(f"[thread] Error in '{fn.__name__}': {e}")

def _extract_rotation_scale(m):
    # 2x3 Matrix:
    # [ a c tx ]
    # [ b d ty ]
    a, b, c, d = m[0][0], m[1][0], m[0][1], m[1][1]

    scale = math.sqrt(a*a + b*b)
    angle = math.atan2(b, a)

    return angle, scale

def _as_rgba(c):
    if not isinstance(c, (tuple, list)):
        raise TypeError("Expected color tuple")
    if len(c) == 3:
        return c[0], c[1], c[2], 255
    if len(c) == 4:
        return c
    raise ValueError("Invalid color format")

def _rgb_to_hsb_scaled(r, g, b):
    h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
    return (
        h * _P._color_max[0],
        s * _P._color_max[1],
        v * _P._color_max[2],
    )

def _camel_to_snake(name):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


def _copy_style():
    return {
        "fill_color": _P._fill_color,
        "stroke_color": _P._stroke_color,
        "use_fill": _P._use_fill,
        "use_stroke": _P._use_stroke,
        "stroke_weight": _P._stroke_weight,
        "color_mode": _P._color_mode,
        "color_max": list(_P._color_max),
        "rect_mode": _P._rect_mode,
        "ellipse_mode": _P._ellipse_mode,
        "font_path": _P._font_path,
        "font_size": _P._font_size,
        "font": _P._font,
        "text_leading": _P._text_leading,
        "text_align_x": _P._text_align_x,
        "text_align_y": _P._text_align_y,
        "smooth": _P._smooth,
    }

def _identity_matrix():
    return [[1,0,0],[0,1,0],[0,0,1]]

def _matmul(a,b):
    return [[sum(a[i][k]*b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]

def _transform_point(m, x, y):
    nx = m[0][0]*x + m[0][1]*y + m[0][2]
    ny = m[1][0]*x + m[1][1]*y + m[1][2]
    return nx, ny

# -------------------------- PFont --------------------------

class PFont:
    """
    Processing-compatible font descriptor.
    Holds font source (name or file) and default size.
    """

    def __init__(self, source=None, size=16):
        self.source = source   # None | str | pygame.font.Font
        self.size = int(size)

    def __repr__(self):
        return f"PFont(source={self.source}, size={self.size})"


# -------------------------- PImage --------------------------

class PImage:
    def __init__(self, surface):
        if not isinstance(surface, pygame.Surface):
            raise TypeError("PImage expects a pygame.Surface")
        self.surface = surface.convert_alpha()
        self.width = surface.get_width()
        self.height = surface.get_height()

        self.pixels = None      # für spätere Erweiterung

    def loadPixels(self):
        self.pixels = pygame.surfarray.pixels3d(self.surface)

    def updatePixels(self):
        del self.pixels

# -------------------------- State --------------------------
class _State:
    def __init__(self):
        self.width = 640
        self.height = 480
        self.surface = None

        # Looping
        self._looping = True
        self._draw_next_frame = True
        self._draw_exists = False
        
        # Environment
        self._window_title = "pygame processing-Style"
        self._cursor_visible = True
        self._cursor_mode = ARROW
        self._cursor_image = None
        self._cursor_hotspot = (0, 0)
        self._smooth = True

        # Styles & Color mode
        self._color_mode = 'RGB'     # 'RGB' or 'HSB'
        self._color_max = [255, 255, 255, 255]  # r,g,b,a OR h,s,b,a
        self._fill_color = (255, 255, 255, 255)
        self._stroke_color = (0, 0, 0, 255)
        self._background_color = (200,200,200, 255)
        self._use_fill = True
        self._use_stroke = True
        self._stroke_weight = 1
        self._font_path = None
        self._font = None
#FIXME        self._text_size = 16
        self._font_source = None   # None | str | pygame.font.Font
        self._font_size = 16
        self._font_cache = {}
        self._text_align_x = _CONSTANTS['LEFT']
        self._text_align_y = _CONSTANTS['BASELINE']
        self._text_font_cache = {}
        self._text_leading = int(self._font_size * 1.2)
        
        # Modes
        self._rect_mode = 'CORNER'
        self._ellipse_mode = 'CENTER'

        # Timing
        self._target_fps = 60.0
        self.frameRate = 60
        self.frameCount = 0
        self._clock = None
        self._running = True
        self._last_time_global = 0
        self._last_frame_time = None

        # Input
        self.mouseX = 0
        self.mouseY = 0
        self.pmouseX = 0
        self.pmouseY = 0
        self.mousePressed = False
        self.mouseButton = None
        


        self.key = None
        self.keyCode = None
        self.keyPressed = False
        # Key state (continuous pressed state)
        self._keys_down = set()

        self._verbose = True
        
        self._matrix = _identity_matrix()
        self._matrix_stack = []
        self._shape_vertices = []
        self._shape_mode = None
        self._style_stack = []
        
        # Image
        self._image_mode = 'CORNER'   # CORNER | CENTER | CORNERS
        self._tint = None             # None oder (r,g,b,a)
        self._blend_mode = None       # später

    def _get_font(self):
        key = (self._font_source, self._font_size)

        if key in self._text_font_cache:
            return self._text_font_cache[key]

        size = int(self._font_size)

        if isinstance(self._font_source, pygame.font.Font):
            font = self._font_source

        elif isinstance(self._font_source, str):
            if self._font_source.lower().endswith((".ttf", ".otf")):
                font = pygame.font.Font(self._font_source, size)
            else:
                font = pygame.font.SysFont(self._font_source, size)

        else:
            font = pygame.font.SysFont(None, size)

        self._text_font_cache[key] = font
        return font


_P = _State()


# -------------------------- Full Proxy System --------------------------

class _BaseProxy:
    def __init__(self, state, attr):
        self._state = state
        self._attr = attr
        self._callback = None

    def get(self):
        return getattr(self._state, self._attr)

    def set(self, value):
        setattr(self._state, self._attr, value)

    def register_callback(self, fn):
        if callable(fn):
            self._callback = fn

    # Descriptor
    def __get__(self, instance=None, owner=None):
        return self.get()
    def __set__(self, instance, value):
        self.set(value)

    # Callable
    def __call__(self, *args, **kwargs):
        if self._callback:
            return self._callback(*args, **kwargs)
        raise TypeError(f"{self._attr} is not callable (no callback assigned)")

    # Representation
    def __repr__(self): return repr(self.get())
    def __str__(self): return str(self.get())

    # Bool / Comparison
    def __bool__(self): return bool(self.get())
    def __eq__(self, other): return self.get() == other
    def __ne__(self, other): return self.get() != other
    def __lt__(self, other): return self.get() < other
    def __le__(self, other): return self.get() <= other
    def __gt__(self, other): return self.get() > other
    def __ge__(self, other): return self.get() >= other

    # Numeric
    def __int__(self): return int(self.get())
    def __float__(self): return float(self.get())
    def __complex__(self): return complex(self.get())
    def __index__(self): return int(self.get())

    # Arithmetic
    def __add__(self, other): return self.get() + other
    def __radd__(self, other): return other + self.get()
    def __sub__(self, other): return self.get() - other
    def __rsub__(self, other): return other - self.get()
    def __mul__(self, other): return self.get() * other
    def __rmul__(self, other): return other * self.get()
    def __truediv__(self, other): return self.get() / other
    def __rtruediv__(self, other): return other / self.get()
    def __floordiv__(self, other): return self.get() // other
    def __rfloordiv__(self, other): return other // self.get()
    def __mod__(self, other): return self.get() % other
    def __rmod__(self, other): return other % self.get()
    def __pow__(self, other): return self.get() ** other
    def __rpow__(self, other): return other ** self.get()
    def __neg__(self): return -self.get()
    def __pos__(self): return +self.get()
    def __abs__(self): return abs(self.get())

class _ProcessingVar(_BaseProxy):
    def set(self, value):
        if self._attr == "frameRate":
            # frameRate ist read-only wie in Processing
            return
        super().set(value)

class _DualProxy(_BaseProxy):
    def get(self):
        return getattr(self._state, self._attr)
    def set(self, value):
        setattr(self._state, self._attr, value)
    def __call__(self, *args, **kwargs):
        if self._callback:
            return self._callback(*args, **kwargs)
        return None

class _FunctionProxy(_BaseProxy):
    def get(self):
        return self._callback
    def __call__(self, *args, **kwargs):
        if self._callback:
            return self._callback(*args, **kwargs)
        return None

def _inject_var(name, dual=False):
    proxy_class = _DualProxy if dual else _ProcessingVar
    proxy = proxy_class(_P, name)
    snake = _camel_to_snake(name)

    # Callback falls schon vorhanden
    user_fn = getattr(__main__, name, None)
    if callable(user_fn) and dual:
        proxy.register_callback(user_fn)

    setattr(__main__, name, proxy)
    setattr(__main__, snake, proxy)
    return proxy

def _inject_fun(name):
    proxy_class = _FunctionProxy
    proxy = proxy_class(_P, name)
    snake = _camel_to_snake(name)

    # Callback falls schon vorhanden
    mod = sys.modules[__name__]  
    user_fn = getattr(mod, name, None) 
    if callable(user_fn):
        proxy.register_callback(user_fn)

    setattr(__main__, name, proxy)
    setattr(__main__, snake, proxy)
    return proxy


# -------------------------- Constants --------------------------


def _apply_fill(surf,func,*args,**kwargs):
    if _P._use_fill and _P._fill_color:
        func(surf,_P._fill_color[:3],*args,**kwargs)

def _apply_stroke(surf,func,*args,**kwargs):
    if _P._use_stroke and _P._stroke_color:
        func(surf,_P._stroke_color[:3],*args,width=_P._stroke_weight,**kwargs)

def _update_mouse(event):
    # Handle movement
    if event.type == pygame.MOUSEMOTION:
        _P.pmouseX, _P.pmouseY = _P.mouseX, _P.mouseY
        _P.mouseX, _P.mouseY = event.pos

        if _P.mousePressed:
            # Dragging
            _P._mouse_dragged = True
            if callable(getattr(__main__, 'mouseDragged', None)):
                __main__.mouseDragged()
        else:
            # Moving without button
            if callable(getattr(__main__, 'mouseMoved', None)):
                __main__.mouseMoved()
        return

    # Handle mouse down
    if event.type == pygame.MOUSEBUTTONDOWN:
        # Wheel events should not trigger click logic
        if event.button in (4, 5):
            return

        _P.pmouseX, _P.pmouseY = _P.mouseX, _P.mouseY
        _P.mouseX, _P.mouseY = event.pos

        _P.mousePressed = True
        _P.mouseButton = {1:'LEFT', 2:'CENTER', 3:'RIGHT'}.get(event.button)
        _P._mouse_dragged = False
        _P._mouse_down_pos = event.pos
        _P._mouse_down_time = time.time()

        if callable(getattr(__main__, 'mousePressed', None)):
            __main__.mousePressed()
        return

    # Handle mouse up
    if event.type == pygame.MOUSEBUTTONUP:
        # Again: wheel events do not trigger click logic
        if event.button in (4, 5):
            return

        _P.pmouseX, _P.pmouseY = _P.mouseX, _P.mouseY
        _P.mouseX, _P.mouseY = event.pos

        was_dragged = _P._mouse_dragged
        down_pos = _P._mouse_down_pos
        down_time = _P._mouse_down_time

        _P.mousePressed = False
        _P.mouseButton = None

        # Always trigger mouseReleased
        if callable(getattr(__main__, 'mouseReleased', None)):
            __main__.mouseReleased()

        # Click detection: small movement + fast release
        if not was_dragged:
            dx = _P.mouseX - down_pos[0]
            dy = _P.mouseY - down_pos[1]
            dist_sq = dx*dx + dy*dy
            time_diff = time.time() - down_time

            if dist_sq < 9 and time_diff < 0.3:
                if callable(getattr(__main__, 'mouseClicked', None)):
                    __main__.mouseClicked()
        return


def _update_mouse_wheel(event):
    """
    Processing-kompatibles mouseWheel():
    - event.delta > 0  = nach oben
    - event.delta < 0  = nach unten

    Processing ruft mouseWheel(event) auf,
    wobei event.count die Scroll-Richtung enthält.
    """

    # Pygame: button 4 (up), button 5 (down)
    if event.type == pygame.MOUSEWHEEL:
        wheel = event.y
    elif event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 4:
            wheel = 1
        elif event.button == 5:
            wheel = -1
        else:
            return
    else:
        return


    class WheelEvent:
        def __init__(self, count):
            self.count = count

    if callable(getattr(__main__, "mouseWheel", None)):
        __main__.mouseWheel(WheelEvent(wheel))

def _update_keyboard(event):
    if event.type==pygame.KEYDOWN:
        _P.keyPressed=True
        _P.keyCode=event.key
        # If not a special name, try unicode
        if event.key in _keycode_map:
            key_name = _keycode_map[event.key]
            _P.key = key_name
            _P._keys_down.add(key_name)
        else:
            try:
                _P.key=event.unicode
                if _P.key:
                    _P._keys_down.add(_P.key)
            except:
                _P.key=None
        if callable(getattr(__main__,'keyPressed',None)):
            __main__.keyPressed()
        if callable(getattr(__main__,'keyTyped',None)) and _P.key:
            __main__.keyTyped()
    elif event.type==pygame.KEYUP:
        _P.keyPressed=False
        # Remove from pressed set
        if event.key in _keycode_map:
            _P._keys_down.discard(_keycode_map[event.key])
        else:
            try:
                if event.unicode:
                    _P._keys_down.discard(event.unicode)
            except:
                pass
        if callable(getattr(__main__,'keyReleased',None)):
            __main__.keyReleased()

def _init():
    pygame.init()

    # Apply startup cursor state
    if not _P._cursor_visible:
        pygame.mouse.set_visible(False)
    else:
        if _P._cursor_image:
            cursor(_P._cursor_image, *_P._cursor_hotspot)
        elif _P._cursor_mode:
            cursor(_P._cursor_mode)
        else:
            cursor()

    size(_P.width,_P.height)
    pygame.display.set_caption(_P._window_title)
    _P._clock = pygame.time.Clock()

    _P._running = True
    _P._last_time = time.time()
    _P._last_time_global = _P._last_time
    _P._last_frame_time = None  # Frame-Zeit initialisieren

# -------------------------- Run loop --------------------------
def run():
    """
    Starts the Processing-style sketch loop.

    Notes:
        - Calls setup() once (if defined).
        - Calls draw() repeatedly depending on loop state.
        - Handles events, rendering, and frame timing.
        - Blocks until the sketch exits.
    """
    if not pygame.get_init():
        _init()

    setup_fn = getattr(__main__,'setup',None)
    if callable(setup_fn):
        setup_fn()

    draw_fn = getattr(__main__,'draw',None)
    _P._draw_exists = callable(draw_fn)
    if not _P._draw_exists:
        noLoop()
        _P._draw_next_frame = False
    while _P._running:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                _P._running=False
            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEWHEEL):
                _update_mouse(event)
                _update_mouse_wheel(event)
            elif event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP):
                _update_mouse(event)
            elif event.type in (pygame.KEYDOWN,pygame.KEYUP):
                _update_keyboard(event)

        # Wenn looping aktiv oder redraw angefordert
        if _P._looping or _P._draw_next_frame:
            try:
                draw_fn()
            except Exception:
                import traceback; traceback.print_exc()
                _P._running=False
                break
            _P._draw_next_frame = False  # redraw zurücksetzen
        if not _P._draw_exists:
            if getPressed('ESC'):
                exit()    

        pygame.display.get_surface().blit(_P.surface,(0,0))
        pygame.display.flip()

        # --- Framerate-Messung (Processing-like) ---
        now = time.time()
        if _P._last_frame_time is None:
            _P._last_frame_time = now
        else:
            dt = now - _P._last_frame_time
            if dt > 0:
                instant_fps = 1.0 / dt
                # sanfte Glättung wie Processing
                _P.frameRate = (_P.frameRate * 0.9) + (instant_fps * 0.1)
            _P._last_frame_time = now

        _P.frameCount += 1
        _P._clock.tick(_P._target_fps)

    pygame.quit()
    
# -------------------------- Inject all variables --------------------------
_PUBLIC_FUNCTIONS = [
    # control
    run, exit, loop, noLoop, redraw, thread, delay,

    # time
    millis, second, minute, hour, day, month, year, weekday, timestamp,

    # random
    random, randomSeed, randomGaussian, map,

    # input
    getPressed,

    # window
    size, windowTitle, smooth, noSmooth, cursor, noCursor,

    # text
    text, textSize, textAlign, textFont, textAscent, textDescent,
    textWidth, textLeading, loadFont, createFont,

    # color
    color, colorMode, lerpColor,
    alpha, red, green, blue, hue, saturation, brightness,

    # style
    background, clear, fill, noFill, stroke, noStroke,
    strokeWeight, rectMode, ellipseMode, pushStyle, popStyle,

    # shapes
    line, point, rect, ellipse, circle, triangle, square, quad, arc,
    beginShape, vertex, endShape, bezier,
    
    # transformations
    translate, rotate, scale, pushMatrix, popMatrix,
    
    # images
    tint, noTint, imageMode, loadImage, image, blendMode, createImage, copyImage, mask, getPixel, setPixel
]

def _inject_all():
    # first those three variables for which a function with the same name (might) exist
    _inject_var("mousePressed", dual=True)
    _inject_var("keyPressed", dual=True)
    _inject_var("frameRate", dual=True)

    # all system variables
    for var in ["width","height","mouseX","mouseY","pmouseX","pmouseY","mouseButton",
                "key","keyCode","frameCount"]:
        _inject_var(var)

    # inject everything else that is callable and not
    # yet injected as functions in camelCase and snake_case
    for fn in _PUBLIC_FUNCTIONS:
        _inject_fun(fn.__name__)

def _inject_key_constants_into_main():
    for name in _PROCESSING_KEY_CONSTANTS:
        setattr(__main__, name, name)
    for name in _CURSOR_CONSTANTS:
        setattr(__main__, name, name)
    for name in _NAMED_COLORS:
        setattr(__main__, name, name)
    if not hasattr(__main__, "PImage"):
        setattr(__main__, "PImage", PImage)
    if not hasattr(__main__, "PFont"):
        setattr(__main__, "PFont", PFont)
    if not hasattr(__main__, "_P"):
        setattr(__main__, "_P", _P)

    for name,val in _CONSTANTS.items():
        # Typ prüfen: float/int → direkt, alles andere → String
        if isinstance(val, (int, float)):
            setattr(__main__, name, val)
        else:
            setattr(__main__, name, str(val))
    __main__.RETURN = "ENTER"

_inject_all()  
_inject_key_constants_into_main()

# -------------------------- Demo --------------------------
if __name__=='__main__':
    def setup():
        size(640, 480)
        frameRate(60)

    def draw():
        background(30, 120, 200)
        fill(RED)
        stroke(255)
        strokeWeight(4)
        ellipse(width/2, height/2, 150, 150)
        if getPressed(ESC):
            exit()
       
    run()
    
