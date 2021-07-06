from selenium import webdriver
import time
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import dateparser
from datetime import datetime
from helpers import PostHandler
from helpers import PostsScraper


class FacebookBot:
    __username = None
    __password = None
    browser = None
    __post_handler = None
    posts_scraper = None
    post_ID = None
    likes_limit = None

    __postContentUrl = 'https://mbasic.facebook.com/story.php?story_fbid={post_ID}&id=415518858611168'
    __postLikesUrl = 'https://mbasic.facebook.com/ufi/reaction/profile/browser/fetch/?limit={' \
                     'limit}&total_count=17&ft_ent_identifier={post_ID} '

    # Cache
    last_scraped_ids = None

    def __init__(self, username, password):
        self.__username = username
        self.__password = password
        self.browser = webdriver.Chrome(r'E:\Progz\chromedriver_win32\chromedriver')
        self.likes_limit = 200
        self.__post_handler = PostHandler()
        self.posts_scraper = PostsScraper(self.browser)
        self.login()

    def login(self):
        url = 'https://facebook.com'

        self.browser.get(url)

        username = self.browser.find_element_by_id("email")
        password = self.browser.find_element_by_id("pass")

        username.send_keys(self.__username)
        time.sleep(2)

        password.send_keys(self.__password)
        time.sleep(4)

        username.submit()
        time.sleep(10)

        self.browser.get('https://mbasic.facebook.com/profile')
        # assert self.__browser.current_url == 'https://mbasic.facebook.com/profile', "Login Failed"

    def parse_html(self, request_url):

        self.browser.get(request_url)
        page_content = self.browser.page_source
        return page_content

    def __get_soup(self, url_form, _post_id=-1, likes_limit=200):
        """
        Get soup from url with certain form
        used for targeted pages(post with id or likes page)
        """
        final_url = url_form.replace('{limit}', str(likes_limit))

        # if no post id provided extract from id assigned in object
        if _post_id == -1:
            final_url = final_url.replace('{post_ID}', str(self.post_ID))
        else:
            final_url = final_url.replace('{post_ID}', str(_post_id))
        soup = BeautifulSoup(self.parse_html(final_url), "html.parser")
        return soup

    def get_post_content(self, _post_id=-1):
        self.__post_handler.soup = self.__get_soup(self.__postContentUrl, _post_id)
        return self.__post_handler.post_content()

    def get_post_date(self, _post_id=-1):
        self.__post_handler.soup = self.__get_soup(self.__postContentUrl, _post_id)
        return self.__post_handler.date_posted()

    def get_post_reacts(self, _post_id=-1, likes_limit=200, react_type=True):
        self.__post_handler.soup = self.__get_soup(self.__postLikesUrl, _post_id, likes_limit)
        return self.__post_handler.post_likes(react_type)

    def set_browser(self, browser):
        self.browser = browser
        self.posts_scraper.set_browser(browser)

    ###########################################
    ############### SCRAPING ##################
    ###########################################
    def scrape_post_ids_by_number(self, profile_url):
        self.__last_scraped_ids = (profile_url, self.posts_scraper.scrape_profile_posts_by_number(profile_url, 10))
        return self.__last_scraped_ids

    def scrape_post_ids_by_date_range(self, start_date, end_date):
        pass

    def scrape_post_ids_to_date(self, start_url, target_date):
        """takes start page and scrapes to date"""
        self.__last_scraped_ids = self.posts_scraper.scrape_profile_to_date(start_url, target_date)
        return self.__last_scraped_ids
