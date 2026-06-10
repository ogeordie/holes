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
# in ExperimentRunner.py. It also contains code to plot graphs and tables using Plotter.py.
# Tables contain results of data analysis using Tables.py.

# Data produced are stored in subdirectories of the "data" directory and graphs and tables
# are stored in subdirectories of the "graphs" directory.


from ExperimentRunner import ExperimentRunner
from Field import Field
from Players import HexagonalLikePlayer, HaltonPlayer, RandomPlayer, HexagonalPlayer
from Tables import maximumDifferenceInSuccess, breakEvenRatios, areaUnderCurve, crossoverPoint, getMaximumDifferenceInSuccessLayout, getMaximumDifferenceInSuccessLayoutFromFiles
from SizeMattersExperiments import BasicExperiment
from Treasure import TreasureManager, RectangularTreasureManager, PolygonTreasureManager, RandomisedTreasureManager
from Plotter import plotTable, plotSummaryExperiment, plotSummaryCrossoverTable, plotPolygonSuccessExperiment, plotSuccessExperiment, plotHolesForSuccessRatesTable, plotPolygonHolesForSuccessRatesTable, plotCostGraph, plotRotationExperiment, createLegend, plotRandomisedTreasureExperiment
from HolesDictionary import HolesDictionary
from rich.progress import Progress, BarColumn
from pathlib import Path
import math
import multiprocessing
import traceback
from datetime import datetime
import sys
import random


# A base Experiment for Layout Matters experiments
class BasicLayoutExperiment(BasicExperiment):

    def __init__(self, treasureManager:TreasureManager):
        super().__init__(treasureManager);
        self.mNumRepeats = globalNumRepeats;
        self.mSmallNumHolesNumRepeats = globalVeryHighNumRepeats;
        self.mSmallNumHolesNumRepeatsCutoff = 40;


# DEFINE EXPERIMENT SUBCLASSES FOR EACH LAYOUT ALGORITHM

class HexagonalLikeExperiment(BasicLayoutExperiment):
    def __init__(self, treasureManager:TreasureManager):
        super().__init__(treasureManager);

    def getPlayer(self, field:Field, holes:int):
        return HexagonalLikePlayer(field, self.mHoleSize, holes, self.mLRBorder, False);


class StaggerXYExperiment(BasicLayoutExperiment):

    def __init__(self, treasureManager:TreasureManager):
        super().__init__(treasureManager);
    
    def getPlayer(self, field:Field, holes:int):
        return HexagonalLikePlayer(field, self.mHoleSize, holes, self.mLRBorder, True);

class HaltonExperiment(BasicLayoutExperiment):

    def __init__(self, treasureManager:TreasureManager):
        super().__init__(treasureManager);
        self.mSmallNumHolesIncrement = 3;
        self.mSmallNumHolesIncrementCutoff = 30;
        self.mHoleIncrement = 10;

    def getPlayer(self, field:Field, holes:int):
        # set numpy random number generator seed
        seed = random.randint(1, sys.maxsize);
        return HaltonPlayer(field, self.mHoleSize, holes, seed, self.mLRBorder);

class RandomExperiment(BasicLayoutExperiment):

    def __init__(self, treasureManager:TreasureManager):
        super().__init__(treasureManager);
        self.mSmallNumHolesIncrement = 3;
        self.mSmallNumHolesIncrementCutoff = 30;
        self.mHoleIncrement = 10;

    def getPlayer(self, field:Field, holes:int):
        return RandomPlayer(field, self.mHoleSize, holes, self.mLRBorder);

class RandomisedStaggerXYExperiment(BasicLayoutExperiment):

    def __init__(self, treasureManager:TreasureManager, stdDevDivisor:int):
        super().__init__(treasureManager);
        self.stdDeviationDivisor = stdDevDivisor;

    def getPlayer(self, field:Field, holes:int):
        return HexagonalLikePlayer(field, self.mHoleSize, holes, self.mLRBorder, True, True, self.stdDeviationDivisor);


class HexExperiment(BasicLayoutExperiment):
    def __init__(self, treasureManager:TreasureManager):
        super().__init__(treasureManager);

    def getPlayer(self, field:Field, holes:int):
        return HexagonalPlayer(field, self.mHoleSize, holes);


# SET SOME GLOBAL VARIABLES

# default number of simulation interations for each number of holes
globalVeryHighNumRepeats = 15000;
globalHighNumRepeats = 8000;
globalNumRepeats = 4000;

# subdirectories of the data and graphs directories in which to store experiment results
summaryDirectory = HolesDictionary.getSummaryDirectoryName();
successDirectory = HolesDictionary.getSuccessDirectoryName();
caseStudiesDirectory = HolesDictionary.getCaseStudiesDirectoryName();
largeRatioDirectory = HolesDictionary.getLargeRatioDirectoryName();
smallHolesDirectory = HolesDictionary.getSmallNumHolesDirectoryName();
circularDirectory = HolesDictionary.getCircularDirectoryName();
rotationDirectory = HolesDictionary.getRotationDirectoryName();
randomisedTreasureDirectory = HolesDictionary.getRandomisedTreasureDirectoryName();


# FUNCTIONS TO RUN EXPERIMENTS

# Runs an Experiment on an ExperimentRunner.
# Success data are generated for the given experiment parameters (including the
# Player/layout algorithm to use and a TreasureManager which provides the Treasure to use)
# over a range of number of holes.
# See the ExperimentRunner class for more details.
# The field is a square of size fieldSize x fieldSize.
# Optionally, the number of holes at which to start the experiment is startHoles.
# Optionally, the maximum number of holes to use in the experiment is maxHoles.
# Optionally, the exact number of holes to use in the experiment is numHoles (usually an experiment
# will run from 1 hole to the maximum number but experiments could consider only a single number of holes).
# Optionally, the number of simulation iterations to run for each number of holes is numRepeats.
# Optionally the number of simulation iterations to run for small numbers of holes is smallNumHolesNumRepeats.
# Optionally, printExperimentHoles is the number of holes to use when printing the experiment field.
# NOTE that when printExperimentHoles is defined, the experiment will not be run, only printed.
def doRunExperiment(fieldSize:int, experiment:BasicLayoutExperiment, outputFileName:str, startHoles:int = None, maxHoles:int = None, numHoles:int = None, numRepeats:int = globalNumRepeats, smallNumHolesNumRepeats:int = None, printExperimentHoles = None) -> None:
    experiment.mFieldSize = fieldSize;
    experiment.mNumRepeats = numRepeats;
    if maxHoles != None:
        experiment.mMaxHoles = maxHoles;
    if startHoles != None:
        experiment.mStartHoles = startHoles;
    if numHoles != None:
        experiment.mStartHoles = numHoles;
        experiment.mMaxHoles = numHoles;
    if smallNumHolesNumRepeats != None:
        experiment.mSmallNumHolesNumRepeats = smallNumHolesNumRepeats;

    experiment.mOutputFileName = outputFileName;
    runner = ExperimentRunner(experiment);
    if printExperimentHoles != None:
        runner.printExperiment(printExperimentHoles);
    else:
        runner.runExperiment(printData=False);

# Return the csv filename in which to store success data for an experiment using RectangularTreasure.
# The file is called:
# "<longSide>x<shortSide>@<rotation>rectangle <layoutAlgorithm> fieldsize<fieldSize> siteArea<siteArea>.csv"
# in the dir subdirectory of the data directory.
def getRectangularFileName(fieldSize:int, siteArea:int, layoutAlgorithm:str, longSide:float, shortSide:float, rotation:float, dir:str, addToFileName:str = "") -> str:
    tshort = round(shortSide, 2);
    tlong = round(longSide, 2);
    if addToFileName != "":
        addToFileName = " " + addToFileName;
    return dir + "/" + str(tlong) + "x" + str(tshort) + "@" + str(rotation) + "rectangle " + layoutAlgorithm + " fieldsize" + str(fieldSize) + " siteArea" + str(siteArea) + addToFileName +  ".csv";

