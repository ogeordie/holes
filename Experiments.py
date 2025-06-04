# Holes

# Holes is a program for simulations of archaeological excavations.

# Copyright 2024-2025 Geordie Oakes

# This program is free software: you can redistribute it and/or modify it under the terms of 
# the GNU General Public License v3 as published by the Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
# See the GNU General Public License v3 for more details.

# You should have received a copy of the GNU General Public License along with this program. 
# If not, see https://www.gnu.org/licenses/gpl-3.0.html.


# See the "README.md" file for information, and installation and usage instructions.


# This is the main file for the Holes project.
# It contains code to run Experiments on the ExperimentRunner implemented
# in Holes.py. It also contains code to plot graphs and tables using Plotter.py.
# Tables contain results of data analysis using Tables.py.

# Data produced is stored in the "data" directory and graphs and tables in the 
# "graphs" directory

from Holes import Experiment, ExperimentRunner, Field, HexagonalLikePlayer, Player
from Tables import maximumDifferenceInSuccess, breakEvenRatios
from Plotter import plotExperiment, plotTable
from pathlib import Path


# A Basic experiment that sets all the experiment parameters with default values.
# For comments on each getter method see the Experiment class in Holes.py.
class BasicExperiment(Experiment):
    def __init__(self):
        self.mFieldSize = 100;
        self.mHoleSize = 0.5;
        self.mHoleIncrement = 1;
        # at this value of mMaxHoles experiments will stop when 100% success rate is reached:
        self.mMaxHoles = 10000;
        self.mRealWorldData = False;
        self.mRealWorldDataFileName = "real world data/Low Density Artefact Coordinates.csv";
        self.mTreasureShape = "circle";
        self.mTreaureRadius = 3.5;
        self.mTreasureWidth = 20;
        self.mTreasureHeight = 5;
        self.mNumRepeats = 10000;
        self.mLRBorder = True;
        self.mStaggerY = False;
        self.mOutputFileName = "experiment.csv"
        self.mPrintAtHoles = 120;
    
    # see Experiment class for details
    def getFieldSize(self) -> int:
        return self.mFieldSize;

    # see Experiment class for details
    def  getHoleSize(self) -> float:
        return self.mHoleSize;

    # see Experiment class for details    
    def getHoleIncrement(self) -> int:
        return self.mHoleIncrement;

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
    def getNumRepeats(self) -> int:
        return self.mNumRepeats;

    # see Experiment class for details
    def getLRBorder(self) -> bool:
        return self.mLRBorder;

    # see Experiment class for details
    def getStaggerY(self) -> bool:
        return self.mStaggerY;

    # see Experiment class for details
    def getOutputFileName(self) -> str:
        return self.mOutputFileName;

    # see Experiment class for details
    def getPrintAtHoles(self) -> int:
        return self.mPrintAtHoles;

    # see Experiment class for details
    def getPlayer(self, field:Field, holes:int) -> Player:
        return HexagonalLikePlayer(field, self.mHoleSize, holes, self.mLRBorder, self.mStaggerY);

# Experiments with a circular treasure of diameter 7m on a 100m x 100m field,
# first with 0.5m x 0.5m holes, then with 1m x 1m holes
def run7mCircle100mField():
    experiment = BasicExperiment();
    experiment.mOutputFileName = "7mCircle 100mField 0.5mPits.csv";
    runner = ExperimentRunner(experiment);
    runner.runExperiment(printData=False);

    experiment.mHoleSize = 1;
    experiment.mOutputFileName = "7mCircle 100mField 1mPits.csv"
    runner = ExperimentRunner(experiment);
    runner.runExperiment(printData=False);

# Experiments with a circular treasure of diameter 7m on a 200m x 200m field,
# first with 0.5m x 0.5m holes, then with 1m x 1m holes
def run7mCircle200mField():
    experiment = BasicExperiment();
    experiment.mFieldSize = 200;
    # experiment.mMaxHoles = 1000;
    experiment.mOutputFileName = "7mCircle 200mField 0.5mPits.csv"
    runner = ExperimentRunner(experiment);
    runner.runExperiment(printData=False);

    experiment.mHoleSize = 1;
    experiment.mOutputFileName = "7mCircle 200mField 1mPits.csv"
    runner = ExperimentRunner(experiment);
    runner.runExperiment(printData=False);

