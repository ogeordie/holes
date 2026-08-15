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

# NOTE: THIS FILE IS NOT CURRENTLY SUPPORTED AS A MAIN FILE FOR THE HOLES PROJECT

# This is a main file for the Holes project, used in the Size Matters article.
# It contains code to run Experiments on the ExperimentRunner implemented
# in ExperimentRunner.py. It also contains code to plot graphs and tables using Plotter.py.
# Tables contain results of data analysis using Tables.py.

# Treasure is placed wholly within the Field.

# Data produced is stored in the "data/sizematters" directory and graphs and tables in the 
# "graphs/sizematters" directory

from ExperimentRunner import Experiment, ExperimentRunner
from Field import Field
from Players import HexagonalLikePlayer, Player
from Tables import maximumDifferenceInSuccess, breakEvenRatios
from Treasure import TreasureManager, CircularTreasureManager, RectangularTreasureManager, RealWorldTreasureManager
from HolesDictionary import HolesDictionary
from Plotter import plotExperiment, plotTable
from rich.progress import Progress, BarColumn
import random
from datetime import datetime


# A Basic experiment that sets all the experiment parameters with default values.
# The Player created is a HexagonalLikePlayer.
# For comments on each getter method see the Experiment class in ExperimentRunner.py.
class BasicExperiment(Experiment):
    def __init__(self, treasureManager:TreasureManager):
        self.mFieldSize = 100;
        self.mHoleSize = 0.5;
        self.mHoleIncrement = 1;
        self.mSmallNumHolesIncrement = 1;
        self.mSmallNumHolesIncrementCutoff = 0;
        self.mStartHoles = 1;
        # at this value of mMaxHoles experiments will stop when 100% success rate is reached:
        self.mMaxHoles = 100000;
        self.mNumRepeats = 10000;
        self.mSmallNumHolesNumRepeats = 10000;
        self.mSmallNumHolesNumRepeatsCutoff = 40;
        self.mStopAtSuccess = 100;
        self.mReturnAfterHit = True;
        self.mOutputFileName = sizeMattersDirectory + "/experiment.csv"
        self.mTreasureManager = treasureManager;
    
    # see Experiment class for details
    def getFieldSize(self) -> int:
        return self.mFieldSize;

    # see Experiment class for details
    def  getHoleSize(self) -> float:
        return self.mHoleSize;

    # see Experiment class for details
    def getHoleIncrement(self) -> int:
        return self.mHoleIncrement;

    def getSmallNumHolesIncrement(self) -> int:
        return self.mSmallNumHolesIncrement;
    
    def getSmallNumHolesIncrementCutoff(self) -> int:
        return self.mSmallNumHolesIncrementCutoff;

    def getStartHoles(self) -> int:
        return self.mStartHoles;

    # see Experiment class for details    
    def getMaxHoles(self) -> int:
        return self.mMaxHoles;
    
    # see Experiment class for details
    def getNumRepeats(self) -> int:
        return self.mNumRepeats;

    # see Experiment class for details
    def getSmallNumHolesNumRepeats(self) -> int:
        return self.mSmallNumHolesNumRepeats;

    # see Experiment class for details
    def getSmallNumHolesNumRepeatsCutoff(self) -> int:
        return self.mSmallNumHolesNumRepeatsCutoff;

    # see Experiment class for details
    def getReturnAfterHit(self):
        return self.mReturnAfterHit;

    # see Experiment class for details
    def getStopAtSuccess(self) -> float:
        return self.mStopAtSuccess;

    # see Experiment class for details
    def getOutputFileName(self) -> str:
        return self.mOutputFileName;

    # see Experiment class for details
    def getPrintedFieldFileName(self, holesDug:int) -> str:
        holesDugString = "";
        if holesDug != None:
            holesDugString = " holes " + str(holesDug);
        return self.mTreasureManager.getTreasureDescription() + " " + self.getPlayerName() + holesDugString + " fieldsize " + str(self.mFieldSize) + " holesize " + str(self.mHoleSize);

    # see Experiment class for details
    def getPlayerName(self) -> str:
        return "Hexagonal-like";

    # see Experiment class for details
    def getPlayer(self, field:Field, holes:int) -> Player:
        return HexagonalLikePlayer(field, self.mHoleSize, holes, True, False, TBBorder=True);

    # see Experiment class for details
    def getTreasureManager(self) -> TreasureManager:
        return self.mTreasureManager;