# Return the csv filename in which to store success data for an experiment using a PolygonTreasure.
# The file is called "casestudypolygon <description>@<rotation> <layoutAlgorithm> fieldsize<fieldSize>.csv"
# in the dir subdirectory of the data directory.
def getPolygonFileName(fieldSize:int, layoutAlgorithm:str, description:str, rotation:float, dir:str):
    return dir + "/casestudypolygon " + description + "@" + str(rotation) + " " + layoutAlgorithm + " fieldsize" + str(fieldSize) + ".csv"

# Return the csv filename in which to store success data for an experiment using a randomised
# RectangularTreasure. The file is called:
# "randomisedtreasure <layoutAlgorithm> fieldsize<fieldSize>.csv"
# in the dir subdirectory of the data directory.
def getRandomisedTreasureFileName(fieldSize:int, layoutAlgorithm:str, dir:str):
    return dir + "/randomisedtreasure " + layoutAlgorithm + " fieldsize" + str(fieldSize) + ".csv";

# Returns an Experiment for the given layoutAlgorithm and TreasureManager.
def getExperiment(treasureManager:TreasureManager, layoutAlgorithm:str) -> BasicLayoutExperiment:
    if layoutAlgorithm == "hexlike":
        experiment = HexagonalLikeExperiment(treasureManager);
    elif layoutAlgorithm == "staggerXY":
        experiment = StaggerXYExperiment(treasureManager);
    elif layoutAlgorithm == "randomisedStaggerXY sd8":
        experiment = RandomisedStaggerXYExperiment(treasureManager, 8);
    elif layoutAlgorithm == "random":
        experiment = RandomExperiment(treasureManager);
    elif layoutAlgorithm == "halton":
        experiment = HaltonExperiment(treasureManager);
    elif layoutAlgorithm == "hex":
        experiment = HexExperiment(treasureManager);
    else:
        print("unknown layout algorithm:", layoutAlgorithm);
        exit(1);
    return experiment;

# Run an experiment using the given layoutAlgorithm with a RectangularTreasure of the given
# longSide, shortSide, and rotation. Places results in the dir subdirectory of the data
# directory (see getRectangularFileName() above for file name details).
# The number of repeats to use is numRepeats and smallNumHolesNumRepeats for smaller numbers
# of holes. printExperimentHoles is the number of holes to use when printing the experiment field.
# NOTE that when printExperimentHoles is defined, the experiment will not be run, only printed.
def runRectangularExperiment(layoutAlgorithm:str, longSide:float, shortSide:float, rotation:float, fieldSize:int, siteArea:int, dir:str, numRepeats = globalNumRepeats, smallNumHolesNumRepeats = None, printExperimentHoles = None):
    treasureManager = RectangularTreasureManager(longSide, shortSide, rotation);
    fileName = getRectangularFileName(fieldSize, siteArea, layoutAlgorithm, longSide, shortSide, rotation, dir);
    experiment = getExperiment(treasureManager, layoutAlgorithm);
    if smallNumHolesNumRepeats != None:
        experiment.mSmallNumHolesNumRepeats = smallNumHolesNumRepeats;
    doRunExperiment(fieldSize, experiment, fileName, numRepeats = numRepeats, printExperimentHoles = printExperimentHoles);

# Run an experiment using the given layoutAlgorithm with a PolygonTreasure with the given polygonFile
# defining the polygon shape (in shapefile format), description, and rotation. The polygon in the
# shapefile is assumed to be oriented vertically. Place results in the
# dir subdirectory of the data directory. The number of repeats to use is numRepeats.
# printExperimentHoles is the number of holes to use when printing the experiment field.
# NOTE that when printExperimentHoles is defined, the experiment will not be run, only printed.
def runPolygonExperiment(layoutAlgorithm:str, polygonFile:str, description:str, rotation:float, fieldSize:int, dir:str, numRepeats = globalNumRepeats, printExperimentHoles = None):
    treasureManager = PolygonTreasureManager(polygonFile, rotation);
    fileName = getPolygonFileName(fieldSize, layoutAlgorithm, description, rotation, dir);
    experiment = getExperiment(treasureManager, layoutAlgorithm);
    doRunExperiment(fieldSize, experiment, fileName, numRepeats = numRepeats, printExperimentHoles = printExperimentHoles);

# Run an experiment using the given layoutAlgorithm with a randomised RectangularTreasure.
# The treasure is randomised by the RandomisedTreasureManager. Place results in the dir
# subdirectory of the data directory. printExperimentHoles is the number of holes to use when printing
# the experiment field.
# # NOTE that when printExperimentHoles is defined, the experiment will not be run, only printed.
def runRandomisedTreasureExperiment(layoutAlgorithm:str, fieldSize:int, dir:str, printExperimentHoles = None):
    treasureManager = RandomisedTreasureManager();
    fileName = getRandomisedTreasureFileName(fieldSize, layoutAlgorithm, dir);
    experiment = getExperiment(treasureManager, layoutAlgorithm);
    if layoutAlgorithm == "halton" or layoutAlgorithm == "random" or layoutAlgorithm == "randomisedStaggerXY sd8":
        experiment.mStopAtSuccess = 99;
    doRunExperiment(fieldSize, experiment, fileName, numRepeats = 60000, smallNumHolesNumRepeats = 60000, printExperimentHoles = printExperimentHoles);


# FUNCTIONS TO GENERATE GRAPHS AND TABLES

