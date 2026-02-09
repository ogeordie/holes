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


# This code was used to run the simulations described in the articles "Size Matters:
# Determining Optimal Test Pit Size for Dispersed Archaeological Test Excavation Programs"
# (in preparation) and "Layout Matters: Determining Optimal Test Pit Layout for Dispersed
# Archaeological Test Excavation Programs" (submitted to Journal of Archaeological Science)
# by Geordie Oakes and Andrew McLaren.

# It places square test pits ("holes" in the code) of given number and size on a square field 
# of a given size. The field has a randomly placed archaeological site (referred to as both
# "treasure" and "site" in the code), either specified by a circle, rectangle, or polygon
# (for intersection experiments), or by real-world data on artefact distribution from digs
# in NSW Australia (for detection experiments in "Size Matters"). See the csv files in the
# `real world data` directory for the real-world data and polygon `shapefile` definition.

# The pits are placed according to a layout algorithm. Layout algorithms are implemented by 
# subclasses of the class `Player`. Calling `Player.play()` performs one archaeological dig 
# (digging a certain number of holes on the `Field` according to the layout algorithm), and 
# returns `True` if treasure is found (`False` otherwise). The Hexagonal-like algorithm
# was used in "Size Matters" and "Layout Matters", the rest only in "Layout Matters".
# Layout algorithms are implemented as follows:
# - Hexagonal-like by the `HexagonalLikePlayer`
# - StaggerXY by the `HexagonalLikePlayer` with appropriate arguments to its constructor
# - RandomisedStaggerXY by the `HexagonalLikePlayer` with appropriate arguments to its constructor
# - Halton by `HaltonPlayer`
# - Random by `RandomPlayer`
# - `HexagonalPlayer` was used to test if it had similar performance to the
# `HexagonalLikePlayer`, which it did.  

# See the document `size matters and layout matters layout algorithms.pdf`
# for details of the layout algorithms.

# `ExperimentRunner.runExperiment()` in Holes.py is the entry point to the simulation, and an
# experiment is described by subclasses of the `Experiment` class. This class defines all
# parameters except number of holes (field size, hole size, treasure specification, player 
# type, etc.). For each number of holes (from 1 to a maximum value, or until 100% success rate
# is reached) the inner simulation procedure is run 10000 times in "Size Matters"
# (i.e. there are 10000 digs for each number of holes), with the treasure placed randomly
# each time. In "Layout Matters" the procedure is run
# 10000 times for success experiments and 3000 times for summary experiments.
# The lower number is used for summary experiments as the experiments take a very long time.
# The output of an experiment is, for each number of holes, the desired number of holes,
# the actual number of holes as determined by the layout algorithm (which may differ from
# the desired number of holes due to layout algorithm constraints), and the percentage of
# runs where a hole found treasure ("success rate"). These data are printed to standard
# output (optionally) and saved to a csv file. The output for the real-world artefact
# distribution treasure also includes the average number of artefacts found over the
# runs and average number of holes that found anything, but the `returnAfterHit`
# argument to `Player.play()` must be set to False for these to be accurate. These additional
# data are not used in either paper.

# As mentioned above, note that some players dig a slightly different number of holes than the 
# one supplied to them as the layout algorithm may not work with all numbers of holes. This 
# actual number of holes is also returned by `Player.play()` (as well as whether the dig was
# successful). `Player.play()` has an argument `returnAfterHit` which if `True` will cause
# the method to return as soon as treasure if found. However note that the actual number of
# holes returned is the number of holes that would have been dug if `returnAfterHit` was
# `False` (i.e. the number of holes determined by the layout algorithm).

# The main file is `Experiments.py` for "Size Matters" and `LayoutExperiments.py` for 
# "Layout Matters". These files trigger the various experiments and the generation
# of graphs and tables. Note that one can set the "go" variables in these files to
# control what is triggered (for example if one wishes to use pre-generated data rather
# than generating it which can take over 42 hours on a fast computer for "Layout Matters"
# experiments). The file `Holes.py` contains code to run simulations as described above.
# There is also the functionality to save a field (with holes and treasure) to a text file,
# by calling `ExperimentRunner.printExperiment()` (which can also be triggered from
# `Experiments.py` and `LayoutExperiments.py` by setting `goPrintExperiments` to `True`).
# The file `CreateFieldImage.py` contains code to read such a text file and produce a
# graphical representation of the field, useful in debugging. Printed experiments are saved
# to `hpf` files (for Holes Printed Field).

# The inner simulation procedure (called thousands of times for each number of holes) is simplified
# as (for example):
# ```
# field = Field(fieldSize, fieldSize)
# field.placeCircularTreasure(treasureRadius)
# player = HexagonalLikePlayer(field, holeSize, numberOfHoles)
# result = player.play()
# if result[0]:
#     successes = successes + 1
# actualNumberOfHoles = result[1]
# ```
# Then after the many iterations, the output is `<number of holes>`,
# `actualNumberOfHoles`, and `successes * 100 / <number of iterations>` which is the
# success rate. (We assume `actualNumberOfHoles` will be the same when `<number of holes>`
# is the same). The output is saved to the file specified in the `Experiment` subclass.

# The code defines the top left of the field as the origin (0,0).

# The code was only tested with the experiments explored in the articles. It 
# may not be correct in all circumstances.

# See the README.md file for more details.

import io
import random
import math
import sys
import traceback
import time
import csv
from scipy.stats import qmc
from pathlib import Path
from rich.progress import Progress, SpinnerColumn, TaskProgressColumn, TimeRemainingColumn, BarColumn
import re;
import numpy as np
from shapely import Polygon, Point
from dataclasses import dataclass
import shapefile
from abc import abstractmethod

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


# an abstract field on which holes can be dug. Implementations are responsible
# for providing methods to place treasure on the field.
# To use, first place the treasure, then call digHole() for each hole in the
# layout algorithm, which returns True if the hole finds treasure.
# A Field is intended to be used once only: placing a  second treasure does not
# remove the first one.
#
# NOTE: Some parts of this code assume a square field.
class Field:
        
    # dig a square hole on a field with centre (x,y), of width and height holeSize.
    # Returns True if the hole finds treasure, False otherwise.
    @abstractmethod
    def digHole(self, holeSize:float, x:float, y:float) -> bool:
        pass;

    # returns True if newHole intersects an existing hole on the field.
    # This is useful if the layout algorithm doesn't want to place two
    # holes on the field that intersect each other.
    @abstractmethod
    def intersectsExistingHole(self, newHole:Hole) -> bool:
        pass;

    # prints the field data to a text file. This can be then used by CreateFieldImage.py
    # to print a graphical representation of the field, holes, and treasure. See that
    # python file for a description of the field file format.
    @abstractmethod
    def print(self, fileName:str = ""):
        pass;


