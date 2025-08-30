from datetime import datetime
from typing import Dict, Optional
from .base_crawler import NewsCrawler


class ChinaTimesCrawler(NewsCrawler):
    """中時電子報財經新聞爬蟲"""
    
    def __init__(self):
        super().__init__("中時電子報")
    
    def get_latest_news(self) -> Optional[Dict[str, str]]:
        """抓取中時電子報最新財經新聞"""
        # 使用 context manager 避免重複開關瀏覽器
        with self.browser_session() as driver:
            if not driver:
                return None
            
            # 抓取列表頁
            soup = self.fetch_page_with_browser(driver, 'https://www.chinatimes.com/realtimenews/260410')
            if not soup:
                return None
            
            # 找到第一篇文章
            article_div = soup.find('h3', 'title')
            publish_time = soup.find('time')
            
            if not article_div or not publish_time:
                print(f"{self.name}: 找不到文章元素")
                return None
            
            article_url = 'https://www.chinatimes.com' + article_div.a['href']
            
            # 使用同一個瀏覽器實例抓取文章內容
            article_soup = self.fetch_page_with_browser(driver, article_url)
            if not article_soup:
                return None
            
            article_title = article_soup.find('h1', 'article-title')
            header_wrapper = article_soup.find('div', 'meta-info-wrapper')
            article_body = article_soup.find('div', 'article-body')
            
            if not all([article_title, header_wrapper, article_body]):
                print(f"{self.name}: 找不到文章內容元素")
                return None
            
            # 解析發布時間
            published_at_str = header_wrapper.div.time.text
            published_at = datetime.strptime(published_at_str, '%H:%M%Y/%m/%d').strftime('%Y-%m-%d %H:%M:00')
            
            # 提取文章內容
            paragraphs = [p.text.strip().replace('\n', '') for p in article_body.find_all('p')]
            content = ','.join(filter(None, paragraphs))
            
            return {
                'url': article_url,
                'title': article_title.text.strip(),
                'content': content,
                'published_at': published_at
            }