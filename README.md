# Holes
Holes is a program for simulations of archaeological excavations.


Copyright 2024 Geordie Oakes

This program is free software: you can redistribute it and/or modify it under the terms of the
GNU General Public License v3 as published by the Free Software Foundation.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License v3 for more details.

You should have received a copy of the GNU General Public License along with this program.
If not, see https://www.gnu.org/licenses/gpl-3.0.html.

## DESCRIPTION
This code was used to run the simulations described in the article "Size Matters:
Determining Optimal Test Pit Size for Dispersed Archaeological Test Excavation Programs"
by Geordie Oakes and Andrew McLaren, submitted to Australian Archaeology.

It places square test pits ("holes" in the code) of given number and size on a square field 
of a given size. The field has a randomly placed archaeological site ("treasure" in the 
code), either specified by a circle or rectangle (for intersection experiments), or by 
real-world data on artefact distribution from digs in NSW Australia (for detection 
experiments). See the csv files in the `real world data` directory for these data.

The pits are placed according to a layout algorithm. Layout algorithms are implemented by 
subclasses of the class `Player`. Calling `Player.play()` performs one archaeological dig 
(digging a certain number of holes on the `Field` according to the layout algorithm), and 
returns `True` if treasure is found (`False` otherwise). The `HexagonalLikePlayer` player was used 
in the simulations for the article. Other `Player` subclasses include `HexagonalPlayer`, 
`HaltonPlayer`, and `RandomPlayer`. See the document `size matters layout algorithms.pdf` for 
explanation of the layout algorithms.

The function `exploreNumberOfHoles()` is the main function for most experiments. This fixes all 
parameters except number of holes (field size, hole size, treasure specification, player 
type, etc.), and for each number of holes (from 1 to a maximum value) the inner simulation 
procedure is run 10000 times (i.e. there are 10000 digs for each number of holes), with the 
treasure placed randomly each time. The output (printed to standard output) for each number 
of holes is the desired number of holes, the actual number of holes as determined by the 
layout algorithm (which may differ from the desired number of holes due to layout algorithm 
constraints), and the percentage of runs where a hole found treasure ("success rate"). The 
output for the real-world artefact distribution treasure also includes the average number of 
artefacts found over the runs and average number of holes that found anything.

As mentioned above, note that some players dig a slightly different number of holes than the 
one supplied to them as the layout algorithm may not work with all numbers of holes. This 
actual number of holes is also returned by `Player.play()` (as well as weather the dig was
successful).

The function `doSpecificGridExperiment()` allows experiments to be done with a list of specific 
numbers of holes, or a list of specific number of holes horizontally and vertically.

The file `Holes.py` contains code to run simulations as described above. There is also the 
functionality to save a field (with holes and treasure) to a text file.
The file `CreateFieldImage.py` contains code to read said text file and produce a graphical 
representation of the field.

The inner simulation procedure (called 10000 times for each number of holes) is simplified as:
```
field = Field(fieldSize, fieldSize)
field.placeCircularTreasure(treasureRadius)
player = HexagonalLikePlayer(field, holeSize, numberOfHoles)
result = player.play()
if result[0]:
    successes = successes + 1
actualNumberOfHolesDug = result[1]
```
Then after the 10000 runs, print out `numberOfHoles`, `actualHolesDug`, and `successes * 100 / 10000`
(We assume `actualHolesDug` by the player will be the same when `numberOfHoles` is the same).

This code was only tested with the limited experiments explored in the article. It 
may not be correct in all circumstances.


## INSTALLATION

There are two ways to get the code: from Zenodo or GitHub.
The GitHub repository is https://github.com/ogeordie/holes.

There are many ways to view, edit, and run a Python script, too many describe each one.
In particular, one can use an Integrated Development Environment (IDE) or run instructions
from the command line.
Below are installation instructions for installation using VSCode (a popular and freely
available IDE that runs on Windows, MacOS, and Linux), and also instructions
for installation using the command line in a bash environment under Debian Linux (including Ubuntu),
macOS, and Windows. We trust that these instructions can be adapted to the setup of your choice.

