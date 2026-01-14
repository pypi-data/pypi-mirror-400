
"""
Initialization file for the unstdlibpy package.
Provides access to various utility modules such as math, random, save, const, algo, and universal.You name it
"""

from . import algebra, algo, const, hlambda, math, random_old, random, rgb, save

def universal_load():
    """
    Because module universal is so big,
    so I deside to make a function of it.
    If you need to import it, please write:
    'universal = universal_load()'
    Do you understand?
    """

    from . import universal
    return universal

__version__ = "0.1.0.0.2"
