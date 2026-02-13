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

# This is a main file for the Holes project, for the Layout Matters article.
# It contains code to run Experiments on the ExperimentRunner implemented
# in Holes.py. It also contains code to plot graphs and tables using Plotter.py.
# Tables contain results of data analysis using Tables.py.

# Data produced is stored in subdirectories of the "data" directory and graphs and tables
# are stored in subdirectories of the "graphs" directory.

from Holes import Experiment, ExperimentRunner, Field, HexagonalLikePlayer, HaltonPlayer, RandomPlayer, HexagonalPlayer
from Tables import maximumDifferenceInSuccess, breakEvenRatios, areaUnderCurve, crossoverPoints, getMaximumDifferenceInSuccessLayout
from Experiments import BasicExperiment
from Plotter import plotExperiment, plotTable, plotSummaryExperiment, plotSummaryCrossoverTable, plotPolygonSuccessExperiment, plotSuccessExperiment, plotSummaryCrossoverGraph, plotSpecificNumberOfHoles, plotHolesForSuccessRatesTable, plotPolygonHolesForSuccessRatesTable, plotCostGraph
from rich.progress import Progress, BarColumn
from pathlib import Path
import math
import threading
import multiprocessing
import traceback
import time
import csv
from datetime import datetime
import os
import sys


# A basic layout experiment, using a HexagonalLikePlayer
class BasicLayoutExperiment(BasicExperiment):

    def __init__(self):
        super().__init__();
        self.mNumRepeats = globalNumRepeats;
        self.mSmallNumHolesNumRepeats = 10000;
        self.mSmallNumHolesNumRepeatsCutoff = 40;


# DEFINE EXPERIMENT SUBCLASSES FOR EACH LAYOUT ALGORITHM

class StaggerXYExperiment(BasicLayoutExperiment):

    def __init__(self):
        super().__init__();
        self.mStaggerY = True;
    
    def getPlayer(self, field:Field, holes:int):
        return HexagonalLikePlayer(field, self.mHoleSize, holes, self.mLRBorder, True);

class HaltonExperiment(BasicLayoutExperiment):

    def __init__(self):
        super().__init__();
        self.mSmallNumHolesIncrement = 3;
        self.mSmallNumHolesIncrementCutoff = 30;

    def getPlayer(self, field:Field, holes:int):
        return HaltonPlayer(field, self.mHoleSize, holes, self.mLRBorder);

class RandomExperiment(BasicLayoutExperiment):

    def __init__(self):
        super().__init__();
        self.mSmallNumHolesIncrement = 3;
        self.mSmallNumHolesIncrementCutoff = 30;

    def getPlayer(self, field:Field, holes:int):
        return RandomPlayer(field, self.mHoleSize, holes, self.mLRBorder);

class RandomisedStaggerXYExperiment(BasicLayoutExperiment):

    def __init__(self, stdDevDivisor:int):
        super().__init__();
        self.mStdDeviationDivisor = stdDevDivisor;

    def getPlayer(self, field:Field, holes:int):
        return HexagonalLikePlayer(field, self.mHoleSize, holes, self.mLRBorder, True, True, self.mStdDeviationDivisor);


class HexExperiment(BasicLayoutExperiment):

    def getPlayer(self, field:Field, holes:int):
        return HexagonalPlayer(field, self.mHoleSize, holes);


# SET SOME GLOBAL VARIABLES

# default number of simulation interations for each number of holes
globalHighNumRepeats = 10000;
globalNumRepeats = 3000;

# subdirectories of the data and graphs directories in which to store experiment results
summaryDirectory = "summary";
drillDownDirectory = "drilldown";
realWorldDirectory = "realworld";
largeRatioDirectory = "largeratio";
smallHolesDirectory = "smallnumholes"
specificHolesDirectory = "specificholes"
circularDirectory = "circular";


# FUNCTIONS TO RUN EXPERIMENTS

# This first group of functions runs experiments using the layout algorithm indicated in the function name.
# The experiment generates success data for the given algorithm over a range of number of holes
# (from 1 to the maximum number, or until 100% success rate is reached) using the ExperimentRunner
# in Holes.py. Data is stored in a file:
# "<treasureWidth>x<treasureHeight>rectangle <algorithm name> fieldsize<fieldSize> siteArea<siteArea>.csv"
# in the dir subdirectory of the data directory.
# The treasure is rectangular of dimensions treasureWidth x treasureHeight.
# The field is a square of size fieldSize x fieldSize.
# The site (aka treasure) area is siteArea (set separately to treasure dimensions due to rounding of those
# dimensions).
# Optionally, the number of holes at which to start the experiment is startHoles.
# Optionally, the maximum number of holes to use in the experiment is maxHoles.
# Optionally, the exact number of holes to use in the experiment is numHoles (usually an experiment
# will run from 1 hole to the maximum number but some experiments only consider a single number of holes).
# Optionally, the number of simulation iterations to run for each number of holes is numRepeats.
# Optionally, the subdirectory of the data directory where result data is stored is dir.
# Optionally, addToFileName is a string added to the end of the name of the data file.
# Optionally, printExperimentHoles is the number of holes to use when printing the experiment field.
# NOTE that when printExperimentHoles is defined, the experiment will not be run, only printed.
# Some functions allow setting of smallHolesNumRepeats, the number of simulation iterations
# to run for small numbers of holes.

def runElongatedHexLike(fieldSize : int, treasureWidth:float, treasureHeight:float, siteArea:int, startHoles:int = None, maxHoles:int = None, numHoles:int = None, numRepeats:int = globalNumRepeats, dir:str = summaryDirectory, addToFileName:str = "", printExperimentHoles:bool = None):
    experiment = BasicLayoutExperiment();
    experiment.mFieldSize = fieldSize;
    experiment.mTreasureShape="rectangle"
    experiment.mTreasureWidth = treasureWidth;
    experiment.mTreasureHeight = treasureHeight;
    experiment.mNumRepeats = numRepeats;
    experiment.mNumRepeats = numRepeats;
    if maxHoles != None:
        experiment.mMaxHoles = maxHoles;
    if numHoles != None:
        experiment.mStartHoles = numHoles;
        experiment.mMaxHoles = numHoles;
    if startHoles != None:
        experiment.mStartHoles = startHoles;
    if addToFileName != "":
        addToFileName = " " + addToFileName;
    twidth = round(treasureWidth, 2);
    theight = round(treasureHeight, 2);
    experiment.mOutputFileName = dir + "/" + str(twidth) + "x" + str(theight) + "rectangle hexlike fieldsize" + str(fieldSize) + " siteArea" + str(siteArea) + addToFileName +  ".csv";
    runner = ExperimentRunner(experiment);
    if printExperimentHoles != None:
        runner.printExperiment(printExperimentHoles);
    else:
        runner.runExperiment(printData=False);

def runElongatedHex(fieldSize : int, treasureWidth:float, treasureHeight:float, siteArea:int, numRepeats:int = globalNumRepeats, dir:str = "", addToFileName:str = "", printExperimentHoles:bool = None):
    experiment = HexExperiment();
    experiment.mFieldSize = fieldSize;
    experiment.mTreasureShape="rectangle"
    experiment.mTreasureWidth = treasureWidth;
    experiment.mTreasureHeight = treasureHeight;
    experiment.mNumRepeats = numRepeats;
    if addToFileName != "":
        addToFileName = " " + addToFileName;
    twidth = round(treasureWidth, 2);
    theight = round(treasureHeight, 2);
    experiment.mOutputFileName = dir + "/" + str(twidth) + "x" + str(theight) + "rectangle hex fieldsize" + str(fieldSize) + " siteArea" + str(siteArea) + ".csv";
    runner = ExperimentRunner(experiment);
    if printExperimentHoles != None:
        runner.printExperiment(printExperimentHoles);
    else:
        runner.runExperiment(printData=False);