# implementation of Field in which treasure is defined by a circle or rectangle
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
        self.__treasurePlaced = False;
        self.__treasureRadius = 0;
        self.__treasureWidth = 0;
        self.__treasureHeight = 0;

    # returns True if the point (x,y) intersects the treasure on the field.
    # assumes a treasure has been placed.
    def __pointIntersectsTreasure(self, x:float, y:float) -> bool:
        if self.__rectangularTreasure == False:
            d = math.sqrt((x - self.__treasureCentreX)**2 + (y - self.__treasureCentreY)**2);
            return d <= self.__treasureRadius;
        else:
            # rectangularTreasure is True
            xInBounds = x > self.__treasureCentreX - self.__treasureWidth/2 and x < self.__treasureCentreX + self.__treasureWidth/2;
            yInBounds = y > self.__treasureCentreY - self.__treasureHeight/2 and y < self.__treasureCentreY + self.__treasureHeight/2;
            return xInBounds and yInBounds;

    # returns True iff hole intersects the treasure on the field. Assumes treasure has been placed.
    def __intersectsTreasure(self, hole:Hole) -> bool:
        if self.__rectangularTreasure == False:
            holeL = hole.centreX - hole.width/2;
            holeR = hole.centreX + hole.width/2;
            holeT = hole.centreY - hole.height/2;
            holeB = hole.centreY + hole.height/2;
        
            closestXToCircle = max(holeL, min(self.__treasureCentreX, holeR));
            closestYToCircle = max(holeT, min(self.__treasureCentreY, holeB));
        
            distanceToClosestPoint = math.sqrt((self.__treasureCentreX - closestXToCircle)**2 + (self.__treasureCentreY - closestYToCircle) **2);
        
            return distanceToClosestPoint < self.__treasureRadius;
    
            # alternatively use shapely intersection detection
            # centreCircle = Point(self.__treasureCentreX, self.__treasureCentreY);
            # hole = Polygon([\
            #     (hole.centreX - hole.width/2, hole.centreY - hole.height/2), \
            #     (hole.centreX + hole.width/2, hole.centreY - hole.height/2), \
            #     (hole.centreX + hole.width/2, hole.centreY + hole.height/2), \
            #     (hole.centreX - hole.width/2, hole.centreY + hole.height/2)]);
            # bufferedCircle = centreCircle.buffer(self.__treasureRadius);
            # return hole.intersects(bufferedCircle);

        else:
            # __rectangularTreasure is True

            #return self.__pointIntersectsTreasure(hole.centreX, hole.centreY); # test holes as points
            
            holeLeft = hole.centreX - hole.width/2;
            holeRight = hole.centreX + hole.width/2;
            holeBottom = hole.centreY + hole.height/2;
            holeTop = hole.centreY - hole.height/2;

            treasureLeft = self.__treasureCentreX - self.__treasureWidth/2;
            treasureRight = self.__treasureCentreX + self.__treasureWidth/2;
            treasureBottom = self.__treasureCentreY + self.__treasureHeight/2;
            treasureTop = self.__treasureCentreY - self.__treasureHeight/2;
    
            xOverlaps = treasureLeft < holeRight and treasureRight > holeLeft;
            yOverlaps = treasureTop < holeBottom and treasureBottom > holeTop;
    
            return xOverlaps and yOverlaps;


    # returns True if newHole intersects an existing hole on the field.
    # This is useful if the layout algorithm doesn't want to place two
    # holes on the field that overlap.
    def intersectsExistingHole(self, newHole:Hole) -> bool:
        for h in self.holes:
            if h.intersects(newHole):
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
        if not self.__treasurePlaced:
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
        #if (self.adjustedHoleAtBorder):
        #   pass;
        
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
# in self.__artefacts. self.__artefacts[i][j] contains a DataParcel of artefacts. An
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
            # keep track of the minimum and maximum x and y coordinates of artefacts (unnormalised)
            self.__setMinX(x);
            self.__setMaxX(x);
            self.__setMinY(y);
            self.__setMaxY(y);

            self.__rawArtefacts.append((x,y));
        
        self.__normalisedArtefacts = [];
        for a in self.__rawArtefacts:
            self.__normalisedArtefacts.append((a[0] - self.minX, a[1] - self.minY));

        # adjust minimum and maximum to the normalised values
        self.maxX = self.maxX - self.minX;
        self.maxY = self.maxY - self.minY;
        self.minX = 0;
        self.minY = 0;
            
        # create a 2D array of DataParcels, see class documentation for explanation
        self.__artefacts = [[self.DataParcel() for y in range(math.ceil(self.maxY))] for x in range(math.ceil(self.maxX))];

        for i in range(len(self.__normalisedArtefacts)):
            x = self.__normalisedArtefacts[i][0];
            y = self.__normalisedArtefacts[i][1];
            self.__artefacts[math.floor(x)][math.floor(y)].addArtefact(x,y);
        
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
    # Only sets new value if it is the new minimum or maximum.
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
        # normalisedArtefactCount = 0;
        # for i in range(len(self.__normalisedArtefacts)):
        #     (x,y) = self.__normalisedArtefacts[i];
        #     if hole.centreX - hole.width/2 <= self.topLeftX + x and \
        #         hole.centreX + hole.width/2 >= self.topLeftX + x and \
        #         hole.centreY - hole.height/2 <= self.topLeftY + y and \
        #         hole.centreY + hole.height/2 >= self.topLeftY + y:
        #             normalisedArtefactCount += 1;
        # #if (normalisedArtefactCount > 0):
        # #    print("raw data:", normalisedArtefactCount);

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
                        # Use <= and >= as artefacts are described by points.
                        # In reality they would have some width and height.
                        if left <= artefactX and \
                            right >= artefactX and \
                            top <= artefactY and \
                            bottom >= artefactY:
                            artefactCount += 1;
            # if testing against raw data (see above in this method), uncomment:
            # if (artefactCount != normalisedArtefactCount):
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
        if not self.__treasurePlaced:
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
        for h in self.__holes:
            if h.intersects(newHole):
                return True;
        return False;

    # prints the field data (holes and treasure placement) to a text file.
    # first line is the string "realworld", second line is field dimensions,
    # third line is the string "realworldtreasure"
    # fourth line is treasure dimensions (bounding box).
    # then a line for each artefact.
    # finally a line for each hole locations and dimensions and whether it uncovers treasure
    # see CreateFieldImage.py for more details of the file format.
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
        for h in self.__holes:
            print("hole:", h.centreX, h.centreY, h.width, h.height, self.__intersectsTreasure(h), file=output);
        output.close();


# A Polygon that represents a treasure on a PolygonField
class PolygonTreasure():

    # aPoints is the list of coordinates of the polygon's vertices
    def __init__(self, aPoints:list[tuple[float, float]]):
        self.__mPoints = aPoints;

        # calculate bounding box
        minX = -1;
        minY = -1;
        maxX = -1;
        maxY = -1;
        for i in range(0, len(self.__mPoints)):
            point = self.__mPoints[i];
            if point[0] < minX or minX == -1:
                minX = point[0];
            if point[1] < minY or minY == -1:
                minY = point[1];
            if point[0] > maxX:
                maxX = point[0];
            if point[1] > maxY:
                maxY = point[1]
        
        # normalize points to have 0 minimum x and y coordinates
        self.__normalisedPoints = [];
        for p in self.__mPoints:
            self.__normalisedPoints.append((p[0] - minX, p[1] - minY));
    
        self.maxX = maxX - minX;
        self.maxY = maxY - minY;
    
    # Places the treasure at the given top left coordinates
    # and sets mPolygon to reflect the new position
    def placeTopLeft(self, x:float, y:float) -> None:
        self.topLeftX = x;
        self.topLeftY = y;

        points = [];
        for p in range(len(self.__normalisedPoints)):
            pointX = self.__normalisedPoints[p][0] + self.topLeftX;
            pointY = self.__normalisedPoints[p][1] + self.topLeftY;
            points.append((pointX, pointY));
        self.mPolygon = Polygon(points);

    # returns True iff hole intersects this polygon
    def intersects(self, hole:Hole) -> bool:
        holeLeft = hole.centreX - hole.width / 2;
        holeRight = hole.centreX + hole.width / 2;
        holeTop = hole.centreY - hole.height / 2;
        holeBottom = hole.centreY + hole.height / 2;

        # check the bounding box for efficiency
        if holeLeft > self.topLeftX + self.maxX or \
            holeRight < self.topLeftX or \
            holeTop > self.topLeftY + self.maxY or \
            holeBottom < self.topLeftY:
            return False;
        
        holePolygon = Polygon([(holeLeft, holeTop), (holeRight, holeTop), (holeRight, holeBottom), (holeLeft, holeBottom)]);
        return self.mPolygon.intersects(holePolygon);
    
    # print a line to file describing each point
    def print(self, file):
        for point in self.__normalisedPoints:
            print("point: " + str(point[0] + self.topLeftX) + " " + str(point[1] + self.topLeftY), file=file);


