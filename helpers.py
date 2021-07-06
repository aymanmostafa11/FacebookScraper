from selenium import webdriver
import time
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import dateparser
from datetime import datetime


class Post():
    id = None
    date_posted = None
    content = None
    image = None
    image_description = None
    likes = None
    comments = None
    shares = None

class PostHandler:
    soup = None
    def post_content(self, with_soup = False):
        content = self.soup.find_all('p')
        #photo_desc = self.soup.find_all('')
        post_content = []
        for lines in content:
            post_content.append(lines.text)

        post_content = ' '.join(post_content)
        if with_soup:
            return post_content, self.soup
        else:
            return post_content

    def date_posted(self):
        date_posted = self.soup.find('abbr')
        return date_posted.text

    def post_likes(self, type_r=True):

        names = self.soup.find_all('h3')

        people_who_liked = []
        for name in names:
            if name.text != '' and name.text[0].isdigit():
                continue
            people_who_liked.append(name.text)
        people_who_liked = [i for i in people_who_liked if i]
        if type_r:
            reacts = self.soup.find_all('img', {'class': 'bh r'})
            people_who_liked = [(i, react['alt']) for i, react in zip(people_who_liked, reacts)]
        return people_who_liked


class PostsScraper:
    __browser = None
    # Cache
    Clast_date_navigation_url = None
    Clast_date_range_scrape = None

    def __init__(self, browser):
        self.__browser = browser

    def parse_html(self, request_url):

        self.__browser.get(request_url)
        page_content = self.__browser.page_source
        return page_content

    def find_post_id(self, element):
        """
        @param element: a soup tag element of type 'article'
        @return post id
        """
        res = ''
        tags = element['data-ft'].split(',')
        for tag in tags:
            if 'top_level' in tag:
                res = tag
                break
        assert res != '', 'Post id not found'
        return res.split(':')[1][1:-1]

    def extract_ids(self, soup_):
        """
        extracts posts ids from page soup
        @return list of ids
        """
        posts = soup_.find_all('article')
        ids = []
        for post in posts:
            try:
                ids.append(self.find_post_id(post))
            except:
                continue
        print(f'Found {len(ids)} posts')
        return ids

    ################################
    ########### Navigation ##########
    #################################
    def __navigate_next_page(self, soup_tmp):
        # curr_url = self.__browser.current_url
        # soup_tmp = BeautifulSoup(self.parse_html(curr_url), "html.parser")
        div_id = soup_tmp.find('div',
                               {'id': 'structured_composer_async_container'}).findChildren('div',
                                                                                           recursive=False)[0]['id']
        more = self.__browser.find_element_by_id(div_id).find_element_by_tag_name('a')
        more.click()

    def navigate_profile_to_date(self, profile_url, target_date):
        """Get link of the page containing the first encounterd target date"""
        self.__browser.get(profile_url)
        soup_ = BeautifulSoup(self.parse_html(self.__browser.current_url), "html.parser")
        i = 0
        while not self.found_date_range(soup_, target_date):
            time.sleep(0.5)
            self.__navigate_next_page()
            # print(browser.current_url)
            soup_ = BeautifulSoup(self.parse_html(self.__browser.current_url), "html.parser")
            print(i)
            i += 1
            self.last_date_navigation_url = self.__browser.current_url
        return self.__browser.current_url



    ######################################
        ########## SCRAPING ########
    #####################################
    def scrape_profile_posts_by_number(self, profile_url, posts=10):
        """
        Scrapes profile for number of given posts

        returns: list of posts ids
        """
        self.__browser.get(profile_url)
        posts_ids = []
        while len(posts_ids) < posts:
            soup_ = BeautifulSoup(self.parse_html(self.__browser.current_url), "html.parser")
            posts_ids.extend(self.extract_ids(soup_))
            time.sleep(0.5)
            self.__navigate_next_page(soup_)
            # print(f"scraped {len(posts_ids)} posts")
            # clear_output(wait=True)
        return posts_ids

    ############ Date based ############
    def scrape_posts_by_date_range(self, begin_date, end_date, profile_url):
        """
        Extract posts between two fixed dates
        """
        cache = {}
        cache['profile_url'] = profile_url
        cache['start_url'] = self.navigate_profile_to_date(profile_url, begin_date)
        cache['ids'] = self.scrape_profile_to_date(cache['start_url'], end_date)
        cache['end_url'] = self.__browser.current_url
        self.Clast_date_range_scrape = cache
        return cache

    def scrape_profile_to_date(self, start_page, target_date):
        """
        Scrapes profile for posts ids using date range
        """
        self.__browser.get(start_page)
        soup_ = BeautifulSoup(self.parse_html(self.__browser.current_url), "html.parser")
        ids = []
        while not self.found_date_range(soup_, target_date):
            ids.extend(self.extract_ids(soup_))
            time.sleep(0.5)
            self.__navigate_next_page(soup_)
            soup_ = BeautifulSoup(self.parse_html(self.__browser.current_url), "html.parser")
            print(len(ids))
            # clear_output(wait=True)
        return ids

    def found_date_range(self, soup_, target):
        """
        Returns true of the date found in soup in range
        """
        # finds first and last post date in page
        date_1 = soup_.find_all('abbr')[0].text
        date_2 = soup_.find_all('abbr')[-1].text

        p_date1 = dateparser.parse(date_1)
        p_date2 = dateparser.parse(date_2)
        #     print(p_date1, p_date2)
        #     print('\n')
        if p_date1 < target or p_date2 < target:
            return True
        else:
            return False

    def set_browser(self, browser):
        self.__browser = browser