def runElongatedStaggerXY(fieldSize: int, treasureWidth:float, treasureHeight:float, siteArea:int, startHoles:int = None, maxHoles:int = None, numHoles:int = None, numRepeats:int = globalNumRepeats, dir:str = summaryDirectory, addToFileName:str = "", printExperimentHoles:bool = None):
    experiment = StaggerXYExperiment();
    experiment.mFieldSize = fieldSize;
    experiment.mTreasureShape="rectangle"
    experiment.mTreasureWidth = treasureWidth;
    experiment.mTreasureHeight = treasureHeight;
    experiment.mStaggerY = True;
    experiment.mNumRepeats = numRepeats;
    if maxHoles != None:
        experiment.mMaxHoles = maxHoles;
    if numHoles != None:
        experiment.mStartHoles = numHoles;
        experiment.mMaxHoles = numHoles;
    if startHoles != None:
        experiment.mStartHoles = startHoles;
    if addToFileName != "":
        addToFileName = " " + addToFileName;
    twidth = round(treasureWidth, 2);
    theight = round(treasureHeight, 2);
    experiment.mOutputFileName = dir + "/" + str(twidth) + "x" + str(theight) + "rectangle staggerXY fieldsize" + str(fieldSize) + " siteArea" + str(siteArea) + addToFileName + ".csv";
    runner = ExperimentRunner(experiment);
    if printExperimentHoles != None:
        runner.printExperiment(printExperimentHoles);
    else:
        runner.runExperiment(printData=False);

def runElongatedHalton(fieldSize: int, treasureWidth:float, treasureHeight:float, siteArea:int, startHoles:int = None, maxHoles:int = None, numHoles:int = None, addToFileName:str = "", numRepeats:int = globalNumRepeats, smallNumHolesNumRepeats:int = None, dir:str = summaryDirectory, printExperimentHoles:bool = None):
    experiment = HaltonExperiment();
    experiment.mFieldSize = fieldSize;
    experiment.mHoleIncrement = 10;
    experiment.mTreasureShape="rectangle"
    experiment.mTreasureWidth = treasureWidth;
    experiment.mTreasureHeight = treasureHeight;
    experiment.mNumRepeats = numRepeats;
    if smallNumHolesNumRepeats != None:
        experiment.mSmallNumHolesNumRepeats = smallNumHolesNumRepeats;
    if maxHoles != None:
        experiment.mMaxHoles = maxHoles;
    if numHoles != None:
        experiment.mStartHoles = numHoles;
        experiment.mMaxHoles = numHoles;
    if startHoles != None:
        experiment.mStartHoles = startHoles;
    if addToFileName != "":
        addToFileName = " " + addToFileName;
    twidth = round(treasureWidth, 2);
    theight = round(treasureHeight, 2);
    experiment.mOutputFileName = dir + "/" + str(twidth) + "x" + str(theight) + "rectangle halton fieldsize" + str(fieldSize) + " siteArea" + str(siteArea) + addToFileName + ".csv";
    runner = ExperimentRunner(experiment);
    if printExperimentHoles != None:
        runner.printExperiment(printExperimentHoles);
    else:
        runner.runExperiment(printData=False);

def runElongatedRandom(fieldSize: int, treasureWidth:float, treasureHeight:float, siteArea:int, startHoles:int = None, maxHoles:int = None, numHoles:int = None, addToFileName:str = "", numRepeats:int = globalNumRepeats, smallNumHolesNumRepeats:int = None, dir:str = summaryDirectory, printExperimentHoles:bool = None):
    experiment = RandomExperiment();
    experiment.mFieldSize = fieldSize;
    experiment.mHoleIncrement = 10;
    experiment.mTreasureShape="rectangle"
    experiment.mTreasureWidth = treasureWidth;
    experiment.mTreasureHeight = treasureHeight;
    experiment.mNumRepeats = numRepeats;
    if smallNumHolesNumRepeats != None:
        experiment.mSmallNumHolesNumRepeats = smallNumHolesNumRepeats;
    if maxHoles != None:
        experiment.mMaxHoles = maxHoles;
    if numHoles != None:
        experiment.mStartHoles = numHoles;
        experiment.mMaxHoles = numHoles;
    if startHoles != None:
        experiment.mStartHoles = startHoles;
    if addToFileName != "":
        addToFileName = " " + addToFileName;
    twidth = round(treasureWidth, 2);
    theight = round(treasureHeight, 2);
    experiment.mOutputFileName = dir + "/" + str(twidth) + "x" + str(theight) + "rectangle random fieldsize" + str(fieldSize) + " siteArea" + str(siteArea) + addToFileName + ".csv";
    runner = ExperimentRunner(experiment);
    if printExperimentHoles != None:
        runner.printExperiment(printExperimentHoles);
    else:
        runner.runExperiment(printData=False);

# stdDevFactor is the value by which the distance between holes is divided to give one standard deviation
# for randomisation of hole positions. See StaggeredPlayer.doStaggeredLayout() in Holes.py for
# more information.
def runRandomisedStaggerXY(fieldSize:int, treasureWidth:float, treasureHeight:float, stdDevFactor:int, siteArea:int, startHoles:int = None, maxHoles:int = None, numHoles:int = None, addToFileName:str = "", numRepeats:int = globalNumRepeats, smallNumHolesNumRepeats:int = None, dir:str = summaryDirectory, printExperimentHoles:bool = None):
    experiment = RandomisedStaggerXYExperiment(stdDevFactor);
    experiment.mFieldSize = fieldSize;
    experiment.mTreasureShape = "rectangle"
    experiment.mTreasureWidth = treasureWidth;
    experiment.mTreasureHeight = treasureHeight;
    experiment.mStaggerY = True;
    experiment.mRandomise = True;
    experiment.mNumRepeats = numRepeats;
    if smallNumHolesNumRepeats != None:
        experiment.mSmallNumHolesNumRepeats = smallNumHolesNumRepeats;
    if maxHoles != None:
        experiment.mMaxHoles = maxHoles;
    if numHoles != None:
        experiment.mStartHoles = numHoles;
        experiment.mMaxHoles = numHoles;
    if startHoles != None:
        experiment.mStartHoles = startHoles;
    experiment.mStdDeviationDivisor = stdDevFactor;
    if addToFileName != "":
        addToFileName = " " + addToFileName;
    twidth = round(treasureWidth, 2);
    theight = round(treasureHeight, 2);
    experiment.mOutputFileName = dir + "/" + str(twidth) + "x" + str(theight) + "rectangle randomisedStaggerXY sd" + str(stdDevFactor) + " fieldsize" + str(fieldSize) + " siteArea" + str(siteArea) + addToFileName + ".csv";
    runner = ExperimentRunner(experiment);
    if printExperimentHoles != None:
        runner.printExperiment(printExperimentHoles);
    else:
        runner.runExperiment(printData=False);


# This next group of functions also runs experiments using the layout algorithm indicated in the function name.
# The treasure is a polygon described by polygonFile which must be a zip file containing files
# in the shapefile format. See https://en.wikipedia.org/wiki/Shapefile .
# The given shapefile data must define exactly one polygon and no other constructs.
# The polygon is assumed to be vertically oriented. If rotate is True it is rotated to be
# horizontally oriented.
# The success data for an experiment is stored in a file:
# "<orientation>polygon <algorithm name> fieldsize<fieldSize>.csv", where orientation is "vertical"
# or "horizontal", by default in the realWorldDirectory subdirectory of the data directory
# (see global variables above).
# The field is of size fieldSize.
# Optionally, printExperimentHoles is the number of holes to use when printing the experiment field.
# NOTE that when printExperimentHoles is defined, the experiment will not be run, only printed.
# Optionally, the subdirectory of the data directory where result data is stored is dir

def runPolygonHexLike(fieldSize: int, polygonFile:str, rotate:bool = False, dir:str = realWorldDirectory, printExperimentHoles:bool = None):
    experiment = BasicLayoutExperiment();
    experiment.mFieldSize = fieldSize;
    experiment.mNumRepeats = globalHighNumRepeats;
    experiment.mTreasureShape="polygon"
    experiment.mPolygonFile = polygonFile;
    experiment.mRotatePolygon = rotate;
    if rotate:
        experiment.mOutputFileName = "horizontalpolygon hexlike fieldsize" + str(fieldSize) + ".csv";
    else:
        experiment.mOutputFileName = "verticalpolygon hexlike fieldsize" + str(fieldSize) + ".csv";
    experiment.mOutputFileName = dir + "/" + experiment.mOutputFileName;
    runner = ExperimentRunner(experiment);
    if printExperimentHoles != None:
        runner.printExperiment(printExperimentHoles);
    else:
        runner.runExperiment(printData=False);

