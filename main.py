#!/usr/bin/env python
"""
簡化版新聞爬蟲主程式
使用 APScheduler + 自定義爬蟲類別，不依賴 Scrapy 框架
"""

from datetime import datetime

import pytz
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
from services.StockCodeService import StockCodeService
import config


TAIPEI_TZ = pytz.timezone('Asia/Taipei')

# 各爬蟲在「正常時段」（08:00-18:00）的執行間隔（秒）。
# 00:00-08:00 全部暫停不執行；18:00-00:00 為省 token 時段，間隔統一放大 NIGHT_MULTIPLIER 倍。
# TrendForce 為研究機構的產業快訊，更新頻率遠低於一般新聞網站（約每週數篇），基礎間隔本身就拉長為 5 分鐘。
BASE_INTERVALS = {
    'chinatimes': 60,
    'udn': 70,
    'ettoday': 80,
    # 'ctee': 90,  # 目前停用
    'ltn': 100,
    'cnyes': 50,
    'yahoo': 110,
    'trendforce': 300,
    'technews': 90,
}

NIGHT_MULTIPLIER = 10  # 18:00-00:00 執行間隔放大倍數


def job_id_of(crawler_name: str) -> str:
    return f'{crawler_name}_job'


class NewsManager:
    """新聞管理器 - 負責排程和協調爬蟲與處理器"""

    def __init__(self, stock_code_service: StockCodeService = None):
        self.processor = NewsProcessor(stock_code_service)

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


def get_current_period(now: datetime = None) -> str:
    """依台灣時間判斷目前所在時段：
    'pause'  00:00-08:00 暫停所有爬蟲
    'normal' 08:00-18:00 正常頻率
    'slow'   18:00-00:00 頻率放慢 NIGHT_MULTIPLIER 倍
    """
    now = now or datetime.now(TAIPEI_TZ)
    hour = now.hour
    if 0 <= hour < 8:
        return 'pause'
    if 8 <= hour < 18:
        return 'normal'
    return 'slow'


def apply_pause(scheduler: BlockingScheduler):
    """00:00 觸發：暫停所有爬蟲排程"""
    for name in BASE_INTERVALS:
        scheduler.pause_job(job_id_of(name))
    print("[00:00] 進入省 token 時段，暫停所有爬蟲")


def apply_normal(scheduler: BlockingScheduler):
    """08:00 觸發：恢復正常執行頻率"""
    for name, seconds in BASE_INTERVALS.items():
        scheduler.reschedule_job(job_id_of(name), trigger='interval', seconds=seconds)
        scheduler.resume_job(job_id_of(name))
    print("[08:00] 恢復正常執行頻率")


def apply_slow(scheduler: BlockingScheduler):
    """18:00 觸發：執行間隔放大 NIGHT_MULTIPLIER 倍"""
    for name, seconds in BASE_INTERVALS.items():
        scheduler.reschedule_job(job_id_of(name), trigger='interval', seconds=seconds * NIGHT_MULTIPLIER)
        scheduler.resume_job(job_id_of(name))  # 保險：確保不是暫停狀態
    print(f"[18:00] 進入低頻時段，執行間隔 x{NIGHT_MULTIPLIER}")


def main():
    """主程式入口"""
    # 台股上市櫃公司代號對照表：啟動時先同步一次確保可用，之後交給排程每日更新，
    # 用來校正 OpenAI 提取股票關鍵字時可能出現的代號/上市狀態幻覺
    stock_code_service = StockCodeService(config.STOCK_CODE_FILE)
    stock_code_service.sync()

    manager = NewsManager(stock_code_service)
    scheduler = BlockingScheduler(timezone=TAIPEI_TZ)

    # 每日凌晨 7:00 重新同步一次上市櫃公司代號對照表（早於 8:00 恢復正常爬蟲頻率）
    scheduler.add_job(stock_code_service.sync, 'cron', hour=7, minute=0, id='sync_stock_code_job')

    # 依基礎頻率註冊各爬蟲排程，實際頻率會依下方時段控制排程動態調整
    for name, seconds in BASE_INTERVALS.items():
        scheduler.add_job(
            manager.run_crawler,
            'interval',
            args=[name],
            seconds=seconds,
            id=job_id_of(name)
        )

    # 時段控制排程：00:00 暫停、08:00 恢復正常頻率、18:00 放慢頻率
    scheduler.add_job(lambda: apply_pause(scheduler), 'cron', hour=0, minute=0, id='pause_night_job')
    scheduler.add_job(lambda: apply_normal(scheduler), 'cron', hour=8, minute=0, id='resume_day_job')
    scheduler.add_job(lambda: apply_slow(scheduler), 'cron', hour=18, minute=0, id='slowdown_evening_job')

    # 啟動當下依現在時間套用正確時段，避免程式在中途啟動時頻率不對
    period = get_current_period()
    if period == 'pause':
        apply_pause(scheduler)
    elif period == 'slow':
        apply_slow(scheduler)
    # 'normal' 不需額外處理，上面 add_job 當下就是用 BASE_INTERVALS 建立

    print("新聞爬蟲排程器已啟動...")
    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("排程器已停止")
        scheduler.shutdown()


if __name__ == '__main__':
    main()
