from worksheet_iterator import WorkSheetIterator

import xlsxwriter
wb = xlsxwriter.Workbook("demo.xlsx")
it = WorkSheetIterator(wb, "Sheet1")
it.set_value("ok").next_column().set_value(42)
wb.close()