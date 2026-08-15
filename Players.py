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


# This file defines the abstract class Player and implements several subclasses.
# A Player is called to play() digging Holes on a Field to find Treasure.
# Each Player implements a different layout algorithm, such as Hexagonal-like,
# Random, etc.

# The code was only tested with the experiments explored in the articles. It 
# may not be correct in all circumstances.

# See the README.md file for more details.

from abc import abstractmethod, ABC
from Field import Field
from Hole import Hole
import random
import math
import numpy as np
from numpy.random import Generator
from scipy.stats import qmc


# An abstract archaeologist that digs holes in a field according to its layout algorithm,
# given a Field and the desired number of holes to dig.
# The actual number of holes dug may differ from the desired due to layout
# constraints.
# It is assumed that subclasses dig the same number of holes when the desired number of holes
# is the same.
# Player's are not in general reusable - create a new one before calling play().
class Player(ABC):

    # Digs holes according to the layout algorithm implemented by the Player
    # subclass, and returns tuple indicating if treasure was found
    # and the number of holes determined by the layout algorithm.
    # returnAfterHit indictes whether to return as soon as a treasure is found.
    # NOTE: the number of holes returned is the total number of holes
    # that would be dug if returnAfterHit was False, i.e. the number of holes
    # determined by the layout algorithm.
    @abstractmethod
    def play(self, returnAfterHit:bool = True) -> tuple[bool, int]:
        pass;


# an abstract Player that provides support for a staggered layout
class StaggeredPlayer(Player):

    # Create a staggered layout with the given parameters.
    #
    # Returns whether treasure was found and the number of holes determined by the layout
    # algorithm. NOTE: this is the total number of holes that would be dug if returnAfterHit was
    # False when play() is called.
    #
    # The top left of the field is considered to be 0,0.
    #
    # xHoles and yHoles are numbers of holes in the x and y directions respectively.
    # borderX and borderY are the left and top borders respectively where no holes are placed
    # (these should be at least holeSize/2 as the centre of a hole may fall on a border).
    # dX and dY are the distances between holes in the x and y directions respectively.
    # staggerY is True if the layout should be staggered in the y direction as well as the x.
    # If randomise is true, each hole is shifted in both x and y directions by a random 
    # amount, according to a normal distribution with the original position as mean,
    # and the standard deviation dX/stdDevDivisor for the x direction and dY/stdDevDivisor for
    # the y direction.
    # The borders on the right and bottom of the field are determined by the above parameters
    # but it is assumed that they are equal to the borders on the left and top respectively
    # to 2 decimal places (otherwise an error is printed).
    # returnAfterHit indicates whether to return as soon as treasure is found, but the number of
    # holes returned will be as if this were False.
    def doStaggeredLayout(self, field:Field, holeSize:float, xHoles:int, borderX:float, dX:float, yHoles:int, borderY:float, dY:float, staggerY:bool, randomise:bool = False, stdDevDivisor = 1, returnAfterHit:bool = True) -> tuple[bool, int]:
        # check the parameters fit properly on the field
        if xHoles > 1 and yHoles > 1:
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
                # if (hit):
                #     self.numHolesSucceed += 1;

                #     if (isinstance(field, RealWorldField)):
                #         self.artefactCount += field.artefactCount;
                holesMade += 1;
                pos_x += dX;
                if returnAfterHit and found:
                    return found, xHoles * yHoles;
            row += 1;
        return found, holesMade;


