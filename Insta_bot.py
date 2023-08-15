import random
import os
import wget
import time
import pickle

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException


class InstagramBot:
    # Insta bot by Fersus
    def __init__(self, username, password, chrome_driver_path):
        self.username = username
        self.password = password
        self.options = webdriver.ChromeOptions()
        self.service = Service(executable_path=chrome_driver_path)
        self.options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246")
        self.options.add_argument(
            '--disable-blink-features=AutomationControlled')
        self.driver = webdriver.Chrome(
            service=self.service, options=self.options)

    def close_browser(self):
        self.driver.close()
        self.driver.quit()

    def login(self):
        # authorization
        self.driver.get('https://www.instagram.com/')
        time.sleep(3)
        login_input = self.driver.find_element(By.NAME, 'username')
        login_input.clear()
        login_input.send_keys(self.username)
        time.sleep(5)
        psw_input = self.driver.find_element(By.NAME, 'password')
        psw_input.clear()
        psw_input.send_keys(self.password)
        time.sleep(5)
        # press_ent
        psw_input.send_keys(Keys.ENTER)
        time.sleep(5)
        # cookies
        # collect cookies
        # pickle.dump(self.driver.get_cookies(), open(f'{self.username}_cookies', 'wb'))

    def login_with_cookie(self):
        self.driver.get('https://www.instagram.com/')
        time.sleep(3)
        # load cookies
        for cookie in pickle.load(open('../Gui/app_dzen_cookies', 'rb')):
            self.driver.add_cookie(cookie)
        time.sleep(3)
        self.driver.refresh()
        self.driver.implicitly_wait(5)
        buttons = self.driver.find_element(
            By.CSS_SELECTOR, "div[role='dialog']").find_elements(By.TAG_NAME, 'button')
        buttons[1].click()
        time.sleep(5)

    def liking_posts_user(self, user, scroll=2):
        # search user_page
        self.driver.find_element(
            By.CSS_SELECTOR, 'svg[aria-label="Поисковый запрос"]').click()
        input_requests = self.driver.find_element(
            By.CSS_SELECTOR, "input[aria-label='Ввод поискового запроса'")
        input_requests.clear()
        input_requests.send_keys(user)
        time.sleep(5)
        input_requests.send_keys(Keys.ENTER)
        time.sleep(7)
        input_requests.send_keys(Keys.ENTER)
        time.sleep(7)
        # Scroll down
        for i in range(1, scroll):
            self.driver.execute_script(
                'window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(random.randrange(7, 10))
        # Collect all reference from page
        links = self.driver.find_elements(By.TAG_NAME, 'a')
        posts = []
        # Filter post's url
        for item in links[0:2]:
            links = item.get_attribute('href')
            if '/p/' in links:
                posts.append(links)
        # print(posts)
        print(len(posts))
        self.driver.implicitly_wait(5)
        # Iteration through posts
        for post in posts[0:5]:
            try:
                self.driver.get(post)
                # Press like button
                WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
                    (By.XPATH, '/html/body/div[1]/div/div/div/div[1]/div/div/div/div[1]/div[1]/div[2]/section/main/div[1]/div[1]/article/div/div[2]/div/div[2]/section[1]/span[1]/button'))).click()
                time.sleep(10)
            except Exception as ex:
                print(ex)
                self.close_browser()

    def is_xpath_exist(self, xpath):
        # inspect is exist xpath on a page
        driver = self.driver
        try:
            driver.find_element(By.XPATH, xpath)
            exist = True
        except NoSuchElementException:
            exist = False
        return exist

    def download_img(self, userpage, scroll=2):
        driver = self.driver
        driver.find_element(
            By.CSS_SELECTOR, 'svg[aria-label="Поисковый запрос"]').click()
        input_requests = driver.find_element(
            By.CSS_SELECTOR, "input[aria-label='Ввод поискового запроса'")
        input_requests.clear()
        input_requests.send_keys(userpage)
        time.sleep(5)
        input_requests.send_keys(Keys.ENTER)
        time.sleep(7)
        input_requests.send_keys(Keys.ENTER)
        time.sleep(5)
        # Scroll down if you need
        for i in range(1, scroll):
            driver.execute_script(
                'window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(random.randrange(7, 10))
        # Collect all reference from page
        links = driver.find_elements(By.TAG_NAME, 'img')
        images = []
        # Filter post's url
        for item in links:
            links = item.get_attribute('src')
            images.append(links)
        # print(images)
        print(len(images))
        driver.implicitly_wait(5)
        path = os.getcwd()
        path = os.path.join(path, userpage)
        os.mkdir(path)
        counter = 0
        for image in images:
            save_as = (os.path.join(path, userpage + str(counter) + '.jpg'))
            wget.download(image, save_as)
            counter += 1

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
                                             '/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/div[1]/div[2]/section/main/div/header/section/ul/li[2]/a/div/span').get_attribute('title')
        driver.find_element(
            By.XPATH, '/html/body/div[2]/div/div/div/div[1]/div/div/div/div[1]/div[1]/div[2]/section/main/div/header/section/ul/li[2]/a').click()

        print(numb_followers)
        pop_up_window = driver.find_element(By.XPATH,
                                            '/html/body/div[2]/div/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[2]')
        count = numb_iter

        for i in range(1, numb_iter):
            driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;',
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