# Generates A summary graph of the overall success (over all number of holes)
# of various layout algorithms versus log of the treasure elongation ratio.
# The graph is for a treasure orientation of rotation degrees.
# Assumes all the raw success data is in the dir subdirectory of the data directory
# (defaults to summaryDirectory - see global variables above). For example the user
# should call the function generateSummaryData() before calling this function.
# The raw success data is then analysed by this function, computing the "area under the curve"
# of the success curves specified by each success experiment. Such a computation is done
# for each layout algorithm for each treasure dimension.
# The results of this analysis is stored in a csv file whose name is:
# "summary orientation<rotation> fieldsize<fieldSize> siteArea<siteArea> maxholes<maximumHoles>.csv".
# in the outputDir subdirectory of the data directory.
# The area under the curve is approximated by summing the success rates for each number
# of holes, from 1 to maximumHoles (for cases where success data reaches 100% before
# maximumHoles, 100% success rate is used for the remaining number of holes).
# maximumHoles should be larger than any algorithm takes to reach 100%.
# Where data aren't available for each number of holes, values are interpolated.
# The graph will be shown in a window if showGraph is True, otherwise just saved.
# The graph will zoom the y axis so that the mininum y value relates to the minimum value of the
# minFieldName algorithm if zoomCentral is True.
# If minY is set, that will be the minimum value on the y axis (and minFieldName is ignored).
# Data will not be re-analysed if compileData is False (rather a stored version
# of the "summary" data file will be used, which must exist).
# If suppressNumHoleWarning is True, a warning is printed if we encounter numbers of holes
# greater than maximumHoles in the data, otherwise no warning is produced.
# If saveGraph is False, no graph will be produced, only the summary data files mentioned
# above.
def generateSummaryGraph(fieldSize:int, siteArea:int, shortSides:list, rotation:float, showGraph:bool = True, zoomCentral:bool = False, minFieldName:str = "random", compileData:bool = True, maximumHoles=14000, dir:str = summaryDirectory, outputDir:str = summaryDirectory, suppressNumHoleWarning:bool = False, saveGraph = True, minY = None, maxY = None):
    fileStem = "summary orientation" + str(rotation) + " fieldsize" + str(fieldSize) + " siteArea" + str(siteArea) + " maxholes" + str(maximumHoles);

    if (compileData):
        fileName = "data/" + outputDir + "/" + fileStem + ".csv";
        outputFile = Path(fileName);
        outputFile.parent.mkdir(exist_ok=True, parents=True);
        f = open(fileName, "w");
        f.write("ratio, hexlike, staggerXY, randomisedStaggerXY8, halton, random\n");

        for s in shortSides:
            longSide = siteArea/s;
            shortSide = s;
            roundedShortSide = round(s, 2);
            roundedLongSide = round(longSide, 2);

            fileStart = dir + "/" + str(roundedLongSide) + "x" + str(roundedShortSide) + "@" + str(rotation) + "rectangle";
            fileEnd = "fieldsize" + str(fieldSize) + " siteArea" + str(siteArea) + ".csv";

            successHexLike = areaUnderCurve(fileStart + " hexlike " + fileEnd, maximumHoles, suppressWarning =suppressNumHoleWarning)/maximumHoles;
            successStaggerXY = areaUnderCurve(fileStart + " staggerXY " + fileEnd, maximumHoles, suppressWarning =suppressNumHoleWarning)/maximumHoles;
            successHalton = areaUnderCurve(fileStart + " halton " + fileEnd, maximumHoles, suppressWarning =suppressNumHoleWarning)/maximumHoles;
            successRandom = areaUnderCurve(fileStart + " random " + fileEnd, maximumHoles, suppressWarning =suppressNumHoleWarning)/maximumHoles;
            successRandomisedStaggerXY8 = areaUnderCurve(fileStart + " randomisedStaggerXY sd8 " + fileEnd, maximumHoles, suppressWarning =suppressNumHoleWarning)/maximumHoles;

            ratio = longSide / shortSide;
            f.write(str(ratio) + ", " + str(successHexLike) + ", " +  str(successStaggerXY) + ", " + str(successRandomisedStaggerXY8) + ", " + str(successHalton) + ", " + str(successRandom) + "\n");

        f.flush();
    
    if saveGraph:
        graphFileName = fileStem;
        if zoomCentral:
            graphFileName = graphFileName + " central";
            minX = None;
            maxX = None;
            plotSummaryExperiment(fileStem, siteArea, rotation, fieldSize, graphFileName, minFieldName=minFieldName, maxHoles = maximumHoles, dir = outputDir, outputDir = outputDir, minX = minX, maxX = maxX, zoom=True, showGraph = showGraph, minY = minY, maxY = maxY);
        else:
            plotSummaryExperiment(fileStem, siteArea, rotation, fieldSize, graphFileName, minFieldName=minFieldName, maxHoles = maximumHoles, dir = outputDir, outputDir = outputDir, showGraph = showGraph, minY = minY, maxY = maxY);


# Generates a graph of overall success of the algorithms for a given treasure elongation ratio
# against orientation of the treasure (from -90 to 90 degrees). Areas under the curve of raw success
# data are calculated as for generateSummaryGraph() as a measure of overall performance of the algorithms,
# and stored in a file named "rotation ratio<ratio> fieldsize<fieldSize> siteArea<siteArea> maxholes<maximumHoles>"
# in the rotationDirectory subdirectory of the data directory. Raw success data must exist in that same directory,
# for example call generateRotationData() before calling this function.
def generateRotationGraph(fieldSize:int, siteArea:float, ratio:float, maximumHoles:int):
    fileStem = "rotation ratio" + str(ratio) + " fieldsize" + str(fieldSize) + " siteArea" + str(siteArea) + " maxholes" + str(maximumHoles);
    fileName = "data/" + rotationDirectory + "/" + fileStem + ".csv";
    outputFile = Path(fileName);
    outputFile.parent.mkdir(exist_ok=True, parents=True);
    f = open(fileName, "w");

    f.write("orientation, hexlike, staggerXY, randomisedStaggerXY8, halton, random\n");

    angles = [i * 7.5 for i in range(-12, 13)];
    for angle in angles:
        angle = round(angle, 1);
        shortSide = math.sqrt(siteArea / ratio);
        longSide = siteArea/shortSide;
        shortSide = round(shortSide, 2);
        longSide = round(longSide, 2);
        fileStart = rotationDirectory + "/" + str(longSide) + "x" + str(shortSide) + "@" + str(angle) + "rectangle";
        fileEnd = "fieldsize" + str(fieldSize) + " siteArea" + str(siteArea) +  ".csv";

        successHexLike = areaUnderCurve(fileStart + " hexlike " + fileEnd, maximumHoles)/maximumHoles;
        successStaggerXY = areaUnderCurve(fileStart + " staggerXY " + fileEnd, maximumHoles)/maximumHoles;
        successHalton = areaUnderCurve(fileStart + " halton " + fileEnd, maximumHoles)/maximumHoles;
        successRandom = areaUnderCurve(fileStart + " random " + fileEnd, maximumHoles)/maximumHoles;
        successRandomisedStaggerXY8 = areaUnderCurve(fileStart + " randomisedStaggerXY sd8 " + fileEnd, maximumHoles)/maximumHoles;

        f.write(str(angle) + ", " + str(successHexLike) + ", " +  str(successStaggerXY) + ", " + str(successRandomisedStaggerXY8) + ", " + str(successHalton) + ", " + str(successRandom) + "\n");

    f.flush();
    plotRotationExperiment(fileStem, fieldSize, siteArea, ratio, ["hexlike", "staggerXY", "randomisedStaggerXY8", "halton", "random"], maximumHoles);


# Generates success graph of randomised treasure experiments, zoomed in to various parts of the curves.
# Data are assumed to be in the randomisedTreasureDirectory subdirectory of the data directory.
# For example call generateRandomisedTreasureData() before calling this function.
def generateRandomisedTreasureGraphs(fieldSize:int):
    plotRandomisedTreasureExperiment(fieldSize, ["hexlike", "staggerXY", "randomisedStaggerXY sd8", "halton", "random"], maxX = 1200);
    plotRandomisedTreasureExperiment(fieldSize, ["hexlike", "staggerXY", "randomisedStaggerXY sd8", "halton", "random"], maxX = 25, addToFile = "25");
    plotRandomisedTreasureExperiment(fieldSize, ["hexlike", "staggerXY", "randomisedStaggerXY sd8", "halton", "random"], minX = 80, maxX = 200, addToFile = "200");
    plotRandomisedTreasureExperiment(fieldSize, ["hexlike", "staggerXY", "randomisedStaggerXY sd8", "halton", "random"], minX = 200, maxX = 400, addToFile = "400");
    plotRandomisedTreasureExperiment(fieldSize, ["hexlike", "staggerXY", "randomisedStaggerXY sd8", "halton", "random"], minX = 400, maxX = 800, addToFile = "800");
    plotRandomisedTreasureExperiment(fieldSize, ["hexlike", "staggerXY", "randomisedStaggerXY sd8", "halton", "random"], minX = 800, maxX = 1200, addToFile = "1200");


# Generates a success graph of data from simulations using the case study polygon treasure
# for the various layout algorithms, for the rotation orientation.
# desription describes the polygon shape we are using.
# Raw data in the caseStudiesDirectory subdirectory of the data directory (see global variables
# above) must exist, for example the user should call generatePolygonData() before
# calling this function.
# A graph is shown in a window if showGraph is True.
# If zoom is True the graph will zoom in to the first 80 holes.
def generatePolygonSuccessGraph(fieldSize:int, description:str, rotation:float, zoom:bool = False, showGraph:bool = False):
    zoomString = "";
    maxX = 350;
    maxY = 100;
    if zoom:
        maxY = 50;
        maxX = 40
        zoomString = "zoom ";
    filename = caseStudiesDirectory + "/casestudypolygon " + description + "@" + str(rotation) + " " + zoomString + "fieldsize" + str(fieldSize) + ".png"
    plotPolygonSuccessExperiment(fieldSize, description, filename, maxX, maxY, rotation);