def runPolygonRandom(fieldSize:int, polygonFile:str, rotate:bool = False, dir:str = realWorldDirectory, printExperimentHoles:bool = None):
    experiment = RandomExperiment();
    experiment.mFieldSize = fieldSize;
    experiment.mHoleIncrement = 10;
    experiment.mNumRepeats = globalHighNumRepeats;
    experiment.mTreasureShape="polygon"
    experiment.mPolygonFile = polygonFile;
    experiment.mRotatePolygon = rotate;
    if rotate:
        experiment.mOutputFileName = "horizontalpolygon random fieldsize" + str(fieldSize) + ".csv";
    else:
        experiment.mOutputFileName = "verticalpolygon random fieldsize" + str(fieldSize) + ".csv";
    experiment.mOutputFileName = dir + "/" + experiment.mOutputFileName;
    runner = ExperimentRunner(experiment);
    if printExperimentHoles != None:
        runner.printExperiment(printExperimentHoles);
    else:
        runner.runExperiment(printData=False);

def runPolygonHalton(fieldSize: int, polygonFile:str, rotate:bool = False, dir:str = realWorldDirectory, printExperimentHoles:bool = None):
    experiment = HaltonExperiment();
    experiment.mFieldSize = fieldSize;
    experiment.mHoleIncrement = 10;
    experiment.mNumRepeats = globalHighNumRepeats;
    experiment.mTreasureShape="polygon"
    experiment.mPolygonFile = polygonFile;
    experiment.mRotatePolygon = rotate;
    if rotate:
        experiment.mOutputFileName = "horizontalpolygon halton fieldsize" + str(fieldSize) + ".csv";
    else:
        experiment.mOutputFileName = "verticalpolygon halton fieldsize" + str(fieldSize) + ".csv";
    experiment.mOutputFileName = dir + "/" + experiment.mOutputFileName;
    runner = ExperimentRunner(experiment);
    if printExperimentHoles != None:
        runner.printExperiment(printExperimentHoles);
    else:
        runner.runExperiment(printData=False);

def runPolygonStaggerXY(fieldSize:int, polygonFile:str, rotate:bool = False, dir:str = realWorldDirectory, printExperimentHoles:bool = None):
    experiment = StaggerXYExperiment();
    experiment.mFieldSize = fieldSize;
    experiment.mNumRepeats = globalHighNumRepeats; # was 5000;
    experiment.mTreasureShape="polygon"
    experiment.mPolygonFile = polygonFile;
    experiment.mRotatePolygon = rotate;
    experiment.mStaggerY = True;
    if rotate:
        experiment.mOutputFileName = "horizontalpolygon staggerXY fieldsize" + str(fieldSize) + ".csv";
    else:
        experiment.mOutputFileName = "verticalpolygon staggerXY fieldsize" + str(fieldSize) + ".csv";
    experiment.mOutputFileName = dir + "/" + experiment.mOutputFileName;
    runner = ExperimentRunner(experiment);
    if printExperimentHoles != None:
        runner.printExperiment(printExperimentHoles);
    else:
        runner.runExperiment(printData=False);

# stdDevFactor is the value by which the distance between holes is divided to give one standard deviation
# for randomisation of hole positions. See StaggeredPlayer.doStaggeredLayout() in Holes.py for
# more information.
def runPolygonRandomisedStaggerXY(fieldSize:int, polygonFile:str, stdDevFactor:int, rotate:bool = False, dir:str = realWorldDirectory, printExperimentHoles:bool = None):
    experiment = RandomisedStaggerXYExperiment(stdDevFactor);
    experiment.mFieldSize = fieldSize;
    experiment.mNumRepeats = globalHighNumRepeats; # was 5000;
    experiment.mTreasureShape = "polygon"
    experiment.mPolygonFile = polygonFile;
    experiment.mRotatePolygon = rotate;
    experiment.mStaggerY = True;
    experiment.mRandomise = True;
    experiment.mStdDeviationDivisor = stdDevFactor;
    if rotate:
        experiment.mOutputFileName = "horizontalpolygon randomisedStaggerXY sd" + str(stdDevFactor) + " fieldsize" + str(fieldSize) + ".csv";
    else:
        experiment.mOutputFileName = "verticalpolygon randomisedStaggerXY sd" + str(stdDevFactor) + " fieldsize" + str(fieldSize) + ".csv";
    experiment.mOutputFileName = dir + "/" + experiment.mOutputFileName;
    runner = ExperimentRunner(experiment);
    if printExperimentHoles != None:
        runner.printExperiment(printExperimentHoles);
    else:
        runner.runExperiment(printData=False);


# Run experiments with a circular treasure.
# These are not used in the Layout Matters article and can be ignored.

def runCircularHexagonal(fieldSize:int, treasureRadius:float, numRepeats:int = globalNumRepeats, numHoles:int = None, dir:str = circularDirectory):
    experiment = HexExperiment();
    experiment.mFieldSize = fieldSize;
    experiment.mTreasureShape="circle"
    experiment.mTreaureRadius = treasureRadius;
    experiment.mNumRepeats = numRepeats;
    addToFileName = "";
    if numHoles != None:
        experiment.mStartHoles = numHoles;
        experiment.mMaxHoles = numHoles;
        addToFileName = " holes" + str(numHoles);
    experiment.mOutputFileName = dir + "/" + str(treasureRadius) + "circle hex fieldsize" + str(fieldSize) + addToFileName +  ".csv";
    runner = ExperimentRunner(experiment);
    runner.runExperiment(printData=False);

def runCircularHexagonalLike(fieldSize:int, treasureRadius:float, numRepeats:int = globalNumRepeats, numHoles:int = None, dir:str = circularDirectory):
    experiment = BasicLayoutExperiment();
    experiment.mFieldSize = fieldSize;
    experiment.mTreasureShape="circle"
    experiment.mTreaureRadius = treasureRadius;
    experiment.mNumRepeats = numRepeats;
    addToFileName = ""
    if numHoles != None:
        experiment.mStartHoles = numHoles;
        experiment.mMaxHoles = numHoles;
        addToFileName = " holes" + str(numHoles);
    experiment.mOutputFileName = dir + "/" + str(treasureRadius) + "circle hexlike fieldsize" + str(fieldSize) + addToFileName + ".csv";
    runner = ExperimentRunner(experiment);
    runner.runExperiment(printData=False);

def runCircularStaggerXY(fieldSize:int, treasureRadius:float, numRepeats:int = globalNumRepeats, numHoles:int = None, dir:str = circularDirectory):
    experiment = StaggerXYExperiment();
    experiment.mFieldSize = fieldSize;
    experiment.mTreasureShape="circle"
    experiment.mTreaureRadius = treasureRadius;
    experiment.mNumRepeats = numRepeats;
    addToFileName = ""
    if numHoles != None:
        experiment.mStartHoles = numHoles;
        experiment.mMaxHoles = numHoles;
        addToFileName = " holes" + str(numHoles);
    experiment.mOutputFileName = dir + "/" + str(treasureRadius) + "circle staggerXY fieldsize" + str(fieldSize) + addToFileName + ".csv";
    runner = ExperimentRunner(experiment);
    runner.runExperiment(printData=False);


