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

# This file contains definitions of abstract classes Treasure and TreasureManager, as well as
# several implementations of same.

from abc import ABC
from abc import abstractmethod
from Hole import Hole
from HolesDictionary import HolesDictionary
import random
import math
from shapely import Polygon, intersects
from shapely.affinity import rotate, translate
import csv
import traceback
import shapefile
from dataclasses import dataclass
from pathlib import Path
import re
import sys
import os


# An abstract Treasure that sits on a Field. Treasure implementations should
# be able to be reused by calling placeRandomly(), unless otherwise
# indicated.
class Treasure(ABC):

    # Place the treasure on a Field of the given dimensions. Some Treasure
    # implementations lie wholly within the field. Others (including all those
    # used in "Layout Matters") lie partially within the Field. In this case
    # at least two thirds of at least two sides of the the treasure's bounding
    # box lie within the field (the centre of the bounding box is then at least
    # one sixth the lengths of the relevant bounding box sides from the edge
    # of the field). This means usually at least two thirds of the bounding box
    # area will lie within the Field. When placed near the corners of the 
    # Field, at least four ninths of the bounding box area will lie within
    # the Field.
    @abstractmethod
    def placeRandomly(self, fieldWidth:int, fieldHeight:int) -> None:
        pass;

    # Return True if hole intersects this Treasure, False otherwise
    @abstractmethod
    def intersectsHole(self, hole:Hole) -> bool:
        pass;

    # Print the details of this Treasure to file in the format
    # specified in CreateFieldImage.py file comments.
    @abstractmethod
    def printTreasure(self, file) -> None:
        pass;


# An abstract manager that creates and returns a type of Treasure
class TreasureManager(ABC):

    # Return the treasure managed by this class. On first call, it will be a
    # new Treasure. On subsequent calls it may be the same Treasure if
    # circumstances allow. Certain implementations assume getTreasure()
    # is called during each simulation iteration.
    @abstractmethod
    def getTreasure(self) -> Treasure:
        pass;

    # Return a string summarizing the treasure, used for creating filenames
    # when printing a Field.
    @abstractmethod
    def getTreasureDescription(self) -> str:
        pass;


