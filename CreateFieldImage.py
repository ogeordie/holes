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


# This file is a utility that produces a graphical image of a Field with holes and treasure
# using the kivy library.
# Files can be generated with ExperimentRunner.printExperiment() in ExperimentRunner.py,
# which is also called by LayoutExperiments.py and SizeMattersExperiments.py when
# goPrintExperiments is set to True. Such files generally have a hpf suffix.
# These files are stored in the printedFields directory, and the generated image is also
# saved to this directory.

# To use, choose a mode at the top of the code in this file (search "set mode"). The mode can
# either be allNewHPFFiles or onlyNamedFile. Uncomment the mode you want and comment out
# the other one. The allNewHPFFiles mode will display and create .png files for every .hpf
# file in the printedFields directory that doesn't have a corresponding .png file that is more
# recent. Each window displayed must be closed individually to cause the file to be saved.
# The onlyNamedFile mode will only display and create a png file for the file named in
# the filename variable. To use this second mode, paste the file name in the filename variable
# just beneath the mode variable (search "set file name").

# File format:
# 
# The first line is "field".
# The second line is the field size: <x> <y>, though we only support square fields.
#
# The third line is the treasure type, "rectangularTreasure", "polygonTreasure", "circularTreasure"
# or "realworldTreasure"
#
# If third line is "rectangularTreasure" or "polygonTreasure":
#   the fourth line is the treasure bounding box: <x1> <y1> <x2> <y2>
#   then one line for each vertex of the shape: "point:" <x> <y>
# If the third line is "circularTreasure":
#   the fourth line is the treasure dimensions:
#       <centreX> <centreY> <radius>
# If the third line is "realworldTreasure":
#   the fourth line is the treasure bounding box: <x1> <y1> <x2> <y2>
#   then one line for each artefact: "artefact:" <x> <y>
#
# For all cases, the remaining lines begin "hole:" followed by:
#   <centreX>, <centreY>, <width> <height>
# then "True" if the hole uncovers treasure otherwise "False".

# This code was only tested using the limited number of parameters explored in the article.
# It may not be correct in all circumstances.

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line, Rectangle, Point, Mesh, PushMatrix, PopMatrix, Rotate
from kivy.graphics.tesselator import Tesselator, TYPE_POLYGONS, WINDING_POSITIVE, WINDING_ODD, WINDING_NONZERO
from kivy.core.window import Window
from kivy.metrics import Metrics
from kivy.uix.label import Label, CoreLabel
from kivy.utils import get_color_from_hex
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.config import Config
from kivy.uix.popup import Popup
from kivy.uix.label import Label
import os
from pathlib import Path


# This mode displays and generates png files for any hpf files in printedFields
# directory that don't have a corresponding png file that is more recent:
allNewHPFFiles = 1;
# This mode displays and generates a png file for the file named in filname (below):
onlyNamedFile = 2;

# set mode:
mode = allNewHPFFiles;
#mode = onlyNamedFile;

# set file name: change this to refer to the file with field data you want
# to display when the mode is onlyNamedFile. Leave the printedFields directory in the file name.
# The Image will be saved as "printedFields/<filename>.png".
filename = "printedFields/\
rectangle 20x5 orientation 0 Hexagonal-like holes 120 fieldsize 100 holesize 0.5\
.hpf"