sizeMattersDirectory = HolesDictionary.getSizeMattersDirectoryName();


# Runs experiments with a circular treasure of diameter 7m on a 100m x 100m field,
# first with 0.5m x 0.5m holes, then with 1m x 1m holes
# printExperimentHoles is the number of holes to use when printing the experiment field.
# NOTE that when printExperimentHoles is defined, the experiments will not be run, only printed.
def run7mCircle100mField(printExperimentHoles:int = None):
    treasureManager = CircularTreasureManager(3.5);
    experiment = BasicExperiment(treasureManager);
    experiment.mOutputFileName = sizeMattersDirectory + "/7mCircle 100mField 0.5mPits.csv";
    runner = ExperimentRunner(experiment);
    if printExperimentHoles != None:
        runner.printExperiment(printExperimentHoles);
    else:
        runner.runExperiment(printData=False);

    experiment.mHoleSize = 1;
    experiment.mOutputFileName = sizeMattersDirectory + "/7mCircle 100mField 1mPits.csv"
    runner = ExperimentRunner(experiment);
    #runner.printExperiment(120);
    if printExperimentHoles != None:
        runner.printExperiment(printExperimentHoles);
    else:
        runner.runExperiment(printData=False);

# Runs experiments with a circular treasure of diameter 7m on a 200m x 200m field,
# first with 0.5m x 0.5m holes, then with 1m x 1m holes
# printExperimentHoles is the number of holes to use when printing the experiment field.
# NOTE that when printExperimentHoles is defined, the experiments will not be run, only printed.
def run7mCircle200mField(printExperimentHoles:int = None):
    treasureManager = CircularTreasureManager(3.5);
    experiment = BasicExperiment(treasureManager);
    experiment.mFieldSize = 200;
    experiment.mOutputFileName = sizeMattersDirectory + "/7mCircle 200mField 0.5mPits.csv"
    runner = ExperimentRunner(experiment);
    if printExperimentHoles != None:
        runner.printExperiment(printExperimentHoles);
    else:
        runner.runExperiment(printData=False);

    experiment.mHoleSize = 1;
    experiment.mOutputFileName = sizeMattersDirectory + "/7mCircle 200mField 1mPits.csv"
    runner = ExperimentRunner(experiment);
    if printExperimentHoles != None:
        runner.printExperiment(printExperimentHoles);
    else:
        runner.runExperiment(printData=False);

# Runs experiments with a circular treasure of diameter 28m on a 100m x 100m field,
# first with 0.5m x 0.5m holes, then with 1m x 1m holes
# printExperimentHoles is the number of holes to use when printing the experiment field.
# NOTE that when printExperimentHoles is defined, the experiments will not be run, only printed.
def run28mCircle100mField(printExperimentHoles:int = None):
    treasureManager = CircularTreasureManager(14);
    experiment = BasicExperiment(treasureManager);
    experiment.mOutputFileName = sizeMattersDirectory + "/28mCircle 100mField 0.5mPits.csv";
    runner = ExperimentRunner(experiment);
    if printExperimentHoles != None:
        runner.printExperiment(printExperimentHoles);
    else:
        runner.runExperiment(printData=False);

    experiment.mHoleSize = 1;
    experiment.mOutputFileName = sizeMattersDirectory + "/28mCircle 100mField 1mPits.csv"
    runner = ExperimentRunner(experiment);
    if printExperimentHoles != None:
        runner.printExperiment(printExperimentHoles);
    else:
        runner.runExperiment(printData=False);

# Runs experiments with a circular treasure of diameter 1m on a 100m x 100m field,
# first with 0.5m x 0.5m holes, then with 1m x 1m holes
# printExperimentHoles is the number of holes to use when printing the experiment field.
# NOTE that when printExperimentHoles is defined, the experiments will not be run, only printed.
def run1mCircle100mField(printExperimentHoles:int = None):
    treasureManager = CircularTreasureManager(0.5);
    experiment = BasicExperiment(treasureManager);
    experiment.mOutputFileName = sizeMattersDirectory + "/1mCircle 100mField 0.5mPits.csv";
    runner = ExperimentRunner(experiment);
    if printExperimentHoles != None:
        runner.printExperiment(printExperimentHoles);
    else:
        runner.runExperiment(printData=False);

    experiment.mHoleSize = 1;
    experiment.mOutputFileName = sizeMattersDirectory + "/1mCircle 100mField 1mPits.csv"
    runner = ExperimentRunner(experiment);
    if printExperimentHoles != None:
        runner.printExperiment(printExperimentHoles);
    else:
        runner.runExperiment(printData=False);