# A Treasure that is a possibly rotated rectangle.
class RectangularTreasure(Treasure):

    # Create the RectangularTreasure with the given dimensions and rotation.
    # Rotation is counter-clockwise from horizontal (note that (0,0) is
    # the top left of the Field).
    # If whollyWithinField, the treasure lies wholly within the field.
    # Otherwise partially as described in the Treasure.placeRandomly()
    # comments.
    def __init__(self, longSide:float, shortSide:float, rotation:float, whollyWithinField:bool = False):
        self._longSide = longSide;
        self._shortSide = shortSide;
        self._rotation = rotation;
        self._centreX = self._centreY = 0;
        self._whollyWithinField = whollyWithinField;
        if round(self._longSide, 2) < round(self._shortSide, 2):
            print("incorrect treasure dimensions");
            exit(1);
        
        self._initialVertices = [(0,0), (self._longSide, 0), (self._longSide, self._shortSide), (0, self._shortSide)];
        self._initialPolygon = Polygon(self._initialVertices);
        self._initialCentre = (self._longSide/2, self._shortSide/2);


    # Place this on a Field of given dimensions. Stores position
    # in self._centreX and self._centreY, and the rectangle in
    # self._polygon.
    def placeRandomly(self, fieldWidth, fieldHeight):
        # rotate counterclockwise, noting (0,0) is top left of field
        rotatedPolygon = rotate(self._initialPolygon, -1*self._rotation);
        xVertices, yVertices = rotatedPolygon.exterior.coords.xy;
        minX = min(xVertices);
        maxX = max(xVertices);
        minY = min(yVertices);
        maxY = max(yVertices);

        if (maxX - minX > fieldWidth or maxY - minY > fieldHeight):
            print("field not big enough for treasure");
            exit(1);

        xRandom = random.random();
        yRandom = random.random();
        boundingWidth = maxX - minX;
        boundingHeight = maxY - minY;
        if self._whollyWithinField:
            self._centreX = xRandom * (fieldWidth - boundingWidth) + boundingWidth/2;
            self._centreY = yRandom * (fieldHeight - boundingHeight) + boundingHeight/2;
        else:
            self._centreX = xRandom * (fieldWidth - (2/6) * boundingWidth) + (1/6) * boundingWidth;
            self._centreY = yRandom * (fieldHeight - (2/6) * boundingHeight) + (1/6) * boundingHeight;

        # for a rectangle the centre of the bounding box doesn't change with rotation
        shiftX = self._centreX - self._initialCentre[0];
        shiftY = self._centreY - self._initialCentre[1];
        shiftedVertices = [(v[0] + shiftX, v[1] + shiftY) for v in self._initialVertices];
        shiftedPolygon = Polygon(shiftedVertices);
        self._polygon = rotate(shiftedPolygon, -1*self._rotation);
        self._xVertices, self._yVertices = self._polygon.exterior.coords.xy;
        self._boundsMinX = min(self._xVertices);
        self._boundsMaxX = max(self._xVertices);
        self._boundsMinY = min(self._yVertices);
        self._boundsMaxY = max(self._yVertices);


    # Determine if this treasure intersects hole.
    # First check the rectangle's bounding box for efficiency.
    def intersectsHole(self, hole:Hole) -> bool:
        holeLeft = hole.centreX - hole.width/2;
        holeRight = hole.centreX + hole.width/2;
        holeBottom = hole.centreY + hole.height/2;
        holeTop = hole.centreY - hole.height/2;

        boundingXOverlap = self._boundsMinX <= holeRight and self._boundsMaxX >= holeLeft;
        boundingYOverlap = self._boundsMinY <= holeBottom and self._boundsMaxY >= holeTop;

        if self._rotation == 0 or self._rotation == 90:
            return boundingXOverlap and boundingYOverlap;

        intersect = False;
        if boundingXOverlap and boundingYOverlap:
            try:
                holePolygon = Polygon([(holeLeft, holeTop), (holeRight, holeTop), (holeRight, holeBottom), (holeLeft, holeBottom)]);
                intersect = self._polygon.intersects(holePolygon);
            except:
                print("error finding intersection of hole and site. This is not serious unless it happens often");
        
        return intersect;

    # Print details of this treasure to outputFile, starting with the
    # line "rectangularTreasure:", followed by the bounding box on one line,
    # and then a "point" line for each vertex.
    def printTreasure(self, outputFile) -> None:
        print("rectangularTreasure:", file=outputFile);
        print(self._boundsMinX, self._boundsMinY, self._boundsMaxX, self._boundsMaxY , file=outputFile);
        vertices = zip(self._xVertices, self._yVertices);
        for v in vertices:
            print("point:", v[0], v[1], file=outputFile);


