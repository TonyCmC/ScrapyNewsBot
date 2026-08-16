import datetime
from time import mktime
from typing import Dict, Optional
import feedparser
from .base_crawler import NewsCrawler


class TechNewsCrawler(NewsCrawler):
    """TechNews 科技新報財經新聞爬蟲"""

    RSS_URL = 'https://technews.tw/category/finance/feed/'

    # 文章結尾常見的贊助/Google新聞追蹤導流文字，非正文內容
    SKIP_KEYWORDS = ('看完覺得有幫助', '咖啡贊助', 'Google 新聞', '科技新知，時時更新')

    def __init__(self):
        super().__init__("TechNews科技新報")

    def get_latest_news(self) -> Optional[Dict[str, str]]:
        """抓取 TechNews 科技新報最新財經新聞"""
        try:
            # 抓取 RSS feed
            response = self.session.get(self.RSS_URL, timeout=10)
            response.raise_for_status()

            feed = feedparser.parse(response.text)
            if not feed.entries:
                print(f"{self.name}: RSS feed 沒有文章")
                return None

            latest_entry = feed.entries[0]

            # 解析發布時間（RSS pubDate 為 GMT，feedparser 正規化為 UTC，需轉換為台北時間）
            published_at = ''
            if latest_entry.get('published_parsed'):
                dt = datetime.datetime.fromtimestamp(mktime(latest_entry.published_parsed))
                dt += datetime.timedelta(hours=8)
                published_at = dt.strftime('%Y-%m-%d %H:%M:%S')

            # 抓取文章內容
            article_soup = self.fetch_page(latest_entry.link)
            if not article_soup:
                return None

            title_element = article_soup.find('h1', class_='entry-title')
            article_body = article_soup.find(class_='entry-content')

            if not all([title_element, article_body]):
                print(f"{self.name}: 找不到文章內容元素")
                return None

            # 提取文章段落，過濾結尾的贊助/追蹤導流文字
            paragraphs = [p.get_text(strip=True) for p in article_body.find_all('p')]
            paragraphs = [p for p in paragraphs if self._is_valid_paragraph(p)]
            content = ''.join(filter(None, paragraphs))

            if not content:
                print(f"{self.name}: 文章內文為空")
                return None

            return {
                'url': latest_entry.link,
                'title': title_element.get_text(strip=True),
                'content': content,
                'published_at': published_at
            }

        except Exception as e:
            print(f"{self.name} 爬取失敗: {e}")
            return None

    @classmethod
    def _is_valid_paragraph(cls, text: str) -> bool:
        """過濾文章結尾常見的贊助/追蹤導流段落"""
        if not text:
            return False
        return not any(keyword in text for keyword in cls.SKIP_KEYWORDS)
