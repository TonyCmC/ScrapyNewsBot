import datetime
import re
from typing import Dict, Optional
import feedparser
from .base_crawler import NewsCrawler


class EttodayCrawler(NewsCrawler):
    """ETtoday 新聞雲財經新聞爬蟲"""
    
    def __init__(self):
        super().__init__("ETtoday新聞雲")
    
    def get_latest_news(self) -> Optional[Dict[str, str]]:
        """抓取 ETtoday 最新財經新聞"""
        try:
            # 抓取 RSS feed
            response = self.session.get('http://feeds.feedburner.com/ettoday/finance?format=xml', timeout=10)
            response.raise_for_status()
            
            # 解析 RSS
            feed = feedparser.parse(response.text)
            if not feed.entries:
                print(f"{self.name}: RSS feed 沒有文章")
                return None
            
            latest_entry = feed.entries[0]

            # 解析發布時間
            published_at = datetime.datetime.strptime(
                latest_entry.published, 
                '%a,%d %b %Y %H:%M:%S +0800'
            ).strftime('%Y-%m-%d %H:%M:%S')
            
            # 從原始 URL 提取新聞 ID，轉換為 AMP 格式
            if not latest_entry.link:
                print(f"{self.name}: 無法從 URL 提取新聞 ID")
                return None
            
            # 抓取文章內容
            article_soup = self.fetch_page(latest_entry.link)
            if not article_soup:
                return None
            
            # 提取文章元素
            article_title = article_soup.find('title', '')
            article_div = article_soup.find('div', {"itemprop":"articleBody"})
            modified_at = article_soup.find('meta', {"itemprop": "dateModified"})

            if not all([article_title, article_div]):
                print(f"{self.name}: 找不到文章內容元素")
                return None
            
            if not article_title:
                print(f"{self.name}: 找不到文章標題")
                return None

            # 更新發布時間（如果頁面有更精確的時間）
            if modified_at and modified_at.get('content'):
                published_at = datetime.datetime.strptime(
                    modified_at.get('content'),
                    '%Y-%m-%dT%H:%M:%S+08:00'
                ).strftime('%Y-%m-%d %H:%M:00')
            
            # 提取文章內容
            paragraphs = [p.text.strip().replace('\n', '') for p in article_div.find_all('p')]
            content = ','.join(filter(None, paragraphs))
            
            return {
                'url': latest_entry.link,
                'title': article_title.text.strip(),
                'content': content,
                'published_at': published_at
            }
            
        except Exception as e:
            print(f"{self.name} 爬取失敗: {e}")
            return None