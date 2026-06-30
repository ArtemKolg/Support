# -*- coding: utf-8 -*-
"""Точка входа: запуск локального сервера и открытие браузера."""

import socket
import threading
import webbrowser

from .server import app


def _free_port(preferred: int = 5000) -> int:
    for p in (preferred, 5001, 5050, 8080, 0):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('127.0.0.1', p))
            port = s.getsockname()[1]
            s.close()
            return port
        except OSError:
            continue
    return preferred


def main() -> None:
    port = _free_port(5000)
    url = f'http://127.0.0.1:{port}/'
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    print('=' * 56)
    print('  Расчёт параметров крепления — приложение запущено')
    print(f'  Откройте в браузере: {url}')
    print('  Чтобы остановить — закройте это окно.')
    print('=' * 56)
    app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False, threaded=True)


if __name__ == '__main__':
    main()