# Experiments with a circular treasure of diameter 28m on a 100m x 100m field,
# first with 0.5m x 0.5m holes, then with 1m x 1m holes
def run28mCircle100mField():
    experiment = BasicExperiment();
    experiment.mTreaureRadius = 14;
    # experiment.mMaxHoles = 25;
    experiment.mOutputFileName = "28mCircle 100mField 0.5mPits.csv";
    runner = ExperimentRunner(experiment);
    runner.runExperiment(printData=False);

    experiment.mHoleSize = 1;
    experiment.mOutputFileName = "28mCircle 100mField 1mPits.csv"
    runner = ExperimentRunner(experiment);
    runner.runExperiment(printData=False);

# Experiments with a circular treasure of diameter 1m on a 100m x 100m field,
# first with 0.5m x 0.5m holes, then with 1m x 1m holes
def run1mCircle100mField():
    experiment = BasicExperiment();
    experiment.mTreaureRadius = 0.5
    # experiment.mMaxHoles = 7300;
    experiment.mOutputFileName = "1mCircle 100mField 0.5mPits.csv";
    runner = ExperimentRunner(experiment);
    runner.runExperiment(printData=False);

    experiment.mHoleSize = 1;
    # experiment.mMaxHoles = 6000;
    experiment.mOutputFileName = "1mCircle 100mField 1mPits.csv"
    runner = ExperimentRunner(experiment);
    runner.runExperiment(printData=False);

# Experiments with an elongated treasure of dimensions 20m x 5m on a 100m x 100m field,
# first with 0.5m x 0.5m holes, then with 1m x 1m holes
def run20x5mRectangle100mField():
    experiment = BasicExperiment();
    experiment.mTreasureShape="rectangle";
    experiment.mTreasureWidth = 20;
    experiment.mTreasureHeight = 5;
    # experiment.mMaxHoles = 350;
    experiment.mOutputFileName = "20x5mRectangle 100mField 0.5mPits.csv";
    runner = ExperimentRunner(experiment);
    runner.runExperiment(printData=False);

    experiment.mHoleSize = 1;
    experiment.mOutputFileName = "20x5mRectangle 100mField 1mPits.csv"
    runner = ExperimentRunner(experiment);
    runner.runExperiment(printData=False);

# Experiments with treasure defined by real world data on artefact coordinates
# on a 100m x 100m field, first with 0.5m x 0.5m holes, then with 1m x 1m holes.
# outputFileNameStart should not include a path, e.g. "LowDensity"
def runRealWorldExperiment(realWorldDataFileName:str, maxHoles:int, ouptutFileNameStart:str):
    experiment = BasicExperiment();
    experiment.mRealWorldData = True;
    experiment.mRealWorldDataFileName = realWorldDataFileName;
    experiment.mMaxHoles = maxHoles;
    experiment.mOutputFileName = ouptutFileNameStart + " 100mField 0.5mPits.csv";
    runner = ExperimentRunner(experiment);
    runner.runExperiment(printData=False);

    experiment.mHoleSize = 1;
    experiment.mOutputFileName = ouptutFileNameStart + " 100mField 1mPits.csv";
    runner = ExperimentRunner(experiment);
    runner.runExperiment(printData=False);


# generate the data, placing it in the data directory
def generateData():
    print("GENERATING DATA IN THE data DIRECTORY");
    print("This may take many hours, especially on a slower computer.");
    print("It may appear to be stuck but it is not stuck!");

    # intersection experiments:
    run7mCircle100mField();
    run7mCircle200mField();
    run28mCircle100mField();
    run1mCircle100mField();
    run20x5mRectangle100mField()

    # detection (real world data) experiments:
    runRealWorldExperiment("real world data/Low Density Artefact Coordinates.csv", 10000, "LowDensity");
    runRealWorldExperiment("real world data/Moderate Density Artefact Coordinates.csv", 10000, "ModerateDensity");
    runRealWorldExperiment("real world data/High Density Artefact Coordinates.csv", 10000, "HighDensity");


