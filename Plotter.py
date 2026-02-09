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
# It expects data as created by Holes.py.

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


# Plots a table with the given data. Data is a 2-D array, with an inner array for each
# row in the table. The first row is assumed to have column titles.
# figwidth and figheight are the dimensions of the graph. 
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


# Plots a graph of the success of various layout algorithms when the treasure is
# defined by a real world polygon.
# Data is assumed to be in the "realworld" subdirectory of the "data" directory.
# Graph is stored in outputFileName which should include the subdirectory of the
# graphs directory and a ".png" suffix.
# The polygon is assumed to be vertically elongated, unless rotate is True
# in which case it is assumed to be horizontally elongated.
def plotPolygonSuccessExperiment(fieldSize:int, outputFileName:str, maxX:int = -1, maxY:int = -1, rotate:bool = False, showGraph = False):
    fig = plt.figure();
    ax1 = fig.add_subplot(111);

    if rotate:
        orientation = "horizontal";
    else:
        orientation = "vertical"

    fileStart = "data/realworld/" + orientation + "polygon "
    fileEnd = " fieldsize" + str(fieldSize) + ".csv"

    maxHoles = -1;
    for la in ["hexlike", "staggerXY", "randomisedStaggerXY sd8", "halton", "random"]:
        f = open(fileStart + la + fileEnd);
        lines = csv.DictReader(f, delimiter=',', skipinitialspace=True);
        holes = [];
        data = [];
        for row in lines:
            holesValue = int(row["actualholes"]);
            holes.append(holesValue);
            data.append(float(row["successrate"]));
            if holesValue > maxHoles:
                maxHoles = holesValue;

        ax1.plot(holes, data, label=HolesDictionary.lookup(la, True));
    ax1.legend(loc="lower right");
    plt.grid();
    if maxX == -1:
        maxX = maxHoles;
    if maxY == -1:
        maxY = 100
    ax1.set_xlim(0, maxX);
    ax1.set_ylim(0, maxY);
    ax1.set_xlabel("number of holes");
    ax1.set_ylabel("success rate");
    titleOrientation = orientation.capitalize();
    plt.title("Success Rate of Layout Algorithms on " + titleOrientation + " Real World Site");
    fig.tight_layout();
    plt.draw();

    filename = "graphs/" + outputFileName;
    outputFile = Path(filename);
    outputFile.parent.mkdir(exist_ok=True, parents=True)
    plt.savefig(filename);
    if showGraph:
        plt.show();

    plt.close(fig);