# a Field which contains a treasure defined by a polygon
class PolygonField(Field):

    # width and height are the dimensions of the field
    def __init__(self, width:int, height:int):
        self.width = width;
        self.height = height;
        self.__holes = [];

    # filename is the name of the zip file containing files
    # in the shapefile format. See https://en.wikipedia.org/wiki/Shapefile .
    # The given shapefile data must define exactly one polygon and no other constructs.
    # The polygon is assumed to be vertically oriented. If rotate is True it is rotated to be
    # horizontally oriented.
    # If treasure is specified (to avoid re-reading it from the file), fileName and rotate are
    # ignored. It will be rotated iff rotate was True when the treasure was created from the file.
    def placePolygonTreasure(self, fileName:str="", rotate:bool = False, treasure:PolygonTreasure = None) -> None:
        if (treasure == None):
            sf = shapefile.Reader("real world data/" + fileName);
            shapes = sf.shapes();
            polygon = shapes[0];
            polygonPoints = [];
            for p in polygon.points:
                if rotate:
                    polygonPoints.append((p[1], p[0]));
                else:
                    polygonPoints.append(p);

            self.__mTreasure = PolygonTreasure(polygonPoints);
        else:
            self.__mTreasure = treasure;

        # check the treasure will fit
        if self.__mTreasure.maxX > self.width or self.__mTreasure.maxY > self.height:
            print("treasure doesn't fit on the field");
            exit();

        # now place it randomly on field
        topLeftX = random.random() * (self.width - self.__mTreasure.maxX);
        topLeftY = random.random() * (self.height - self.__mTreasure.maxY);
        
        self.__mTreasure.placeTopLeft(topLeftX, topLeftY);
        self.__treasurePlaced = True;
    
        if topLeftX < 0 or topLeftX + self.__mTreasure.maxX > self.width:
            print("error: top left x for polygon out of bounds");
        
        if topLeftY < 0 or topLeftY + self.__mTreasure.maxY > self.height:
            print("error: top left y for polygon out of bounds");

    # returns a PolygonTreasure which can be reused in placePolygonTreasure    
    def getTreasure(self) -> PolygonTreasure:
        return self.__mTreasure;
    
    # dig a hole on the field. centreX and centreY specify the location of the hole.
    # Returns whether or not the hole intersects the treasure.
    def digHole(self, holeSize:float, centreX:float, centreY:float) -> bool:
        if not self.__treasurePlaced:
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

    # Returns whether the given hole intersects __mTreasure
    def __intersectsTreasure(self, hole:Hole) -> bool:
        return self.__mTreasure.intersects(hole);

    # Returns whether of not the given newHole intersects an existing
    # hole on the field.
    def intersectsExistingHole(self, newHole:Hole) -> bool:
        for h in self.__holes:
            if h.intersects(newHole):
                return True;
        return False;

    # prints the field in a format which can be read by CreateFieldImage.py
    # See the comments in that file for details of the format.
    def print(self, fileName:str = "") -> None:
        if fileName != "":
            output = open(fileName, 'w');
        else:
            output = sys.stdout;
        print("intersect", file=output);
        print(self.width, self.height, file=output);
        print("polygonTreasure:", self.__mTreasure.topLeftX, self.__mTreasure.topLeftY, \
                    self.__mTreasure.maxX + self.__mTreasure.topLeftX, self.__mTreasure.maxY + self.__mTreasure.topLeftY, file=output);
        self.__mTreasure.print(output);
        for h in self.__holes:
            print("hole:", h.centreX, h.centreY, h.width, h.height, self.__intersectsTreasure(h), file=output);
        output.close();


# An archaeologist that places holes in a field according to its layout strategy,
# which is usually provided with a Field and the desired number of holes to dig.
# The actual number of holes dug may differ from the desired due to layout
# constraints.
# It is assumed that subclasses dig the same number of holes when the parameters
# supplied are the same (e.g. desired number of holes).
class Player:

    # Digs holes according to the layout algorithm implemented by the Player
    # subclass, and returns tuple indicating if treasure was found
    # and the number of holes determined by the layout algorithm.
    # returnAfterHit indictes whether to return as soon as a treasure is found.
    # NOTE: the number of holes returned is the total number of holes
    # that would be dug if returnAfterHit was False, i.e. the number of holes
    # determined by the layout algorithm.
    # If the field is a RealWorldField, after calling this method with returnAfterHit = False
    # self.artefactCount is the number of artefacts uncovered during the dig
    # and self.numHolesSucceeded is the number of holes that uncovered an artefact.
    # NOTE THAT THESE TWO VALUES ARE NOT ACCURATE UNLESS returnAfterHit IS False.
    @abstractmethod
    def play(self, returnAfterHit:bool = True) -> tuple[bool, int]:
        pass;