# This class encapsulates data for locations of individual artefacts, read from a csv file.
# The file has first title line "<ignored>, xcoord, ycoord".
# The following lines each have three comma separated values, the first is ignored,
# the next is the x coordinate of the artefact, the third is the y coordinate of the artefact.
#
# As the number of artefacts can be large, they are stored as a grid of data parcels
# in self._artefacts. self._artefacts[i][j] contains a DataParcel of artefacts. An
# artefact at location a,b (floats) is stored in self._artefacts[floor(a)][floor(b)]
# and so can be located effieciently.
#
# It also allows this treasure definition to be placed at a position on a field,
# rather than a field having to transpose each artefact.
class RealWorldData:
    # a data parcel of artefacts, stored in a list of (x,y) tuples
    class DataParcel:
        def __init__(self):
            self.artefacts = [];
            self._numArtefacts = 0;
    
        # add an artefact to the data parcel at the given coordinates
        def addArtefact(self, x:float, y:float):
            self.artefacts.append((x,y));
            self._numArtefacts += 1;

        def printParcel(self):
            print(self._numArtefacts, "", end='');

    # csvFileName is the name of the file specifying the location of artefacts.
    # See class documentation for the expected format.
    def __init__(self, csvFileName:str):
        csvfile = open(csvFileName,'r');
        lines = csv.DictReader(csvfile, delimiter=',');
        self._rawArtefacts = [];
        self.minX = -1;
        self.maxX = -1;
        self.minY = -1;
        self.maxY = -1;
        for row in lines:
            x = float(row['xcoord']);
            y = float(row['ycoord']);
            # keep track of the minimum and maximum x and y coordinates of artefacts (unnormalised)
            self._setMinX(x);
            self._setMaxX(x);
            self._setMinY(y);
            self._setMaxY(y);

            self._rawArtefacts.append((x,y));
        
        self._normalisedArtefacts = [];
        for a in self._rawArtefacts:
            self._normalisedArtefacts.append((a[0] - self.minX, a[1] - self.minY));

        # adjust minimum and maximum to the normalised values
        self.maxX = self.maxX - self.minX;
        self.maxY = self.maxY - self.minY;
        self.minX = 0;
        self.minY = 0;
        self.width = self.maxX;
        self.height = self.maxY;

        # create a 2D array of DataParcels, see class documentation for explanation
        self._artefacts = [[self.DataParcel() for y in range(math.ceil(self.height))] for x in range(math.ceil(self.width))];

        for i in range(len(self._normalisedArtefacts)):
            x = self._normalisedArtefacts[i][0];
            y = self._normalisedArtefacts[i][1];
            self._artefacts[math.floor(x)][math.floor(y)].addArtefact(x,y);
    
    # place the real world site so that the top left corner is at the given coordinates.
    # This top left coordinate is used when determining if a hole uncovers an artefact.
    def placeTopLeft(self, x:float, y:float):
        self.topLeftX = x;
        self.topLeftY = y;

    # Methods to keep track of the minimum and maximum coordinates for read world artefact data.
    # Only sets new value if it is the new minimum or maximum.
    def _setMinX(self, x:float):
        if self.minX == -1 or x < self.minX:
            self.minX = x;
    
    def _setMaxX(self, x:float):
        if self.maxX == -1 or x > self.maxX:
            self.maxX = x;

    def _setMinY(self, y:float):
        if self.minY == -1 or y < self.minY:
            self.minY = y;
    
    def _setMaxY(self, y:float):
        if self.maxY == -1 or y > self.maxY:
            self.maxY = y;

    # Returns the number of artefacts uncovered by the given hole
    def numArtefactsInHole(self, hole:Hole) -> int:

        # test against raw data
        # this code can be uncommented to test that the data parcel optimization
        # is behaving correctly by testing against the raw artefact data
        # normalisedArtefactCount = 0;
        # for i in range(len(self._normalisedArtefacts)):
        #     (x,y) = self._normalisedArtefacts[i];
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
        if left > self.topLeftX + self.width or \
            right < self.topLeftX or \
            top > self.topLeftY + self.height or \
            bottom < self.topLeftY:
            return 0;

        # determine in which data parcels we should look for artefacts
        startX = math.floor(max(left, self.topLeftX) - self.topLeftX);
        endX = math.floor(min(right, self.topLeftX + self.width) - self.topLeftX); 
        startY = math.floor(max(top, self.topLeftY) - self.topLeftY);
        endY = math.floor(min(bottom, self.topLeftY + self.height) - self.topLeftY); #inclusive

        # for each data parcel of interest, examine its list of artefacts and check if it
        # is within the hole
        artefactCount = 0;
        try:
            for x in range(startX, endX + 1):
                for y in range(startY, endY + 1):
                    parcel = self._artefacts[x][y];
                    for i in range(len(parcel.artefacts)):
                        artefactX = self.topLeftX + parcel.artefacts[i][0];
                        artefactY = self.topLeftY + parcel.artefacts[i][1];
                        if left <= artefactX and \
                            right >= artefactX and \
                            top <= artefactY and \
                            bottom >= artefactY:
                            artefactCount += 1;
            # if testing against raw data (see above in this method), uncomment:
            # if (artefactCount != normalisedArtefactCount):
            #     print("** artefact count error");

            return artefactCount;
        except:
            print("error:", x, "artefact max:", len(self._artefacts));
            print(traceback.print_exc())
            exit();
    
    # print out the artefacts in all data parcels to the given file
    def printData(self, file):
        for i in range(len(self._artefacts)):
            for j in range(len(self._artefacts[i])):
                for k in range(len(self._artefacts[i][j].artefacts)):
                    print("artefact:", self._artefacts[i][j].artefacts[k][0] + self.topLeftX, self._artefacts[i][j].artefacts[k][1] + self.topLeftY, file=file);


