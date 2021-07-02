from selenium import webdriver
import time
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import dateparser
from datetime import datetime
import FacebookBot

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