# This is not used in the article.
# It may not work as is, but is included in case we need to modify it to work in the future.
# 
# Generates a summary graph of success of various layout algorithms versus log of the elongation
# ratio, including data for very elongated treasure dimensions.
# Raw data on success of each algorithm at treasure short side in shortSides must exist in the
# largeRatioDirectory subdirectory of the data directory.
# For example the user should call generateLargeRatioData() before calling this function.
# This function compiles that data, writing the "area under the curve" of the success curves for each
# algorithm for each treasure dimensions to a file in the largeRatioDirectory named:
# "summary large ratio fieldsize<fieldSize> siteArea<siteArea>.csv".
# If showGraph is True a graph will be displayed in a window, otherwise just saved.
# If addToFileName is set, its value will be added to the summary file produced.
def generateSummaryGraphLargeRatio(fieldSize:int, siteArea:int, shortSides:list, showGraph:bool = False, addToFileName:str = "") -> None:
    maxHoles = 14000;
    if addToFileName != "":
        addToFileName = " " + addToFileName;
    fileStem = "summary large ratio fieldsize" + str(fieldSize) + " siteArea" + str(siteArea) + addToFileName
    fileName = "data/" + largeRatioDirectory + "/" + fileStem + ".csv";
    f = open(fileName, "w");
    f.write("ratio, randomisedStaggerXY, halton, random\n");
    rotation = 90;

    for s in shortSides:
        shortSide = s;
        longSide = siteArea / s;
        fileStart = largeRatioDirectory + "/" + str(round(longSide, 2)) + "x" + str(round(shortSide, 2)) + "@" + str(rotation) + "rectangle";
        fileEnd = "fieldsize" + str(fieldSize) + " siteArea" + str(siteArea) + ".csv";
        successHalton = areaUnderCurve(fileStart + " halton " + fileEnd, maximumHoles=maxHoles)/maxHoles;
        successRandom = areaUnderCurve(fileStart + " random " + fileEnd, maximumHoles=maxHoles)/maxHoles;
        successRandomisedStaggerXY8 = areaUnderCurve(fileStart + " randomisedStaggerXY sd8 " + fileEnd, maximumHoles=maxHoles)/maxHoles;

        ratio = longSide / shortSide;

        f.write(str(ratio) + ", " + str(successRandomisedStaggerXY8) + ", " +  str(successHalton) +", " + str(successRandom) + "\n");
    f.flush();
    plotSummaryExperiment(fileStem, siteArea, rotation, fieldSize, fileStem, fieldNames=["randomisedStaggerXY", "halton", "random"], maxHoles = maxHoles, dir=largeRatioDirectory, showGraph = showGraph);


# Generates a table of the "crossover points" (elongation ratios) of the success of each layout
# algorithm in layoutAlgorithms and the halton layout algorithm, using the summary data.
# That data must exist, for example call generateSummaryGraph() before calling this function.
# There is a row for vertically and for horizontally elongated sites.
# It assumes that the algorithms start out performing better than the halton layout for
# elongation ratio of 1, and then "cross over" the halton performance to perform worse only
# once as elongation ratio increases. This turns out to be true for vertical and horizontal
# elongation.
def generateCrossoverTable(fieldSize:int, siteArea:float, layoutAlgorithms:list) -> None:
    fileStem = summaryDirectory + "/" "crossover fieldsize" + str(fieldSize) + " siteArea" + str(siteArea);
    fileName = "data/" + fileStem + ".csv";
    f = open(fileName, "w");

    # write headers
    f.write("rotation, ");
    for i in range(len(layoutAlgorithms)):
        f.write(layoutAlgorithms[i]);
        if i != len(layoutAlgorithms) - 1:
                f.write(", ");
    f.write("\n");

    # write data
    for rotation in [0, 90]:
        f.write(str(rotation) + ", ");
        for i in range(len(layoutAlgorithms)):
            dataFileName = "summary orientation" + str(rotation) + " fieldsize" + str(fieldSize) + " siteArea" + str(siteArea) + " maxholes" + str(2250) + ".csv";
            crossover = crossoverPoint(dataFileName, layoutAlgorithms[i]);
            f.write(str(crossover));
            if i != len(layoutAlgorithms) - 1:
                f.write(", ");
        f.write("\n");
    f.flush();

    plotSummaryCrossoverTable(fileStem, layoutAlgorithms, 100, 7, 2.8, 0.2, False);


# Generates several graphs of success of various layout algorithms. A graph is generated for each of
# a small number of treasure elongation ratios, for several orientations. Site area is fixed at 100.
# Raw success data for these must exist in the successDirectory subdirectory of the data
# directory. For example the user should call generateSuccessData() before calling this function.
def generateSuccessGraphs(fieldSize:int):

    for rotation in [0, 30, 60, 90]:
        for ratio in [1, 5, 20]:
            if rotation == 90 and ratio == 1:
                # we don't need vertical and horizontal for a square treasure
                continue;
            for siteArea in [100]:
                shortSide = math.sqrt(siteArea / ratio);
                longSide = siteArea/shortSide;
                shortSide = round(shortSide, 2);
                longSide = round(longSide, 2);

                # set the maximum x value for each graph
                maxX = -1;
                # we currently only consider siteArea of 100 but that may change in the future
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
                
                plotSuccessExperiment(fieldSize, shortSide, longSide, rotation, siteArea, ["hexlike", "staggerXY", "randomisedStaggerXY sd8", "halton", "random"], maxX = maxX);

                if siteArea == 100:
                    # plot a graph zoomed in to a small number of holes when siteArea is 100.
                    plotSuccessExperiment(fieldSize, shortSide, longSide, rotation, siteArea, ["hexlike", "staggerXY", "randomisedStaggerXY sd8", "halton", "random"], maxX = 30, maxY = 40);


# This is not used in the paper and may not work as is. It is included in case
# we need to modify it to work in the future.
#
# Generates graphs showing the number of additional holes that must be dug
# to increase the success rate by 1 percentage point, over a range of
# success rates (from 1 to 100).
# Graphs are generated for a number of elongation ratios (with both horizontal and
# vertical orientation), for a site area of 100.
# Graphs will be saved in the "success" subdirectory of the graphs directory.
# This was not used in the paper, but may be used in future.
def generateCostGraphs(fieldSize:int):
    for rotation in [0, 90]:
        for ratio in [1, 5, 20]:
            if rotation == 90 and ratio == 1:
                continue;
            for siteArea in [100]:
                shortSide = math.sqrt(siteArea / ratio);
                longSide = siteArea/shortSide
                plotCostGraph(fieldSize, shortSide, longSide, rotation, siteArea, "halton", maxY = 50);
                plotCostGraph(fieldSize, shortSide, longSide, rotation, siteArea, "randomisedStaggerXY sd8", maxY = 50);


# Generates a table showing the number of holes needed to achieve success rates
# of 85%, 90%, and 100% using data from the success experiments for the layout
# algorithms used in those experiments. Data are included for horizontal and
# vertical treasure orientations and several elongation ratios.
# Assumes that data are in the success subdirectory of the data directory.
# fieldSize and siteArea are as provided.
# There is a row in the table for each combination of treasure elongation ratio, orientation,
# and layout algorithm.
def generateSuccessHolesForSuccessRatesTables(fieldSize:int, siteArea:int):
    plotHolesForSuccessRatesTable(fieldSize, siteArea, ["hexlike", "staggerXY", "randomisedStaggerXY sd8", "halton", "random"]);