# an abstract Player that provides support for a staggered layout
class StaggeredPlayer(Player):

    # Create a staggered layout with the given parameters.
    #
    # If the field is a RealWorldField, sets self.numHolesSucceed and self.artefactCount
    # are set when the function returns.
    # NOTE THAT THESE TWO VALUES ARE NOT ACCURATE UNLESS returnAfterHit IS False.
    # 
    # Returns whether treasure was found and the number of holes determined by the layout
    # algorithm. NOTE: this is the total number of holes that would be dug if returnAfterHit was
    # False).
    #
    # The top left of the field is considered to be 0,0.
    #
    # xHoles and yHoles are numbers of holes in the x and y directions respectively.
    # borderX and borderY are the left and top borders respectively where no holes are placed.
    # dX and dY are the distances between holes in the x and y directions respectively.
    # staggerY is True if the layout should be staggered in the y direction as well as the x.
    # If randomise is true, each hole is shifted in both x and y directions by a random 
    # amount, according to a normal distribution with the original position as mean,
    # and the standard deviation dX/stdDevDivisor for the x direction and dY/stdDevDivisor for
    # the y direction.
    # The borders on the right and bottom of the field are determined by the above parameters
    # but it is assumed that they are equal to the borders on the left and top respectively
    # to 2 decimal places.
    # returnAfterHit indicates whether to return as soon as treasure is found, but the number of
    # holes returned will be as if this were False.
    def doStaggeredLayout(self, field:Field, holeSize:float, xHoles:int, borderX:float, dX:float, yHoles:int, borderY:float, dY:float, staggerY:bool, randomise:bool = False, stdDevDivisor = 1, returnAfterHit:bool = True) -> tuple[bool, int]:
        # check the parameters fit properly on the field
        totalX = (2 * borderX) + ((xHoles - 0.5) * dX);
        totalY = (2 * borderY) + ((yHoles - 1) * dY);
        if staggerY:
            totalY = (2 * borderY) + ((yHoles - 0.5) * dY);
        if round(totalX, 2) != round(field.width, 2):
            print("error: staggered layout does not fit the field width");
            print(self.__class__.__name__, xHoles, yHoles, borderX, borderY, dX, dY, staggerY);
            exit();
        if round(totalY, 2) != round(field.height, 2):
            print("error: staggered layout does not fit the field height");
            print(self.__class__.__name__, xHoles, yHoles, borderX, borderY, dX, dY, staggerY);
            exit();
        
        # do the layout
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
                
                if randomise:
                    startX = pos_x - dX/2
                    endX = pos_x + dX/2
                    startY = pos_y - dY/2;
                    endY = pos_y + dY/2;
                    randomx = random.gauss(pos_x, dX/stdDevDivisor);
                    randomy = random.gauss(pos_y, dY/stdDevDivisor);
                    # if a hole is on the border, don't shift it away (only
                    # shift in the other direction)
                    onLeftBorder = round(pos_x, 2) == round(borderX, 2);
                    onRightBorder = round(pos_x, 2) == round(field.width - borderX, 2);
                    onTopBorder = round(pos_y, 2) == round(borderY, 2) ;
                    onBottomBorder = round(pos_y, 2) == round(field.height - borderY, 2);
                    if not(onLeftBorder or onRightBorder):
                        if randomx < startX:
                            randomx = startX;
                        if randomx > endX:
                            randomx = endX;
                    elif onLeftBorder:
                        randomx = borderX;
                    elif onRightBorder:
                        randomx = field.width - borderX;
                    
                    if not(onTopBorder or onBottomBorder):
                        if randomy < startY:
                            randomy = startY;
                        if randomy > endY:
                            randomy = endY;
                    elif onTopBorder:
                        randomy = borderY;
                    elif onBottomBorder:
                        randomy = field.height - borderY;

                    hit = field.digHole(holeSize, randomx, randomy);
                else:                    
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
                if returnAfterHit and found:
                    return found, xHoles * yHoles;
            row += 1;
        return found, holesMade;


# a Player that uses a scrambled 2-D halton distribution of holes.
# We use the SciPy implementation of the scrambled halton distribution.
class HaltonPlayer(Player):

    # create the player with the given values
    def __init__(self, field:Field, holeSize:float, numHoles:int, border:bool=False):
        self.__field = field;
        self.__holeSize = holeSize;
        self.__numHoles = numHoles;
        if border and (self.__field.width != self.__field.height):
            print("non square field not supported");
            exit();
        if (border and self.__numHoles != 0):
            self.__border = (self.__field.width / math.sqrt(self.__numHoles)) / 2;
        else:
            self.__border = self.__holeSize / 2;

    # Digs holes according to the scrambled Halton distribution.
    # Returns whether treasure was found and the number of holes
    # determined by the layout algorithm (which will be equal to the
    # number of holes supplied to the constructor for this layout).
    # If the field is a RealWorldField, sets self.numHolesSucceed and self.artefactCount
    # are set when the function returns (NOTE THAT THESE TWO VALUES ARE NOT ACCURATE UNLESS
    # returnAfterHit IS False).
    def play(self, returnAfterHit:bool = True) -> tuple[bool, int]:
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
            # return early. Note artefactCount and numHolesSucceeded won't be accurate
            if returnAfterHit and found:
                return found, self.__numHoles;
        return found, self.__numHoles;


# A Player that uses the hexagonal-like layout algorithm
# (see the "Layout Matters" paper and the "size matters and layout matters
# layout algorithms.pdf" document).
# This layout is staggered horizontally - If the distance between holes
# in the same row is a, every other row is shifted right by a/2.
# Numbers of holes in a row and the number of rows are chosen
# to be close to the desired number of holes (supplied to the constructor)
# while also being close to hexagonal (i.e. the distance between holes in a
# row is nearly equal to the distance between the closest holes on adjacent
# rows, forming equilateral triangles). If staggerY is True, this hexagonal
# constraint will hold "before" the additional staggering occurs, and because
# of this staggering the layout can no longer be called hexagonal.
#
# If LRBorder (left and right border) is True, each even row
# has a left border of a/2 (and so the left border for each odd row is a
# as it is staggered). The right borders will be a for non-staggered rows
# and a/2 for staggered rows.
# If the distance between rows is c, the top and bottom borders are c/2.
# If staggerY is True, each second hole in each row is shifted down by c/2,
# and the closest holes to the top and bottom will be c/2 from the field edge.
# If randomise is True, hole positions are shifted in both x and y directions
# by a random amount according to a normal distribution, with the original
# position as mean, and standard deviation of dX/stdDevDivisor and dY/stdDevDivisor
# in each direction respectively.
class HexagonalLikePlayer(StaggeredPlayer):

    # create the player with the given values (see class comments)
    def __init__(self, field:Field, holeSize:float, numHoles:int, LRBorder:bool = True, staggerY:bool = False, randomise:bool = False, stdDevDivisor = 1):
        # these are not private as subclasses may want them
        self.field = field;
        self.holeSize = holeSize;
        self.numHoles = numHoles;
        self.LRBorder = LRBorder;
        self.staggerY = staggerY;
        self.randomise = randomise;
        self.stdDevDivisor = stdDevDivisor;

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

    # Dig holes according to the hexagonal-like layout algorithm. See Player.play()
    # for more details.
    # Returns whether treasure was found and the number of holes determined by the layout
    # algorithm (the number of holes that would have been dug if returnAfterHit was False).
    # If the field is a RealWorldField, sets self.numHolesSucceed and self.artefactCount
    # are set when the function returns (NOTE THAT THESE TWO VALUES ARE NOT ACCURATE UNLESS
    # returnAfterHit IS False).
    # On return self.layoutError is True if the algorithm was unable to
    # fit the number of holes on the field, otherwise False.
    def play(self, returnAfterHit:bool = True) -> tuple[bool, int]:
        if (self.LRBorder):
            # calculate number of holes in a row according to the hexagonal-like formula
            numHoles_x = self.quadratic(2 * self.field.height, self.field.height, -1 * math.sqrt(3) * self.numHoles * self.field.width);
            if self.staggerY:
                numHoles_x = self.quadratic(
                    4 * self.field.height, 2 * self.field.height - math.sqrt(3) * self.field.width, \
                    -2 * math.sqrt(3) * self.numHoles * self.field.width);
        else:
            if self.staggerY:
                print("stagger Y with no horizontal border not supported");
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
        if border_x < self.holeSize/2 or border_y < self.holeSize/2 or self.d_x < self.holeSize or self.d_y < self.holeSize:
            self.layoutError = True;

        return self.doStaggeredLayout(self.field, self.holeSize, actualNumHoles[0], border_x, self.d_x, actualNumHoles[1], border_y, self.d_y, self.staggerY, self.randomise, self.stdDevDivisor, returnAfterHit = returnAfterHit);


