#!/usr/bin/env python
"""
測試簡化版爬蟲
"""

from crawlers.chinatimes_crawler import ChinaTimesCrawler
from crawlers.udn_crawler import UdnCrawler
from crawlers.ettoday_crawler import EttodayCrawler
from crawlers.ctee_crawler import CteeCrawler
from crawlers.ltn_crawler import LtnCrawler
from crawlers.cnyes_crawler import CnyesCrawler
from crawlers.yahoo_crawler import YahooCrawler
from crawlers.trendforce_crawler import TrendForceCrawler
from processors.news_processor import NewsProcessor


def test_crawler_only(crawler_class, name):
    """測試單個爬蟲（僅爬取功能）"""
    print(f"\n=== 測試 {name} 爬取功能 ===")
    crawler = crawler_class()
    news = crawler.get_latest_news()
    
    if news:
        print(f"✅ 成功抓取新聞")
        print(f"標題: {news['title']}")
        print(f"網址: {news['url']}")
        print(f"發布時間: {news['published_at']}")
        print(f"內容長度: {len(news['content'])} 字元")
        print(f"內容預覽: {news['content'][:100]}...")
        return news
    else:
        print(f"❌ 抓取失敗")
        return None


def test_full_pipeline():
    """測試完整流程（爬取 + 處理）"""
    print(f"\n=== 測試完整流程 ===")
    try:
        processor = NewsProcessor()
        crawler = UdnCrawler()
        news = crawler.get_latest_news()
        
        if news:
            result = processor.process_news(news, crawler.name)
            print(f"✅ 完整流程測試: {'成功' if result else '跳過'}")
        else:
            print(f"❌ 爬取失敗，無法測試完整流程")
    except Exception as e:
        print(f"❌ 完整流程測試失敗: {e}")


if __name__ == '__main__':
    # 測試各個爬蟲
    test_crawler_only(ChinaTimesCrawler, "中時電子報")
    # test_crawler_only(UdnCrawler, "聯合新聞網")
    # test_crawler_only(EttodayCrawler, "ETtoday新聞雲")
    test_crawler_only(CteeCrawler, "工商時報")
    # test_crawler_only(LtnCrawler, "自由財經")
    test_crawler_only(CnyesCrawler, "鉅亨網")
    test_crawler_only(YahooCrawler, "Yahoo奇摩股市")
    test_crawler_only(TrendForceCrawler, "TrendForce")
    
    # 測試完整流程（需要設定 .env）
    # test_full_pipeline()