# Generates a summary graph of the overall success (over all number of holes)
# of various layout algorithms versus log of the treasure elongation ratio.
# Assumes all the raw success data is in the dir subdirectory of the data directory
# (defaults to summaryDirectory - see global variables above). For example the user
# should call the function generateSummaryData() before calling this function.
# The raw success data is then analysed by this function, computing the "area under the curve"
# of the success graphs specified by each success experiment. Such a computation is done
# for each layout algorithm for each treasure dimension.
# The results of this analysis is stored in a csv file whose name is:
# "summary fieldsize<fieldSize> siteArea<siteArea> maxholes<maximumHoles>.csv".
# in the outputDir subdirectory of the data directory.
# The area under the curve is approximated by summing the success rates for each number
# of holes, from 1 to maximumHoles (for cases where success data reaches 100% before
# maximumHoles, 100% success rate is used for the remaining number of holes).
# maximumHoles should be larger than any algorithm takes to reach 100%.
# The graph will be shown in a window if showGraph is True, otherwise just saved.
# The graph will zoom the y axis so that the mininum y value is the minimum value of the
# minFieldName algorithm if zoomCentral is True.
# If minY is set, that will be the minimum value on the y axis (and minFieldName is ignored).
# Data will not be re-analysed if compileData is False (rather a stored version
# of the "summary" data file will be used, which must exist).
# If suppressNumHoleWarning is True, a warning is printed if we encounter numbers of holes
# greater than maximumHoles in the data, otherwise no warning is produced.
# If saveGraph is False, no graph will be produced, only the summary data files mentioned
# above.
def generateSummaryGraph(fieldSize:int, siteArea:int, heights:list, showGraph:bool = True, zoomCentral:bool = False, minFieldName:str = "random", compileData:bool = True, maximumHoles=14000, dir:str = summaryDirectory, outputDir:str = summaryDirectory, suppressNumHoleWarning:bool = False, saveGraph = True, minY = None):
    fileStem = "summary fieldsize" + str(fieldSize) + " siteArea" + str(siteArea) + " maxholes" + str(maximumHoles);
    squareLength = round(math.sqrt(siteArea), 2);

    if (compileData):
        fileName = "data/" + outputDir + "/" + fileStem + ".csv";
        outputFile = Path(fileName);
        outputFile.parent.mkdir(exist_ok=True, parents=True);
        f = open(fileName, "w");
        f.write("ratio, hexlike, staggerXY, randomisedStaggerXY8, halton, random\n");

        for h in heights:
            height = round(h, 2);
            width = round(siteArea / h, 2);
            fileStart = dir + "/" + str(width) + "x" + str(height) + "rectangle";
            fileEnd = "fieldsize" + str(fieldSize) + " siteArea" + str(siteArea) + ".csv";

            successHexLike = areaUnderCurve(fileStart + " hexlike " + fileEnd, maximumHoles, suppressWarning =suppressNumHoleWarning)/maximumHoles;
            successStaggerXY = areaUnderCurve(fileStart + " staggerXY " + fileEnd, maximumHoles, suppressWarning =suppressNumHoleWarning)/maximumHoles;
            successHalton = areaUnderCurve(fileStart + " halton " + fileEnd, maximumHoles, suppressWarning =suppressNumHoleWarning)/maximumHoles;
            successRandom = areaUnderCurve(fileStart + " random " + fileEnd, maximumHoles, suppressWarning =suppressNumHoleWarning)/maximumHoles;
            successRandomisedStaggerXY8 = areaUnderCurve(fileStart + " randomisedStaggerXY sd8 " + fileEnd, maximumHoles, suppressWarning =suppressNumHoleWarning)/maximumHoles;

            if (round(h, 2) >= squareLength):
                w = siteArea / h;
                ratio = -h / w;
            else :
                w = siteArea / h;
                ratio = w / h;

            f.write(str(ratio) + ", " + str(successHexLike) + ", " +  str(successStaggerXY) + ", " + str(successRandomisedStaggerXY8) + ", " + str(successHalton) + ", " + str(successRandom) + "\n");

        f.flush();
    
    if saveGraph:
        graphFileName = fileStem;
        if zoomCentral:
            graphFileName = graphFileName + " central";
            minX = None;
            maxX = None;
            plotSummaryExperiment(fileStem, squareLength, siteArea, fieldSize, graphFileName, minFieldName=minFieldName, maxHoles = maximumHoles, dir = outputDir, outputDir = outputDir, minX = minX, maxX = maxX, zoom=True, showGraph = showGraph, minY = minY);
        else:
            plotSummaryExperiment(fileStem, squareLength, siteArea, fieldSize, graphFileName, minFieldName=minFieldName, maxHoles = maximumHoles, dir = outputDir, outputDir = outputDir, showGraph = showGraph, minY = minY);


# Generates a success graph of data from simulations using the real world polygon treasure,
# for the various layout algorithms.
# Raw data in the realWorldDirectory subdirectory of the data directory (see global variables
# above) must exist, for example the user should call generatePolygonData() before
# calling this function.
# A graph is shown in a window if showGraph is True.
# Data on horizontal orientation of the polygon will be used if rotate is True,
# otherwise data on the vertical orientation will be used.
# If zoom is True the graph will zoom in to the first 80 holes.
def generatePolygonSuccessGraph(fieldSize:int, zoom:bool = False, showGraph:bool = False, rotate:bool = False):
    if rotate:
        orientation = "horizontal";
    else:
        orientation = "vertical"

    zoomString = "";
    maxX = 600;
    maxY = -1;
    if zoom:
        maxY = 40;
        maxX = 80
        zoomString = "zoom ";
    
    filename = realWorldDirectory + "/" + orientation + "polygon " + zoomString + "fieldsize" + str(fieldSize) + ".png"
    plotPolygonSuccessExperiment(fieldSize, filename, maxX, maxY, rotate=rotate, showGraph = showGraph);


# Generates a summary graph of success of various layout algorithms versus log of the elongation
# ratio, including data for very elongated treasure dimensions.
# Raw data on success of each algorithm at treasure heights in "heights" must exist in the
# largeRatioDirectory subdirectory of the data directory.
# For example the user should call generateLargeRatioData() before calling this function.
# This function compiles that data, writing the "area under the curve" of the success graphs for each
# algorithm for each treasure dimensions to a file in the largeRatioDirectory named:
# "summary large ratio fieldsize<fieldSize> siteArea<siteArea>.csv".
# If showGraph is True a graph will be displayed in a window, otherwise just saved.
# If addToFileName is set, its value will be added to the summary file produced.
def generateSummaryGraphLargeRatio(fieldSize:int, siteArea:int, heights:list, showGraph:bool = False, addToFileName:str = "") -> None:
    maxHoles = 14000;
    if addToFileName != "":
        addToFileName = " " + addToFileName;
    fileStem = "summary large ratio fieldsize" + str(fieldSize) + " siteArea" + str(siteArea) + addToFileName
    fileName = "data/" + largeRatioDirectory + "/" + fileStem + ".csv";
    f = open(fileName, "w");
    f.write("ratio, randomisedStaggerXY, halton, random\n");

    for h in heights:
        height = round(h, 2);
        width = round(siteArea / h, 2);
        fileStart = largeRatioDirectory + "/" + str(width) + "x" + str(height) + "rectangle";
        fileEnd = "fieldsize" + str(fieldSize) + " siteArea" + str(siteArea) + ".csv";
        successHalton = areaUnderCurve(fileStart + " halton " + fileEnd, maximumHoles=maxHoles)/maxHoles;
        successRandom = areaUnderCurve(fileStart + " random " + fileEnd, maximumHoles=maxHoles)/maxHoles;
        successRandomisedStaggerXY8 = areaUnderCurve(fileStart + " randomisedStaggerXY sd8 " + fileEnd, maximumHoles=maxHoles)/maxHoles;
        
        squareLength = round(math.sqrt(siteArea), 2);
        if (round(h, 2) >= squareLength):
            w = siteArea / h;
            ratio = -h/w;
        else :
            w = siteArea / h;
            ratio = w/h;

        f.write(str(ratio) + ", " + str(successRandomisedStaggerXY8) + ", " +  str(successHalton) +", " + str(successRandom) + "\n");
    f.flush();
    plotSummaryExperiment(fileStem, squareLength, siteArea, fieldSize, fileStem, fieldNames=["randomisedStaggerXY", "halton", "random"], maxHoles = maxHoles, dir=largeRatioDirectory, showGraph = showGraph);


# Generates a table and graph of "crossover points" of the success of each layout
# algorithm in layoutAlgorithms and the halton layout algorithm, using the summary data.
# There is a column in the table for each layout algorithm, and a row for each siteArea.
# The fieldSize is a constant.
# It assumes that the halton algorithm starts out performing better than the given algorithm for
# larger vertical ratios, crosses over once and performs worse for a while at smaller vertical
# and horizontal ratios, and crosses over again (once) and performs better for larger horizontal ratios.
# See the "Layout Matters" paper and the summary graphs for more detail.
# If vertical is True, the crossover points for vertical elongation will be used (the first crossover),
# otherwise crossover points for horizontal elongation will be used (the second crossover).
# The function assumes summary data (produced by e.g. generateSummaryGraph()) for each layout algorithm
# and siteArea exists in the summaryDirectory.
# This function compiles data into a crossover data file in the summaryDirectory named:
# "<orientation> crossover fieldsize<fieldSize>.csv", where orientation is either "vertical" or
# "horizontal". The a Plotter function is called for table and graph generation.
# The graph and table is saved to the summaryDirectory subdirectory of the graphs directory.
def generateCrossoverTableAndGraph(fieldSize:int, siteAreas:list, layoutAlgorithms:list, vertical:bool, showGraph:bool = False) -> None:
    if vertical:
        orientation = "vertical"
    else:
        orientation = "horizontal"
    fileStem = summaryDirectory + "/" + orientation + " crossover fieldsize" + str(fieldSize);
    fileName = "data/" + fileStem + ".csv";
    f = open(fileName, "w");

    # write headers
    f.write("site area, ");
    for i in range(len(layoutAlgorithms)):
        f.write(layoutAlgorithms[i]);
        if i != len(layoutAlgorithms) - 1:
                f.write(", ");
    f.write("\n");

    # write data
    for i in range(len(siteAreas)):
        f.write(str(siteAreas[i]) + ", ");
        for j in range(len(layoutAlgorithms)):
            dataFileName = "summary fieldsize" + str(fieldSize) + " siteArea" + str(siteAreas[i]) + " maxholes" + str(6000) + ".csv";
            crossovers = crossoverPoints(dataFileName, layoutAlgorithms[j]);
            if vertical:
                f.write(str(-crossovers[0]));
            else:
                f.write(str(crossovers[1]));
            if j != len(layoutAlgorithms) - 1:
                f.write(", ");
        f.write("\n");
    f.flush();

    plotSummaryCrossoverTable(fileStem, layoutAlgorithms, 9, 4, "site area", 0.2, vertical, showGraph);
    plotSummaryCrossoverGraph(fileStem, layoutAlgorithms, "crossover points of various algorithms " + orientation, showGraph);


