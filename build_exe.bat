@echo off
REM Сборка krep_app в .exe (Windows).
REM Запуск: build_exe.bat

echo === Сборка krep_app ===

uv sync
uv run pyinstaller krep_app.spec --noconfirm --clean

echo.
echo === Готово ===
echo Исполняемый файл: dist\krep_app.exe
pause
