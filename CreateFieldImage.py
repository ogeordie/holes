# Holes

# Holes is a program for simulations of archaeological excavations.

# Copyright 2024 Geordie Oakes

# This program is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License v3 as published by the Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License v3 for more details.

# You should have received a copy of the GNU General Public License along with this program.
# If not, see https://www.gnu.org/licenses/gpl-3.0.html.


# This file is a utility that produces a graphical display of a Field with holes and treasure.
# Files can be generated with Holes.py.

# To use paste the file name in the displayField() method (search "set file name")

# File format:
# 
# The first line is "intersect" or "realworld" (see Holes.py for more detail on these).
# The second line is the field size: <x> <y>
#
# If intersect:
#   the third line starts "circularTreasure:" or "rectangularTreasure:" followed
#   by the treasure dimensions:
#       <centreX> <centreY> <radius> for circular
#       <centreX> <centreY> <width> <height> for rectangular
#
# If realworld:
#   the third line starts "realworldtreasure" followed by the dimensions
#   <topLeftX> <topLeftY> <bottomRightX> <bottomRightY>
# The next lines begin "artefact:" followed by <x-position> <y-position>, for each artefact
#
# For all cases, the remaining lines begin "hole:" followed by
# <centreX>, <centreY>, <width> <height>
# then "True" if the hole uncovers treasure otherwise "False".

# This code was only tested using the limited number of parameters explored in the article.
# It may not be correct in all circumstances.

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line, Rectangle, Point
from kivy.core.window import Window
from kivy.metrics import Metrics


class CreateFieldImage(Widget):
    def __init__(self,  **kwargs):
        super().__init__(**kwargs);
        self.displayFactor = 0;

        self.displayField();
#        self.export_as_image().save("square.png");
    
    def convertPoint(self, x, y):
        p = self.convertSize(x, y);
        return (p[0], self.dimensions[1] - 1 - p[1]);

    def continuousConvertPoint(self, x, y):
        p = self.convertSize(x, y);
        return (p[0], self.dimensions[1] - p[1]);

    def convertSize(self, x, y):
        return (x*self.displayFactor, y*self.displayFactor);

    def displayField(self):
        # set file name:  change this to refer to the file with field data
        filename = "\
realWorldField 100 holesize 1 holes 120 HexagonalLikePlayer\
"
        self.f = open("" + filename, 'r');
        fieldType = self.f.readline();
        dimensionsLine = self.f.readline();
        dimensionsTokens = dimensionsLine.split();
        biggestSide = int(dimensionsTokens[0]);
        if int(dimensionsTokens[1]) > biggestSide:
            biggestSide = int(dimensionsTokens[1]);
        self.displayFactor = 10 / (biggestSide/100);
        self.dimensions = self.convertSize(int(dimensionsTokens[0]), int(dimensionsTokens[1]));
        Window.size = (self.dimensions[0]/Metrics.density, self.dimensions[1]/Metrics.density);
        Window.clearcolor = (1, 1, 1);
        Window.top = 50;
        Window.left = 50;
        
        with self.canvas:
            Color(0, 0, 0);
            Line(points=[0,0,1000,0, 1000, 1000, 0, 1000, 0,0], width=2);
        
        with self.canvas:
            Color(1, 1, 1);
            Rectangle(pos=(0,0), size=(1000, 1000));

        if fieldType.startswith("realworld"):
            self.displayRealWorldField();
        elif fieldType.startswith("intersect"):
            self.displayIntersectField();
        else:
            print("error: type of field not recognized");
    
    # display a field containing real world data on artefact distribution
    def displayRealWorldField(self):
        with self.canvas:
            Color(0, 0, 0);
            Line(points=[0, self.dimensions[1], self.dimensions[0], self.dimensions[1]]);
     
            treasureLine = self.f.readline();
            treasureLineTokens = treasureLine.split();
            if treasureLineTokens[0].startswith("realworldtreasure"):
                Color(0,0,0);
                bottomLeft = self.continuousConvertPoint(float(treasureLineTokens[1]), float(treasureLineTokens[2]));
                topRight = self.continuousConvertPoint(float(treasureLineTokens[3]), float(treasureLineTokens[4]));
                size = topRight[0] - bottomLeft[0], topRight[1] - bottomLeft[1];
                Line(rectangle=(bottomLeft[0], bottomLeft[1], size[0], size[1]));#(pos=(topLeft[0], bottomRight[1]), size = size);
            line = self.f.readline();
            while len(line) > 0:
                lineTokens = line.split();
                Color(0,1,0);
                if (lineTokens[0].startswith("artefact")):
                    x = float(lineTokens[1]);
                    y = float(lineTokens[2]);
                    point = self.continuousConvertPoint(x, y);
                    Point(points=point, pointsize=0.5);
                elif (lineTokens[0].startswith("hole")):
                    if lineTokens[5].startswith("True"):
                        Color(1, 0, 0);
                    else:
                        Color(0, 0, 0);
                    thePos = self.continuousConvertPoint(float(lineTokens[1]), float(lineTokens[2]));
                    theSize = (float(lineTokens[3])*self.displayFactor, float(lineTokens[4])*self.displayFactor);
                    posX = thePos[0] - theSize[0]/2;
                    posY = thePos[1] - theSize[1]/2;
                    Rectangle(pos=(posX, posY), size=theSize);
                line = self.f.readline();

    # display a field containing circular or rectangular treasure
    def displayIntersectField(self):
        with self.canvas:
            Color(0, 0, 0);
            Line(points=[0, self.dimensions[1], self.dimensions[0], self.dimensions[1]]);

            treasureLine = self.f.readline();
            treasureLineTokens = treasureLine.split();
            if treasureLineTokens[0].startswith("circularTreasure"):
                Color(0, 1, 0);
                centre = self.continuousConvertPoint(float(treasureLineTokens[1]), float(treasureLineTokens[2]));
                radius = float(treasureLineTokens[3]) * self.displayFactor;

                bottomLeftX = centre[0] - radius;
                bottomLeftY = centre[1] - radius;
                Ellipse(pos=(bottomLeftX, bottomLeftY), size=(radius*2, radius*2));
            else:
                Color(0, 1, 0);
                centre = self.continuousConvertPoint(float(treasureLineTokens[1]), float(treasureLineTokens[2]));
                size = (float(treasureLineTokens[3])*self.displayFactor, float(treasureLineTokens[4])*self.displayFactor);
                posX = centre[0] - size[0]/2;
                posY = centre[1] - size[1]/2;
                Rectangle(pos=(posX, posY), size = size);

            line = self.f.readline();
            while len(line) > 0:
                lineTokens = line.split();
                if not(lineTokens[0].startswith("hole")):
                    print("ERROR: expecting hole line");
                    exit();
                if lineTokens[5].startswith("True"):
                    Color(1, 0, 0);
                else:
                    Color(0, 0, 0);
                thePos = self.continuousConvertPoint(float(lineTokens[1]), float(lineTokens[2]));
                theSize = (float(lineTokens[3])*self.displayFactor, float(lineTokens[4])*self.displayFactor);
                posX = thePos[0] - theSize[0]/2;
                posY = thePos[1] - theSize[1]/2;
                Rectangle(pos=(posX, posY), size=theSize);
                line = self.f.readline();

class FieldApp(App):
    def build(self):
        self.widget = CreateFieldImage()
        #self.widget.export_to_png("balck.png");
        return self.widget;

    def export(self):
        self.widget.export_to_png('layout paper/halton.png')

if __name__ == '__main__':
    app = FieldApp();
    app.run();
    app.export();

    