# Generates a table showing the number of holes needed to achieve success rates
# of 85%, 90%, and 100% using data from the case study polygon treasure
# experiments for the layout algorithms used in those experiments. Data 
# for the given treasure rotation are used and are assumed to exist in the
# casestudies subdirectory of the data directory. There is a row in the table
# for each layout algorithm.
def generatePolygonHolesForSuccessRatesTables(fieldSize:int, description:str, rotation:float):
    filename = "graphs/" + caseStudiesDirectory + "/holes for success rates table " + description + " polygon fieldsize" + str(fieldSize) + ".png"
    plotPolygonHolesForSuccessRatesTable(fieldSize, description, ["hexlike", "staggerXY", "randomisedStaggerXY sd8", "halton", "random"], rotation);


# Generates a table showing the maximum difference in success rates across all
# layout algorithms across a range of numbers of holes. This is the biggest difference
# between any two curves of a success graph. This uses the success data in the "success"
# subdirectory of the data directory (which are assumed to exist). The treasure elongation ratios
# and layout algorithms used in those success experiments are considered. Only horizontal
# and vertical orientations are considered.
# There is a column for the maximum difference across all numbers of holes, and another for
# the first 25 holes. There is a row for each combination of treasure elongation ratio
# and orientation.
# Site area and field size are constant (both 100).
def generateMaximumDifferenceInSuccessTable():
    data = [];
    data.append(["Site Orientation\nand Elongation", "Maximum Difference\nfor All Numbers of Pits\n(percentage points)", "Maximum Difference\nfor 1-25 Pits\n(percentage points)"]);

    for ratio in [1, 5, 20]:
        for rotation in [0, 90]:
            if rotation == 90 and ratio == 1:
                continue;
            
            data.append([str(rotation) + " Degrees\n(" + str(ratio) + ":1)"]);

            fieldSize = 100;
            siteArea = 100;
            layoutAlgorithms = ["hexlike", "staggerXY", "randomisedStaggerXY sd8", "halton", "random"];

            max = 0;
            max25 = 0;

            shortSide = math.sqrt(siteArea / ratio);
            longSide = siteArea/shortSide;

            for la1 in range(len(layoutAlgorithms)):
                for la2 in range(len(layoutAlgorithms)):
                    # we only consider each combination of layout algorithms once
                    if la2 < la1:
                        maxDiff = getMaximumDifferenceInSuccessLayout(fieldSize, siteArea, layoutAlgorithms[la1], layoutAlgorithms[la2], shortSide, longSide, rotation);
                        if maxDiff > max:
                            max = maxDiff;
                        maxDiff25 = getMaximumDifferenceInSuccessLayout(fieldSize, siteArea, layoutAlgorithms[la1], layoutAlgorithms[la2], shortSide, longSide, rotation, maxHoles=25);
                        if maxDiff25 > max25:
                            max25 = maxDiff25;
            data[len(data) - 1].append(round(max, 2));
            data[len(data) - 1].append(round(max25, 2));

    plotTable(data, 6, 5, 2, 3.2, successDirectory + "/maximum differences in success siteArea 100.png", cellHeight=0.04, title="Maximum Difference in Success Rates\nAcross All Layout Algorithms\nFor Any Given Number of Pits\nField Size 100m x 100m, Site Area 100m\u00b2");


# As for generateMaximumDifferenceInSuccessTable() but for randomised treasure experiments.
# Data are assumed to exist in the randomisedTreasureDirectory subdirectory of the data
# directory.
def printMaximumDifferenceInSucessForRandomTreasure(fieldSize:int):
    layoutAlgorithms = ["hexlike", "staggerXY", "randomisedStaggerXY sd8", "halton", "random"];
    max = 0;
    max25 = 0;
    maxHoles = 1000;
    for la1 in range(len(layoutAlgorithms)):
        for la2 in range(len(layoutAlgorithms)):
            # we only consider each combination of layout algorithms once
            if la2 < la1:
                file1 = "data/" + randomisedTreasureDirectory + "/randomisedtreasure " + layoutAlgorithms[la1] + " fieldsize" + str(fieldSize) + ".csv";
                file2 = "data/" + randomisedTreasureDirectory + "/randomisedtreasure " + layoutAlgorithms[la2] + " fieldsize" + str(fieldSize) + ".csv";
                maxDiff = getMaximumDifferenceInSuccessLayoutFromFiles(file1, file2, maxHoles = maxHoles);
                if maxDiff > max:
                    max = maxDiff;
                maxDiff25 = getMaximumDifferenceInSuccessLayoutFromFiles(file1, file2, maxHoles=25);
                if maxDiff25 > max25:
                    max25 = maxDiff25;
    print("randomised treasure field size " + str(fieldSize) + " maximum difference over 1 to " + str(maxHoles) + " pits", max);
    print("randomised treasure field size " + str(fieldSize) + " maximum difference over 1 to 25 pits", max25);


# A class that runs a function in a new process. Multiprocessing is
# used to decrease the running times of the experiments.
# Call start() to call the function with the given arguments,
# and join() to wait for it to complete.
class MyProcess(multiprocessing.Process):

    # function is the function to run, with the given arguments.
    # seed is the random seed to set for python random number generator,
    # which needs to be set in each new process to allow reproducibility.
    # Best practice is for seed to be different each time this is created.
    def __init__(self, seed:int, function, *args, **kwargs):
        super().__init__();
        self.seed = seed;
        self.function = function;
        self.args = args;
        self.kwargs = kwargs;
    
    # run the function. However start() should be called, which in turn
    # causes this to run.
    def run(self):
        try:
            random.seed(self.seed);
            self.function(*self.args, **self.kwargs);
        except Exception as e:
            print("exception: ", e);
            traceback.print_exc();
            exit(1);


# Runs experiments to generate raw success data for various layout algorithms, for the given
# fieldSize and siteArea, and the rectangular treasures whose short side are in shortSides.
# These data are used in the summary analyses, where each point in a summary graph
# is a "summary" of success data for one layout algorithm (given a siteArea, fieldSize,
# treasure elongation ratio, and orientation), being the area under the curve of that success experiment
# (approximated by summing the success rates over all numbers of holes from 1 to a number
# greater than the maximum number any algorithm needs to reach 100% success rate).
# These data are also used in the low intensity summary analysis (small number of holes).
# Data is stored in the dir subdirectory of the data directory, in the filenames specified
# in the comments for the get...FileName() functions (above).
# After calling this function, the data can be graphed using generateSummaryGraph().
# seed is the random number generator seed to begin with.
def generateSummaryData(fieldSize:int, siteArea:int, shortSides:list, rotation:float, seed:int, dir:str = summaryDirectory) -> None:
    progress_columns = (
        "[progress.description]{task.description}",
        BarColumn());

    for s in shortSides:
        longSide = siteArea/s;
        with Progress(*progress_columns) as progress2:
            task = progress2.add_task("generating short side = " + str(round(s, 2)) + " rotation = "  + str(rotation) + " site area = " + str(siteArea) + " field size = " + str(fieldSize), total=10100, start=False);
            seed += 1;
            a = MyProcess(seed, runRectangularExperiment, "halton", longSide, s, rotation, fieldSize, siteArea, dir);
            a.start();
            seed += 1;
            b = MyProcess(seed, runRectangularExperiment, "random", longSide, s, rotation, fieldSize, siteArea, dir);
            b.start();
            seed += 1;
            c = MyProcess(seed, runRectangularExperiment, "hexlike", longSide, s, rotation, fieldSize, siteArea, dir);
            c.start();
            seed += 1;
            d = MyProcess(seed, runRectangularExperiment, "staggerXY", longSide, s, rotation, fieldSize, siteArea, dir);
            d.start();
            seed += 1;
            e = MyProcess(seed, runRectangularExperiment, "randomisedStaggerXY sd8", longSide, s, rotation, fieldSize, siteArea, dir);
            e.start();

            a.join();
            b.join();
            c.join();
            d.join();
            e.join();

            progress2.start_task(task);
            progress2.update(task, advance=10100)


