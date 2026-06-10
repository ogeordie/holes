# Holes

# Holes is a program for simulations of archaeological excavations.

# Copyright 2024-2026 Geordie Oakes

# This program is free software: you can redistribute it and/or modify it under the terms of the GNU 
# General Public License v3 as published by the Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without 
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
# General Public License v3 for more details.

# You should have received a copy of the GNU General Public License along with this program. If not, 
# see https://www.gnu.org/licenses/gpl-3.0.html.

# This file implements the class Hole which can be placed on a Field by a Player.

# See the README.md file for more details.


from dataclasses import dataclass


# a hole on a field
@dataclass(frozen=True)
class Hole:
    centreX:float
    centreY:float
    width:float
    height:float

    # Returns True if this hole intersects anotherHole, otherwise False
    def intersects(self, anotherHole) -> bool:
        h1Top = self.centreY - self.height /2;
        h1Left = self.centreX - self.width  / 2;
        h1Bottom = self.centreY + self.height / 2;
        h1Right = self.centreX + self.width / 2;

        h2Top = anotherHole.centreY - anotherHole.height /2;
        h2Left = anotherHole.centreX - anotherHole.width  / 2;
        h2Bottom = anotherHole.centreY + anotherHole.height / 2;
        h2Right = anotherHole.centreX + anotherHole.width / 2;

        xOverlaps = h2Left < h1Right and h2Right > h1Left;
        yOverlaps = h2Top < h1Bottom and h2Bottom > h1Top;

        return xOverlaps and yOverlaps;

