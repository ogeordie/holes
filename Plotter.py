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


# This file contains code to plot graphs and tables using the matplotlib library.
# It expects data as created by ExperimentRunner.py and Tables.py.

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.font_manager import FontProperties
import csv
import math
import sys
from pathlib import Path
from Tables import interpolateHoles, interpolateSuccessRate
from HolesDictionary import HolesDictionary
from cycler import cycler

# Plot experiments used in the Size Matters paper.
# Plots experiments with small holes and with big holes. Also optionally plots the small
# strategy at different ratios (if "ratios" is True). The filenames supplied should
# include the subdirectory of the "data" directory (usually "sizematters" for this function)
# and ".csv" suffixes.
# "title" is the title of the graph, "endx" is the maximum value on the x axis,
# and "intervalx" is the interval between ticks on the x axis. Note that
# endx must divide by intervalx.
# The graph will be saved to outputFileName in graphs/<outputFileName>, which
# name should include the subdirectory e.g. "sizematters" and a ".png" suffix
def plotExperiment(smallHolesFileName:str, bigHolesFileName:str, outputFileName:str, title:str, endx:int, intervalx, ratios:bool=False):

    if (endx % intervalx != 0):
        print("plotExperiment requires that endx divides by intervalx");
        return;

    xsmall = [];
    ysmall = [];

    xbig = [];
    ybig = [];

    if (ratios):
        x2ratio = []
        x3ratio = [];
        x4ratio = []

    # read the data from csv files into the arrays
    smallCsvFile = open("data/"+smallHolesFileName, 'r');
    bigCsvFile = open("data/"+bigHolesFileName, 'r');
    smallLines = csv.DictReader(smallCsvFile, delimiter=',', skipinitialspace=True);
    bigLines = csv.DictReader(bigCsvFile, delimiter=',', skipinitialspace=True);
    maxHole1x1 = 0;
    for row in smallLines:
        if row['successrate'] != '':
            xsmall.append(int(row['actualholes']));
            ysmall.append(float(row['successrate']));
            smallMaxHole = int(row['actualholes']);
    smallCsvFile.close();

    for row in bigLines:
        if (row['successrate']) != '':
            xbig.append(int(row['actualholes']))
            ybig.append(float(row['successrate']))
            bigMaxHole = int(row['actualholes'])
    bigCsvFile.close();

    # create the x axis values for the ratios
    if (ratios):
        x2ratio = [z/2 for z in xsmall];
        x3ratio = [z/3 for z in xsmall];
        x4ratio = [z/4 for z in xsmall];

    fig = plt.figure()
    ax1 = fig.add_subplot(111)

    # set up the x axis ticks for ax1
    ax1.set_xlim(0, endx);
    ax1.set_ylim(0, 100);
    ax1.set_xticks(np.arange(0, endx + intervalx, intervalx));
    ax1.set_yticks(np.arange(0, 110, 10));
    ax1.set_xlabel('number of test pits')
    ax1.set_ylabel('success rate')

    # set up and plot the ratio lines and axes
    if (ratios):
        fig.subplots_adjust(bottom=0.35)

        ax2 = ax1.twiny()
        ax3 = ax1.twiny();
        ax4 = ax1.twiny();
        x1ticks = ax1.get_xticks();
        ax4.set_xlim(0, endx);
    
        # plot the data on ax4 so that the grid sits behind the lines rather than on top of it
        ax4.plot(xsmall, ysmall, color = 'black', linestyle="dotted", label = "{}m\u00b2 pits (1:1 ratio)".format(0.25));
        ax4.plot(xbig, ybig, color = 'black', linestyle="dashed", label = "{}m\u00b2 pits (1:1 ratio)".format(1));
        ax4.plot(x2ratio, ysmall, color="red", label="2:1 ratio ({}m\u00b2)".format(0.25))
        ax4.plot(x3ratio, ysmall, color="blue", label="3:1 ratio ({}m\u00b2)".format(0.25))
        ax4.plot(x4ratio, ysmall, color="green", label="4:1 ratio ({}m\u00b2)".format(0.25))

        ax2.xaxis.set_ticks_position("bottom")
        ax2.xaxis.set_label_position("bottom")
        ax3.xaxis.set_ticks_position("bottom")
        ax3.xaxis.set_label_position("bottom")
        ax4.xaxis.set_ticks_position("bottom")
        ax4.xaxis.set_label_position("bottom")

        ax2.spines["bottom"].set_position(("axes", -0.18))
        ax3.spines["bottom"].set_position(("axes", -0.32))
        ax4.spines["bottom"].set_position(("axes", -0.45))

        ax2.set_frame_on(True)
        ax2.patch.set_visible(False)
        ax3.set_frame_on(True)
        ax3.patch.set_visible(False);
        ax4.set_frame_on(True)
        ax4.patch.set_visible(False);
    
        for sp in ax2.spines.values():
            sp.set_visible(False)
        for sp in ax3.spines.values():
            sp.set_visible(False)
        for sp in ax4.spines.values():
            sp.set_visible(False)
        ax2.spines["bottom"].set_visible(True)
        ax3.spines["bottom"].set_visible(True)
        ax4.spines["bottom"].set_visible(True)

        ax2.spines["bottom"].set_color("red");
        ax3.spines["bottom"].set_color("blue");
        ax4.spines["bottom"].set_color("green");

        ax2.tick_params(colors='red');
        ax3.tick_params(colors='blue');
        ax4.tick_params(colors='green');

        ax2.xaxis.label.set_color('red');
        ax3.xaxis.label.set_color('blue');
        ax4.xaxis.label.set_color('green');

        ax2.set_xticks(x1ticks);
        ax2.set_xticklabels([z * 2 for z in x1ticks]);
        ax3.set_xticks(x1ticks);
        ax3.set_xticklabels([z * 3 for z in x1ticks]);
        ax4.set_xticks(x1ticks);
        ax4.set_xticklabels([z * 4 for z in x1ticks]);

    else:
        # ratios is False, plot the lines on ax1
        ax1.plot(xsmall, ysmall, color = 'black', linestyle="dotted", label = "{}m\u00b2 pits".format(0.25));
        ax1.plot(xbig, ybig, color = 'black', linestyle="dashed", label = "{}m\u00b2 pits".format(1));


    ax1.grid(visible=True, axis="both");
    if (ratios):
        ax2.grid(visible=True, axis="both");
        ax3.grid(visible=True, axis="both");
        ax4.grid(visible=True, axis="both");
        
    plt.title(title + "\n", fontsize = 12)
    
    if ratios:
        ax4.legend(loc="lower right");
    else:
        ax1.legend(loc="lower right");
    
    fig.tight_layout()
    plt.draw()

    # save the graph, creating the graphs directory if necessary
    outputFile = Path("graphs/" + outputFileName);
    outputFile.parent.mkdir(exist_ok=True, parents=True)
    plt.savefig("graphs/" + outputFileName);


