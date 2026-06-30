#!/usr/bin/env bash
# Сборка krep_app в один исполняемый файл (macOS / Linux).
# Запуск: ./build.sh
set -e

echo "=== Сборка krep_app ==="

# Установить зависимости (включая pyinstaller)
uv sync

# Запустить PyInstaller через uv run
uv run pyinstaller krep_app.spec --noconfirm --clean

echo ""
echo "=== Готово ==="
echo "Исполняемый файл: dist/krep_app"
echo "Запуск: ./dist/krep_app"
