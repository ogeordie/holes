# Holes

# Holes is a program for simulations of archaeological digs.

# Copyright 2024 Geordie Oakes

# This program is free software: you can redistribute it and/or modify it under the terms of 
# the GNU General Public License v3 as published by the Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
# See the GNU General Public License v3 for more details.

# You should have received a copy of the GNU General Public License along with this program. 
# If not, see https://www.gnu.org/licenses/gpl-3.0.html.


# DESCRIPTION

# This code was used to run the simulations described in the article "Size Matters: Optimal 
# Test Pit Size for Dispersed Archaeological Test Excavations" by Oakes and McLaren.

# It places square test pits ("holes" in the code) of given number and size on a square field 
# of a given size. The field has a randomly placed archaeological site ("treasure" in the 
# code), either specified by a circle or rectangle (for intersection experiments), or by 
# real-world data on artefact distribution from digs in NSW Australia (for detection 
# experiments). See the csv files in the real world data directory for these data.

# The pits are placed according to a layout algorithm. Layout algorithms are implemented by 
# subclasses of the class Player. Calling Player.play() performs one archaeological dig 
# (digging a certain number of holes on the Field according to the layout algorithm), and 
# returns True if treasure is found (False otherwise). The HexagonalLikePlayer player was used 
# in the simulations for the article. Other Player subclasses include HexagonalPlayer, 
# HaltonPlayer, and RandomPlayer. See the document size matters layout algorithms.pdf for 
# explanation of the layout algorithms.

# The function exploreNumberOfHoles() is the main function for most experiments. This fixes 
# all parameters except number of holes (field size, hole size, treasure specification, player 
# type, etc.), and for each number of holes (from 1 to a maximum value) the inner simulation 
# procedure is run 10000 times (i.e. there are 10000 digs for each number of holes), with the 
# treasure placed randomly each time. The output (printed to standard output) for each number 
# of holes is the desired number of holes, the actual number of holes as determined by the 
# layout algorithm (which may differ from the desired number of holes due to layout algorithm 
# constraints), and the percentage of runs where a hole found treasure ("success rate"). The 
# output for the real-world artefact distribution treasure also includes the average number of 
# artefacts found over the runs and average number of holes that found anything.

# As mentioned above, note that some players dig a slightly different number of holes than the 
# one supplied to them as the layout algorithm may not work with all numbers of holes. This 
# actual number of holes is also returned by Player.play() (as well as weather the dig was 
# successful).

# The function doSpecificGridExperiment() allows experiments to be done with a list of 
# specific numbers of holes, or a list of specific number of holes horizontally and vertically.

# This file Holes.py contains code to run simulations as described above. There is also the 
# functionality to save a field (with holes and treasure) to a text file. The file 
# CreateFieldImage.py contains code to read said text file and produce a graphical 
# representation of the field.

# The inner simulation procedure (called 10000 times for each number of holes) is simplified 
# as:
#     field = Field(fieldSize, fieldSize)
#     field.placeCircularTreasure(treasureRadius)
#     player = HexagonalLikePlayer(field, holeSize, numberOfHoles)
#     result = player.play()
#     if result[0]:
#         successes = successes + 1
#     actualNumberOfHolesDug = result[1]
# Then after the 10000 runs, print out numberOfHoles, actualHolesDug, and successes * 100 / 
# 10000 (We assume actualHolesDug by the player will be the same when numberOfHoles is the 
# same).

# This code was only tested with the limited experiments explored in the article. It may not 
# be correct in all circumstances.

import random
import math
import sys
import traceback
import time
import csv
from scipy.stats import qmc

# a hole on a field
class Hole:
    def __init__(self, centreX:float, centreY:float, width:float, height:float):
        self.centreX = centreX;
        self.centreY = centreY;
        self.width = width;
        self.height = height;

# an abstract field on which holes can be dug. Implementations are responsible
# for allowing treasure to be placed on the field too.
# To use, first place the treasure, then call digHole() for each hole in the
# layout algorithm, which returns True if the hole finds treasure.
# A Field is intended to be used once only: placing a 
# second treasure does not remove the first one.
#
# NOTE: Some parts of this code assume a square field.
class Field:
    def print(self, fileName=""):
        pass;
    
    # dig a square hole on a field with centre (x,y), of width and height holeSize
    # Returns True if the hole finds treasure, False otherwise
    def digHole(self, holeSize:float, x:float, y:float) -> bool:
        pass

    # returns True if newHole intersects an existing hole on the field.
    # This is useful if the layout algorithm doesn't want to place two
    # holes on the field that intersect each other.
    def intersectsExistingHole(newHole:Hole) -> bool:
        pass;

    # prints the field data to a text file. This can be then used to print a graphical
    # representation of the field, holes, and treasure
    def print(self, fileName:str = ""):
        pass;

