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


# This is a main file for the Holes project, used in the Size Matters article.
# It contains code to run Experiments on the ExperimentRunner implemented
# in Holes.py. It also contains code to plot graphs and tables using Plotter.py.
# Tables contain results of data analysis using Tables.py.

# Data produced is stored in the "data/sizematters" directory and graphs and tables in the 
# "graphs/sizematters" directory

from Holes import Experiment, ExperimentRunner, Field, HexagonalLikePlayer, Player
from Tables import maximumDifferenceInSuccess, breakEvenRatios
from Plotter import plotExperiment, plotTable
from rich.progress import Progress, BarColumn
from pathlib import Path


# A Basic experiment that sets all the experiment parameters with default values.
# For comments on each getter method see the Experiment class in Holes.py.
class BasicExperiment(Experiment):
    def __init__(self):
        self.mFieldSize = 100;
        self.mHoleSize = 0.5;
        self.mHoleIncrement = 1;
        self.mSmallNumHolesIncrement = 1;
        self.mSmallNumHolesIncrementCutoff = 0;
        self.mStartHoles = 1;
        # at this value of mMaxHoles experiments will stop when 100% success rate is reached:
        self.mMaxHoles = 100000;
        self.mRealWorldData = False;
        self.mRealWorldDataFileName = "real world data/Low Density Artefact Coordinates.csv";
        self.mTreasureShape = "circle";
        self.mTreaureRadius = 3.5;
        self.mTreasureWidth = 20;
        self.mTreasureHeight = 5;
        self.mPolygonFile = "";
        self.mRotatePolygon = False;
        self.mNumRepeats = 10000;
        self.mSmallNumHolesNumRepeats = 10000;
        self.mSmallNumHolesNumRepeatsCutoff = 40;
        self.mStopAtSuccess = 100;
        self.mReturnAfterHit = True;
        self.mLRBorder = True;
        self.mStdDeviationDivisor = 1;
        self.mStaggerY = False;
        self.mRandomise = False;
        self.mOutputFileName = sizeMattersDirectory + "/experiment.csv"
    
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
    def getRealWorldData(self) -> bool:
        return self.mRealWorldData;

    # see Experiment class for details
    def getRealWorldDataFile(self) -> str:
        return self.mRealWorldDataFileName;

    # see Experiment class for details
    def getTreasureShape(self) -> str:
        return self.mTreasureShape;

    # see Experiment class for details
    def getTreasureRadius(self) -> float:
        return self.mTreaureRadius;

    # see Experiment class for details
    def getTreasureWidth(self) -> float:
        return self.mTreasureWidth;

    # see Experiment class for details
    def getTreasureHeight(self) -> float:
        return self.mTreasureHeight;

    # see Experiment class for details
    def getPolygonFile(self) -> str:
        return self.mPolygonFile;

    # see Experiment class for details
    def getRotatePolygon(self) -> bool:
        return self.mRotatePolygon;
    
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
    def getLRBorder(self) -> bool:
        return self.mLRBorder;

    # see Experiment class for details
    def getStaggerY(self) -> bool:
        return self.mStaggerY;

    # see Experiment class for details
    def getRandomise(self) -> bool:
        return self.mRandomise;

    # see Experiment class for details
    def getStdDeviationDivisor(self) -> int:
        return self.mStdDeviationDivisor;

    # see Experiment class for details
    def getOutputFileName(self) -> str:
        return self.mOutputFileName;

    # see Experiment class for details
    def getPlayer(self, field:Field, holes:int) -> Player:
        return HexagonalLikePlayer(field, self.mHoleSize, holes, self.mLRBorder, self.mStaggerY);

sizeMattersDirectory = "sizematters";

# Runs experiments with a circular treasure of diameter 7m on a 100m x 100m field,
# first with 0.5m x 0.5m holes, then with 1m x 1m holes
# printExperimentHoles is the number of holes to use when printing the experiment field.
# NOTE that when printExperimentHoles is defined, the experiments will not be run, only printed.
def run7mCircle100mField(printExperimentHoles:int = None):
    experiment = BasicExperiment();
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
    experiment = BasicExperiment();
    experiment.mFieldSize = 200;
    # experiment.mMaxHoles = 1000;
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
    experiment = BasicExperiment();
    experiment.mTreaureRadius = 14;
    # experiment.mMaxHoles = 25;
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
    experiment = BasicExperiment();
    experiment.mTreaureRadius = 0.5
    # experiment.mMaxHoles = 7300;
    experiment.mOutputFileName = sizeMattersDirectory + "/1mCircle 100mField 0.5mPits.csv";
    runner = ExperimentRunner(experiment);
    if printExperimentHoles != None:
        runner.printExperiment(printExperimentHoles);
    else:
        runner.runExperiment(printData=False);

    experiment.mHoleSize = 1;
    # experiment.mMaxHoles = 6000;
    experiment.mOutputFileName = sizeMattersDirectory + "/1mCircle 100mField 1mPits.csv"
    runner = ExperimentRunner(experiment);
    if printExperimentHoles != None:
        runner.printExperiment(printExperimentHoles);
    else:
        runner.runExperiment(printData=False);

