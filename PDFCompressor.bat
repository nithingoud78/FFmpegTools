@echo off
setlocal EnableExtensions EnableDelayedExpansion

title FFmpegTools - PDF Compressor

echo.
echo ============================================
echo        FFmpegTools - PDF Compressor
echo ============================================
echo.

if "%~1"=="" (
    echo Drag and drop one or more PDF files onto this BAT file.
    echo.
    pause
    exit /b
)

:: --------------------------------------------------
:: Find Ghostscript
:: --------------------------------------------------

set "GS="

if exist "%~dp0gswin64c.exe" set "GS=%~dp0gswin64c.exe"
if not defined GS if exist "%~dp0gswin32c.exe" set "GS=%~dp0gswin32c.exe"

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
    echo Put gswin64c.exe in the same folder as this BAT,
    echo or add Ghostscript to your system PATH.
    echo.
    pause
    exit /b 1
)

:: --------------------------------------------------
:: Ask target size
:: --------------------------------------------------

set "TARGET="

set /p "TARGET=Enter maximum desired size (example: 2MB or 500KB): "

if not defined TARGET (
    echo.
    echo ERROR: No target size entered.
    pause
    exit /b 1
)

:: --------------------------------------------------
:: Convert target size to bytes
:: Bare number = MB
:: --------------------------------------------------

