import datetime
import json
import re

import bs4
import feedparser
import scrapy
from news_bots.items import NewsBotsItem


class EttodaySpider(scrapy.Spider):
    name = 'Ettoday'
    allowed_domains = ['feeds.feedburner.com', 'finance.ettoday.net']
    start_urls = ['http://feeds.feedburner.com/ettoday/finance?format=xml']

    def parse(self, response):
        d = feedparser.parse(response.text)
        parsed_time = datetime.datetime.strptime(d.entries[0].published, '%a,%d %b %Y %H:%M:%S +0800').strftime(
            '%Y-%m-%d %H:%M:%S')

        latest_news = {
            'url': d.entries[0].link,
            'title': d.entries[0].title,
            'published_at': parsed_time
        }
        match = re.search(r'(\d+).htm', latest_news.get('url'))
        transferred_url = 'https://finance.ettoday.net/amp/amp_news.php7?news_id=' + match.group(1)

        yield response.follow(transferred_url, callback=self.parse_article)

    def parse_article(self, response):
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        header_wrapper = soup.find('header', 'article-desc')
        article_title = header_wrapper.h1
        published_at_str = header_wrapper.time['datetime']
        published_at = datetime.datetime.strptime(published_at_str, '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d %H:%M:00')
        article_div = soup.find('div', 'content-container')
        vals = [i.text.strip(' \r\t\n').replace('\n', '') for i in article_div.find_all('p')]
        vals = filter(None, vals)
        content = ','.join(vals)

        article = NewsBotsItem()
        article['url'] = response.url
        article['title'] = article_title.text
        article['published_at'] = published_at
        article['content'] = content

        yield article
