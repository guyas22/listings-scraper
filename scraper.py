import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
import base64
import os

class Scraper:
    def __init__(self, logger):
        self.logger = logger

    def transform_url(self, original_url):
        # Extract the ID from the original URL
        id_part = original_url.split('/')[-1]
        
        # Determine the domain and construct the new URL accordingly
        if 'zoopla' in original_url:
            new_url = f"https://www.zoopla.co.uk/to-rent/details/{id_part}/"
        elif 'rightmove' in original_url:
            new_url = f"https://www.rightmove.co.uk/properties/{id_part}"
        elif 'onthemarket' in original_url:
            new_url = f"https://www.onthemarket.com/details/{id_part}"
        else:
            new_url = original_url 
        
        return new_url

    async def take_full_page_screenshot(self, original_url, output_file='full_screenshot.png', headless=True):
        browser = None
        try:
            transformed_url = self.transform_url(original_url)
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=headless)
                context = await browser.new_context(java_script_enabled=True)
                page = await context.new_page()

                await page.goto(transformed_url)
                current_url = page.url
                if "ID" not in current_url:
                    self.logger.warning(f"ID not found in URL: {current_url}, skipping...")
                    return None

                await page.screenshot(path=output_file, full_page=True)
                self.logger.info(f"Screenshot saved to {output_file}")
                return self.encode_image(output_file)

        except Exception as e:
            self.logger.error(f"An error occurred during screenshot capture: {e}")
        
        finally:
            if browser:
                await browser.close()


    def encode_image(self, image_path):
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except FileNotFoundError:
            self.logger.error(f"File not found: {image_path}")
            return None
        except Exception as e:
            self.logger.error(f"An error occurred while encoding the image: {e}")
            return None
