import datetime
from time import mktime
from typing import Dict, Optional
import feedparser
from .base_crawler import NewsCrawler


class YahooCrawler(NewsCrawler):
    """Yahoo奇摩股市財經新聞爬蟲"""

    RSS_URL = 'https://tw.stock.yahoo.com/rss?category=tw-market'

    # Yahoo股市新聞轉載自多家聯播媒體，正文段落外常混有「加入為 Google 偏好來源」
    # 「OO新聞網提醒您」「更多OO新聞網報導」等導讀/免責文字，需過濾掉
    SKIP_KEYWORDS = ('提醒您', '僅供參考', '審慎評估風險')

    def __init__(self):
        super().__init__("Yahoo奇摩股市")

    def get_latest_news(self) -> Optional[Dict[str, str]]:
        """抓取 Yahoo奇摩股市最新財經新聞"""
        try:
            # 抓取 RSS feed
            response = self.session.get(self.RSS_URL, timeout=10)
            response.raise_for_status()

            feed = feedparser.parse(response.text)
            if not feed.entries:
                print(f"{self.name}: RSS feed 沒有文章")
                return None

            latest_entry = feed.entries[0]

            # 解析發布時間（若文章頁面有更精確的時間會再覆蓋）
            published_at = ''
            if latest_entry.get('published_parsed'):
                published_at = datetime.datetime.fromtimestamp(
                    mktime(latest_entry.published_parsed)
                ).strftime('%Y-%m-%d %H:%M:%S')

            # 抓取文章內容
            article_soup = self.fetch_page(latest_entry.link)
            if not article_soup:
                return None

            title_element = article_soup.find('h1')
            article_body = article_soup.find('section', class_='module-article-body')
            time_element = article_soup.find('time')

            if not all([title_element, article_body]):
                print(f"{self.name}: 找不到文章內容元素")
                return None

            # 正文段落固定包在 class="atoms" 的容器內，藉此排除頁首的 Google/Yahoo 訂閱推廣文字
            paragraphs = [
                p.get_text(strip=True)
                for p in article_body.find_all('p')
                if p.parent and 'atoms' in (p.parent.get('class') or [])
            ]
            paragraphs = [p for p in paragraphs if self._is_valid_paragraph(p)]
            content = ''.join(filter(None, paragraphs))

            if not content:
                print(f"{self.name}: 文章內文為空")
                return None

            if time_element and time_element.get('datetime'):
                try:
                    dt = datetime.datetime.strptime(time_element['datetime'], '%Y-%m-%dT%H:%M:%S.%fZ')
                    dt += datetime.timedelta(hours=8)
                    published_at = dt.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    pass

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
        """過濾聯播媒體常見的提醒/免責聲明段落，以及結尾的「更多OO報導」導流段落"""
        if not text:
            return False
        if any(keyword in text for keyword in cls.SKIP_KEYWORDS):
            return False
        if text.startswith('更多') and ('報導' in text or '新聞' in text):
            return False
        return True