# A Treasure defined by locations of individual artefacts.
class RealWorldTreasure(Treasure):

    # If the data argument is provided, it will be used. If not,
    # data will be read from the file of the given name.
    # This is to avoid having to read from the file repeatedly which is time consuming.
    def __init__(self, csvFileName:str = "", data:RealWorldData = None):
        if (data == None):
            self._data = RealWorldData(csvFileName);
        else:
            self._data = data;

    # Place the treasure randomly on a Field of the given dimensions.
    # Set's the _data's top left position. The treasure lies wholly within
    # the field.
    def placeRandomly(self, fieldWidth:int, fieldHeight:int) -> None:
        # check the treasure will fit
        if self._data.width > fieldWidth or self._data.height > fieldHeight:
            print("treasure doesn't fit on the field");
            exit();

        # now place it randomly on field.
        xRandom = random.random();
        yRandom = random.random();
        # self._data.minX and self._data.minY are assumed to be 0
        if self._data.minX != 0 or self._data.minY != 0:
            print("error, min value not 0 in real world treasure");

        topLeftX = xRandom * (fieldWidth - self._data.width);
        topLeftY = yRandom * (fieldHeight - self._data.height);
        
        self._data.placeTopLeft(topLeftX, topLeftY);
        self._treasurePlaced = True;

    # Return True if this treasure intersects the hole, otherwise False.
    def intersectsHole(self, hole:Hole) -> bool:
        self.artefactCount = self._data.numArtefactsInHole(hole);

        if (self.artefactCount > 0):
            return True;
        return False;
    
    # Print this treasure to outputFile, starting with a line "realworldTreasure:"
    # The a line for the bounding box, followed by one line for each artefact.
    def printTreasure(self, outputFile) -> None:
        print("realworldTreasure:", file=outputFile);
        print(self._data.topLeftX, self._data.topLeftY, \
            self._data.width + self._data.topLeftX, self._data.height + self._data.topLeftY, file=outputFile);
        self._data.printData(outputFile);

    # return the RealWorldData object which defines the treasure. This is useful so
    # it can be re-used to avoid repeatedly reading data from the file
    def getData(self) -> RealWorldData:
        return self._data;


# A Treasure defined by an arbitrary rotated polygon. The vertically oriented
# polygon is specified in Shapefile format.
# This treasure can be reused to avoid reading in the Shapefile data each time.
# placeRandomly() changes its position.
class PolygonTreasure(Treasure):

    # Read the given shapfile files and create the polygon normalised
    # to (0,0). The shapefile is assumed to define a polygon that is
    # vertically oriented.
    # If whollyWithinField, the treasure lies wholly
    # within the field. Otherwise partially as specified in the
    # Treasure.placeRandomly() comments.
    # It is assumed that the polygon has a high extent (i.e. fills most of
    # its bounding box, rather than having big open curves or long thin arms).
    # This is to ensure that some of the treasure intersects the field
    # when the bounding box is partially within the field.
    def __init__(self, fileName:str, rotation:float=0, whollyWithinField:bool = False):
        sf = shapefile.Reader(HolesDictionary.getCaseStudiesDataDirectoryName() + "/" + fileName);
        shapes = sf.shapes();
        polygon = shapes[0];
        polygonPoints = [];
        for p in polygon.points:
            polygonPoints.append(p);
        self._mPoints = polygonPoints;
        self._rotation = rotation;
        self._whollyWithinField = whollyWithinField;

        # calculate bounding box
        minX = sys.maxsize;
        minY = sys.maxsize;
        maxX = -1*sys.maxsize;
        maxY = -1*sys.maxsize;
        horizontalPoints = [];
        for i in range(len(self._mPoints)):
            point = self._mPoints[i];
            horizontalPoints.append((-1*point[1], point[0]));
        
        for j in range(len(horizontalPoints)):
            point = horizontalPoints[j];
            if point[0] < minX:
                minX = point[0];
            if point[1] < minY:
                minY = point[1];
            if point[0] > maxX:
                maxX = point[0];
            if point[1] > maxY:
                maxY = point[1]
            
        # normalize points to have 0 minimum x and y coordinates
        self._normalisedPoints = [];
        for p in horizontalPoints:
            self._normalisedPoints.append((p[0] - minX, p[1] - minY));

        self._originalPolygon = Polygon(self._normalisedPoints);
        self._originalBounds = self._originalPolygon.bounds;
        self._originalCentre = ((self._originalBounds[0] + self._originalBounds[2]) / 2, (self._originalBounds[1] + self._originalBounds[3]) / 2);

    # Place the treasure on a Field of the given dimensions in a random position.
    # Rotate the polygon and set the bounding box. The treasure lies partially
    # within the field as described in Treasure.placeRandomly() comments
    # unless self._whollyWithinField is True in which case is lies wholly
    # within the field. The treasure is stored in self._polygon.
    def placeRandomly(self, fieldWidth:int, fieldHeight:int) -> None:
        q = rotate(self._originalPolygon, -1*self._rotation);
        qBounds = q.bounds;
        boundWidth = qBounds[2] - qBounds[0];
        boundHeight = qBounds[3] - qBounds[1];
        if boundWidth > fieldWidth or boundHeight > fieldHeight:
            print("error: polygon site doesn't fit on field");
            exit(1);
        randomX = random.random();
        randomY = random.random();
        if self._whollyWithinField:
            centreX = (randomX * (fieldWidth - boundWidth)) + boundWidth / 2;
            centreY = (randomY * (fieldHeight - boundHeight)) + boundHeight / 2;
        else:
            centreX = randomX * (fieldWidth - (2/6) * boundWidth) + (1/6) * boundWidth;
            centreY = randomY * (fieldHeight - (2/6) * boundHeight) + (1/6) * boundHeight;

        shiftX = centreX - (qBounds[2] + qBounds[0])/2;
        shiftY = centreY - (qBounds[3] + qBounds[1])/2;
        shiftedPolygon = translate(q, xoff=shiftX, yoff=shiftY);
        self._polygon = shiftedPolygon;
        self._bounds = self._polygon.bounds;
        self._minBoundingX = self._bounds[0];
        self._minBoundingY = self._bounds[1];
        self._maxBoundingX = self._bounds[2];
        self._maxBoundingY = self._bounds[3];


    # Returns True iff hole intersects this treasure.
    def intersectsHole(self, hole:Hole) -> bool:
        holeLeft = hole.centreX - hole.width / 2;
        holeRight = hole.centreX + hole.width / 2;
        holeTop = hole.centreY - hole.height / 2;
        holeBottom = hole.centreY + hole.height / 2;

        # check the bounding box for efficiency
        bounds = self._polygon.bounds;
        if holeLeft > bounds[2] or \
            holeRight < bounds[0] or \
            holeTop > bounds[3] or \
            holeBottom < bounds[1]:
            return False;

        holePolygon = Polygon([(holeLeft, holeTop), (holeRight, holeTop), (holeRight, holeBottom), (holeLeft, holeBottom)]);

        return self._polygon.intersects(holePolygon);
    
    # Print this treasure to outputFile, starting with a line "polygonTreasure:"
    # then a line specifying the bounding box, then one line for each polygon vertex.
    def printTreasure(self, outputFile):
        print("polygonTreasure:", file=outputFile);
        print(self._minBoundingX, self._minBoundingY, \
                    self._maxBoundingX, self._maxBoundingY, file=outputFile);
        for point in self._polygon.exterior.coords:
            print("point: " + str(point[0]) + " " + str(point[1]), file=outputFile);