# As for generateCrossoverTableAndGraph() except that no graph is produced, and there is
# a row for each fieldSize while siteArea remains constant.
def generateFieldSizeCrossoverTable(fieldSizes:list, siteArea:int, layoutAlgorithms:list, vertical:bool) -> None:
    if vertical:
        orientation = "vertical"
    else:
        orientation = "horizontal"
    fileStem = summaryDirectory + "/" + orientation + " crossover siteArea" + str(siteArea);
    fileName = "data/" + fileStem + ".csv";
    f = open(fileName, "w");

    # write headers
    f.write("field size, ");
    for i in range(len(layoutAlgorithms)):
        f.write(layoutAlgorithms[i]);
        if i != len(layoutAlgorithms) - 1:
                f.write(", ");
    f.write("\n");

    # write data
    for i in range(len(fieldSizes)):
        f.write(str(fieldSizes[i]) + ", ");
        for j in range(len(layoutAlgorithms)):
            dataFileName = "summary fieldsize" + str(fieldSizes[i]) + " siteArea" + str(siteArea) + " maxholes" + str(9000) + ".csv";
            crossovers = crossoverPoints(dataFileName, layoutAlgorithms[j]);
            if vertical:
                f.write(str(-crossovers[0]));
            else:
                f.write(str(crossovers[1]));
            if j != len(layoutAlgorithms) - 1:
                f.write(", ");
        f.write("\n");
    f.flush();

    plotSummaryCrossoverTable(fileStem, layoutAlgorithms, 9, 4, "field size", 0.2, vertical);
 

# Generates graph for success of various layout algorithms for a single number of holes (numHoles),
# versus log of treasure elongation ratio.
# Success data must exist in the dir subdirectory of the data directory (defaults to
# specificHolesDirectory) for each treasure height in heights, for the given fieldSize
# and siteArea. For example the user should call generateSpecificNumberOfHolesData()
# before calling this function.
# If minFieldName is specified, it is the layout algorithm for which the minimum success rate
# is the minimum y axis value.
# This graph was not used in the paper and still needs testing.
def generateSpecificNumberOfHolesGraph(fieldSize:int, siteArea:int, heights:list, numHoles:int, dir:str = specificHolesDirectory, minFieldName:str = None) -> None:
    layoutAlgorithms = ["hexlike", "staggerXY", "randomisedStaggerXY sd8", "halton", "random"];

    plotSpecificNumberOfHoles(fieldSize, siteArea, heights, numHoles, layoutAlgorithms, dir = dir, minFieldName = minFieldName);


# Generates several graphs of success of various layout algorithms. A graph is generated for each of
# a small number of treasure elongation ratios, for each of a small number of site areas (currently
# uses only a single siteArea value), for each elongation orientation (vertical and horizontal).
# Raw success data for these must exist in the drillDownDirectory subdirectory of the data
# directory. For example the user should call generateSpecificRatioData() before calling this function.
def generateSpecificRatioGraphs(fieldSize:int):
    progress_columns = (
    "[progress.description]{task.description}",
    BarColumn());

    for vertical in [True, False]:
        if vertical:
            orientation = "vertical";
        else:
            orientation = "horizontal"
        for ratio in [1, 5, 20]:
            if not vertical and ratio == 1:
                # we don't need both orientations of a square treasure
                continue;
            for siteArea in [100]:
                if vertical:
                    width = round(math.sqrt(siteArea / ratio), 2);
                    height = round(siteArea/width, 2);
                else:
                    height = round(math.sqrt(siteArea / ratio), 2);
                    width = round(siteArea/height, 2);

                # set the maximum x value for each graph
                maxX = -1;
                if ratio == 1:
                    if siteArea == 20:
                        maxX = 1500;
                    if siteArea == 100:
                        maxX = 400;
                    if siteArea == 200:
                        maxX = 200;
                if ratio == 5:
                    if siteArea == 20:
                        maxX = 1500;
                    if siteArea == 100:
                        maxX = 400;
                    if siteArea == 200:
                        maxX = 200;
                if ratio == 20:
                    if siteArea == 20:
                        maxX = 1600;
                    if siteArea == 100:
                        maxX = 500;
                    if siteArea == 200:
                        maxX = 300;
                
                plotSuccessExperiment(fieldSize, width, height, siteArea, ["hexlike", "staggerXY", "randomisedStaggerXY sd8", "halton", "random"], maxX = maxX, showGraph = False);

                if siteArea == 100:
                    # plot a graph zoomed in to a small number of holes when siteArea is 100.
                    # These were not used in the paper.
                    plotSuccessExperiment(fieldSize, width, height, siteArea, ["hexlike", "staggerXY", "randomisedStaggerXY sd8", "halton", "random"], maxX = 30, maxY = 40, showGraph = False);


# Generates graphs showing the number of additional holes that must be dug
# to increase the success rate by 1 percentage point, over a range of
# success rates (from 1 to 100).
# Graphs are generated for a number of elongation ratios (with both horizontal and
# vertical orientation), for a site area of 100.
# Graphs will be saved in the "drilldown" subdirectory of the graphs directory.
# This was not used in the paper, but may be used in future.
def generateCostGraphs(fieldSize:int):
    for vertical in [True, False]:
        for ratio in [1, 5, 20]:
            if not vertical and ratio == 1:
                continue;
            for siteArea in [100]:
                if vertical:
                    width = round(math.sqrt(siteArea / ratio), 2);
                    height = round(siteArea/width, 2);
                else:
                    height = round(math.sqrt(siteArea / ratio), 2);
                    width = round(siteArea/height, 2);
                plotCostGraph(fieldSize, width, height, siteArea, "halton", maxY = 50);
                plotCostGraph(fieldSize, width, height, siteArea, "randomisedStaggerXY sd8", maxY = 50);


# Generates a table showing the number of holes needed to achieve success rates
# of 85%, 90%, and 100% using data from the drilldown (specific ratios) success
# experiments, for the treasure specifications (elongation ratios) and layout algorithms
# used in those experiments. Assumes that data is in the drilldown subdirectory of the
# data directory.
# fieldSize and siteArea are constants.
# There is a row in the table for each combination of treasure elongation ratio and
# layout algorithm.
def generateSpecificRatioHolesForSuccessRatesTables(fieldSize:int, siteArea:int):
    plotHolesForSuccessRatesTable(fieldSize, siteArea, ["hexlike", "staggerXY", "randomisedStaggerXY sd8", "halton", "random"]);


# Generates a table showing the number of holes needed to achieve success rates
# of 85%, 90%, and 100% using data from the real world polygon treasure
# experiments for the layout algorithms used in those experiments. The table
# shows value for a vertically oriented polygon unless rotate is True in
# which case data for the horizontally oriented polygon is used.
# There is a row in the table for each layout algorithm.
def generatePolygonHolesForSuccessRatesTables(fieldSize:int, rotate:bool = False):
    if rotate:
        orientation = "horizontal";
    else:
        orientation = "vertical"

    filename = "graphs/" + realWorldDirectory + "/holes for success rates table " + orientation + "polygon fieldsize" + str(fieldSize) + ".png"
    plotPolygonHolesForSuccessRatesTable(fieldSize, ["hexlike", "staggerXY", "randomisedStaggerXY sd8", "halton", "random"], not rotate);


