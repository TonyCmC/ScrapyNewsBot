import datetime
from time import mktime
from typing import Dict, Optional
import feedparser
from .base_crawler import NewsCrawler


class UdnCrawler(NewsCrawler):
    """聯合新聞網財經新聞爬蟲"""
    
    def __init__(self):
        super().__init__("經濟日報")
    
    def get_latest_news(self) -> Optional[Dict[str, str]]:
        """抓取聯合新聞網最新財經新聞"""
        try:
            # 抓取 RSS feed
            response = self.session.get('https://money.udn.com/rssfeed/news/1001/5591/5612?ch=money', timeout=10)
            response.raise_for_status()
            
            # 解析 RSS
            feed = feedparser.parse(response.text)
            if not feed.entries:
                print(f"{self.name}: RSS feed 沒有文章")
                return None
            
            latest_entry = feed.entries[0]
            
            # 解析發布時間
            parsed_datetime = datetime.datetime.fromtimestamp(mktime(feed.feed.published_parsed))
            parsed_datetime += datetime.timedelta(hours=8)  # 調整時區
            published_at = parsed_datetime.strftime('%Y-%m-%d %H:%M:%S')
            
            # 抓取文章內容
            article_soup = self.fetch_page(latest_entry.link)
            if not article_soup:
                return None
            
            # 提取文章內容
            article_body = article_soup.find("section", id='article_body')
            title_element = article_soup.find('h1', id='story_art_title')
            time_element = article_soup.find('time', 'article-body__time')
            
            if not all([article_body, title_element]):
                print(f"{self.name}: 找不到文章內容元素")
                return None
            
            content = article_body.text.strip().replace('\n', '')
            
            return {
                'url': latest_entry.link,
                'title': title_element.text.strip(),
                'content': content,
                'published_at': time_element.text if time_element else published_at
            }
            
        except Exception as e:
            print(f"{self.name} 爬取失敗: {e}")
            return None