# A Treasure that is a circle.
class CircularTreasure(Treasure):

    # Create the circle with the given radius.
    def __init__(self, radius:float):
        self._radius = radius;

    # Implements the well known clamp function
    def clamp(self, x, minimum, maximum):
        retval = max(minimum, min(x, maximum));
        return retval;

    # Place the centre of the circle on a Field of the given dimensions
    # in a random position. The treasure lies wholly within the field.
    def placeRandomly(self, fieldWidth:int, fieldHeight:int) -> None:
        if (fieldHeight < self._radius * 2 or fieldWidth < self._radius * 2):
            print("field not big enough for treasure");
            exit(1);

        xRandom = random.random();
        yRandom = random.random();
        self._centreX = xRandom * (fieldWidth - 2*self._radius) + self._radius;
        self._centreY = yRandom * (fieldHeight - 2*self._radius) + self._radius;

    # Return True if this treasre intersects hole, otherwise False.
    def intersectsHole(self, hole:Hole) -> bool:
        holeL = hole.centreX - hole.width/2;
        holeR = hole.centreX + hole.width/2;
        holeT = hole.centreY - hole.height/2;
        holeB = hole.centreY + hole.height/2;
    
        closestXToCircleClamp = self.clamp(self._centreX, holeL, holeR);
        closestYToCircleClamp = self.clamp(self._centreY, holeT, holeB);

        distanceToClosestPoint = math.sqrt((self._centreX - closestXToCircleClamp)**2 + (self._centreY - closestYToCircleClamp) **2);
    
        return distanceToClosestPoint <= self._radius;

    # Print this treasure to outputFile, starting with the line "circularTreasure:"
    # then a line specifying the centre and radius.
    def printTreasure(self, outputFile) -> None:
        print("circularTreasure:", file=outputFile)
        print(self._centreX, self._centreY, self._radius, file=outputFile);


