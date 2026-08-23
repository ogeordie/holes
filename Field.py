# Holes

# Holes is a program for simulations of archaeological excavations.

# Copyright 2024-2026 Geordie Oakes

# This program is free software: you can redistribute it and/or modify it under the terms of 
# the GNU General Public License v3 as published by the Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
# See the GNU General Public License v3 for more details.

# You should have received a copy of the GNU General Public License along with this program. 
# If not, see https://www.gnu.org/licenses/gpl-3.0.html.


# See the "README.md" file for information, and installation and usage instructions.

# This file implements a Field on which Treasure is placed, and on which a Player
# digs Holes to see if the Treasure is found.

# NOTE: The origin (0,0) is defined as the top left of the field.
 
from Treasure import Treasure
from Hole import Hole
import sys


# A Field that contains a Treasure. Holes can be dug on it.
# To use, first call placeTreasure(), then call digHole() for each hole in the
# layout algorithm, which returns True if the hole intersects the treasure.
# A Field is intended to be used once only, create a new one before
# placeTreasure() is called.
# NOTE: Some parts of this code assume a square field.
class Field:

    # create the field with the given dimensions
    def __init__(self, width:int, height:int):
        self.width = width;
        self.height = height;
        self.holes = [];
        self._treasurePlaced = False;
        self.adjustedHoleAtBorder = False;
        self._treasure = None;

    # Place treasure on the field at a random location. For "Layout Matters" experiments,
    # the treasure lies so that at least two thirds of at least two sides of its
    # bounding box lie within the field (so the bounding box centre is at least 
    # one sixth the lengths of the relevant sides of the bounding box from the field edge).
    # This means usually at least two thirds of the bounding box
    # area will lie within the Field. When placed near the corners of the 
    # Field, at least four ninths of the bounding box area will lie within
    # the Field.
    def placeTreasure(self, treasure:Treasure):
        self._treasure = treasure;
        self._treasure.placeRandomly(self.width, self.height);
        self._treasurePlaced = True;
    
    # dig a square hole on a field with centre (centreX, centreY) and width and
    # height of holeSize.
    # Returns True if the hole finds treasure, False otherwise.
    def digHole(self, holeSize:float, centreX:float, centreY:float) -> bool:
        if not self._treasurePlaced:
            print("define treasure before placing holes");
            exit();
        
        if centreX - holeSize/2 < 0:
            centreX = holeSize/2;
            self.adjustedHoleAtBorder = True;
        elif centreX + holeSize/2 > self.width:
            centreX = self.width - holeSize/2;
            self.adjustedHoleAtBorder = True;
        if centreY - holeSize/2 < 0:
            self.adjustedHoleAtBorder = True;
            centreY = holeSize/2;
        elif centreY + holeSize/2 > self.height:
            self.adjustedHoleAtBorder = True;
            centreY = self.height - holeSize/2;

        hole = Hole(centreX, centreY, holeSize, holeSize);
        self.holes.append(hole);
        return self._treasure.intersectsHole(hole);

    # returns True if newHole intersects an existing hole on the field.
    # This is useful if the layout algorithm doesn't want to place two
    # holes on the field that intersect each other.
    def intersectsExistingHole(self, newHole:Hole) -> bool:
        for h in self.holes:
            if h.intersects(newHole):
                return True;
        return False;

    # Get the treasure that was placed on the field.
    def getTreasure(self) -> Treasure:
        if not self._treasurePlaced:
            print("attempt to get non-existant treasure");
            exit(1);
        return self._treasure;
    
    # Prints the field including holes and treasure to a text file fileName.
    # This can be then used by CreateFieldImage.py to print a graphical
    # representation of the field, holes, and treasure. See that
    # python file for a description of the field file format.
    def printField(self, fileName:str = ""):
        if fileName != "":
            output = open(fileName, 'w');
        else:
            output = sys.stdout;
        print("field", file=output);
        print(self.width, self.height, file=output);
        self._treasure.printTreasure(output);
        for h in self.holes:
            print("hole:", h.centreX, h.centreY, h.width, h.height, self._treasure.intersectsHole(h), file=output);
