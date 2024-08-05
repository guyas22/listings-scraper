import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

DATABASE_SHEET_ID = "1dmooq-6IlTZxCXsIgq7pY-46029Km2IJ-J2t8T_UGD0"

scopes = [
    "https://www.googleapis.com/auth/spreadsheets"
]



class GoogleSheetsClient:
    def __init__(self):
        self.creds = Credentials.from_service_account_file("google_sheets_creds.json", scopes=scopes)
        self.client = gspread.authorize(self.creds)
        print("Google Sheets client initialized")
  
    def save_sheet_to_df(self, sheet_id):
        sheet = self.client.open_by_key(sheet_id)
        worksheet = sheet.get_worksheet(0)
        rows = worksheet.get_all_records()
        df = pd.DataFrame(rows)
        return df
    
    def upload_df_to_sheet(self, df, sheet_id):
        sheet = self.client.open_by_key(sheet_id)
        worksheet = sheet.get_worksheet(0)
        worksheet.clear()
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())
        print("Data uploaded successfully")