# A kivy Widget that draws the holes and treasure defined in filename (above)
# on the canvas.
class CreateFieldImage(RelativeLayout):
    def __init__(self,  fileName:str, **kwargs):
        super().__init__(**kwargs);
        self.fileName = fileName;
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
        self.f = open("" + self.fileName, 'r');
        fieldLine = self.f.readline();
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
        
        treasureTypeLine = self.f.readline();
        treasureTokens = treasureTypeLine.split();
        if treasureTokens[0].startswith("realworldTreasure"):
            self.displayRealWorld();
        else:
            t = treasureTokens[0];
            if not t.startswith("polygonTreasure") and not t.startswith("circularTreasure") and not t.startswith("rectangularTreasure"):
                print("error: type of field not recognized");
            self.displayDefault(t);
        self.f.close();
    
    # display a field containing real world data on artefact distribution
    def displayRealWorld(self):
        with self.canvas:
            treasureLine = self.f.readline();
            treasureLineTokens = treasureLine.split();
            Color(0,0,0);
            bottomLeft = self.continuousConvertPoint(float(treasureLineTokens[0]), float(treasureLineTokens[1]));
            topRight = self.continuousConvertPoint(float(treasureLineTokens[2]), float(treasureLineTokens[3]));
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
    def displayDefault(self, treasureType:str):
        with self.canvas:
            if treasureType.startswith("circularTreasure"):
                treasureLine = self.f.readline();
                treasureLineTokens = treasureLine.split();
                Color(0, 1, 0);
                centre = self.continuousConvertPoint(float(treasureLineTokens[0]), float(treasureLineTokens[1]));
                radius = float(treasureLineTokens[2]) * self.displayFactor;

                bottomLeftX = centre[0] - radius;
                bottomLeftY = centre[1] - radius;
                Ellipse(pos=(bottomLeftX, bottomLeftY), size=(radius*2, radius*2));
                nextLine = self.f.readline();
            elif treasureType.startswith("rectangularTreasure") or treasureType.startswith("polygonTreasure"):
                treasureLine = self.f.readline();
                treasureLineTokens = treasureLine.split();
                # polygon treasure bounds
                Color(0,0,0);
                bottomLeft = self.continuousConvertPoint(float(treasureLineTokens[0]), float(treasureLineTokens[1]));
                topRight = self.continuousConvertPoint(float(treasureLineTokens[2]), float(treasureLineTokens[3]));
                size = topRight[0] - bottomLeft[0], topRight[1] - bottomLeft[1];
                Line(rectangle=(bottomLeft[0], bottomLeft[1], size[0], size[1]));
                # polygon treasure shape
                nextLine = self.printPolygonShape();

            line = nextLine;
            while len(line) > 0:
                lineTokens = line.split();
                if not(lineTokens[0].startswith("hole")):
                    print("ERROR: expecting hole line in", self.fileName);
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
        lineList = [];
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
                lineList.append(converted[0]);
                lineList.append(converted[1]);
            else:
                with self.canvas:
                    Color(0.02, 0.48, 0.32, 1)
                    Line(points=lineList, width = 1.25)
                return line;
            line = self.f.readline();


# A widget that surrounds the CreateFieldImage widget with a border
class ContainerWidget(FloatLayout):
    def __init__(self, fileName, **kwargs):
        
        super().__init__(**kwargs)
        Window.size = (1004/Metrics.density, 1025/Metrics.density);
        Window.top = 50;
        Window.left = 50;
        with self.canvas:
            Color(1, 1, 1, 1);
            Rectangle(pos = (0,0), size = (1004, 1025));
            Color(0, 0, 0);
            Line(points=[0,1003,1003,1004], width = 1.5);
            Line(points=[0, 1000, 0,0,1004,0, 1004, 1000], width=3);

        self.add_widget(CreateFieldImage(fileName, pos=(2,2)));
        with self.canvas:
            Color(1, 1, 1, 1);
            Rectangle(pos = (0, 1004), size = (1004, 21));
        filePath = Path(fileName);
        l = Label(text = filePath.stem, color = (0,0,0,1), font_size = 14, pos_hint = {"center_x":0.5, "center_y":0.99});
        self.add_widget(l);


# A kivy app that creates the CreateFieldImage widget
class FieldApp(App):
    def __init__(self, fileName):
        super().__init__();
        self.fileName = fileName;
    
    def build(self):
        self.widget = ContainerWidget(self.fileName);
        self.title = self.fileName;
        return self.widget;

    # saves the graphical field as a png file
    def export(self):
        stem = os.path.splitext(self.fileName)[0];
        self.widget.export_to_png(stem + '.png');


# A message to display when no new hpf files are found.
class Message(App):
    def build(self):
        Window.size = (400, 100);
        self.title = "No Files Found";
        content = Label(text = "No new hpf files found.\nSee the printedFields directory for png files.", halign = "center");
        return content;


if __name__ == '__main__':
    if mode == allNewHPFFiles:
        numFiles = 0;
        for f in Path("printedFields").glob("*.hpf"):
            fname = f.name;
            png = Path("printedFields/" + f.stem + ".png");
            if not png.exists() or png.stat().st_mtime < f.stat().st_mtime:
                numFiles += 1;
                app = FieldApp("printedFields/" + fname);
                app.run();
                app.export();
        if numFiles == 0:
            popup = Message();
            popup.run();
    
    elif mode == onlyNamedFile:
        app = FieldApp(filename);
        app.run();
        app.export();
    else:
        print("unexpected mode:", mode);

