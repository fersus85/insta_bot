import pytest
import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options

from webdriver_manager.chrome import ChromeDriverManager

from dotenv import load_dotenv
from pathlib import Path


env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

name = os.getenv('NAME')
psw = os.getenv('PSW')


@pytest.fixture
def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    return driver


@pytest.fixture
def get_credentials():
    return (name, psw)
