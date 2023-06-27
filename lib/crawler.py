import random
import asyncio
from selenium.webdriver.common.keys import Keys

from logger import Logger

logger = Logger.get_instance()

# Set the range of random durations for staying on each page (in seconds)
page_duration_min = 2
page_duration_max = 5

# Set the range of random scroll counts for each page
scroll_count_min = 3
scroll_count_max = 7

# Set the range of random durations for waiting after each scroll (in seconds)
scroll_wait_duration_min = 0.5
scroll_wait_duration_max = 1.5

websites = [
    {
        'url': 'https://news.google.com',
        'button_xpath': '//span[text()="Accept all"]'
    },
    {
        'url': 'https://news.yahoo.com',
        'button_xpath': '//button[text()="Accept all"]'
    }
]


def filter_links(links):
    filtered_links = []
    for link in links:
        if link is not None and websites[0].get("url") + "/articles" in link or link is not None and websites[1].get(
                "url") in link:
            filtered_links.append(link)
    return set(filtered_links)


async def start_crawler(browser):
    all_links = []
    for website in websites:
        await asyncio.sleep(2)
        browser.get("https://google.com/search?q="+website.get('url'))
        try:
            browser.find_element_by_xpath('//div[text()="Accept all"]').click()
        except Exception as e:
            logger.error(e)
        await asyncio.sleep(3)
        browser.get(website.get('url'))
        try:
            browser.find_element_by_xpath(website.get("button_xpath")).click()
        except Exception as e:
            logger.error(e)
        await asyncio.sleep(3)
        a_tags = browser.find_elements_by_xpath("//a")
        for a in a_tags:
            all_links.append(a.get_attribute("href"))
    links_to_crawl = filter_links(all_links)
    logger.info(f"total links to crawl:{len(links_to_crawl)}")
    # Iterate over the collection of links
    for link in links_to_crawl:
        # Open the link
        browser.get(link)
        logger.info(f"crawling: {link}")
        # Generate a random duration for staying on the page
        page_duration = random.uniform(page_duration_min, page_duration_max)
        logger.info(f"wait page_duration: {page_duration}")
        # Wait for the specified page duration
        await asyncio.sleep(page_duration)

        # Generate a random scroll count for the page
        scroll_count = random.randint(scroll_count_min, scroll_count_max)
        logger.info(f"scroll_count: {scroll_count}")

        # Perform scrolling actions
        for _ in range(scroll_count):
            # Scroll randomly up or down
            if random.choice([True, False]):
                browser.find_element_by_tag_name('body').send_keys(Keys.PAGE_UP)
            else:
                browser.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)

            # Generate a random wait duration after each scroll
            scroll_wait_duration = random.uniform(scroll_wait_duration_min, scroll_wait_duration_max)
            logger.info(f"scroll_wait_duration: {scroll_wait_duration}")

            # Wait a short interval between scrolls
            await asyncio.sleep(scroll_wait_duration)
        # Generate a random duration for staying on the page
        page_duration = random.uniform(page_duration_min, page_duration_max)
        logger.info(f"wait page_duration: {page_duration}")

        # Wait for the specified page duration
        await asyncio.sleep(page_duration)
    browser.quit()
