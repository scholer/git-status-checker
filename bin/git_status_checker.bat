@echo off

REM cmd file variables:
REM %~dp0 : Directory containing this script ("dir of parameter zero").
REM %* : Parameters given to this script (not including the script filename).

REM Note: Always consider whether using a batch script is indeed the best way solve your problem.
REM Often it is better to just invoke the python script directly including parameters as required.

REM Change to projects root directory:
cd %~dp0\..\..

REM Invoke git_status_checker script from projects root directory:
python %~dp0\git_status_checker.py --ignore-untracked %* .

IF ERRORLEVEL 1 pause
