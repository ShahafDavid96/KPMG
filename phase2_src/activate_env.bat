@echo off
echo Activating virtual environment...
cd ..
call .venv\Scripts\activate
cd phase2_src
echo Virtual environment activated!
echo Current directory: %CD%
echo Python path: %PATH%
cmd /k
