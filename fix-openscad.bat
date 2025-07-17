@echo off
echo Deleting OpenSCAD registry key...
reg delete "HKEY_CURRENT_USER\Software\OpenSCAD\OpenSCAD" /f
if %errorlevel% == 0 (
    echo Registry key deleted successfully!
) else (
    echo Failed to delete registry key or key doesn't exist.
)
pause