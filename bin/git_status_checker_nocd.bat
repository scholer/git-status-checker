@echo off

REM This script is usually used by placing a shortcut in the base directory,
REM and setting the shortcut's "Start in" parameter.

REM Do not change directory!
REM cd %~dp0\..\..

REM Invoke git_status_checker script from projects root directory:
REM python %~dp0\git_status_checker.py --ignore-untracked %* .
python %~dp0\..\git_status_checker\git_status_checker.py %* .

IF ERRORLEVEL 1 pause