# implementation of Field in which treasure is defined by a shape (circle or rectangle)
# and digHole() returns True if the hole intersects the treasure shape.
# To use first call placeCircularTreasure() or placeRectangularTreasure() and then
# call digHole() for each hole to be dug.
class IntersectField(Field):
    def __init__(self, width:int, height:int):
        self.width = width;
        self.height = height;
        self.holes = [];
        self.__treasurePlaced = False;
        self.adjustedHoleAtBorder = False;

    # returns True if the point (x,y) intersects the treasure on the field.
    # assumes a treasure has been placed.
    def __pointIntersectsTreasure(self, x:float, y:float) -> bool:
        if self.__rectangularTreasure == False:
            d = math.sqrt((x - self.__treasureCentreX)**2 + (y - self.__treasureCentreY)**2);
            return d <= self.__treasureRadius;
        else: #rectangularTreasure == True
            xInBounds = x > self.__treasureCentreX - self.__treasureWidth/2 and x < self.__treasureCentreX + self.__treasureWidth/2;
            yInBounds = y > self.__treasureCentreY - self.__treasureHeight/2 and y < self.__treasureCentreY + self.__treasureHeight/2;
            return xInBounds and yInBounds;


    # returns True iff hole intersects the treasure on the field. Assumes treasure has been placed.
    def __intersectsTreasure(self, hole:Hole) -> bool:
        if self.__rectangularTreasure == False:
            holeX = hole.centreX;
            holeY = hole.centreY;
            circleDistanceX = abs(self.__treasureCentreX - holeX);
            circleDistanceY = abs(self.__treasureCentreY - holeY);

            if (circleDistanceX > (hole.width/2 + self.__treasureRadius)):
                return False;
            if (circleDistanceY > (hole.height/2 + self.__treasureRadius)):
                return False;

            if (circleDistanceX <= (hole.width/2)):
                return True;
            if (circleDistanceY <= (hole.height/2)):
                return True;

            cornerDistance_sq = (circleDistanceX - hole.width/2)**2 + (circleDistanceY - hole.height/2)**2;

            return (cornerDistance_sq <= (self.__treasureRadius**2));
        else: # __rectangularTreasure == True
            topLeftHole = (hole.centreX - hole.width/2, hole.centreY - hole.height/2);
            topRightHole = (hole.centreX + hole.width/2, hole.centreY - hole.height/2);
            bottomLeftHole = (hole.centreX - hole.width/2, hole.centreY + hole.height/2);
            bottomRightHole = (hole.centreX + hole.width/2, hole.centreY + hole.height/2);
            if self.__pointIntersectsTreasure(topLeftHole[0], topLeftHole[1]):
                return True;
            if self.__pointIntersectsTreasure(topRightHole[0], topRightHole[1]):
                return True;
            if self.__pointIntersectsTreasure(bottomLeftHole[0], bottomLeftHole[1]):
                return True;
            if self.__pointIntersectsTreasure(bottomRightHole[0], bottomRightHole[1]):
                return True;
            return False;

    # returns True if newHole intersects an existing hole on the field.
    # This is useful if the layout algorithm doesn't want to place two
    # holes on the field that overlap.
    def intersectsExistingHole(self, newHole:Hole) -> bool:
        newLX = newHole.centreX - newHole.width/2;
        newBY = newHole.centreY + newHole.height/2;
        newRX = newHole.centreX + newHole.width/2;
        newTY = newHole.centreY - newHole.height/2;
        for h in self.holes:
            hLX = h.centreX - h.width/2;
            hBY = h.centreY + h.height/2;
            hRX = h.centreX + h.width/2;
            hTY = h.centreY - h.height/2;

            if newBY > hTY and newTY < hBY and newRX > hLX and newLX < hRX:
                return True;
        return False;

    # place a circular treasure on the field at a random position, of given radius.
    # The treasure will be placed wholly within the field.
    def placeCircularTreasure(self, radius:float):
        if (self.height < radius * 2 or self.width < radius * 2):
            print("field not big enough for treasure");
            exit(1);

        self.__treasureCentreX = random.random() * (self.width - 2*radius) + radius;
        self.__treasureCentreY = random.random() * (self.height - 2*radius) + radius;
       
        self.__rectangularTreasure = False;
        self.__treasureRadius = radius;
        self.__treasurePlaced = True;
    
    # places a rectangular treasure of given width and height randomly on the field.
    # Treasure will be placed wholly within the field.
    def placeRectangularTreasure(self, width:float, height:float):
        if (width > self.width or height > self.height):
            print("field not big enough for treasure");
            exit(1);
        self.__treasureCentreX = (random.random() * (self.width - width/2 - width/2)) + width/2;
        self.__treasureCentreY = (random.random() * (self.height - height/2 - height/2)) + height/2;

        self.__treasureWidth = width;
        self.__treasureHeight = height;
        
        self.__rectangularTreasure = True;
        self.__treasurePlaced = True;

    # digs a hole centered at the given coordinates, returning True iff
    # the hole intersects the treasure on the field. Assumes a treasure has been placed.
    def digHole(self, holeSize:float, centreX:float, centreY:float) -> bool:
        if not(self.__treasurePlaced):
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
        
        # used in testing
        # if (self.adjustedHoleAtBorder):
        #     pass;
        
        if centreX + holeSize/2 > self.width:
            print("hole out of x bounds");
        if centreY + holeSize / 2 > self.height:
            print("hole out of y bounds");
        hole = Hole(centreX, centreY, holeSize, holeSize);
        self.holes.append(hole);
        return self.__intersectsTreasure(hole);

    # prints the field data (holes and treasure placement) to a text file.
    # first line is the string "intersect", second line is field dimensions,
    # third line is the string "circularTreasure" or "rectangularTreasure"
    # fourth line is treasure dimensions
    # the following lines are the hole locations and dimensions and whether it uncovers treasure, one line per hole
    def print(self, fileName:str = ""):
        if fileName != "":
            output = open(fileName, 'w');
        else:
            output = sys.stdout;
        print("intersect", file=output);
        print(self.width, self.height, file=output);
        if self.__rectangularTreasure == False:
            print("circularTreasure:", self.__treasureCentreX, self.__treasureCentreY, self.__treasureRadius, file=output);
        else:
            print("rectangularTreasure:", self.__treasureCentreX, self.__treasureCentreY, self.__treasureWidth, self.__treasureHeight, file=output);
        for h in self.holes:
            print("hole:", h.centreX, h.centreY, h.width, h.height, self.__intersectsTreasure(h), file=output);
            
