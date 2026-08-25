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

# This file defines the abstract class Experiment and implements the ExperimentRunner class.
# See the class comments for more details.

# The code was only tested with the experiments explored in the articles. It 
# may not be correct in all circumstances.

# See the README.md file for more details.

import io
import random
import math
import traceback
from pathlib import Path
import re
from shapely import Polygon, Point
from shapely.affinity import rotate
from abc import abstractmethod
from abc import ABC
from Field import Field
from Players import Player, HexagonalLikePlayer, HexagonalPlayer, HaltonPlayer, RandomPlayer
from Treasure import TreasureManager, RectangularTreasure, RealWorldTreasureManager, CircularTreasureManager, RectangularTreasureManager, PolygonTreasureManager, RandomisedTreasureManager
import numpy as np


# A class that describes an experiment to be run in the ExperimentRunner.
class Experiment(ABC):

    # the height and width of the square field.
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
    # Note data returned from Player.play() on number of
    # holes dug are the number of holes that would have been dug if this
    # were False (i.e. the number determined by the layout algorithm).
    @abstractmethod
    def getReturnAfterHit(self) -> bool:
        pass;

    # the file to output the results of the simulation. The file will be
    # placed in the "data" directory. For example "sizematters/7mCircle 100mField 0.5mPits.csv".
    # This includes the subdirectory of the data directory in which to save the data.
    @abstractmethod
    def getOutputFileName(self) -> str:
        pass;
    
    # the filename to output a printed field to if ExperimentRunner.printExperiment() is called.
    # Doesn't include suffix or "printedFields" directory (which is assumed).
    # If holesDug is None it is omitted.
    @abstractmethod
    def getPrintedFieldFileName(self, holesDug:int) -> str:
        pass;

    # the name of the type of player returned by getPlayer().
    @abstractmethod
    def getPlayerName(self) -> str:
        pass;

    # get the Player that implements the layout algorithm chosen for
    # the experiment.
    @abstractmethod
    def getPlayer(self, field:Field, holes:int) -> Player:
        pass;

    # get the treasure manager for this experiment
    @abstractmethod
    def getTreasureManager() -> TreasureManager:
        pass;