# Plots a graph of the success of the given layoutAlgorithms on a square field
# of size fieldSize, with treasure of the given dimensions and area.
# Graph is shown in a window if showGraph is True. Data is assumed
# to be in the "drilldown" subdirectory of the data directory.
# minX, maxX, minY, and maxY are the minimum and maximum values for the
# x and y axes respectively.
# The graph is saved in a file named:
# "success <orientation> ratio <ratio> fieldsize<fieldSize> siteArea<siteArea>.png".
def plotSuccessExperiment(fieldSize:int, treasureWidth:float, treasureHeight:float, siteArea:int, layoutAlgorithms:list, minX = -1, maxX:int = -1, minY = -1, maxY = -1, showGraph:bool = True):
    fig = plt.figure();
    ax1 = fig.add_subplot(111);

    maxHoles = -1;
    for la in layoutAlgorithms:
        fileName = "data/drilldown/"+str(treasureWidth) + "x" + str(treasureHeight) + "rectangle " + la + " fieldsize" + str(fieldSize) + " siteArea" + str(siteArea) + ".csv";
        f = open(fileName);
        lines = csv.DictReader(f, delimiter=',', skipinitialspace=True);
        holes = [];
        data = [];
        for row in lines:
            holesValue = int(row["actualholes"]);
            successRate = float(row["successrate"]);
            if successRate == 0:
                pass;
            else:
                holes.append(holesValue);
                data.append(successRate);
            if holesValue > maxHoles:
                maxHoles = holesValue;

        ax1.plot(holes, data, label=HolesDictionary.lookup(la, True));
    ax1.legend(loc="lower right");
    if maxX == -1:
        maxX = maxHoles;
    if maxY == -1:
        maxY = 100;
    if minX == -1:
        minX = 0;
    if minY == -1:
        minY = 0;

    ax1.set_xlim(minX, maxX);
    ax1.set_ylim(minY, maxY);
    ax1.set_xlabel("number of holes");
    ax1.set_ylabel("success rate");
    if treasureWidth > treasureHeight:
        orientation = "Horizontally Elongated";
        ratio = treasureWidth/treasureHeight
    elif treasureWidth == treasureHeight:
        orientation = "Square";
        ratio = 1;
    else:
        orientation = "Vertically Elongated";
        ratio = treasureHeight / treasureWidth;
    plt.title("Success Rate of Layout Algorithms on " + orientation + " Site\nElongation Ratio " + str(round(ratio)) + ", Field Size " + str(fieldSize) + "m x " + str(fieldSize) + "m, Site Area " + str(siteArea) + "m\u00b2");
    fig.tight_layout();
    plt.grid();
    plt.draw();

    addToFileName = "";
    if maxX < 100:
        addToFileName = " zoom"
    filename = "graphs/drilldown/success " + orientation + " ratio " + str(round(ratio)) + " fieldsize" + str(fieldSize) + " siteArea" + str(siteArea) + addToFileName + ".png";
    outputFile = Path(filename);
    outputFile.parent.mkdir(exist_ok=True, parents=True)
    plt.savefig(filename);

    if showGraph:
        plt.show();
    
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


# Adds data for the given layoutAlgorithm to the given data list for success rates
# 80%, 95%, and 100%, being the number of holes needed to reach each success threshold.
# The data added are for the given treasureWidth and treasureHeight, using raw success
# data assumed to be in the "data/drilldown" directory. The data are added as a list
# appended to the end of the data list (so data is a 2D array to be used to create a table).
def _fillInData(fieldSize:int, siteArea:int, data:list, layoutAlgorithm:str, treasureWidth:float, treasureHeight:float) -> None:
    fileName = "data/drilldown/"+str(treasureWidth) + "x" + str(treasureHeight) + "rectangle " + layoutAlgorithm + " fieldsize" + str(fieldSize) + " siteArea" + str(siteArea) + ".csv";
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
# ratios (1, 5, and 20, both vertically and horizontally elongated).
# There are 5 rows (one for each layout algorithm) for each treasure specification.
# Raw success data is assumed to be in the "data/drilldown" directory.
# The table is saved to a file named:
# "graphs/drilldown/holes for success rates table fieldsize<fieldSize> siteArea<siteArea>.png".
# Also saves the data to a csv file with the same file name but a ".csv" suffix.
def plotHolesForSuccessRatesTable(fieldSize:int, siteArea:int, layoutAlgorithms:list):
    data = [["Site Shape\n(Elongation Ratio)", "Layout Algorithm", "80% Success\nRate (pits)", "95% Success\nRate (pits)", "100% Success\nRate (pits)"]];
    for ratio in [1, 5, 20]:
        for vertical in [True, False]:
            if not vertical and ratio == 1:
                continue;
            if vertical:
                width = round(math.sqrt(siteArea / ratio), 2);
                height = round(siteArea/width, 2);
            else:
                height = round(math.sqrt(siteArea / ratio), 2);
                width = round(siteArea/height, 2);

            if ratio == 1:
                data.append(["Square\n(1:1)"]);
                for la in layoutAlgorithms:
                    _fillInData(fieldSize, siteArea, data, la, width, height);
                    if la != layoutAlgorithms[len(layoutAlgorithms) - 1]:
                        data.append([""]);
            elif vertical == True:
                data.append(["Vertically Elongated\n(" + str(ratio) + ":1)"]);
                for la in layoutAlgorithms:
                    _fillInData(fieldSize, siteArea, data, la, width, height);
                    if la != layoutAlgorithms[len(layoutAlgorithms) - 1]:
                        data.append([""]);
            elif vertical == False:
                data.append(["Horizontally Elongated\n(" + str(ratio) + ":1)"]);
                for la in layoutAlgorithms:
                    _fillInData(fieldSize, siteArea, data, la, width, height);
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
        cell.set_height(0.04);
        if col == 0 and row > 0:
            cell.set_text_props(fontproperties=FontProperties(weight='bold'))
        if (row, col) in minimumCells:
            cell.get_text().set_color('darkgreen');
    plt.title("Pits for Success Rates\n Field Size " + str(fieldSize) + "m x " + str(fieldSize) + "m, Site Area " + str(siteArea) + "m\u00b2", pad=25);

    filestem = "graphs/drilldown/holes for success rates table fieldsize" + str(fieldSize) + " siteArea" + str(siteArea);
    outputFile = Path(filestem + ".png");
    outputFile.parent.mkdir(exist_ok=True, parents=True)
    plt.savefig(filestem + ".png");

    _saveTableDataToCsv(filestem, data);


