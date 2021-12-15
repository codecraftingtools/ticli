#!/usr/bin/env python3

# Copyright (C) 2021 NTA, Inc.

import fire
from ticli import option

@option.group
class Test_Options:
    """
    Testing Options.

    Group of options for testing purposes.

    Args:
      a: first option
      b: second option
    """
    a: int = 1
    b: int = 2

    def __post_init__(self, x:int=8, y:int=9):
        """ Args:
              x: first init arg
              y: second init arg
        """
        print(f"__post_init__: x:{x} y:{y}")

    def __post_call__(self, arg):
        """ Args:
              arg: first invoke arg
        """
        print(f"__post_call__: arg:{arg}")

    def f(self, c=3):
        """ Args:
              c: first f arg
        """
        print(f"f: c:{c}")
    
if __name__ == '__main__':
    
    # Work-around to keep fire from using "less" to show help output
    import os
    os.environ["PAGER"] = "cat"
    
    fire.Fire(Test_Options)
