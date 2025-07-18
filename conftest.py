import pytest
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

@pytest.fixture(scope="function")
def driver():
    options = webdriver.ChromeOptions()
    #options.add_argument('--headless')
    options.add_argument('--start-maximized')
    # Desactivar el Chrome profile picker
    options.add_argument('--disable-features=EnableChromeBrowserCloudManagement,ChromeWhatsNewUI,ChromeProfilePicker')
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    version = driver.capabilities['browserVersion']
    print(f"Versión de Chrome usada por Selenium: {version}")
    yield driver
    driver.quit()