# This class encapsulates data for locations of individual artefacts, read from a csv file.
# The file has first line "<ignored>, xcoord, ycoord".
# The following lines each have three comma separated values, the first is ignored,
# the next is the x coordinate of the artefact, the third is the y coordinate of the artefact.
#
# As the number of artefacts can be large, they are stored as a grid of data parcels
# in self.__artefacts. self.__artefacts[i][j] contains a list of artefacts. An
# artefact at location a,b (floats) is stored in self.__artefacts[floor(a)][floor(b)]
# and so can be located easily.
#
# It also allows this treasure definition to be placed at a position on a field,
# rather than a field having to transpose each artefact.
class RealWorldData:
    # a data parcel of artefacts, stored in a list of (x,y) tuples
    class DataParcel:
        def __init__(self):
            self.artefacts = [];
            self.__numArtefacts = 0;
    
        # add an artefact to the data parcel at the given coordinates
        def addArtefact(self, x:float, y:float):
            self.artefacts.append((x,y));
            self.__numArtefacts += 1;

        def print(self):
            print(self.__numArtefacts, "", end='');
            
    # csvFileName is the name of the file specifying the location of artefacts.
    # see class documentation for the expected format
    def __init__(self, csvFileName:str):
        csvfile = open(csvFileName,'r');
        lines = csv.DictReader(csvfile, delimiter=',');
        self.__rawArtefacts = [];
        self.minX = -1;
        self.maxX = -1;
        self.minY = -1;
        self.maxY = -1;
        for row in lines:
            x = float(row['xcoord']);
            y = float(row['ycoord']);
            # keep track of the minimum and maximum x and y coordinates of artefacts
            self.__setMinX(x);
            self.__setMaxX(x);
            self.__setMinY(y);
            self.__setMaxY(y);

            self.__rawArtefacts.append((x,y));
    
        # assume min values are 0
        if math.floor(self.minX) != 0 or math.floor(self.minY) != 0:
            print("error: real world data does not start at (0,0)");
        
        # create a 2D array of DataParcels, see class documentation for explanation
        self.__artefacts = [[self.DataParcel() for y in range(math.ceil(self.maxY))] for x in range(math.ceil(self.maxX))];

        for i in range(len(self.__rawArtefacts)):
            x = self.__rawArtefacts[i][0];
            y = self.__rawArtefacts[i][1];
            self.__artefacts[math.floor(x)][math.floor(y)].addArtefact(x,y);
        #print("rwdata units maxX:", self.maxX, "maxY:", self.maxY);
        
    def print(self):
        for i in range(len(self.__artefacts)):
            for j in range(len(self.__artefacts[i])):
                self.__artefacts[i][j].print();
            print();
    
    # place the real world site so that the top left corner is at the given coordinates.
    # This top left coordinate is used when determining if a hole uncovers an artefact.
    def placeTopLeft(self, x:float, y:float):
        self.topLeftX = x;
        self.topLeftY = y;

    # Methods to keep track of the minimum and maximum coordinates for read world artefact data.
    def __setMinX(self, x:float):
        if self.minX == -1 or x < self.minX:
            self.minX = x;
    
    def __setMaxX(self, x:float):
        if self.maxX == -1 or x > self.maxX:
            self.maxX = x;

    def __setMinY(self, y:float):
        if self.minY == -1 or y < self.minY:
            self.minY = y;
    
    def __setMaxY(self, y:float):
        if self.maxY == -1 or y > self.maxY:
            self.maxY = y;

    # Returns the number of artefacts uncovered by the given hole
    def numArtefactsInHole(self, hole:Hole) -> int:

        # test against raw data
        # this code can be uncommented to test that the data parcel optimization
        # is behaving correctly by testing against the raw artefact data
        # rawArtefactCount = 0;
        # for i in range(len(self.__rawArtefacts)):
        #     (x,y) = self.__rawArtefacts[i];
        #     if hole.centreX - hole.width/2 < self.topLeftX + x and \
        #         hole.centreX + hole.width/2 > self.topLeftX + x and \
        #         hole.centreY - hole.height/2 < self.topLeftY + y and \
        #         hole.centreY + hole.height/2 > self.topLeftY + y:
        #             rawArtefactCount += 1;
        # if (rawArtefactCount > 0):
        #     print("raw data:", rawArtefactCount);

        # get the left, right, top, and bottom of the hole
        left = hole.centreX - hole.width/2;
        right = hole.centreX + hole.width/2;
        top = hole.centreY - hole.height/2;
        bottom = hole.centreY + hole.height/2;

        # if the hole isn't within the minimum and maximum borders of the treasure site
        # return 0
        if left > self.topLeftX + self.maxX or \
            right < self.topLeftX + self.minX or \
            top > self.topLeftY + self.maxY or \
            bottom < self.topLeftY + self.minY:
            return 0;

        # determine in which data parcels we should look for artefacts
        startX = math.floor(max(left, self.topLeftX) - self.topLeftX);
        endX = math.floor(min(right, self.topLeftX + self.maxX) - self.topLeftX); 
        startY = math.floor(max(top, self.topLeftY) - self.topLeftY);
        endY = math.floor(min(bottom, self.topLeftY + self.maxY) - self.topLeftY); #inclusive

        # for each data parcel of interest, examine its list of artefacts and check if it
        # is within the hole
        artefactCount = 0;
        try:
            for x in range(startX, endX + 1):
                for y in range(startY, endY + 1):
                    parcel = self.__artefacts[x][y];
                    for i in range(len(parcel.artefacts)):
                        artefactX = self.topLeftX + parcel.artefacts[i][0];
                        artefactY = self.topLeftY + parcel.artefacts[i][1];
                        if left < artefactX and \
                            right > artefactX and \
                            top < artefactY and \
                            bottom > artefactY:
                            artefactCount += 1;
            # if (artefactCount != rawArtefactCount):
            #     print("** error");
            return artefactCount;
        except:
            print("error:", x, "artefact max:", len(self.__artefacts));
            print(traceback.print_exc())
            exit();
    
    # print out the artefacts in all data parcels to the given file
    def print(self, file):
        for i in range(len(self.__artefacts)):
            for j in range(len(self.__artefacts[i])):
                for k in range(len(self.__artefacts[i][j].artefacts)):
                    print("artefact:", self.__artefacts[i][j].artefacts[k][0] + self.topLeftX, self.__artefacts[i][j].artefacts[k][1] + self.topLeftY, file=file);


# a Field of the given size in which the treasure is defined by data of individual artefacts,
# encapsulated by a RealWorldData object.
class RealWorldField(Field):
    def __init__(self, width:int, height:int):
        self.width = width;
        self.height = height;
        # the holes on the Field
        self.__holes = [];
        self.__treasurePlaced = False;

    # Place the treasure defined by individual artefact data.
    # If the data argument is provided, it will be used. If not,
    # data will be read from the file of the given name.
    # This is to avoid having to read from the file repeatedly which is time consuming.
    def placeRealWorldTreasure(self, csvFileName:str = "", data:RealWorldData = None):
        if (data == None):
            self.__data = RealWorldData(csvFileName);
        else:
            self.__data = data;

        # check the treasure will fit
        if self.__data.maxX > self.width or self.__data.maxY > self.height:
            print("treasure doesn't fit on the field");
            exit();

        # now place it randomly on field
        topLeftX = random.random() * (self.width - self.__data.maxX);
        topLeftY = random.random() * (self.height - self.__data.maxY);
        
        self.__data.placeTopLeft(topLeftX, topLeftY);
        self.__treasurePlaced = True;

    # return the RealWorldData object which defines the treasure. This is useful so
    # it can be re-used to avoid repeatedly reading data from the file
    def getData(self) -> RealWorldData:
        return self.__data;

    # dig a hole of the given size at the given coordinates.
    # Returns True if the hole uncovers artefacts, otherwise False.
    # After calling this, self.artefactCount gives number of artefacts within hole.
    def digHole(self, holeSize:float, centreX:float, centreY:float) -> bool:
        if not(self.__treasurePlaced):
            print("define treasure before placing holes");
            exit();
        if centreX - holeSize/2 < 0:
            centreX = holeSize/2;
        elif centreX + holeSize/2 > self.width:
            centreX = self.width - holeSize/2;
        if centreY - holeSize/2 < 0:
            centreY = holeSize/2;
        elif centreY + holeSize/2 > self.height:
            centreY = self.height - holeSize/2;
        hole = Hole(centreX, centreY, holeSize, holeSize);
        self.__holes.append(hole);
        return self.__intersectsTreasure(hole);

    # returns True if the hole uncovers any artefacts, otherwise False.
    # Also sets self.artefactCount to the number of artefacts uncovered by the hole.
    def __intersectsTreasure(self, hole:Hole) -> bool:
        self.artefactCount = self.__data.numArtefactsInHole(hole);

        if (self.artefactCount > 0):
            return True;
        return False;

    # returns True if newHole intersects an existing hole on the field.
    # This is useful if the layout algorithm doesn't want to place two
    # holes on the field that intersect each other.
    def intersectsExistingHole(self, newHole:Hole) -> bool:
        # establish top, bottom, left, and right of newHole
        newLX = newHole.centreX - newHole.width/2;
        newBY = newHole.centreY + newHole.height/2;
        newRX = newHole.centreX + newHole.width/2;
        newTY = newHole.centreY - newHole.height/2;

        # for each hole in the Field, check if it intersects newHole, returning
        # True if it does
        for h in self.__holes:
            hLX = h.centreX - h.width/2;
            hBY = h.centreY + h.height/2;
            hRX = h.centreX + h.width/2;
            hTY = h.centreY - h.height/2;

            if newBY > hTY and newTY < hBY and newRX > hLX and newLX < hRX:
                return True;
    
        # no intersecting hole was found
        return False;

    # prints the field data (holes and treasure placement) to a text file.
    # first line is the string "realworld", second line is field dimensions,
    # third line is the string "realworldtreasure"
    # fourth line is treasure dimensions (bounding box).
    # the following lines are the hole locations and dimensions and whether it uncovers treasure, one line per hole
    def print(self, fileName = ""):
        if fileName != "":
            output = open(fileName, 'w');
        else:
            output = sys.stdout;
        print("realworld", file=output);
        print(self.width, self.height, file=output);
        print("realworldtreasure:", self.__data.minX + self.__data.topLeftX, self.__data.minY + self.__data.topLeftY, \
                    self.__data.maxX + self.__data.topLeftX, self.__data.maxY + self.__data.topLeftY, file=output);
        self.__data.print(output);
        # for i in range(len(self.__artefacts)):
        #     print("artefact:", self.__artefacts[i][0], self.__artefacts[i][1], file=output);
        for h in self.__holes:
            print("hole:", h.centreX, h.centreY, h.width, h.height, self.__intersectsTreasure(h), file=output);
        output.close();


