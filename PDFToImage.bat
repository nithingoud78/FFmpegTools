@echo off
setlocal EnableExtensions EnableDelayedExpansion

title FFmpegTools - PDF Converter

echo.
echo ============================================
echo        FFmpegTools - PDF Converter
echo ============================================
echo.

if "%~1"=="" (
    echo Drag and drop one or more PDF files onto this BAT file.
    echo.
    pause
    exit /b
)

:: ------------------------------------------------
:: Find Ghostscript
:: ------------------------------------------------

set "GS="

if exist "%~dp0gswin64c.exe" set "GS=%~dp0gswin64c.exe"
if exist "%~dp0gswin32c.exe" set "GS=%~dp0gswin32c.exe"

if not defined GS (
    where gswin64c.exe >nul 2>&1
    if not errorlevel 1 set "GS=gswin64c.exe"
)

if not defined GS (
    where gswin32c.exe >nul 2>&1
    if not errorlevel 1 set "GS=gswin32c.exe"
)

if not defined GS (
    echo ERROR: Ghostscript was not found.
    echo.
    echo Put gswin64c.exe in the same folder as this BAT
    echo or add Ghostscript to your Windows PATH.
    echo.
    pause
    exit /b 1
)

:: ------------------------------------------------
:: Format selection
:: ------------------------------------------------

echo Choose output format:
echo.
echo   [J] JPG / JPEG
echo   [P] PNG
echo   [T] TIFF
echo   [B] BMP
echo   [S] SVG
echo   [M] PPM / PNM
echo.

set "CHOICE="
set /p "CHOICE=Enter your choice: "

set "CHOICE=!CHOICE:~0,1!"
set "CHOICE=!CHOICE:J=j!"
set "CHOICE=!CHOICE:P=p!"
set "CHOICE=!CHOICE:T=t!"
set "CHOICE=!CHOICE:B=b!"
set "CHOICE=!CHOICE:S=s!"
set "CHOICE=!CHOICE:M=m!"

:: ------------------------------------------------
:: Format configuration
:: ------------------------------------------------

if /I "!CHOICE!"=="j" (
    set "DEVICE=jpeg"
    set "EXT=jpg"
    set "DPI=300"
    set "OPTIONS=-dJPEGQ=100"
    set "FORMAT_NAME=JPG"
    goto :FORMAT_SELECTED
)

if /I "!CHOICE!"=="p" (
    set "DEVICE=png16m"
    set "EXT=png"
    set "DPI=300"
    set "OPTIONS="
    set "FORMAT_NAME=PNG"
    goto :FORMAT_SELECTED
)

if /I "!CHOICE!"=="t" (
    set "DEVICE=tiff24nc"
    set "EXT=tif"
    set "DPI=300"
    set "OPTIONS=-sCompression=lzw"
    set "FORMAT_NAME=TIFF"
    goto :FORMAT_SELECTED
)

if /I "!CHOICE!"=="b" (
    set "DEVICE=bmp16m"
    set "EXT=bmp"
    set "DPI=300"
    set "OPTIONS="
    set "FORMAT_NAME=BMP"
    goto :FORMAT_SELECTED
)

if /I "!CHOICE!"=="s" (
    set "DEVICE=svg"
    set "EXT=svg"
    set "DPI=300"
    set "OPTIONS="
    set "FORMAT_NAME=SVG"
    goto :FORMAT_SELECTED
)

if /I "!CHOICE!"=="m" (
    set "DEVICE=ppmraw"
    set "EXT=ppm"
    set "DPI=300"
    set "OPTIONS="
    set "FORMAT_NAME=PPM"
    goto :FORMAT_SELECTED
)

echo.
echo Invalid choice.
echo Please use J, P, T, B, S, or M.
echo.
pause
exit /b 1

:FORMAT_SELECTED

echo.
echo Selected format: !FORMAT_NAME!
echo Resolution: !DPI! DPI
echo.
echo Starting conversion...
echo.

:: ------------------------------------------------
:: Process all dropped PDFs
:: ------------------------------------------------

for %%F in (%*) do (

    echo ============================================
    echo File: %%~nxF
    echo ============================================
    echo.

    set "INPUT=%%~fF"
    set "DIR=%%~dpF"
    set "NAME=%%~nF"

    :: Ghostscript automatically adds page numbers
    :: when multiple pages are generated.
    ::
    :: Example:
    :: document_page_001.jpg
    :: document_page_002.jpg

    "%GS%" ^
        -q ^
        -dBATCH ^
        -dNOPAUSE ^
        -dSAFER ^
        -sDEVICE=!DEVICE! ^
        -r!DPI! ^
        !OPTIONS! ^
        -sOutputFile="!DIR!!NAME!_page_%%03d.!EXT!" ^
        "!INPUT!"

    if errorlevel 1 (
        echo.
        echo ERROR converting %%~nxF
    ) else (
        echo.
        echo Successfully converted:
        echo %%~nxF
    )

    echo.
)

echo ============================================
echo Conversion complete.
echo ============================================
echo.
pause
exit /b