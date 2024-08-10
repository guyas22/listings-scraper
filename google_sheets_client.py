import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import os
import json

DATABASE_SHEET_ID = "1dmooq-6IlTZxCXsIgq7pY-46029Km2IJ-J2t8T_UGD0"

scopes = [
    "https://www.googleapis.com/auth/spreadsheets"
]

class GoogleSheetsClient:
    def __init__(self, logger):
        self.logger = logger

        try:
            if os.getenv("STAGE") == "local":
                self.logger.info("Initializing Google Sheets client in local stage.")
                private_key_id = os.getenv("PRIVATE_KEY_ID")
                private_key = os.getenv("PRIVATE_KEY")
                if not private_key or not private_key_id:
                    raise ValueError("PRIVATE_KEY_ID or PRIVATE_KEY environment variables are missing.")
                private_key = private_key.replace('\\n', '\n')  # Ensure proper newline formatting
            elif os.getenv("STAGE") == "prod":
                self.logger.info("Initializing Google Sheets client in production stage.")
                secret_string = os.getenv("MY_SECRET")
                if not secret_string:
                    raise ValueError("MY_SECRET environment variable is missing.")
                
                try:
                    secrets = json.loads(secret_string)
                    private_key_id = secrets.get('PRIVATE_KEY_ID')
                    private_key = secrets.get('PRIVATE_KEY')

                    if not private_key or not private_key_id:
                        raise KeyError("PRIVATE_KEY_ID or PRIVATE_KEY is missing in MY_SECRET.")
                    # Replace literal '\n' in the private key with actual newlines
                    private_key = private_key.replace(' ', '').replace('\n', '\n').replace('-----BEGINPRIVATEKEY-----', '-----BEGIN PRIVATE KEY-----\n').replace('-----ENDPRIVATEKEY-----', '\n-----END PRIVATE KEY-----')
                except json.JSONDecodeError as e:
                    self.logger.error(f"Failed to parse secrets from MY_SECRET: {e}")
                    raise
                except KeyError as e:
                    self.logger.error(f"KeyError: {e}")
                    raise
            else:
                raise ValueError("Unknown STAGE environment variable. It must be either 'local' or 'prod'.")

            # Create the service account credentials dictionary
            creds_dict = {
                "type": "service_account",
                "project_id": "listings-scraper-431417",
                "private_key_id": private_key_id,
                "private_key": private_key,
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
            self.logger.info("Private key set")

            # Authorize the Google Sheets client
            self.client = gspread.authorize(self.creds)
            self.logger.info("Google Sheets client initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize Google Sheets Client: {e}")
            raise

    def save_sheet_to_df(self, sheet_id):
        try:
            sheet = self.client.open_by_key(sheet_id)
            worksheet = sheet.get_worksheet(0)
            rows = worksheet.get_all_records()
            df = pd.DataFrame(rows)
            self.logger.info(f"Data fetched from sheet {sheet_id}")
            return df
        except Exception as e:
            self.logger.error(f"Failed to save sheet to DataFrame: {e}")
            raise

    def upload_df_to_sheet(self, df, sheet_id):
        try:
            sheet = self.client.open_by_key(sheet_id)
            worksheet = sheet.get_worksheet(0)
            worksheet.clear()
            worksheet.update([df.columns.values.tolist()] + df.values.tolist())
            self.logger.info("Data uploaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to upload DataFrame to sheet {sheet_id}: {e}")
            raise