# a Player that adjusts the horizontal and vertical borders used in the
# HexagonalLikePlayer to make the layout truly hexagonal.
# This may not be the best way to implement a hexagonal layout.
# This player staggers holes horizontally - if the distance between holes
# in the same row is a, each even row is shifted right by a/2.
class HexagonalPlayer(HexagonalLikePlayer):

    # use the given values. Note staggerY =True is not currently supported for this player.
    def __init__(self, field:Field, holeSize:float, numHoles:int, staggerY:bool = False):
        HexagonalLikePlayer.__init__(self, field, holeSize, numHoles, True, staggerY);
        if staggerY:
            print("staggering in the Y direction not supported for HexagonalPlayer");
            exit();
    
    # Digs holes according to the hexagonal layout algorithm.
    # Returns whether treasure was found and the number of holes determined by the layout
    # algorithm (the number of holes that would have been dug if returnAfterHit was False).
    # If the field is a RealWorldField, sets self.numHolesSucceed and self.artefactCount
    # are set when the function returns (NOTE THAT THESE TWO VALUES ARE NOT ACCURATE UNLESS
    # returnAfterHit IS False).
    # On return self.layoutError is True if the algorithm was unable to
    # fit the number of holes on the field, otherwise False.
    def play(self, returnAfterHit:bool = True) -> tuple[bool, int]:
        # calculate number of holes in a row according to the hexagonal-like formula
        numHoles_x = self.quadratic(2 * self.field.height, self.field.height, -1 * math.sqrt(3) * self.numHoles * self.field.width);

        if self.staggerY:
            print("staggering in the Y direction not supported for HexagonalPlayer");
            exit();
            # this formula hasn't been checked:
            # numHoles_x = self.quadratic(
            #     4 * self.field.height, 2 * self.field.height - math.sqrt(3) * self.field.width, \
            #     -2 * math.sqrt(3) * self.numHoles * self.field.width);
        
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

        return self.doStaggeredLayout(self.field, self.holeSize, actualNumHoles[0], border_x, a, actualNumHoles[1], border_y, c, self.staggerY, returnAfterHit=returnAfterHit);


# A Player that places holes in a staggered grid, using the given
# number of holes in a row (xHoles) and number of rows (yHoles).
# Horizontal and vertical borders are half the distance between holes and rows
# respectively. The Player will also stagger the columns if staggerY is True.
# This class is not used but may be useful in the future.
class SpecifiedGridPlayer(StaggeredPlayer):

    def __init__(self, field:Field, holeSize:float, xHoles:int, yHoles:int, staggerY:bool = False):
        self.__field = field;
        self.__holeSize = holeSize;
        self.__xHoles = xHoles;
        self.__yHoles = yHoles;
        self.__staggerY = staggerY;

    # after calling, self.layoutError is True if the holes don't fit on the field
    def play(self, returnAfterHit:bool = True) -> tuple[bool, int]:
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
        
        return self.doStaggeredLayout(self.__field, self.__holeSize, self.__xHoles, border_x, d_x, self.__yHoles, border_y, d_y, self.__staggerY, returnAfterHit=returnAfterHit);


# Encapsulates the random values used to position holes on the field.
class RandomHolesSpecification:

    def __init__(self, xRandom:list, yRandom:list):
        self.xRandom = xRandom;
        self.yRandom = yRandom;


# A Player that places holes randomly on the Field.
# Holes do not overlap.
#
# If too many holes are asked for (i.e. they don't all fit), play() will never return.
#
# For efficiency considerations the field is divided into buckets
# of length and width one fiftieth of the field, and holes in each bucket
# stored in a 2-D list.
#
# Assumes a square Field.
class RandomPlayer(Player):

    # if border is True, holes will not be placed on the edges of the field,
    # there will be a border of half distance between holes (and rows) if the layout
    # was a square grid with the same number of holes.
    def __init__(self, field:Field, holeSize:float, numHoles:int, border:bool = False):
        self.__numHoles = numHoles;
        self.__field = field;
        self.__holeSize = holeSize;
        self.__numHorizontalParcels = math.ceil(50);
        self.__numVerticalParcels = math.ceil(50);

        if border and (self.__field.width != self.__field.height):
            print("non square fields not supported");
            exit();
        if border and numHoles != 0:
            self.__border = (self.__field.width / math.sqrt(numHoles)) / 2 ;
        else:
            self.__border = self.__holeSize / 2;
        self.__holeSpecification = None;
        self.__usingHoleCache = False;

    # set the random values used in positioning holes on the field, if the user
    # wants to reuse these values
    # NOTE: caching random values is currently not used and not tested properly
    def setHoleSpecification(self, holeSpec:RandomHolesSpecification) -> None:
        self.__holeSpecification = holeSpec;
        if holeSpec != None:
            self.__usingHoleCache = True;
            if len(self.__holeSpecification.xRandom) != self.__numHoles:
                print("got hole spec of " + str(len(self.__holeSpecification.xRandom)) + " for numholes " + str(self.__numHoles));
                exit(1);
    
    # get the random values used in positioning holes on the field, if the user
    # wants to reuse these values. Note this should be called after play().
    # NOTE: caching random values is currently not used and not tested properly
    def getHoleSpecification(self) -> RandomHolesSpecification:
        return RandomHolesSpecification(self.xrandom, self.yrandom);
    
    # returns whether newHole intersects and existing hole on the field
    def __intersectsExistingHole(self, newHole:Hole) -> bool:
        # assumes all holes on the field are of self.__holeSize
        bucketWidth = self.__field.width / self.__numHorizontalParcels;
        bucketHeight = self.__field.height / self.__numVerticalParcels;
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

        for xBucket in range(startXBucket, endXBucket + 1):
            for yBucket in range(startYBucket, endYBucket + 1):
                for i in range(len(self.__holePositions[xBucket][yBucket])):
                    h = self.__holePositions[xBucket][yBucket][i]

                    oldHole = Hole(h[0], h[1], self.__holeSize, self.__holeSize);
                    if oldHole.intersects(newHole):
                        return True;

                    #    check = self.__field.intersectsExistingHole(newHole);
                    #    if not(check):
                    #        print("**error")
    
        # check = self.__field.intersectsExistingHole(newHole);
        # if check:
        #     print("**error")
        return False;

    # Digs holes randomly and returns tuple indicating if treasure was found
    # and the actual number of holes dug (NOTE: this is the total number of holes
    # that would be dug if returnAfterHit was False, i.e. the number of holes
    # determined by the layout algorithm, which for the random layout algorithm is
    # identical to the number of holes requested in the constructor).
    # If the field is a RealWorldField, after calling this method with returnAfterHit = False
    # self.artefactCount is the number of artefacts uncovered during the dig
    # and self.numHolesSucceeded is the number of holes that uncovered an artefact.
    # NOTE THAT THESE TWO VALUES ARE NOT ACCURATE UNLESS returnAfterHit IS False.
    #
    # NOTE: holes don't overlap. If not all holes fit on the field this will never return
    def play(self, returnAfterHit:bool = True) -> tuple[bool, int]:
        h = 0;
        found = False;
        self.numHolesSucceed = 0;
        self.artefactCount = 0;
        self.xrandom = [];
        self.yrandom = [];
        if self.__usingHoleCache:
            self.xrandom = self.__holeSpecification.xRandom;
            self.yrandom = self.__holeSpecification.yRandom;
        else:
            self.__holePositions = [[[] for y in range(self.__numVerticalParcels)] for x in range(self.__numHorizontalParcels)];
        
        while h < self.__numHoles:
            if self.__usingHoleCache:
                randomXValue = self.__holeSpecification.xRandom[h];
                randomYValue = self.__holeSpecification.yRandom[h];
            else:
                randomXValue = np.random.rand();
                randomYValue = np.random.rand();
            x = randomXValue * (self.__field.width - 2 * self.__border) + self.__border;
            y = randomYValue * (self.__field.height - 2 * self.__border) + self.__border;
            hole = Hole(x, y, self.__holeSize, self.__holeSize);
            if self.__usingHoleCache or (not self.__intersectsExistingHole(hole)):
                # only dig the hole if it doesn't intersect another
                hit = self.__field.digHole(self.__holeSize, x, y);
                if not self.__usingHoleCache:
                    self.xrandom.append(randomXValue);
                    self.yrandom.append(randomYValue);
                eachBucketWidth = self.__field.width / self.__numHorizontalParcels;
                eachBucketHeight = self.__field.height / self.__numVerticalParcels;
                try:
                    if (not self.__usingHoleCache):
                        self.__holePositions[math.floor(x/eachBucketWidth)][math.floor(y/eachBucketHeight)].append((x,y));
                except Exception:
                    print ("error at x =", x, "eachBucketWidth =", eachBucketWidth, "y =", y);
                found = found or hit;
                if (hit):
                    self.numHolesSucceed += 1;
                    if (isinstance(self.__field, RealWorldField)):
                        self.artefactCount += self.__field.artefactCount;
                h += 1;
                if returnAfterHit and found:
                    return found, self.__numHoles;
        return found, h;


