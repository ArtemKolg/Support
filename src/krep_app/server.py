# -*- coding: utf-8 -*-
"""Flask-приложение: маршруты загрузки файла и запуска расчёта."""

import os
import sys

import pandas as pd
from flask import Flask, Response, jsonify, render_template, request, send_file

from .calc import (
    REQUIRED_FIELDS,
    auto_match,
    build_excel,
    process_mine_workings,
    read_dataframe,
)


def _template_folder() -> str:
    # PyInstaller распаковывает данные в sys._MEIPASS при запуске из .exe
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, 'templates')
    return os.path.join(os.path.dirname(__file__), 'templates')


app = Flask(__name__, template_folder=_template_folder())
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024  # 64 МБ

# Хранилище загруженных датафреймов (однопользовательское локальное приложение).
SESSIONS: dict[str, pd.DataFrame] = {}


@app.route('/')
def index() -> Response:
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    f = request.files.get('file')
    if f is None:
        return jsonify({'error': 'Файл не передан'}), 400

    fmt = request.form.get('fmt', 'csv')
    csv_sep = request.form.get('sep', ',')
    csv_enc = request.form.get('enc', 'utf-8')

    try:
        df = read_dataframe(f.read(), fmt, csv_sep=csv_sep, csv_encoding=csv_enc)
    except Exception as e:
        return jsonify({'error': f'Не удалось прочитать файл: {e}'}), 400

    token = os.urandom(8).hex()
    SESSIONS[token] = df
    columns = [str(c) for c in df.columns]
    preview = df.head(8).astype(str).values.tolist()

    return jsonify({
        'token':   token,
        'columns': columns,
        'nrows':   int(len(df)),
        'preview': preview,
        'auto':    auto_match(columns),
    })


@app.route('/process', methods=['POST'])
def process():
    data = request.get_json(force=True)
    token = data.get('token')
    mapping = data.get('mapping', {})
    filename = (data.get('filename') or 'результат_крепления').strip()
    if not filename.lower().endswith('.xlsx'):
        filename += '.xlsx'

    df = SESSIONS.get(token)
    if df is None:
        return jsonify({'error': 'Данные не загружены. Сначала загрузите файл.'}), 400

    missing = [REQUIRED_FIELDS[k] for k in REQUIRED_FIELDS if not mapping.get(k)]
    if missing:
        return jsonify({'error': 'Не сопоставлены поля: ' + ', '.join(missing)}), 400

    try:
        input_df = pd.DataFrame({
            'name':     df[mapping['name']],
            'purpose':  df[mapping['purpose']],
            'category': df[mapping['category']].astype(str).str.strip(),
            'width':    df[mapping['width']],
        })
        result_df = process_mine_workings(input_df)
        bio = build_excel(result_df)
    except KeyError as e:
        return jsonify({'error': f'Столбец не найден: {e}'}), 400
    except Exception as e:
        return jsonify({'error': f'Ошибка обработки: {e}'}), 500

    return send_file(
        bio,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
