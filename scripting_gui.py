#!/bin/python2

import knack_tools as kt
import scripts


## Import all the scripts in the "scripts/" folder
available_scripts = scripts.import_scripts()

## Create the window object.
gui = kt.ScriptingWindow(available_scripts)

## Hand off the program to the gui. 
##   The gui reacts to the user input and will call
##   "gui.run_script()" when the user clicks "Process File"
gui.mainloop()
