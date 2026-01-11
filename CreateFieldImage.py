# Holes

# Holes is a program for simulations of archaeological excavations.

# Copyright 2024-2026 Geordie Oakes

# This program is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License v3 as published by the Free Software Foundation.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License v3 for more details.

# You should have received a copy of the GNU General Public License along with this program.
# If not, see https://www.gnu.org/licenses/gpl-3.0.html.


# This file is a utility that produces a graphical image of a Field with holes and treasure.
# Files can be generated with Experiment.printExperiment() in Holes.py, which is also called
# by the LayoutExperiments.py and Experiments.py when goPrintExperiments is set to True.
# These files are stored in the printedFields directory, and the output image is alse
# saved to this directory.

# To use, paste the file name in the filename variable at the top of the code in this file
# (search "set file name").

# File format:
# 
# The first line is "intersect" or "realworld" (see Holes.py for more detail on these).
# The second line is the field size: <x> <y>
#
# If first line is "intersect":
#   the third line starts "circularTreasure:", "rectangularTreasure:", or "polygonTreasure:" followed
#   by the treasure dimensions:
#       <centreX> <centreY> <radius> for circular
#       <centreX> <centreY> <width> <height> for rectangular
#       <topLeftX> <topLeftY> <bottomRightX> <bottomRightY>
#   and for polygonTreasure, one line for each defining point:
#        point: <polygonPointX> <polygonPointY>
#
# If first line is "realworld":
#   the third line starts "realworldtreasure" followed by the bounding rectangle dimensions:
#       <topLeftX> <topLeftY> <bottomRightX> <bottomRightY>
# The next lines begin "artefact:" followed by <x-position> <y-position>, for each artefact
#
# For all cases, the remaining lines begin "hole:" followed by:
#   <centreX>, <centreY>, <width> <height>
# then "True" if the hole uncovers treasure otherwise "False".

# This code was only tested using the limited number of parameters explored in the article.
# It may not be correct in all circumstances.

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line, Rectangle, Point, Mesh
from kivy.core.window import Window
from kivy.metrics import Metrics
from kivy.uix.label import Label, CoreLabel
from kivy.utils import get_color_from_hex
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout

# set file name:  change this to refer to the file with field data you want
# to display. Leave the printedFields directory in the file name.
# The Image will be saved as "printedFields/<filename>.png".
filename = "printedFields/\
intersectField 100 holesize 0.5 treasure 10x10 holes 42 HexagonalLike\
"

