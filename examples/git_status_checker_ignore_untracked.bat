@echo off

REM This batch script is exactly like `git_status_checker.bat`, but adds

REM Change to projects root directory:
cd %~dp0\..\..

REM Invoke git_status_checker script from projects root directory:
python %~dp0\..\git_status_checker\git_status_checker.py --ignore-untracked %* .

IF ERRORLEVEL 1 pause