# Generates success data for various layout algorithms using a small number of treasure
# elongation ratios for a number of orientations. Site area is 100.
# These data are used in the success analysis, and graphs can be produced by
# calling generateSuccessGraphs().
# Data are stored in the successDirectory subdirectory of the data directory,
# in the filenames specified in the comments for the get...FileName() functions.
# seed is the random number generator seed to begin with.
def generateSuccessData(fieldSize:int, seed:int):
    progress_columns = (
    "[progress.description]{task.description}",
    BarColumn());

    for rotation in [0, 30, 60, 90]:
        for ratio in [1, 5, 20]:
            if rotation - 90 >= 0 and ratio == 1:
                # do not need more rotations of a (rotated) square site
                continue;
            for siteArea in [100]:
                shortSide = math.sqrt(siteArea / ratio);
                longSide = siteArea/shortSide;
                
                with Progress(*progress_columns) as progress:
                    task = progress.add_task("generating " + str(rotation) + " degree ratio " + str(ratio) + " site area " + str(siteArea) +  " field size = " + str(fieldSize), total=10100, start=False);
                    seed += 1;
                    a = MyProcess(seed, runRectangularExperiment, "random", longSide, shortSide, rotation, fieldSize, siteArea, successDirectory, numRepeats = globalHighNumRepeats);
                    a.start();
                    seed += 1;
                    b = MyProcess(seed, runRectangularExperiment, "halton", longSide, shortSide, rotation, fieldSize, siteArea, successDirectory, numRepeats = globalHighNumRepeats);
                    b.start();
                    seed += 1;
                    c = MyProcess(seed, runRectangularExperiment, "hexlike", longSide, shortSide, rotation, fieldSize, siteArea, successDirectory, numRepeats = globalHighNumRepeats);
                    c.start();
                    seed += 1;
                    d = MyProcess(seed, runRectangularExperiment, "staggerXY", longSide, shortSide, rotation, fieldSize, siteArea, successDirectory, numRepeats = globalHighNumRepeats);
                    d.start();
                    seed += 1;
                    e = MyProcess(seed, runRectangularExperiment, "randomisedStaggerXY sd8", longSide, shortSide, rotation, fieldSize, siteArea, successDirectory, numRepeats = globalHighNumRepeats);
                    e.start();

                    a.join();
                    b.join();
                    c.join();
                    d.join();
                    e.join();
                    
                    progress.start_task(task);
                    progress.update(task, advance=10100)


# Runs success experiments on the case study site shape defined in polygonFile for various layout algorithms.
# The polygon file must be a zip file containing files in the shapefile format.
# See https://en.wikipedia.org/wiki/Shapefile . The files must contain one polygon shape and no other constructs.
# The polygon is assumed to be oriented vertically. It is converted to horizontal and then
# rotated by rotation degrees.
# This is used in the case study analysis, and success graphs can be generated by
# calling generatePolygonSuccessGraph().
# Data is stored in the caseStudiesDirectory subdirectory of the data directory, in the filenames
# specified in the comments for the get...FileName() functions.
# seed is the random number geneator seed to begin with.
def generatePolygonData(fieldSize:int, polygonFile:str, description:str, rotation:float, seed:int):
    progress_columns = (
        "[progress.description]{task.description}",
        BarColumn());

    with Progress(*progress_columns) as progress:
        task = progress.add_task("generating data for " + description + " polygon rotation " + str(rotation), total=10100, start=False);

        seed += 1;
        a = MyProcess(seed, runPolygonExperiment, "random", polygonFile, description, rotation, fieldSize, caseStudiesDirectory, numRepeats = globalHighNumRepeats);
        a.start();
        seed += 1;
        b = MyProcess(seed, runPolygonExperiment, "halton", polygonFile, description, rotation, fieldSize, caseStudiesDirectory, numRepeats = globalHighNumRepeats);
        b.start();
        seed += 1;
        c = MyProcess(seed, runPolygonExperiment, "hexlike", polygonFile, description, rotation, fieldSize, caseStudiesDirectory, numRepeats = globalHighNumRepeats);
        c.start();
        seed += 1;
        d = MyProcess(seed, runPolygonExperiment, "staggerXY", polygonFile, description, rotation, fieldSize, caseStudiesDirectory, numRepeats = globalHighNumRepeats);
        d.start();
        seed += 1;
        e = MyProcess(seed, runPolygonExperiment, "randomisedStaggerXY sd8", polygonFile, description, rotation, fieldSize, caseStudiesDirectory, numRepeats = globalHighNumRepeats);
        e.start();

        a.join();
        b.join();
        c.join();
        d.join();
        e.join();

        progress.start_task(task);
        progress.update(task, advance=10100)


# This is not used but included in case it is needed in future
#
# Runs experiments for various layout algorithms using the given fieldSize and siteArea.
# Experiments are run for each treasure short side in shortSides (the long side is
# determined by the short side and the siteArea). This can include treasure that is very elongated.
# Data is stored in the largeRatioDirectory subdirectory of the data directory,
# in the filenames specified in the comments for the get...FileName() functions.
# The data are used in the summary analysis (similar to generateSummaryData() - 
# see those comments for details).
# seed is the random number generator seed to begin with.
def generateLargeRatioData(fieldSize:int, siteArea:int, shortSides:list, seed:int) -> None:
    progress_columns = (
        "[progress.description]{task.description}",
        BarColumn());
    
    rotation = 0;
    for s in shortSides:
        longSide = siteArea/s;
        with Progress(*progress_columns) as progress:    
            task = progress.add_task("generating short side = " + str(s) + " site area = " + str(siteArea), total=10100, start=False);

            seed += 1;
            a = MyProcess(seed, runRectangularExperiment, "random", longSide, s, rotation, fieldSize, siteArea, largeRatioDirectory, smallNumHolesRepeats = globalNumRepeats);
            a.start();
            seed += 1;
            b = MyProcess(seed, runRectangularExperiment, "halton", longSide, s, rotation, fieldSize, siteArea, largeRatioDirectory, smallNumHolesRepeats = globalNumRepeats);
            b.start();
            seed += 1;
            c = MyProcess(seed, runRectangularExperiment, "randomisedStaggerXY sd8", longSide, s, rotation, fieldSize, siteArea, largeRatioDirectory, smallNumHolesRepeats = globalNumRepeats);
            c.start();

            a.join();
            b.join();
            c.join();

            progress.start_task(task);
            progress.update(task, advance=10100)


# Generate success data to be used in the rotation summary graphs. Treasures are
# rectangles of the given elongationRatio. Success data is generated for orientations
# from -90 degrees to 90 degrees, in steps of 7.5 degrees.
# seed is the random number generator seed to begin with.
def generateRotationData(fieldSize:int, siteArea:int, elongationRatio:float, seed:int):
    progress_columns = (
        "[progress.description]{task.description}",
        BarColumn());
    
    angles = [i * 7.5 for i in range(-12, 13)];
    for angle in angles:
        angle = round(angle, 1);
        with Progress(*progress_columns) as progress:    
            task = progress.add_task("generating ratio = " + str(elongationRatio) + " rotation = " + str(angle) + " site area = " + str(siteArea), total=10100, start=False);

            shortSide = math.sqrt(siteArea / elongationRatio);
            longSide = siteArea/shortSide;

            seed += 1;
            a = MyProcess(seed, runRectangularExperiment, "random", longSide, shortSide, angle, fieldSize, siteArea, rotationDirectory);
            a.start();
            seed += 1;
            b = MyProcess(seed, runRectangularExperiment, "halton", longSide, shortSide, angle, fieldSize, siteArea, rotationDirectory);
            b.start();
            seed += 1;
            c = MyProcess(seed, runRectangularExperiment, "hexlike", longSide, shortSide, angle, fieldSize, siteArea, rotationDirectory);
            c.start();
            seed += 1;
            d = MyProcess(seed, runRectangularExperiment, "staggerXY", longSide, shortSide, angle, fieldSize, siteArea, rotationDirectory);
            d.start();
            seed += 1;
            e = MyProcess(seed, runRectangularExperiment, "randomisedStaggerXY sd8", longSide, shortSide, angle, fieldSize, siteArea, rotationDirectory);
            e.start();

            a.join();
            b.join();
            c.join();
            d.join();
            e.join();
            
            progress.start_task(task);
            progress.update(task, advance=10100)


