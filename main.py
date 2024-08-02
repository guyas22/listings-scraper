import asyncio
import os
import pandas as pd
from scraper import take_full_page_screenshot

async def main():
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

if __name__ == "__main__":
    asyncio.run(main())