# Plots a table with the given data. data is a 2-D array, with an inner array for each
# row in the table. The first row is assumed to have column titles.
# figwidth and figheight are the dimensions of the table.
# scalex and scaley are the amount to scale the graph in each direction (e.g. 2, 2).
# outputFileName is where the table is stored. This should include the subdirectory,
# of the "graphs" directory in which to store the table and a ".png" suffix.
# cellHeight defines the height of the non-title rows.
# Also saves the data to a csv file with the same stem as outputFileName, and
# a ".csv" suffix.
def plotTable(data:list, figwidth:float, figheight:float, scalex:float, scaley:float, outputFileName:str, cellHeight:float = -1, title:str = None):
    fig, ax = plt.subplots(figsize=(figwidth, figheight));
    ax.axis('off')  # Hide axes for cleaner table display

    # make the title background grey
    ccolors = np.full(len(data[0]), 'lightgrey')

    # create the table
    table = ax.table(cellText=data[1:], colLabels=data[0], loc='center', cellLoc='left', colColours=ccolors);
    table.auto_set_font_size(False);
    table.auto_set_column_width(col=list(range(len(data))))

    if (cellHeight != -1):
        for (row, col), cell in table.get_celld().items():
            if (row > 0):
                cell.set_height(cellHeight);
    table.scale(scalex, scaley)  # Adjust table size

    if title != None:
        plt.title(title, y=0.925);
    
    # draw the table and save it in the graphs directory (creating it if needed)
    plt.draw();
    outputFile = Path("graphs/" + outputFileName);
    outputFile.parent.mkdir(exist_ok=True, parents=True)
    plt.savefig("graphs/" + outputFileName);

    _saveTableDataToCsv("graphs/" + outputFileName[:-4], data);


# Creates a legend for Layout Matters graphs, showing colours for the various
# layout algorithms.
def createLegends():
    plt.plot([], [], label='Hexagonal-like', color = HolesDictionary.getColour("hexlike"));
    plt.plot([], [], label='StaggerXY', color = HolesDictionary.getColour("staggerXY"));
    plt.plot([], [], label='RandomisedStaggerXY', color = HolesDictionary.getColour("randomisedStaggerXY"));
    plt.plot([], [], label='Halton', color = HolesDictionary.getColour("halton"));
    plt.plot([], [], label='Random', color = HolesDictionary.getColour("random"));
    plt.axis("off");

    legend = plt.legend(fontsize=26, loc="center");
    for line in legend.get_lines():
        line.set_linewidth(3.0);

    plt.tight_layout();
    filename = "graphs/legend.png";
    outputFile = Path(filename);
    outputFile.parent.mkdir(exist_ok=True, parents=True)
    plt.savefig(filename);

    plt.close();

    plt.plot([], [], label='Hexagonal-like', color = HolesDictionary.getColour("hexlike"));
    plt.plot([], [], label='Hexagonal', color = HolesDictionary.getColour("hex"));
    plt.axis("off");

    legend = plt.legend(fontsize=26, loc="center");
    for line in legend.get_lines():
        line.set_linewidth(3.0);

    plt.tight_layout();
    filename = "graphs/hex legend.png";
    outputFile = Path(filename);
    outputFile.parent.mkdir(exist_ok=True, parents=True)
    plt.savefig(filename);

    plt.close();


# Helper function to plot a success experiment showing success rate vs number of holes
# for each of the layoutAlgorithms.
# fileStart is the start of the data files to use and fileEnd the end, (including the csv
# suffix) so the data files are "<fileStart><layout-algorithm><fileEnd>".
# capY caps the y axis at its value, when maxY is None.
def _plotSuccessExperiment(fileStart:str, fileEnd:str, layoutAlgorithms:list, title:str, outputFileName:str, maxX:int = None, maxY:int = None, minX:int = None, minY:int = None, capY:int = None, addToYPercent:int = 0):
    fig = plt.figure();
    ax1 = fig.add_subplot(111);

    maxHoles = -1;
    dataMinY = sys.maxsize;
    dataMaxY = -1;
    for la in layoutAlgorithms:
        f = open(fileStart + la + fileEnd);
        lines = csv.DictReader(f, delimiter=',', skipinitialspace=True);
        holes = [];
        data = [];
        for row in lines:
            holesValue = int(row["actualholes"]);
            successRate = float(row["successrate"]);
            holes.append(holesValue);
            data.append(successRate);
            if holesValue > maxHoles:
                maxHoles = holesValue;
            if (minX == None or holesValue > minX) and (maxX == None or holesValue < maxX):
                if successRate < dataMinY:
                    dataMinY = successRate;
                if successRate > dataMaxY:
                    dataMaxY = successRate;

        ax1.plot(holes, data, label=HolesDictionary.lookup(la, True), color = HolesDictionary.getColour(la));
    if maxX == None:
        maxX = maxHoles;
    if maxY == None:
        maxY = dataMaxY + (addToYPercent/100 * (dataMaxY - dataMinY));
    if capY != None and maxY > capY:
        maxY = capY;
    if minX == None:
        minX = 0;
    if minY == None:
        minY = dataMinY;
    ax1.set_xlim(minX, maxX);
    ax1.set_ylim(minY, maxY);
    ax1.set_xlabel("number of pits");
    ax1.set_ylabel("success rate (%)");
    plt.title(title);
    plt.grid();
    fig.tight_layout();
    plt.draw();

    outputFile = Path(outputFileName);
    outputFile.parent.mkdir(exist_ok=True, parents=True)
    plt.savefig(outputFileName);

    plt.close(fig);