# Generates a table showing the maximum difference in success rates across all
# layout algorithms across a range of numbers of holes. This uses the success data in the "drilldown"
# subdirectory of the data directory (which is assumed to exist). The treasure elongation ratios
# (and orientations) and layout algorithms used in those success experiments are considered.
# There is a column for the maximum difference across all numbers of holes, and another for
# the first 25 numbers of holes. There is a column for each treasure elongation ratio.
# Site area and field size are constant (both 100).
def generateMaximumDifferenceInSuccessTable():
    data = [];
    data.append(["Elongation", "Maximum Difference\nfor All Numbers of Pits\n(percentage points)", "Maximum Difference\nfor 1-25 Pits\n(percentage points)"]);

    for ratio in [1, 5, 20]:
        for vertical in [True, False]:
            if vertical:
                orientation = "Vertical";
            else:
                orientation = "Horizontal"

            if not vertical and ratio == 1:
                continue;
            
            if ratio == 1:
                data.append(["Square\n(1:1)"]);
            else:
                data.append([orientation + "ly Elongated\n(" + str(ratio) + ":1)"]);

            fieldSize = 100;
            siteArea = 100;
            layoutAlgorithms = ["hexlike", "staggerXY", "randomisedStaggerXY sd8", "halton", "random"];

            max = 0;
            max25 = 0;

            if vertical:
                width = round(math.sqrt(siteArea / ratio), 2);
                height = round(siteArea/width, 2);
            else:
                height = round(math.sqrt(siteArea / ratio), 2);
                width = round(siteArea/height, 2);

            for la1 in range(len(layoutAlgorithms)):
                for la2 in range(len(layoutAlgorithms)):
                    # we only consider each combination of layout algorithms once
                    if la2 < la1:
                        maxDiff = getMaximumDifferenceInSuccessLayout(fieldSize, siteArea, layoutAlgorithms[la1], layoutAlgorithms[la2], width, height);
                        if maxDiff > max:
                            max = maxDiff;
                        maxDiff25 = getMaximumDifferenceInSuccessLayout(fieldSize, siteArea, layoutAlgorithms[la1], layoutAlgorithms[la2], width, height, maxHoles=25);
                        if maxDiff25 > max25:
                            max25 = maxDiff25;
            data[len(data) - 1].append(round(max, 2));
            data[len(data) - 1].append(round(max25, 2));

    plotTable(data, 6, 5, 2, 3.2, drillDownDirectory + "/maximum differences in success siteArea 100.png", cellHeight=0.04, title="Maximum Difference in Success Rates\nAcross All Layout Algorithms\nFor Any Given Number of Pits\nField Size 100m x 100m, Site Area 100m\u00b2");


# A class that runs a function in a new process. Multiprocessing is
# used to decrease the running times of the experiments.
# Call start() to call the function with the given arguments,
# and join() to wait for it to complete.
class MyProcess(multiprocessing.Process):

    # function is the function to run, with the given arguments
    def __init__(self, function, *args, **kwargs):
        super().__init__();
        self.function = function;
        self.args = args;
        self.kwargs = kwargs;
    
    # run the function. However start() should be called, which in turn
    # causes this to run.
    def run(self):
        try:
            self.function(*self.args, **self.kwargs);
        except Exception as e:
            print("exception: ", e);
            traceback.print_exc();
            exit(1);


# Runs experiments to generate raw success data for various layout algorithms, for the given
# fieldSize and siteArea, and the treasure heights in height.
# These data are used in the summary analyses, where each point in a summary graph
# is a "summary" of success data for one layout algorithm (given a siteArea, fieldSize, and
# treasure elongation ratio), being the area under the curve of that success experiment
# (approximated by summing the success rates over all numbers of holes from 1 to a number
# greater than the maximum number any algorithm needs to reach 100% success rate).
# These data are also used in the low intensity summary analysis (small number of holes).
# Data is stored in the dir subdirectory of the data directory, in the filenames specified
# in the comments for the run...() functions (above).
# After calling this function, the data can be graphed using generateSummaryGraph().
def generateSummaryData(fieldSize:int, siteArea:int, height:list, dir:str = summaryDirectory) -> None:
    progress_columns = (
        "[progress.description]{task.description}",
        BarColumn());

    for h in height:
        with Progress(*progress_columns) as progress2:
            task = progress2.add_task("generating height = " + str(h) + " site area = " + str(siteArea) + " field size = " + str(fieldSize), total=10100, start=False);

            a = MyProcess(runElongatedHalton, fieldSize, siteArea/h, h, siteArea, dir=dir);
            a.start();
            b = MyProcess(runElongatedRandom, fieldSize, siteArea/h, h, siteArea, dir=dir);
            b.start();
            c = MyProcess(runElongatedHexLike, fieldSize, siteArea/h, h, siteArea, dir=dir);
            c.start();
            d = MyProcess(runElongatedStaggerXY, fieldSize, siteArea/h, h, siteArea, dir=dir);
            d.start();
            e = MyProcess(runRandomisedStaggerXY, fieldSize, siteArea/h, h, 8, siteArea, dir=dir);
            e.start();

            a.join();
            b.join();
            c.join();
            d.join();
            e.join();

            progress2.start_task(task);
            progress2.update(task, advance=10100)


# Runs experiments for various layout algorithms for a specific number of holes (numHoles).
# Experiments are run for the given fieldSize and siteArea and treasure heights in height.
# Data is stored in the dir subdirectory of the data directory, in the filenames specified in
# the comments for the run...() functions.
# This was not used in the paper and still needs testing.
def generateSpecificNumberOfHolesData(fieldSize:int, siteArea:int, height:list, numHoles:int = 30, dir:str = specificHolesDirectory):
    progress_columns = (
        "[progress.description]{task.description}",
        BarColumn());

    for h in height:
        with Progress(*progress_columns) as progress2:
            task = progress2.add_task("generating height = " + str(h) + " site area = " + str(siteArea) + " field size = " + str(fieldSize) + " holes = " + str(numHoles), total=10100, start=False);

            startHoles = numHoles - 15;
            stopHoles = numHoles + 15;
            a = MyProcess(runElongatedRandom, fieldSize, siteArea/h, h, siteArea, numRepeats=globalHighNumRepeats, numHoles=numHoles, dir=dir, addToFileName = "holes" + str(numHoles));
            a.start();
            b = MyProcess(runElongatedHalton, fieldSize, siteArea/h, h, siteArea, numRepeats=globalHighNumRepeats, numHoles=numHoles, dir=dir, addToFileName = "holes" + str(numHoles));
            b.start();
            c = MyProcess(runElongatedHexLike, fieldSize, siteArea/h, h, siteArea, numRepeats=globalHighNumRepeats, startHoles = startHoles, maxHoles = stopHoles, dir=dir, addToFileName = "holes" + str(numHoles));
            c.start();
            d = MyProcess(runElongatedStaggerXY, fieldSize, siteArea/h, h, siteArea, numRepeats=globalHighNumRepeats, startHoles = startHoles, maxHoles = stopHoles, dir=dir, addToFileName = "holes" + str(numHoles));
            d.start();
            e = MyProcess(runRandomisedStaggerXY, fieldSize, siteArea/h, h, 8, siteArea, numRepeats=globalHighNumRepeats, startHoles = startHoles, maxHoles = stopHoles, dir=dir, addToFileName = "holes" + str(numHoles));
            e.start();

            a.join();
            b.join();
            c.join();
            d.join();
            e.join();

            progress2.start_task(task);
            progress2.update(task, advance=10100)