# Adds data for the given layoutAlgorithm to the given data list for success rates.
# The data are the numbers of holes needed by that layout algorithm to reach
# 80%, 95%, and 100% success thresholds.
# The data added are for a real world polygon treasure, in the vertical orientation
# if vertical is True, otherwise the horizontal orientation. Raw success
# data is assumed to be in the "data/realworld" directory. The data are added as a list
# appended to the end of the data list (so data is a 2D array to be used to create a table).
def _fillInDataPolygon(fieldSize:int, data:list, layoutAlgorithm:str, vertical:bool = True):
    orientation = "vertical";
    if not vertical:
        orientation = "horizontal"
    fileName = "data/realworld/"+ orientation + "polygon " + layoutAlgorithm + " fieldsize" + str(fieldSize) + ".csv";
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


# Plots a table showing the number of holes needed to acheive success rates of
# 80%, 95%, and 100% for the various layoutAlgorithms for treasure defined
# by a real world polygon shape. The treasure is oriented vertically if vertical
# is True, otherwise horizontally.
# Raw success data is assumed to be in the "data/realworld" directory.
# The graph is saved to a file named:
# "graphs/realworld/holes for success rates table <orientation>polygon fieldsize<fieldSize>.png".
# Data is also saved to a csv file with the same name (but ".csv" suffix).
def plotPolygonHolesForSuccessRatesTable(fieldSize:int, layoutAlgorithms:list, vertical:bool = True):
    data = [["Layout Algorithm", "80% Success\nRate (pits)", "95% Success\nRate (pits)", "100% Success\nRate (pits)"]];
    for la in layoutAlgorithms:
        data.append([]);
        _fillInDataPolygon(fieldSize, data, la, vertical);
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
    ax.spines['bottom'].set_visible(False)
    orientation = "horizontal";
    if vertical:
        orientation = "vertical";
    titleOrientation = orientation.capitalize();
    plt.title("Pits for Success Rates\nReal World Site Shape, " + titleOrientation + "\nField Size " + str(fieldSize) + "m x " + str(fieldSize) + "m",y = 0.9);
    
    filestem = "graphs/realworld/holes for success rates table " + orientation + "polygon fieldsize" + str(fieldSize);
    outputFile = Path(filestem + ".png");
    outputFile.parent.mkdir(exist_ok=True, parents=True)
    plt.savefig(filestem + ".png");

    _saveTableDataToCsv(filestem, data);