# Runs experiments with a rectangular treasure of dimensions 20m x 5m on a 100m x 100m field,
# first with 0.5m x 0.5m holes, then with 1m x 1m holes
# printExperimentHoles is the number of holes to use when printing the experiment field.
# NOTE that when printExperimentHoles is defined, the experiments will not be run, only printed.
def run20x5mRectangle100mField(printExperimentHoles:int = None):
    treasureManager = RectangularTreasureManager(20, 5, 0, True);
    experiment = BasicExperiment(treasureManager);
    experiment.mOutputFileName = sizeMattersDirectory + "/20x5mRectangle 100mField 0.5mPits.csv";
    runner = ExperimentRunner(experiment);
    if printExperimentHoles != None:
        runner.printExperiment(printExperimentHoles);
    else:
        runner.runExperiment(printData=False);

    experiment.mHoleSize = 1;
    experiment.mOutputFileName = sizeMattersDirectory + "/20x5mRectangle 100mField 1mPits.csv"
    runner = ExperimentRunner(experiment);
    if printExperimentHoles != None:
        runner.printExperiment(printExperimentHoles);
    else:
        runner.runExperiment(printData=False);

# Runs experiments with treasure defined by real world data on artefact coordinates
# on a 100m x 100m field, first with 0.5m x 0.5m holes, then with 1m x 1m holes.
# outputFileNameStart should not include a path, e.g. "LowDensity".
# printExperimentHoles is the number of holes to use when printing the experiment field.
# NOTE that when printExperimentHoles is defined, the experiments will not be run, only printed.
def runRealWorldExperiment(realWorldDataFileName:str, ouptutFileNameStart:str, printExperimentHoles:int = None):
    treasureManager = RealWorldTreasureManager(realWorldDataFileName);
    experiment = BasicExperiment(treasureManager);
    experiment.mRealWorldData = True;
    experiment.mRealWorldDataFileName = realWorldDataFileName;
    experiment.mOutputFileName = sizeMattersDirectory + "/" + ouptutFileNameStart + " 100mField 0.5mPits.csv";
    runner = ExperimentRunner(experiment);
    if printExperimentHoles != None:
        runner.printExperiment(printExperimentHoles);
    else:
        runner.runExperiment(printData=False);

    experiment.mHoleSize = 1;
    experiment.mOutputFileName = sizeMattersDirectory + "/" + ouptutFileNameStart + " 100mField 1mPits.csv";
    runner = ExperimentRunner(experiment);
    if printExperimentHoles != None:
        runner.printExperiment(printExperimentHoles);
    else:
        runner.runExperiment(printData=False);