# A class that runs an experiment described by an Experiment object,
# and outputs results to a file as well as (optionally) standard output.
# Experiment parameters are as defined by the Experiment subclass provided
# (see Experiment above).
# Many iterations are run for each number of holes, with a Treasure
# placed randomly on a Field in each iteration, and a Player called
# to dig Holes on the Field to find the Treasure.
# After all iterations are run for a given number of holes, the success rate
# is printed to the output file.
class ExperimentRunner:

    # create an ExperimentRunner with the experiment to run
    def __init__(self, experiment: Experiment):
        self.mExperiment = experiment;
        self.realWorldDataCache = None;
        self.polygonTreasureCache = None;

    # print a description of the experiment to stdout    
    def printDescription(self):
        print(self.mExperiment.getPrintedFieldFileName(None));

    # creates the field and places treasure randomly
    def createFieldAndPlaceTreasure(self):
        self.field = Field(self.fieldSize, self.fieldSize);
        treasure = self.treasureManager.getTreasure();
        self.field.placeTreasure(treasure);

    # save the field, holes, and treasure after a single dig to a text file in
    # the "printedFields" directory. This file can be read by CreateFieldImage.py to
    # create a graphical depiction of the field.
    def printExperiment(self, numHoles:int) -> None:
        self._readExperimentValues();
        self.createFieldAndPlaceTreasure();
        player = self.mExperiment.getPlayer(self.field, numHoles);
        result = player.play(returnAfterHit=False);
        if isinstance(player, HexagonalLikePlayer):
            if player.layoutError:
                print("layout algorithm error: probably too many holes for the field size");
                self.printDescription();
        self._printField(result[1]);

    # prints the given Field to a file in the "printedFields" directory.
    # This file can be read by CreateFieldImage.py to create a graphical
    # depiction of the field. See that file for details of the format.
    def _printField(self, holesDug:int):
        filename = self.mExperiment.getPrintedFieldFileName(holesDug);
        filename = "printedFields/" + filename + ".hpf";
        outputFile = Path(filename);
        outputFile.parent.mkdir(exist_ok=True, parents=True);
        # print the field   
        self.field.printField(filename);
    
    # prints the results of the simulation after numRepeats digs have been run
    # for a given number of holesDug (holes is the desired number of holes supplied
    # to the layout algorithm, and holesDug the actual number of holes arrived at
    # by the layout algorithm).
    # successes are the number of digs where a hole found the treasure.
    # The desired number of holes, the actual number of holes, and the
    # success rate are printed to outputFile.
    def printResults(self, printData:bool, outputFile:io.TextIOWrapper, holes:int, holesDug:int, successes:int, numRepeats:int):
        outputFile.write(str(holes) + ", " + str(holesDug) + ", " + str(successes * 100 / numRepeats) + "\n");
        outputFile.flush();
        if printData:
            # if (self.realWorldData):
            #     print (holes, holesDug, successes * 100 / numRepeats, artefactCount / numRepeats, numHolesSucceed / numRepeats);
            # else:
            print (holes, holesDug, successes * 100 / numRepeats);

    # transfers the various parameters in mExperiment to member variables
    def _readExperimentValues(self) -> None:
        self.fieldSize = self.mExperiment.getFieldSize();
        self.holeSize = self.mExperiment.getHoleSize();

        self.holeIncrement = self.mExperiment.getHoleIncrement();
        self.smallNumHolesIncrement = self.mExperiment.getSmallNumHolesIncrement();
        self.smallNumHolesIncrementCutoff = self.mExperiment.getSmallNumHolesIncrementCutoff();

        self.startHoles = self.mExperiment.getStartHoles();
        self.maxHoles = self.mExperiment.getMaxHoles();

        self.treasureManager = self.mExperiment.getTreasureManager();

        self.numRepeats = self.mExperiment.getNumRepeats();
        self.smallNumHolesNumRepeats = self.mExperiment.getSmallNumHolesNumRepeats();
        self.smallNumHolesNumRepeatsCutoff = self.mExperiment.getSmallNumHolesNumRepeatsCutoff();

        self.stopAtSuccess = self.mExperiment.getStopAtSuccess();
        self.returnAfterHit = self.mExperiment.getReturnAfterHit();

        self.outputFileName = self.mExperiment.getOutputFileName();

    # Do an experiment simulating archaeological digs over range of hole numbers
    # (from self.startHoles to self.maxHoles or until self.stopAtSuccess success
    # rate is reached - usually 100%). The number of holes is incremented
    # each time around by self.holeIncrement, unless the number of holes is
    # less than self.smallNumHolesIncrementCutoff in which case it is incremented
    # by self.smallNumHolesIncrement.
    # For each such number of holes, self.numRepeats iterations are run, except
    # if the number of holes is less than self.smallNumHolesNumRepeatsCutoff
    # in which case self.smallNumHolesNumRepeats iterations are run.
    # In each iteration Treasure from self.treasureManager is placed on a new
    # Field and a Player from mExperiment.getPlayer() is called to play()
    # which involves digging Holes on the Field according to its layout
    # algorithm to see if it successfully finds the Treasure. A success rate is
    # then recorded over all iterations.
    # The data (number of holes and success rate) are saved in self.outputFileName
    # in the data directory (outputFileName may include a subdirectory of the data
    # directory). The data are also printed to standard out if printData is True.
    def runExperiment(self, printData = True) -> None:
        self._readExperimentValues();

        if (printData):
            print("generating \"" + self.mExperiment.getOutputFileName() + "\"");
        if printData:
            self.printDescription();
        
        # This is the value of the actual number of holes dug for the previous value of "holes".
        # As this is before any value of "holes" we set to -1
        lastHole = -1;

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
                # If we find that the layout is not new we skip the remaining repeats for that value of "holes".
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

                    if not new:
                        # we have seen this same layout from the player for a previous value of "holes",
                        # skip the remaining repeats for this value.
                        break;
                    
                    try:
                        result = player.play(self.returnAfterHit);

                        # Check for layout errors, usually because the desired layout with the given holeSize won't fit on the field.
                        # Use repeats == 1 as it weans out the "not new" number of holes
                        if repeats == 1 and (isinstance(player, HexagonalPlayer) or isinstance(player, HexagonalLikePlayer)):
                            if player.layoutError:
                                print("layout algorithm error: probably too many holes for the field size");
                                self.printDescription();
                                exit(1);
                        
                        if result[0]:
                            # the player uncovered treasure
                            successes += 1;
                            # if isinstance(self.treasureManger, RealWorldTreasureManager):
                            #     artefactCount += player.artefactCount;
                            #     numHolesSucceed += player.numHolesSucceed;

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
                            # only need to set this on the first repeat as all subsequent
                            # repeats will have the same holesDug
                            lastHole = holesDug;
                    except:
                        print("ERROR");
                        traceback.print_exc();
                        exit();
                if new:
                    self.printResults(printData, outputFile, holes, holesDug, successes, numRepeats);

                    if ((successes * 100 / numRepeats) >= self.stopAtSuccess):
                        return;
            
                # increment holes 
                if holes < self.smallNumHolesIncrementCutoff:
                    holes = holes + self.smallNumHolesIncrement;
                else:
                    holes = holes + self.holeIncrement;


## DEBUGGING FUNCTIONS

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
    fieldFileName = "printedFields/hexliketest.hpf";
    field = Field(100, 100);
    treasure = RectangularTreasure(20, 5, 0, False);
    field.placeTreasure(treasure);
    player = HexagonalLikePlayer(field, 0.5, 50, True, staggerY=False, TBBorder=True);
    # player = HexagonalPlayer(field, 0.5, 40, False);
    #player = RandomPlayer(field, 1, 18, True);
    #player = HaltonPlayer(field, 2, 2, 50);
    result = player.play();
    print ("hit:", result[0], "numHoles:", result[1]);
    # field.printField(fileName=fieldFileName);
    calculateHoleDistances(field);


# debugging function to print the top and bottom, and left and right borders
# the chosen player after play() is called.
def testBorders():
    field = Field(100, 100);
    treasure = RectangularTreasure(20, 5, 0);
    field.placeTreasure(treasure);
    player = HexagonalLikePlayer(field, 0.5, 8000, True, True, True, 8, TBBorder = True);
    # player = HexagonalPlayer(field, 0.5, 2000, False);
    # player = RandomPlayer(field, 0.5, 5000, True);
    # player = HaltonPlayer(field, 0.5, 5000, np.random.default_rng(12345), True);


    # Note, returnAfterHit is False
    result = player.play(False);
    print("numholes", result[1]);
    #field.printField("test field");
    testBordersOfField(field);

# debugging function to find the borders on a field (in which no holes have been dug).
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


if __name__ == "__main__":
    print("LayoutExperiments.py is the main file for this project");
