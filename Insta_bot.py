import random
import os
import wget
import time
import pickle
from pathlib import Path
from typing import Optional, TypeAlias

from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

from webdriver_manager.chrome import ChromeDriverManager


env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

name = os.getenv('NAME')
psw = os.getenv('PSW')

instagram_username: TypeAlias = str
instagram_psw: TypeAlias = str


class InstagramBot:
    # Insta bot by Fersus
    def __init__(self, username: instagram_username,
                  password: instagram_psw):
        self.username = username
        self.password = password
        self.service = ChromeService(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service)

        
    def close_browser(self):
        ''' close webdriver '''
        self.driver.close()
        self.driver.quit()


    def login_collect_cookie(self) -> None:
        ''' Login in instagram account with usrname and psw, collect cookie '''
        try:
            self.driver.implicitly_wait(10)
            self.driver.get('https://www.instagram.com/')

            u_name_input = self.driver.find_element(By.NAME, "username")
            u_name_input.clear()
            u_name_input.send_keys(self.username)

            psw_input = self.driver.find_element(By.NAME, "password")
            psw_input.clear()
            psw_input.send_keys(self.password)

            psw_input.send_keys(Keys.ENTER)
            
            time.sleep(5)
            pickle.dump(self.driver.get_cookies(),
                         open(f'{self.username}_cookies', 'wb'))

        except Exception as ex:
            print(ex)


    def login_with_cookie(self, headless: bool=False) -> None:
        ''' Login in instagram account if you have cookie '''
        if headless:
            options = Options()
            options.add_argument("--headless=new")
            self.driver = webdriver.Chrome(
                service=ChromeService(ChromeDriverManager().install()), options=options)
        try:
            self.driver.get('https://www.instagram.com/')

            self.driver.implicitly_wait(10)
            
            for cookie in pickle.load(open('deriabin_evg_cookies', 'rb')):
                self.driver.add_cookie(cookie)
            time.sleep(3)
            self.driver.refresh()

            buttons = self.driver.find_element(
                By.CSS_SELECTOR,"div[role='dialog']").find_elements(
                By.TAG_NAME, 'button')
            buttons[1].click()
        except Exception as ex:
            print(ex)


    def collect_posts_user(self, user: str, scroll: int=4,
                            save_to_file: bool = False) -> Optional[list]:
        ''' save user's posts in file or return list with its '''
        self.driver.implicitly_wait(10)
        try:
            self.driver.get(f'https://www.instagram.com/{user}/')
            for i in range(1, scroll):
                self.driver.execute_script(
                    'window.scrollTo(0, document.body.scrollHeight);')
                time.sleep(random.randrange(3, 7))
            links = self.driver.find_elements(By.TAG_NAME, 'a')
            posts_urls = [item.get_attribute('href') for item in links if "/p/" in item.get_attribute('href')]
            if save_to_file:
                with open(f"{user}'s_posts", 'w') as file:
                    for url in posts_urls:
                        file.write(url)
            else:
                return posts_urls
        except Exception as ex:
            print(ex)

    def likes_on_post(self, posts: list) -> None:
        ''' press like button on posts '''
        self.driver.implicitly_wait(10)
        for post in posts[0:3]:
            try:
                self.driver.get(post)
                WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
                    (By.CLASS_NAME, "xp7jhwk"))).click()
                time.sleep(random.randrange(3, 5))
            except Exception as ex:
                print(ex)
                self.close_browser()

    def _is_xpath_exist(self, xpath):
        ''' inspect is exist xpath on a page '''
        return bool(self.driver.find_elements(By.XPATH, xpath))


    def download_img(self, user: str, scroll: int=2) -> None:
        ''' download images from instagram page '''
        self.driver.implicitly_wait(10)
        try:
            self.driver.get(f'https://www.instagram.com/{user}/')
            for i in range(1, scroll):
                self.driver.execute_script(
                    'window.scrollTo(0, document.body.scrollHeight);')
                time.sleep(random.randrange(3, 7))

            links = self.driver.find_elements(By.TAG_NAME, 'img')
            for el in links:
                print(el.get_attribute('value'))
                print(el.__dict__())
                # print(el.accessible_name, el.aria_role)
            images = [item.get_attribute('src') for item in links]
            # print(images[0])
    
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
        

    def grab_followers(self, userpage, numb_iter):
        driver = self.driver
        driver.find_element(
            By.CSS_SELECTOR, 'svg[aria-label="Поисковый запрос"]').click()
        input_requests = driver.find_element(
            By.CSS_SELECTOR, "input[aria-label='Ввод поискового запроса'")
        input_requests.clear()
        input_requests.send_keys(userpage)
        time.sleep(5)
        input_requests.send_keys(Keys.ENTER)
        time.sleep(3)
        input_requests.send_keys(Keys.ENTER)
        time.sleep(3)
        print('watch followers...')
        numb_followers = driver.find_element(By.XPATH,
                                             '').get_attribute('title')
        driver.find_element(
            By.XPATH, '').click()

        print(numb_followers)
        pop_up_window = driver.find_element(By.XPATH,
                                            '')
        count = numb_iter

        for i in range(1, numb_iter):
            driver.execute_script(
                'arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;',
                                  pop_up_window)
            time.sleep(random.randrange(7, 9))
            count -= 1
            print(f'left {count} times')
        time.sleep(5)
        links = driver.find_elements(By.TAG_NAME, 'a')
        hrefs = []
        for link in links:
            href = link.get_attribute('href')
            if '/p/' not in href:
                hrefs.append(href)
                # print(href)
        hrefs = set(hrefs)
        hrefs = list(hrefs)
        with open(f'links of followers/links of {userpage} followers.txt', 'w') as file:
            for href in hrefs[28:]:
                file.write(href + '/n')

    def follow_and_like(self, filename, num_users=70):
        driver = self.driver
        # open file with links
        print('load links...')
        with open(filename, 'r') as file:
            followers = file.read()
            links = followers.split('/n')
            # iterate through links
            count = num_users
            try:
                for link in links:
                    count -= 1
                    print(f'Left {count} links')
                    if link != 'https://www.instagram.com':
                        driver.get(link)
                        time.sleep(random.randrange(3, 5))
                        sub_but = "/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/section/main/div/header/section/div[1]/div[1]/div/div[1]/button"
                        if self.is_xpath_exist(sub_but):
                            driver.find_element(By.XPATH, sub_but).click()
                            time.sleep(random.randrange(3, 5))
                            if self.is_xpath_exist('/html/body/div[1]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]/button[2]'):
                                driver.find_element(
                                    By.XPATH, '/html/body/div[1]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]/button[2]').click()
                        try:
                            links = driver.find_elements(By.TAG_NAME, 'a')
                            posts = []
                            # Filter post's url
                            for item in links:
                                links = item.get_attribute('href')
                                if '/p/' in links:
                                    posts.append(links)
                            print(len(posts))
                            numbers_likes = random.randrange(2, 5)
                            for post in posts[0:numbers_likes]:
                                driver.get(post)
                                # Press like button
                                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,
                                                                                            '/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/section/main/div[1]/div[1]/article/div/div[2]/div/div[2]/section[1]/span[1]/button'))).click()
                                time.sleep(random.randrange(3, 5))
                        except Exception as ex:
                            print(ex)
            except Exception as ex:
                print(ex)


bot = InstagramBot(username=name, password=psw)
bot.login_with_cookie()
# posts = bot.collect_posts_user('explor1r')
# bot.likes_on_post(posts)
bot.download_img('explor1r')
bot.close_browser()