# A kivy Widget that draws the holes and treasure defined in filename (above)
# on the canvas.
class CreateFieldImage(RelativeLayout):
    def __init__(self,  **kwargs):
        super().__init__(**kwargs);
        self.displayFactor = 0;

        self.displayField();

    # converts a point as defined in the input file to a point on the canvas
    def continuousConvertPoint(self, x, y):
        p = self.convertSize(x, y);
        return (p[0], self.dimensions[1] - p[1]);

    # scales the point (x,y) to the dimensions of the canvas
    def convertSize(self, x, y):
        return (x*self.displayFactor, y*self.displayFactor);

    # sets up the dimensions of the window, draws the background on the canvas,
    # and delegates drawing of the field to the appropriate method
    def displayField(self):
        self.f = open("" + filename, 'r');
        fieldType = self.f.readline();
        dimensionsLine = self.f.readline();
        dimensionsTokens = dimensionsLine.split();
        biggestSide = int(dimensionsTokens[0]);
        if int(dimensionsTokens[1]) > biggestSide:
            biggestSide = int(dimensionsTokens[1]);
        self.displayFactor = 10 / (biggestSide/100);
        self.dimensions = self.convertSize(int(dimensionsTokens[0]), int(dimensionsTokens[1]));

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
            treasureLine = self.f.readline();
            treasureLineTokens = treasureLine.split();
            if treasureLineTokens[0].startswith("realworldtreasure"):
                Color(0,0,0);
                bottomLeft = self.continuousConvertPoint(float(treasureLineTokens[1]), float(treasureLineTokens[2]));
                topRight = self.continuousConvertPoint(float(treasureLineTokens[3]), float(treasureLineTokens[4]));
                size = topRight[0] - bottomLeft[0], topRight[1] - bottomLeft[1];
                Line(rectangle=(bottomLeft[0], bottomLeft[1], size[0], size[1]));
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
                    theSize = self.convertSize(float(lineTokens[3]), float(lineTokens[4]));
                    posX = thePos[0] - theSize[0]/2;
                    posY = thePos[1] - theSize[1]/2;
                    Rectangle(pos=(posX, posY), size=theSize);
                line = self.f.readline();

    # display a field containing circular, rectangular, or polygon treasure
    def displayIntersectField(self):
        with self.canvas:
            treasureLine = self.f.readline();
            treasureLineTokens = treasureLine.split();
            if treasureLineTokens[0].startswith("circularTreasure"):
                Color(0, 1, 0);
                centre = self.continuousConvertPoint(float(treasureLineTokens[1]), float(treasureLineTokens[2]));
                radius = float(treasureLineTokens[3]) * self.displayFactor;

                bottomLeftX = centre[0] - radius;
                bottomLeftY = centre[1] - radius;
                Ellipse(pos=(bottomLeftX, bottomLeftY), size=(radius*2, radius*2));
                nextLine = self.f.readline();
            elif treasureLineTokens[0].startswith("rectangularTreasure"):
                Color(0, 1, 0);
                centre = self.continuousConvertPoint(float(treasureLineTokens[1]), float(treasureLineTokens[2]));
                size = self.convertSize(float(treasureLineTokens[3]), float(treasureLineTokens[4]));
                posX = centre[0] - size[0]/2;
                posY = centre[1] - size[1]/2;
                Rectangle(pos=(posX, posY), size = size);
                nextLine = self.f.readline();
            else:
                # polygon treasure bounds
                Color(0,0,0);
                bottomLeft = self.continuousConvertPoint(float(treasureLineTokens[1]), float(treasureLineTokens[2]));
                topRight = self.continuousConvertPoint(float(treasureLineTokens[3]), float(treasureLineTokens[4]));
                size = topRight[0] - bottomLeft[0], topRight[1] - bottomLeft[1];
                Line(rectangle=(bottomLeft[0], bottomLeft[1], size[0], size[1]));
                # polygon treasure shape
                nextLine = self.printPolygonShape();

            line = nextLine;
            while len(line) > 0:
                lineTokens = line.split();
                if not(lineTokens[0].startswith("hole")):
                    print("ERROR: expecting hole line");
                    exit();
                if lineTokens[5].startswith("True"):
                    Color(1, 0, 0);
                    pass;
                else:
                    Color(0, 0, 0);
                thePos = self.continuousConvertPoint(float(lineTokens[1]), float(lineTokens[2]));
                theSize = self.convertSize(float(lineTokens[3]), float(lineTokens[4]));
                posX = thePos[0] - theSize[0]/2;
                posY = thePos[1] - theSize[1]/2;
                Rectangle(pos=(posX, posY), size=theSize);

                # Code to produce coordinate labels below holes
                # mylabel = CoreLabel(text="(" + str(round(thePos[0]/self.displayFactor)) + "," + str(round(thePos[1]/self.displayFactor)) + ")", font_size=20, color=(0, 0, 0, 1))
                # mylabel.refresh()
                # texture = mylabel.texture
                # texture_size = list(texture.size)
                # rectPos = (posX - texture.size[0]/2 + 5, posY - (theSize[1]*2+5));
                # Rectangle(texture=texture, size=texture_size, pos=rectPos);

                line = self.f.readline();

    # draws a polygon treasure on the canvas.
    # Returns the first line of the holes definitions in the input file.
    def printPolygonShape(self) -> str:
        verticesList = [];
        index = 0;
        indicesList = [];
        line = self.f.readline();
        while len(line) > 0:
            lineTokens = line.split();
            if (line.startswith("point")):
                x = lineTokens[1];
                y = lineTokens[2]
                converted = self.continuousConvertPoint(float(x), float(y));
                verticesList.append(converted[0]);
                verticesList.append(converted[1]);
                verticesList.append(1);
                verticesList.append(1);
                indicesList.append(index);
                index = index + 1;
            else:
                with self.canvas:
                    Color(0, 1, 0)
                    #indicesList.append(0);
                    Mesh(vertices = verticesList, indices = indicesList, mode="triangle_fan");
                return line;
            line = self.f.readline();

# A widget that surrounds the CreateFieldImage widget with a border
class ContainerWidget(FloatLayout):
    def __init__(self, **kwargs):
        
        super().__init__(**kwargs)
        Window.size = (1004/Metrics.density, 1004/Metrics.density);
        Window.top = 50;
        Window.left = 50;
        with self.canvas:
            Color(0, 0, 0);
            Line(points=[0,0,1004,0, 1004, 1004, 0, 1004, 0,0], width=2);


        self.add_widget(CreateFieldImage(pos=(2,2)));

# A kivy app that creates the CreateFieldImage widget
class FieldApp(App):
    def build(self):
        self.widget = ContainerWidget()
        return self.widget;

    # saves the graphical field as a png file
    def export(self):
        self.widget.export_to_png(filename + '.png')

if __name__ == '__main__':
    app = FieldApp();
    app.run();
    app.export();
