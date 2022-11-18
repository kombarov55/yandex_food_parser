import time

import xlsxwriter
from xlsxwriter import Workbook
from xlsxwriter.worksheet import Worksheet

from model.food import FoodVO


def to_csv(xs: list[FoodVO], path: str):
    workbook = xlsxwriter.Workbook(path)
    worksheet = workbook.add_worksheet()

    write_header(worksheet, workbook)
    row = 1
    for x in xs:
        col = 0
        worksheet.write(row, col, x.restaurant_id)
        col += 1
        worksheet.write(row, col, x.name)
        col += 1
        worksheet.write(row, col, x.price)
        col += 1
        worksheet.write(row, col, x.weight)
        col += 1
        row += 1

    workbook.close()


def write_header(worksheet: Worksheet, workbook: Workbook):
    bold = workbook.add_format({"bold": True})
    col = 0
    worksheet.write(0, col, "slug ресторана", bold)
    col += 1
    worksheet.write(0, col, "Название", bold)
    col += 1
    worksheet.write(0, col, "Цена", bold)
    col += 1
    worksheet.write(0, col, "Вес", bold)
    col += 1