# An archaeologist that places holes in a field according to its layout strategy.
# It is usually provided with a Field and the desired number of holes to dig.
# The actual number of holes dug may differ from the desired due to layout
# constraints.
# It is assumed that subclasses dig the same number of holes when the parameters
# supplied are the same (e.g. desired number of holes).
class Player:
    # makes holes and returns tuple indicating if treasure was found
    # and the actual number of holes dug.
    # If the field is a RealWorldField, after calling this method
    # self.artefactCount is the number of artefacts uncovered during the dig
    # and self.numHolesSucceeded is the number of holes that uncovered an artefact.
    def play(self) -> tuple[bool, int]:
        return False, 0;

# an abstract Player that provides support for a staggered layout
class StaggeredPlayer(Player):
    # Create a staggered layout with the given parameters.
    # If the field is a RealWorldField, sets self.numHolesSucceed and self.artefactCount
    def doStaggeredLayout(self, field:Field, holeSize:float, xHoles:int, borderX:float, dX:float, yHoles:int, borderY:float, dY:float, staggerY:bool) -> tuple[bool, float]:
        row = 0;
        holesMade = 0;
        found = False;
        self.numHolesSucceed = 0;
        self.artefactCount = 0;
        for y in range (yHoles):
            # a new row. set the starting x and y positions for the first hole
            pos_x = borderX;
            pos_y = borderY + dY * y;
            if (row % 2 != 0):
                # stagger the even rows
                pos_x += dX / 2;
            
            for x in range (xHoles):
                # stagger the odd columns if staggerY is True 
                if staggerY:
                    if (x % 2 == 0):
                        pos_y = borderY + dY * y;
                    else:
                        pos_y = borderY + (dY / 2) + dY * y;
                
                # dig a hole
                hit = field.digHole(holeSize, pos_x, pos_y);
                # found records whether or not any hole so far has found treasure
                found = found or hit;
                if (hit):
                    self.numHolesSucceed += 1;

                    if (isinstance(field, RealWorldField)):
                        self.artefactCount += field.artefactCount;
                holesMade += 1;
                pos_x += dX;
            row += 1;
        return found, holesMade;


# a Player that uses a scrambled 2-D halton distribution of holes
class HaltonPlayer(Player):
    def __init__(self, field:Field, holeSize:float, numHoles:int, border:bool=False):
        self.__field = field;
        self.__holeSize = holeSize;
        self.__numHoles = numHoles;
        if self.__field.width != self.__field.height:
            print("non square field not supported");
            exit();
        if (border):
            self.__border = (self.__field.width / math.sqrt(self.__numHoles)) / 2;
        else:
            self.__border = 0;

    def play(self) -> tuple[bool, int]:
        sampler = qmc.Halton(d=2, scramble=True);
        sample = sampler.random(n=self.__numHoles);
        points = sample;
        found = False;
        self.artefactCount = 0;
        self.numHolesSucceed = 0;
        for p in points:
            x = p[0] * (self.__field.width - 2*self.__border) + self.__border;
            y = p[1] * (self.__field.height - 2*self.__border) + self.__border;
            hit = self.__field.digHole(self.__holeSize, x, y);
            if (hit):
                self.numHolesSucceed += 1;
                if (isinstance(self.__field, RealWorldField)):
                    self.artefactCount += self.__field.artefactCount;
            found = hit or found;
        return found, self.__numHoles;

# A Player that uses the hexagonal-like layout algorithm
# (see "size matter layout algorithms.pdf").
# This player is staggered horizontally - If the distance between holes
# in the same row is a, every other row is shifted right by a/2.
# If LRBorder (left and right border) is True, each even row
# has a border of a/2 (and so the border for each odd row is a as it is staggered).
# If the distance between rows is c, the top and bottom borders are c/2.
# If staggerY is True, each second hole in each row is shifted down by c/2.
# Note that staggerY was always False for the experiments in the article.
# Numbers of holes in a row and the number of rows are chosen
# to be close to the desired number of holes while also being close
# to hexagonal
class HexagonalLikePlayer(StaggeredPlayer):
    def __init__(self, field:Field, holeSize:float, numHoles:int, LRBorder:bool = True, staggerY:bool = False):
        # these are not private as subclasses may want them
        self.field = field;
        self.holeSize = holeSize;
        self.numHoles = numHoles;
        self.LRBorder = LRBorder;
        self.staggerY = staggerY;

    # perform the quadratic formula calculation
    def quadratic(self, a:float, b:float, c:float) -> float:
        x1 = (-1 * b + math.sqrt(b**2 - 4 * a * c)) / (2 * a);
        x2 = (-1 * b - math.sqrt(b**2 - 4 * a * c)) / (2 * a);
        if x1 > 0:
            return x1;
        else:
            return x2;

    # revises the numbers of holes in a row (xf) and the number of rows (yf)
    # to be integers
    def __reviseNumHoles(self, n:int, xf:float, yf:float) -> tuple[int, int]:
        return (round(xf), round(yf));

    # on return self.layoutError is True if the algorithm was unable to
    # fit the number of holes on the field, otherwise False.
    def play(self) -> tuple[bool, int]:
        if (self.LRBorder):
            # calculate number of holes in a row according to the hexagonal-like formula
            numHoles_x = self.quadratic(2 * self.field.height, self.field.height, -1 * math.sqrt(3) * self.numHoles * self.field.width);
            if self.staggerY:
                numHoles_x = self.quadratic(
                    4 * self.field.height, 2 * self.field.height - math.sqrt(3) * self.field.width, \
                    -2 * math.sqrt(3) * self.numHoles * self.field.width);
        else:
            if self.staggerY:
                print("stagger with no border not supported");
                exit();
            numHoles_x = self.quadratic(2 * self.field.height, -1 * self.field.height, -1 * math.sqrt(3) * self.numHoles * self.field.width);
        
        # calculate number of rows
        numHoles_y = self.numHoles / numHoles_x;

        # turn our floats into integers
        actualNumHoles = self.__reviseNumHoles(self.numHoles, numHoles_x, numHoles_y);
        
        # d_x is the distance between holes in the same row
        if (self.LRBorder):
            self.d_x = self.field.width / (actualNumHoles[0] + 0.5);
        else:
            self.d_x = (self.field.width - self.holeSize) / (actualNumHoles[0] - 0.5);
