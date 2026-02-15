# Holes
Holes is a program for simulations of archaeological excavations.


Copyright &copy; 2024-2026 Geordie Oakes.

This program is free software: you can redistribute it and/or modify it under the terms of the
GNU General Public License v3 as published by the Free Software Foundation.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License v3 for more details.

You should have received a copy of the GNU General Public License along with this program.
If not, see https://www.gnu.org/licenses/gpl-3.0.html.

## DESCRIPTION
This code was used to run the simulations described in the articles "Size Matters:
Determining Optimal Test Pit Size for Dispersed Archaeological Test Excavation Programs"
(in preparation) and "Layout Matters: Determining Optimal Test Pit Layout for Dispersed
Archaeological Test Excavation Programs" (submitted to Journal of Archaeological Science)
by Geordie Oakes and Andrew McLaren.

It places square test pits ("holes" in the code) of given number and size on a square field 
of a given size. The field has a randomly placed archaeological site (referred to as both
"treasure" and "site" in the code), either specified by a circle, rectangle, or polygon
(for intersection experiments), or by real-world data on artefact distribution from digs
in NSW Australia (for detection experiments in "Size Matters"). See the `real world data`
directory for the real-world data csv files and the polygon `shapefile` definition.

The pits are placed according to a layout algorithm. Layout algorithms are implemented by 
subclasses of the class `Player`. Calling `Player.play()` performs one archaeological dig 
(digging a certain number of holes on the `Field` according to the layout algorithm), and 
returns `True` if treasure is found (`False` otherwise). The Hexagonal-like algorithm
was used in "Size Matters" and "Layout Matters", the rest only in "Layout Matters".
Layout algorithms are implemented as follows:
- Hexagonal-like by the `HexagonalLikePlayer`
- StaggerXY by the `HexagonalLikePlayer` with appropriate arguments to its constructor
- RandomisedStaggerXY by the `HexagonalLikePlayer` with appropriate arguments to its constructor
- Halton by `HaltonPlayer`
- Random by `RandomPlayer`
- `HexagonalPlayer` was used to test if it had similar performance to the
`HexagonalLikePlayer`, which it did.  

See the document `size matters and layout matters layout algorithms.pdf`
for details of the layout algorithms.

