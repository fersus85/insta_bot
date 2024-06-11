import os
import re
import wget
import time
import pickle
import random
import logging
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


logger = logging.getLogger(name=__name__)
logger.setLevel(logging.DEBUG)

handler = logging.FileHandler(f'logs/{__name__}.log', mode='w')
formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

handler.setFormatter(formatter)
logger.addHandler(handler)

load_dotenv()

NAME = os.getenv('NAME')
PSW = os.getenv('PSW')
INSTAGRAM = 'https://www.instagram.com/'

instagram_username: TypeAlias = str
instagram_psw: TypeAlias = str


class InstagramBot:
    '''
    Бот для автоматизации действий в instagram.

    Атрибуты
    --------
    username : имя пользователя Instagram
    password : пароль пользователя Instagram

    Публичные методы
    ------
    login_and_collect_cookies(headless)
        входит в аккаунт инстаграмм и сохраняет куки в файл.

    save_user_posts_in_file(user,headless,scroll)
        Сохраняет список url адресов постов введенного пользователя в файл.

    user_posts_urls(user, headless, scroll)
        Возвращает список url адресов постов введенного пользователя.

    press_like_on_posts(driver, posts: list[str])
        Принимает список url адресов постов юзера и ставит лайк на каждый пост.

    download_images(user, scroll, headless)
        Cохраняет фотографии со страницы юзера локально.
    '''
    def __init__(self, username: instagram_username, password: instagram_psw):
        '''
        Инициализация бота

        :param username: str имя пользователя Instagram
        :param password: str пароль пользователя Instagram
        '''
        self.username = username
        self.password = password

    def login_and_collect_cookies(self, headless: bool = False) -> None:
        '''
        Вход в аккаунт instagram, используя имя пользователя и пароль

        :param headless: bool режим работы браузера
        '''
        try:
            driver = self._create_webdriver(headless)
            driver.get(INSTAGRAM)

            wait = WebDriverWait(driver, timeout=10)

            user_name_input = wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
                )
            psw_input = wait.until(
                EC.presence_of_element_located((By.NAME, "password"))
                )

            user_name_input.clear()
            user_name_input.send_keys(self.username)

            psw_input.clear()
            psw_input.send_keys(self.password)

            psw_input.send_keys(Keys.ENTER)

            time.sleep(10)

            self._collect_cookies(driver)
            logger.debug('func login_and_collect_cookies finished correctly')
            self._close_browser(driver)
        except Exception as ex:
            logger.error(ex, exc_info=True)

    def save_user_posts_in_file(self,
                                user: str,
                                headless: bool = False,
                                scroll: int = 2) -> None:
        '''
        Сохраняет список url адресов постов введенного пользователя в файл.

        :param user: str имя пользователя
        :param headless: bool режим работы браузера
        :param scroll: int количество прокручиваний страницы пользователя
        '''
        try:
            driver = self._reach_user_page(user, headless, scroll)
            self._collect_posts(driver, save_to_file=True)
            logger.debug('links saved in file')
            self._close_browser(driver)
        except Exception as ex:
            logger.error(ex, exc_info=True)

    def user_posts_urls(self,
                        user: str,
                        headless: bool = False,
                        scroll: int = 2) -> tuple[webdriver.Chrome, list[str]]:
        '''
        Возвращает список url адресов постов введенного пользователя.

        :param user: str имя пользователя
        :param headless: bool режим работы браузера
        :param scroll: int количество прокручиваний страницы пользователя
        :return: список url адресов постов введенного пользователя.
        '''
        try:
            driver = self._reach_user_page(user, headless, scroll)
            logger.debug('links returned')
            return driver, self._collect_posts(driver, save_to_file=False)
        except Exception as ex:
            logger.error(ex, exc_info=True)

    def press_like_on_posts(self,
                            driver: webdriver.Chrome,
                            posts: list[str]) -> None:
        '''
        Принимает список url адресов постов юзера и ставит лайк на каждый пост.

        :param driver: драйвер для управления браузером
        :param posts: список url адресов постов юзера
        '''
        for post in posts[:2]:
            try:
                like = "xp7jhwk"
                driver.get(post)
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, like))
                    ).click()
                driver.find_element(By.CLASS_NAME, like).click()
                time.sleep(random.randrange(3, 5))
            except Exception as ex:
                logger.error(ex, exc_info=True)
        self._close_browser(driver)
        logger.debug('success liked posts')

    def download_images(self,
                        user: str,
                        scroll: int = 2,
                        headless: bool = False) -> None:
        '''
        Cохраняет фотографии со страницы юзера локально.

        :param user: str имя пользователя для скачивания фото.
        :param scroll: int кол-во прокручиваний страницы.
        :param headless: bool режим управления браузером.
        '''
        try:
            driver = self._reach_user_page(user, headless, scroll)
            wait = WebDriverWait(driver, timeout=10)
            links = wait.until(
                EC.presence_of_all_elements_located((By.TAG_NAME, 'img')))
            images = [item.get_attribute('src') for item in links]
            logger.debug('img links collected')
            path = self._create_folder(user)
            self._save_imgs(images, path, user)
            logger.debug('all img saved')
        except Exception as ex:
            logger.error(ex, exc_info=True)

    @staticmethod
    def _create_webdriver(headless: bool = False) -> webdriver.Chrome:
        '''
        Создаёт веб-драйвер для использования браузера

        :param headless: bool режим работы браузера
        :return: веб-драйвер для использования браузера
        '''
        options = Options()
        if headless:
            options.add_argument("--headless=new")
        try:
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            logger.debug('webdriver created')
        except Exception as ex:
            logger.error(ex, exc_info=True)
        return driver

    @staticmethod
    def _close_browser(driver: webdriver.Chrome) -> None:
        '''
        Закрывает браузер

        :param driver: драйвер для управления браузером Chrome
        '''
        driver.close()
        driver.quit()

    def _collect_cookies(self, driver: webdriver.Chrome) -> None:
        '''
        Сохраняет cookies в файл

        :param driver: драйвер для управления браузером Chrome
        '''
        try:
            pickle.dump(driver.get_cookies(),
                        open(f'cookies/{self.username}_cookies', 'wb'))
            logger.info('cookies successful dumped')
        except Exception as ex:
            logger.error(ex, exc_info=True)

    def _load_cookies(self, driver: webdriver.Chrome) -> webdriver.Chrome:
        '''
        Загружает cookies в драйвер

        :param driver: драйвер для управления браузером Chrome
        :return: драйвер с загруженными куками
        '''
        try:
            for cookie in pickle.load(
                    open(f'cookies/{self.username}_cookies', 'rb')
                    ):
                driver.add_cookie(cookie)
            logger.debug('cookies loaded')
            return driver
        except Exception as ex:
            logger.error(ex, exc_info=True)

    def _login_use_cookies(self,
                           driver: webdriver.Chrome) -> None:
        '''
        Вход в аккаунт instagram, используя cookies

        :param driver: драйвер для управления браузером Chrome
        '''
        try:
            driver.get(INSTAGRAM)
            driver = self._load_cookies(driver)
            driver.refresh()

            buttons = driver.find_element(
                By.CSS_SELECTOR, "div[role='dialog']").find_elements(
                    By.TAG_NAME, 'button')

            buttons[1].click()
            logger.debug('success login')
            return driver
        except Exception as ex:
            logger.error(ex, exc_info=True)

    def _reach_user_page(self,
                         user: str,
                         headless: bool = False,
                         scroll: int = 2) -> webdriver.Chrome:
        '''
        Заходит на страницу юзера с постами и прокручивает ее scroll раз

        :param user: str имя пользователя
        :param headless: bool режим работы браузера
        :param scroll: int количество прокручиваний страницы пользователя
        '''
        try:
            driver = self._create_webdriver(headless)
            logger.debug('driver created')
            driver = self._login_use_cookies(driver)
            driver.get(f'{INSTAGRAM}/{user}/')
            logger.debug('reach user page')
            for _ in range(1, scroll):
                driver.execute_script(
                    'window.scrollTo(0, document.body.scrollHeight);')
                time.sleep(random.randrange(3, 7))
            return driver
        except Exception as ex:
            logger.error(ex, exc_info=True)

    def _collect_posts(self,
                       driver: webdriver.Chrome,
                       save_to_file: bool = False) -> Optional[list]:
        '''
        Собирает url адреса инстаграм постов юзера,
        в зависимости от выбранной опции либо возвращает
        список постов либо сохраняет его в файл.

        :param driver: драйвер для управления браузером
        :param save_to_file: режим работы save/return
        :return: список url адресов.
        '''
        try:
            links = driver.find_elements(By.TAG_NAME, 'a')
            posts_urls = [item.get_attribute('href')
                          for item in links
                          if "/p/" in item.get_attribute('href')]
            logger.debug('links collected')
            if save_to_file:
                user = driver.current_url.split('/')[4]
                with open(f"grabed_posts/{user}'s_posts", 'w') as file:
                    for url in posts_urls:
                        file.write(url + '\n')
            else:
                logger.debug('returned list of url')
                return posts_urls
        except Exception as ex:
            logger.error(ex, exc_info=True)

    def _is_xpath_exist(self, xpath):
        ''' inspect is exist xpath on a page '''
        return bool(self.driver.find_elements(By.XPATH, xpath))

    @staticmethod
    def _save_imgs(urls: list, path: str, user: str) -> None:
        counter = 1
        for url in urls:
            try:
                if 'data:image' not in url:
                    save_as = os.path.join(path, f'{user}_{str(counter)}.jpg')
                    wget.download(url, save_as)
                    logger.debug(f'img {counter} saved')
                    counter += 1
            except Exception as ex:
                logger.debug(ex, exc_info=True)

    @staticmethod
    def _create_folder(user: str):
        try:
            path = os.getcwd()
            path = os.path.join(path, user)
            os.mkdir(path)
            logger.debug('dir created')
            return path
        except FileExistsError as ex:
            logger.warning(ex)

    def grab_followers(self,  user: str, numb_iter: int = 3) -> None:
        ''' Write links user's followers in file '''
        self.driver.implicitly_wait(10)
        self.driver.get(f'{INSTAGRAM}/{user}/')

        xpath = '//header/section[1]/ul[1]/li[2]/a[1]'
        if self._is_xpath_exist(xpath):
            self.driver.find_element(By.XPATH, xpath).click()
        else:
            print('xpath was changed')
            self._close_browser()

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


bot = InstagramBot(username=NAME, password=PSW)
# bot.login_and_collect_cookies()
# bot.save_user_posts_in_file('explor1r', headless=True, scroll=3)
# driver, posts = bot.user_posts_urls('explor1r')
# bot.press_like_on_posts(driver, posts)
bot.download_images('explor1r')
# bot.follow_and_like("explor1r's followers.txt")
# bot.grab_followers(user='explor1r')
# posts = bot.collect_posts_user('explor1r')
# bot.likes_on_post(posts)
# bot.download_img('explor1r')
# bot._close_browser()
