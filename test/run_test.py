#!/usr/bin/env python3

import fire
from ticli.option import *

@options
class Options:
    """
    Class.

    More Class.
    """
    
    def __init__(self, x:int=8, y:int=9):
        """ Args:
              x: first init arg
              y: second init arg
        """
        print(f"_init: x:{x} y:{y}")

    def _check_options(self, a:int=1, b:int=2):
        """ Args:
              a: first arg
              b: second arg
        """
        print(f"_check_options: a:{a} b:{b}")

    def _invoke(self, invoke1):
        """ Args:
              invoke1: first invoke arg
        """
        print("_invoke", invoke1)
        return self
    
if __name__ == '__main__':
    # Work-around to keep fire from using "less" to show help output
    import os
    os.environ["PAGER"] = "cat"
    
    fire.Fire(Options)