`ExperimentRunner.runExperiment()` in Holes.py is the entry point to the simulation, and an
experiment is described by subclasses of the `Experiment` class. This class defines all
parameters except number of holes (field size, hole size, treasure specification, player 
type, etc.). For each number of holes (from 1 to a maximum value, or until 100% success rate
is reached) the inner simulation procedure is run 10000 times in "Size Matters"
(i.e. there are 10000 digs for each number of holes), with the treasure placed randomly
each time. In "Layout Matters" the procedure is run
10000 times for success experiments and 3000 times for summary experiments (see
[LAYOUT MATTERS EXPERIMENTS](#LAYOUT-MATTERS-EXPERIMENTS) below for descriptions of these).
The lower number is used for summary experiments as the experiments take a very long time.
The output of an experiment is, for each number of holes, the desired number of holes,
the actual number of holes as determined by the layout algorithm (which may differ from
the desired number of holes due to layout algorithm constraints), and the percentage of
runs where a hole found treasure ("success rate"). These data are printed to standard
output (optionally) and saved to a csv file. The output for the real-world artefact
distribution treasure also includes the average number of artefacts found over the
runs and average number of holes that found anything, but the `returnAfterHit`
argument to `Player.play()` must be set to False for these to be accurate. These additional
data are not used in either paper.

As mentioned above, note that some players dig a slightly different number of holes than the 
one supplied to them as the layout algorithm may not work with all numbers of holes. This 
actual number of holes is also returned by `Player.play()` (as well as whether the dig was
successful). `Player.play()` has an argument `returnAfterHit` which if `True` will cause
the method to return as soon as treasure if found. However note that the actual number of
holes returned is the number of holes that would have been dug if `returnAfterHit` was
`False` (i.e. the number of holes determined by the layout algorithm).

The main file is `Experiments.py` for "Size Matters" and `LayoutExperiments.py` for 
"Layout Matters". These files trigger the various experiments and the generation
of graphs and tables. Note that one can set the "go" variables in these files to
control what is triggered (for example if one wishes to use pre-generated data rather
than generating it which can take over 40 hours on a fast computer for "Layout Matters"
experiments). The file `Holes.py` contains code to run simulations as described above.
There is also the functionality to save a field (with holes and treasure) to a text file,
by calling `ExperimentRunner.printExperiment()` (which can also be triggered from
`Experiments.py` and `LayoutExperiments.py` by setting `goPrintExperiments` to `True`).
The file `CreateFieldImage.py` contains code to read such a text file and produce a
graphical representation of the field, useful in debugging. Printed experiments are saved
to `hpf` files (for Holes Printed Field). See the [FILES](#FILES) section
below for information on other files.

The inner simulation procedure (called thousands of times for each number of holes) is simplified
as (for example):
```
field = Field(fieldSize, fieldSize)
field.placeCircularTreasure(treasureRadius)
player = HexagonalLikePlayer(field, holeSize, numberOfHoles)
result = player.play()
if result[0]:
    successes = successes + 1
actualNumberOfHoles = result[1]
```
Then after the many iterations, the output is `number of holes`,
`actualNumberOfHoles`, and `successes * 100 / <number of iterations>` which is the
success rate. (We assume `actualNumberOfHoles` will be the same when `number of holes`
is the same). The output is saved to the file specified in the `Experiment` subclass.

The code defines the top left of the field as the origin (0,0).

The code was only tested with the experiments explored in the articles. It 
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

The code was developed and tested with Python 3.13.

### VS Code Instructions
1.  Follow the steps in this tutorial 
    https://code.visualstudio.com/docs/python/python-tutorial
    to install Python 3.13, VS Code, and the VS Code Python extension. Be sure you install the
    Python extension from the VS Code Extension Marketplace (see
    https://code.visualstudio.com/docs/configure/extensions/extension-marketplace) and search
    for Python.
    Note that Python 3.13 was used during development of this code.
    While the code will probably work with later versions (subject to the dependencies in
    `requirements.txt` supporting later versions), revert to 3.13 if there are any
    issues. Note that while the tutorial says "The system install of Python on macOS is not supported"
    we have found that it does in fact work (downloading from https://python.org/downloads/macos/).
    However if it doesn't work for you use "brew" as the tutorial suggests.

2.  Continue with steps in that tutorial to create a workspace folder, e.g.
    `C:\programming\holes` (for Windows) and open that folder in VS Code. Avoid spaces in the
    folder path.

3.  Place the python files and the other files and folders from the repository in that folder.
    If using GitHub, you can use it to manage your code if you
    like, including VS Code GitHub integration (but we have not tested this). We have included
    the `.venv` folder in the `.gitignore` file - see step 4. Otherwise you can simply download the
    files in the repository as a zip file from GitHub or Zenodo, unzip them, and copy them
    to your directory (be sure the files and folders are in the folder you opened with VS Code).

4.  Continue with steps in the tutorial to create a virtual Venv environment using the
    VS Code `Python: Create Environment` command (with the folder open in VS Code).
    You will need to select the Python version to use in the environment, which should
    be 3.13.x. This virtual environment will avoid installed dependencies from conflicting with
    other projects.

5.  With the folder open, create a `New Terminal` from the `Terminal` menu (**NOTE: it is important that
    a new terminal is created after creating the virtual python environment. Make sure the prompt
    begins with `(.venv)`**). Run `python --version` which should show 3.13.x. Then install dependencies
    of Holes in the VS Code terminal by running:
    ```
    python -m pip install -r requirements.txt
    ```

6.  Run the code! With `Experiments.py` (for "Size Matters" experiments)
    or `LayoutExperiments.py` (for "Layout Matters" experiments) open in the
    editor (click it in the Explorer bar on the left of the VS Code window),
    press F5 to debug or Ctrl-F5 to run (or select the option from the Run menu).
    If you are asked to choose debugger choose "Python Debugger".
    If you are asked for a "Debug Configuration" choose "Python File". It is more efficient
    to "run" the program rather then "debug".

Whenever you run commands from the VS Code Terminal, make sure the command prompt begins with `(.venv)`.
If it doesn't, create a `New Terminal` from the `Terminal` menu. If that doesn't work you may
have missed creating a virtual environment in step 4 above for the folder that's open in VS Code.


### Command Line Instructions
1.  Install python environment

    - Using bash under Debian Linux:
        ```
        sudo add-apt-repository ppa:deadsnakes/ppa
        sudo apt update
        sudo apt install python3.13
        sudo apt install python3-pip
        sudo apt install python3.13-venv
        ```

    - On macOS install latest python 3.13 from https://python.org/downloads/macos/

    - On Windows install latest python 3.13 from https://www.python.org/downloads/windows/
    (**NOTE: tick the box to add python.exe to your PATH**)

2.  Create a directory (e.g. `~/programming/holes` on Linux and macOS or `C:\programming\holes` on Windows),
    place the files and folders from the repository in it, and `cd` to it. Make sure the directory you
    are in contains the python files and all the other files and folders from the repository.

3.  Create and activate a python virtual environment
    - On bash using macOS Terminal or Linux (run `bash` if it is not the default shell):
        ```
        python3.13 -m venv .venv
        source .venv/bin/activate
        pip3 install -r requirements.txt
        ```

    - On Windows Command Prompt, use the `py` loader to select the correct version (3.13):
        ```
        py -3.13 -m venv .venv
        .venv\Scripts\activate
        pip install -r requirements.txt
        ```

    The prompt should now begin with `(.venv)`, indicating that
    the virtual environment has been activated.

4.  Run the code. Confirm that `python --version` shows 3.13.x. Also ensure
    you have activated the virtual environment (`source .venv/bin/activate` on bash
    or `.venv\Scripts\activate` on Windows Command Prompt). Then run:
    ```
    python Experiments.py
    ```
    for "Size Matters" experiments, or:
    ```
    python LayoutExperiments.py
    ```
    for "Layout Matters" experiments.

    Note that `"go"` variables can be set in these files to control what they do.
    By default they produce the graphs and tables using pre-generated data,
    but this can be changed to create the data from scratch (for
    LayoutExperiments.py this can take over 40 hours on a fast computer, and
    for Experiments.py over 1 hour and 30 minutes).

    To create a graphical image of a field, you first print the field to the
    `printedFields` directory (e.g. by setting `goPrintExperiments` to `True` in `Experiments.py`
    or `LayoutExperiments.py`). Printed fields are saved in `hpf` files. Example printed field
    files for "Size Matters" and "Layout Matters" exist in the `printedFields` directory.
    Then paste the file name of the printed field file into `CreateFieldImage.py`
    (the `filename` variable is near the top), and run:
    ```
    python CreateFieldImage.py
    ```
    This will display the image and also save it as a `png` file in the
    `printedFields` directory.

5. To deactivate the virtual environment:
    ```
    deactivate
    ```
    Be sure to `activate` it again before running the program again. You need to `activate` it
    each time your shell or command prompt is started (the prompt should begin
    with `(.venv)` when the virtual environment has been activated).


## DEPENDENCIES

Dependencies are listed in the `requirements.txt` file for easy installation, and their
licenses are available (in the `site-packages` directory somewhere in `.venv` subdirectories)
once they have been installed.

The Kivy framework (version 2.3.1) is used in `CreateImageField.py` to graphically display a field
for debugging purposes.

The sciPy library (version 1.16.3) is used in `Holes.py` to generate Halton distributions.

The numPy library (version 2.3.4) is used in `Tables.py` and `Plotter.py`.

The matplotlib library (version 3.10.7) is used in `Plotter.py` to produce graphs and tables.

The rich library (version 14.2.0) is used in `Experiments.py` and `LayoutExperiments.py`
to generate progress bars

The PyShp library (version 3.0.2.post1) is used in `Holes.py` to read treasure polygon shapes
in the `shapefile` format (usually a zip file containing the shape description).
See https://en.wikipedia.org/wiki/Shapefile.

The Shapely library (version 2.1.2) is used in `Holes.py` to detect if a square hole
intersects a treasure defined by a polygon.

The versions given are those used during development. Newer versions
will probably work but use the stated versions if you run into issues.
Kivy may not support installation of previous versions, so remove the "==2.3.1" 
from the `requirements.txt` file if there is an error during installation.


## FILES

These are the files in the `holes` distribution:
-   `Experiments.py` is a main file for running simulations and reproduces
    the experiments and produces graphs and tables used in "Size Matters" article.
-   `LayoutExperiments.py` is a main file for running simulations and reproduces
    the experiments and produces graphs and tables used in "Layout Matters" article.
-   `Holes.py`: The code implementing the players and simulations.
-   `CreateFieldImage.py`: Code to produce a graphical representation of a `Field`
    printed from `Holes.py` by calling `ExperimentRunner.printExperiment()`,
    used for debugging.
-   `Plotter.py` plots graphs and tables using the matplotlib library.
-   `Tables.py` provides functions to analyse the data used in the tables.
-   `requirements.txt`: the dependencies of the above python files, used during
    installation.
-   `README.md`: this file, describing the software and how to install and use it.
-   `LICENSE`: the GPL v3 license.
-   `size matters and layout matters layout algorithms.pdf`: Description of the layout
    algorithms implemented in `Holes.py`.
-   `real world data` folder: contains the data used in the detection experiments
    reported in "Size Matters", and the polygon in `shapefile` format used in
    "Layout Matters".
-   `printedFields` folder is where fields are printed when `ExperimentRunner.printExperiment()`
    is called. They can be displayed with `CreateFieldImage.py`.
-   `data/sizematters` folder: contains the data generated by `Experiments.py`.
    To regenerate the data set `goData` to `True` in `Experiments.py`.
    It may take over an hour and 30 minutes on a fast computer.
-   `other data subdirectories`: contain the data generated by `LayoutExperiments.py`.
    To regenerate the data set the `go` variables to `True` in `LayoutExperiments.py`
    (search for "go variables"). It may take over 40 hours to generate all data
    on a fast computer (can take days on an older or slower computer).
-   `graphs/sizematters` folder: contains the graphs and tables generated by `Experiments.py`.
    Run `Experiments.py` to regenerate these.
-   `other graphs subdirectories`: contain the graphs and tables generated by
    `LayoutExperiments.py`. Set `goGraphsAndTables` in `LayoutExperiments.py` to `True`
    and run the file to regenerate these (note: set the other go variables
    to False to avoid regenerating the data).


## SIZE MATTERS EXPERIMENTS

The experiments reported in the "Size Matters" paper fall into two broad categories: Intersection
experiments (using circular or rectangular treasure sites) and Detection experiments
(using artefact location data from real world excavations).

For each tested set of values, an experiment is run for 0.25 square metre holes (0.5m x 0.5m) and
another experiment for 1 square metre holes (1m x 1m).

In all experiments the `Player` used is the `HexagonalLikePlayer` implementing the
Hexagonal-like layout algorithm.

The experiments are set up in `Experiments.py` and passed to the `ExperimentRunner` in
`Holes.py`. Below are the settings for the experiments reported in the paper.

An experiment concludes when the maximum number of holes is reached, or a success rate
of 100% is reached. In these experiments maxHoles is set to 100000, which results in
experiments running until 100% success rate is reached.

Data produced using `Experiments.py` are output to the `data/sizematters` directory.
Figures and Tables are output to the `graphs/sizematters` directory. Tables are saved
both as `.png` images and `.csv` files. By default `Experiments.py`
uses pre-generated data from the `data/sizematters` directory. If you wish to generate your own data
set `goData` to `True` in `Experiments.py`. It may take over an hour and 30 minutes on a fast
computer. Note that as the simulation involves pseudo-random processes, the results will differ
slightly each time data is generated.

### Intersection Experiments

The values printed to standard output (optionally) and saved to a csv file for the Intersection
Experiments are: `<desired number of holes> <actual number of holes> <success rate after 10000 digs>`
For example a line `110 120 57.59` means the simulation requested that 110 holes are dug,
the layout algorithm settled on 120 holes (to keep things close to hexagonal), and
the treasure was intersected by at least one hole in 57.59% of the 10000 digs.

Figures are produced by calling `plotExperiment()` in the file `Plotter.py`, which plots
the `<actual number of holes>` values (the second column) on
the x axis and `<success rate after 10000 digs>` on the y axis, for small holes and big holes.
This optionally also plots the small hole strategy at different effort ratios (2:1, 3:1, and 4:1).

#### Figure 4A: Site (7m diameter circle), Field (100m x 100m), Layout (Hexagonal)
This graph is output to the file `7mCircle 100mField.png` in the graphs directory.
The parameters for these experiments are:
```
fieldSize = 100
holeSize = 0.5 (for first experiment) and 1 (for second experiment)
holeIncrement = 1
realWorldData = False
treasureShape = "circle"
treasureRadius = 3.5
numRepeats = 10000
```
#### Figure 4B: Site (7m diameter circle), Field (200m x 200m), Layout (Hexagonal)
This graph is output to the file `7mCircle 200mField.png` in the graphs directory.
The values are as for Figure 4A, except:
```
fieldSize = 200
```

#### Figure 4C: Site (28m diameter circle), Field (100m x 100m), Layout (Hexagonal)
This graph is output to the file `28mCircle 100mField.png` in the graphs directory.
The values are as for Figure 4A (note that `fieldSize` is again 100), except:
```
treasureRadius = 14
```

#### Figure 4D: Site (1m diameter circle), Field (100m x 100m), Layout (Hexagonal)
This graph is output to the file `1mCircle 100mField.png` in the graphs directory.
The values are as for Figure 4A, except:
```
treasureRadius = 0.5
```

#### Figure 4E: Site (20m x 5m elongated), Field (100m x 100m), Layout (Hexagonal)
This graph is output to the file `20x5mRectangle 100mField.png` in the graphs directory.
The values are as for Figure 4A, except:
```
treasureShape = "rectangle"
treasureWidth = 20
treasureHeight = 5
```

#### Figures 5, 6, and 7: Intersection effort ratio success rates
These graphs, showing the small hole strategy at various effort ratios are output to:
- `1mCircle 100mField ratios.png`
- `7mCircle 100mField ratios.png`
- `28mCircle 100mField ratios.png`.

The data for the 1:1 ratio curves (for the small holes and the big holes) is as for the
Figure 4 experiments (4D, 4A, and 4C respectively).
Data for the small hole strategy at other ratios are generated by dividing the x value
(`<actual holes dug>`) by the ratio value (2, 3, and 4) and plotting this against
small hole success rate on the y axis.

#### Table 1
This is output to `intersectDifferenceInSuccess.png`.
Table 1 uses the same data as the figures, analysed using `Tables.py`.

#### Table 2
This is output to `intersectBreakEvenRatios.png`.
Table 2 uses the same data once again, analysed using `Tables.py`


### Detection Experiments
The values printed to one line of standard output (optionally) are:
```
<desired number of holes> <actual number of holes> <success rate after 10000 digs>
<average number of artefacts found over 10000 digs>
<average number of holes that found anything over 10000 digs>
```
For example `110 120 98.87 10.7975 1.5141` means the simulation requested that 110 holes
are dug, the layout algorithm settled on 120 holes (to keep things close to hexagonal),
an artefact was detected by a hole in 98.87% of the 10000 digs, on average 10.7975
artefacts were detected by holes over the 10000 digs, and on average 1.5141 holes
detected an artefact over the 10000 digs. The first three values are also saved in a
csv file in the `data/sizematters` directory (the last two values weren't used in the paper,
but if they are required `returnAfterHit` must be set to `False` when calling `Player.play()`).

Again note that two experiments are run, one for 0.25 square metre holes (0.5m x 0.5m) and again
for 1 square metre holes (1m x 1m), setting `holeSize` to 0.5 and 1 respectively.

#### Figures 8, 10, and 12
These graphs are ouptut to:
- `LowDensity 100mField.png`
- `ModerateDensity 100mField.png`
- `HighDensity 100mField.png`.

These graphs show the success rates of small holes and big holes for real world
artefact distributions of different densities (Low, Moderate, and High respectively)

The parameters for these experiments are:
```
fieldSize = 100
holeSize = 0.5 (for first experiment) and 1 (for second experiment)
holeIncrement = 1
realWorldData = True
realWorldDataFileName =
    - "real world data/Low Density Artefact Coordinates.csv",
    - "real world data/Moderate Density Artefact Coordinates.csv",
    - "real world data/High Density Artefact Coordinates.csv (respectively)
numRepeats = 10000
```

#### Figures 9, 11, and 13: effort ratio comparison
These graphs are output to:
- `LowDensity 100mField ratios.png`
- `ModerateDensity 100mField ratios.png`
- `HighDensity 100mField ratios.png`.

These use the same data as for Figure 8, 10, and 12 respectively,
and additionally plots the success of the small hole strategy at different effort ratios.

#### Tables 3, 4, and 5
These use the same data as Figures 9, 11, and 13 respectively, analysed using `Tables.py`.
The graphs are output to:
- `lowDensitySummary.png`
- `moderateDensitySummary.png`
- `highDensitySummary.png`.


### LAYOUT MATTERS EXPERIMENTS

Layout experiments compare various layout algorithms in various ways. The treasures (sites)
are rectangles of various areas with various elongation ratios, e.g. 1:1 (square),
5:1, 20:1, etc., oriented both horizontally and vertically. Additionally a polygon shape
of a real world site is used.

Generated data is stored in various subdirectories of the `data` directory. Raw data on success
of a layout algorithm over a range of numbers of holes are stored in files named:
`<treasure-width>x<treasure-height>rectangle <layout-algorithm> fieldsize<field-size> siteArea<site-area>.csv`.
For real world site shape (polygon) experiments the data are stored in files named:
`<orientation>polygon <layout-algorithm> fieldsize<field-size>.csv` where `<orientation>`
is either `vertical` or `horizontal`.

The "success" graphs use these data. The "summary" graphs are generated by
analysing these raw success data and generating files named
`summary fieldsize<field-size> siteArea<site-area> maxholes<maximum-holes>.csv` in
various subdirectories of the `data` directory (specified below). These are then used
for plotting summary graphs.

Tables are saved both as `.png` images and `.csv` files. 

#### Figures 3A, B, C, D, E: Layout Algorithm Success Curves
These graphs show the success rates of the various algorithms (on the y axis) plotted against the
number of holes determined by the layout algorithm (on the x axis), for a treasure area of
$100m^2$. Data are produced by `goSpecificRatioData()` and are stored in the `data/drilldown`
directory. `goSpecificRatioGraphs()` generates graphs in `graphs/drilldown` showing success
curves of various layout algorithms for various site areas and site elongation
ratios.

**A** is `success Square ratio 1 fieldsize100 siteArea100.png`   
**B** is `success Vertically Elongated ratio 5 fieldsize100 siteArea100.png`   
**C** is `success Horizontally Elongated ratio 5 fieldsize100 siteArea100.png`   
**D** is `success Vertically Elongated ratio 20 fieldsize100 siteArea100.png`   
**E** is `success Horizontally Elongated ratio 20 fieldsize100 siteArea100.png`

#### Table 1
This table uses the same data as Figure 3, and shows the number of holes needed
to achieve three success thresholds (80%, 95%, 100%). The table is generated
by `goSpecificRatioHolesForSuccessRatesTables()`, is stored in the `graphs/drilldown`
directory, and is named `holes for success rates table fieldsize100 siteArea100.png`
(and `.csv`).

#### Table 2
This table shows the maximum difference in success rates across all algorithms for
any given number of holes, for each site ratio considered in Figures 3. It shows this
maximum for both all numbers of holes and for to 1-25 holes. It is generated by
`goMaximumDifferenceInSuccessTable()` which uses `getMaximumDifferenceInSuccessLayout()`
in Tables.py. It is stored in the `graphs/drilldown` directory and is named
`maximum differences in success siteArea 100.png` (and `.csv`).

#### Figures 4A, B, C, E: Layout Algorithm Summary Experiments
(See below for 4D).
Raw success data produced by `goSummaryData()` are stored in the `data/summary` directory
for various treasure areas and elongations.
`goSummaryGraphs()` analyses these raw data and produces files also in `data/summary` named
`summary fieldsize<field-size> siteArea<site-area> maxholes<maximum-holes>.csv`. These files
contain the area under the success curves of the various layout algorithms
for various site elongation ratios. Graphs are stored in the `graphs/summary` directory.
Figure 4E is a zoomed out version of 4B.

**A** is `summary fieldsize100 siteArea20 maxholes6000 central.png`   
**B** is `summary fieldsize100 siteArea100 maxholes6000 central.png`   
**C** is `summary fieldsize100 siteArea200 maxholes6000 central.png`   
**E** is `summary fieldsize100 siteArea100 maxholes6000.png`

#### Figure 4D
This graph shows how some layout algorithms behave with very large elongation ratios,
using a site area of $20m^2$ (so that highly elongated sites still fit on the field).
Raw success data are generated by `goLargeRatioData()` and are stored in the
`data/largeratio` directory. `goLargeRatioGraphs()` analyses that raw data 
and produces a file in `data/largeratio` named `summary large ratio fieldsize100 siteArea20.csv`.
This is in turn used to produce a graph in the `graphs/largeratio` directory called
`summary large ratio fieldsize100 siteArea20.png`.

#### Tables 3, 4, 5, 6: Algorithm Summary Crossover Points
These use the `summary` files in the `data/summary` directories (including those
used in Figures 4A, B, C) produced by `goSummaryGraphs()` to display the treasure
elongation ratios at which the performance of various layout algorithms "crosses over"
(starts to perform worse than) the performance of the `Halton` layout algorithm as the
elongation ratio increases (in both the horizontal and vertical directions).
Tables 3 and 4 fix the site area at $100m^2$ and show various field sizes.
Tables 5 and 6 fix the field size at 100m x 100m and show various site areas.
See the paper and `generateCrossoverTableAndGraph()` in `LayoutExperiment.py`
for more information on crossover points. `goCrossoverTables()` generates the tables
in the `graphs/summary` directory.

**3** is `horizontal crossover siteArea100 table.png` (and `.csv`)   
**4** is `vertical crossover siteArea100 table.png` (and `.csv`)   
**5** is `horizontal crossover fieldsize100 table.png` (and `.csv`)   
**6** is `vertical crossover fieldsize100 table.png` (and `.csv`)

#### Figures 5A, B, C: Low Intensity Test Pit Summary Curves
These are summary graphs but only over 1 to 25 holes.
They use the raw success data in the `data/summary` directory (as for Figures 4A, B, C).
`goSmallNumberOfHolesGraphs()` analyses these data and produces `summary` data files
in the `data/smallnumholes` directory. These in turn are used to produce graphs in
the `graphs/smallnumholes` directory.

**A** is `summary fieldsize100 siteArea20 maxholes25 central.png`  
**B** is `summary fieldsize100 siteArea100 maxholes25 central.png`  
**C** is `summary fieldsize100 siteArea200 maxholes25 central.png`

#### Figures 6A, B: Real-World Site Success Curves
These use data generated by `goRealWorldData()` which are stored in the
`data/realworld` directory. `goRealWorldGraphs()` produces graphs of the
various algorithms for a real world treasure shape (polygon) oriented in
both the vertical and horizontal directions.

**A** is `horizontalpolygon fieldsize100.png`  
**B** is `verticalpolygon fieldsize100.png`

#### Tables 7 and 8: 
These use the same data as in Figures 6A and B, and shows the number of holes needed
to achieve three success thresholds (80%, 95%, 100%) for the various layout algorithms,
for both a horizontally and vertically oriented real world site shape.
The tables are generated by `goRealWorldHolesForSuccessRatesTables()` in the `graphs/realworld`
directory.

**7** is `holes for success rates table horizontalpolygon fieldsize100.png` (and `.csv`)  
**8** is `holes for success rates table verticalpolygon fieldsize100.png` (and `.csv`)