# Generates success data for various layout algorithms using a small number of treasure
# elongation ratios for a small number of site areas (currently only one).
# Data is generated for vertical and horizontal orientations for each of the ratios.
# These data are used in the success analysis, and graphs can be produced by
# calling generateSpecificRatioGraphs().
# Data is stored in the drillDownDirectory subdirectory of the data directory,
# in the filenames specified in the comments for the run...() functions.
def generateSpecificRatioData(fieldSize:int):
    progress_columns = (
    "[progress.description]{task.description}",
    BarColumn());

    for vertical in [True, False]:
        if vertical:
            orientation = "vertical";
        else:
            orientation = "horizontal"

        for ratio in [1, 5, 20]:
            if not vertical and ratio == 1:
                # do not need both orientations of a square site
                continue;
            for siteArea in [100]:
                if vertical:
                    width = round(math.sqrt(siteArea / ratio), 2);
                    height = round(siteArea/width, 2);
                else:
                    height = round(math.sqrt(siteArea / ratio), 2);
                    width = round(siteArea/height, 2);
                
                with Progress(*progress_columns) as progress:
                    task = progress.add_task("generating " + orientation + " ratio " + str(ratio) + " site area " + str(siteArea) +  " field size = " + str(fieldSize), total=10100, start=False);

                    a = MyProcess(runElongatedRandom, fieldSize, width, height, siteArea, numRepeats=globalHighNumRepeats, dir=drillDownDirectory);
                    a.start();
                    b = MyProcess(runElongatedHalton, fieldSize, width, height, siteArea, numRepeats=globalHighNumRepeats, dir=drillDownDirectory);
                    b.start();
                    c = MyProcess(runElongatedHexLike, fieldSize, width, height, siteArea, numRepeats=globalHighNumRepeats, dir=drillDownDirectory);
                    c.start();
                    d = MyProcess(runElongatedStaggerXY, fieldSize, width, height, siteArea, numRepeats=globalHighNumRepeats, dir=drillDownDirectory);
                    d.start();
                    e = MyProcess(runRandomisedStaggerXY, fieldSize, width, height, 8, siteArea, numRepeats=globalHighNumRepeats, dir=drillDownDirectory)
                    e.start();

                    a.join();
                    b.join();
                    c.join();
                    d.join();
                    e.join();
                    
                    progress.start_task(task);
                    progress.update(task, advance=10100)


# Runs success experiments on the real world site shape defined in polygonFile for various layout algorithms.
# The polygon file must be a zip file containing files in the shapefile format.
# See https://en.wikipedia.org/wiki/Shapefile . The files must contain one polygon shape and no other constructs.
# The polygon is assumed to be elongated vertically. If rotate is true, the experiments
# are run on a rotated, horizontally elongated polygon.
# This is used in the real world analysis, and success graphs can be generated by
# calling generatePolygonSuccessGraph().
# Data is stored in the realWorldDirectory subdirectory of the data directory, in the filenames
# specified in the comments for the run...() functions.
def generatePolygonData(fieldSize:int, polygonFile:str, rotate:bool = False):
    progress_columns = (
        "[progress.description]{task.description}",
        BarColumn());
    
    if rotate:
        orientation = "horizontal";
    else:
        orientation = "vertical";

    with Progress(*progress_columns) as progress:
        task = progress.add_task("generating " + orientation + " polygon field size = " + str(fieldSize), total=10100, start=False);

        a = MyProcess(runPolygonRandom, fieldSize, polygonFile, rotate);
        a.start();
        b = MyProcess(runPolygonHalton, fieldSize, polygonFile, rotate);
        b.start();
        c = MyProcess(runPolygonHexLike, fieldSize, polygonFile, rotate);
        c.start();
        d = MyProcess(runPolygonStaggerXY, fieldSize, polygonFile, rotate);
        d.start();
        e = MyProcess(runPolygonRandomisedStaggerXY, fieldSize, polygonFile, 8, rotate);
        e.start();

        a.join();
        b.join();
        c.join();
        d.join();
        e.join();

        progress.start_task(task);
        progress.update(task, advance=10100)


# Runs experiments for various layout algorithms using the given fieldSize and siteArea.
# Experiments are run for each treasure height in height (the width is determined by
# the height and the siteArea). This can include treasure that is very elongated.
# Data is stored in the largeRatioDirectory subdirectory of the data directory,
# in the filenames specified in the comments for the run...() functions.
# The data are used in the summary analysis (similar to generateSummaryData() - 
# see those comments for details).
def generateLargeRatioData(fieldSize:int, siteArea:int, height:list) -> None:
    progress_columns = (
        "[progress.description]{task.description}",
        BarColumn());
    
    for h in height:
        with Progress(*progress_columns) as progress:    
            task = progress.add_task("generating height = " + str(h) + " site area = " + str(siteArea), total=10100, start=False);

            a = MyProcess(runElongatedRandom, fieldSize, siteArea/h, h, siteArea, dir=largeRatioDirectory, smallNumHolesNumRepeats = globalNumRepeats);
            a.start();
            b = MyProcess(runElongatedHalton, fieldSize, siteArea/h, h, siteArea, dir=largeRatioDirectory, smallNumHolesNumRepeats = globalNumRepeats)
            b.start();
            c = MyProcess(runRandomisedStaggerXY, fieldSize, siteArea/h, h, 8, siteArea, dir=largeRatioDirectory, smallNumHolesNumRepeats = globalNumRepeats);
            c.start();

            a.join();
            b.join();
            c.join();

            progress.start_task(task);
            progress.update(task, advance=10100)


# Generates treasure heights for the given siteArea, over a range of elongation ratios.
# Heights are generated for both horizontally and vertically elongated treasure (starting with vertical).
# The maximum elongation ratio is ratioEnd.
# While the log of the ratio is less than one, the log is incremented by lowRatioInterval.
# After that it is incremented by highRatioInterval.
def generateHeightsIntervals(siteArea:int, ratioEnd=40, lowRatioInterval = 0.1, highRatioInterval = 0.2) -> list:
    heights = [];
    smallHeights = [];
    end = math.log(ratioEnd, 10);
    logratio = 0;
    while logratio < end:
        ratioToOne = 10**logratio;
        heights.append(math.sqrt(ratioToOne * siteArea));
        if logratio < 1:
            logratio += lowRatioInterval;
        else:
            logratio += highRatioInterval;
    ratioToOne = ratioEnd;
    heights.append(math.sqrt(ratioToOne * siteArea));
    heights.reverse();
    for m in range(len(heights) - 2, -1, -1):
        smallHeights.append(siteArea/heights[m]);
    allHeights = heights + smallHeights;
    return allHeights


# GO DATA FUNCTIONS
# These functions perform all experiments for the various analyses used in the paper.
# The corresponding generate...Data() functions are called.
# Some take a long time, so if running all these functions leave it running overnight.
# It takes around 40 hours to run all of these on a fast computer.
# It could take days on an older or slower computer.

# this takes 22 hours on a fast computer
def goSummaryData():
    print("GENERATING SUMMARY DATA");
    current_datetime = datetime.now();
    print(current_datetime);
    
    for fieldSize in [100]:
        for siteArea in [20, 100, 200]:
            generateSummaryData(fieldSize, siteArea, generateHeightsIntervals(siteArea, 40, 0.1, 0.15));
            current_datetime = datetime.now();
            print(current_datetime);
    for fieldSize in [150, 200]:
        for siteArea in [100]:
            generateSummaryData(fieldSize, siteArea, generateHeightsIntervals(siteArea, 40, 0.1, 0.15));
            current_datetime = datetime.now();
            print(current_datetime);

# this takes 15 hours on a fast computer
def goLargeRatioData():
    print("GENERATING LARGE RATIO DATA");
    current_datetime = datetime.now();
    print(current_datetime);
    generateLargeRatioData(100, 20, generateHeightsIntervals(20, 500, 0.1, 0.2));
    current_datetime = datetime.now();
    print(current_datetime);

# this takes 55 minutes on a fast computer
# this was not used in the paper and still needs testing
def goSpecificNumberOfHolesData():
    print("GENERATING SPECIFIC NUMBER OF HOLES DATA");
    current_datetime = datetime.now();
    print(current_datetime);
    for fieldSize in [100]:
        for siteArea in [20, 100, 200]:
            for holes in [25, 48, 99]:
                generateSpecificNumberOfHolesData(fieldSize, siteArea, generateHeightsIntervals(siteArea, 40, 0.1, 0.15), holes, specificHolesDirectory);
                current_datetime = datetime.now();
                print(current_datetime);

# this takes 30 minutes on a fast computer.
# Also known as "drilldown" experiments.
def goSpecificRatioData():
    print("GENERATING SPECIFIC RATIO DATA");
    current_datetime = datetime.now();
    print(current_datetime);
    generateSpecificRatioData(100);
    current_datetime = datetime.now();
    print(current_datetime);

# this takes 40 minutes on a fast computer
def goRealWorldData():
    print("GENERATING REAL WORLD DATA");
    current_datetime = datetime.now();
    print(current_datetime);
    generatePolygonData(100, "Woorong Park Residual Rise 1.zip", rotate=False);
    current_datetime = datetime.now();
    print(current_datetime);
    generatePolygonData(100, "Woorong Park Residual Rise 1.zip", rotate=True);
    current_datetime = datetime.now();
    print(current_datetime);


