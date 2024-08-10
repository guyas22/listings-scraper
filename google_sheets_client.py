import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import os

DATABASE_SHEET_ID = "1dmooq-6IlTZxCXsIgq7pY-46029Km2IJ-J2t8T_UGD0"

scopes = [
    "https://www.googleapis.com/auth/spreadsheets"
]

class GoogleSheetsClient:
    def __init__(self):
        # Create the service account credentials dictionary with environment variables
        creds_dict = {
            "type": "service_account",
            "project_id": "listings-scraper-431417",
            "private_key_id": os.getenv("PRIVATE_KEY_ID"),
            "private_key": os.getenv("PRIVATE_KEY").replace('\\n', '\n'),  # Replace literal \n with newline
            "client_email": "python-api@listings-scraper-431417.iam.gserviceaccount.com",
            "client_id": "105647197633534698815",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/python-api@listings-scraper-431417.iam.gserviceaccount.com",
            "universe_domain": "googleapis.com"
        }

        # Create credentials from the dictionary
        self.creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        
        print("Private key set")
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