### VS Code Instructions
1.  Follow the steps in this tutorial 
    https://code.visualstudio.com/docs/python/python-tutorial
    to install Python 3.12, VS Code, and the VS Code Python extension. Be sure you install the
    Python extension from the VS Code Extension Marketplace (see
    https://code.visualstudio.com/docs/configure/extensions/extension-marketplace) and search
    for Python.
    Note that Python 3.12 was used during development of this code.
    While the code will probably work with later versions, revert to 3.12 if there are any
    issues. Note that while the tutorial says "The system install of Python on macOS is not supported"
    we have found that it does in fact work (downloading from https://python.org/downloads/macos/).
    However if it doesn't work for you use "brew" as the tutorial suggests.

2.  Continue with steps in that tutorial to create a workspace folder, e.g.
    `C:\programming\holes` (for Windows) and open that folder in VS Code. Avoid spaces in the
    folder path.

3.  Place the files `Holes.py`, `CreateFieldImage.py`, and `requirements.txt` in that folder
    (and the other files and folders from the repository).
    If using GitHub, you can use it to manage your code if you
    like, including VS Code GitHub integration (but we have not tested this). We have included
    the `.venv` folder in the `.gitignore` file - see step 4. Otherwise you can simply download the
    files in the repository as a zip file from GitHub or Zenodo, unzip them, and copy them
    to your directory (be sure the files are in the folder you opened with VS Code).

4.  Continue with steps in the tutorial to create a virtual Venv environment using the
    VS Code `Python: Create Environment` command (with the folder open in VS Code).
    You will need to select the Python version to use in the environment, which should
    be 3.12.x. This virtual environment will avoid installed packages from conflicting with other
    projects.

5.  With the folder open, install dependencies in the VS Code terminal (access it from the View menu)
    by running:
    ```
    python3.12 -m pip install -r requirements.txt
    ```
    or if it doesn't work run `python --version` which should show 3.12.x, then
    ```
    python -m pip install -r requirements.txt
    ```

6.  Run the code! With `Holes.py` open in the editor (click it in the Explorer bar on the left
    of the VS Code window) press F5 to debug or Ctrl-F5 to run (or select the option
    from the Run menu). If you are asked to choose debugger choose "Python Debugger".
    If you are asked for a "Debug Configuration" choose "Python File". It is more efficient
    to "run" the program rather then "debug".

### Command Line Instructions
1.  Install python environment

    - Using bash under Debian Linux:
        ```
        sudo add-apt-repository ppa:deadsnakes/ppa
        sudo apt update
        sudo apt install python3.12
        sudo apt install python3-pip
        sudo apt install python3.12-venv
        ```

    - On macOS install latest python 3.12 from https://python.org/downloads/macos/

    - On Windows install latest python 3.12 from https://www.python.org/downloads/windows/
    (NOTE: tick the box to add python.exe to your PATH)

2.  Create a directory (e.g. `~/programming/holes` on Linux and macOS or `C:\programming\holes` on Windows),
    place the files from the repository in it, and `cd` to it. Make sure the directory you are in contains the
    python files `Holes.py`, `CreateFieldImage.py`, `requirements.txt` and the other files and folders
    from the repository.

3.  Create a python virtual environment
    - On bash using macOS Terminal or Linux (run `bash` if it is not the default shell):
        ```
        python3.12 -m venv .venv
        source .venv/bin/activate
        pip3 install -r requirements.txt
        ```

    - On Windows Command Prompt, first check that you are using the correct version by running
    `python --version`, which should be 3.12.x. Then continue with:
        ```
        python -m venv .venv
        .venv\Scripts\activate
        pip install -r requirements.txt
        ```

4.  Run the code:
    ```
    python Holes.py
    ```
    and when you have printed a field from `Holes.py` and edited `CreateFieldImage.py`
    to reflect the file name of the field file:
    ```
    python CreateFieldImage.py
    ```

5. To deactivate the virtual environment:
```
deactivate
```
Be sure to `activate` it again before running the program again.

## DEPENDENCIES
Dependencies are listed in the `requirements.txt` file for easy installation.

The Kivy framework (version 2.3.0) is used in `CreateImageField.py` to graphically display a field
for debugging purposes.

The sciPy library (version 1.14.1) is used in `Holes.py` to generate Halton distributions (not used
in the simulations for the paper). The sciPy installation installs the numPy library as a dependency as well.

The versions given are those used during development. Newer versions
will probably work but use the stated versions if you run into issues.
Kivy may not support installation of previous versions, so remove the "==2.3.0" 
from the `requirements.txt` file if there is an error during installation.


## FILES

These are the files in the `holes` distribution:
-   `Holes.py`: The code to run the simulations reported in the paper
-   `CreateFieldImage.py`: Code to produce a graphical representation of a `Field`
    printed from `Holes.py`, used for debugging
-   `requirements.txt`: the dependencies of the above python files, used during
    installation
-   `README.md`: this file, describing the software and how to install and use it
-   `size matters layout algorithms.pdf`: Description of the layout algorithms
    implemented in `Holes.py`. The `Hexagonal-Like` algorithm is the one used
    in the experiments reported in the paper
-   `real world data` folder: contains the data used in the detection experiments
    reported in the paper
-   `calculate break even ratio.xlsm`: an Excel spreadsheet with a macro to
    calculate the break-even ratios for each success rate. This example contains
    data for a treasure radius of 3.5 (7m diameter) but you can replace these
    with any data you wish (the macro expects the data to be in the same
    place as it is in the example). Run the macro after pasting the new data.
-   `intersectField 100 holesize 0.5 treasure 3.5 holes 120 HexagonalLikePlayer`:
    an example print out of a field produced by `Holes.py` and which can be
    displayed with `CreateFieldImage.py`


## EXPERIMENTS

The experiments reported in the paper fall into two broad categories: Intersection
experiments (using circular or rectangular treasure sites) and Detection experiments
(using artefact location data from real world excavations).

In all experiments, the program is run once for 0.25 square metre holes (0.5m x 0.5m) and again
for 1 square metre holes (1m x 1m).

In all experiments the `Player` used is the `HexagonalLikePlayer`.

The experiments are set up in the `exploreNumberOfHoles()` function in `Holes.py`. Following
are the settings for the experiments reported in the paper.

An experiment can be manually interruped once you have enough data (Cntrl-C in the terminal
or "stop debugging" in VS Code) instead of waiting until the maximum number of holes is reached.


### Intersection Experiments

The values printed to standard output for the Intersection Experiments are:
`<desired number of holes> <actual number of holes dug> <success rate after 10000 digs>`
For example a line `110 120 57.59` means the simulation requested that 110 holes are dug,
the layout algorithm settled on 120 holes (to keep things close to hexagonal), and
the treasure was intersected by at least one hole in 57.59% of the 10000 digs.

The figures were produced in Excel by plotting the `<actual number of holes dug>` values
(the second column) on
the x axis and `<success rate after 10000 digs>` on the y axis (see below for
how to plot the small hole strategy at different effort ratios in Figures 5, 6, and 7).
When pasting text data into Excel, use the "text import wizard" to format the data into columns.
You can also use "text to columns" from the Data tab once the data has been pasted and selected.
Ensure "Space" is ticked in the "delimiters" list.

#### Figure 4A: Site (7m diameter circle), Field (100m x 100m), Layout (Hexagonal)
The values for the variables in `exploreNumberOfHoles()` are:
```
fieldSize = 100;

# hole size for 0.25 square metre holes (0.5m x 0.5m)
# NOTE: change this to 1 for 1 square metre holes (1m x 1m)
holeSize = 0.5;

# increment number of holes by this value each iteration
holeIncrement = 1;
maxHoles = 6000; # stop when this number of holes is reached
# (you can manually stop the program before this if you have enough data)

# set whether we are using real world data and where it can be found
realWorldData = False;
realWorldDataFile = "<not used>"

# if realWorldData is False, set the treasure shape and dimensions
treasureShape = "circle";
# if circle - note this is the radius, while the diameter was given in the article:
treasureRadius = 3.5; # for 7m diameter
# if rectangle:
treasureWidth = 20;
treasureHeight = 5;

numRepeats = 10000;
```

Note that the program is run once for `holeSize = 0.5` and again changing the value
to `holeSize = 1`.

#### Figure 4B: Site (7m diameter circle), Field (200m x 200m), Layout (Hexagonal)
The values are as for Figure 4A, except:
```
fieldSize = 200;
```

#### Figure 4C: Site (28m diameter circle), Field (100m x 100m), Layout (Hexagonal)
The values are as for Figure 4A (note that `fieldSize` is again 100), except:
```
treasureRadius = 14;
```

#### Figure 4D: Site (1m diameter circle), Field (100m x 100m), Layout (Hexagonal)
The values are as for Figure 4A, except:
```
treasureRadius = 0.5;
```

#### Figure 4E: Site (20m x 5m elongated), Field (100m x 100m), Layout (Hexagonal)
The values are as for Figure 4A, except:
```
treasureShape = "rectangle";
treasureWidth = 20;
treasureHeight = 5;
```

#### Figures 5, 6, and 7: Intersection effort ratio success rates
The data for the 1:1 ratio lines (for the small holes and the big holes) is as for the
Figure 4 experiments (4D, 4A, and 4C respectively).
Data for the small hole strategy at other ratios are generated in Excel
by dividing the x value (`<actual holes dug>`) by the ratio value (2, 3, and 4)
and plotting this against small hole success rate on the y axis.

#### Table 1
Table 1 uses the same data as the figures, analysed in Excel.

#### Table 2
Table 2 uses the same data once again, with an Excel macro to generate the
data on break-even ratios. (see the `calculate break even ratio.xlsm` file).
The macro must be run after pasting new data into the spreadsheet.

### Detection Experiments
The values printed to one line of standard output for the Detection Experiments are:
```
<desired number of holes> <actual number of holes dug> <success rate after 10000 digs>
<average number of artefacts found over 10000 digs>
<average number of holes that found anything over 10000 digs>
```
For example `110 120 98.87 10.7975 1.5141` means the simulation requested that 110 holes
are dug, the layout algorithm settled on 120 holes (to keep things close to hexagonal),
an artefact was detected by a hole in 98.87% of the 10000 digs, on average 10.7975
artefacts were detected by holes over the 10000 digs, and on average 1.5141 holes
detected an artefact over the 10000 digs.

Again note that two experiments are run, one for 0.25 square metre holes (0.5m x 0.5m) and again
for 1 square metre holes (1m x 1m), setting `holeSize` to 0.5 and 1 respectively.

#### Figures 8, 10, and 12
These figures show the success rates of small holes and big holes for real world
artefact distributions of different densities.

The values for the variables in `exploreNumberOfHoles()` are:
```
fieldSize = 100;

# hole size for 0.25 square metre holes (0.5m x 0.5m)
# NOTE: change this to 1 for 1 square metre holes (1m x 1m)
holeSize = 0.5;

# increment number of holes by this value each iteration
holeIncrement = 1;
maxHoles = 6000; # stop when this number of holes is reached
# (you can manually stop the program before this if you have enough data)

# set whether we are using real world data and where it can be found
realWorldData = True;
# NOTE: change this to use Moderate and High Density data
realWorldDataFile = "real world data/Low Density Artefact Coordinates.csv"

numRepeats = 10000;

# THE FOLLOWING ARE NOT USED FOR DETECTION (REAL WORLD) EXPERIMENTS
# if realWorldData is False, set the treasure shape and dimensions
treasureShape = "circle";
# if circle - note this is the radius, while the diameter was given in the article:
treasureRadius = 3.5; # for 7m diameter
# if rectangle:
treasureWidth = 20;
treasureHeight = 5;
```

Note that Figure 10 uses the `Moderate Density Artefact Coordinates.csv` and
Figure 12 the `High Density Artefact Coordinates.csv`, changing the `realWorldDataFile`
variable accordingly.

#### Figures 9, 11, and 13: effort ratio comparison
This uses the same data as for Figure 8, 10, and 12 respectively,
and additionally plots the success of the small hole strategy at different effort ratios.
Data for the small hole strategy at other ratios are generated in Excel
by dividing the x value (`<actual holes dug>`) by the ratio value (2, 3, and 4)
and plotting this against small hole success rate on the y axis.

#### Tables 3, 4, and 5
These use the same data as Figures 9, 11, and 13 respectively, with an Excel
macro to generate the data on break-even ratios (see the `calculate break even ratio.xlsm` file).
The macro must be run after pasting new data into the spreadsheet.