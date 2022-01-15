#!/usr/bin/env python3

# This software is copyrighted and licensed under the terms of the MIT
# license.  See the LICENSE file found in the top-level directory of this
# distribution for copyright information and license terms.

# Author: Jeff Webb <jeff.webb@codecraftsmen.org>

from ticli import Fire
from typing import Literal

Dialect = Literal["formal", "informal", "hillbilly"]

def greet(dialect:Dialect="formal", verbose:bool=False):
    """
    Greet command.

    Command the computer to greet you.

    Args:
      dialect: Language dialect to use for greeting
      verbose: Enable verbose output
    """
    greetings = {
        "formal": "Hello.",
        "informal": "Hi!",
        "hillbilly": "Howdy, there!",
    }
    greeting = greetings[dialect]
    
    if verbose:
        print("getting ready to greet")
        
    print(f"{greeting}")
    
    if verbose:
        print("finished greeting")

if __name__ == '__main__':
    Fire(greet)