# Plots a graph of the success of various layout algorithms when the treasure is
# defined by a case study polygon, for a given rotation.
# Data are assumed to be in the "casestudies" subdirectory of the "data" directory.
# Graph is stored in outputFileName which should include the subdirectory of the
# graphs directory and a ".png" suffix.
def plotPolygonSuccessExperiment(fieldSize:int, description:str, outputFileName:str, maxX:int = None, maxY:int = None, rotation:float = 0):
    fileStart = "data/" + HolesDictionary.getCaseStudiesDirectoryName() + "/casestudypolygon " + description + "@" + str(rotation) + " ";
    fileEnd = " fieldsize" + str(fieldSize) + ".csv"
    layoutAlgorithms = HolesDictionary.getLayoutAlgorithms();
    titleDescripton = HolesDictionary.lookup(description);
    orientation = HolesDictionary.orientationLabel(rotation);
    title = "Performance of Layout Algorithms\n" + titleDescripton + " Case Study Site\n" + orientation + " Orientation";
    outputFilename = "graphs/" + outputFileName;
    _plotSuccessExperiment(fileStart, fileEnd, layoutAlgorithms, title, outputFilename, maxX = maxX, maxY = maxY);


# Plots a graph of the success of the given layoutAlgorithms on a square field
# of size fieldSize, with treasure of the given dimensions, area, and rotation.
# Data are assumed to be in the "success" subdirectory of the data directory.
# minX, maxX, minY, and maxY are the minimum and maximum values for the
# x and y axes respectively.
# The graph is saved in a file named outputFileName.
def plotSuccessExperiment(fieldSize:int, treasureShortSide:float, treasureLongSide:float, treasureRotation:float, siteArea:int, layoutAlgorithms:list, outputFileName:str, minX = None, maxX:int = None, minY = None, maxY = None):
    fileStart = "data/" + HolesDictionary.getSuccessDirectoryName() + "/" +str(treasureLongSide) + "x" + str(treasureShortSide) + "@" + str(treasureRotation) + "rectangle ";
    fileEnd = " fieldsize" + str(fieldSize) + " siteArea" + str(siteArea) + ".csv";

    ratio = treasureLongSide / treasureShortSide;
    orientation = HolesDictionary.orientationLabel(treasureRotation);
    title = "Performance of Layout Algorithms for " + orientation + " Orientation\nElongation Ratio " + str(round(ratio)) + ", Field Size " + str(fieldSize) + "m x " + str(fieldSize) + "m, Site Area " + str(siteArea) + "m\u00b2";

    _plotSuccessExperiment(fileStart, fileEnd, layoutAlgorithms, title, outputFileName, minX = minX, maxX = maxX, minY = minY, maxY = maxY);


# Plots a graph showing the performance of layoutAlgorithm at the given treasure area, ratio,
# and rotation. The graph has curves for field sizes of 50, 100, and 200. The x axis
# is number-of-holes * 100^2 / field area (which is fieldsize^2). If the curves are
# aligned it indicates that this model of field size is accurate. Data are assumed
# to exist in the success subdirectory of the data directory. The graph is saved in
# the supplemental/success subdirectory of the graphs directory.
def plotFieldSizeExperiment(siteArea:int, ratio:int, rotation:float, layoutAlgorithm:str):
    shortSide = math.sqrt(siteArea/ratio);
    longSide = siteArea/shortSide;
    fileStart = "data/" + HolesDictionary.getSuccessDirectoryName() + "/" + str(round(longSide, 2)) + "x" + str(round(shortSide, 2)) + "@" + str(round(rotation, 2)) + "rectangle " + layoutAlgorithm;
    outputFileName = "graphs/supplemental/" + HolesDictionary.getSuccessDirectoryName() + "/field sizes for " + HolesDictionary.lookup(layoutAlgorithm) + " orientation" + str(rotation) + " siteArea" + str(siteArea) + ".png";
    orientation = HolesDictionary.orientationLabel(rotation);
    title = HolesDictionary.lookup(layoutAlgorithm, True) + " at Different Field Sizes\nSite Area " + str(siteArea) + "m\u00b2, " + orientation + " Orientation";
    _plotFieldSizeExperiment([50, 100, 200], siteArea, fileStart, outputFileName, title);


