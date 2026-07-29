@echo off
setlocal

if "%~1"=="" (
    echo.
    echo Drag and drop one or more MP4 files onto this BAT.
    pause
    exit /b
)

for %%F in (%*) do (
    echo.
    echo Converting: %%~nxF

    "%~dp0ffmpeg.exe" -y ^
    -i "%%~fF" ^
    -vf "palettegen=stats_mode=full" ^
    "%%~dpnF_palette.png"

    "%~dp0ffmpeg.exe" -y ^
    -i "%%~fF" ^
    -i "%%~dpnF_palette.png" ^
    -lavfi "paletteuse=dither=sierra2_4a" ^
    "%%~dpnF.gif"

    del "%%~dpnF_palette.png"

    echo Done: %%~dpnF.gif
)

echo.
echo All conversions complete.
pause