# -*- coding: utf-8 -*-
"""Логика расчёта параметров крепления горных выработок."""

import io

import pandas as pd

from .data import df_krep, df_mesh

REQUIRED_FIELDS = {
    'name':     'Название выработки',
    'purpose':  'Назначение (тип) выработки',
    'category': 'Категория нарушенности',
    'width':    'Ширина выработки, м',
}


def find_anchoring_params(purpose: str, category: str, width: float) -> dict | None:
    filtered = df_mesh[
        (df_mesh['category'] == category) &
        (df_mesh['purpose'].str.contains(str(purpose), na=False))
    ]
    for _, row in filtered.iterrows():
        if row['width_range_min'] <= width <= row['width_range_max']:
            return {
                'step_anchoring': f"{row['mesh_spacing_a']}×{row['mesh_spacing_b']} м",
                'anchoring_depth': row['anchoring_depth'],
            }
    return None


def find_support_params(category: str) -> dict | None:
    row = df_krep[df_krep['Q'] == str(category).strip()]
    if not row.empty:
        return {
            'temp_support':     row['Временной крепи'].iloc[0],
            'temp_support_lag': row['Отставание временной крепи, м'].iloc[0],
            'perm_support':     row['Постоянной крепи'].iloc[0],
            'perm_support_lag': row['Отставание постоянной крепи, м'].iloc[0],
        }
    return None


def process_mine_workings(input_df: pd.DataFrame) -> pd.DataFrame:
    """Принимает DataFrame с колонками name/purpose/category/width, возвращает расчёт."""
    results = []
    for _, row in input_df.iterrows():
        try:
            width = float(str(row['width']).replace(',', '.'))
        except (ValueError, TypeError):
            width = None

        anchoring = (
            find_anchoring_params(row['purpose'], row['category'], width)
            if width is not None else None
        )
        support = find_support_params(row['category'])

        results.append({
            'Название выработки':            row['name'],
            'Категория':                      row['category'],
            'Параметры временного крепления': support['temp_support']     if support   else 'Не найдено',
            'Глубина анкерования, м':         anchoring['anchoring_depth'] if anchoring else 'Не найдено',
            'Шаг анкерования':               anchoring['step_anchoring']  if anchoring else 'Не найдено',
            'Отставание временной крепи, м':  support['temp_support_lag'] if support   else 'Не найдено',
            'Параметры постоянного крепления': support['perm_support']    if support   else 'Не найдено',
            'Отставание постоянного крепления, м': support['perm_support_lag'] if support else 'Не найдено',
        })
    return pd.DataFrame(results)


def read_dataframe(
    file_bytes: bytes,
    fmt: str,
    csv_sep: str = ',',
    csv_encoding: str = 'utf-8',
) -> pd.DataFrame:
    fmt = fmt.lower()
    bio = io.BytesIO(file_bytes)
    if fmt == 'csv':
        sep = '\t' if csv_sep in ('\\t', 'tab', 'таб') else csv_sep
        return pd.read_csv(bio, sep=sep, encoding=csv_encoding)
    if fmt in ('excel', 'xlsx', 'xls'):
        return pd.read_excel(bio)
    if fmt == 'json':
        return pd.read_json(bio)
    raise ValueError(f'Неподдерживаемый формат: {fmt}')


def build_excel(result_df: pd.DataFrame) -> io.BytesIO:
    """Возвращает BytesIO с .xlsx (перенос текста + автоширина колонок)."""
    bio = io.BytesIO()
    with pd.ExcelWriter(bio, engine='openpyxl') as writer:
        result_df.to_excel(writer, index=False, sheet_name='Крепление')
        ws = writer.sheets['Крепление']
        for col_cells in ws.columns:
            letter = col_cells[0].column_letter
            max_len = 0
            for cell in col_cells:
                if cell.value is not None:
                    longest = max((len(s) for s in str(cell.value).split('\n')), default=0)
                    max_len = max(max_len, longest)
                    cell.alignment = cell.alignment.copy(wrap_text=True, vertical='top')
            ws.column_dimensions[letter].width = min(max_len + 2, 60)
    bio.seek(0)
    return bio


def auto_match(columns: list[str]) -> dict[str, str]:
    """Пытается автоматически сопоставить столбцы с требуемыми полями."""
    cols_lower = {str(c).lower().strip(): c for c in columns}
    aliases = {
        'name':     ['name', 'название', 'название выработки', 'выработка', 'наименование'],
        'purpose':  ['purpose', 'назначение', 'тип', 'назначение выработки'],
        'category': ['category', 'категория', 'категория нарушенности', 'q'],
        'width':    ['width', 'ширина', 'ширина выработки', 'ширина, м'],
    }
    out = {}
    for key, names in aliases.items():
        for n in names:
            if n in cols_lower:
                out[key] = cols_lower[n]
                break
    return out
