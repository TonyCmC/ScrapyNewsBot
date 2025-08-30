from datetime import datetime
from typing import Dict, Optional
from .base_crawler import NewsCrawler


class CteeCrawler(NewsCrawler):
    """工商時報證券即時新聞爬蟲"""
    
    def __init__(self):
        super().__init__("工商時報")
    
    def get_latest_news(self) -> Optional[Dict[str, str]]:
        """抓取工商時報最新證券新聞"""
        # 工商時報需要使用瀏覽器才能正常訪問
        with self.browser_session() as driver:
            if not driver:
                return None
            
            # 抓取證券即時新聞列表頁
            soup = self.fetch_page_with_browser(driver, 'https://www.ctee.com.tw/livenews/stock')
            if not soup:
                return None
            
            # 找到第一篇新聞
            news_items = soup.find_all('div', class_='newslist__card')
            if not news_items:
                print(f"{self.name}: 找不到新聞列表")
                return None
            
            first_news = news_items[0]
            title_element = first_news.find('h3', class_='news-title')
            time_element = first_news.find('time')

            if not title_element:
                print(f"{self.name}: 找不到新聞標題")
                return None
            
            article_url = 'https://www.ctee.com.tw' + title_element.a.get('href')
            title = title_element.text.strip()
            
            # 抓取文章內容
            article_soup = self.fetch_page_with_browser(driver, article_url)
            if not article_soup:
                return None
            
            # 提取文章內容
            article_body = article_soup.find('div', class_='post-content')
            publish_time = article_soup.find('time', class_='post-date')
            
            if not article_body:
                print(f"{self.name}: 找不到文章內容")
                return None
            
            # 提取文章段落
            paragraphs = [p.text.strip() for p in article_body.find_all('p')]
            content = ' '.join(filter(None, paragraphs))
            
            # 處理發布時間
            published_at = ""
            if publish_time:
                published_at = publish_time.get('datetime', '')
                if published_at:
                    try:
                        # 轉換時間格式
                        dt = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                        published_at = dt.strftime('%Y-%m-%d %H:%M:00')
                    except:
                        published_at = publish_time.text.strip()
            
            return {
                'url': article_url,
                'title': title,
                'content': content,
                'published_at': published_at
            }