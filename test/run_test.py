#!/usr/bin/env python3

# Copyright (C) 2021 NTA, Inc.

import fire
from ticli import option
from ticli.validation import (
    validate_arguments,
    ValidationError,
    print_validation_errors,
)

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
        """ Args:
              x: first init arg
              y: second init arg
        """
        print(f"__post_init__: x:{x} y:{y}")
        print(f"             : option_data: {self._option_data}")
        
    def __post_call__(self, arg:int=7):
        """ Args:
              arg: first invoke arg
        """
        print(f"__post_call__: arg:{arg}")
        print(f"             : option_data: {self._option_data}")
        return self
    
    @validate_arguments
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
    
if __name__ == '__main__':
    
    # Work-around to keep fire from using "less" to show help output
    import os
    os.environ["PAGER"] = "cat"
    
    try:
        fire.Fire(Test)
    except ValidationError as exc:
        print_validation_errors(exc)
