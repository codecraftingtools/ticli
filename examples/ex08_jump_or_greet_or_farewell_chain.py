#!/usr/bin/env python3

# This software is copyrighted and licensed under the terms of the MIT
# license.  See the LICENSE file found in the top-level directory of this
# distribution for copyright information and license terms.

# Author: Jeff Webb <jeff.webb@codecraftsmen.org>

from ticli import command, option, Fire
from typing import Literal

Dialect = Literal["formal", "informal", "hillbilly"]

@command
class Farewell:
    """
    Farewell command.

    Command the computer to bid you farewell.

    Args:
      dialect: Language dialect to use for farewell
    """
    dialect: Dialect = "formal"
    
    def __post_init__(self, config):
        self._config = config
        
    def __post_call__(self):
        farewells = {
            "formal": "Goodbye.",
            "informal": "Bye!",
            "hillbilly": "Y'all come back now, ya hear!",
        }
        farewell = farewells[self.dialect]
        
        if self._config.verbose:
            print("getting ready to bid you farewell")
            
        print(f"{farewell}")
        
        if self._config.verbose:
            print("finished bidding you farewell")

        return option.next_in_chain_after(self)
    
Unit = Literal["feet", "inches", "meters"]

@option.group
class Top:
    """
    Multipurpose program.

    Allows the user to invoke a subcommand.

    Args:
      verbose: Enable verbose output
    """
    verbose: bool = False

    def __post_init__(self):
        self.farewell = Farewell(
            self, next_in_chain=option.next_in_chain_after(self))
        
    def jump(self, height:float, units:Unit="feet"):
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
            
        if self.verbose:
            print("getting ready to jump")
            
        print(f"jumping {height} feet")
        
        if self.verbose:
            print("finished jumping")        
    
        return option.next_in_chain_after(self)
    
    def greet(self, dialect:Dialect="formal"):
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
        
        if self.verbose:
            print("getting ready to greet")
            
        print(f"{greeting}")
        
        if self.verbose:
            print("finished greeting")
        
        return option.next_in_chain_after(self)
    
if __name__ == '__main__':
    Fire(Top(next_in_chain="self"))