# Generates data for randomised treasure experiments. Here the treasure is of random
# area, length, and orientation, and is different in each iteration of the experiment.
# Data are stored in the randomisedTreasureDirectory subdirectory of the data directory.
def generateRandomisedTreasureData(fieldSize:int, seed:int):
    progress_columns = (
        "[progress.description]{task.description}",
        BarColumn());

    with Progress(*progress_columns) as progress:

        task = progress.add_task("generating randomised treasure field size = " + str(fieldSize), total=10100, start=False);
        a = MyProcess(seed, runRandomisedTreasureExperiment, "random", fieldSize, randomisedTreasureDirectory);
        a.start();
        seed += 1;
        b = MyProcess(seed, runRandomisedTreasureExperiment, "halton", fieldSize, randomisedTreasureDirectory);
        b.start();
        seed += 1;
        c = MyProcess(seed, runRandomisedTreasureExperiment, "hexlike", fieldSize, randomisedTreasureDirectory);
        c.start();
        seed += 1;
        d = MyProcess(seed, runRandomisedTreasureExperiment, "staggerXY", fieldSize, randomisedTreasureDirectory);
        d.start();
        seed += 1;
        e = MyProcess(seed, runRandomisedTreasureExperiment, "randomisedStaggerXY sd8", fieldSize, randomisedTreasureDirectory);
        e.start();

        a.join();
        b.join();
        c.join();
        d.join();
        e.join();
        
        progress.start_task(task);
        progress.update(task, advance=10100)


# Generates treasure short sides for the given siteArea, over a range of elongation ratios,
# to be used in summary graphs (in which the log of the ratio is the x axis).
# The elongations range from 1 to ratioEnd.
# While the log of the ratio is less than one, the log is incremented by lowRatioInterval.
# After that it is incremented by highRatioInterval.
def generateShortSides(siteArea:int, ratioEnd=40, lowRatioInterval = 0.1, highRatioInterval = 0.2) -> list:
    shortSides = [];
    end = math.log(ratioEnd, 10);
    logratio = 0;
    while logratio < end:
        ratioToOne = 10**logratio;
        shortSides.append(math.sqrt(siteArea/ratioToOne));
        if round(logratio, 2) < 1:
            logratio += lowRatioInterval;
        else:
            logratio += highRatioInterval;
    ratioToOne = ratioEnd;
    shortSides.append(math.sqrt(siteArea/ratioToOne));
    return shortSides;


# GO DATA FUNCTIONS
# These functions perform all experiments for the various analyses used in the paper.
# The corresponding generate...Data() functions are called.
# Some take a long time. It takes over 13.35 hours to run all of these on a fast computer.
# It could take days on an older or slower computer.

# this takes 3.4 hours on a fast computer
def goSummaryData():
    print("GENERATING SUMMARY DATA");
    startDatetime = datetime.now();
    print(startDatetime);
    
    seed = 1;
    for fieldSize in [100]:
        for siteArea in [100]:
            for rotation in [0, 30, 60, 90]:
                seed += 1000;
                generateSummaryData(fieldSize, siteArea, generateShortSides(siteArea, 40, 0.1, 0.15), rotation, seed);
                currentDatetime = datetime.now();
                print(currentDatetime);
        # for siteArea in [20, 200]:
        #     for rotation in [0, 90]:
        #         generateSummaryData(fieldSize, siteArea, generateShortSides(siteArea, 40, 0.1, 0.15), rotation);
        #         currentDatetime = datetime.now();
        #         print(currentDatetime);
    endDatetime = datetime.now();
    print("Summary experiments took", endDatetime - startDatetime);

# this takes 15 hours on a fast computer
# not used in the paper
def goLargeRatioData():
    print("GENERATING LARGE RATIO DATA");
    currentDatetime = datetime.now();
    print(currentDatetime);
    generateLargeRatioData(100, 20, generateShortSides(20, 500, 0.1, 0.2), 100000);
    currentDatetime = datetime.now();
    print(currentDatetime);

# this takes 1 hour on a fast computer.
def goSuccessData():
    print("GENERATING SUCCESS DATA");
    startDatetime = datetime.now();
    print(startDatetime);
    generateSuccessData(100, 200000);
    endDatetime = datetime.now();
    print(endDatetime);
    print("Succes experiments took", endDatetime-startDatetime);


# this takes 2 hours on a fast computer
def goCaseStudiesData():
    print("GENERATING CASE STUDIES DATA");
    startDatetime = datetime.now();
    print(startDatetime);
    seed = 300000;
    for rotation in [0, 30, 60, 90]:
        seed += 1000;
        generatePolygonData(100, "High Elongation Site Form.zip", "highelongation", rotation, seed);
        seed += 1000;
        generatePolygonData(100, "Moderate Elongation Site Form.zip", "moderateelongation", rotation, seed);
        seed += 1000;
        generatePolygonData(100, "Low Elongation Site Form.zip", "lowelongation", rotation, seed);
    endDatetime = datetime.now();
    print(endDatetime);
    print("Case studies experiments took", endDatetime-startDatetime);

# This takes 3.8 hours on a fast computer
def goRotationData():
    print("GENERATING ROTATION DATA");
    startDatetime = datetime.now();
    print(startDatetime);
    seed = 400000;
    generateRotationData(100, 100, 1, seed);
    currentDatetime = datetime.now();
    print(currentDatetime);
    seed += 1000;
    generateRotationData(100, 100, 5, seed);
    currentDatetime = datetime.now();
    print(currentDatetime);
    seed += 1000;
    generateRotationData(100, 100, 20, seed);
    endDatetime = datetime.now();
    print(endDatetime);
    print("Rotation experiments took", endDatetime-startDatetime);

# this takes TODO
def goRandomisedTreasureData():
    print("GENERATING RANDOM TREASURE DATA");
    seed = 500000;
    startDatetime = datetime.now();
    print(startDatetime);
    generateRandomisedTreasureData(100, seed);
    # currentDatetime = datetime.now();
    # print(currentDatetime);
    # seed += 1000;
    # generateRandomisedTreasureData(50, seed);
    # currentDatetime = datetime.now();
    # print(currentDatetime);
    # seed += 1000;
    # generateRandomisedTreasureData(150, seed);
    endDatetime = datetime.now();
    print(endDatetime);
    print("Random treasure experiments took", endDatetime-startDatetime);


# GO GRAPH FUNCTIONS
# These functions generate graphs and tables for the various analyses in the paper.
# The corresponding generate...() functions for graphs and tables are called.

def goSuccessGraphs():
    print("generating success graphs...");
    generateSuccessGraphs(100);

