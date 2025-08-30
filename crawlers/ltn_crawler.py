from datetime import datetime
from typing import Dict, Optional
from .base_crawler import NewsCrawler


class LtnCrawler(NewsCrawler):
    """自由財經即時新聞爬蟲"""
    
    def __init__(self):
        super().__init__("自由財經")
    
    def get_latest_news(self) -> Optional[Dict[str, str]]:
        """抓取自由財經最新即時新聞"""
        # 自由財經有動態載入，需要使用瀏覽器
        with self.browser_session() as driver:
            if not driver:
                return None
            
            # 抓取財經即時新聞列表頁
            soup = self.fetch_page_with_browser(driver, 'https://ec.ltn.com.tw/list/breakingnews')
            if not soup:
                return None
            
            # 找到新聞列表
            news_list = soup.find('ul', class_='listpage_news')
            if not news_list:
                print(f"{self.name}: 找不到新聞列表")
                return None
            
            # 找到第一篇新聞
            first_news = news_list.find('li')
            if not first_news:
                print(f"{self.name}: 找不到新聞項目")
                return None
            
            title_element = first_news.find('h3', class_='newstitle')
            time_element = first_news.find('font', class_='newstime')

            if not title_element:
                print(f"{self.name}: 找不到新聞標題")
                return None
            
            article_url = first_news.a.get('href')
            title = title_element.text.strip()
            
            # 處理相對路徑
            if article_url.startswith('/'):
                article_url = 'https://ec.ltn.com.tw' + article_url
            
            # 抓取文章內容
            article_soup = self.fetch_page_with_browser(driver, article_url)
            if not article_soup:
                return None
            
            # 提取文章內容
            article_body = article_soup.find('div', class_='whitecon boxTitle boxText')
            article_time = article_body.find('span', class_='time')
            
            if not article_body:
                print(f"{self.name}: 找不到文章內容")
                return None
            
            # 提取文章段落
            paragraphs = [p.text.strip() for p in article_body.find_all('p')]
            black_list = ["點我訂閱自由財經Youtube頻道", "熱門賽事、球星動態不漏接", "請繼續往下閱讀", "相關新聞","保證天天中獎", "點我下載APP", "按我看活動辦法"]
            filtered_result = []

            for idx, paragraph in enumerate(paragraphs):
                if paragraph not in black_list:
                    filtered_result.append(paragraph)

            content = ' '.join(filter(None, filtered_result))
            
            # 處理發布時間
            published_at = ""
            if article_time:
                published_at = article_time.text.strip()
            elif time_element:
                published_at = time_element.text.strip()
            
            # 嘗試格式化時間
            if published_at:
                try:
                    # 自由時報時間格式通常是 "2024/01/01 12:34"
                    if '/' in published_at and ':' in published_at:
                        dt = datetime.strptime(published_at, '%Y/%m/%d %H:%M')
                        published_at = dt.strftime('%Y-%m-%d %H:%M:00')
                except:
                    pass  # 保持原格式
            
            return {
                'url': article_url,
                'title': title,
                'content': content,
                'published_at': published_at
            }