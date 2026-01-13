from __future__ import annotations

import xlsxwriter
from typing import List, Dict, Any, Tuple, Optional, Union


class WorkSheetIterator:
    """XlsxWriter工作表迭代器，提供链式调用接口"""

    def __init__(self, workbook: xlsxwriter.Workbook, name: str):
        self.wb = workbook
        self.row: int = 0
        self.column: int = 0
        self.name: str = name
        self.ws = workbook.add_worksheet(name)

        self._bookmark_stack = []
        self._named_bookmarks = {}

        self._format_props = {
            'thin_border': {
                'border': 1,
                'border_color': '#CCCCCC',
                'valign': 'vcenter',
                'font_size': 11,
                'font_color': '#000000'
            },
            'bold': {
                'bold': True,
                'border': 1,
                'border_color': '#CCCCCC',
                'valign': 'vcenter',
                'font_size': 11,
                'font_color': '#000000'
            },
            'header': {
                'bold': True,
                'border': 1,
                'border_color': '#CCCCCC',
                'align': 'left',
                'valign': 'vcenter',
                'font_size': 12,
                'font_color': '#000000'
            },
            'left_align': {
                'align': 'left',
                'border': 1,
                'border_color': '#CCCCCC',
                'valign': 'vcenter',
                'font_size': 11,
                'font_color': '#000000'
            },
            'right_align': {
                'align': 'right',
                'border': 1,
                'border_color': '#CCCCCC',
                'valign': 'vcenter',
                'font_size': 11,
                'font_color': '#000000'
            },
            'center_align': {
                'align': 'center',
                'border': 1,
                'border_color': '#CCCCCC',
                'valign': 'vcenter',
                'font_size': 11,
                'font_color': '#000000'
            },
            'percent': {
                'num_format': '0.0%',
                'align': 'right',
                'border': 1,
                'border_color': '#CCCCCC',
                'valign': 'vcenter',
                'font_size': 11,
                'font_color': '#000000'
            },
            'percent_left': {
                'num_format': '0.0%',
                'align': 'left',
                'border': 1,
                'border_color': '#CCCCCC',
                'valign': 'vcenter',
                'font_size': 11,
                'font_color': '#000000'
            },
            'percent_center': {
                'num_format': '0.0%',
                'align': 'center',
                'border': 1,
                'border_color': '#CCCCCC',
                'valign': 'vcenter',
                'font_size': 11,
                'font_color': '#000000'
            },
            'percent_right': {
                'num_format': '0.0%',
                'align': 'right',
                'border': 1,
                'border_color': '#CCCCCC',
                'valign': 'vcenter',
                'font_size': 11,
                'font_color': '#000000'
            },
            'bold_left': {
                'bold': True,
                'align': 'left',
                'border': 1,
                'border_color': '#CCCCCC',
                'valign': 'vcenter',
                'font_size': 11,
                'font_color': '#000000'
            },
            'bold_right': {
                'bold': True,
                'align': 'right',
                'border': 1,
                'border_color': '#CCCCCC',
                'valign': 'vcenter',
                'font_size': 11,
                'font_color': '#000000'
            },
            'bold_center': {
                'bold': True,
                'align': 'center',
                'border': 1,
                'border_color': '#CCCCCC',
                'valign': 'vcenter',
                'font_size': 11,
                'font_color': '#000000'
            },
            'number_format': {
                'num_format': '#,##0',
                'align': 'right',
                'border': 1,
                'border_color': '#CCCCCC',
                'valign': 'vcenter',
                'font_size': 11,
                'font_color': '#000000'
            },
            'white_font': {
                'font_color': '#FFFFFF',
                'border': 1,
                'border_color': '#CCCCCC',
                'valign': 'vcenter',
                'font_size': 11
            }
        }

        self._format_cache = {}

    @classmethod
    def from_existing_worksheet(cls, workbook: xlsxwriter.Workbook, worksheet_name: str, start_row: int = 0, start_col: int = 0):
        worksheets = workbook.worksheets()
        target_sheet = None
        for ws in worksheets:
            if ws.name == worksheet_name:
                target_sheet = ws
                break

        if not target_sheet:
            raise ValueError(f"工作表 '{worksheet_name}' 不存在")

        wsi = cls.__new__(cls)
        wsi.wb = workbook
        wsi.ws = target_sheet
        wsi.name = worksheet_name
        wsi.row = start_row
        wsi.column = start_col

        wsi._bookmark_stack = []
        wsi._named_bookmarks = {}
        wsi._format_props = {
            'thin_border': {
                'border': 1,
                'border_color': '#CCCCCC',
                'valign': 'vcenter',
                'font_size': 11,
                'font_color': '#000000'
            },
            'bold': {
                'bold': True,
                'border': 1,
                'border_color': '#CCCCCC',
                'valign': 'vcenter',
                'font_size': 11,
                'font_color': '#000000'
            },
            'header': {
                'bold': True,
                'border': 1,
                'border_color': '#CCCCCC',
                'align': 'left',
                'valign': 'vcenter',
                'font_size': 12,
                'font_color': '#000000'
            },
            'left_align': {
                'align': 'left',
                'border': 1,
                'border_color': '#CCCCCC',
                'valign': 'vcenter',
                'font_size': 11,
                'font_color': '#000000'
            },
            'right_align': {
                'align': 'right',
                'border': 1,
                'border_color': '#CCCCCC',
                'valign': 'vcenter',
                'font_size': 11,
                'font_color': '#000000'
            },
            'center_align': {
                'align': 'center',
                'border': 1,
                'border_color': '#CCCCCC',
                'valign': 'vcenter',
                'font_size': 11,
                'font_color': '#000000'
            },
            'percent': {
                'num_format': '0.0%',
                'align': 'right',
                'border': 1,
                'border_color': '#CCCCCC',
                'valign': 'vcenter',
                'font_size': 11,
                'font_color': '#000000'
            },
            'percent_left': {
                'num_format': '0.0%',
                'align': 'left',
                'border': 1,
                'border_color': '#CCCCCC',
                'valign': 'vcenter',
                'font_size': 11,
                'font_color': '#000000'
            },
            'percent_center': {
                'num_format': '0.0%',
                'align': 'center',
                'border': 1,
                'border_color': '#CCCCCC',
                'valign': 'vcenter',
                'font_size': 11,
                'font_color': '#000000'
            },
            'percent_right': {
                'num_format': '0.0%',
                'align': 'right',
                'border': 1,
                'border_color': '#CCCCCC',
                'valign': 'vcenter',
                'font_size': 11,
                'font_color': '#000000'
            },
            'bold_left': {
                'bold': True,
                'align': 'left',
                'border': 1,
                'border_color': '#CCCCCC',
                'valign': 'vcenter',
                'font_size': 11,
                'font_color': '#000000'
            },
            'bold_right': {
                'bold': True,
                'align': 'right',
                'border': 1,
                'border_color': '#CCCCCC',
                'valign': 'vcenter',
                'font_size': 11,
                'font_color': '#000000'
            },
            'bold_center': {
                'bold': True,
                'align': 'center',
                'border': 1,
                'border_color': '#CCCCCC',
                'valign': 'vcenter',
                'font_size': 11,
                'font_color': '#000000'
            },
            'number_format': {
                'num_format': '#,##0',
                'align': 'right',
                'border': 1,
                'border_color': '#CCCCCC',
                'valign': 'vcenter',
                'font_size': 11,
                'font_color': '#000000'
            },
            'white_font': {
                'font_color': '#FFFFFF',
                'border': 1,
                'border_color': '#CCCCCC',
                'valign': 'vcenter',
                'font_size': 11
            }
        }
        wsi._format_cache = {}
        return wsi

    def _get_format(self, format_name: str) -> xlsxwriter.format.Format:
        if format_name not in self._format_cache:
            if format_name in self._format_props:
                self._format_cache[format_name] = self.wb.add_format(self._format_props[format_name])
            else:
                return self.wb.add_format(self._format_props['thin_border'])
        return self._format_cache[format_name]

    def combine_formats(self, *format_names: str) -> xlsxwriter.format.Format:
        combined_props: Dict[str, Any] = {}
        for name in format_names:
            if name in self._format_props:
                combined_props.update(self._format_props[name])
        return self.wb.add_format(combined_props)

    @property
    def thin_border(self):
        return self._get_format('thin_border')

    @property
    def bold_format(self):
        return self._get_format('bold')

    @property
    def header_format(self):
        return self._get_format('header')

    @property
    def left_align_format(self):
        return self._get_format('left_align')

    @property
    def right_align_format(self):
        return self._get_format('right_align')

    @property
    def center_align_format(self):
        return self._get_format('center_align')

    @property
    def percent_format(self):
        return self._get_format('percent')

    @property
    def percent_left_format(self):
        return self._get_format('percent_left')

    @property
    def percent_center_format(self):
        return self._get_format('percent_center')

    @property
    def percent_right_format(self):
        return self._get_format('percent_right')

    @property
    def bold_left_format(self):
        return self._get_format('bold_left')

    @property
    def bold_right_format(self):
        return self._get_format('bold_right')

    @property
    def bold_center_format(self):
        return self._get_format('bold_center')

    @property
    def number_format(self):
        return self._get_format('number_format')

    @property
    def white_font_format(self):
        return self._get_format('white_font')

    def define_name(self, name: str, formula: str):
        self.wb.define_name(name, formula)
        return self

    def set_format_value(self, cell_ref: str, cell_format=None):
        formula = f"""=LET(总值,{cell_ref},IF(总值>=亿阈值,LET(转换值,总值/亿单位,IF(转换值=INT(转换值),TEXT(转换值,"0")&"亿",TEXT(转换值,"0.###")&"亿")),IF(总值>=万阈值,LET(转换值,总值/万单位,IF(转换值=INT(转换值),TEXT(转换值,"0")&"万",TEXT(转换值,"0.###")&"万")),TEXT(总值,"0"))))"""
        format_to_use = cell_format or self.right_align_format
        self.ws.write_formula(self.row, self.column, formula, format_to_use)
        return self

    def set_format_right(self, cell_format=None):
        right_cell = self.get_cell_ref(self.row, self.column + 1)
        return self.set_format_value(right_cell, cell_format)

    def set_format_left(self, cell_format=None):
        left_cell = self.get_cell_ref(self.row, self.column - 1)
        return self.set_format_value(left_cell, cell_format)

    def set_font_size(self, size: int, cell_format=None):
        new_format_props: Dict[str, Any] = {}
        if cell_format and hasattr(cell_format, '__dict__'):
            valid_keys = {
                'bold', 'italic', 'underline', 'font_name', 'font_size',
                'font_color', 'strikeout', 'superscript', 'subscript',
                'num_format', 'locked', 'hidden', 'align', 'valign',
                'rotation', 'text_wrap', 'text_justlast', 'reading_order',
                'indent', 'shrink', 'pattern', 'bg_color', 'fg_color',
                'border', 'border_color', 'left', 'right',
                'top', 'bottom', 'left_color', 'right_color', 'top_color',
                'bottom_color', 'diag_type', 'diag_border', 'diag_color',
                'font_family', 'font_scheme',
                'font_outline', 'font_shadow', 'font_condense', 'font_extend',
                'theme', 'color_indexed'
            }
            for key, value in cell_format.__dict__.items():
                if key in valid_keys and value is not None:
                    new_format_props[key] = value
        else:
            new_format_props.update(self._format_props['thin_border'])

        new_format_props['font_size'] = size
        new_format = self.wb.add_format(new_format_props)
        return new_format

    def set_font_color(self, color: str, cell_format=None):
        new_format_props: Dict[str, Any] = {}
        if cell_format and hasattr(cell_format, '__dict__'):
            valid_keys = {
                'bold', 'italic', 'underline', 'font_name', 'font_size',
                'font_color', 'strikeout', 'superscript', 'subscript',
                'num_format', 'locked', 'hidden', 'align', 'valign',
                'rotation', 'text_wrap', 'text_justlast', 'reading_order',
                'indent', 'shrink', 'pattern', 'bg_color', 'fg_color',
                'border', 'border_color', 'left', 'right',
                'top', 'bottom', 'left_color', 'right_color', 'top_color',
                'bottom_color', 'diag_type', 'diag_border', 'diag_color',
                'font_family', 'font_scheme',
                'font_outline', 'font_shadow', 'font_condense', 'font_extend',
                'theme', 'color_indexed'
            }
            for key, value in cell_format.__dict__.items():
                if key in valid_keys and value is not None:
                    new_format_props[key] = value
        else:
            new_format_props.update(self._format_props['thin_border'])

        new_format_props['font_color'] = color
        new_format = self.wb.add_format(new_format_props)
        return new_format

    def set_font_style(self, size: int = None, color: str = None, bold: bool = None, cell_format=None):
        new_format_props: Dict[str, Any] = {}
        if cell_format and hasattr(cell_format, '__dict__'):
            valid_keys = {
                'bold', 'italic', 'underline', 'font_name', 'font_size',
                'font_color', 'strikeout', 'superscript', 'subscript',
                'num_format', 'locked', 'hidden', 'align', 'valign',
                'rotation', 'text_wrap', 'text_justlast', 'reading_order',
                'indent', 'shrink', 'pattern', 'bg_color', 'fg_color',
                'border', 'border_color', 'left', 'right',
                'top', 'bottom', 'left_color', 'right_color', 'top_color',
                'bottom_color', 'diag_type', 'diag_border', 'diag_color',
                'font_family', 'font_scheme',
                'font_outline', 'font_shadow', 'font_condense', 'font_extend',
                'theme', 'color_indexed'
            }
            for key, value in cell_format.__dict__.items():
                if key in valid_keys and value is not None:
                    new_format_props[key] = value
        else:
            new_format_props.update(self._format_props['thin_border'])

        if size is not None:
            new_format_props['font_size'] = size
        if color is not None:
            new_format_props['font_color'] = color
        if bold is not None:
            new_format_props['bold'] = bold

        new_format = self.wb.add_format(new_format_props)
        return new_format

    def get_cell_ref(self, row_or_tuple: Optional[Union[int, Tuple[int, int]]] = None, col: Optional[int] = None) -> str:
        if row_or_tuple is not None and isinstance(row_or_tuple, tuple):
            row = row_or_tuple[0]
            col = row_or_tuple[1]
        else:
            row = row_or_tuple if row_or_tuple is not None else self.row
            col = col if col is not None else self.column

        excel_row = row + 1
        col_letter = ''
        col_temp = col
        while col_temp >= 0:
            col_letter = chr(col_temp % 26 + ord('A')) + col_letter
            col_temp = col_temp // 26 - 1
            if col_temp < 0:
                break

        return f"{col_letter}{excel_row}"

    def get_current_cell_ref(self) -> str:
        return self.get_cell_ref()

    def get_range_ref(self, row1: int, col1: int, row2: int, col2: int) -> str:
        cell1 = self.get_cell_ref(row1, col1)
        cell2 = self.get_cell_ref(row2, col2)
        return f"{cell1}:{cell2}"

    def get_current_range_ref(self, rows: int = 1, cols: int = 1) -> str:
        return self.get_range_ref(self.row, self.column, self.row + rows - 1, self.column + cols - 1)

    def push_bookmark(self, name: str = None) -> str:
        bookmark_id = name if name else f"bookmark_{len(self._bookmark_stack)}"
        self._bookmark_stack.append({
            'id': bookmark_id,
            'row': self.row,
            'column': self.column
        })
        return bookmark_id

    def pop_bookmark(self) -> dict:
        if not self._bookmark_stack:
            raise IndexError("书签栈为空，无法弹出书签")

        bookmark = self._bookmark_stack.pop()
        self.row = bookmark['row']
        self.column = bookmark['column']
        return bookmark

    def set_bookmark(self, name: str) -> None:
        self._named_bookmarks[name] = {
            'row': self.row,
            'column': self.column
        }

    def goto_bookmark(self, name: str) -> dict:
        if name in self._named_bookmarks:
            bookmark = self._named_bookmarks[name]
            self.row = bookmark['row']
            self.column = bookmark['column']
            return bookmark

        for bookmark in reversed(self._bookmark_stack):
            if bookmark['id'] == name:
                self.row = bookmark['row']
                self.column = bookmark['column']
                return bookmark

        raise KeyError(f"书签 '{name}' 不存在")

    def has_bookmark(self, name: str) -> bool:
        if name in self._named_bookmarks:
            return True
        for bookmark in self._bookmark_stack:
            if bookmark['id'] == name:
                return True
        return False

    def get_bookmark_position(self, name: str) -> tuple:
        if name in self._named_bookmarks:
            bookmark = self._named_bookmarks[name]
            return (bookmark['row'], bookmark['column'])
        for bookmark in self._bookmark_stack:
            if bookmark['id'] == name:
                return (bookmark['row'], bookmark['column'])
        raise KeyError(f"书签 '{name}' 不存在")

    def clear_bookmarks(self) -> None:
        self._bookmark_stack.clear()
        self._named_bookmarks.clear()

    def list_bookmarks(self) -> list:
        bookmarks = []
        for bookmark in self._bookmark_stack:
            bookmarks.append({
                'id': bookmark['id'],
                'type': 'stack',
                'position': f"({bookmark['row']}, {bookmark['column']})",
                'cell_ref': self.get_cell_ref(bookmark['row'], bookmark['column'])
            })
        for name, bookmark in self._named_bookmarks.items():
            bookmarks.append({
                'id': name,
                'type': 'named',
                'position': f"({bookmark['row']}, {bookmark['column']})",
                'cell_ref': self.get_cell_ref(bookmark['row'], bookmark['column'])
            })
        return bookmarks

    def goto_top_left(self):
        self.row = 0
        self.column = 0
        return self

    def next_row(self, add: int = 1):
        self.row += add
        return self

    def next_column(self, add: int = 1):
        self.column += add
        return self

    def move_to(self, row: int, column: int):
        self.row = row
        self.column = column
        return self

    def goto_row(self, row: int):
        self.row = row
        return self

    def goto_column(self, column: int):
        self.column = column
        return self

    def go_line_begin(self):
        self.column = 0
        return self

    def set_value(self, value: Any, cell_format=None):
        format_to_use = cell_format or self.thin_border
        if isinstance(value, (int, float)) and cell_format:
            self.ws.write_number(self.row, self.column, value, format_to_use)
        else:
            self.ws.write(self.row, self.column, value, format_to_use)
        return self

    def set_formula(self, formula: str, cell_format=None):
        format_to_use = cell_format or self.thin_border
        self.ws.write_formula(self.row, self.column, formula, format_to_use)
        return self

    def set_percent(self, value: float, cell_format=None):
        format_to_use = cell_format or self.percent_format
        self.ws.write_number(self.row, self.column, value / 100.0, format_to_use)
        return self

    def set_percent_from_decimal(self, value: float, cell_format=None):
        format_to_use = cell_format or self.percent_format
        self.ws.write_number(self.row, self.column, value, format_to_use)
        return self

    def set_number(self, value: float, decimals: int = 2, cell_format=None):
        if cell_format is None:
            cell_format = self.wb.add_format({
                'num_format': f'0.{("0" * decimals) if decimals > 0 else ""}',
                'align': 'right',
                'border': 1,
                'border_color': '#CCCCCC'
            })
        self.ws.write_number(self.row, self.column, value, cell_format)
        return self

    def set_formula_percent(self, formula: str, cell_format=None):
        format_to_use = cell_format or self.percent_format
        self.ws.write_formula(self.row, self.column, formula, format_to_use)
        return self

    def merge_cells(self, rows: int, cols: int, value: Any = None, cell_format=None):
        format_to_use = cell_format or self.thin_border
        self.ws.merge_range(
            self.row, self.column,
            self.row + rows - 1, self.column + cols - 1,
            value if value is not None else '',
            format_to_use
        )
        return self

    def set_range_value(self, values: List[List[Any]], start_row=None, start_col=None, cell_format=None):
        start_row = start_row if start_row is not None else self.row
        start_col = start_col if start_col is not None else self.column
        for i, row_data in enumerate(values):
            for j, value in enumerate(row_data):
                self.ws.write(start_row + i, start_col + j, value, cell_format)
        return self

    def set_column_width(self, cols: List[Dict[str, Any]]):
        for col_spec in cols:
            self.ws.set_column(col_spec['cols'], col_spec['width'])
        return self

    def hide_columns(self, col_ranges: List[str]):
        for col_range in col_ranges:
            self.ws.set_column(col_range, None, None, {'hidden': True})
        return self
