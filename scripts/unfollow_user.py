import random
import time
from selenium import webdriver
from config import TWITTER_PASSWORD
from settings import constants

buttons = set()
unfollow_count = 0
height = constants.SCROLL_HEIGHT_LIMIT

driver = webdriver.Firefox()
driver.get(constants.TWITTER_LOGIN_URL)

username_field = driver.find_element_by_name("session[username_or_email]")
password_field = driver.find_element_by_name("session[password]")

username_field.send_keys(constants.USER_NAME)
driver.implicitly_wait(constants.LOGIN_SCREEN_WAIT_TIME)

password_field.send_keys(TWITTER_PASSWORD)
driver.implicitly_wait(constants.LOGIN_SCREEN_WAIT_TIME)

# login button
driver.find_element_by_xpath(constants.LOGIN_BUTTON_XPATH).click()

driver.get(constants.TWITTER_FOLLOWING_URL)

while True:
    driver.execute_script("window.scrollTo(0," + str(height) + ")")
    height += constants.SCROLL_HEIGHT_LIMIT
    time.sleep(constants.SCROLL_PAUSE_TIME)
    new_buttons = driver.find_elements_by_xpath("//*[contains(text(), 'Following')]");
    new_ones = list(set(new_buttons).difference(buttons))
    print('Diff', len(new_ones))
    buttons.update(new_buttons)
    print('Total length', len(buttons))
    if len(buttons) >= constants.UNFOLLOW_NOT_APPLY_LIMIT:
        for button in new_ones:
            try:
                button.click()
                time.sleep(random.randrange(*constants.UNFOLLOW_SLEEP_TIME_RANGE))
                driver.find_element_by_xpath(constants.UNFOLLOW_APPLY_BUTTON_XPATH).click()
                time.sleep(random.randrange(*constants.UNFOLLOW_APPLY_SLEEP_TIME_RANGE))
                unfollow_count += 1
                print('Unfollow count', unfollow_count)
            except Exception as e:
                print('Unfollow error', str(e))
                pass

print('{} user is unfollowed.'.format(unfollow_count))

driver.close()