# A Player that places holes in a plain square grid
# This class is not currently used but may be useful in the future.
class NonStaggeredPlayer(Player):
    def __init__(self, field:Field, holeSize:float, numHoles:int):
        self.__numHoles = numHoles;
        self.__field = field;
        self.__holeSize = holeSize;

    def play(self, returnAfterHit:bool = True) -> tuple[bool, int]:
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
            if returnAfterHit and found:
                return found, xHoles * yHoles;
        return found, numHolesDug;


# debugging function to examine how hexagonal the layout of holes on a Field is.
# Prints the horizontal distance between the first two holes on the first row,
# and the diagonal distance between the first hole on the first row and the
# first hole on the second row.
# Assumes these holes exist and that holes are not staggered in the y direction.
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
    while currentHole < len(field.holes) and field.holes[currentHole].centreY == firstRowY:
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


# test hexagonality using calculateHoleDistances().
# Change values of fieldFileName, field size, player arguments,
# treasure size and shape, player type as desired
def testHexagonality() -> None:
    fieldFileName = "hex";
    field = IntersectField(100, 100);
    #player = HexagonalLikePlayer(field, 0.5, 12, True, True); #Note stagger Y on
    player = HexagonalPlayer(field, 0.5, 12, False);
    # player = DeltaStaggeredXYPlayer(field, 0.5, 80);
    #player = SpecifiedGridPlayer(field, 1, 5, 5, True);
    #player = NonStaggeredPlayer(field, 1, 25);
    #player = RandomPlayer(field, 1, 18, True);
    #player = HexagonalPlayer\(field, 1, 80);
    #player = HaltonPlayer(field, 2, 2, 50);
    #field.placeRectangularTreasure(60, 6.67);
    field.placeCircularTreasure(5);
    result = player.play();
    print ("hit:", result[0], "numHoles:", result[1]);
    field.print(fileName=fieldFileName);
    calculateHoleDistances(field);


# debugging function to print the top and bottom, and left and right borders
# the chosen player after play() is called.
def testBorders():
    field = IntersectField(100, 100);
    player = HexagonalLikePlayer(field, 0.5, 2000, True, True, False, 8);
    #player = RandomPlayer(field, 0.5, 2000, True);
    #player = HaltonPlayer(field, 0.5, 1000, True);
    
    field.placeRectangularTreasure(10, 10);

    # Note, returnAfterHit is False
    result = player.play(False);
    #field.print("test field");
    testBordersOfField(field);

def testBordersOfField(field:Field, printBorders:bool = True):
    leftBorder = field.width;
    rightBorder = field.width;
    topBorder = field.height;
    bottomBorder = field.height;
    i = 0;
    while i < len(field.holes):
        currentHole = field.holes[i];
        if currentHole.centreX < leftBorder:
            leftBorder = currentHole.centreX;
        if field.width - currentHole.centreX < rightBorder:
            rightBorder = field.width - currentHole.centreX;
        if currentHole.centreY < topBorder:
            topBorder = currentHole.centreY;
        if field.height - currentHole.centreY < bottomBorder:
            bottomBorder = field.height - currentHole.centreY;
        i = i + 1;
    if (printBorders):
        print("left:", leftBorder, "right:", rightBorder);
        print("top:", topBorder, "bottom:", bottomBorder);
    elif (round(leftBorder, 2) != round(rightBorder, 2)) or (round(topBorder, 2) != round(bottomBorder, 2)):
        print("error");
        print("left:", leftBorder, "right:", rightBorder);
        print("top:", topBorder, "bottom:", bottomBorder);