#            self.d_x = self.field.width / (actualNumHoles[0] - 0.5);
        
        # d_y is the distance between rows
        if self.staggerY:
            self.d_y = self.field.height / (actualNumHoles[1] + 0.5);
        else:
            self.d_y = self.field.height / actualNumHoles[1];

        # the sizes of the horizontal and vertical borders
        if self.LRBorder:
            border_x = self.d_x / 2;
        else:
            border_x = self.holeSize / 2;
        border_y = self.d_y / 2;

        # check that the holes fit on the field
        self.layoutError = False;
        if self.d_x < self.holeSize or self.d_y < self.holeSize:
            self.layoutError = True;

        return self.doStaggeredLayout(self.field, self.holeSize, actualNumHoles[0], border_x, self.d_x, actualNumHoles[1], border_y, self.d_y, self.staggerY);


# a Player that adjusts the horizontal and vertical borders used in the
# HexagonalLikePlayer to make the layout truly hexagonal.
# This may not be the best way to implement a hexagonal layout.
# This player staggers holes horizontally - if the distance between holes
# in the same row is a, each even row is shifted right by a/2.
# If staggerY is True, each second hole in each row is shifted down by c/2.
# Note that staggerY was always False for the experiments in the article.
class HexagonalPlayer(HexagonalLikePlayer):
    # staggerY is true if you want to stagger the columns of holes vertically.
    # The holes will always be staggered horizontally. 
    def __init__(self, field:Field, holeSize:float, numHoles:int, staggerY:bool = False):
        HexagonalLikePlayer.__init__(self, field, holeSize, numHoles, True, staggerY);
    
    # revises the numbers of holes in a row (xf) and the number of rows (yf)
    # to be integers
    def __reviseNumHoles(self, n:int, xf:float, yf:float) -> tuple[int, int]:
        return (round(xf), round(yf));

    # on return self.layoutError is True if the algorithm was unable to
    # create a hexagonal layout, otherwise False
    def play(self) -> tuple[bool, int]:
        # calculate number of holes in a row according to the hexagonal-like formula
        numHoles_x = self.quadratic(2 * self.field.height, self.field.height, -1 * math.sqrt(3) * self.numHoles * self.field.width);

        if self.staggerY:
            numHoles_x = self.quadratic(
                4 * self.field.height, 2 * self.field.height - math.sqrt(3) * self.field.width, \
                -2 * math.sqrt(3) * self.numHoles * self.field.width);
        
        # calculate number of rows
        numHoles_y = self.numHoles / numHoles_x;

        actualNumHoles = [round(numHoles_x), round(numHoles_y)];


        # fix the vertical border and c to their original values and adjust the horizontal border
        # and a to create a hexagonal layout
        if self.staggerY:
            c = self.field.height / (actualNumHoles[1] + 0.5)
        else:
            c = self.field.height / actualNumHoles[1];
        a = 2 * c / math.sqrt(3);
        border_x = (self.field.width - a * ((actualNumHoles[0]) - 0.5)) / 2;
        border_y = c/2;

        self.layoutError = False;

        # check if horizontal border is big enough to fit a hole at the edge, otherwise
        # set it to its minimum value and recalculate a, c, and border_y
        self.adjust = False;
        unexpected = False;
        if a < self.holeSize or border_y < self.holeSize / 2 or c < self.holeSize:
            unexpected = True;
        if border_x < self.holeSize / 2:
            self.adjust = True;
            a = (self.field.width - self.holeSize) / (actualNumHoles[0] - 0.5)
            c = (math.sqrt(3) * a) / 2
            border_x = self.holeSize / 2;
            if self.staggerY:
                border_y = (self.field.height - c * (actualNumHoles[1] - 0.5)) / 2
            else:
                border_y = (self.field.height - c * (actualNumHoles[1] - 1)) / 2
        
        # check if the new values allow the holes to fit on the field
        if border_x < self.holeSize / 2 or a < self.holeSize or border_y < self.holeSize / 2 or c < self.holeSize:
            self.layoutError = True;
        elif unexpected:
            print("unexpected case in HexagonalPlayer");

        return self.doStaggeredLayout(self.field, self.holeSize, actualNumHoles[0], border_x, a, actualNumHoles[1], border_y, c, self.staggerY);

# A Player that places holes in a staggered grid, using the given
# number of holes in a row (xHoles) and number of rows (yHoles).
# Horizontal and vertical borders are half the distance between holes and rows
# respectively. The Player will also stagger the columns if staggerY is True.
class SpecifiedGridPlayer(StaggeredPlayer):
    def __init__(self, field:Field, holeSize:float, xHoles:int, yHoles:int, staggerY:bool = False):
        self.__field = field;
        self.__holeSize = holeSize;
        self.__xHoles = xHoles;
        self.__yHoles = yHoles;
        self.__staggerY = staggerY;

    # after calling, self.layoutError is True if the holes don't fit on the field
    def play(self) -> tuple[bool, int]:
        d_x = self.__field.width / (self.__xHoles + 0.5)
        if self.__staggerY:
            d_y = self.__field.height / (self.__yHoles + 0.5);
        else:
            d_y = self.__field.height / self.__yHoles;

        border_x = d_x / 2;
        border_y = d_y / 2;

        self.layoutError = False;
        if (border_x < self.__holeSize/2) or (border_y < self.__holeSize/2):
            self.layoutError = True;
        
        return self.doStaggeredLayout(self.__field, self.__holeSize, self.__xHoles, border_x, d_x, self.__yHoles, border_y, d_y, self.__staggerY);

