import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def test_login(get_driver, get_credentials):
    name, psw = get_credentials
    DASHBOARD_URL = 'https://www.instagram.com/'
    URL_AFTER_AUTH = "https://www.instagram.com/accounts/onetap/?next=%2F"
    try:
        get_driver.implicitly_wait(10)
        get_driver.get('https://www.instagram.com/')

        assert get_driver.current_url == DASHBOARD_URL

        u_name_input = get_driver.find_element(By.NAME, "username")
        u_name_input.clear()
        u_name_input.send_keys(name)
       
        psw_input = get_driver.find_element(By.NAME, "password")
        psw_input.clear()
        psw_input.send_keys(psw)

        psw_input.send_keys(Keys.ENTER)

        time.sleep(10)

        assert get_driver.current_url == URL_AFTER_AUTH

        get_driver.close()
        get_driver.quit()

    except Exception as ex:
        get_driver.close()
        get_driver.quit()
