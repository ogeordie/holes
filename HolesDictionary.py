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

# See the "README.md" file for information, and installation and usage instructions.

# This file contains:
#    - a dictionary of layout algorithm names and case study elongation descriptions,
#      going from the abbreviations used in the code to the proper names used in graphs and tables,
#    - a method returning text for treasure orientations given the rotation value,
#    - methods returning the names of subdirectories of the data and graphs directory to use
#      for various experimental data, graphs, and tables.


class HolesDictionary:
    
    # Look up an abbreviation, capitalising the returned name if capitalise is True
    @staticmethod
    def lookup(abbreviation:str, capitalise:bool = False) -> str:
        dict = {
            "hexlike" : "hexagonal-like",
            "hex" : "hexagonal",
            "random" : "random",
            "halton" : "halton", 
            "staggerXY" : "staggerXY",
            "randomisedStaggerXY sd8" : "randomisedStaggerXY",
            "randomisedStaggerXY8" : "randomisedStaggerXY",
            "randomisedStaggerXY" : "randomisedStaggerXY",
            "rSXY6" : "rSXY6",
            "rSXY4" : "rSXY4",
            "lowelongation" : "Low Elongation",
            "moderateelongation" : "Moderate Elongation",
            "highelongation" : "High Elongation"
        }
        result = dict[abbreviation];
        if result == None:
            print("error: abbreviation " + abbreviation + " not found in dictionary");
            return abbreviation;
        if capitalise:
            return result[0].upper() + result[1:];
        else:
            return str(result);

    # Return text for a treasure's orientation based on the numerical orientation
    @staticmethod
    def orientationLabel(orientation:float) -> str:
        if orientation == 0:
            return "Horizontal";
        if orientation == 90:
            return "Vertical";
        return (str(orientation) + " Degree");

    @staticmethod
    def getSuccessDirectoryName() -> str:
        return "success";

    @staticmethod
    def getSummaryDirectoryName() -> str:
        return "summary";

    @staticmethod
    def getCaseStudiesDirectoryName() -> str:
        return "casestudies";

    @staticmethod
    def getLargeRatioDirectoryName() -> str:
        return "largeratio";

    @staticmethod
    def getSmallNumHolesDirectoryName() -> str:
        return "smallnumholes";

    @staticmethod
    def getRotationDirectoryName() -> str:
        return "rotation";

    @staticmethod
    def getCircularDirectoryName() -> str:
        return "circular";

    @staticmethod
    def getSizeMattersDirectoryName() -> str:
        return "sizematters"

    @staticmethod
    def getRandomisedTreasureDirectoryName() -> str:
        return "randomtreasure"
    