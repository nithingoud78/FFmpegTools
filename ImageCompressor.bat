@echo off
setlocal EnableExtensions

title FFmpegTools - Image Compressor

echo.
echo ============================================
echo       FFmpegTools - Image Compressor
echo ============================================
echo.

if "%~1"=="" (
    echo Drag and drop a JPG/JPEG image onto this BAT.
    echo.
    pause
    exit /b
)

where ffmpeg.exe >nul 2>&1
if errorlevel 1 (
    echo ERROR: FFmpeg was not found.
    echo.
    echo Test this in Command Prompt:
    echo ffmpeg -version
    echo.
    pause
    exit /b
)

echo Target size range
echo Example: 50 to 150 means 50 KB - 150 KB
echo.

set /p "MIN=Minimum KB: "
set /p "MAX=Maximum KB: "

echo.

if "%MIN%"=="" goto BAD_INPUT
if "%MAX%"=="" goto BAD_INPUT

echo %MIN%| findstr /r /x "[0-9][0-9]*" >nul
if errorlevel 1 goto BAD_INPUT

echo %MAX%| findstr /r /x "[0-9][0-9]*" >nul
if errorlevel 1 goto BAD_INPUT

set /a MIN_BYTES=MIN*1024
set /a MAX_BYTES=MAX*1024

if %MIN_BYTES% GTR %MAX_BYTES% (
    echo Minimum cannot be greater than maximum.
    pause
    exit /b
)

echo Target: %MIN% KB - %MAX% KB
echo.

for %%F in (%*) do call :COMPRESS "%%~fF"

echo.
echo ============================================
echo Finished
echo ============================================
echo.
pause
exit /b


:COMPRESS

set "INPUT=%~1"
set "FOLDER=%~dp1"
set "NAME=%~n1"
set "EXT=%~x1"

echo.
echo ============================================
echo Input:
echo %INPUT%
echo ============================================
echo.

if /i not "%EXT%"==".jpg" if /i not "%EXT%"==".jpeg" (
    echo ERROR: JPG/JPEG only.
    exit /b
)

set "OUTPUT=%FOLDER%%NAME%_compressed.jpg"
set "TEST=%TEMP%\ffmpeg_test_%RANDOM%%RANDOM%.jpg"

del "%TEST%" >nul 2>&1
del "%OUTPUT%" >nul 2>&1

echo Creating compressed image...
echo.

rem ==========================================================
rem Try several fixed combinations.
rem Highest quality / resolution first.
rem ==========================================================

call :TRY 100 8
if exist "%OUTPUT%" exit /b

call :TRY 90 8
if exist "%OUTPUT%" exit /b

call :TRY 80 8
if exist "%OUTPUT%" exit /b

call :TRY 70 8
if exist "%OUTPUT%" exit /b

call :TRY 60 8
if exist "%OUTPUT%" exit /b

call :TRY 50 8
if exist "%OUTPUT%" exit /b

call :TRY 80 15
if exist "%OUTPUT%" exit /b

call :TRY 70 15
if exist "%OUTPUT%" exit /b

call :TRY 60 15
if exist "%OUTPUT%" exit /b

call :TRY 50 15
if exist "%OUTPUT%" exit /b

call :TRY 40 15
if exist "%OUTPUT%" exit /b

call :TRY 30 15
if exist "%OUTPUT%" exit /b

call :TRY 70 22
if exist "%OUTPUT%" exit /b

call :TRY 60 22
if exist "%OUTPUT%" exit /b

call :TRY 50 22
if exist "%OUTPUT%" exit /b

call :TRY 40 22
if exist "%OUTPUT%" exit /b

call :TRY 30 22
if exist "%OUTPUT%" exit /b

echo.
echo ============================================
echo No result was found between %MIN% KB and %MAX% KB.
echo ============================================
echo.
echo Try a larger maximum size.
echo.

del "%TEST%" >nul 2>&1
exit /b


:TRY

set "SCALE=%1"
set "QUALITY=%2"

echo Trying resolution %SCALE%%% - quality %QUALITY%...

ffmpeg.exe -y -hide_banner ^
-i "%INPUT%" ^
-vf "scale=trunc(iw*%SCALE%/100/2)*2:trunc(ih*%SCALE%/100/2)*2:flags=lanczos" ^
-frames:v 1 ^
-q:v %QUALITY% ^
-map_metadata -1 ^
"%TEST%"

if not exist "%TEST%" (
    echo FFmpeg failed.
    echo.
    exit /b
)

for %%Z in ("%TEST%") do set "SIZE=%%~zZ"

set /a SIZEKB=SIZE/1024

echo Result: %SIZEKB% KB

if %SIZE% GEQ %MIN_BYTES% if %SIZE% LEQ %MAX_BYTES% (
    copy /y "%TEST%" "%OUTPUT%" >nul

    echo.
    echo ============================================
    echo SUCCESS
    echo ============================================
    echo Output:
    echo %OUTPUT%
    echo.
    echo Size: %SIZEKB% KB
    echo Resolution scale: %SCALE%%%
    echo JPEG quality: %QUALITY%
    echo ============================================
    echo.

    del "%TEST%" >nul 2>&1
    exit /b
)

del "%TEST%" >nul 2>&1
exit /b


:BAD_INPUT

echo.
echo Invalid input.
echo Enter numbers only.
echo Example:
echo Minimum KB: 50
echo Maximum KB: 150
echo.
pause
exit /b
