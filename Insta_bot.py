import os
import re
import wget
import time
import pickle
import random
from typing import Optional, TypeAlias

from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService

from webdriver_manager.chrome import ChromeDriverManager


load_dotenv()

NAME = os.getenv('NAME')
PSW = os.getenv('PSW')
INSTAGRAM = 'https://www.instagram.com/'

instagram_username: TypeAlias = str
instagram_psw: TypeAlias = str


class InstagramBot:
    # Insta bot by Fersus
    def __init__(self, username: instagram_username, password: instagram_psw):
        ''' Инициализация бота '''
        self.username = username
        self.password = password
        self.service = ChromeService(ChromeDriverManager().install())

    def create_webdriver(self, headless=False):
        ''' Создаёт веб-драйвер для использования браузера '''
        options = Options()
        if headless:
            options.add_argument("--headless=new")
        return webdriver.Chrome(service=self.service, options=options)

    def close_browser(self):
        ''' Закрывает браузер '''
        self.driver.close()
        self.driver.quit()

    def _collect_cookies(self) -> None:
        ''' Сохраняет cookies в файл '''
        pickle.dump(self.driver.get_cookies(),
                    open(f'{self.username}_cookies', 'wb'))

    def _load_cookies(self) -> None:
        ''' Загружает cookies '''
        for cookie in pickle.load(open(f'{self.username}_cookies', 'rb')):
            self.driver.add_cookie(cookie)

    def _add_headless_options(self):
        options = Options()
        options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=options)

    def login_and_collect_cookies(self) -> None:
        ''' Вход в аккаунт instagram, используя имя пользователя и пароль '''
        if self.headless:
            self._add_headless_options(self)
        try:
            self.driver.implicitly_wait(10)
            self.driver.get(INSTAGRAM)

            u_name_input = self.driver.find_element(By.NAME, "username")
            u_name_input.clear()
            u_name_input.send_keys(self.username)

            psw_input = self.driver.find_element(By.NAME, "password")
            psw_input.clear()
            psw_input.send_keys(self.password)

            psw_input.send_keys(Keys.ENTER)
            time.sleep(5)
            self._collect_cookies(self)
        except Exception as ex:
            print(ex)

    def login_use_cookies(self, headless: bool = False) -> None:
        ''' Вход в аккаунт instagram, используя cookies '''
        if self.headless:
            self._add_headless_options(self)
        try:
            self.driver.get(INSTAGRAM)

            self.driver.implicitly_wait(10)

            self._load_cookies(self)
            time.sleep(3)
            self.driver.refresh()

            buttons = self.driver.find_element(
                By.CSS_SELECTOR, "div[role='dialog']").find_elements(
                By.TAG_NAME, 'button')
            buttons[1].click()
        except Exception as ex:
            print(ex)

    def _collect_posts(self, save_to_file: bool = False) -> list:
        try:
            links = self.driver.find_elements(By.TAG_NAME, 'a')
            posts_urls = [item.get_attribute('href')
                          for item in links
                          if "/p/" in item.get_attribute('href')]
            if save_to_file:
                user = self.driver.current_url.split('/')[3]
                with open(f"{user}'s_posts", 'w') as file:
                    for url in posts_urls:
                        file.write(url)
            else:
                return posts_urls
        except Exception as ex:
            print(ex)

    def collect_posts_user(self, user: str,
                           scroll: int = 2,
                           save_to_file: bool = False) -> Optional[list]:
        ''' save user's posts in file or return list with its '''
        self.driver.implicitly_wait(10)
        try:
            self.driver.get(f'{INSTAGRAM}/{user}/')
            for i in range(1, scroll):
                self.driver.execute_script(
                    'window.scrollTo(0, document.body.scrollHeight);')
                time.sleep(random.randrange(3, 7))
            return self._collect_posts(save_to_file)
        except Exception as ex:
            print(ex)

    def press_like_on_posts(self, posts: list) -> None:
        ''' press like button on each post in posts '''
        self.driver.implicitly_wait(10)
        for post in posts[:3]:
            try:
                self.driver.get(post)
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.CLASS_NAME, "xp7jhwk")
                        )).click()
                time.sleep(random.randrange(3, 5))
            except Exception as ex:
                print(ex)
                self.close_browser()

    def _is_xpath_exist(self, xpath):
        ''' inspect is exist xpath on a page '''
        return bool(self.driver.find_elements(By.XPATH, xpath))

    def download_images(self, user: str, scroll: int = 2) -> None:
        ''' download images from instagram page '''
        self.driver.implicitly_wait(10)
        try:
            self.driver.get(f'{INSTAGRAM}/{user}/')
            for i in range(1, scroll):
                self.driver.execute_script(
                    'window.scrollTo(0, document.body.scrollHeight);')
                time.sleep(random.randrange(3, 7))

            links = self.driver.find_elements(By.TAG_NAME, 'img')
            images = [item.get_attribute('src') for item in links]

            path = os.getcwd()
            path = os.path.join(path, user)
            os.mkdir(path)
            counter = 0
            for image in images:
                save_as = (os.path.join(path, user + str(counter) + '.jpg'))
                wget.download(image, save_as)
                print('ok')
                counter += 1
        except Exception as ex:
            print(ex)

    def grab_followers(self,  user: str, numb_iter: int = 3) -> None:
        ''' Write links user's followers in file '''
        self.driver.implicitly_wait(10)
        self.driver.get(f'{INSTAGRAM}/{user}/')

        xpath = '//header/section[1]/ul[1]/li[2]/a[1]'
        if self._is_xpath_exist(xpath):
            self.driver.find_element(By.XPATH, xpath).click()
        else:
            print('xpath was changed')
            self.close_browser()

        pop_up_window = self.driver.find_element(By.CLASS_NAME, '_aano')
        for i in range(1, numb_iter):
            scr = 'arguments[0].scrollTop = \
                arguments[0].scrollTop + arguments[0].offsetHeight;'
            self.driver.execute_script(scr, pop_up_window)
            time.sleep(random.randrange(4, 7))

        links = self.driver.find_elements(By.TAG_NAME, 'a')

        hrefs = [link.get_attribute('href')
                 for link in links if '/p/' not in link.get_attribute('href')]

        clean_hrefs = set(
            re.findall(r'\w{5}\W{3}\w+.\w+.\w+\/\w+\/', '\n'.join(hrefs))
        )
        tech_links = ['https://www.instagram.com/direct/',
                      'https://about.instagram.com/blog/',
                      'https://about.meta.com/technologies/',
                      'https://about.meta.com/technologies/',
                      'https://www.instagram.com/web/',
                      'https://www.instagram.com/reels/',
                      'https://developers.facebook.com/docs/',
                      'https://www.instagram.com/about/'
                      ]
        with open(f"{user}'s followers.txt", 'w') as file:
            for href in clean_hrefs:
                if href not in tech_links:
                    file.write(href + '\n')

    def follow_and_like(self, filename: str) -> None:
        ''' follow by users from file and press like on their posts '''
        self.driver.implicitly_wait(10)
        with open(filename, 'r') as file:
            followers = file.read()
            links = followers.split('\n')
            try:
                for link in links:
                    self.driver.get(link)
                    xpath = "//div[contains(text(),'Follow')]"
                    if self._is_xpath_exist(xpath):
                        self.driver.find_element(
                            By.XPATH, xpath).click()
                        time.sleep(random.randrange(2, 4))
                        posts = self._collect_posts()
                        time.sleep(random.randrange(2, 4))
                        self.likes_on_post(posts)
                    else:
                        print('no xpass')

            except Exception as ex:
                print(ex)


# service = ChromeService(ChromeDriverManager().install())
# bot = InstagramBot(username=NAME, password=PSW)
# bot.login_and_collect_cookies()
# bot.follow_and_like("explor1r's followers.txt")
# bot.grab_followers(user='explor1r')
# posts = bot.collect_posts_user('explor1r')
# bot.likes_on_post(posts)
# bot.download_img('explor1r')
# bot.close_browser()
