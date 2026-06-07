@echo off
:: Drag & drop any video onto this file to get a WAV for Audacity

set "input=%~1"
set "name=%~n1"
set "folder=%~dp1"

if "%input%"=="" (
    echo Drag and drop a video file onto this script to extract audio as WAV.
    pause
    exit
)

"%~dp0ffmpeg.exe" -i "%input%" -vn -acodec pcm_s16le -ar 44100 -ac 2 "%folder%%name%.wav"

echo Done! Saved as "%folder%%name%.wav"
pause
