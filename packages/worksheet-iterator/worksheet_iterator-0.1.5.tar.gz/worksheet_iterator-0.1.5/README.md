# worksheet-iterator

[English](README.md) | [中文](README.zh_CN.md)

`worksheet-iterator` provides a `WorkSheetIterator` class based on XlsxWriter, which lets you write and format cells in a worksheet with chainable calls.

## English

### Installation

```bash
pip install worksheet-iterator
```

### Usage example

The following example is the same as `demo.py` in the repository root. It shows how to use `WorkSheetIterator` to write data to a worksheet in a chainable way:

```python
from worksheet_iterator import WorkSheetIterator

import xlsxwriter

wb = xlsxwriter.Workbook("demo.xlsx")

# Create a worksheet iterator that points to "Sheet1"
it = WorkSheetIterator(wb, "Sheet1")

# Write "ok" to the first cell, then move to the next column and write 42
it.set_value("ok").next_column().set_value(42)

wb.close()
```

### Key features

- Utility for writing Excel worksheets based on XlsxWriter
- Supports chainable calls (such as `set_value().next_column().set_value()`)
- Makes it easier to organize and maintain complex Excel writing logic