for /f "delims=" %%A in ('powershell -NoProfile -Command ^
    "$s='%TARGET%'.Trim().ToUpper(); ^
     if($s -match '^[0-9]+([.,][0-9]+)?$'){ ^
        $n=[double]($s -replace ',','.'); ^
        [int64]($n*1MB) ^
     } elseif($s -match '^([0-9]+([.,][0-9]+)?)\s*MB$'){ ^
        $n=[double](($matches[1]) -replace ',','.'); ^
        [int64]($n*1MB) ^
     } elseif($s -match '^([0-9]+([.,][0-9]+)?)\s*KB$'){ ^
        $n=[double](($matches[1]) -replace ',','.'); ^
        [int64]($n*1KB) ^
     } elseif($s -match '^([0-9]+([.,][0-9]+)?)\s*GB$'){ ^
        $n=[double](($matches[1]) -replace ',','.'); ^
        [int64]($n*1GB) ^
     } else { 0 }"') do set "TARGET_BYTES=%%A"

if "%TARGET_BYTES%"=="0" (
    echo.
    echo ERROR: Invalid size.
    echo Examples:
    echo   2MB
    echo   500KB
    echo   1.5MB
    echo   10MB
    echo.
    pause
    exit /b 1
)

echo.
echo Target maximum size:
powershell -NoProfile -Command "[math]::Round(%TARGET_BYTES%/1MB,2)" | findstr /r "." >nul
echo.

:: --------------------------------------------------
:: Compression profiles
::
:: Highest quality -> strongest compression
:: --------------------------------------------------

set "DPI1=180"
set "DPI2=150"
set "DPI3=120"
set "DPI4=100"
set "DPI5=85"
set "DPI6=72"
set "DPI7=60"

set "JPG1=90"
set "JPG2=85"
set "JPG3=80"
set "JPG4=75"
set "JPG5=70"
set "JPG6=60"
set "JPG7=50"

:: --------------------------------------------------
:: Process every dropped PDF
:: --------------------------------------------------

for %%F in (%*) do (

    echo ============================================
    echo Processing:
    echo %%~nxF
    echo ============================================
    echo.

    set "INPUT=%%~fF"
    set "DIR=%%~dpF"
    set "NAME=%%~nF"

    set "OUTPUT=!DIR!!NAME!_compressed.pdf"
    set "BEST=!DIR!!NAME!_compressed_best.pdf"

    if exist "!OUTPUT!" del /q "!OUTPUT!" >nul 2>&1
    if exist "!BEST!" del /q "!BEST!" >nul 2>&1

    set "FOUND=0"

    :: ----------------------------------------------
    :: Profile 1
    :: ----------------------------------------------
    call :compress "!INPUT!" "!BEST!" "!OUTPUT!" "!DPI1!" "!JPG1!" "!TARGET_BYTES!" "!FOUND!"
    if "!FOUND!"=="1" goto :DONE_FILE

    :: Profile 2
    call :compress "!INPUT!" "!BEST!" "!OUTPUT!" "!DPI2!" "!JPG2!" "!TARGET_BYTES!" "!FOUND!"
    if "!FOUND!"=="1" goto :DONE_FILE

    :: Profile 3
    call :compress "!INPUT!" "!BEST!" "!OUTPUT!" "!DPI3!" "!JPG3!" "!TARGET_BYTES!" "!FOUND!"
    if "!FOUND!"=="1" goto :DONE_FILE

    :: Profile 4
    call :compress "!INPUT!" "!BEST!" "!OUTPUT!" "!DPI4!" "!JPG4!" "!TARGET_BYTES!" "!FOUND!"
    if "!FOUND!"=="1" goto :DONE_FILE

    :: Profile 5
    call :compress "!INPUT!" "!BEST!" "!OUTPUT!" "!DPI5!" "!JPG5!" "!TARGET_BYTES!" "!FOUND!"
    if "!FOUND!"=="1" goto :DONE_FILE

    :: Profile 6
    call :compress "!INPUT!" "!BEST!" "!OUTPUT!" "!DPI6!" "!JPG6!" "!TARGET_BYTES!" "!FOUND!"
    if "!FOUND!"=="1" goto :DONE_FILE

    :: Profile 7
    call :compress "!INPUT!" "!BEST!" "!OUTPUT!" "!DPI7!" "!JPG7!" "!TARGET_BYTES!" "!FOUND!"

:DONE_FILE

    if exist "!BEST!" (
        move /y "!BEST!" "!OUTPUT!" >nul

        echo.
        echo SUCCESS
        echo Output:
        echo !OUTPUT!
        echo.

        for /f "delims=" %%S in ('powershell -NoProfile -Command ^
            "$x=(Get-Item -LiteralPath '!OUTPUT!').Length; ^
             '{0:N2} MB' -f ($x/1MB)"') do echo Final size: %%S
    ) else (
        echo.
        echo WARNING:
        echo Could not create compressed PDF.
    )

    echo.
)

echo ============================================
echo All files processed.
echo ============================================
echo.
pause
exit /b


:: ==================================================
:: COMPRESSION FUNCTION
:: ==================================================

:compress

set "IN=%~1"
set "BEST=%~2"
set "OUT=%~3"
set "DPI=%~4"
set "JPG=%~5"
set "LIMIT=%~6"

echo Trying %DPI% DPI / JPEG quality %JPG%...

"%GS%" ^
    -q ^
    -dBATCH ^
    -dNOPAUSE ^
    -sDEVICE=pdfwrite ^
    -dCompatibilityLevel=1.7 ^
    -dDetectDuplicateImages=true ^
    -dCompressFonts=true ^
    -dSubsetFonts=true ^
    -dColorImageDownsampleType=/Bicubic ^
    -dColorImageResolution=%DPI% ^
    -dGrayImageDownsampleType=/Bicubic ^
    -dGrayImageResolution=%DPI% ^
    -dMonoImageDownsampleType=/Subsample ^
    -dMonoImageResolution=180 ^
    -dAutoFilterColorImages=false ^
    -dColorImageFilter=/DCTEncode ^
    -dJPEGQ=%JPG% ^
    -dAutoFilterGrayImages=false ^
    -dGrayImageFilter=/DCTEncode ^
    -dPDFSETTINGS=/default ^
    -sOutputFile="%OUT%" ^
    "%IN%"

if not exist "%OUT%" (
    echo   Failed.
    exit /b
)

for /f "delims=" %%S in ('powershell -NoProfile -Command ^
    "(Get-Item -LiteralPath '%OUT%').Length"') do set "SIZE=%%S"

echo   Result:
powershell -NoProfile -Command ^
    "'{0:N2} MB' -f (%SIZE%/1MB)"

if %SIZE% LEQ %LIMIT% (
    copy /y "%OUT%" "%BEST%" >nul
    del /q "%OUT%" >nul 2>&1
    set "FOUND=1"
    echo   Target reached.
    exit /b
)

echo   Still above target.
del /q "%OUT%" >nul 2>&1

exit /b