# Plots a graph showing the additional number of holes needed to increase the
# success rate by 1 percentage point, accross all success rates (from 1% to 100%)
# for the various layoutAlgorithms.
# This is not used in the papers, but may be used in future.
# Data is assumed to exist int the "data/drilldown" directory.
# The graph is saved to a file with name:
# "graphs/drilldown/cost of success <layoutAlgorithm> <orientation> ratio<ratio> fieldsize<fieldSize> siteArea<siteArea>.png". 
def plotCostGraph(fieldSize:int, treasureWidth:float, treasureHeight:float, siteArea:int, layoutAlgorithm:str, maxY = None):
    fileName = "data/drilldown/"+str(treasureWidth) + "x" + str(treasureHeight) + "rectangle " + layoutAlgorithm + " fieldsize" + str(fieldSize) + " siteArea" + str(siteArea) + ".csv";
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

    if treasureWidth > treasureHeight:
        orientation = "Horizontally Elongated";
        ratio = treasureWidth/treasureHeight
    elif treasureWidth == treasureHeight:
        orientation = "Square";
        ratio = 1;
    else:
        orientation = "Vertically Elongated";
        ratio = treasureHeight / treasureWidth;
    
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
    outputFileName = "graphs/drilldown/cost of success " + HolesDictionary.lookup(layoutAlgorithm) + " " + orientation + " ratio" + str(round(ratio)) + " fieldsize" + str(fieldSize) + " siteArea" + str(siteArea); 
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
# is not specified dir is used)
# minFieldName is the name of the layout algorithm whose minimum value is used as the minimum
# y axis value if zoom is True (unless minY is specified).
# If fieldNames is specified, it is the list of layout algorithm names to use, which
# must each be featured in the data file.
# The data file is looked for in the dir subdirectory of the data directory.
# Minimum and maximum values for the x axis and minimum value for the y axis may be specified.
# Graph is shown in a window if showGraph is True.
def plotSummaryExperiment(csvDataFileName:str, squareSize:float, siteArea:int, fieldSize:int, outputFileName:str, minFieldName:str = "random", fieldNames:list = None, maxHoles:int = None, dir:str ="", outputDir = None, minX:float = None, maxX:float = None, zoom = False, showGraph:bool = False, minY = None) -> None:
    colours = list(mcolors.TABLEAU_COLORS.values());
    if dir != "":
        dir = dir + "/";
    csvFile = open("data/" + dir + csvDataFileName +".csv", 'r');
    lines = csv.DictReader(csvFile, delimiter=',', skipinitialspace=True);

    logRatios = [];
    for row in lines:
        ratio = float(row["ratio"]);
        if (ratio < 0):
            logRatios.append(-math.log(-ratio, 10));
        else:
            logRatios.append(math.log(ratio, 10));
    if (fieldNames == None):
        fieldNames = lines.fieldnames;
    else:
        fieldNames = ["dummy"] + fieldNames;
    data = [[] for n in range(len(fieldNames) - 1)];
    index = 0;
    fieldMinY = sys.maxsize;
    maxY = 0;
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
            if zoom and logRatios[j] > minX and logRatios[j] < maxX:
                if fieldNames[i] == minFieldName:
                    if value < fieldMinY:
                        fieldMinY = value;
                if value > maxY:
                    maxY = value;
            j = j + 1;
        index = index + 1;
    if minY == None:
        minY = fieldMinY;
    fig = plt.figure();
    ax1 = fig.add_subplot(111);
    for i in range(len(fieldNames) - 1):
        ax1.plot(logRatios, data[i], color=colours[i], label = HolesDictionary.lookup(fieldNames[i+1], True));
  
    ax1.legend();
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax1.set_xlabel("-log(ratio) for vertical elongation and log(ratio) for horizontal elongation");
    yLabel = "overall success";
    if (maxHoles != None):
        yLabel = yLabel + "\npercentage of oracle over " + str(maxHoles) + " test pits";
    ax1.set_ylabel(yLabel);
    ax1.text(0.6, -0.15, 'horizontal elongation -->',
        horizontalalignment='left',
        verticalalignment='top',
        transform=ax1.transAxes);
    ax1.text(0.4, -0.15, '<-- vertical elongation',
        horizontalalignment='right',
        verticalalignment='top',
        transform=ax1.transAxes);
    i = 0;
    while logRatios[i] < 0:
        i = i + 1;

    interval = logRatios[len(logRatios) - 1] / 3;
    verticalXTicks = np.arange(logRatios[0], logRatios[i-1], interval);
    horizontalXTicks = np.arange(interval, logRatios[len(logRatios) - 1] + interval, interval);
    # add the central point
    verticalXTicks = np.append(verticalXTicks, [0]);
    xticks = np.concatenate((verticalXTicks, horizontalXTicks));
    ax1.set_xticks(xticks);
    xTickLabels = [];
    for i in range(len(xticks)):
        if i == 0:
            xTickLabels.append("-log(" + str(round(10**-xticks[i], 1)) + ")");
        elif i == len(xticks) - 1:
            xTickLabels.append("log(" + str(round(10**xticks[i], 1)) + ")");
        elif xticks[i] < 0:
            xTickLabels.append("-log(" + str(round(10**-xticks[i], 1)) + ")");
        else:
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
    
    fig.set_figwidth(8);

    title = "Success of Layout Algorithms vs log(Site Ratio)\nField Size " + str(fieldSize) + ", Site Area " + str(siteArea) + "m\u00b2";
    if maxHoles != None and maxHoles < 100:
        title = "Success of Layout Algorithms vs log(Site Ratio) From 1 to " + str(maxHoles) + " test pits\nField Size " + str(fieldSize) + ", Site Area " + str(siteArea) + "m\u00b2";

    plt.title(title, fontsize = 12);
    fig.tight_layout();
    plt.grid();
    plt.draw();

    if outputDir == None:
        outputDirectory = dir;
    else:
        outputDirectory = outputDir + "/";
    outputFN = "graphs/" + outputDirectory + outputFileName + ".png"
    outputFile = Path(outputFN);
    outputFile.parent.mkdir(exist_ok=True, parents=True)
    plt.savefig(outputFN);
    if showGraph:
        plt.show();
    plt.close(fig);