# a Player that uses a scrambled 2-D halton distribution of holes.
# We use the SciPy implementation of the scrambled halton distribution.
# Note that if border is True, both horizontal and vertical borders will
# be enforced.
class HaltonPlayer(Player):

    # create the player with the given values
    # seed is the value to use with the NumPy random number generator.
    def __init__(self, field:Field, holeSize:float, numHoles:int, rng:Generator, border:bool=False):
        self._field = field;
        self._holeSize = holeSize;
        self._numHoles = numHoles;
        self._rng = rng;
        if border and (self._field.width != self._field.height):
            print("non square field not supported");
            exit();
        if (border and self._numHoles != 0):
            p =4;
            self._border = self._field.width / (p * (2/p + math.sqrt(numHoles) - 1));
        else:
            self._border = self._holeSize / 2;

    # Digs holes according to the scrambled Halton distribution.
    # Returns whether treasure was found and the number of holes
    # determined by the layout algorithm (which will be equal to the
    # number of holes supplied to the constructor for this layout).
    def play(self, returnAfterHit:bool = True) -> tuple[bool, int]:
        sampler = qmc.Halton(d=2, scramble=True, rng = self._rng);
        sample = sampler.random(n=self._numHoles);
        points = sample;
        found = False;
        # self.artefactCount = 0;
        self.numHolesSucceed = 0;
        for p in points:
            x = p[0] * (self._field.width - 2*self._border) + self._border;
            y = p[1] * (self._field.height - 2*self._border) + self._border;
            hit = self._field.digHole(self._holeSize, x, y);
            # if (hit):
            #     self.numHolesSucceed += 1;
            #     if (isinstance(self._field, Field)):
            #         self.artefactCount += self._field.artefactCount;
            found = hit or found;
            # return early. Note artefactCount and numHolesSucceeded won't be accurate, but
            # these are not currently used
            if returnAfterHit and found:
                return found, self._numHoles;
        return found, self._numHoles;