# generate the graphs and tables used in the paper
def generateGraphsAndTables():
    print("GENERATING GRAPHS AND TABLES IN THE graphs DIRECTORY");

    # PLOT INTERSECTION FIGURES

    plotExperiment("7mCircle 100mField 0.5mPits.csv", "7mCircle 100mField 1mPits.csv", "7mCircle 100mField.png", "Site: 7m diameter, Field: 100m x 100m", 260, 20, ratios=False);
    plotExperiment("7mCircle 200mField 0.5mPits.csv", "7mCircle 200mField 1mPits.csv", "7mCircle 200mField.png", "Site: 7m diameter, Field: 200m x 200m", 1000, 100, ratios=False);
    plotExperiment("28mCircle 100mField 0.5mPits.csv", "28mCircle 100mField 1mPits.csv", "28mCircle 100mField.png", "Site: 28m diameter, Field: 100m x 100m", 20, 5, ratios=False);
    plotExperiment("1mCircle 100mField 0.5mPits.csv", "1mCircle 100mField 1mPits.csv", "1mCircle 100mField.png", "Site: 1m diameter, Field: 100m x 100m", 6000, 1000, ratios=False);
    plotExperiment("20x5mRectangle 100mField 0.5mPits.csv", "20x5mRectangle 100mField 1mPits.csv", "20x5mRectangle 100mField.png", "Site: 20m x 5m elongated, Field: 100m x 100m", 300, 50, ratios=False);

    # plot ratio figures
    plotExperiment("7mCircle 100mField 0.5mPits.csv", "7mCircle 100mField 1mPits.csv", "7mCircle 100mField ratios.png", "Site: 7m diameter, Field: 100m x 100m", 260, 20, ratios=True);
    plotExperiment("28mCircle 100mField 0.5mPits.csv", "28mCircle 100mField 1mPits.csv", "28mCircle 100mField ratios.png", "Site: 28m diameter, Field: 100m x 100m", 20, 5, ratios=True);
    plotExperiment("1mCircle 100mField 0.5mPits.csv", "1mCircle 100mField 1mPits.csv", "1mCircle 100mField ratios.png", "Site: 1m diameter, Field: 100m x 100m", 6000, 1000, ratios=True);


    # PLOT DETECTION (REAL WORLD DATA) FIGURES

    plotExperiment("LowDensity 100mField 0.5mPits.csv", "LowDensity 100mField 1mPits.csv", "LowDensity 100mField.png", "Low Density, Field: 100m x 100m", 550, 50);
    plotExperiment("ModerateDensity 100mField 0.5mPits.csv", "ModerateDensity 100mField 1mPits.csv", "ModerateDensity 100mField.png", "Moderate Density, Field: 100m x 100m", 160, 20);
    plotExperiment("HighDensity 100mField 0.5mPits.csv", "HighDensity 100mField 1mPits.csv", "HighDensity 100mField.png", "High Density, Field: 100m x 100m", 140, 20);

    # plot ratio figures
    plotExperiment("LowDensity 100mField 0.5mPits.csv", "LowDensity 100mField 1mPits.csv", "LowDensity 100mField ratios.png", "Low Density, Field: 100m x 100m", 550, 50, ratios=True);
    plotExperiment("ModerateDensity 100mField 0.5mPits.csv", "ModerateDensity 100mField 1mPits.csv", "ModerateDensity 100mField ratios.png", "Moderate Density, Field: 100m x 100m", 160, 20, ratios=True);
    plotExperiment("HighDensity 100mField 0.5mPits.csv", "HighDensity 100mField 1mPits.csv", "HighDensity 100mField ratios.png", "High Density, Field: 100m x 100m", 140, 20, ratios=True);


    # PRODUCE TABLES

    # summary of max differences in success for intersect experiments
    data = [
        ["Site Size (m)", "Effort Ratio", "Maximum Difference in Success\n(percentage points)", "Optimal Test Pit Size"]
    ]
    data.append(["1m diameter", "1:1", str(round(maximumDifferenceInSuccess("1mCircle 100mField 0.5mPits.csv", "1mCircle 100mField 1mPits.csv", 1))), "{}m\u00b2".format(1)]);
    data.append(["1m diameter", "2:1", str(round(maximumDifferenceInSuccess("1mCircle 100mField 0.5mPits.csv", "1mCircle 100mField 1mPits.csv", 2))), "{}m\u00b2".format(0.25)]);
    data.append(["1m diameter", "3:1", str(round(maximumDifferenceInSuccess("1mCircle 100mField 0.5mPits.csv", "1mCircle 100mField 1mPits.csv", 3))), "{}m\u00b2".format(0.25)]);
    data.append(["1m diameter", "4:1", str(round(maximumDifferenceInSuccess("1mCircle 100mField 0.5mPits.csv", "1mCircle 100mField 1mPits.csv", 4))), "{}m\u00b2".format(0.25)]);
    data.append(["7m diameter", "1:1", str(round(maximumDifferenceInSuccess("7mCircle 100mField 0.5mPits.csv", "7mCircle 100mField 1mPits.csv", 1))), "{}m\u00b2".format(1)]);
    data.append(["7m diameter", "2:1", str(round(maximumDifferenceInSuccess("7mCircle 100mField 0.5mPits.csv", "7mCircle 100mField 1mPits.csv", 2))), "{}m\u00b2".format(0.25)]);
    data.append(["7m diameter", "3:1", str(round(maximumDifferenceInSuccess("7mCircle 100mField 0.5mPits.csv", "7mCircle 100mField 1mPits.csv", 3))), "{}m\u00b2".format(0.25)]);
    data.append(["7m diameter", "4:1", str(round(maximumDifferenceInSuccess("7mCircle 100mField 0.5mPits.csv", "7mCircle 100mField 1mPits.csv", 4))), "{}m\u00b2".format(0.25)]);
    data.append(["28m diameter", "1:1", str(round(maximumDifferenceInSuccess("28mCircle 100mField 0.5mPits.csv", "28mCircle 100mField 1mPits.csv", 1))), "{}m\u00b2".format(1)]);
    data.append(["28m diameter", "2:1", str(round(maximumDifferenceInSuccess("28mCircle 100mField 0.5mPits.csv", "28mCircle 100mField 1mPits.csv", 2))), "{}m\u00b2".format(0.25)]);
    data.append(["28m diameter", "3:1", str(round(maximumDifferenceInSuccess("28mCircle 100mField 0.5mPits.csv", "28mCircle 100mField 1mPits.csv", 3))), "{}m\u00b2".format(0.25)]);
    data.append(["28m diameter", "4:1", str(round(maximumDifferenceInSuccess("28mCircle 100mField 0.5mPits.csv", "28mCircle 100mField 1mPits.csv", 4))), "{}m\u00b2".format(0.25)]);
    data.append(["20m x 5m elongated", "1:1", str(round(maximumDifferenceInSuccess("20x5mRectangle 100mField 0.5mPits.csv", "20x5mRectangle 100mField 1mPits.csv", 1))), "{}m\u00b2".format(1)]);
    plotTable(data, 7.5, 5.5, 2, 2.25, "intersectDifferenceInSuccess.png");

    # break even ratio table for circular sites
    data = [
        ["Site Diameter (m)", "Maximum Break-Even Ratio\n(0.25m\u00b2 to 1m\u00b2)", "Mean Break-Even Ratio\n(0.25m\u00b2 to 1m\u00b2)"],
    ];
    ratios1 = breakEvenRatios("1mCircle 100mField 0.5mPits.csv", "1mCircle 100mField 1mPits.csv");
    data.append(["1", str(round(ratios1[0], 1))+":1", str(round(ratios1[1], 1))+":1"]);
    ratios7 = breakEvenRatios("7mCircle 100mField 0.5mPits.csv", "7mCircle 100mField 1mPits.csv")
    data.append(["7", str(round(ratios7[0], 1))+":1", str(round(ratios7[1], 1))+":1"]);
    ratios28 = breakEvenRatios("28mCircle 100mField 0.5mPits.csv", "28mCircle 100mField 1mPits.csv")
    data.append(["28", str(round(ratios28[0], 1))+":1", str(round(ratios28[1], 1))+":1"]);
    plotTable(data, 6, 2, 2, 2.25, "intersectBreakEvenRatios.png");

    # low density artefact coordinates summary
    data = [
        ["Artefact\nDensity", "Effort\nRatio", "Maximum Difference\nin Success\n(percentage porounds)", "Maximum\nBreak-Even\nRatio\n(0.25m\u00b2 to 1m\u00b2)", "Mean\nBreak-Even\nRatio\n(0.25m\u00b2 to 1m\u00b2)", "Optimal Test\nPit Size"]
    ]
    ratiosLow = breakEvenRatios("LowDensity 100mField 0.5mPits.csv", "LowDensity 100mField 1mPits.csv");
    maxDiffInSuccess = str(round(maximumDifferenceInSuccess("LowDensity 100mField 0.5mPits.csv", "LowDensity 100mField 1mPits.csv", 1)));
    data.append(["Low (2.7/m\u00b2)", "1:1", maxDiffInSuccess, str(round(ratiosLow[0], 1))+":1", str(round(ratiosLow[1], 1))+":1", "1m\u00b2"]);
    data.append(["Low (2.7/m\u00b2)", "2:1", round(maximumDifferenceInSuccess("LowDensity 100mField 0.5mPits.csv", "LowDensity 100mField 1mPits.csv", 2)), "-", "-", "1m\u00b2"]);
    data.append(["Low (2.7/m\u00b2)", "3:1", round(maximumDifferenceInSuccess("LowDensity 100mField 0.5mPits.csv", "LowDensity 100mField 1mPits.csv", 3)), "-", "-", "0.25m\u00b2"]);
    data.append(["Low (2.7/m\u00b2)", "4:1", round(maximumDifferenceInSuccess("LowDensity 100mField 0.5mPits.csv", "LowDensity 100mField 1mPits.csv", 4)), "-", "-", "0.25m\u00b2"]);
    plotTable(data, 7.5, 2, 1, 4.5, "lowDensitySummary.png", cellHeight=0.04);

    # moderate density artefact coordinates summary
    data = [
        ["Artefact\nDensity", "Effort\nRatio", "Maximum Difference\nin Success\n(percentage points)", "Maximum\nBreak-Even\nRatio\n(0.25m\u00b2 to 1m\u00b2)", "Mean\nBreak-Even\nRatio\n(0.25m\u00b2 to 1m\u00b2)", "Optimal Test\nPit Size"]
    ]
    ratiosModerate = breakEvenRatios("ModerateDensity 100mField 0.5mPits.csv", "ModerateDensity 100mField 1mPits.csv");
    maxDiffInSuccess = str(round(maximumDifferenceInSuccess("ModerateDensity 100mField 0.5mPits.csv", "ModerateDensity 100mField 1mPits.csv", 1)));
    data.append(["Moderate (28.8/m\u00b2)", "1:1", maxDiffInSuccess, str(round(ratiosModerate[0], 1))+":1", str(round(ratiosModerate[1], 1))+":1", "1m\u00b2"]);
    data.append(["Moderate (28.8/m\u00b2)", "2:1", round(maximumDifferenceInSuccess("ModerateDensity 100mField 0.5mPits.csv", "ModerateDensity 100mField 1mPits.csv", 2)), "-", "-", "0.25m\u00b2"]);
    data.append(["Moderate (28.8/m\u00b2)", "3:1", round(maximumDifferenceInSuccess("ModerateDensity 100mField 0.5mPits.csv", "ModerateDensity 100mField 1mPits.csv", 3)), "-", "-", "0.25m\u00b2"]);
    data.append(["Moderate (28.8/m\u00b2)", "4:1", round(maximumDifferenceInSuccess("ModerateDensity 100mField 0.5mPits.csv", "ModerateDensity 100mField 1mPits.csv", 4)), "-", "-", "0.25m\u00b2"]);
    plotTable(data, 8.2, 2, 1, 4.5, "moderateDensitySummary.png", cellHeight=0.04);

    # high density artefact coordinates summary
    data = [
        ["Artefact\nDensity", "Effort\nRatio", "Maximum Difference\nin Success\n(percentage points)", "Maximum\nBreak-Even\nRatio\n(0.25m\u00b2 to 1m\u00b2)", "Mean\nBreak-Even\nRatio\n(0.25m\u00b2 to 1m\u00b2)", "Optimal Test\nPit Size"]
    ]
    ratiosHigh = breakEvenRatios("HighDensity 100mField 0.5mPits.csv", "HighDensity 100mField 1mPits.csv");
    maxDiffInSuccess = str(round(maximumDifferenceInSuccess("HighDensity 100mField 0.5mPits.csv", "HighDensity 100mField 1mPits.csv", 1)));
    data.append(["High (96.8/m\u00b2)", "1:1", maxDiffInSuccess, str(round(ratiosHigh[0], 1))+":1", str(round(ratiosHigh[1], 1))+":1", "1m\u00b2"]);
    data.append(["High (96.8/m\u00b2)", "2:1", round(maximumDifferenceInSuccess("HighDensity 100mField 0.5mPits.csv", "HighDensity 100mField 1mPits.csv", 2)), "-", "-", "0.25m\u00b2"]);
    data.append(["High (96.8/m\u00b2)", "3:1", round(maximumDifferenceInSuccess("HighDensity 100mField 0.5mPits.csv", "HighDensity 100mField 1mPits.csv", 3)), "-", "-", "0.25m\u00b2"]);
    data.append(["High (96.8/m\u00b2)", "4:1", round(maximumDifferenceInSuccess("HighDensity 100mField 0.5mPits.csv", "HighDensity 100mField 1mPits.csv", 4)), "-", "-", "0.25m\u00b2"]);
    plotTable(data, 8.2, 2, 1, 4.5, "highDensitySummary.png", cellHeight=0.04);

# Set generate to True to generate your own data.
# It may take many hours.
generate = False;
if generate:
    generateData();
else:
    print("Using pre-generated data.");
    print("If you wish to generate your own data, set \"generate\" to True in Experiments.py.");
    print("It may take many hours.\n");

generateGraphsAndTables();
