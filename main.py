from selenium import webdriver
import time
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import dateparser
from datetime import datetime
from facebookBot import FacebookBot

mail = 'ayman.mano32@hotmail.com'
passw = '24098722coldfusion'


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    bot = FacebookBot(mail, passw)
    bot.scrape_post_ids_to_date("https://mbasic.facebook.com/ayman.moustafa.33?_rdr#_",
                                datetime(2021, 7, 3))

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
