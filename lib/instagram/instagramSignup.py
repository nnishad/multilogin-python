import asyncio
import aiohttp
import random

from lib.instagram.followAccounts import follow_accounts
from logger import Logger
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from httpClient import HttpClient

logger = Logger.get_instance()


async def signup(environment, browser, user, profile_id):
    browser.get('https://instagram.com')
    await asyncio.sleep(10)
    span = browser.find_element_by_xpath('//span[text()="Sign up"]')

    # Click on the span element
    span.click()
    # browser.get('https://instagram.com/accounts/emailsignup/')
    # Wait until the element is present
    wait = WebDriverWait(browser, 30)  # Maximum wait time of 10 seconds
    inputEmailOrPhone = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name=emailOrPhone]")))
    await asyncio.sleep(0.3)
    for char in user['number']:
        inputEmailOrPhone.send_keys(char)
        await asyncio.sleep(0.5)
    await asyncio.sleep(0.5)
    inputFullName = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name=fullName]")))
    for char in user['name']:
        inputFullName.send_keys(char)
        await asyncio.sleep(0.5)
    await asyncio.sleep(0.7)
    inputUsername = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name=username]")))
    for char in user['username']:
        inputUsername.send_keys(char)
        await asyncio.sleep(0.5)

    inputUsername.send_keys(Keys.TAB + Keys.SPACE)
    await asyncio.sleep(1)
    # browser.send_keys(Keys.SPACE)
    await asyncio.sleep(1.3)
    # submitButton = browser.find_element_by_xpath('//button[@type="button"]')
    # submitButton.click()
    await asyncio.sleep(1.3)
    generatedUsername = inputUsername.get_attribute("value")
    user['username'] = generatedUsername
    await asyncio.sleep(2)
    inputPassword = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name=password]")))
    for char in user['password']:
        inputPassword.send_keys(char)
        await asyncio.sleep(0.5)

    await asyncio.sleep(0.7)
    submitButton = browser.find_element_by_xpath('//button[@type="submit"]')
    submitButton.click()
    await asyncio.sleep(4)

    async def add_account_data_to_profile():
        await asyncio.sleep(4)
        url = "http://localhost:3001"
        account_details = {
            'username': user['username'],
            'password': user['password'],
            'phoneNumber': user['number']
        }
        logger.info(account_details)
        json_response = await HttpClient(url).post(f"/profile/{profile_id}/addAccount", account_details)
        logger.info(json_response)

    async def fetch_otp_details():
        api_status = 1
        while api_status not in [0, 2, 3, 4, 5, 6]:
            try:
                await asyncio.sleep(3)
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                            f"{environment['sms_pool_fetch_api']}?orderid={user['orderId']}&key={user['key']}") as response:
                        if response.status == 200:
                            json_data = await response.json()
                            message = str(json_data['sms'])
                            api_status = json_data['status']
                            time_left = json_data['time_left']
                            logger.info(json_data)
                            await asyncio.sleep(4)
                        else:
                            logger.info('An error occurred while checking API status:' + str(response.status))
                            break
            except Exception as e:
                logger.info('An error occurred while checking API status:' + str(e))
        logger.info('[Status of the API is]' + str(api_status))
        return api_status, message

    await asyncio.sleep(5)

    def get_random_integer(min_val, max_val):
        return str(random.randint(min_val, max_val))

    select_month = browser.find_element_by_css_selector('select[title="Month:"]')
    select = Select(select_month)
    select.select_by_value(get_random_integer(1, 12))

    select_day = browser.find_element_by_css_selector('select[title="Day:"]')
    select = Select(select_day)
    select.select_by_value(get_random_integer(1, 29))

    select_year = browser.find_element_by_css_selector('select[title="Year:"]')
    select = Select(select_year)
    select.select_by_value(get_random_integer(1965, 2000))

    await asyncio.sleep(5)

    next_buttons = browser.find_element_by_xpath('//button[text()="Next"]')
    next_buttons.click()

    await asyncio.sleep(10)

    status, otp_message = await fetch_otp_details()
    inputConfirmationCode = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[name=confirmationCode]")))
    await asyncio.sleep(5)
    if status != 1:
        for char in otp_message:
            inputConfirmationCode.send_keys(char)
            await asyncio.sleep(0.5)
        await asyncio.sleep(5)
        confirmation_signup_button = browser.find_element_by_xpath('//button[text()="Confirm"]')
        confirmation_signup_button.click()
        await add_account_data_to_profile()

    await asyncio.sleep(2)
    await follow_accounts(browser, get_random_integer(1, 29))

    await asyncio.sleep(5)

    browser.close()