def goSummaryGraphs():
    print("generating summary graphs...");
    maximumHoles = 2250;
    for fieldSize in [100]:
        #for siteArea in [20, 100, 200]:
        for siteArea in [100]:
            for rotation in [0, 30, 60, 90]:
                minY = None;
                maxY = None;
                if rotation == 0 or rotation == 90:
                    minY = 96;
                    maxY = 98.25;
                generateSummaryGraph(fieldSize, siteArea, generateShortSides(siteArea, 40, 0.1, 0.15), rotation, maximumHoles=maximumHoles, minFieldName="random", zoomCentral=True, showGraph=False, minY = minY, maxY = maxY);
    generateSummaryGraph(fieldSize, 100, generateShortSides(100, 40, 0.1, 0.15), 0, maximumHoles=maximumHoles, minFieldName="random", zoomCentral=False, showGraph=False, maxY = 100);

def goRotationGraphs():
    print("generating rotation graphs...");
    for ratio in [1, 5, 20]:
        generateRotationGraph(100, 100, ratio, 1250);

def goRandomisedTreasureGraphs():
    print("generating randomised treasure graphs...");
    generateRandomisedTreasureGraphs(100);

# note: summary graphs must be generated before calling this function
def goCrossoverTable():
    print("generating summary crossover table...");
    generateCrossoverTable(100, 100, ["hexlike", "staggerXY", "randomisedStaggerXY8"]);

def goLargeRatioGraphs():
    print("generating large ratio graphs...");
    generateSummaryGraphLargeRatio(100, 20, generateShortSides(20, 500, 0.1, 0.2), False);

def goSmallNumberOfHolesGraphs():
    print("generating small number of holes graph...");
    for siteArea in [100]:
        for rotation in [0, 30, 60, 90]:
            minY = None;
            if rotation == 0 or rotation == 90:
                if siteArea == 100:
                    minY = 14;
                # currently only siteArea of 100 is used but keep this in case
                elif siteArea == 200:
                    minY = 26;
            if rotation == 30 or rotation == 150:
                if siteArea == 200:
                    minY = 28;
            generateSummaryGraph(100, siteArea, generateShortSides(siteArea, 40, 0.1, 0.15), rotation, zoomCentral=True, minFieldName="random", maximumHoles=25, dir = summaryDirectory, outputDir = smallHolesDirectory, compileData=True, showGraph = False, suppressNumHoleWarning=True, minY = minY);

def goCaseStudiesGraphs():
    print("generating case studies polygon graphs...");
    for rotation in [0, 30, 60, 90]:
        generatePolygonSuccessGraph(100, "highelongation", rotation, zoom=False);
        generatePolygonSuccessGraph(100, "moderateelongation", rotation, zoom=False);
        generatePolygonSuccessGraph(100, "lowelongation", rotation, zoom=False);

        generatePolygonSuccessGraph(100, "highelongation", rotation, zoom=True);
        generatePolygonSuccessGraph(100, "moderateelongation", rotation, zoom=True);
        generatePolygonSuccessGraph(100, "lowelongation", rotation, zoom=True);

def goCostGraphs():
    print("generating cost graphs...");
    generateCostGraphs(100);

def goSuccessHolesForSuccessRatesTables():
    print("generating success holes for success rates tables...");
    generateSuccessHolesForSuccessRatesTables(100, 100);

def goCaseStudyHolesForSuccessRatesTables():
    print("generating case studies holes for success rates tables...");
    for rotation in [0, 90]:
        generatePolygonHolesForSuccessRatesTables(100, "highelongation", rotation);
        generatePolygonHolesForSuccessRatesTables(100, "moderateelongation", rotation);
        generatePolygonHolesForSuccessRatesTables(100, "lowelongation", rotation);

def goMaximumDifferenceInSuccessTable():
    print("generating maximum difference in success table...");
    generateMaximumDifferenceInSuccessTable();


if __name__ == '__main__':    
    multiprocessing.set_start_method('spawn');

    # go variables
    # Set these to True to run the experiments in the given category and generate data.
    # Some "go" data functions take a very long time. If setting all to True
    # be prepared to wait around 13.35 hours on a fast computer.
    # It could take days on an older or slower computer.
    
    # this takes 1 hour on a fast computer.
    goSuccess = False;
    # this takes 3.4 hours on a fast computer:
    goSummary = False;
    # this takes 2 hours on a fast computer:
    goCaseStudies = False;
    # this takes 3.8 hours on a fast computer:
    goRotation = False;
    # this takes 3.15 hours on a fast computer
    goRandomisedTreasure = False;

    goGraphsAndTables = False;

    goPrintExperiments = True;

    if not(goSuccess or goSummary or goCaseStudies or goRotation or goRandomisedTreasure) and goGraphsAndTables:
        print("USING PRE-GENERATED DATA.");
        print("To generate your own data set the appropriate \"go\" variables to True in LayoutExperiments.py.");
        print("Generating all data may take over 13.35 hours on a fast computer,")
        print("and could take days on an older or slower computer.");
        print();
        print("Generating graphs and tables will take under a minute on a fast computer.");
        print();
    
    runtime = 0;
    if goSuccess:
        runtime += 1;
    if goSummary:
        runtime += 3.4;
    if goCaseStudies:
        runtime += 2;
    if goRotation:
        runtime += 3.8;
    if goRandomisedTreasure:
        runtime += 3.15;

    if goSuccess or goSummary or goCaseStudies or goRotation or goRandomisedTreasure:
        print("GENERATING DATA");
        print("This will take around " + str(round(runtime, 1)) + " hours on a fast computer");
        print();

    if goSuccess:
        goSuccessData();
    if goSummary:
        goSummaryData();
    if goCaseStudies:
        goCaseStudiesData();
    if goRotation:
        goRotationData();
    if goRandomisedTreasure:
        goRandomisedTreasureData();

    if goGraphsAndTables:
        createLegend();
        goSuccessGraphs();
        goSummaryGraphs();
        goCrossoverTable();
        goSmallNumberOfHolesGraphs();
        goCaseStudiesGraphs();
        goSuccessHolesForSuccessRatesTables();
        goCaseStudyHolesForSuccessRatesTables();
        goMaximumDifferenceInSuccessTable();
        goRotationGraphs();
        goRandomisedTreasureGraphs();
        printMaximumDifferenceInSucessForRandomTreasure(100);

    if goPrintExperiments:
        print("Printing experiments to the printedFields directory...");

        # the various algorithms at 0 rotation
        runRectangularExperiment("hexlike", 20, 5, 0, 100, 100, "", printExperimentHoles = 42);
        runRectangularExperiment("staggerXY", 20, 5, 0, 100, 100, "", printExperimentHoles = 42);
        runRectangularExperiment("randomisedStaggerXY sd8", 20, 5, 0, 100, 100, "", printExperimentHoles = 42);
        runRectangularExperiment("random", 20, 5, 0, 100, 100, "", printExperimentHoles = 42);
        runRectangularExperiment("halton", 20, 5, 0, 100, 100, "", printExperimentHoles = 42);

        # halton at various rotations
        runRectangularExperiment("halton", 20, 5, 30, 100, 100, "", printExperimentHoles = 42);
        runRectangularExperiment("halton", 20, 5, 60, 100, 100, "", printExperimentHoles = 42);
        runRectangularExperiment("halton", 20, 5, 90, 100, 100, "", printExperimentHoles = 42);

        # case studies at 0 rotation
        runPolygonExperiment("staggerXY", "Low Elongation Site Form.zip", "lowelongation", 0, 100, "", printExperimentHoles = 42);
        runPolygonExperiment("staggerXY", "Moderate Elongation Site Form.zip", "moderateelongation", 0, 100, "", printExperimentHoles = 42);
        runPolygonExperiment("staggerXY", "High Elongation Site Form.zip", "highelongation", 0, 100, "", printExperimentHoles = 42);

        # randomised treasure
        runRandomisedTreasureExperiment("staggerXY", 100, "", printExperimentHoles=42);
