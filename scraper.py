import base64
import os
import logging
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class Scraper:
    def __init__(self, logger, adblocker_path=None):
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
        options = Options()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-gpu")


        service = Service()  # Using the installed geckodriver for Firefox
        browser = None

        try:
            id_part = original_url.split('/')[-1]
            transformed_url = self.transform_url(original_url)
            browser = webdriver.Firefox(service=service, options=options)  # Using Firefox instead of Chrome

            # Navigate to the transformed URL
            browser.get(transformed_url)

            # Wait until the page is fully loaded (DOM readyState is 'complete')
            WebDriverWait(browser, 10).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )

            current_url = browser.current_url

            # Skipping logic: check if "ID" is not in the URL
            if id_part not in current_url:
                self.logger.warning(f"ID not found in URL: {current_url}, skipping...")
                return None

            # Take a full-page screenshot using Firefox's full-page screenshot capability
            image_bytes = browser.get_full_page_screenshot_as_png()
            with open(output_file, "wb") as file:
                file.write(image_bytes)

            self.logger.info(f"Screenshot saved to {output_file}")
            return self.encode_image(output_file)

        except Exception as e:
            self.logger.error(f"An error occurred during screenshot capture: {e}")
            return None

        finally:
            if browser:
                browser.quit()

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