# generate all the data for all experiments, placing them in the data/sizematters directory
# NOTE: this may take over an hour and 45 minutes on a fast computer
def generateData():
    print("GENERATING DATA IN THE data/sizematters DIRECTORY");
    print("This may take over 1 hour and 45 minutes on a fast computer.");

    progress_columns = (
        "[progress.description]{task.description}",
        BarColumn()
    )


    # INTERSECTION EXPERIMENTS:

    with Progress(*progress_columns) as progress:
        task = progress.add_task("generating 7m circle 100m field...", total=10100, start=False);
        run7mCircle100mField();
        progress.start_task(task);
        progress.update(task, advance=10100);
   
    with Progress(*progress_columns) as progress:
        task = progress.add_task("generating 7m circle 200m field...", total=10100, start=False);
        run7mCircle200mField();
        progress.start_task(task);
        progress.update(task, advance=10100);

    with Progress(*progress_columns) as progress:
        task = progress.add_task("generating 28m circle 100m field...", total=10100, start=False);
        run28mCircle100mField();
        progress.start_task(task);
        progress.update(task, advance=10100);
    
    with Progress(*progress_columns) as progress:
        task = progress.add_task("generating 1m circle 100m field...", total=10100, start=False);
        run1mCircle100mField();
        progress.start_task(task);
        progress.update(task, advance=10100);
    
    with Progress(*progress_columns) as progress:
        task = progress.add_task("generating 20x5 rectangle 100m field...", total=10100, start=False);
        run20x5mRectangle100mField();
        progress.start_task(task);
        progress.update(task, advance=10100);


    # DETECTION (REAL WORLD DATA) EXPERIMENTS:

    realWorldDataDirectory = HolesDictionary.getRealWorldDataDirectoryName();
    with Progress(*progress_columns) as progress:
        task = progress.add_task("generating low density...", total=10100, start=False);
        runRealWorldExperiment(realWorldDataDirectory + "/Low Density Artefact Coordinates.csv", "LowDensity");
        progress.start_task(task);
        progress.update(task, advance=10100);
    
    with Progress(*progress_columns) as progress:
        task = progress.add_task("generating moderate density...", total=10100, start=False);
        runRealWorldExperiment(realWorldDataDirectory + "/Moderate Density Artefact Coordinates.csv", "ModerateDensity");
        progress.start_task(task);
        progress.update(task, advance=10100);

    with Progress(*progress_columns) as progress:
        task = progress.add_task("generating high density...", total=10100, start=False);
        runRealWorldExperiment(realWorldDataDirectory + "/High Density Artefact Coordinates.csv", "HighDensity");
        progress.start_task(task);
        progress.update(task, advance=10100);