# Plots a graph of crossover points of the layoutAlgorithms with the halton algorithm, which
# data are in csvFileName (this must include the subdirectory of the data directory
# in which the file exists, and have no sufix).
# See generateCrossoverTableAndGraph() in LayoutExperiments.py for explanation of crossover points.
# The graph is saved to a file named: "graphs/<csvFileName> graph.png".
# This isn't used in the paper.
def plotSummaryCrossoverGraph(csvFileName:str, layoutAlgorithms:list, title:str, showGraph:bool = False) -> None:
    colours = list(mcolors.TABLEAU_COLORS.values());
    siteAreas = [];
    data = [];
    dataIndex = 0;
    for la in layoutAlgorithms:
        csvFile = open("data/" + csvFileName +".csv", 'r');
        lines = csv.DictReader(csvFile, delimiter=',', skipinitialspace=True);
        data.append([]);
        for row in lines:
            if dataIndex == 0:
                siteAreas.append(int(row["site area"]));
            data[dataIndex].append(float(row[la]));
        dataIndex = dataIndex + 1;
    fig = plt.figure();
    ax1 = fig.add_subplot(111);
    for i in range(len(data)):
        ax1.plot(siteAreas, data[i], color=colours[i], label = layoutAlgorithms[i]);
    ax1.legend();
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax1.set_xlabel("site area");
    ax1.set_ylabel("crossover point");

    plt.title(title);
    fig.tight_layout();
    plt.draw();
    plt.savefig("graphs/" + csvFileName + " graph.png");
    if showGraph:
        plt.show();
    plt.close(fig);
    

# Helper function to get the log of the ratio for a treasure of siteArea and treasureHeight,
# and the interpolated success rate of a specific number of holes (numHoles)
# for success data in csvFileName which includes the path and a ".csv" suffix.
def getLogRatioAndSuccess(csvFileName:str, numHoles:int, siteArea:int, treasureHeight:float) -> tuple[float, float]:
    f = open(csvFileName, "r");
    lines = csv.DictReader(f, delimiter=',', skipinitialspace=True);
    i = 0;
    width = siteArea/treasureHeight;
    holes =[];
    successes = [];
    for row in lines:
        holes.append(int(row["actualholes"]));
        successes.append(float(row["successrate"]));
    if successes[len(successes) - 1] != 100:
        if holes[0] > numHoles or holes[len(holes) - 1] < numHoles:
            print("error: data don't cover specific number of holes");
    success = interpolateHoles(numHoles, holes, successes);
    if treasureHeight > width:
        return -math.log(treasureHeight/width, 10), success;
    else:
        return math.log(width/treasureHeight, 10), success;


