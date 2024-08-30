@echo off
REM TTS/aligner portion
REM Initialize Conda if needed
CALL C:\...\miniconda3\Scripts\activate.bat

REM Activate Conda environment and run tts/alignment portion
CALL conda activate tts

REM Run the first Python script
CALL python "C:\...\RedditMaker\tts.py"

REM Deactivate Conda environment
CALL conda deactivate

REM Run video portion using Python 3.9.13
CALL "C:\Program Files\Python39\python.exe" "C:\...\RedditMaker\vid.py"