# A Player that uses the hexagonal-like layout algorithm
# (see the "Layout Matters" paper and the "size matters and layout matters
# layout algorithms.pdf" document).
# This layout is staggered horizontally - If the distance between holes
# in the same row is a, every other row is shifted right by a/2.
# Numbers of holes in a row and the number of rows are chosen
# to be close to the desired number of holes (supplied to the constructor)
# while also being close to hexagonal (i.e. the distance between holes in a
# row is nearly equal to the distance between the closest holes on adjacent
# rows, forming nearly equilateral triangles). If staggerY is True, this hexagonal
# constraint will hold "before" the additional staggering occurs, and because
# of this staggering the layout can no longer be called hexagonal.
#
# If LRBorder (left and right border) is True, each even row
# has a left border of a/4 (and so the left border for each odd row is 3*a/4
# as it is staggered). The right borders will be 3*a/4 for non-staggered rows
# and a/4 for staggered rows.
# If the distance between rows is c, the top and bottom borders are c/4 if
# TBBorder is True.
# If LRBorder or TBBorder is False, that border will be holeSize/2 as the
# centre of the hole may fall on a border.
# If the border is less than holeSize/2 the algorithm fails (self.layoutError is
# set to True). This could be modified to set the borders to this minimum value and
# recalculate the numbers of holes to use with "no" border (actually holeSize/2).
# If staggerY is True, each second hole in each row is shifted down by c/2,
# and the closest holes to the top and bottom will be c/4 from the field edge
# (if TBBorder is True).
# If randomise is True, hole positions are shifted in both x and y directions
# by a random amount according to a normal distribution, with the original
# position as mean, and standard deviation of dX/stdDevDivisor and dY/stdDevDivisor
# in each direction respectively (with the exception that holes on the border
# are not shifted in that direction).
class HexagonalLikePlayer(StaggeredPlayer):

    # create the player with the given values (see class comments)
    def __init__(self, field:Field, holeSize:float, numHoles:int, LRBorder:bool = True, staggerY:bool = False, randomise:bool = False, stdDevDivisor = 1, TBBorder:bool = True):
        # these are not private as subclasses may want them
        self.field = field;
        self.holeSize = holeSize;
        self.numHoles = numHoles;
        self.LRBorder = LRBorder;
        self.TBBorder = TBBorder;
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
    def _reviseNumHoles(self, n:int, xf:float, yf:float) -> tuple[int, int]:
        return (round(xf), round(yf));

    # Dig holes according to the hexagonal-like layout algorithm. See Player.play()
    # and this class's comments for more details.
    # Returns whether treasure was found and the number of holes determined by the layout
    # algorithm (the number of holes that would have been dug if returnAfterHit was False).
    # On return self.layoutError is True if the algorithm was unable to
    # fit the number of holes on the field, otherwise False.
    def play(self, returnAfterHit:bool = True) -> tuple[bool, int]:
        self.layoutError = False;
        p = 4;
        if (self.LRBorder and self.TBBorder):
            # calculate number of holes in a row according to the hexagonal-like formula.
            # Horizontal borders are a/p and vertical c/p, where a is the distance between
            # pits in a row, and c the distance between rows.
            numHoles_x = self.quadratic(\
                2 * self.field.height,
                4 * self.field.height / p - self.field.height + math.sqrt(3) * self.field.width - 2 * math.sqrt(3) * self.field.width / p,\
                -1 * math.sqrt(3) * self.field.width * self.numHoles);
            if self.staggerY:
                numHoles_x = self.quadratic(\
                    2 * self.field.height,\
                    4 * self.field.height / p - self.field.height + math.sqrt(3) * self.field.width / 2 - 2 * math.sqrt(3) * self.field.width / p,\
                    -1 * math.sqrt(3) * self.field.width * self.numHoles);
        elif (not self.LRBorder and not self.TBBorder):
            # all borders are holeSize/2
            numHoles_x = self.quadratic( \
                2 * self.field.height - 4 * self.holeSize/2,\
                math.sqrt(3) * self.field.width - 2 * math.sqrt(3) * self.holeSize/2 - self.field.height + self.holeSize,\
                math.sqrt(3) * (self.holeSize * self.numHoles - self.field.width * self.numHoles));
                # 2 * self.field.height, math.sqrt(3) * self.field.width - self.field.height, -1 * math.sqrt(3) * self.numHoles * self.field.width)
            if self.staggerY:
                numHoles_x = self.quadratic( \
                    2 * self.field.height - 4 * self.holeSize/2,\
                    self.holeSize - self.field.height + math.sqrt(3) * self.field.width / 2 - math.sqrt(3) * self.holeSize/2,
                    math.sqrt(3) * self.numHoles * (self.holeSize - self.field.width));
        elif (not self.LRBorder and self.TBBorder):
            # horizontal borders are holeSize/2, vertical are c/p, where c is the distance
            # between rows
            if self.staggerY:
                print("stagger Y with no horizontal border and a vertical border not supported");
                exit();
            
            numHoles_x = self.quadratic(2 * self.field.height * p,\
                math.sqrt(3) * self.field.width * p + 4 * math.sqrt(3) * (self.holeSize/2) - self.field.height * p - 2 * math.sqrt(3) * self.field.width - 2 * math.sqrt(3) * (self.holeSize/2) * p,\
                -1 * math.sqrt(3) * self.numHoles * (self.field.width - self.holeSize) * p)
        else:
            print("unsupported configuration in HexagonalLikePlayer");
            exit(1);
        
        if numHoles_x == 0:
            print("cannot place 0 holes");
            exit(1);
        # calculate number of rows
        numHoles_y = self.numHoles / numHoles_x;

        # turn our floats into integers
        actualNumHoles = self._reviseNumHoles(self.numHoles, numHoles_x, numHoles_y);

        # d_x is the distance between holes in the same row
        if (self.LRBorder):
            self.d_x = self.field.width / (2/p + actualNumHoles[0] - 0.5);
            border_x = self.d_x / p;
        else:
            self.d_x = (self.field.width - self.holeSize) / (actualNumHoles[0] - 0.5);
            border_x = self.holeSize / 2;
        
        if (self.TBBorder):
            if self.staggerY:
                self.d_y = self.field.height / (2/p + actualNumHoles[1] - 0.5);
            else:
                self.d_y  = self.field.height / (2/p + actualNumHoles[1] - 1);
            border_y = self.d_y / p;
        else:
            # no top and bottom border
            if self.staggerY:
                self.d_y = (self.field.height - self.holeSize) / (actualNumHoles[1] - 0.5);
            else:
                if actualNumHoles[1] == 1:
                    self.d_y = (self.field.height - self.holeSize);
                else:
                    self.d_y = (self.field.height - self.holeSize) / (actualNumHoles[1] - 1);
            border_y = self.holeSize / 2;

        # check that the holes fit on the field
        if border_x < self.holeSize/2 or border_y < self.holeSize/2 or self.d_x < self.holeSize or self.d_y < self.holeSize:
            # TODO: when the borders are too small, set to holeSize/2 and recalculate numbers of holes with no borders
            # using the equation near the top of this method.
            self.layoutError = True;

        return self.doStaggeredLayout(self.field, self.holeSize, actualNumHoles[0], border_x, self.d_x, actualNumHoles[1], border_y, self.d_y, self.staggerY, self.randomise, self.stdDevDivisor, returnAfterHit = returnAfterHit);