# As for plotFieldSizeExperiment(), but for randomised treasure data (so no site area,
# ratio, or rotation is specified). Data are assumed to exist in the randomtreasure
# subdirectory of the data directory, and graph is saved to the
# supplemental/randomtreasure subdirectory of the graphs directory.
def plotRandomisedTreasureFieldSizeExperiment(layoutAlgorithm, maxX = None):
    fileStart = "data/" + HolesDictionary.getRandomisedTreasureDirectoryName() + "/randomisedtreasure " + layoutAlgorithm;
    outputFileName = "graphs/supplemental/" + HolesDictionary.getRandomisedTreasureDirectoryName() + "/field sizes for randomised treasure " + HolesDictionary.lookup(layoutAlgorithm) + ".png";
    title = HolesDictionary.lookup(layoutAlgorithm, True) + " at Different Field Sizes\nRandomised Site";
    _plotFieldSizeExperiment([100, 150, 200], None, fileStart, outputFileName, title, maxX = 600);


# Does the work of the plotting field size experiments. A graph is saved to outputFileName showing
# the performance of a layout algorithm at each of fieldSizes with the x axis adjusted to
# number-of-holes * 100^2 / field area (which is fieldsize^2). siteArea can be None to allow for
# random treasure data. fileStart is the beginning of the data file name for all field sizes,
# and field size and (possibly) site area are appended to get each data file name. The layout
# algorithm is the one described in fileStart.
def _plotFieldSizeExperiment(fieldSizes:list, siteArea:int, fileStart:str, outputFileName, title, maxX = None):
    fig = plt.figure();
    ax1 = fig.add_subplot(111);

    for fieldSize in fieldSizes:
        if siteArea != None:
            csvFile = fileStart + " fieldsize" + str(fieldSize) + " siteArea" + str(siteArea) + ".csv";
        else:
            csvFile = fileStart + " fieldsize" + str(fieldSize) + ".csv";
        f = open(csvFile);
        lines = csv.DictReader(f, delimiter=',', skipinitialspace=True);
        holes = [];
        successRates = [];
        for row in lines:
            holes.append(float(row["actualholes"]));
            successRates.append(float(row["successrate"]));
        adjustedHoles = [];
        for h in holes:
            adjustedHoles.append(h * 100**2 / fieldSize**2);
        ax1.plot(adjustedHoles, successRates, label="field size " + str(fieldSize) + "m x " + str(fieldSize) + "m");
    
    if maxX != None:
        ax1.set_xlim(0, maxX);
    plt.legend();
    plt.grid();
    plt.title(title);
    ax1.set_xlabel("number of pits x 100\u00b2 / field area");
    ax1.set_ylabel("success rate (%)");
    fig.tight_layout();

    plt.draw();

    outputFile = Path(outputFileName);
    outputFile.parent.mkdir(exist_ok=True, parents=True)
    plt.savefig(outputFileName);

    plt.close(fig);


# saves the given data (which is assumed to be a two-D array suitable for
# creating a table) to fileName which should include the path but no suffix.
def _saveTableDataToCsv(fileName:str, data:list) -> None:
    with open(fileName + ".csv", 'w', newline='') as file:
        for row in range(len(data)):
            for column in range(len(data[row])):
                string = str(data[row][column]);
                cleaned = string.replace('\n', ' ').replace('\r', ' ');
                file.write(cleaned);
                if column != len(data[row]) - 1:
                    file.write(",");
                else:
                    file.write("\n");


# Adds a row of data for a layoutAlgorithm to the given data list, being the number of holes
# needed to reach the success thresholds of 80%, 95%, and 100%.
# The given fileName is assumed to contain success data for the algorithm, which includes
# the relative path starting with (and including) the data directory.
# Data are added as a list appended to the end of the data list (so data is a 2D array
# to be used to create a table).
def _fillInData(fileName:str, data:list, layoutAlgorithm:str) -> None:
    f = open(fileName);
    lines = csv.DictReader(f, delimiter=',', skipinitialspace=True);
    holes = [];
    successRates = [];
    for row in lines:
        holesValue = int(row["actualholes"]);
        successRate = float(row["successrate"]);
        holes.append(holesValue);
        successRates.append(successRate);
    data[len(data) - 1].append(HolesDictionary.lookup(layoutAlgorithm, True));
    for sr in [80, 95, 100]:
        interpolatedHole = interpolateSuccessRate(sr, successRates, holes);
        data[len(data) - 1].append(round(interpolatedHole, 2));


# Takes a list of data which should be a two-D array of data for the
# plotHolesForSuccessRatesTable() or plotPolygonHolesForSuccessRatesTable().
# The table has a number of sites, each taking 5 rows (one for each layout algorithm),
# and columns for the number of pits it takes that algorithm to reach
# 80%, 95%, and 100% success rates.
# Returns a list of tuples, being the (row, column) locations in the given
# data list which contain the minimum values in each column for each
# of the five site rows. There are numSites sites, each of which is assumed to have
# 3 columns (starting at startColumn) and 5 rows of data.
def _getMinimumCells(data:list, numSites:int, startColumn:int) -> list:
    retval = [];
    startRow = 1;
    for site in range(numSites):
        for column in range(startColumn, startColumn + 3):
            min = sys.float_info.max
            for row in range(startRow, startRow + 5):
                cellValue = float(data[row][column]);
                if cellValue < min:
                    min = cellValue;
            for row in range(startRow, startRow + 5):
                cellValue = float(data[row][column]);
                if round(cellValue, 2) == round(min, 2):
                    retval.append((row, column));
        startRow = startRow + 5;
    return retval;


