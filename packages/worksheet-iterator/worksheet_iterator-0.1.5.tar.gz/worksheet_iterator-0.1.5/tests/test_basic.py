import os

import xlsxwriter

from ws_utils import WorkSheetIterator


def test_create_basic_workbook(tmp_path):
    file_path = tmp_path / "test.xlsx"
    workbook = xlsxwriter.Workbook(str(file_path))

    it = WorkSheetIterator(workbook, "Sheet1")
    it.set_value("hello").next_column().set_value(123)

    workbook.close()

    assert os.path.exists(file_path)