# A manager of a RectangularTreasure
class RectangularTreasureManager(TreasureManager):
    # The rectangular treasure will have these parameters. If whollyWithinField,
    # the Treasure will be placed wholly within the field, otherwise partially
    # as described in Treasure.placeRandomly() comments.
    def __init__(self, longSide:float, shortSide:float, rotation:float, whollyWithinField:bool = False):
        self._longSide = longSide;
        self._shortSide = shortSide;
        self._rotation = rotation;
        self._treasure = None;
        self._whollyWithinField = whollyWithinField;

    def getTreasure(self) -> Treasure:
        if self._treasure == None:
            self._treasure = RectangularTreasure(self._longSide, self._shortSide, self._rotation, self._whollyWithinField);
        return self._treasure;

    def getTreasureDescription(self) -> str:
        return "rectangle " + str(round(self.getLongSide(), 2)) + "x" + str(round(self.getShortSide(), 2)) + " orientation " + str(self.getRotation());

    # Return the length of the long side of the treasure
    def getLongSide(self) -> float:
        return self._longSide;

    # Return the length of the short side of the treasure
    def getShortSide(self) -> float:
        return self._shortSide;
    
    # Return the rotation of the treasure
    def getRotation(self) -> float:
        return self._rotation;


# A manager of a CircularTreasure
class CircularTreasureManager(TreasureManager):
    # The circular treasure will have this radius
    def __init__(self, radius = float):
        self._radius = radius;
        self._treasure = None;

    def getTreasure(self) -> Treasure:
        if self._treasure == None:
            self._treasure = CircularTreasure(self._radius);
        return self._treasure;

    def getTreasureDescription(self) -> str:
        return "circular " + str(self.getRadius());

    # Return the radius of the treasure
    def getRadius(self) -> float:
        return self._radius;


# A manager of a PolygonTreasure
class PolygonTreasureManager(TreasureManager):
    # shapeFileName is the name of a file in ShapeFile format that defines
    # the polygon shape, oriented vertically.
    def __init__(self, shapeFileName:str, rotation:float):
        self._shapeFileName = shapeFileName;
        self._treasure = None;
        self._rotation = rotation;

    def getTreasure(self) -> Treasure:
        if self._treasure == None:
            self._treasure = PolygonTreasure(self._shapeFileName, self._rotation, False);
        return self._treasure;

    def getTreasureDescription(self) -> str:
        caseStudy = self.getShapeFileName().removesuffix(".zip");
        return "casestudy " + caseStudy + " orientation " + str(self.getRotation());

    # Get the name of the ShapeFile file defining the polygon
    def getShapeFileName(self) -> str:
        return self._shapeFileName;

    # Return the rotation of the treasure.
    def getRotation(self) -> float:
        return self._rotation


# A manager of a RealWorldTreasure
class RealWorldTreasureManager(TreasureManager):
    # The treasure is defined by artefacts listed in artefactFileName.
    # See RealWorldData class for format of the file.
    def __init__(self, artefactFileName:str):
        self._artefactFileName = artefactFileName;
        self._treasure = None;

    def getTreasure(self) -> Treasure:
        if self._treasure == None:
            self._treasure = RealWorldTreasure(self._artefactFileName);
        return self._treasure;

    def getTreasureDescription(self) -> str:
        fileName = self.getArtefactFileName();
        p = Path(fileName);
        firstWord = re.split(r'\.| ', p.name)[0];
        return "realworld " + firstWord;

    # Return the file name of the file defining the artefacts.
    def getArtefactFileName(self) -> str:
        return self._artefactFileName;


# A manager that returns a new RectangularTreasure with random site area,
# length (from the length of a 1:1 rectangle to that of a 40:1 rectangle given
# the site area), and orientation. There is also an option to randomise the ratio
# directly rather than the length. In experiments with randomised treasure specs,
# getTreasure() should be called in each iteration of the simulation, as it
# is different each time.
class RandomisedTreasureManager(TreasureManager):
    def __init__(self, randomiseRatio:bool):
        self._treasure = None;
        self._randomiseRatio = randomiseRatio;

    def getTreasure(self) -> Treasure:
        rotation = random.random() * 180;

        siteArea = random.uniform(1, 200);

        if self._randomiseRatio:
            ratio = random.uniform(1, 40);
            longSide = math.sqrt(ratio * siteArea);
            shortSide = siteArea / longSide;
        else:
            # randomise length
            maxLongestSide = math.sqrt(siteArea * 40);
            minLongestSide = math.sqrt(siteArea);
            longSide = random.uniform(minLongestSide, maxLongestSide);
            shortSide = siteArea / longSide;

        return RectangularTreasure(longSide, shortSide, rotation, False);

    def getTreasureDescription(self) -> str:
        return "randomtreasure";