# Plots a table showing the number of holes needed to acheive success rates of
# 80%, 95%, and 100% for the various layoutAlgorithms for various treasure elongation
# ratios (1, 5, and 20) and for both vertically and horizontally oriented treasure.
# There are 5 rows (one for each layout algorithm) for each treasure specification.
# Raw success data are assumed to be in the "data/success" directory.
# The table is saved to a file named:
# "graphs/success/holes for success rates table fieldsize<fieldSize> siteArea<siteArea>.png".
# Also saves the data to a csv file with the same file name but a ".csv" suffix.
def plotHolesForSuccessRatesTable(fieldSize:int, siteArea:int, layoutAlgorithms:list):
    data = [["Site Shape\n(Orientation and \nElongation Ratio)", "Layout Algorithm", "80% Success\nRate (pits)", "95% Success\nRate (pits)", "100% Success\nRate (pits)"]];
    for ratio in [1, 5, 20]:
        for rotation in [0, 90]:
            if rotation == 90 and ratio == 1:
                continue;
            shortSide = math.sqrt(siteArea / ratio);
            longSide = siteArea/shortSide;
            data.append([HolesDictionary.orientationLabel(rotation) + "\n(" + str(ratio) + ":1)"]);
            # data.append([str(rotation) + " Degrees\n(" + str(ratio) + ":1)"]);
            for la in layoutAlgorithms:
                fileName = "data/" + HolesDictionary.getSuccessDirectoryName() + "/" + str(round(longSide, 2)) + "x" + str(round(shortSide, 2)) + "@" + str(rotation) + "rectangle " + la + " fieldsize" + str(fieldSize) + " siteArea" + str(siteArea) + ".csv";
                _fillInData(fileName, data, la);
                if la != layoutAlgorithms[len(layoutAlgorithms) - 1]:
                    data.append([""]);

    minimumCells = _getMinimumCells(data, 5, 2);
    figwidth = 9.4;
    figheight = 13;
    fig, ax = plt.subplots(figsize=(figwidth, figheight));
    ax.axis('off')  # Hide axes for cleaner table display
    ccolors = np.full(len(data[0]), 'lightgrey');
    table = ax.table(cellText=data[1:], colLabels=data[0], loc='center', cellLoc='left', colColours=ccolors, colWidths=[0.3, 0.25, 0.15, 0.15, 0.15]);
    table.auto_set_font_size(False);
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_height(0.06);
        else:
            cell.set_height(0.04);
        if col == 0 and row > 0:
            cell.set_text_props(fontproperties=FontProperties(weight='bold'))
        if (row, col) in minimumCells:
            cell.get_text().set_color('darkgreen');
    plt.title("Pits for Success Rates\n Field Size " + str(fieldSize) + "m x " + str(fieldSize) + "m, Site Area " + str(siteArea) + "m\u00b2", pad=25);

    filestem = "graphs/" + HolesDictionary.getSuccessDirectoryName() + "/holes for success rates table fieldsize" + str(fieldSize) + " siteArea" + str(siteArea);
    outputFile = Path(filestem + ".png");
    outputFile.parent.mkdir(exist_ok=True, parents=True)
    plt.savefig(filestem + ".png");

    _saveTableDataToCsv(filestem, data);


# Plots a table showing the number of holes needed to acheive success rates of
# 80%, 95%, and 100% for the various layoutAlgorithms for treasure defined
# by a case study polygon shape at the given rotation (can be either 0 or 90).
# Raw success data are assumed to be in the "data/casestudies" directory.
# The graph is saved to a file named:
# "graphs/casestudies/holes for success rates table <description> <orientation> polygon fieldsize<fieldSize>.png".
# Data are also saved to a csv file with the same name (but ".csv" suffix).
def plotPolygonHolesForSuccessRatesTable(fieldSize:int, description:str, layoutAlgorithms:list, rotation:float):
    data = [["Layout Algorithm", "80% Success\nRate (pits)", "95% Success\nRate (pits)", "100% Success\nRate (pits)"]];
    for la in layoutAlgorithms:
        data.append([]);
        fileName = "data/" + HolesDictionary.getCaseStudiesDirectoryName() + "/casestudypolygon "+ description + "@" + str(rotation) + " " + la + " fieldsize" + str(fieldSize) + ".csv";
        _fillInData(fileName, data, la);
    minimumCells = _getMinimumCells(data, 1, 1);
    
    fig, ax = plt.subplots(figsize=(8, 4));
    ax.axis('off')  # Hide axes for cleaner table display
    ccolors = np.full(len(data[0]), 'lightgrey');
    table = ax.table(cellText=data[1:], colLabels=data[0], loc='center', cellLoc='left', colColours=ccolors, colWidths=[0.4, 0.2, 0.2, 0.2]);
    table.auto_set_font_size(False);
    for (row, col), cell in table.get_celld().items():
        cell.set_height(0.125);
        if col == 0 and row > 0:
            cell.set_text_props(fontproperties=FontProperties(weight='bold'))
        if (row, col) in minimumCells:
            cell.get_text().set_color('darkgreen');
    table.scale(1.2, 1);
    fig.set_figheight(5);
    ax.spines['bottom'].set_visible(False)
    
    if rotation == 0:
        orientation = "horizontal";
    elif rotation == 90:
        orientation = "vertical";
    else:
        print("unexpected rotation: " + str(rotation));
        exit(1);
    titleOrientation = orientation.capitalize();
    titleElongation = HolesDictionary.lookup(description);
    plt.title("Pits for Success Rates\nCase Study Site Shape, " + titleElongation + "\n" + titleOrientation + " Orientation\nField Size " + str(fieldSize) + "m x " + str(fieldSize) + "m",y = 0.9);
    
    filestem = "graphs/" + HolesDictionary.getCaseStudiesDirectoryName() + "/holes for success rates table " + description + " " + orientation + " polygon fieldsize" + str(fieldSize);
    outputFile = Path(filestem + ".png");
    outputFile.parent.mkdir(exist_ok=True, parents=True)
    plt.savefig(filestem + ".png");

    _saveTableDataToCsv(filestem, data);


