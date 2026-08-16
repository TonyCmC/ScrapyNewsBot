#!/usr/bin/env python
"""
簡化版新聞爬蟲主程式
使用 APScheduler + 自定義爬蟲類別，不依賴 Scrapy 框架
"""

from apscheduler.schedulers.blocking import BlockingScheduler
from crawlers.chinatimes_crawler import ChinaTimesCrawler
from crawlers.udn_crawler import UdnCrawler
from crawlers.ettoday_crawler import EttodayCrawler
from crawlers.ctee_crawler import CteeCrawler
from crawlers.ltn_crawler import LtnCrawler
from crawlers.cnyes_crawler import CnyesCrawler
from crawlers.yahoo_crawler import YahooCrawler
from crawlers.trendforce_crawler import TrendForceCrawler
from crawlers.technews_crawler import TechNewsCrawler
from processors.news_processor import NewsProcessor


class NewsManager:
    """新聞管理器 - 負責排程和協調爬蟲與處理器"""
    
    def __init__(self):
        self.processor = NewsProcessor()
        
        # 初始化爬蟲
        self.crawlers = {
            'chinatimes': ChinaTimesCrawler(),
            'udn': UdnCrawler(),
            'ettoday': EttodayCrawler(),
            # 'ctee': CteeCrawler(),
            'ltn': LtnCrawler(),
            'cnyes': CnyesCrawler(),
            'yahoo': YahooCrawler(),
            'trendforce': TrendForceCrawler(),
            'technews': TechNewsCrawler()
        }
    
    def run_crawler(self, crawler_name: str):
        """執行指定爬蟲並處理新聞"""
        crawler = self.crawlers.get(crawler_name)
        if not crawler:
            print(f"找不到爬蟲: {crawler_name}")
            return
        
        print(f"開始處理 {crawler.name} 新聞...")
        
        # 爬取最新新聞
        news = crawler.get_latest_news()
        
        # 交給處理器處理
        self.processor.process_news(news, crawler.name)


def main():
    """主程式入口"""
    manager = NewsManager()
    scheduler = BlockingScheduler()
    
    # 設定排程任務
    scheduler.add_job(
        manager.run_crawler, 
        'interval', 
        args=['chinatimes'], 
        seconds=60,
        id='chinatimes_job'
    )
    
    scheduler.add_job(
        manager.run_crawler, 
        'interval', 
        args=['udn'], 
        seconds=70,
        id='udn_job'
    )
    
    scheduler.add_job(
        manager.run_crawler, 
        'interval', 
        args=['ettoday'], 
        seconds=80,
        id='ettoday_job'
    )
    
    # scheduler.add_job(
    #     manager.run_crawler,
    #     'interval',
    #     args=['ctee'],
    #     seconds=90,
    #     id='ctee_job'
    # )
    #
    scheduler.add_job(
        manager.run_crawler,
        'interval',
        args=['ltn'],
        seconds=100,
        id='ltn_job'
    )

    scheduler.add_job(
        manager.run_crawler,
        'interval',
        args=['cnyes'],
        seconds=50,
        id='cnyes_job'
    )

    scheduler.add_job(
        manager.run_crawler,
        'interval',
        args=['yahoo'],
        seconds=110,
        id='yahoo_job'
    )

    # TrendForce 為研究機構的產業快訊，更新頻率遠低於一般新聞網站（約每週數篇），
    # 排程間隔拉長為 5 分鐘，避免不必要的頻繁請求
    scheduler.add_job(
        manager.run_crawler,
        'interval',
        args=['trendforce'],
        seconds=300,
        id='trendforce_job'
    )

    scheduler.add_job(
        manager.run_crawler,
        'interval',
        args=['technews'],
        seconds=90,
        id='technews_job'
    )

    print("新聞爬蟲排程器已啟動...")
    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("排程器已停止")
        scheduler.shutdown()


if __name__ == '__main__':
    main()