#!/usr/bin/env python3

# This software is copyrighted and licensed under the terms of the MIT
# license.  See the LICENSE file found in the top-level directory of this
# distribution for copyright information and license terms.

# Author: Jeff Webb <jeff.webb@codecraftsmen.org>

from ticli import Fire

def jump(height:float, verbose:bool=False):
    """
    Jump command.

    Command the computer to jump for you.

    Args:
      height: How high to jump (in feet)
      verbose: Enable verbose output
    """
    if verbose:
        print("getting ready to jump")
        
    print(f"jumping {height} feet")
    
    if verbose:
        print("finished jumping")

if __name__ == '__main__':
    Fire(jump)