# Plots a graph showing the additional number of holes needed to increase the
# success rate by 1 percentage point, accross all success rates (from 1% to 100%)
# for the various layoutAlgorithms.
# This is not used in the papers, but may be used in future.
# Data are assumed to exist int the "data/success" directory.
# The graph is saved to a file with name:
# "graphs/success/cost of success <layoutAlgorithm> <orientation> ratio<ratio> fieldsize<fieldSize> siteArea<siteArea>.png". 
def plotCostGraph(fieldSize:int, treasureShortSide:float, treasureLongSide:float, rotation:float, siteArea:int, layoutAlgorithm:str, maxY = None):
    fileName = "data/" + HolesDictionary.getSuccessDirectoryName() + "/" + str(round(treasureLongSide, 2)) + "x" + str(round(treasureShortSide, 2)) + "@" + str(rotation) + "rectangle " + layoutAlgorithm + " fieldsize" + str(fieldSize) + " siteArea" + str(siteArea) + ".csv";
    f = open(fileName);
    lines = csv.DictReader(f, delimiter=',', skipinitialspace=True);
    holes = [];
    successRates = [];
    for row in lines:
        holeValue = int(row["actualholes"]);
        holes.append(holeValue);
        successRateValue = float(row["successrate"]);
        successRates.append(successRateValue);

    hole = 0;
    additionalHoles = [];
    enumeratedSuccessRates = [];
    for successRate in range(1, 101):
        enumeratedSuccessRates.append(successRate);
        newHole = interpolateSuccessRate(successRate, successRates, holes);
        additionalHoles.append(newHole - hole);
        hole = newHole;

    ratio = treasureLongSide/treasureShortSide;
    if treasureShortSide == treasureLongSide:
        orientation = "Square";
    elif rotation == 0:
        orientation = "Horizontally Elongated";
    elif rotation == 90:
        orientation = "Vertically Elongated";
    
    fig = plt.figure();
    ax1 = fig.add_subplot(111);
    ax1.plot(enumeratedSuccessRates, additionalHoles);
    if maxY != None:
        ax1.set_ylim(top = maxY);
    ax1.set_ylim(bottom = 0);
    plt.xticks(np.arange(0, 100 + 1, 10));
    ax1.set_xlabel("success rate");
    ax1.set_ylabel("number of additional pits needed to\nincrease success rate by 1 percentage point");
    fig.set_figheight(5);
    plt.subplots_adjust(top=0.85);
    plt.title("Cost of Increasing Success Rate by 1 Percentage Point\n" + HolesDictionary.lookup(layoutAlgorithm, True) + " Layout, " + orientation + " Site\nElongation Ratio " + str(round(ratio)) + ", Field Size " + str(fieldSize) + "m x " + str(fieldSize) + "m, Site Area " + str(siteArea) + "m\u00b2");
    outputFileName = "graphs/" + HolesDictionary.getSuccessDirectoryName() + "/cost of success " + HolesDictionary.lookup(layoutAlgorithm) + " " + orientation + " ratio" + str(round(ratio)) + " fieldsize" + str(fieldSize) + " siteArea" + str(siteArea); 
    outputFile = Path(outputFileName);
    outputFile.parent.mkdir(exist_ok=True, parents=True)
    plt.savefig(outputFileName);


