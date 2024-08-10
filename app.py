from flask import Flask, request, render_template, redirect, url_for
import asyncio
import os
import pandas as pd
from scraper import Scraper
from google_sheets_client import GoogleSheetsClient, DATABASE_SHEET_ID
from df import update_row_from_json, clean_dataframe
from openAI_client import OpenAIClient
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize clients with error handling
sheets_client_error = False
openai_client_error = False

try:
    sheets_client = GoogleSheetsClient(logger)
except Exception as e:
    sheets_client = None
    sheets_client_error = True
    logger.error(f"Failed to initialize Google Sheets Client: {e}")

try:
    openai_client = OpenAIClient(logger)
except Exception as e:
    openai_client = None
    openai_client_error = True
    logger.error(f"Failed to initialize OpenAI Client: {e}")

# Initialize the Scraper
scraper = Scraper(logger)

@app.route('/')
def index():
    if sheets_client_error or openai_client_error:
        return redirect(url_for('error_page'))
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if sheets_client_error or openai_client_error:
        return redirect(url_for('error_page'))

    # Ensure the uploads directory exists
    uploads_dir = 'uploads'
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)

    # Save the uploaded file
    file = request.files['file']
    file_path = os.path.join(uploads_dir, file.filename)
    file.save(file_path)

    # Process the file
    asyncio.run(process_csv(file_path))
    return 'File uploaded and processed successfully.'


@app.route('/error')
def error_page():
    error_messages = []
    if sheets_client_error:
        error_messages.append("Google Sheets Client failed to initialize.")
    if openai_client_error:
        error_messages.append("OpenAI Client failed to initialize.")
    return render_template('error.html', errors=error_messages)

async def process_csv(file_path):
    input_data = pd.read_csv(file_path)

    if not sheets_client:
        logger.error("Google Sheets Client is not initialized. Exiting process.")
        return
    
    db_data = sheets_client.save_sheet_to_df(DATABASE_SHEET_ID)
    new_data = db_data.copy()
    screenshots_dir = 'screenshots'
    os.makedirs(screenshots_dir, exist_ok=True)

    for index, row in input_data.iterrows():
        original_url = row['URL']
        screenshot_path = os.path.join(screenshots_dir, f'screenshot_{index}.png')
        base64_img = await scraper.take_full_page_screenshot(original_url, screenshot_path)
        if base64_img and openai_client:
            try:
                parsed_json = openai_client.parse_img_to_json(base64_img)
                updated_row = update_row_from_json(row, parsed_json)
                logger.info(f"updated_row: {updated_row}")
                new_data = pd.concat([new_data, updated_row.to_frame().T], ignore_index=True)
            except Exception as e:
                logger.error(f"Error parsing image or updating row: {e}")
        elif not openai_client:
            logger.error("OpenAI Client is not initialized. Skipping image parsing.")

    try:
        new_data = clean_dataframe(new_data)
        logger.info(f"New data \n --------------- \n{new_data}")
        sheets_client.upload_df_to_sheet(new_data, DATABASE_SHEET_ID)
    except Exception as e:
        logger.error(f"Error uploading data to Google Sheets: {e}")
        sheets_client.upload_df_to_sheet(db_data, DATABASE_SHEET_ID)

if __name__ == '__main__':
    app.run(debug=True)
