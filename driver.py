import os
from selenium import webdriver

def find_driver(heroku):
    dirname = os.path.dirname(os.path.abspath(__file__))
    options = webdriver.ChromeOptions()
    if heroku == 0:
        executable_path = os.path.join(dirname, "chromedriver.exe")
        print(executable_path)
    else:
        options.binary_location = '/app/.apt/usr/bin/google_chrome'
        options.add_argument("--headless")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        executable_path = '/app/.chromedriver/bin/chromedriver'
    return webdriver.Chrome(executable_path = executable_path, options = options)