# A class that describes an experiment to be run in the ExperimentRunner.
class Experiment:

    # the height and width of the square field.
    # Values of 100m, 150m, and 200m were used in the articles
    @abstractmethod
    def getFieldSize(self) -> int:
        pass;
    
    # the length and width of the square holes to be dug.
    # Values of 0.5m and 1m were used in the "Size Matters" article
    # and 0.5m in "Layout Matters"
    @abstractmethod
    def  getHoleSize(self) -> float:
        pass;
    
    # the number by which the number of holes is incremented each time
    # round the simulation.
    # 1 was used in the "Size Matters" article
    # In "Layout Matters", RandomPlayer and HaltonPlayer experiments
    # had a value of 10, the rest 1
    @abstractmethod
    def getHoleIncrement(self) -> int:
        pass;
    
    # the number by which the number of holes is incremented each time round
    # the simulation for smaller numbers of holes, until the
    # getSmallNumHolesIncrementCutoff() is reached.
    # In "Layout Matters", Random and Halton experiments had a value of 3
    @abstractmethod
    def getSmallNumHolesIncrement(self) -> int:
        pass;
    
    # the number at which we switch from getSmallNumHolesIncrement()
    # to getHoleIncrement() to define the number by which the number
    # of holes is incremented on each round of the simulation
    @abstractmethod
    def getSmallNumHolesIncrementCutoff(self) -> int:
        pass;
    
    # the number of holes at which to start the experiment.
    # This is usually 1.
    @abstractmethod
    def getStartHoles(self) -> int:
        pass;
    
    # the number of holes at which to stop the simulation, unless
    # 100% success rate is acheived beforehand (in which case the
    # simulation stops)
    @abstractmethod
    def getMaxHoles(self) -> int:
        pass;

    # whether the experiment uses real world data (True)
    # or a circular, rectangular, or polygon treasure (False)
    @abstractmethod
    def getRealWorldData(self) -> bool:
        pass;

    # if getRealWorldData() returns True, this is the name of the
    # csv file that specifies the data. For example
    # "real world data/Low Density Artefact Coordinates.csv"
    @abstractmethod
    def getRealWorldDataFile(self) -> str:
        pass;

    # if getRealWorldData() returns False, this is the shape of the treasure.
    # Can be "circle", "rectangle", or "polygon"
    @abstractmethod
    def getTreasureShape(self) -> str:
        pass;

    # if getTreasureShape() returns "circle", this is the radius of the treasure.
    # Note that in the "Size Matters" paper diameters are cited rather than radius.
    @abstractmethod
    def getTreasureRadius(self) -> float:
        pass;

    # if getTreasureShape() returns "rectangle", this is the width of the treasure
    @abstractmethod
    def getTreasureWidth(self) -> float:
        pass;

    # if getTreasureShape() returns "rectangle", this is the height of the treasure
    @abstractmethod
    def getTreasureHeight(self) -> float:
        pass;

    # returns the name of the zip file defining the polygon if treasure shape is "polygon"
    @abstractmethod
    def getPolygonFile(self) -> str:
        pass;
    
    # indicates whether to rotate the polygon treasure from vertical
    # to horizontal orientation
    @abstractmethod
    def getRotatePolygon(self) -> bool:
        pass;
    
    # returns the divisor of width between holes (and rows) which is one standard deviation if
    # randomising hole positions. See StaggeredPlayer.doStaggeredLayout() for more details.
    @abstractmethod
    def getStdDeviationDivisor(self) -> int:
        pass;
    
    # the number of simulation iterations for each number of holes
    @abstractmethod
    def getNumRepeats(self) -> int:
        pass;
    
    # the number of iterations for smaller number of holes
    @abstractmethod
    def getSmallNumHolesNumRepeats(self) -> int:
        pass;

    # the number of holes below which getSmallNumHolesNumRepeats() is used
    @abstractmethod
    def getSmallNumHolesNumRepeatsCutoff(self) -> int:
        pass;

    # returns the success rate at which to terminate the experiment.
    # Usually 100 (percent) is used.
    @abstractmethod
    def getStopAtSuccess(self) -> float:
        pass;
    
    # indicates whether to stop a dig once treasure is found.
    # If running a realworld data experiment and want the artefact
    # count and number of holes succeeding after calling play(),
    # this should be False. Note data returned from Player.play() on number of
    # holes dug are the number of holes that would have been dug if this
    # were False (i.e. the number determined by the layout algorithm).
    @abstractmethod
    def getReturnAfterHit(self) -> bool:
        pass;

    # whether or not the layout algorithm should enforce left and right borders
    # on the field in which no holes are dug (always True in the experiments
    # reported in the papers). For Random and Halton players, this determines
    # whether borders are made on all edges of the field.
    @abstractmethod
    def getLRBorder(self) -> bool:
        pass;

    # whether or not a staggered layout should stagger in the y direction
    # as well as the x direction (always False in the experiments reported
    # in "Size Matters", but True is also used in "Layout Matters").
    @abstractmethod
    def getStaggerY(self) -> bool:
        pass;
    
    # whether or not to randomise a staggered layout (note this does
    # not need to be true for RandomPlayer or HaltonPlayer)
    @abstractmethod
    def getRandomise(self) -> bool:
        pass;

    # the file to output the results of the simulation. The file will be
    # placed in the "data" directory. For example "7mCircle 100mField 0.5mPits.csv".
    # For "Layout Matters", this includes the subdirectory of the data
    # directory in which to save the data.
    @abstractmethod
    def getOutputFileName(self) -> str:
        pass;

    # get the Player that implements the layout algorithm chosen for
    # the experiment. For "Size Matters" this was always a HexagonalLikePlayer.
    @abstractmethod
    def getPlayer(self, field:Field, holes:int) -> Player:
        pass;


