from dotenv import load_dotenv
import os

import gspread
from gspread_formatting import *
import pandas as pd
from mail_reader import obtener_gastos

load_dotenv()

JSON_PATH = os.getenv('JSON_PATH')
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')

df = obtener_gastos (
    EMAIL,
    PASSWORD,
    label="Banco"
)

if not df.empty:
    # Loading the credentials
    gc = gspread.service_account(filename=JSON_PATH)
    sh = gc.open("gastos")
    worksheet = sh.worksheet("reporte_banco")

    df = df.fillna("")
    print(df)
    worksheet.append_rows(df.values.tolist())

    # formato

    fmt = CellFormat(
        textFormat=TextFormat(
            fontFamily='arial',
            fontSize=11
        )
    )

    rows = worksheet.row_count
    cols = worksheet.col_count

    from gspread.utils import rowcol_to_a1
    rango = f"A1:{rowcol_to_a1(rows, cols)}"

    format_cell_range(worksheet, rango, fmt)