# GO GRAPH FUNCTIONS
# These functions generate graphs for the various analyses used in the paper.
# The corresponding generate...() functions for graphs and tables are called.

def goSpecificRatioGraphs():
    print("generating specific ratio graphs...");
    generateSpecificRatioGraphs(100);

def goSummaryGraphs():
    print("generating summary graphs...");
    for fieldSize in [100]:
        for siteArea in [20, 100, 200]:
            if siteArea == 20:
                minY = 93;
            elif siteArea == 100:
                minY = 98.5;
            elif siteArea == 200:
                minY = 99.1;
            generateSummaryGraph(fieldSize, siteArea, generateHeightsIntervals(siteArea, 40, 0.1, 0.15), maximumHoles=6000, minFieldName="random", zoomCentral=True, showGraph=False, minY = minY);
    generateSummaryGraph(fieldSize, 100, generateHeightsIntervals(100, 40, 0.1, 0.15), maximumHoles=6000, minFieldName="random", zoomCentral=False, showGraph=False);
    # generate summary data for other field sizes, used in the crossover analysis. saveGraph is False.
    generateSummaryGraph(100, 100, generateHeightsIntervals(100, 40, 0.1, 0.15), False, True, "random", True, 9000, summaryDirectory, saveGraph = False);
    generateSummaryGraph(150, 100, generateHeightsIntervals(100, 40, 0.1, 0.15), False, True, "random", True, 9000, summaryDirectory, saveGraph = False);
    generateSummaryGraph(200, 100, generateHeightsIntervals(100, 40, 0.1, 0.15), False, True, "random", True, 9000, summaryDirectory, saveGraph = False);

# note: summary graphs must be generated before calling this function
def goCrossoverTables():
    print("generating crossover tables and graphs...");
    generateCrossoverTableAndGraph(100, [20, 100, 200], ["hexlike", "staggerXY", "randomisedStaggerXY8"], True);
    generateCrossoverTableAndGraph(100, [20, 100, 200], ["hexlike", "staggerXY", "randomisedStaggerXY8"], False);

    generateFieldSizeCrossoverTable([100, 150, 200], 100, ["hexlike", "staggerXY", "randomisedStaggerXY8"], True);
    generateFieldSizeCrossoverTable([100, 150, 200], 100, ["hexlike", "staggerXY", "randomisedStaggerXY8"], False);

def goLargeRatioGraphs():
    print("generating large ratio graphs...");
    generateSummaryGraphLargeRatio(100, 20, generateHeightsIntervals(20, 500, 0.1, 0.2), False);

def goSmallNumberOfHolesGraphs():
    print("generating small number of holes graph...");
    for siteArea in [20, 100, 200]:
        minY = None;
        if siteArea == 100:
            minY = 14;
        elif siteArea == 200:
            minY = 26;
        generateSummaryGraph(100, siteArea, generateHeightsIntervals(siteArea, 40, 0.1, 0.15), zoomCentral=True, minFieldName="random", maximumHoles=25, dir = summaryDirectory, outputDir = smallHolesDirectory, compileData=True, showGraph = False, suppressNumHoleWarning=True, minY = minY);

# this is not used in the paper and still needs testing
def goSpecificNumberOfHolesGraphs():
    print("generating specific number of holes graphs,,,");
    for fieldSize in [100]:
        for siteArea in [20, 100, 200]:
            for holes in [25, 48, 99]:
                generateSpecificNumberOfHolesGraph(fieldSize, siteArea, generateHeightsIntervals(siteArea, 40, 0.1, 0.15), holes, specificHolesDirectory);

def goRealWorldGraphs():
    print("generating real world polygon graphs...");
    generatePolygonSuccessGraph(100, zoom=False, rotate=False);
    generatePolygonSuccessGraph(100, zoom=False, rotate=True);
    generatePolygonSuccessGraph(100, zoom=True, rotate=False);
    generatePolygonSuccessGraph(100, zoom=True, rotate=True);

def goCostGraphs():
    print("generating cost graphs...");
    generateCostGraphs(100);

def goSpecificRatioHolesForSuccessRatesTables():
    print("generating specific ratio holes for success rates tables...");
    generateSpecificRatioHolesForSuccessRatesTables(100, 100);

def goRealWorldHolesForSuccessRatesTables():
    print("generating real world holes for success rates tables...");
    generatePolygonHolesForSuccessRatesTables(100, False);
    generatePolygonHolesForSuccessRatesTables(100, True);

def goMaximumDifferenceInSuccessTable():
    print("generating maximum difference in success table...");
    generateMaximumDifferenceInSuccessTable();


if __name__ == '__main__':    
    multiprocessing.set_start_method('spawn');

    # go variables
    # Set these to True to run the experiments in the given category and generate data.
    # Some "go" data functions take a very long time. If setting all to True
    # be prepared to wait around 40 hours on a fast computer.
    # It could take days on an older or slower computer.
    
    # this takes 30 minutes on a fast computer. Also known as "drilldown" experiments:
    goSpecificRatio = False;
    # this takes 22 hours on a fast computer:
    goSummary = False;
    # this takes 15 hours on a fast computer:
    goLargeRatio = False;
    # this takes 40 minutes on a fast computer:
    goRealWorld = False;

    goGraphsAndTables = True;

    goPrintExperiments = False;

    if not(goSpecificRatio or goSummary or goLargeRatio or goRealWorld) and goGraphsAndTables:
        print("USING PRE-GENERATED DATA.");
        print("To generate your own data set the appropriate \"go\" variables to True in LayoutExperiments.py.");
        print("Generating all data may take over 40 hours on a fast computer,")
        print("and could take days on an older or slower computer.");
        print();
        print("Generating graphs and tables will take under a minute on a fast computer.");
        print();
    
    runtime = 0;
    if goSpecificRatio:
        runtime += 30/60;
    if goSummary:
        runtime += 22;
    if goLargeRatio:
        runtime += 15;
    if goRealWorld:
        runtime += 40/60

    if goSpecificRatio or goSummary or goLargeRatio or goRealWorld:
        print("GENERATING DATA");
        print("This will take around " + str(round(runtime, 1)) + " hours on a fast computer");
        print();

    if goSpecificRatio:
        goSpecificRatioData();
    if goSummary:
        goSummaryData();
    if goLargeRatio:
        goLargeRatioData();
    if goRealWorld:
        goRealWorldData();

    if goGraphsAndTables:
        goSpecificRatioGraphs();
        goSummaryGraphs();
        goCrossoverTables();
        goLargeRatioGraphs();
        goSmallNumberOfHolesGraphs();
        goRealWorldGraphs();
        # goCostGraphs();
        goSpecificRatioHolesForSuccessRatesTables();
        goRealWorldHolesForSuccessRatesTables();
        goMaximumDifferenceInSuccessTable();

    if goPrintExperiments:
        print("Printing experiments to the printedFields directory...")
        runElongatedHexLike(100, 10, 10, 100, printExperimentHoles=42);
        runElongatedHalton(100, 10, 10, 100, printExperimentHoles=42);
        runElongatedRandom(100, 10, 10, 100, printExperimentHoles=42);
        runElongatedStaggerXY(100, 10, 10, 100, printExperimentHoles=42);
        runRandomisedStaggerXY(100, 10, 10, 8, 100, printExperimentHoles=42);
        runPolygonHexLike(100, "Woorong Park Residual Rise 1.zip", printExperimentHoles=42);
        runPolygonHexLike(100, "Woorong Park Residual Rise 1.zip", rotate=True, printExperimentHoles=42);
        runPolygonStaggerXY(100, "Woorong Park Residual Rise 1.zip", printExperimentHoles=42);
        runPolygonStaggerXY(100, "Woorong Park Residual Rise 1.zip", rotate=True, printExperimentHoles=42);
        runPolygonRandomisedStaggerXY(100, "Woorong Park Residual Rise 1.zip", 8, printExperimentHoles=42);
        runPolygonRandomisedStaggerXY(100, "Woorong Park Residual Rise 1.zip", 8, rotate=True, printExperimentHoles=42);
        runPolygonHalton(100, "Woorong Park Residual Rise 1.zip", printExperimentHoles=42);
        runPolygonHalton(100, "Woorong Park Residual Rise 1.zip", rotate=True, printExperimentHoles=42);
        runPolygonRandom(100, "Woorong Park Residual Rise 1.zip", printExperimentHoles=42);
        runPolygonRandom(100, "Woorong Park Residual Rise 1.zip", rotate=True, printExperimentHoles=42);