# A class that runs an experiment described by an Experiment object,
# and outputs results to a file as well as (optionally) standard output
class ExperimentRunner:

    # create an ExperimentRunner with the experiment to run
    def __init__(self, experiment: Experiment):
        self.mExperiment = experiment;
        self.realWorldDataCache = None;
        self.polygonTreasureCache = None;

    # print a description of the experiment to stdout    
    def printDescription(self):
        if self.realWorldData:
            print("realworld, field:", self.fieldSize, "hole size:", self.holeSize, "stagger Y:", self.staggerY);
        elif self.treasureShape == "circle":
            print("circle, field:", self.fieldSize, "hole size:", self.holeSize, "treasure radius:", self.treasureRadius, "stagger Y:", self.staggerY);
        elif self.treasureShape == "rectangle":
            print("rectangle, field:", self.fieldSize, "hole size:", self.holeSize, "treasure dimensions:", str(self.treasureWidth) + "x" + str(self.treasureHeight), "stagger Y:", self.staggerY);
        elif self.treasureShape == "polygon":
            print("polygon field:", self.fieldSize, "hole size:", self.holeSize, "staggerY:", self.staggerY)

    # creates the field and places treasure randomly
    def createFieldAndPlaceTreasure(self):
        if self.realWorldData:
            self.field = RealWorldField(self.fieldSize, self.fieldSize);
            # cache the real world data to avoid reading from the file every time.
            # The data doesn't change throughout this function.
            if self.realWorldDataCache == None:
                self.field.placeRealWorldTreasure(csvFileName=self.realWorldDataFile);
                self.realWorldDataCache = self.field.getData();
            else:
                self.field.placeRealWorldTreasure(data = self.realWorldDataCache);
        else:
            if self.treasureShape == "circle":
                self.field = IntersectField(self.fieldSize, self.fieldSize);
                self.field.placeCircularTreasure(self.treasureRadius);
            elif self.treasureShape == "rectangle":
                self.field = IntersectField(self.fieldSize, self.fieldSize);
                self.field.placeRectangularTreasure(self.treasureWidth, self.treasureHeight);
            else:
                # treasure is a polygon
                self.field = PolygonField(self.fieldSize, self.fieldSize);
                if self.polygonTreasureCache == None:
                    self.field.placePolygonTreasure(fileName = self.polygonFile, rotate = self.rotatePolygon);
                    self.polygonTreasureCache = self.field.getTreasure();
                else:
                    self.field.placePolygonTreasure(treasure = self.polygonTreasureCache);

    # save the field, holes, and treasure after a single dig to a text file in
    # the "printedFields" directory. This file can be read by CreateFieldImage.py to
    # create a graphical depiction of the field.
    def printExperiment(self, numHoles:int) -> None:
        self._readExperimentValues();
        self.createFieldAndPlaceTreasure();
        player = self.mExperiment.getPlayer(self.field, numHoles);
        result = player.play(returnAfterHit=False);
        self._printField(result[1], player.__class__.__name__);
    
    # prints the given Field to a file in the "printedFields" directory.
    # This file can be read by CreateFieldImage.py to create a graphical
    # depiction of the field. See that file for details of the format.
    def _printField(self, holesDug:int, playerClass:str):
        playerType = "unknown algorithm";
        if playerClass.startswith("HexagonalLike"):
            if self.staggerY and self.randomise:
                playerType = "RandomisedStaggerXY";
            elif self.staggerY:
                playerType = "StaggerXY";
            else:
                playerType = "HexagonalLike";
        elif playerClass.startswith("Random"):
            playerType = "Random";
        elif playerClass.startswith("Halton"):
            playerType = "Halton";
        
        # create the file name
        polygonOrientationString = "vertical ";
        if (self.rotatePolygon):
            polygonOrientationString = "horizontal ";

        if self.realWorldData:
            p = Path(self.realWorldDataFile);
            firstWord = re.split(r'\.| ', p.name)[0];
            filename = "realWorldField " + firstWord + " " + str(self.fieldSize) + " holesize " + str(self.holeSize) + " holes " + str(holesDug) + " " + playerType;
        elif self.treasureShape == "circle":
            filename = "intersectField " + str(self.fieldSize) + " holesize " + str(self.holeSize) + " treasure " + str(self.treasureRadius) + " holes " + str(holesDug) + " " + playerType;
        elif self.treasureShape == "rectangle":
            filename = "intersectField " + str(self.fieldSize) + " holesize " + str(self.holeSize) + " treasure " + str(self.treasureWidth) + "x" + str(self.treasureHeight) + " holes " + str(holesDug) + " " + playerType;
        else:
            filename = "polygonField " + str(self.fieldSize) + " holesize " + str(self.holeSize) + " holes " + str(holesDug) + " " + polygonOrientationString + playerType;
        filename = "printedFields/" + filename + ".hpf";
        outputFile = Path(filename);
        outputFile.parent.mkdir(exist_ok=True, parents=True);
        # print the field   
        self.field.print(filename);
    
    # prints the results of the simulation after numRepeats digs have been run
    # for a given number of holesDug (holes is the desired number of holes supplied
    # to the layout algorithm, and holesDug the actual number of holes arrived at
    # by the layout algorithm).
    # successes are the number of digs where a hole found the treasure.
    def printResults(self, printData:bool, outputFile:io.TextIOWrapper, holes:int, holesDug:int, successes:int, numRepeats:int, artefactCount:int, numHolesSucceed:int):
        outputFile.write(str(holes) + ", " + str(holesDug) + ", " + str(successes * 100 / numRepeats) + "\n");
        outputFile.flush();
        if printData:
            if (self.realWorldData):
                print (holes, holesDug, successes * 100 / numRepeats, artefactCount / numRepeats, numHolesSucceed / numRepeats);
            else:
                print (holes, holesDug, successes * 100 / numRepeats);

    # transfers the various parameters in mExperiment to class variables
    def _readExperimentValues(self) -> None:
        self.fieldSize = self.mExperiment.getFieldSize();
        self.holeSize = self.mExperiment.getHoleSize();

        self.holeIncrement = self.mExperiment.getHoleIncrement();
        self.smallNumHolesIncrement = self.mExperiment.getSmallNumHolesIncrement();
        self.smallNumHolesIncrementCutoff = self.mExperiment.getSmallNumHolesIncrementCutoff();

        self.startHoles = self.mExperiment.getStartHoles();
        self.maxHoles = self.mExperiment.getMaxHoles();

        # set whether we are using real world data and where it can be found
        self.realWorldData = self.mExperiment.getRealWorldData();
        self.realWorldDataFile = self.mExperiment.getRealWorldDataFile();

        # if self.realWorldData is False, set the treasure shape and dimensions
        self.treasureShape = self.mExperiment.getTreasureShape(); # can be "rectangle", "circle", or "polygon"
        # if circle - note this is the radius, while the diameter was given in the article:
        self.treasureRadius = self.mExperiment.getTreasureRadius();
        # if rectangle:
        self.treasureWidth = self.mExperiment.getTreasureWidth();
        self.treasureHeight = self.mExperiment.getTreasureHeight();
        # if polygon:
        self.polygonFile = self.mExperiment.getPolygonFile();
        self.rotatePolygon = self.mExperiment.getRotatePolygon();

        self.numRepeats = self.mExperiment.getNumRepeats();
        self.smallNumHolesNumRepeats = self.mExperiment.getSmallNumHolesNumRepeats();
        self.smallNumHolesNumRepeatsCutoff = self.mExperiment.getSmallNumHolesNumRepeatsCutoff();

        self.stopAtSuccess = self.mExperiment.getStopAtSuccess();
        self.returnAfterHit = self.mExperiment.getReturnAfterHit();

        self.outputFileName = self.mExperiment.getOutputFileName();

        self.LRBorder = self.mExperiment.getLRBorder();
        self.staggerY = self.mExperiment.getStaggerY();
        self.randomise = self.mExperiment.getRandomise();

    # Do an experiment simulating archaeological digs over range of hole numbers.
    # For each number of holes self.numRepeats iterations are run, except
    # if the number of holes is less than experiment.getSmallNumHolesNumRepeatsCutoff()
    # in which case experiment.getSmallNumHolesNumRepeats() iterations are run.
    # The data is saved in self.outputFileName in the data directory (outputFileName
    # may include a subdirectory of the data directory).
    # The data is also printed to standard out if printData is True.
    def runExperiment(self, printData = True) -> None:
        self._readExperimentValues();

        if (printData):
            print("generating \"" + self.mExperiment.getOutputFileName() + "\"");
        if printData:
            self.printDescription();
        
        # This is the value of the actual number of holes dug for the previous value of "holes".
        # As this is before any value of "holes" we set to -1
        lastHole = -1;

        # this is where we cache the real world data to avoid having to read the data file on each iteration
        self.realWorldDataCache = None;
        self.polygonTreasureCache = None;

        outputFile = Path("data/" + self.outputFileName);
        outputFile.parent.mkdir(exist_ok=True, parents=True)
        with open("data/" + self.outputFileName, "w") as outputFile:
            outputFile.write("desiredholes, actualholes, successrate\n");
            outputFile.write("0, 0, 0\n");
            outputFile.flush();

            # iterate over number of holes. "holes" is the desired number of holes passed to the
            # Player. The actual number the Player digs may vary according to its layout algorithm
            holes = self.startHoles;
            while holes <= self.maxHoles:
                successes = 0;
                holesDug = -1;

                # Keep track of whether this layout is new: some Players such as HexagonalLikePlayer
                # will use the same actual number of holes (and layout) for several consecutive desired number of holes.
                # If we find that the layout is not new we skip the repeats for that value of "holes".
                new = True;

                artefactCount = 0;
                numHolesSucceed = 0;
                # run many tests for this number of "holes"
                if (holes <= self.smallNumHolesNumRepeatsCutoff):
                    numRepeats = self.smallNumHolesNumRepeats;
                else:
                    numRepeats = self.numRepeats;

                for repeats in range(0, numRepeats):
                    self.createFieldAndPlaceTreasure();

                    player = self.mExperiment.getPlayer(self.field, holes);

                    # print class of Player on first iteration
                    if (printData and holes==0 and repeats == 0):
                        print ("class:", player.__class__);
                    
                    if not new:
                        # we have seen this same layout from the player for a previous value of "holes",
                        # skip the repeats for this value
                        break;
                    
                    try:
                        result = player.play(self.returnAfterHit);

                        # Check for layout errors, usually because the desired layout with the given holeSize won't fit on the field.
                        # Use repeats == 1 as it weans out the "not new" number of holes
                        if repeats == 1 and (isinstance(player, HexagonalPlayer) or isinstance(player, HexagonalLikePlayer)):
                            if player.layoutError:
                                print("layout algorithm error: probably too many holes for the field size");
                                self.printDescription();

                        if repeats == 1 and isinstance(self.field, IntersectField):
                            if self.field.adjustedHoleAtBorder:
                                print("adjusted at border");
                                self.printDescription();
                        if result[0]:
                            # the player uncovered treasure
                            successes += 1;
                            if (self.realWorldData):
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
                    self.printResults(printData, outputFile, holes, holesDug, successes, numRepeats, artefactCount, numHolesSucceed);

                    if ((successes * 100 / numRepeats) >= self.stopAtSuccess):
                        return;
            
                # increment holes 
                if holes < self.smallNumHolesIncrementCutoff:
                    holes = holes + self.smallNumHolesIncrement;
                else:
                    holes = holes + self.holeIncrement;

if __name__ == "__main__":
    print("Experiments.py and LayoutExperiments.py are the main files for this project");
#    testHexagonality();
#    testBorders();
