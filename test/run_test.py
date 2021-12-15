#!/usr/bin/env python3

# Copyright (C) 2021 NTA, Inc.

import fire
from ticli import option

@option.group
class Test_Options:
    """
    Class.

    More Class.
    """
    
    def _options(self, a:int=1, b:int=2):
        """ Args:
              a: first arg
              b: second arg
        """
        print(f"_options: a:{a} b:{b}")

    def _init(self, x:int=8, y:int=9):
        """ Args:
              x: first init arg
              y: second init arg
        """
        print(f"_init: x:{x} y:{y}")

    def _invoke(self, arg):
        """ Args:
              invoke1: first invoke arg
        """
        print("_invoke", arg)

    def f(self, c=3):
        print("f", c)
    
if __name__ == '__main__':
    
    # Work-around to keep fire from using "less" to show help output
    import os
    os.environ["PAGER"] = "cat"
    
    fire.Fire(Test_Options)