# A Player that places holes randomly on the Field.
# Holes do not overlap.
#
# If too many holes are asked for (i.e. they don't all fit), play() will never return.
#
# For efficiency considerations the field is divided into buckets
# of length and width one tenth of the field, and holes in each bucket
# stored in a 2-D list
class RandomPlayer(Player):
    def __init__(self, field:Field, holeSize:float, numHoles:int, border:bool = False):
        self.__numHoles = numHoles;
        self.__field = field;
        self.__holeSize = holeSize;
        self.__numHorizontalParcels = math.ceil(10);
        self.__numVerticalParcels = math.ceil(10);
        self.__holePositions = [[[] for y in range(self.__numVerticalParcels)] for x in range(self.__numHorizontalParcels)];
        if self.__field.width != self.__field.height:
            print("non square fields not supported");
            exit();
        if border:
            self.__border = (self.__field.width / math.sqrt(numHoles)) / 2 ;
        else:
            self.__border = 0;
    
    def __intersectsExistingHole(self, newHole:Hole) -> bool:
        # assumes all holes on the field are of self.__holeSize
        bucketWidth = self.__field.width / 10;
        bucketHeight = self.__field.height / 10;
        startXBucket = math.floor((newHole.centreX - self.__holeSize) / bucketWidth);
        startYBucket = math.floor((newHole.centreY - self.__holeSize) / bucketHeight);
        endXBucket = math.floor((newHole.centreX + self.__holeSize) / bucketWidth);
        endYBucket = math.floor((newHole.centreY + self.__holeSize) / bucketHeight);
        if startXBucket < 0:
            startXBucket = 0;
        if startYBucket < 0:
            startYBucket = 0;
        if endXBucket >= self.__numHorizontalParcels:
            endXBucket = self.__numHorizontalParcels - 1;
        if endYBucket >= self.__numVerticalParcels:
            endYBucket = self.__numVerticalParcels - 1;
        
        newLX = newHole.centreX - newHole.width/2;
        newBY = newHole.centreY + newHole.height/2;
        newRX = newHole.centreX + newHole.width/2;
        newTY = newHole.centreY - newHole.height/2;

        for xBucket in range(startXBucket, endXBucket + 1):
            for yBucket in range(startYBucket, endYBucket + 1):
                length = len(self.__holePositions[xBucket][yBucket]);
                expected = (self.__numHoles / ((self.__field.width / 10) * (self.__field.height / 10)));
                
                for i in range(len(self.__holePositions[xBucket][yBucket])):
                    h = self.__holePositions[xBucket][yBucket][i]
                    hLX = h[0] - self.__holeSize/2;
                    hBY = h[1] + self.__holeSize/2;
                    hRX = h[0] + self.__holeSize/2;
                    hTY = h[1] - self.__holeSize/2;

                    if newBY > hTY and newTY < hBY and newRX > hLX and newLX < hRX:
                        check = self.__field.intersectsExistingHole(newHole);
                        if not(check):
                            print("**error")
                        return True;
        check = self.__field.intersectsExistingHole(newHole);
        if check:
            print("**error")
        return False;

    # note: holes don't overlap. If not all holes fit on the field this will never return
    def play(self) -> tuple[bool, int]:
        h = 0;
        found = False;
        self.numHolesSucceed = 0;
        self.artefactCount = 0;
        while h < self.__numHoles:
            x = random.random() * (self.__field.width - 2*self.__border) + self.__border;
            y = random.random() * (self.__field.height - 2 * self.__border) + self.__border;
            hole = Hole(x, y, self.__holeSize, self.__holeSize);
            if not(self.__intersectsExistingHole(hole)):
                hit = self.__field.digHole(self.__holeSize, x, y);
                eachBucketWidth = self.__field.width / 10;
                eachBucketHeight = self.__field.height / 10;
                try:
                    self.__holePositions[math.floor(x/eachBucketWidth)][math.floor(y/eachBucketHeight)].append((x,y));
                except:
                    print ("error at x =", x, "eachBucketWidth =", eachBucketWidth, "y =", y);
                found = found or hit;
                if (hit):
                    self.numHolesSucceed += 1;
                    if (isinstance(self.__field, RealWorldField)):
                        self.artefactCount += self.__field.artefactCount;
                h += 1;
        return found, h;

# A Player that places holes in a plain grid
class NonStaggeredPlayer(Player):
    def __init__(self, field:Field, holeSize:float, numHoles:int):
        self.__numHoles = numHoles;
        self.__field = field;
        self.__holeSize = holeSize;

    def play(self) -> tuple[bool, int]:
        xHoles = yHoles = round(math.sqrt(self.__numHoles));
        s = self.__field.width / xHoles;
        found = False;
        numHolesDug = 0;
        for y in range (yHoles):
            holeY = round(s/2 + y * s);
            for x in range (xHoles):
                holeX = round(s/2 + x*s);
                hit = self.__field.digHole(self.__holeSize, holeX, holeY);
                found = found or hit;
                numHolesDug += 1;
        return found, numHolesDug;

# debugging function to examine how hexagonal the layout of holes on a Field is.
# Prints the horizontal distance between the first two holes on the first row,
# and the diagonal distance between the first hole on the first row and the
# first hole on the second row.
# Assumes these holes exist.
def calculateHoleDistances(field:Field, doPrint:bool = True) -> tuple[float, float]:
    if len(field.holes) < 2:
        horizontalDistance = 0;
        firstRowY = 0;
    else:
        firstRowFirstHole = field.holes[0];
        firstRowSecondHole = field.holes[1];
        horizontalDistance = firstRowSecondHole.centreX - firstRowFirstHole.centreX;
        firstRowY = firstRowFirstHole.centreY;
    if doPrint:
        print(horizontalDistance, " ", end='');
    
    currentHole = 0
    while(currentHole < len(field.holes) and field.holes[currentHole].centreY == firstRowY):
        currentHole += 1;
    if currentHole == 0 or currentHole == len(field.holes) or field.holes[currentHole].centreY == firstRowY:
        verticalDistance = 0;
    else:
        secondRowFirstHole = field.holes[currentHole];
        verticalDistance = secondRowFirstHole.centreY - firstRowFirstHole.centreY;
    if verticalDistance == 0:
        a = 0;
    else:
        x = secondRowFirstHole.centreX - firstRowFirstHole.centreX;
        y = secondRowFirstHole.centreY - firstRowFirstHole.centreY;
        a = math.sqrt(x**2 + y**2);
    if doPrint:
        print(a);
    return horizontalDistance, a;


