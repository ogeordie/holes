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


# This file contains code used to analyse data and populate the tables.

import csv
import numpy as np
import math

# Given two files with data on a small hole experiment and a big hole experiment,
# calculates the maximum difference in success rates for those two strategies over
# all hole numbers. For example there might be -50 percentage points difference
# between the strategies when 100 holes are dug.
# If ratio > 1, calculates the maximum difference between the strategies when
# "ratio" small holes are dug for each big hole. For example if ratio is 2, there
# might be 30 percentage points difference in success rates when 100 big holes are
# dug and 200 small holes are dug. These small hole success rates are interpolated
# as there may not be exactly "ratio * number-of-big-holes" small holes dug.
# Return values are always "small hole success rate" minus "large hole success rate",
# so a positive value indicates the small hole strategy was more successful than the
# large hole strategy at the point where the maximum difference occurred.
# Note that if the big hole data stops at 100% success rate (which occurs before the
# small hole data reaches 100%) and doesn't record 100% for further numbers of holes,
# that is ok as the difference between the small hole success rate and 100%
# decreases as the number of holes increases.
# Assumes each row of each data file has a different and increasing number of holes.
def maximumDifferenceInSuccess(smallHolesFileName:str, bigHolesFileName:str, ratio:int) -> float:
    xsmall = [];
    ysmall = [];

    xbig = [];
    ybig = [];

    # read data from the csv files
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

    # set up the xratio array, x values for the ratio.
    if (ratio > 1):
        xratio = [z/ratio for z in xsmall];
    else:
        xratio = xsmall;

    # Find the maximum difference is success rates, checking each
    # number of big holes and finding the corresponding number
    # holes in xratio (which has been set to xsmall if ratio = 1).
    maxDiff = 0;
    for row in range(0, len(xbig)):
        bigHoles = xbig[row];
        # find small hole matching bigHole
        i = 0;
        if (i < len(xratio)):
            while (xratio[i] < bigHoles):
                i = i + 1;
                if (i >= len(xratio)):
                    break;
            if (i >= len(xratio)):
                break;
            if (i == 0):
                firstSmallSuccess = 0;
                firstSmallHoles = 0;
            else:
                firstSmallSuccess = ysmall[i-1];
                firstSmallHoles = xratio[i-1]
            secondSmallSuccess = ysmall[i];
            secondSmallHoles = xratio[i];
            # interpolate holes
            if secondSmallHoles == 0 and firstSmallHoles == 0:
                percentage = 0;
            else:
                percentage = (bigHoles - firstSmallHoles) / (secondSmallHoles - firstSmallHoles);
            smallSuccess = firstSmallSuccess + percentage * (secondSmallSuccess - firstSmallSuccess);
            diff = smallSuccess - ybig[row];
            if abs(diff) > abs(maxDiff):
                maxDiff = diff;
                maxAtBigHoles = bigHoles;
    return maxDiff;


# See generateCrossoverTableAndGraph() in LayoutExperiments.py for explanation of crossover points.
# This fuction returns a tuple of site ratios which is (verticalCrossover, horizontalCrossover).
# fileName is looked for in the summary subdirectory of the data directory, and is expected
# to contain summary data for the given layoutAlgorithm over a range of treasure elongation
# ratios, as generated by generateSummaryGraph() in LayoutExperiments.py.
def crossoverPoints(fileName:str, layoutAlgorithm:str) -> tuple[float, float]:
    csvFile = open("data/summary/"+fileName, 'r');
    lines = csv.DictReader(csvFile, delimiter=',', skipinitialspace=True);
    previousDiff = None;
    previousRatio = None;
    verticalCrossover = None;
    horizontalCrossover = None;

    for row in lines:
        success = float(row[layoutAlgorithm]);
        diff = success - float(row["halton"]);
        ratio = float(row["ratio"]);
        if previousDiff != None:
            if previousDiff <= 0 and diff > 0:
                if verticalCrossover == None:
                    verticalCrossover = previousRatio + ((0 - previousDiff) / (diff - previousDiff)) * (ratio - previousRatio);
            if previousDiff >= 0 and diff < 0:
                if horizontalCrossover == None:
                    horizontalCrossover = previousRatio + ((0 - previousDiff) / (diff - previousDiff)) * (ratio - previousRatio);
        previousDiff = diff;
        previousRatio = ratio;
        if verticalCrossover != None and horizontalCrossover != None:
            break;
    if verticalCrossover == None or horizontalCrossover == None:
        print("error finding crossover points in file " + fileName + " layout " + layoutAlgorithm);
        exit(1);
    return (float(verticalCrossover), float(horizontalCrossover));