# Plots a graph of the success rate of various layoutAlgorithms for numHoles number of holes
# versus the log of treasure elongation ratios (specified by treaure height in heights
# and the siteArea).
# Assumes the data for success of each algorithm at numHoles is in files in the dir subdirectory
# of the "data" directory, for example generated by generateSpecificNumberOfHolesData() in
# LayoutExperiments.
# If minFieldName is specified, it is the name of the layout algorithm whose lowest success rate
# will be the minimum y axis value.
# The graph is saved in a file named:
# "graphs/<dir>/<numHoles> holes fieldsize <fieldSize> siteArea<siteArea>.png".
# This was not used in the paper.
def plotSpecificNumberOfHoles(fieldSize:int, siteArea:int, heights:list, numHoles:int, layoutAlgorithms:list, dir:str = "specificholes", minFieldName:str = None) -> None:
    colours = list(mcolors.TABLEAU_COLORS.values());

    fig = plt.figure()
    ax1 = fig.add_subplot(111)

    fileStart = "data/" + dir + "/"
    fileEnd = " fieldsize" + str(fieldSize) + " siteArea" + str(siteArea) + " holes" + str(numHoles) + ".csv";
    colourIndex = 0;
    minY = 100
    maxY = 0;
    for la in layoutAlgorithms:
        logRatios = [];
        successes = [];
        for h in heights:
            height = round(h, 2);
            width = round(siteArea/h, 2);
            fileName = fileStart + str(width) + "x" + str(height) + "rectangle " + la + fileEnd;
            logRatio, success = getLogRatioAndSuccess(fileName, numHoles, siteArea, h);
            logRatios.append(logRatio);
            successes.append(success);
            if la == minFieldName and success < minY:
                minY = success;
            if success > maxY:
                maxY =success;

        ax1.plot(logRatios, successes, label = la, color = colours[colourIndex]);
        colourIndex = colourIndex + 1;
    if minFieldName != None:
        ax1.set_ylim(bottom = minY);

    i = 0;
    while logRatios[i] < 0:
        i = i + 1;
    interval = logRatios[len(logRatios) - 1] / 3;
    verticalXTicks = np.arange(logRatios[0], logRatios[i-1], interval);
    horizontalXTicks = np.arange(interval, logRatios[len(logRatios) - 1] + interval, interval);
    verticalXTicks = np.append(verticalXTicks, [0]);
    xticks = np.concatenate((verticalXTicks, horizontalXTicks));
    ax1.set_xticks(xticks);
    xTickLabels = [];
    for i in range(len(xticks)):
        if xticks[i] < 0:
            xTickLabels.append("-log(" + str(round(10**-xticks[i], 1)) + ")");
        else:
            xTickLabels.append("log(" + str(round(10**xticks[i], 1)) + ")");
                               
    ax1.set_xticklabels(xTickLabels);

    ax1.set_xlabel("-log(ratio) for vertical elongation and log(ratio) for horizontal elongation");
    ax1.set_ylabel("success rate");
    ax1.text(0.6, -0.15, 'horizontal elongation -->',
        horizontalalignment='left',
        verticalalignment='top',
        transform=ax1.transAxes);
    ax1.text(0.4, -0.15, '<-- vertical elongation',
        horizontalalignment='right',
        verticalalignment='top',
        transform=ax1.transAxes);
    ax1.legend();
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left');
    plt.grid();

    plt.title("Success of layout algorithms for exactly " + str(numHoles) + " test pits\nField size " + str(fieldSize) +"m x " + str(fieldSize) + "m, site area " + str(siteArea) + "m\u00b2");
    fig.set_figwidth(8);
    fig.tight_layout();

    # save the graph, creating the graphs directory if necessary
    outFileName = "graphs/" + dir + "/" + str(numHoles) + " holes fieldsize " + str(fieldSize) + " siteArea" + str(siteArea) + ".png";
    outputFile = Path(outFileName);
    outputFile.parent.mkdir(exist_ok=True, parents=True)
    plt.savefig(outFileName);
    plt.close(fig);