# Plots a summary graph of the overall success of various layout algorithms versus the log
# of treasure elongation ratios, for a field of size fieldSize and a site (aka treasure) area of siteArea.
# Expects csvDataFilename to be a summary data file as generated by generateSummaryGraph()
# in LayoutExperiments.py, specifying overall success of each algorithm for each treasure
# elongation ratio, over 1 to maxHoles holes. The file is looked for in the "data/<dir>" directory
# and should not have a suffix.
# The graph is stored in outputFileName.png in the "graphs/<outputDir>" directory (or if outputDir
# is not specified dir is used). If supplemental is True, the output path begins "graphs/supplemental".
# minFieldName is the name of the layout algorithm whose minimum value is used to calculate
# the minimum y axis value if zoom is True (unless minY is specified).
# If fieldNames is specified, it is the list of layout algorithm names to use, which
# must each be featured in the data file, otherwise the names is the first row of the
# data file are used.
# The data file is looked for in the dir subdirectory of the data directory.
# Minimum and maximum values for the x axis and minimum value for the y axis may be specified.
# Graph is shown in a window if showGraph is True.
def plotSummaryExperiment(csvDataFileName:str, siteArea:int, rotation:float, fieldSize:int, outputFileName:str, minFieldName:str = "random", fieldNames:list = None, maxHoles:int = None, dir:str ="", outputDir = None, minX:float = None, maxX:float = None, zoom = False, showGraph:bool = False, minY = None, maxY = None, supplemental:bool = False) -> None:
    #colours = list(mcolors.TABLEAU_COLORS.values());
    if dir != "":
        dir = dir + "/";
    csvFile = open("data/" + dir + csvDataFileName +".csv", 'r');
    lines = csv.DictReader(csvFile, delimiter=',', skipinitialspace=True);

    logRatios = [];
    for row in lines:
        ratio = float(row["ratio"]);
        logRatios.append(math.log(ratio, 10));
    if (fieldNames == None):
        fieldNames = lines.fieldnames;
    else:
        fieldNames = ["dummy"] + fieldNames;
    data = [[] for n in range(len(fieldNames) - 1)];
    index = 0;
    fieldMinY = sys.maxsize;
    dataMaxY = 0;

    if minX == None:
        minX = logRatios[0];
    if maxX == None:
        maxX = logRatios[len(logRatios) - 1];
    for i in range(1, len(fieldNames)):
        csvFile = open("data/" + dir + csvDataFileName + ".csv", 'r');
        lines = csv.DictReader(csvFile, delimiter=',', skipinitialspace=True);
        j = 0;
        for row in lines:
            value = float(row[fieldNames[i]])
            data[index].append(value);
            if logRatios[j] >= minX and logRatios[j] <= maxX:
                if fieldNames[i] == minFieldName:
                    if value < fieldMinY:
                        fieldMinY = value;
                if value > dataMaxY:
                    dataMaxY = value;
            j = j + 1;
        index = index + 1;
    if maxY == None:
        maxY = dataMaxY;
    if minY == None:
        minY = fieldMinY;
        minY -= (maxY - minY)/5;

    fig = plt.figure();
    ax1 = fig.add_subplot(111);
    for i in range(len(fieldNames) - 1):
    #    ax1.plot(logRatios, data[i], color=colours[i], label = HolesDictionary.lookup(fieldNames[i+1], True));
        ax1.plot(logRatios, data[i], label = HolesDictionary.lookup(fieldNames[i+1], True), color = HolesDictionary.getColour(fieldNames[i+1]));
  
    # ax1.legend();
    # ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax1.set_xlabel("log(ratio)");
    yLabel = "overall success";
    if (maxHoles != None):
        yLabel = yLabel + "\npercentage of oracle over " + str(maxHoles) + " test pits";
    ax1.set_ylabel(yLabel);

    interval = logRatios[len(logRatios) - 1] / 6;
    xticks = np.arange(logRatios[0], logRatios[len(logRatios) - 1] + interval, interval);
    ax1.set_xticks(xticks);
    xTickLabels = [];
    for i in range(len(xticks)):
        xTickLabels.append("log(" + str(round(10**xticks[i], 1)) + ")");

    ax1.set_xticklabels(xTickLabels);
    if (minX != None):
        ax1.set_xlim(left = minX);
    else:
        ax1.set_xlim(left = logRatios[0]);
    
    if (maxX != None):
        ax1.set_xlim(right = maxX);
    else:
        ax1.set_xlim(right = logRatios[len(logRatios) - 1]);
    if zoom:
        ax1.set_ylim(minY, maxY);
    else:
        ax1.set_ylim(top = maxY);

    
    fig.set_figwidth(6);
    orientation = HolesDictionary.orientationLabel(rotation);
    title = "Performance of Layout Algorithms vs log(Site Ratio)\n" + orientation + " Orientation\nField Size " + str(fieldSize) + "m x " + str(fieldSize) + "m, Site Area " + str(siteArea) + "m\u00b2";
    if maxHoles != None and maxHoles < 100:
        title = "Performance of Layout Algorithms vs log(Site Ratio)\nFrom 1 to " + str(maxHoles) + " test pits\n" + orientation + " Orientation\nField Size " + str(fieldSize)  + "m x" + str(fieldSize) + "m, Site Area " + str(siteArea) + "m\u00b2";

    plt.title(title, fontsize = 12);
    fig.tight_layout();
    #plt.grid();
    plt.draw();

    if outputDir == None:
        outputDirectory = dir;
    else:
        outputDirectory = outputDir + "/";
    supplementalString = "";
    if supplemental:
        supplementalString = "supplemental/"
    outputFN = "graphs/" + supplementalString + outputDirectory + outputFileName + ".png"
    outputFile = Path(outputFN);
    outputFile.parent.mkdir(exist_ok=True, parents=True)
    plt.savefig(outputFN);
    if showGraph:
        plt.show();
    plt.close(fig);


# Plots a graph showing the overall success of each of the layout algorithms with a column
# in the csvDataFile against the treasure rotation (from -90 to 90 degrees), with elongationRatio.
# Each data point is a summary of a success experiment, as for the summary graphs.
# Data must be in csvDataFileName as generated by generateRotationGraph() in LayoutExperiments.py.
# The graph is saved to the "graphs/rotation" directory. If supplemental is True, the graph is
# saved to "graphs/supplemental/rotation" directory.
def plotRotationExperiment(csvDataFileName:str, fieldSize:int, siteArea:float, elongationRatio:float, maxHoles:int, supplemental:bool = False):
    csvFile = open("data/" + HolesDictionary.getRotationDirectoryName() + "/" + csvDataFileName +".csv", 'r');
    lines = csv.DictReader(csvFile, delimiter=',', skipinitialspace=True);
    angles = [];
    fieldNames = lines.fieldnames;
    for row in lines:
        angle = float(row["orientation"]);
        angles.append(angle);

    fig = plt.figure();
    ax1 = fig.add_subplot(111);

    fig.set_figheight(5);
    fig.set_figwidth(6);


    data = [[] for n in range(len(fieldNames) - 1)];
    for i in range(1, len(fieldNames)):
        csvFile = open("data/" + HolesDictionary.getRotationDirectoryName() + "/" + csvDataFileName +".csv", 'r');
        lines = csv.DictReader(csvFile, delimiter=',', skipinitialspace=True);
        for row in lines:
            data[i-1].append(float(row[fieldNames[i]]));
    for i in range(len(data)):
        ax1.plot(angles, data[i], label = HolesDictionary.lookup(fieldNames[i+1], True), color = HolesDictionary.getColour(fieldNames[i+1]));
    
    ax1.set_xlim(-90, 90);

    ax1.set_xlabel("orientation (degrees)");
    yLabel = "overall success\npercentage of oracle over " + str(maxHoles) + " test pits";
    ax1.set_ylabel(yLabel);

    xticks = np.arange(-90, 90+1, 30);
    ax1.set_xticks(xticks);
    plt.title("Performance of Layout Algorithms vs Site Orientation\nElongation Ratio " + str(elongationRatio) + "\nField Size " + str(fieldSize) + "m x " + str(fieldSize) + "m, Site Area " + str(siteArea) + "m\u00b2", fontsize = 12);
    plt.grid();
    # plt.legend();

    fig.tight_layout();
    supplementalString = "";
    if supplemental:
        supplementalString = "supplemental/"
    outputFN = "graphs/" + supplementalString + HolesDictionary.getRotationDirectoryName() + "/rotation summary ratio" + str(elongationRatio) + " fieldsize" + str(fieldSize) + " siteArea" + str(siteArea) + " maxholes" + str(maxHoles) + ".png"
    outputFile = Path(outputFN);
    outputFile.parent.mkdir(exist_ok=True, parents=True)
    plt.savefig(outputFN);


