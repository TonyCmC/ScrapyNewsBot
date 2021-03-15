from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from apscheduler.schedulers.twisted import TwistedScheduler
from news_bots.spiders.ChinaTimes import ChinatimesSpider
from news_bots.spiders.Ettoday import EttodaySpider
from news_bots.spiders.Udn import UdnSpider

process = CrawlerProcess(get_project_settings())
scheduler = TwistedScheduler()
scheduler.add_job(process.crawl, 'interval', args=[ChinatimesSpider], seconds=60)
scheduler.add_job(process.crawl, 'interval', args=[EttodaySpider], seconds=70)
scheduler.add_job(process.crawl, 'interval', args=[UdnSpider], seconds=80)
scheduler.start()
process.start(False)