# Runs experiments with an elongated treasure of dimensions 20m x 5m on a 100m x 100m field,
# first with 0.5m x 0.5m holes, then with 1m x 1m holes
# printExperimentHoles is the number of holes to use when printing the experiment field.
# NOTE that when printExperimentHoles is defined, the experiments will not be run, only printed.
def run20x5mRectangle100mField(printExperimentHoles:int = None):
    experiment = BasicExperiment();
    experiment.mTreasureShape="rectangle";
    experiment.mTreasureWidth = 20;
    experiment.mTreasureHeight = 5;
    # experiment.mMaxHoles = 350;
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
def runRealWorldExperiment(realWorldDataFileName:str, maxHoles:int, ouptutFileNameStart:str, printExperimentHoles:int = None):
    experiment = BasicExperiment();
    experiment.mRealWorldData = True;
    experiment.mRealWorldDataFileName = realWorldDataFileName;
    experiment.mMaxHoles = maxHoles;
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


# generate all the data for all experiments, placing it in the data/sizematters directory
# NOTE: this may take over an  and 15 minutes on a fast computer
def generateData():
    print("GENERATING DATA IN THE data/sizematters DIRECTORY");
    print("This may take over 1 hour and 15 minutes on a fast computer.");

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
        run20x5mRectangle100mField()
        progress.start_task(task);
        progress.update(task, advance=10100);


    # DETECTION (REAL WORLD DATA) EXPERIMENTS:

    with Progress(*progress_columns) as progress:
        task = progress.add_task("generating low density...", total=10100, start=False);
        runRealWorldExperiment("real world data/Low Density Artefact Coordinates.csv", 10000, "LowDensity");
        progress.start_task(task);
        progress.update(task, advance=10100);
    
    with Progress(*progress_columns) as progress:
        task = progress.add_task("generating moderate density...", total=10100, start=False);
        runRealWorldExperiment("real world data/Moderate Density Artefact Coordinates.csv", 10000, "ModerateDensity");
        progress.start_task(task);
        progress.update(task, advance=10100);
    
    with Progress(*progress_columns) as progress:
        task = progress.add_task("generating high density...", total=10100, start=False);
        runRealWorldExperiment("real world data/High Density Artefact Coordinates.csv", 10000, "HighDensity");
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

    # Set goData to True to generate your own data.
    # It may take over 1 hour and 15 miutes on a fast computer.
    goData = False;
    
    # Set to True to generate the graphs and tables
    goGraphsAndTables = True;

    # Set to True to print examples of the experiments to files.
    # These files will be stored in the "printedFields" directory
    # and can be read by CreateFieldImage.py to create graphical depictions
    # of the experiments
    goPrintExperiments = False;
    
    if goData:
        generateData();
    else:
        print("Using pre-generated data.");
        print("If you wish to generate your own data, set \"goData\" to True in Experiments.py.");
        print("It may take over 1 hour and 15 minutes on a fast computer.\n");
    
    if goGraphsAndTables:
        generateGraphsAndTables();

    if goPrintExperiments:
        print("Printing experiments to the printedFields directory...")
        run1mCircle100mField(printExperimentHoles=120);
        run20x5mRectangle100mField(printExperimentHoles=120);
        run28mCircle100mField(printExperimentHoles=120);
        run7mCircle100mField(printExperimentHoles=120);
        run7mCircle200mField(printExperimentHoles=120);
        runRealWorldExperiment("real world data/Low Density Artefact Coordinates.csv", 10000, "LowDensity", printExperimentHoles=120);
        runRealWorldExperiment("real world data/Moderate Density Artefact Coordinates.csv", 10000, "ModerateDensity", printExperimentHoles=120);
        runRealWorldExperiment("real world data/High Density Artefact Coordinates.csv", 10000, "HighDensity", printExperimentHoles=120);