# Plots success experiments with randomised treasure specifications for the layoutAlgorithms.
# Data are assumed to exist in the randomtreasure subdirectory of the data directory.
# Graphs are saved to the "graphs/randomtreasure" directory, unless supplemental is True
# in which case it is saved to the "graphs/supplemental/randomtreasure" directory.
def plotRandomisedTreasureExperiment(fieldSize:int, layoutAlgorithms:list, minX = None, maxX = None, addToFile = "", supplemental = False, randomiseRatio:bool = False):
    randomiseRatioString = "";
    if randomiseRatio:
        randomiseRatioString = " randomise ratio";
    fileStart = "data/" + HolesDictionary.getRandomisedTreasureDirectoryName() + "/randomisedtreasure ";
    fileEnd = randomiseRatioString + " fieldsize" + str(fieldSize) + ".csv";
    lengthOrRatio = "Length";
    if randomiseRatio:
        lengthOrRatio = "Ratio"
    title = "Randomised Site Area, Orientation and " + lengthOrRatio + "\nField Size " + str(fieldSize) + "m x " + str(fieldSize) + "m";
    if addToFile != "":
        addToFile = " " + addToFile;
    supplementalString = "";
    if supplemental:
        supplementalString = "supplemental/";
    outputFileName = "graphs/" + supplementalString + HolesDictionary.getRandomisedTreasureDirectoryName() + "/randomisedsite" + randomiseRatioString + " fieldsize" + str(fieldSize) + addToFile;
    _plotSuccessExperiment(fileStart, fileEnd, layoutAlgorithms, title, outputFileName, minX = minX, maxX = maxX, capY = 99, addToYPercent=12);


# Generates data for the crossover table. csvFileName should contain
# crossover points as generated by generateCrossoverTable() in
# LayoutExperiments.py, specifying vertical elongation and horizontal
# elongation crossover points. See that function for explanation of crossover
# points. The file name should include the subdirectory of the data directory
# and no suffix.
# Data are returned in a list of lists.
# variable can be "site area", "field size" or "rotation" (only "rotation" is
# used in the article and the others may no longer work).
# The first sub-list is that variable, followed by the names of the layout algorithms
# (the headings of the table).
# Each other sub-list begins with a value for the variable field, then
# the crossover points for each layout algorithm for that value.
def createCrossoverTableData(csvFileName:str, layoutAlgorithms:list, variable:str) -> list:

    if variable == "site area":
        data = [
            ["site area (m\u00b2)"]
        ];
    elif variable == "field size":
        data = [
            ["field size"]
        ];
    elif variable == "rotation":
        data = [
            ["Orientation"]
        ];
    else:
        print("unexpected crossover variable");
        exit(1);
    
    for la in layoutAlgorithms:
        data[0].append(HolesDictionary.lookup(la, True) + "\n(ratio)");
    
    csvFile = open("data/" + csvFileName +".csv", 'r');
    lines = csv.DictReader(csvFile, delimiter=',', skipinitialspace=True);
    dataIndex = 1; 
    for row in lines:
        if variable == "site area":
            data.append([row[variable]]);
        elif variable == "field size":
            data.append([row[variable] + "m x " + row[variable] + "m"]);
        elif variable == "rotation":
            data.append([HolesDictionary.orientationLabel(float(row[variable]))]);
        for la in layoutAlgorithms:
            data[dataIndex].append(round(float(row[la]), 2));
        dataIndex = dataIndex + 1;
    return data;


# Generates a crossover table. See generateCrossoverTable() in LayoutExperiments.py
# for explanation of crossover points. csvFileName should refer to a file generated
# by that function, and should include the subdirectory of the data directory
# in which it lives and no suffix.
# figwidth and figheight are table dimensions, and cellHeight can be specified.
# The table is saved in a file named: "graphs/<csvFileName> table.png".
# Also saves the data to a csv file with the same name but a ".csv" suffix.
def plotSummaryCrossoverTable(csvFileName:str, layoutAlgorithms:list, siteArea:int, figwidth:float, figheight:float, cellHeight:float = -1, showGraph:bool = False):

    variable = "rotation"
    data = createCrossoverTableData(csvFileName, layoutAlgorithms, variable);

    fig, ax = plt.subplots(figsize=(figwidth, figheight));
    ax.axis('off');

    ccolors = np.full(len(data[0]), 'lightgrey')

    table = ax.table(cellText=data[1:], colLabels=data[0], loc='center', cellLoc='left', colColours=ccolors);
    table.auto_set_font_size(False);
    if (cellHeight != -1):
        for (row, col), cell in table.get_celld().items():
            cell.set_height(cellHeight);
    table.scale(1.2, 1)

    plt.title("Site Elongation Ratio at which Layout Algorithms Fall Below Halton Success Rate\nSite Area " + str(siteArea) + "m\u00b2, " + "Field Size 100m x 100m", pad=-40);
    plt.tight_layout();

    plt.savefig("graphs/" + csvFileName + " table.png");
    if showGraph:
        plt.show();
    plt.close(fig);

    _saveTableDataToCsv("graphs/" + csvFileName, data);
