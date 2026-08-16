import datetime
from time import mktime
from typing import Dict, Optional
import feedparser
from .base_crawler import NewsCrawler


class TrendForceCrawler(NewsCrawler):
    """TrendForce(集邦科技)新聞爬蟲"""

    # TrendForce 沒有單一總覽 RSS，只有分別依產業分類的 feed
    # （見 https://www.trendforce.com.tw/presscenter/rss.html），
    # 因此逐一抓取各分類後，取所有分類中發布時間最新的一篇
    FEED_CATEGORIES = [
        'Semiconductors', 'Display', 'macroeconomic', 'Consumer_electronics',
        'Communication', 'Emerging_technology', 'Energy', 'LED'
    ]
    FEED_URL_TEMPLATE = 'https://www.trendforce.com.tw/feed/{category}.html'

    def __init__(self):
        super().__init__("TrendForce")

    def get_latest_news(self) -> Optional[Dict[str, str]]:
        """抓取 TrendForce 所有分類中最新一篇新聞"""
        try:
            latest_entry = self._fetch_latest_entry()
            if not latest_entry:
                print(f"{self.name}: 所有分類 RSS 都沒有文章")
                return None

            # feedparser 會將 published_parsed 正規化為 UTC，需手動轉換為台北時間
            parsed_datetime = datetime.datetime.fromtimestamp(
                mktime(latest_entry.published_parsed)
            ) + datetime.timedelta(hours=8)
            published_at = parsed_datetime.strftime('%Y-%m-%d %H:%M:%S')

            # RSS 的 description 只有第一段預覽文字，完整內文仍需抓文章頁
            article_soup = self.fetch_page(latest_entry.link)
            if not article_soup:
                return None

            article_body = article_soup.find('article', class_='presscenter')
            if not article_body:
                print(f"{self.name}: 找不到文章內容元素")
                return None

            paragraphs = [p.get_text(strip=True) for p in article_body.find_all('p')]
            content = ''.join(filter(None, paragraphs))

            if not content:
                print(f"{self.name}: 文章內文為空")
                return None

            return {
                'url': latest_entry.link,
                'title': latest_entry.title.strip(),
                'content': content,
                'published_at': published_at
            }

        except Exception as e:
            print(f"{self.name} 爬取失敗: {e}")
            return None

    def _fetch_latest_entry(self):
        """逐一抓取各分類 RSS，回傳所有分類中發布時間最新的一篇文章項目"""
        latest_entry = None
        latest_time = None

        for category in self.FEED_CATEGORIES:
            url = self.FEED_URL_TEMPLATE.format(category=category)
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
            except Exception as e:
                print(f"{self.name}: 抓取 {category} RSS 失敗: {e}")
                continue

            feed = feedparser.parse(response.text)
            if not feed.entries:
                continue

            entry = feed.entries[0]
            if not entry.get('published_parsed'):
                continue

            if latest_time is None or entry.published_parsed > latest_time:
                latest_time = entry.published_parsed
                latest_entry = entry

        return latest_entry
