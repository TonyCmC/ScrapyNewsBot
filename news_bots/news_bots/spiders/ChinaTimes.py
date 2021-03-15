import json
from datetime import datetime

import bs4
import scrapy

from news_bots.items import NewsBotsItem

class ChinatimesSpider(scrapy.Spider):
    name = 'ChinaTimes'
    allowed_domains = ['www.chinatimes.com']
    start_urls = ['https://www.chinatimes.com/realtimenews/260410?chdtv']

    def parse(self, response):
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        article_div = soup.find_all('h3', 'title')
        publish_at = soup.find_all('time')
        result = []
        for i in range(len(article_div)):
            result.append({
                'url': 'https://www.chinatimes.com' + article_div[i].a['href'],
                'title': article_div[i].text,
                'published_at': publish_at[i]['datetime']
            })
        latest_news = result[0]
        yield response.follow(latest_news.get('url'), callback=self.parse_article)

    def parse_article(self, response):
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        article_title = soup.find('h1', 'article-title')
        header_wrapper = soup.find('div', 'meta-info-wrapper')
        published_at_str = header_wrapper.div.time.text
        published_at = datetime.strptime(published_at_str, '%H:%M%Y/%m/%d').strftime('%Y-%m-%d %H:%M:00')
        article_div = soup.find('div', 'article-body')
        vals = [i.text.strip(' \r\t\n').replace('\n', '') for i in article_div.find_all('p')]
        vals = filter(None, vals)
        content = ','.join(vals)
        article = NewsBotsItem()
        article['url'] = response.url
        article['title'] = article_title.text
        article['published_at'] = published_at
        article['content'] = content

        yield article
