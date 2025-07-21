from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pytest

@pytest.fixture
def driver():
    options = Options()
    options.add_argument('--user-data-dir=D:\\Selenium_profiles')
    options.add_argument('--profile-directory=Profile 18')
    options.add_argument('--remote-debugging-port=9222')
    options.add_argument('--start-maximized')
    options.add_experimental_option("detach", True)
    options.add_argument("--log-level=3")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    driver.get("https://8-0-0-dot-teammates-grasshoppers-testing.uw.r.appspot.com/web/front/home")
    yield driver
    driver.quit()