# A helper method to interpolate x values (number of holes) given a success rate.
# y[n] defines the success rate when x[n] holes are dug.
# The given success rate may be between y[a] and y[a-1] for some a,
# hence the need for interpolation. Returns:
#   x[a-1] + (((successRate - y[a-1]) / (y[a] - y[a-1])) * (x[a] - x[a-1]))
def __interpolate(successRate:float, x:list, y:list) -> float:
        successIndex = 0;
        while (y[successIndex] < successRate):
            successIndex = successIndex + 1;
            if successIndex >= len(y):
                return -1;
        if successIndex == 0:
            successA = 0;
            holesA = 0;
        else:
            successA = y[successIndex-1];
            holesA = x[successIndex-1]
        successB = y[successIndex];
        holesB = x[successIndex];
        percentage = (successRate - successA) / (successB - successA);
        return holesA + percentage * (holesB - holesA);


# Calculates the maximum and mean break-even ratios given data on a small hole experiment
# and a big hole experiment. For example a mean break-even ratio of 1.6 indicates the small
# hole strategy outperforms the big hole strategy when 1.6 small holes are dug for each
# big hole (on average). Similarly for the maximum.
# Break-even ratios are calculated for each success rate (from 0 to 99), excluding
# 100% as it sometimes leads to anomalous values. For each success rate
# the corresponding number of big holes and of small holes is found (these values
# are interpolated as there won't be an exact match to the success rate).
# The break-even ratio is then number-of-small-holes / number-of-big-holes.
# The filenames should refer to csv files, produced by the ExperimentRunner in Holes.py.
# Returns (maximum, mean).
def breakEvenRatios(smallHolesFileName:str, bigHolesFileName:str) -> tuple[float, float]:
    xsmall = [];
    ysmall = [];

    xbig = [];
    ybig = [];

    # read the data from csv files
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

    # success arrays are for success rates 1 to 99, so s[0] reflects success rate of 1
    smallHoles = [];
    bigHoles = [];

    # for each success rate find the number of big holes with that success rate
    # and the number of small holes for that success rate, interpolating values
    # if necessary. We consider 1% to 99% success rates as requiring 100% sometimes
    # leads to anomalous values
    for i in range(0, 99):
        successRate = i + 1;
        smallHolesVal = __interpolate(successRate, xsmall, ysmall);
        if smallHolesVal == -1:
            break;
        smallHoles.append(smallHolesVal);
        bigHolesVal = __interpolate(successRate, xbig, ybig);
        if bigHolesVal != -1:
            bigHoles.append(bigHolesVal);
    breakEven = [];
    i = 0;
    while (i < len(smallHoles) and i < len(bigHoles)):
        #print(str(i+1) + " " + str(smallHoles[i] / bigHoles[i]))
        breakEven.append(smallHoles[i] / bigHoles[i]);
        i = i + 1;
    maxBE = np.max(breakEven);
    meanBE = np.mean(breakEven);
    return maxBE, meanBE;


# Interpolates values for success based on the given desired number of holes (hole).
# Data for number of holes and their respective success rates are given by
# the two lists. If we run out of holes a success of 100 is returned.
def interpolateHoles(hole:int, holes:list, success:list) -> float:
    holeIndex = 0;
    while (holes[holeIndex] < hole):
        holeIndex = holeIndex + 1;
        if holeIndex >= len(holes):
            return 100;
    if holes[holeIndex] == hole:
        return success[holeIndex];
    if holeIndex == 0:
        successA = 0;
        holesA = 0;
    else:
        successA = success[holeIndex-1];
        holesA = holes[holeIndex-1]
    successB = success[holeIndex];
    holesB = holes[holeIndex];
    percentage = (hole - holesA) / (holesB - holesA);
    return successA + percentage * (successB - successA);


# Inerpolates values for holes based on the desired success rate.
# Data for success rates and their respective number of holes are given by
# the two lists.
def interpolateSuccessRate(successRate:float, successRates:list, holes:list) -> float:
    successRateIndex = 0;
    while(successRates[successRateIndex] < successRate):
        successRateIndex = successRateIndex + 1;
        if successRateIndex >= len(successRates):
            print("error: success rate not found");
            exit(1);
    if round(successRates[successRateIndex], 2) == round(successRate, 2):
        return holes[successRateIndex];
    if successRateIndex == 0:
        holesA = 0;
        successRateA = 0;
    else:
        holesA = holes[successRateIndex - 1];
        successRateA = successRates[successRateIndex - 1];
    holesB = holes[successRateIndex];
    successRateB = successRates[successRateIndex];
    percentage = (successRate - successRateA) / (successRateB - successRateA);
    return holesA + percentage * (holesB - holesA);


