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

# This file contains a dictionary of layout algorithm names, going from the abbreviations
# used in the code to the proper names used in graphs and tables.

import string

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
            "rSXY4" : "rSXY4"
        }
        result = dict[abbreviation];
        if result == None:
            print("error: abbreviation " + abbreviation + " not found in dictionary");
            return abbreviation;
        if capitalise:
            return result[0].upper() + result[1:];
        else:
            return str(result);

