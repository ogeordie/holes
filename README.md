# Holes
Holes is a program for simulations of archaeological digs.


Copyright 2024 Geordie Oakes

This program is free software: you can redistribute it and/or modify it under the terms of the
GNU General Public License v3 as published by the Free Software Foundation.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License v3 for more details.

You should have received a copy of the GNU General Public License along with this program.
If not, see https://www.gnu.org/licenses/gpl-3.0.html.

## DESCRIPTION
This code was used to run the simulations described in the article "Size Matters: Optimal 
Test Pit Size for Dispersed Archaeological Test Excavations" by Oakes and McLaren.

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

There are two ways to get the code: from Zenodo or GitHub.\
https://github.com/ogeordie/holes

There are many ways to view, edit, and run a Python script, too many describe each one. 
The instructions below use VS Code which is freely available on Windows, Mac, and
Linux. The instructions can be adapted for your favourite Python setup.

1.  Follow the steps in this tutorial 
    https://code.visualstudio.com/docs/python/python-tutorial
    to install Python 3, VS Code, and the VS Code Python extension.
    Note that Python 3.12.4 was used during development of this code.
    While the code will probably work with future versions, revert to 3.12.4 if there are any
    issues.

2.  Continue with steps in that tutorial to create a workspace folder, e.g.
    `C:\programming\holes` (for Windows) and open that folder in VS Code. Avoid spaces in the
    folder name.

3.  Place the files `Holes.py` and `CreateFieldImage.py` in that folder (and the other files and
    folders from the repository). If using GitHub, you can use it to manage your code if you
    like, including VS Code GitHub integration (but we have not tested this). We have included
    the `.venv` folder in the `.gitignore` file - see step 4. Otherwise you can simply download the
    main branch of the repository as a zip file from the GitHub repository web page
    or download the files from Zenodo.

4.  Continue with steps in the tutorial to create a virtual Venv environment using the
    VS Code `Python: Create Environment` command (with the folder open in VS Code).
    This virtual environment will avoid installed packages from conflicting with other
    projects.

5.  With the folder open, install dependencies in the VS Code terminal by running:
    ```
        python -m pip install scipy==1.14.1
        python -m pip install "kivy[base]==2.3.0"
    ```
    Kivy is used in `CreateImageField.py`, SciPy in `Holes.py`.
    SciPy installation installs numPy as a dependency as well.
    The versions given are those used during development. Newer versions
    will probably work but use the stated versions if you run into issues.
    Kivy may not support installation of previous versions, so remove the "==2.3.0" if
    there is an error during installation.

6.  Run the code! With `Holes.py` open in the editor (click it in the Explorer bar on the left
    of the VS Code window) press F5 to debug or Ctrl-F5 to run (or select the option
    from the Run menu). If you are asked to choose debugger choose "Python Debugger".
    If you are asked for a "Debug Configuration" choose "Python File".

