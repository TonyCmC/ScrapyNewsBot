import datetime
import html
from typing import Dict, Optional
from bs4 import BeautifulSoup
from .base_crawler import NewsCrawler


class CnyesCrawler(NewsCrawler):
    """鉅亨網台股新聞爬蟲"""

    # 鉅亨網已無公開 RSS，改用其前端頁面實際呼叫的 JSON API，
    # 回傳內容已依時間排序，且文章內文直接內嵌在列表回應中，
    # 不需要再額外抓取文章頁面
    API_URL = 'https://news.cnyes.com/api/v3/news/category/tw_stock'

    def __init__(self):
        super().__init__("鉅亨網")

    def get_latest_news(self) -> Optional[Dict[str, str]]:
        """抓取鉅亨網最新台股新聞"""
        try:
            response = self.session.get(self.API_URL, params={'limit': 1}, timeout=10)
            response.raise_for_status()

            items = response.json().get('items', {}).get('data', [])
            if not items:
                print(f"{self.name}: 沒有抓到新聞")
                return None

            latest = items[0]
            news_id = latest.get('newsId')
            title = latest.get('title')
            raw_content = latest.get('content')
            publish_at = latest.get('publishAt')

            if not all([news_id, title, raw_content]):
                print(f"{self.name}: 找不到文章內容欄位")
                return None

            # content 欄位是 HTML entity 編碼過的文章內文，需先解碼再去除標籤
            soup = BeautifulSoup(html.unescape(raw_content), 'html.parser')
            paragraphs = [p.get_text(strip=True) for p in soup.find_all('p')]
            content = ''.join(filter(None, paragraphs))

            if not content:
                print(f"{self.name}: 文章內文為空")
                return None

            # publishAt 為 UTC unix timestamp，需轉換為台北時間
            published_at = ''
            if publish_at:
                dt = datetime.datetime.utcfromtimestamp(publish_at) + datetime.timedelta(hours=8)
                published_at = dt.strftime('%Y-%m-%d %H:%M:%S')

            return {
                'url': f'https://news.cnyes.com/news/id/{news_id}',
                'title': title.strip(),
                'content': content,
                'published_at': published_at
            }

        except Exception as e:
            print(f"{self.name} 爬取失敗: {e}")
            return None
