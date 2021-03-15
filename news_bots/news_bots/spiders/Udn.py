import datetime
from time import mktime

import bs4
import feedparser
import scrapy

from news_bots.items import NewsBotsItem


class UdnSpider(scrapy.Spider):
    name = 'Udn'
    allowed_domains = ['money.udn.com']
    start_urls = ['https://money.udn.com/rssfeed/news/1001/5591/5612?ch=money']

    def parse(self, response):
        d = feedparser.parse(response.text)
        parsed_datetime_ojb = datetime.datetime.fromtimestamp(mktime(d.feed.published_parsed))
        parsed_datetime_ojb += datetime.timedelta(hours=8)
        latest_news = {
            'url': d.entries[0].link,
            'title': d.entries[0].title,
            'published_at': parsed_datetime_ojb.strftime('%Y-%m-%d %H:%M:%S')
        }

        yield response.follow(latest_news.get('url'), callback=self.parse_article)

    def parse_article(self, response):
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        header_wrapper = soup.find('div', 'shareBar__info--author')
        article_title = soup.find('h2', id='story_art_title')
        published_at_str = header_wrapper.span
        published_at = published_at_str.text
        vals = [i.text.strip(' \r\t\n').replace('\n','') for i in soup.find_all("div", id='article_body')]
        vals = filter(None, vals)
        content = ','.join(vals)
        article = NewsBotsItem()
        article['url'] = response.url
        article['title'] = article_title.text
        article['published_at'] = published_at
        article['content'] = content

        yield article