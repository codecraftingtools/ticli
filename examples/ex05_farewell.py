#!/usr/bin/env python3

# This software is copyrighted and licensed under the terms of the MIT
# license.  See the LICENSE file found in the top-level directory of this
# distribution for copyright information and license terms.

# Author: Jeff Webb <jeff.webb@codecraftsmen.org>

from ticli import option, Fire
from typing import Literal

Dialect = Literal["formal", "informal", "hillbilly"]

@option.group
class Farewell:
    """
    Farewell command.

    Command the computer to bid you farewell.

    Args:
      dialect: Language dialect to use for farewell
    """
    dialect: Dialect = "formal"
    
    def __post_call__(self):
        farewells = {
            "formal": "Goodbye.",
            "informal": "Bye!",
            "hillbilly": "Y'all come back now, ya hear!",
        }
        farewell = farewells[self.dialect]
        print(f"{farewell}")     
        return None
    
if __name__ == '__main__':
    Fire(Farewell())
