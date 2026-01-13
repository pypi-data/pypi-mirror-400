# worksheet-iterator

`worksheet-iterator` 提供一个基于 XlsxWriter 的 `WorkSheetIterator` 类，用于以链式方式在工作表中写入和格式化单元格。

## 安装

```bash
pip install worksheet-iterator
```

## 使用示例

下面的示例与仓库根目录下的 `demo.py` 一致，展示了如何使用 `WorkSheetIterator` 在工作表中链式写入数据：

```python
from worksheet_iterator import WorkSheetIterator

import xlsxwriter

wb = xlsxwriter.Workbook("demo.xlsx")

# 创建一个工作表迭代器，指向 Sheet1
it = WorkSheetIterator(wb, "Sheet1")

# 在第一个单元格写入 "ok"，然后移动到下一列写入 42
it.set_value("ok").next_column().set_value(42)

wb.close()
```

## 主要特性

- 基于 XlsxWriter 的工作表写入工具
- 支持链式调用（如 `set_value().next_column().set_value()`）
- 更易于组织和维护复杂的 Excel 写入逻辑

