# main.py
import asyncio
import os
import pandas as pd
from scraper import *
from openAI_client import *
# from google_sheets_client import *
# from google_sheets_client import GoogleSheetsClient

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
    else:
        print(f"Failed to take a screenshot of {url}")
    parse_img_to_json(base64_img)
    # mock_json = {
    #     "Furnished": "Yes",
    #     "Parking": "Yes",
    #     "Bedrooms": 2,
    #     "Asking Rent": 1500,
    #     "Price per square feet": 10
    # }
    # # Add the extracted data to the Google Sheet
    # sheets_client = GoogleSheetsClient()
    # sheets_client.add_data_to_sheet(mock_json)
    


if __name__ == "__main__":
    asyncio.run(single_run())
