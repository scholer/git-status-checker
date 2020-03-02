@echo off

REM This example can be used if the `git-status-checker` main project folder is located inside the folder
REM which contains all the other repositories that you would like to check for uncommitted git commits.

REM For example, I have the `git-status-checker` project folder and script located in the following folder:
REM 	~/Dev/git-status-checker/
REM 	~/Dev/git-status-checker/git_status_checker/git_status_checker.py
REM And I want to check all git repositories located inside my `~/Dev` folder.

REM This script will first change the current directory to `~/Dev`  (Using `cd %~dp0\..\..`)
REM and then call the `git_status_checker.py` script with the current directory as argument (`.`).
REM Arguments given to this batch script are passed along to `git_status_checker.py` using `%*`.

REM Note: Always consider whether using a batch script is indeed the best way solve your problem.
REM Often it is better to just invoke the python script directly including parameters as required.

REM Change to projects root directory:
cd %~dp0\..\..

REM Invoke git_status_checker script from projects root directory:
python %~dp0\..\git_status_checker\git_status_checker.py --ignore-untracked %* .

IF ERRORLEVEL 1 pause

REM Command prompt (`cmd`) variables, reference:
REM %~dp0 : Directory containing this script ("dir of parameter zero").
REM %* : Parameters given to this script (not including the script filename).