# A Player that adjusts the horizontal and vertical borders used in the
# HexagonalLikePlayer to make the layout truly hexagonal.
# This may not be the best way to implement a hexagonal layout.
# This player staggers holes horizontally - if the distance between holes
# in the same row is a, each even row is shifted right by a/2.
# Note that due to the adjustment of borders, it is based on a
# hexagonal-like layout with a/4 and c/4 horizontal and vertical
# borders respectively.
class HexagonalPlayer(HexagonalLikePlayer):

    # Use the given values. Note staggerY = True is not currently supported for this player.
    def __init__(self, field:Field, holeSize:float, numHoles:int, staggerY:bool = False):
        HexagonalLikePlayer.__init__(self, field, holeSize, numHoles, True, staggerY);
        if staggerY:
            print("staggering in the Y direction not supported for HexagonalPlayer");
            exit();
    
    # Digs holes according to the hexagonal layout algorithm.
    # Returns whether treasure was found and the number of holes determined by the layout
    # algorithm (the number of holes that would have been dug if returnAfterHit was False).
    # On return self.layoutError is True if the algorithm was unable to
    # fit the number of holes on the field, otherwise False.
    def play(self, returnAfterHit:bool = True) -> tuple[bool, int]:
        # calculate number of holes in a row according to the hexagonal-like formula
        p = 4;
        numHoles_x = self.quadratic(\
                2 * self.field.height,
                4 * self.field.height / p - self.field.height + math.sqrt(3) * self.field.width - 2 * math.sqrt(3) * self.field.width / p,\
                -1 * math.sqrt(3) * self.field.width * self.numHoles);

        if self.staggerY:
            print("staggering in the Y direction not supported for HexagonalPlayer");
            exit();
            # this formula for p = 2 hasn't been tested:
            # numHoles_x = self.quadratic(
            #     4 * self.field.height, 2 * self.field.height - math.sqrt(3) * self.field.width, \
            #     -2 * math.sqrt(3) * self.numHoles * self.field.width);
        
        # calculate number of rows
        if numHoles_x == 0:
            print("cannot place 0 holes");
            exit(1);
        numHoles_y = self.numHoles / numHoles_x;

        actualNumHoles = [round(numHoles_x), round(numHoles_y)];

        # fix the vertical border and c to their original values and adjust the horizontal border
        # and a to create a hexagonal layout
        if self.staggerY:
            pass;
        else:
            c  = self.field.height / (2/p + actualNumHoles[1] - 1);
        a = 2 * c / math.sqrt(3);
        border_x = (self.field.width - a * ((actualNumHoles[0]) - 0.5)) / 2;
        border_y = c/p;

        self.layoutError = False;

        # check if horizontal border is big enough to fit a hole at the edge, otherwise
        # set it to its minimum value and recalculate a, c, and border_y
        self.adjust = False;
        unexpected = False;
        if a < self.holeSize or border_y < self.holeSize / 2 or c < self.holeSize:
            unexpected = True;
        if border_x < self.holeSize / 2:
            self.adjust = True;
            a = (self.field.width - self.holeSize) / (actualNumHoles[0] - 0.5);
            c = (math.sqrt(3) * a) / 2;
            border_x = self.holeSize / 2;
            if self.staggerY:
                pass;
            else:
                border_y = (self.field.height - c * (actualNumHoles[1] - 1)) / 2
        
        # check if the new values allow the holes to fit on the field
        if border_x < self.holeSize / 2 or a < self.holeSize or border_y < self.holeSize / 2 or c < self.holeSize:
            self.layoutError = True;
        elif unexpected:
            print("unexpected case in HexagonalPlayer");

        return self.doStaggeredLayout(self.field, self.holeSize, actualNumHoles[0], border_x, a, actualNumHoles[1], border_y, c, self.staggerY, returnAfterHit=returnAfterHit);


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
    # there will be a border of half distance between holes (and rows) as if the layout
    # was a square grid with margins and the same number of holes.
    def __init__(self, field:Field, holeSize:float, numHoles:int, border:bool = False):
        self._numHoles = numHoles;
        self._field = field;
        self._holeSize = holeSize;
        self._numHorizontalParcels = math.ceil(50);
        self._numVerticalParcels = math.ceil(50);
        self.bucketWidth = self._field.width / self._numHorizontalParcels;
        self.bucketHeight = self._field.height / self._numVerticalParcels;

        if border and (self._field.width != self._field.height):
            print("non square fields not supported");
            exit();
        if border and numHoles != 0:
            p = 4;
            self._border = self._field.width / (p * (2/p + math.sqrt(numHoles) - 1));
        else:
            self._border = self._holeSize / 2;

    # returns whether newHole intersects and existing hole on the field
    def _intersectsExistingHole(self, newHole:Hole) -> bool:
        # assumes all holes on the field are of self._holeSize
        startXBucket = math.floor((newHole.centreX - self._holeSize) / self.bucketWidth);
        startYBucket = math.floor((newHole.centreY - self._holeSize) / self.bucketHeight);
        endXBucket = math.floor((newHole.centreX + self._holeSize) / self.bucketWidth);
        endYBucket = math.floor((newHole.centreY + self._holeSize) / self.bucketHeight);

        if startXBucket < 0:
            startXBucket = 0;
        if startYBucket < 0:
            startYBucket = 0;
        if endXBucket >= self._numHorizontalParcels:
            endXBucket = self._numHorizontalParcels - 1;
        if endYBucket >= self._numVerticalParcels:
            endYBucket = self._numVerticalParcels - 1;

        for xBucket in range(startXBucket, endXBucket + 1):
            for yBucket in range(startYBucket, endYBucket + 1):
                for i in range(len(self._holePositions[xBucket][yBucket])):
                    h = self._holePositions[xBucket][yBucket][i]

                    oldHole = Hole(h[0], h[1], self._holeSize, self._holeSize);
                    if oldHole.intersects(newHole):
                        # used for debugging the bucket system
                        # check = self._field.intersectsExistingHole(newHole);
                        # if not(check):
                        #     print("**error")
                        return True;
    
        # used for debugging the bucket system
        # check = self._field.intersectsExistingHole(newHole);
        # if check:
        #     print("**error")
        return False;

    # Digs holes randomly and returns tuple indicating if treasure was found
    # and the actual number of holes dug (NOTE: this is the total number of holes
    # that would be dug if returnAfterHit was False, i.e. the number of holes
    # determined by the layout algorithm, which for the random layout algorithm is
    # identical to the number of holes requested in the constructor).
    #
    # NOTE: holes don't overlap. If not all holes fit on the field this will never return
    def play(self, returnAfterHit:bool = True) -> tuple[bool, int]:
        h = 0;
        found = False;
        self.numHolesSucceed = 0;
        self.artefactCount = 0;
 
        self._holePositions = [[[] for y in range(self._numVerticalParcels)] for x in range(self._numHorizontalParcels)];
        
        fieldWidth = self._field.width;
        fieldHeight = self._field.height;
        while h < self._numHoles:
            randomXValue = random.random();
            randomYValue = random.random();
            x = randomXValue * (fieldWidth - 2 * self._border) + self._border;
            y = randomYValue * (fieldHeight - 2 * self._border) + self._border;
            hole = Hole(x, y, self._holeSize, self._holeSize);
            if not self._intersectsExistingHole(hole):
                # only dig the hole if it doesn't intersect another
                hit = self._field.digHole(self._holeSize, x, y);
                try:
                    self._holePositions[math.floor(x/self.bucketWidth)][math.floor(y/self.bucketHeight)].append((x,y));
                except Exception:
                    print ("error at x =", x, "eachBucketWidth =", self.bucketWidth, "y =", y);
                found = found or hit;
                # if (hit):
                #     self.numHolesSucceed += 1;
                #     if (isinstance(self._field, Field)):
                #         self.artefactCount += self._field.artefactCount;
                h += 1;
                if returnAfterHit and found:
                    return found, self._numHoles;
        return found, h;