# generate the graphs and tables used in the Size Matters paper, and save them in the
# sizematters/graphs directory
def generateGraphsAndTables():
    print("GENERATING GRAPHS AND TABLES IN THE graphs/sizematters DIRECTORY");


    # PLOT INTERSECTION FIGURES

    plotExperiment(sizeMattersDirectory + "/7mCircle 100mField 0.5mPits.csv", sizeMattersDirectory + "/7mCircle 100mField 1mPits.csv", sizeMattersDirectory + "/7mCircle 100mField.png", "Site: 7m diameter, Field: 100m x 100m", 260, 20, ratios=False);
    plotExperiment(sizeMattersDirectory + "/7mCircle 200mField 0.5mPits.csv", sizeMattersDirectory + "/7mCircle 200mField 1mPits.csv", sizeMattersDirectory + "/7mCircle 200mField.png", "Site: 7m diameter, Field: 200m x 200m", 1000, 100, ratios=False);
    plotExperiment(sizeMattersDirectory + "/28mCircle 100mField 0.5mPits.csv", sizeMattersDirectory + "/28mCircle 100mField 1mPits.csv", sizeMattersDirectory + "/28mCircle 100mField.png", "Site: 28m diameter, Field: 100m x 100m", 20, 5, ratios=False);
    plotExperiment(sizeMattersDirectory + "/1mCircle 100mField 0.5mPits.csv", sizeMattersDirectory + "/1mCircle 100mField 1mPits.csv", sizeMattersDirectory + "/1mCircle 100mField.png", "Site: 1m diameter, Field: 100m x 100m", 6000, 1000, ratios=False);
    plotExperiment(sizeMattersDirectory + "/20x5mRectangle 100mField 0.5mPits.csv", sizeMattersDirectory + "/20x5mRectangle 100mField 1mPits.csv", sizeMattersDirectory + "/20x5mRectangle 100mField.png", "Site: 20m x 5m elongated, Field: 100m x 100m", 300, 50, ratios=False);

    # plot ratio figures
    plotExperiment(sizeMattersDirectory + "/7mCircle 100mField 0.5mPits.csv", sizeMattersDirectory + "/7mCircle 100mField 1mPits.csv", sizeMattersDirectory + "/7mCircle 100mField ratios.png", "Site: 7m diameter, Field: 100m x 100m", 260, 20, ratios=True);
    plotExperiment(sizeMattersDirectory + "/28mCircle 100mField 0.5mPits.csv", sizeMattersDirectory + "/28mCircle 100mField 1mPits.csv", sizeMattersDirectory + "/28mCircle 100mField ratios.png", "Site: 28m diameter, Field: 100m x 100m", 20, 5, ratios=True);
    plotExperiment(sizeMattersDirectory + "/1mCircle 100mField 0.5mPits.csv", sizeMattersDirectory + "/1mCircle 100mField 1mPits.csv", sizeMattersDirectory + "/1mCircle 100mField ratios.png", "Site: 1m diameter, Field: 100m x 100m", 6000, 1000, ratios=True);


    # PLOT DETECTION (REAL WORLD DATA) FIGURES

    plotExperiment(sizeMattersDirectory + "/LowDensity 100mField 0.5mPits.csv", sizeMattersDirectory + "/LowDensity 100mField 1mPits.csv", sizeMattersDirectory + "/LowDensity 100mField.png", "Low Density, Field: 100m x 100m", 550, 50);
    plotExperiment(sizeMattersDirectory + "/ModerateDensity 100mField 0.5mPits.csv", sizeMattersDirectory + "/ModerateDensity 100mField 1mPits.csv", sizeMattersDirectory + "/ModerateDensity 100mField.png", "Moderate Density, Field: 100m x 100m", 160, 20);
    plotExperiment(sizeMattersDirectory + "/HighDensity 100mField 0.5mPits.csv", sizeMattersDirectory + "/HighDensity 100mField 1mPits.csv", sizeMattersDirectory + "/HighDensity 100mField.png", "High Density, Field: 100m x 100m", 140, 20);

    # plot ratio figures
    plotExperiment(sizeMattersDirectory + "/LowDensity 100mField 0.5mPits.csv", sizeMattersDirectory + "/LowDensity 100mField 1mPits.csv", sizeMattersDirectory + "/LowDensity 100mField ratios.png", "Low Density, Field: 100m x 100m", 550, 50, ratios=True);
    plotExperiment(sizeMattersDirectory + "/ModerateDensity 100mField 0.5mPits.csv", sizeMattersDirectory + "/ModerateDensity 100mField 1mPits.csv", sizeMattersDirectory + "/ModerateDensity 100mField ratios.png", "Moderate Density, Field: 100m x 100m", 160, 20, ratios=True);
    plotExperiment(sizeMattersDirectory + "/HighDensity 100mField 0.5mPits.csv", sizeMattersDirectory + "/HighDensity 100mField 1mPits.csv", sizeMattersDirectory + "/HighDensity 100mField ratios.png", "High Density, Field: 100m x 100m", 140, 20, ratios=True);


    # PRODUCE TABLES

    # summary of max differences in success for intersect experiments
    data = [
        ["Site Size (m)", "Effort Ratio", "Maximum Difference in Success\n(percentage points)", "Optimal Test Pit Size"]
    ]
    data.append(["1m diameter", "1:1", str(round(maximumDifferenceInSuccess(sizeMattersDirectory + "/1mCircle 100mField 0.5mPits.csv", sizeMattersDirectory + "/1mCircle 100mField 1mPits.csv", 1))), "{}m\u00b2".format(1)]);
    data.append(["1m diameter", "2:1", str(round(maximumDifferenceInSuccess(sizeMattersDirectory + "/1mCircle 100mField 0.5mPits.csv", sizeMattersDirectory + "/1mCircle 100mField 1mPits.csv", 2))), "{}m\u00b2".format(0.25)]);
    data.append(["1m diameter", "3:1", str(round(maximumDifferenceInSuccess(sizeMattersDirectory + "/1mCircle 100mField 0.5mPits.csv", sizeMattersDirectory + "/1mCircle 100mField 1mPits.csv", 3))), "{}m\u00b2".format(0.25)]);
    data.append(["1m diameter", "4:1", str(round(maximumDifferenceInSuccess(sizeMattersDirectory + "/1mCircle 100mField 0.5mPits.csv", sizeMattersDirectory + "/1mCircle 100mField 1mPits.csv", 4))), "{}m\u00b2".format(0.25)]);
    data.append(["7m diameter", "1:1", str(round(maximumDifferenceInSuccess(sizeMattersDirectory + "/7mCircle 100mField 0.5mPits.csv", sizeMattersDirectory + "/7mCircle 100mField 1mPits.csv", 1))), "{}m\u00b2".format(1)]);
    data.append(["7m diameter", "2:1", str(round(maximumDifferenceInSuccess(sizeMattersDirectory + "/7mCircle 100mField 0.5mPits.csv", sizeMattersDirectory + "/7mCircle 100mField 1mPits.csv", 2))), "{}m\u00b2".format(0.25)]);
    data.append(["7m diameter", "3:1", str(round(maximumDifferenceInSuccess(sizeMattersDirectory + "/7mCircle 100mField 0.5mPits.csv", sizeMattersDirectory + "/7mCircle 100mField 1mPits.csv", 3))), "{}m\u00b2".format(0.25)]);
    data.append(["7m diameter", "4:1", str(round(maximumDifferenceInSuccess(sizeMattersDirectory + "/7mCircle 100mField 0.5mPits.csv", sizeMattersDirectory + "/7mCircle 100mField 1mPits.csv", 4))), "{}m\u00b2".format(0.25)]);
    data.append(["28m diameter", "1:1", str(round(maximumDifferenceInSuccess(sizeMattersDirectory + "/28mCircle 100mField 0.5mPits.csv", sizeMattersDirectory + "/28mCircle 100mField 1mPits.csv", 1))), "{}m\u00b2".format(1)]);
    data.append(["28m diameter", "2:1", str(round(maximumDifferenceInSuccess(sizeMattersDirectory + "/28mCircle 100mField 0.5mPits.csv", sizeMattersDirectory + "/28mCircle 100mField 1mPits.csv", 2))), "{}m\u00b2".format(0.25)]);
    data.append(["28m diameter", "3:1", str(round(maximumDifferenceInSuccess(sizeMattersDirectory + "/28mCircle 100mField 0.5mPits.csv", sizeMattersDirectory + "/28mCircle 100mField 1mPits.csv", 3))), "{}m\u00b2".format(0.25)]);
    data.append(["28m diameter", "4:1", str(round(maximumDifferenceInSuccess(sizeMattersDirectory + "/28mCircle 100mField 0.5mPits.csv", sizeMattersDirectory + "/28mCircle 100mField 1mPits.csv", 4))), "{}m\u00b2".format(0.25)]);
    data.append(["20m x 5m elongated", "1:1", str(round(maximumDifferenceInSuccess(sizeMattersDirectory + "/20x5mRectangle 100mField 0.5mPits.csv", sizeMattersDirectory + "/20x5mRectangle 100mField 1mPits.csv", 1))), "{}m\u00b2".format(1)]);
    plotTable(data, 7.5, 5.5, 2, 2.25, sizeMattersDirectory + "/intersectDifferenceInSuccess.png");

    # break even ratio table for circular sites
    data = [
        ["Site Diameter (m)", "Maximum Break-Even Ratio\n(0.25m\u00b2 to 1m\u00b2)", "Mean Break-Even Ratio\n(0.25m\u00b2 to 1m\u00b2)"],
    ];
    ratios1 = breakEvenRatios(sizeMattersDirectory + "/1mCircle 100mField 0.5mPits.csv", sizeMattersDirectory + "/1mCircle 100mField 1mPits.csv");
    data.append(["1", str(round(ratios1[0], 1))+":1", str(round(ratios1[1], 1))+":1"]);
    ratios7 = breakEvenRatios(sizeMattersDirectory + "/7mCircle 100mField 0.5mPits.csv", sizeMattersDirectory + "/7mCircle 100mField 1mPits.csv")
    data.append(["7", str(round(ratios7[0], 1))+":1", str(round(ratios7[1], 1))+":1"]);
    ratios28 = breakEvenRatios(sizeMattersDirectory + "/28mCircle 100mField 0.5mPits.csv", sizeMattersDirectory + "/28mCircle 100mField 1mPits.csv")
    data.append(["28", str(round(ratios28[0], 1))+":1", str(round(ratios28[1], 1))+":1"]);
    plotTable(data, 6, 2, 2, 2.25, sizeMattersDirectory + "/intersectBreakEvenRatios.png");

    # low density artefact coordinates summary
    data = [
        ["Artefact\nDensity", "Effort\nRatio", "Maximum Difference\nin Success\n(percentage porounds)", "Maximum\nBreak-Even\nRatio\n(0.25m\u00b2 to 1m\u00b2)", "Mean\nBreak-Even\nRatio\n(0.25m\u00b2 to 1m\u00b2)", "Optimal Test\nPit Size"]
    ]
    ratiosLow = breakEvenRatios(sizeMattersDirectory + "/LowDensity 100mField 0.5mPits.csv", sizeMattersDirectory + "/LowDensity 100mField 1mPits.csv");
    maxDiffInSuccess = str(round(maximumDifferenceInSuccess(sizeMattersDirectory + "/LowDensity 100mField 0.5mPits.csv", sizeMattersDirectory + "/LowDensity 100mField 1mPits.csv", 1)));
    data.append(["Low (2.7/m\u00b2)", "1:1", maxDiffInSuccess, str(round(ratiosLow[0], 1))+":1", str(round(ratiosLow[1], 1))+":1", "1m\u00b2"]);
    data.append(["Low (2.7/m\u00b2)", "2:1", round(maximumDifferenceInSuccess(sizeMattersDirectory + "/LowDensity 100mField 0.5mPits.csv", sizeMattersDirectory + "/LowDensity 100mField 1mPits.csv", 2)), "-", "-", "1m\u00b2"]);
    data.append(["Low (2.7/m\u00b2)", "3:1", round(maximumDifferenceInSuccess(sizeMattersDirectory + "/LowDensity 100mField 0.5mPits.csv", sizeMattersDirectory + "/LowDensity 100mField 1mPits.csv", 3)), "-", "-", "0.25m\u00b2"]);
    data.append(["Low (2.7/m\u00b2)", "4:1", round(maximumDifferenceInSuccess(sizeMattersDirectory + "/LowDensity 100mField 0.5mPits.csv", sizeMattersDirectory + "/LowDensity 100mField 1mPits.csv", 4)), "-", "-", "0.25m\u00b2"]);
    plotTable(data, 7.5, 2, 1, 4.5, sizeMattersDirectory + "/lowDensitySummary.png", cellHeight=0.04);

    # moderate density artefact coordinates summary
    data = [
        ["Artefact\nDensity", "Effort\nRatio", "Maximum Difference\nin Success\n(percentage points)", "Maximum\nBreak-Even\nRatio\n(0.25m\u00b2 to 1m\u00b2)", "Mean\nBreak-Even\nRatio\n(0.25m\u00b2 to 1m\u00b2)", "Optimal Test\nPit Size"]
    ]
    ratiosModerate = breakEvenRatios(sizeMattersDirectory + "/ModerateDensity 100mField 0.5mPits.csv", sizeMattersDirectory + "/ModerateDensity 100mField 1mPits.csv");
    maxDiffInSuccess = str(round(maximumDifferenceInSuccess(sizeMattersDirectory + "/ModerateDensity 100mField 0.5mPits.csv", sizeMattersDirectory + "/ModerateDensity 100mField 1mPits.csv", 1)));
    data.append(["Moderate (28.8/m\u00b2)", "1:1", maxDiffInSuccess, str(round(ratiosModerate[0], 1))+":1", str(round(ratiosModerate[1], 1))+":1", "1m\u00b2"]);
    data.append(["Moderate (28.8/m\u00b2)", "2:1", round(maximumDifferenceInSuccess(sizeMattersDirectory + "/ModerateDensity 100mField 0.5mPits.csv", sizeMattersDirectory + "/ModerateDensity 100mField 1mPits.csv", 2)), "-", "-", "0.25m\u00b2"]);
    data.append(["Moderate (28.8/m\u00b2)", "3:1", round(maximumDifferenceInSuccess(sizeMattersDirectory + "/ModerateDensity 100mField 0.5mPits.csv", sizeMattersDirectory + "/ModerateDensity 100mField 1mPits.csv", 3)), "-", "-", "0.25m\u00b2"]);
    data.append(["Moderate (28.8/m\u00b2)", "4:1", round(maximumDifferenceInSuccess(sizeMattersDirectory + "/ModerateDensity 100mField 0.5mPits.csv", sizeMattersDirectory + "/ModerateDensity 100mField 1mPits.csv", 4)), "-", "-", "0.25m\u00b2"]);
    plotTable(data, 8.2, 2, 1, 4.5, sizeMattersDirectory + "/moderateDensitySummary.png", cellHeight=0.04);

    # high density artefact coordinates summary
    data = [
        ["Artefact\nDensity", "Effort\nRatio", "Maximum Difference\nin Success\n(percentage points)", "Maximum\nBreak-Even\nRatio\n(0.25m\u00b2 to 1m\u00b2)", "Mean\nBreak-Even\nRatio\n(0.25m\u00b2 to 1m\u00b2)", "Optimal Test\nPit Size"]
    ]
    ratiosHigh = breakEvenRatios(sizeMattersDirectory + "/HighDensity 100mField 0.5mPits.csv", sizeMattersDirectory + "/HighDensity 100mField 1mPits.csv");
    maxDiffInSuccess = str(round(maximumDifferenceInSuccess(sizeMattersDirectory + "/HighDensity 100mField 0.5mPits.csv", sizeMattersDirectory + "/HighDensity 100mField 1mPits.csv", 1)));
    data.append(["High (96.8/m\u00b2)", "1:1", maxDiffInSuccess, str(round(ratiosHigh[0], 1))+":1", str(round(ratiosHigh[1], 1))+":1", "1m\u00b2"]);
    data.append(["High (96.8/m\u00b2)", "2:1", round(maximumDifferenceInSuccess(sizeMattersDirectory + "/HighDensity 100mField 0.5mPits.csv", sizeMattersDirectory + "/HighDensity 100mField 1mPits.csv", 2)), "-", "-", "0.25m\u00b2"]);
    data.append(["High (96.8/m\u00b2)", "3:1", round(maximumDifferenceInSuccess(sizeMattersDirectory + "/HighDensity 100mField 0.5mPits.csv", sizeMattersDirectory + "/HighDensity 100mField 1mPits.csv", 3)), "-", "-", "0.25m\u00b2"]);
    data.append(["High (96.8/m\u00b2)", "4:1", round(maximumDifferenceInSuccess(sizeMattersDirectory + "/HighDensity 100mField 0.5mPits.csv", sizeMattersDirectory + "/HighDensity 100mField 1mPits.csv", 4)), "-", "-", "0.25m\u00b2"]);
    plotTable(data, 8.2, 2, 1, 4.5, sizeMattersDirectory + "/highDensitySummary.png", cellHeight=0.04);


