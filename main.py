# main.py
import asyncio
import os
import pandas as pd
from scraper import *
from openAI_client import *
from google_sheets_client import *
from df import *


async def csv_run():
    # Load the CSV file
    file_path = 'PropertyData_rents_long_let_2024-05-28.csv'
    data = pd.read_csv(file_path)
    
    # Create a directory for screenshots if it doesn't exist
    screenshots_dir = 'screenshots'
    os.makedirs(screenshots_dir, exist_ok=True)
    
    # Iterate over the URLs and take screenshots
    for index, row in data.iterrows():
        original_url = row['URL']
        screenshot_path = os.path.join(screenshots_dir, f'screenshot_{index}.png')
        
        # Take a full-page screenshot of the webpage
        base64_img = await take_full_page_screenshot(original_url, screenshot_path)
        if base64_img:
            print(f"Processed URL {index + 1}/{len(data)}: {original_url}")
        else:
            print(f"Skipped URL {index + 1}/{len(data)}: {original_url}")



async def single_run():
    # URL to take a screenshot of
    url = 'https://www.zoopla.co.uk/to-rent/details/58595185'
    
    # Take a full-page screenshot of the webpage
    screenshot_path = 'screenshot.png'
    base64_img = await take_full_page_screenshot(url, screenshot_path)
    if base64_img:
        print(f"Screenshot saved to {screenshot_path}")
        parse_img_to_json(base64_img)
    else:
        print(f"Failed to take a screenshot of {url}")
    
    sheets_client = GoogleSheetsClient()
    sheets_client.add_data_to_sheet(mock_json)
    

async def csv_run_dev():
    # Load the CSV file
    file_path = 'PropertyData_rents_long_let_2024-05-28.csv'
    input_data = pd.read_csv(file_path)
    sheets_client = GoogleSheetsClient()
    db_data = sheets_client.save_sheet_to_df(DATABASE_SHEET_ID)
    
    # Create a directory for screenshots if it doesn't exist
    screenshots_dir = 'screenshots'
    os.makedirs(screenshots_dir, exist_ok=True)
    
    # Iterate over the URLs and take screenshots
    for index, row in input_data.iterrows():
        original_url = row['URL']
        screenshot_path = os.path.join(screenshots_dir, f'screenshot_{index}.png')
       
        # Take a full-page screenshot of the webpage
        base64_img = await take_full_page_screenshot(original_url, screenshot_path)
        # if base64_img:
        #     print(f"Processed URL {index + 1}/{len(data)}: {original_url}")
        #     parsed_json = parse_img_to_json(base64_img)
        # else:
        #     print(f"Skipped URL {index + 1}/{len(data)}: {original_url}")
        parsed_json = {
            "Furnished": "Yes",
            "Parking": "Yes",
            "Price per square feet": 10
        }
        # Add the extracted data to the Google Sheet
        updated_row = update_row_from_json(row, parsed_json)
        db_data = pd.concat([db_data, updated_row.to_frame().T], ignore_index=True)
    
    # Upload the updated DataFrame to the Google Sheet
    sheets_client.upload_df_to_sheet(db_data, DATABASE_SHEET_ID)


        


if __name__ == "__main__":
    asyncio.run(csv_run_dev())