# Generates data for the crossover table. csvFileName should contain
# crossover points as generated by generateCrossoverTableAndGraph() in
# LayoutExperiments.py, specifying either vertical elongation or horizontal
# elongation crossover points. See that function for explanation of crossover
# points. The file name should include the subdirectory of the data directory
# and no suffix.
# Data is returned in a list of lists.
# The first sub-list is "site area" and the names of the layout algorithms
# (the headings of the table). Each other sub-list begins with a site area and followed by
# the crossover points for each layout algorithm at this site area.
# variable is the name of the first column in csvFileName, and can be "site area" or "field size"
def createCrossoverTableData(csvFileName:str, layoutAlgorithms:list, variable:str) -> list:

    if variable == "site area":
        data = [
            ["site area (m\u00b2)"]
        ];
    else:
        data = [
            ["field size"]
        ];
    for la in layoutAlgorithms:
        data[0].append(HolesDictionary.lookup(la, True) + "\n(ratio)");
    
    csvFile = open("data/" + csvFileName +".csv", 'r');
    lines = csv.DictReader(csvFile, delimiter=',', skipinitialspace=True);
    dataIndex = 1; 
    for row in lines:
        if variable == "site area":
            data.append([row[variable]]);
        else:
            data.append([row[variable] + "m x " + row[variable] + "m"]);
        for la in layoutAlgorithms:
            data[dataIndex].append(round(float(row[la]), 2));
        dataIndex = dataIndex + 1;
    return data;


# Generates a crossover table. See generateCrossoverTableAndGraph() in LayoutExperiments.py
# for explanation of crossover points. csvFileName should refer to a file generated
# by that function, and should include the subdirectory of the data directory
# in which it lives and no suffix.
# figwidth and figheight are table dimensions, and cellHeight can be specified.
# Table title says "vertical" crossover points unless vertical is False, in which
# case it says "horizontal".
# variable is the name of the first column in csvFileName, and can be "site area" or "field size",
# and the corresponding table is produced (i.e. varying site area or varying field size).
# The table is saved in a file named: "graphs/<csvFileName> table.png".
# Also saves the data to a csv file with the same name but a ".csv" suffix.
def plotSummaryCrossoverTable(csvFileName:str, layoutAlgorithms:list, figwidth:float, figheight:float, variable:str = "site area", cellHeight:float = -1, vertical:bool = True, showGraph:bool = False):
    
    data = createCrossoverTableData(csvFileName, layoutAlgorithms, variable);

    fig, ax = plt.subplots(figsize=(figwidth, figheight));
    ax.axis('off')  # Hide axes for cleaner table display

    ccolors = np.full(len(data[0]), 'lightgrey')

    # create the table
    table = ax.table(cellText=data[1:], colLabels=data[0], loc='center', cellLoc='left', colColours=ccolors);
    table.auto_set_font_size(False);
    if (cellHeight != -1):
        for (row, col), cell in table.get_celld().items():
            cell.set_height(cellHeight);
    table.scale(1.2, 1)
    
    if vertical:
        orientation = "Vertical";
    else:
        orientation = "Horizontal"
    if variable == "site area":
        plt.title("Site Elongation Ratio at which Layout Algorithms Fall Below Halton Success Rate\nfor " + orientation + " Elongation, Field Size 100m x 100m", pad=-40);
    else:
        plt.title("Site Elongation Ratio at which Layout Algorithms Fall Below Halton Success Rate\nfor " + orientation + " Elongation, Site Area 100m\u00b2", pad=-40);
    plt.tight_layout();

    plt.savefig("graphs/" + csvFileName + " table.png");
    if showGraph:
        plt.show();
    plt.close(fig);

    _saveTableDataToCsv("graphs/" + csvFileName, data);