# test hexagonality. Change values of fieldFileName, field size, player arguments,
# treasure size and shape, player type as desired
def testHexagonality() -> None:
    fieldFileName = "hexagonalLike.field200.treasure7";
    field = IntersectField(200, 200);
    player = HexagonalLikePlayer(field, 1, 20, True, True); #Note stagger Y on
    player = HexagonalPlayer(field, 1, 25, False);
    #player = SpecifiedGridPlayer(field, 1, 5, 5, True);
    #player = NonStaggeredPlayer(field, 1, 25);
    #player = RandomPlayer(field, 1, 18, True);
    #player = HexagonalPlayer\(field, 1, 80);
    #player = HaltonPlayer(field, 2, 2, 50);
    #field.placeRectangularTreasure(60, 6.67);
    field.placeCircularTreasure(3,5);
    result = player.play();
    print ("hit:", result[0], "numHoles:", result[1]);
    field.print(fileName=fieldFileName);
    calculateHoleDistances(field);

def printField(field:Field, realWorldData:bool, treasureShape:str, fieldSize:int, holeSize:float, treasureRadius:float, treasureWidth:float, treasureHeight:float, holesDug:int, playerClass:str):
    if realWorldData:
        filename = "realWorldField " + str(fieldSize) + " holesize " + str(holeSize) + " holes " + str(holesDug) + " " + playerClass;
    elif treasureShape == "circle":
        filename = "intersectField " + str(fieldSize) + " holesize " + str(holeSize) + " treasure " + str(treasureRadius) + " holes " + str(holesDug) + " " + playerClass;
    else:
        filename = "intersectField " + str(fieldSize) + " holesize " + str(holeSize) + " treasure " + str(treasureWidth) + "x" + str(treasureHeight) + " holes " + str(holesDug) + " " + playerClass;
    field.print(filename);


# do experiments with specific numbers of holes. Change the values of the variables
# to fit the experiment. Also change the class of the Player.
def doSpecificGridExperiment() -> None:

    #==================================================================================
    # Change these variable values to specify an experiment.
    # Also change the subclass of Player that is created later in the function
    # (search "player creation").
    # To decide when to print out the field during the simulation
    # search "print field decision".

    holeSize = 0.5; # 0.5 or 1 in the article
    
    numRepeats = 100000; # can reduce to 10000 or any desired value
    fieldSize = 100;

    # numbers of holes in the x and y directions for players that take them e.g. SpecifiedGridPlayer
    xyParameters = [(2, 3), (3, 4), (3, 6), (4, 6)];
    # total number of holes for players that take them, e.g. RandomPlayer
    numParameters = [6, 12, 18, 24];

    # set this to True if using xyParameters, False if using numParameters
    isXyParameters = True;

    # set this to stagger in the Y direction for players that offer this option
    staggerY = False;

    # set this to True if using real world data, False for intersect experiments
    realWorldData = False;
    # if realWorldData is True, set the filename where the data is to be found
    realWorldDataFile = "real world data/Moderate Density Artefact Coordinates.csv";

    # for intersect case, when realWorldData is False, the treasure is either a "circle" or "rectangle"
    treasureShape = "circle"; # circle or "rectangle"
    # when treasure is a circle, this is the radius (note diameter is quoted in the article)
    treasureRadius = 3.5;
    # when treaure is a rectangle, these are the dimensions
    treasureWidth = 20;
    treasureHeight = 5;
    #==================================================================================

    # determine the number of iterations
    if isXyParameters:
        length = len(xyParameters);
    else:
        length = len(numParameters);

    for i in range(length):
        # on the first iteration, print the experiment data
        if (i == 0 and realWorldData):
            if isXyParameters:
                print("real world, field size:", fieldSize, "hole size:", holeSize, "staggerY:", staggerY);
            else:
                print("real world, field size:", fieldSize, "hole size:", holeSize, "staggerY:", staggerY);
        elif i==0:
            # using a treasure shape
            if treasureShape == "circle":
                print("circle, field:", fieldSize, "hole size:", holeSize, "treasure radius:", treasureRadius, "staggerY:", staggerY);
            else:
                # treasure is rectangle
                print("rectangle, field:", fieldSize, "hole size:", holeSize, "treasure dimensions:", str(treasureWidth) + "x" + str(treasureHeight), "staggerY:", staggerY);

        successes = 0;
        realWorldDataCache = None;
        artefactCount = 0;
        numHolesSucceed = 0;
        for repeats in range(numRepeats):
            if (realWorldData):
                field = RealWorldField(fieldSize, fieldSize);
                if (realWorldDataCache == None):
                    field.placeRealWorldTreasure(csvFileName=realWorldDataFile);
                    realWorldDataCache = field.getData();
                else:
                    field.placeRealWorldTreasure(data=realWorldDataCache);
            else:
                field = IntersectField(fieldSize, fieldSize);
                if treasureShape == "circle":
                    field.placeCircularTreasure(treasureRadius);
                else:
                    field.placeRectangularTreasure(treasureWidth, treasureHeight);
        
            # player creation: specify the Player to use
            # for number of holes specified by the xyParameters list use SpecifiedGridPlayer
            # instead of HexagonalLikePlayer
            player = SpecifiedGridPlayer(field, holeSize, xyParameters[i][0], xyParameters[i][1], staggerY);
            #player = RandomPlayer(field, holeSize, numParameters[i], True);
            #player = HaltonPlayer(field, holeSize, numParameters[i], True);
            #player = HexagonalLikePlayer(field, holeSize, numParameters[i], True, staggerY);
            #player = HexagonalPlayer(field, holeSize, numParameters[i], staggerY);

            if i == 0 and repeats == 0:
                # on the first iteration, print the player class name
                print(player.__class__.__name__);
            result = player.play();
            holesDug = result[1];

            if repeats == 0 and (isinstance(player, HexagonalPlayer) or isinstance(player, HexagonalLikePlayer)\
                or isinstance(player, SpecifiedGridPlayer)):
                if player.layoutError:
                    print("layout algorithm error: probably too many holes for the field size");
            
            # print field decision: set when to print the field out to a file.
            # Can be set to final number of holes, or to False, and then
            # specify numbers of holes
            # doPrint = False;
            doPrint = (i == length -1);
            # if isXyParameters:
            #     #doPrint = (xyParameters[i][0] == 4 and xyParameters[i][1] == 6);
            # else:
            #     doPrint  = numParameters[i] == 18;
            if repeats == 0 and doPrint:
                printField(field, realWorldData, treasureShape, fieldSize, holeSize, treasureRadius, treasureWidth, treasureHeight, holesDug, player.__class__.__name__);
                
            if result[0]:
                successes += 1;
                if (realWorldData):
                    artefactCount += player.artefactCount;
                    numHolesSucceed += player.numHolesSucceed;

        # if isXyParameters:
        #     numHoles = xyParameters[i][0] * xyParameters[i][1];
        # else:  
        #     numHoles = numParameters[i];
        # print the collected results for this iteration of i (this number of holes)
        if (realWorldData):
            print(holesDug, successes * 100 / numRepeats, artefactCount / numRepeats, numHolesSucceed / numRepeats);
        else:
            print(holesDug, successes * 100 / numRepeats);


