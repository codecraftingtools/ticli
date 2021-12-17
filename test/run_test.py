#!/usr/bin/env python3

# Copyright (C) 2021 NTA, Inc.

from ticli import option, Fire

@option.group
class Test:
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
        """
        Args:
          x: first init arg
          y: second init arg
        """
        print(f"__post_init__: x:{x} y:{y}")
        print(f"             : option_data: {self._option_data}")
        
    def __post_call__(self, arg:int=7):
        """
        Args:
          arg: first invoke arg
        """
        print(f"__post_call__: arg:{arg}")
        print(f"             : option_data: {self._option_data}")
        return self
    
    def f(self, c:int):
        """
        Example Command.

        Does something mysterious. 

        Args:
          c: input argument for f command
        """
        print(f"f: c:{c}")
        print(f" : option_data: {self._option_data}")

    def reset(self):
        """
        Restores option settings to the default values.
        """
        print(f"  reset: option_data: {self._option_data}")
        option.restore_defaults(self)
        return self

@option.group
class Extended(Test):
    """
    Extended Testing Options.

    Group of extended options for testing purposes.

    Args:
      e: first extended option
    """
    e: int = 3
    
    def __post_init__(self, q:int=8, r:int=9):
        """
        Args:
          q: first extended init arg
          r: second extended init arg
        """
        print(f"Extended __post_init__: q:{q} r:{r}")
        print(f"                      : option_data: {self._option_data}")

@option.group
class Other:
    """
    Other Options.

    Args:
      o: other option
    """
    o: int = 9
    
@option.group
class More_Extended(Extended, Other):
    """
    More Extended Testing Options.

    Group of even more extended options for testing purposes.

    Args:
      g: more extended option
    """
    g: int = 4

    
if __name__ == '__main__':
    Fire(More_Extended)