# Computes the "area under the curve" of a graph defined by data in
# the given file, which should contain success rates for a layout algorithm
# over a range of number of holes (from 1 to a maximum value).
# This area is approximated by summing the y values (success rates) across
# all number of holes from one to maximumHoles. Where x values are
# missing (not all numbers of holes are compatible with every layout
# algorithm), values are interpolated. If the data stops before
# maximumHoles is reached (as it reaches 100% success rate earlier),
# the remaining number of holes are counted as having a 100% success rate.
# If suppressWarning is False, a warning will be printed if we encounter
# numbers of holes greater than maximumHoles.
def areaUnderCurve(csvFileName:str, maximumHoles = 6000, suppressWarning:bool = False) -> float:
    csvFile = open("data/"+csvFileName, 'r');
    lines = csv.DictReader(csvFile, delimiter=',', skipinitialspace=True);
    holes = [];
    success = [];
    for row in lines:
        holes.append(int(row["actualholes"]));
        success.append(float(row["successrate"]));
    if not suppressWarning and holes[len(holes)-1] > maximumHoles:
        print("error: got more than " + str(maximumHoles) + " holes: " + str(holes[len(holes)-1]) + " file " + csvFileName);
    area = 0;
    for hole in range(1, maximumHoles+1):
        successRate = interpolateHoles(hole, holes, success);
        area += successRate;
    return area;


# Returns the absolute maximum difference in success between layoutAlgorithm1 and layoutAlgorithm2
# for the given treasure dimensions, fieldSize, and siteArea. Data are assumed to exist in
# the data/drilldown directory. It is also assumed that the data for each layout algorithm
# reach 100% success rate at the final number of holes.
def getMaximumDifferenceInSuccessLayout(fieldSize:int, siteArea:int, layoutAlgorithm1:str, layoutAlgorithm2:str, treasureWidth:float, treasureHeight:float, maxHoles = None) -> float:
    fileStart = "data/drilldown/" + str(treasureWidth) + "x" + str(treasureHeight) + "rectangle";
    fileEnd = "fieldsize" + str(fieldSize) + " siteArea" + str(siteArea) + ".csv"
    csvFile1 = open(fileStart + " " + layoutAlgorithm1 + " " + fileEnd);
    csvFile2 = open(fileStart + " " + layoutAlgorithm2 + " " + fileEnd);

    lines1 = csv.DictReader(csvFile1, delimiter=',', skipinitialspace=True);
    lines2 = csv.DictReader(csvFile2, delimiter=',', skipinitialspace=True);

    holes1 = [];
    successes1 = [];
    for row1 in lines1:
        holes1.append(int(row1["actualholes"]));
        successes1.append(float(row1["successrate"]));
    holes2 = [];
    successes2 = [];
    for row2 in lines2:
        holes2.append(int(row2["actualholes"]));
        successes2.append(float(row2["successrate"]));
    
    holeLimit = max(holes1[len(holes1) - 1], holes2[len(holes2) - 1]);
    if maxHoles != None:
        holeLimit = maxHoles;
    
    if maxHoles == None and (successes1[len(holes1) - 1] != 100 or successes2[len(holes2) - 1] != 100):
        print("error: data don't go to 100% success rate");
        exit();
    
    if maxHoles != None and \
    (   (holes1[len(holes1) - 1] < maxHoles and successes1[len(holes1) - 1] != 100)  or \
        (holes2[len(holes2) - 1] < maxHoles and successes2[len(holes2) - 1] != 100) \
    ):
        print("error: data don't reach maxHoles");
        exit();

    maximum = 0;
    for hole in range(holeLimit + 1):
        if hole > holes1[len(holes1) - 1]:
            success1 = 100;
        else:
            success1 = interpolateHoles(hole, holes1, successes1);
        if hole > holes2[len(holes2) - 1]:
            success2 = 100;
        else:
            success2 = interpolateHoles(hole, holes2, successes2);
        diff = abs(success2 - success1);
        if diff > maximum:
            maximum = diff;

    return maximum;
