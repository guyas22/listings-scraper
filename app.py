from flask import Flask, request, render_template, send_file
import asyncio
import os
import pandas as pd
from scraper import take_full_page_screenshot
from google_sheets_client import GoogleSheetsClient, DATABASE_SHEET_ID
from df import update_row_from_json
import base64

app = Flask(__name__)
sheets_client = GoogleSheetsClient()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    file_path = os.path.join('uploads', file.filename)
    file.save(file_path)
    asyncio.run(process_csv(file_path))
    return 'File uploaded and processed successfully.'

async def process_csv(file_path):
    input_data = pd.read_csv(file_path)
    db_data = sheets_client.save_sheet_to_df(DATABASE_SHEET_ID)
    screenshots_dir = 'screenshots'
    os.makedirs(screenshots_dir, exist_ok=True)

    for index, row in input_data.iterrows():
        original_url = row['URL']
        screenshot_path = os.path.join(screenshots_dir, f'screenshot_{index}.png')
        base64_img = await take_full_page_screenshot(original_url, screenshot_path)
        if base64_img:
            print(f"Processed URL {index + 1}/{len(input_data)}: {original_url}")
            parsed_json = parse_img_to_json(base64_img)
            updated_row = update_row_from_json(row, parsed_json)
            db_data = pd.concat([db_data, updated_row.to_frame().T], ignore_index=True)
        else:
            print(f"Skipped URL {index + 1}/{len(input_data)}: {original_url}")

    sheets_client.upload_df_to_sheet(db_data, DATABASE_SHEET_ID)

def parse_img_to_json(base64_img):
    # Replace with your OpenAI client code to parse image
    return {
        "Furnished": "Yes",
        "Parking": "Yes",
        "Price per square feet": 10
    }

if __name__ == '__main__':
    app.run(debug=True)
