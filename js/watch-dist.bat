@echo off
setlocal enabledelayedexpansion

rem === Go to the folder where this .bat lives (works even for UNC paths) ===
pushd "%~dp0" >nul 2>&1
if errorlevel 1 (
    echo Failed to change directory to "%~dp0".
    pause
    exit /b 1
)

rem === CONFIG ===
rem Source: dist folder next to this .bat file
set "SRC=%CD%\dist"

rem Target:
rem  - if passed as 1st argument: use that
rem  - otherwise: "target" folder next to the .bat
if "%~1"=="" (
    set "DEST=F:\Games\World_of_Tanks_EU\res_mods\2.0.1.1\gui\gameface\mods\wotstat-debug-utils"
) else (
    set "DEST=%~1"
)

if not exist "%SRC%" (
    echo Source folder "%SRC%" does not exist: "%SRC%"
    pause
    exit /b 1
)

if not exist "%DEST%" (
    echo Creating target folder "%DEST%"
    mkdir "%DEST%"
)

echo Watching "%SRC%" and syncing to "%DEST%".
echo Press Ctrl+C to stop.
echo.

rem === MAIN LOOP (simple polling) ===
:loop
rem /MIR : mirror entire tree
rem /E   : copy subdirs
rem /W:1 : wait 1s between retries
rem /R:2 : retry twice on failures
rem /NFL /NDL /NJH /NJS /NP : quieter output
robocopy "%SRC%" "%DEST%" /MIR /E /W:1 /R:2 /NFL /NDL /NJH /NJS /NP >nul

rem Wait 2 seconds before checking again
timeout /t 2 /nobreak >nul

goto loop
