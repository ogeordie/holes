# Holes

# Holes is a program for simulations of archaeological excavations.

# Copyright 2024 Geordie Oakes

# This program is free software: you can redistribute it and/or modify it under the terms of 
# the GNU General Public License v3 as published by the Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
# See the GNU General Public License v3 for more details.

# You should have received a copy of the GNU General Public License along with this program. 
# If not, see https://www.gnu.org/licenses/gpl-3.0.html.


# See the "README.md" file for information, and installation and usage instructions.


# This file contains code used to populate the tables, finding break-even ratios
# and maximum differences in success rates between hole digging strategies.

import csv
import numpy as np

# Not used, just testing that maximumDifferenceInSuccess() is correct
# def altMaxDiff(smallHolesFileName:str, bigHolesFileName:str, ratio:int):
#     xsmall = [];
#     ysmall = [];

#     xbig = [];
#     ybig = [];

#     # read data from the csv file
#     smallCsvFile = open("data/"+smallHolesFileName, 'r');
#     bigCsvFile = open("data/"+bigHolesFileName, 'r');
#     smallLines = csv.DictReader(smallCsvFile, delimiter=',', skipinitialspace=True);
#     bigLines = csv.DictReader(bigCsvFile, delimiter=',', skipinitialspace=True);
#     maxHole1x1 = 0;
#     for row in smallLines:
#         if row['successrate'] != '':
#             xsmall.append(int(row['actualholes']));
#             ysmall.append(float(row['successrate']));
#             smallMaxHole = int(row['actualholes']);
#     smallCsvFile.close();

#     for row in bigLines:
#         if (row['successrate']) != '':
#             xbig.append(int(row['actualholes']))
#             ybig.append(float(row['successrate']))
#             bigMaxHole = int(row['actualholes'])
#     bigCsvFile.close();

#     maxDiff = 0;
#     for row in range(0, len(xbig)):
#         bigHoles = xbig[row];
#         # find small hole matching bigHole
#         i = 0;
#         if (i < len(xsmall)):
#             while (xsmall[i] < ratio * bigHoles):
#                 i = i + 1;
#                 if (i >= len(xsmall)):
#                     break;
#             if (i >= len(xsmall)):
#                 break;
#             if (i == 0):
#                 firstSmallSuccess = 0;
#                 firstSmallHoles = 0;
#             else:
#                 firstSmallSuccess = ysmall[i-1];
#                 firstSmallHoles = xsmall[i-1]
#             secondSmallSuccess = ysmall[i];
#             secondSmallHoles = xsmall[i];
#             # interpolate holes
#             if secondSmallHoles == 0 and firstSmallHoles == 0:
#                 percentage = 0;
#             else:
#                 percentage = ((ratio * bigHoles) - firstSmallHoles) / (secondSmallHoles - firstSmallHoles);
#             smallSuccess = firstSmallSuccess + percentage * (secondSmallSuccess - firstSmallSuccess);
#             diff = smallSuccess - ybig[row];
#             if abs(diff) > abs(maxDiff):
#                 maxDiff = diff;
#                 maxAtBigHoles = bigHoles;
#             print(str(diff));
#     #print(str(smallHolesFileName.split(' ', 1)[0]) + ": ratio = " + str(ratio) + ", maximum difference = " + str(round(maxDiff)) + " at " + str(maxAtBigHoles) + " big holes");
#     return maxDiff;


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

    # read data from the csv file
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

    # Fill in xbig and ybig with 100% to match length of xsmall.
    # This is unnecesary as differences will decrease from the number
    # of holes n at which ybig[n] = 100
    # if (len(xbig) < len(xsmall)):
    #     for j in range(len(xbig), len(xsmall)):
    #         xbig.append(xsmall[j]);
    #         ybig.append(100);

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
            #print(str(diff));
    #print(str(smallHolesFileName.split(' ', 1)[0]) + ": ratio = " + str(ratio) + ", maximum difference = " + str(round(maxDiff)) + " at " + str(maxAtBigHoles) + " big holes");
    return maxDiff;

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