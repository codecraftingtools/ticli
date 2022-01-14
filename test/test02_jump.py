#!/usr/bin/env python3

# This software is copyrighted and licensed under the terms of the MIT
# license.  See the LICENSE file found in the top-level directory of this
# distribution for copyright information and license terms.

# Author: Jeff Webb <jeff.webb@codecraftsmen.org>

from ticli import Fire
from typing import Literal

Unit = Literal["feet", "inches", "meters"]

def jump(height:float, verbose:bool=False, units:Unit="feet"):
    """
    Jump command.

    Command the computer to jump for you.

    Args:
      height: How high to jump
      verbose: Enable verbose output
      units: Units for height
    """
    if units == "inches":
        height = height / 12.0
    elif units == "meters":
        height = height * 3.2808399
        
    if verbose:
        print("getting ready to jump")
        
    print(f"jumping {height} feet")
    
    if verbose:
        print("finished jumping")

if __name__ == '__main__':
    Fire(jump)
