import gspread
from gspread.client import Client
from gspread.spreadsheet import Spreadsheet
from gspread.worksheet import Worksheet

class GoogleSheetsEditor:
    def __init__(self, sheet_url: str, creds_file: str = './service_account.json', sheet_name: str = None) -> None:
        self.gc: Client = None
        self.sh: Spreadsheet = None
        self.wh: Worksheet = None

        self.gc = gspread.service_account(creds_file)
        self.sh = self.gc.open_by_url(sheet_url)
        if sheet_name:
            self.wh = self.sh.worksheet(sheet_name)

    def worksheet(self, sheet_name: str):
        self.wh = self.sh.worksheet(sheet_name)
        return self.wh

    def find_col_index(self, col_name: str) -> int:
        if not self.wh:
            raise ValueError('Open worksheet first')

        cell = self.wh.find(col_name)
        if not cell:
            raise ValueError('not found')
        
        return cell.col
