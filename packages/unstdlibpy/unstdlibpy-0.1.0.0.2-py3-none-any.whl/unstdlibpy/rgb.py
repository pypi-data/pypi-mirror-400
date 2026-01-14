
"""
Some color, such as blue, red, green, cyan...You name it!
And the function rgb, make_rgb and make_rgb_mode are your choice.
"""

from typing import Callable

def rgb(string: str, r: int, g: int, b: int, mode: str = 't') -> str:
    assert isinstance(r, int) and isinstance(g, int) and isinstance(b, int) and \
        0 <= r < 256 and 0 <= g < 256 and 0 <= b < 256, f'Bad rgb: {r=}, {g=}, {b=}.'
    if mode == 't': m: int = 38
    elif mode == 'b': m: int = 48
    else: raise NameError(f'Unknown mode: \'{mode}\'.')
    return f'\033[{m};2;{r};{g};{b}m{string}\033[0m'

def make_rgb_mode(r: int, g: int, b: int, mode: str = 't') -> Callable:
    assert isinstance(r, int) and isinstance(g, int) and isinstance(b, int) and \
        0 < r < 256 and 0 < g < 256 and 0 < b < 256, f'Bad rgb: {r=}, {g=}, {b=}.'
    if mode == 't': m: int = 38
    elif mode == 'b': m: int = 48
    else: raise NameError(f'Unknown mode: \'{mode}\'.')
    def wrap(string: str) -> str:
        return f'\033[{m};2;{r};{g};{b}m{string}\033[0m'
    wrap.__name__ = f'rgb({r=}, {g=}, {b=})'
    return wrap

def make_rgb(r: int, g: int, b: int) -> Callable:
    assert isinstance(r, int) and isinstance(g, int) and isinstance(b, int) and \
        0 <= r < 256 and 0 <= g < 256 and 0 <= b < 256, f'Bad rgb: {r=}, {g=}, {b=}.'
    
    def wrap(string: str, mode: str = 't') -> str:
        if mode == 't': m: int = 38
        elif mode == 'b': m: int = 48
        else: raise NameError(f'Unknown mode: \'{mode}\'.')
        return f'\033[{m};2;{r};{g};{b}m{string}\033[0m'
    wrap.__name__ = f'rgb({r=}, {g=}, {b=})'
    return wrap

# some colors.
RED = make_rgb(255, 0, 0)
BLUE = make_rgb(0, 0, 255)
GREEN = make_rgb(0, 255, 0)
YELLOW = make_rgb(255, 255, 0)
ORANGE = make_rgb(255, 128, 0)
CYAN = make_rgb(0, 255, 255)
PURPLE = make_rgb(255, 0, 255)
BLACK = make_rgb(0, 0, 0)
WHITE = make_rgb(255, 255, 255)

# special red
CHINESE_RED = make_rgb(230, 0, 18)
BRIGHT_RED  = make_rgb(255, 0, 36)

# special blue
SKY_BLUE = make_rgb(135, 206, 235)

#special green
EMERALD_GREEN = make_rgb(80, 200, 120)

# ???
MAGIC_COLOR = make_rgb(74, 65, 42)

if __name__ == '__main__':
    print(CHINESE_RED("Water of cow is milk"))
    print(RED        ("Water of cow is milk"))
    print(BRIGHT_RED ("Water of cow is milk"))
    print(MAGIC_COLOR("Water of cow is milk"))
    
