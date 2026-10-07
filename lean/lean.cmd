@echo off
REM Compile the Lean development in this directory against the local mathlib.
setlocal
set "LEAN=E:\study\AImath\.local-lean\toolchain\bin\lean.exe"
set "PKGS=E:\study\AImath\.local-lean\S6Isserlis\.lake\packages"
set "LEAN_PATH=%PKGS%\aesop\.lake\build\lib\lean;%PKGS%\batteries\.lake\build\lib\lean;%PKGS%\importGraph\.lake\build\lib\lean;%PKGS%\LeanSearchClient\.lake\build\lib\lean;%PKGS%\mathlib\.lake\build\lib\lean;%PKGS%\plausible\.lake\build\lib\lean;%PKGS%\proofwidgets\.lake\build\lib\lean;%PKGS%\Qq\.lake\build\lib\lean;E:\study\AImath\.local-lean\toolchain\lib\lean"
"%LEAN%" %*
endlocal
