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
    __browser = None
    __post_handler = None
    __posts_scraper = None
    post_ID = None
    likes_limit = None

    __postContentUrl = 'https://mbasic.facebook.com/story.php?story_fbid={post_ID}&id=415518858611168'
    __postLikesUrl = 'https://mbasic.facebook.com/ufi/reaction/profile/browser/fetch/?limit={' \
                     'limit}&total_count=17&ft_ent_identifier={post_ID} '

    def __init__(self, username, password):
        self.__username = username
        self.__password = password
        self.__browser = webdriver.Chrome(r'E:\Progz\chromedriver_win32\chromedriver')
        self.likes_limit = 200
        self.__post_handler = PostHandler()
        self.__posts_scraper = PostsScraper()
        self.login()

    def login(self):
        url = 'https://facebook.com'

        self.__browser.get(url)

        username = self.__browser.find_element_by_id("email")
        password = self.__browser.find_element_by_id("pass")

        username.send_keys(self.__username)
        time.sleep(2)

        password.send_keys(self.__password)
        time.sleep(4)

        username.submit()
        time.sleep(10)

        self.__browser.get('https://mbasic.facebook.com/profile')
        # assert self.__browser.current_url == 'https://mbasic.facebook.com/profile', "Login Failed"

    def parse_html(self, request_url):
        self.__browser.get(request_url)
        page_content = self.__browser.page_source
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
        self.__browser = browser

    ###########################################
    ############### SCRAPING ##################
    ###########################################
    def navigate_next_page(self, soup_tmp):
        # curr_url = self.__browser.current_url
        # soup_tmp = BeautifulSoup(self.parse_html(curr_url), "html.parser")
        div_id = soup_tmp.find('div',
                               {'id': 'structured_composer_async_container'}).findChildren('div',
                                                                                           recursive=False)[0]['id']
        more = self.__browser.find_element_by_id(div_id).find_element_by_tag_name('a')
        more.click()

    def scrape_profile_posts_by_number(self, profile_url, posts=10):
        """
        Scrapes profile for number of given posts

        returns: list of posts ids
        """
        self.__browser.get(profile_url)
        posts_ids = []
        while len(posts_ids) < posts:
            soup_ = BeautifulSoup(self.parse_html(self.__browser.current_url), "html.parser")
            posts_ids.extend(self.__posts_scraper.extract_ids(soup_))
            time.sleep(0.5)
            self.navigate_next_page(soup_)
            # print(f"scraped {len(posts_ids)} posts")
            # clear_output(wait=True)
        return posts_ids
