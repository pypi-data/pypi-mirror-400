try:
    import openpyxl
except Exception:
    openpyxl = None

from .csv import flattenObject, extractFieldNames
from django.http import HttpResponse


def write_fields_to_row(sheet, fields, row=1):
    for col, field in enumerate(fields, start=1):
        sheet.cell(row=row, column=col, value=field)


def qsetToExcel(request, qset, fields, name):
    # Create a new Excel workbook
    workbook = openpyxl.Workbook()

    # Get the active sheet (by default, there's one sheet in a new workbook)
    sheet = workbook.active
    header, field_names = extractFieldNames(fields)

    write_fields_to_row(sheet, header)
    row = 1
    for item in qset:
        row += 1
        write_fields_to_row(sheet, flattenObject(item, field_names), row)

    # Create an HTTP response with the Excel file content
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename={name}.xlsx'

    # Save the workbook to the response
    workbook.save(response)

    return response