# Do experiments over range of hole numbers.
# Change the values of the variables to specify the experiment, and change the
# class of the Player created.
def exploreNumberOfHoles() -> None:
    #=====================================================================================
    # Change these variable values to specify an experiment.
    # Also change the subclass of Player that is created later in the function
    # (search "player creation").
    # To print out the field at a certain point during the simulation
    # (when a certain number of holes are dug) change the value to which holesDug is
    # compared still later in the function (search "print field decision").

    fieldSize = 100; # values of 100 and 200 were used in the article
    holeSize = 0.5; # values of 0.5 and 1 are used in the article
    # increment number of holes by this value each iteration
    holeIncrement = 1; # set to 1 for HexagonalLikePlayer etc, and 10 for RandomPlayer etc
    maxHoles = 5000; # stop when this number of holes is reached

    # set whether we are using real world data and where it can be found
    realWorldData = False;
    realWorldDataFile = "real world data/Moderate Density Artefact Coordinates.csv"

    # if realWorldData is False, set the treasure shape and dimensions
    treasureShape = "circle"; # can be "rectangle" or "circle"
    # if circle - note this is the radius, while the diameter was given in the article:
    treasureRadius = 3.5;
    # if rectangle:
    treasureWidth = 20;
    treasureHeight = 5;

    numRepeats = 10000; #10000 in the article simulations

    # use a left and right border, this was always True for experiments reported in the article
    LRBorder = True;
    # stagger in the Y direction as well as the X. Some Players are already staggered in the X direction
    # Note that for experiments reported in the article staggerY was always False.
    staggerY = False;
    #=====================================================================================

    if realWorldData:
        print("realworld, field:", fieldSize, "hole size:", holeSize, "stagger Y:", staggerY);
    elif treasureShape == "circle":
        print("circle, field:", fieldSize, "hole size:", holeSize, "treasure radius:", treasureRadius, "stagger Y:", staggerY);
    else:
        print("rectangle, field:", fieldSize, "hole size:", holeSize, "treasure dimensions:", str(treasureWidth) + "x" + str(treasureHeight), "stagger Y:", staggerY);
    
    # This is the value of the actual number of holes dug for the previous value of "holes".
    # As this is before any value of "holes" we set to -1
    lastHole = -1;

    # this is where we cache the real world data to avoid having to read the data file on each iteration
    realWorldDataCache = None;

    # iterate over number of holes. "holes" is the desired number of holes passed to the
    # Player. The actual number the Player digs may vary according to its layout algorithm
    for holes in range(1, maxHoles+1, holeIncrement):
        successes = 0;
        holesDug = -1;

        # Keep track of whether this layout is new: some Players such as HexagonalLikePlayer
        # will use the same actual number of holes (and layout) for several consecutive desired number of holes.
        # If we find that the layout is not new we skip the repeats for that value of "holes".
        new = True;

        artefactCount = 0;
        numHolesSucceed = 0;

        # run many tests for this number of "holes"
        for repeats in range(0,numRepeats):
            if realWorldData:
                field = RealWorldField(fieldSize, fieldSize);
                # cache the real world data to avoid reading from the file every time.
                # The data doesn't change throughout this function.
                if realWorldDataCache == None:
                    field.placeRealWorldTreasure(csvFileName=realWorldDataFile);
                    realWorldDataCache = field.getData();
                else:
                    field.placeRealWorldTreasure(data = realWorldDataCache);
            else:
                field = IntersectField(fieldSize, fieldSize);
                if treasureShape == "circle":
                    field.placeCircularTreasure(treasureRadius);
                else:
                    field.placeRectangularTreasure(treasureWidth, treasureHeight);

            # player creation: change the player here
            player = HexagonalLikePlayer(field, holeSize, holes, LRBorder, staggerY);
            #player = HexagonalPlayer(field, holeSize, holes, staggerY);
            #player = HaltonPlayer(field, holeSize, holes, LRBorder);
            #player = NonStaggeredPlayer(field, holeSize, holes);
            #player = RandomPlayer(field, holeSize, holes, LRBorder);

            # print class of Player on first iteration
            if (holes==1 and repeats == 0):
                print ("class:", player.__class__);
            
            if not(new):
                # we have seen this same layout from the player for a previous value of "holes",
                # skip the repeats for this value
                break;
            
            try:
                result = player.play();

                # Check for layout errors, usually because the desired layout with the given holeSize won't fit on the field.
                # Use repeats == 1 as it weans out the "not new" number of holes
                if repeats == 1 and (isinstance(player, HexagonalPlayer) or isinstance(player, HexagonalLikePlayer)):
                    if player.layoutError:
                        print("layout algorithm error: probably too many holes for the field size");
                    # d = calculateHoleDistances(field, False);
                    # if abs(d[0] - d[1]) > 0.0001:
                    #     print("not hexagonal");  
                    #     calculateHoleDistances(field, True);
                if result[0]:
                    # the player uncovered treasure
                    successes += 1;
                    if (realWorldData):
                        artefactCount += player.artefactCount;
                        numHolesSucceed += player.numHolesSucceed;
                
                if holesDug == -1:
                    # this is the first repeat for this value of "holes"
                    holesDug = result[1];
                elif holesDug != result[1]:
                    # sanity check that this repeat resulted in the same number of holes being dug
                    # as the previous repeat. We assume all Players obey this.
                    print("ERROR: layout algorithm returned inconsistent number of holes dug");
                    exit();
                
                
                # print field decision: optionally print the field. Change the value that holesDug is compared to as needed
                if (holesDug == 120) and repeats == 1:
                    printField(field, realWorldData, treasureShape, fieldSize, holeSize, treasureRadius, treasureWidth, treasureHeight, holesDug, player.__class__.__name__);
                
                # check if this layout is new on the first repeat
                if repeats == 0:
                    if lastHole == holesDug:
                        # we have seen this layout for the previous value of "holes"
                        new = False;
                    lastHole = holesDug;
            except:
                print("ERROR");
                traceback.print_exc();
                exit();

        if new:
            if (realWorldData):
                print (holes, holesDug, successes * 100 / numRepeats, artefactCount / numRepeats, numHolesSucceed / numRepeats);
            else:
                print (holes, holesDug, successes * 100 / numRepeats);

# choose what experiment you want to run
exploreNumberOfHoles();
#doSpecificGridExperiment();
#testHexagonality();