if __name__ == "__main__":

    print("This file is not currently supported.\n" + \
    "\"Size Matters\" experiments will be supported when the paper is ready for submission.\n" +\
    "For now run LayoutExperiments.py.");
    exit(0);
    
    # Set goData to True to generate your own data.
    # It may take over 1 hour and 45 miutes on a fast computer.
    goData = False;
    
    # Set to True to generate the graphs and tables
    goGraphsAndTables = True;

    # Set to True to print examples of the experiments to files.
    # These files will be stored in the "printedFields" directory
    # and can be read by CreateFieldImage.py to create graphical depictions
    # of the experiments
    goPrintExperiments = False;
    
    if goData:
        random.seed(123);
        startDatetime = datetime.now();
        print(startDatetime);
        generateData();
        endDatetime = datetime.now();
        print(endDatetime);
        print("time elapsed:", endDatetime - startDatetime)
    elif goGraphsAndTables:
        print("USING PRE-GENERATED DATA.");
        print("If you wish to generate your own data, set \"goData\" to True in SizeMattersExperiments.py.");
        print("It may take over 1 hour and 45 minutes on a fast computer.\n");
        print("Generating graphs and tables is quick.\n")
    
    if goGraphsAndTables:
        generateGraphsAndTables();

    if goPrintExperiments:
        print("Printing experiments to the printedFields directory...");
        random.seed(112358);
        run1mCircle100mField(printExperimentHoles=120);
        run20x5mRectangle100mField(printExperimentHoles=120);
        run28mCircle100mField(printExperimentHoles=120);
        run7mCircle100mField(printExperimentHoles=120);
        run7mCircle200mField(printExperimentHoles=120);
        runRealWorldExperiment(HolesDictionary.getRealWorldDataDirectoryName() + "/Low Density Artefact Coordinates.csv", "LowDensity", printExperimentHoles=120);
        runRealWorldExperiment(HolesDictionary.getRealWorldDataDirectoryName() + "/Moderate Density Artefact Coordinates.csv", "ModerateDensity", printExperimentHoles=120);
        runRealWorldExperiment(HolesDictionary.getRealWorldDataDirectoryName() + "/High Density Artefact Coordinates.csv", "HighDensity", printExperimentHoles=120);
