@echo off
:: Drag and drop video onto this .bat file to convert to MP4

:: Check if a file was dropped
if "%~1"=="" (
    echo Drag and drop a video file onto this script.
    pause
    exit /b
)

set "input=%~1"
set "filename=%~n1"
set "folder=%~dp1"

:: Use ffmpeg from the same folder as this .bat
set "ffmpegExe=%~dp0ffmpeg.exe"

:: Convert to MP4
"%ffmpegExe%" -i "%input%" -c:v libx264 -c:a aac "%folder%%filename%.mp4"

echo Conversion completed: "%folder%%filename%.mp4"
pause
