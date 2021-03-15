# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from peewee import MySQLDatabase, Model, AutoField, CharField, DateTimeField

from news_bots.Services.TelegramNotifier import TelegramNotifier
from news_bots import settings

db = MySQLDatabase(database=settings.MYSQL_DATABASE,
                   user=settings.MYSQL_USERNAME,
                   password=settings.MYSQL_PASSWORD,
                   host=settings.MYSQL_HOST,
                   port=int(settings.MYSQL_PORT))

tg = TelegramNotifier(settings.TG_TOKEN, settings.TG_CHAT_ID)


class NewsBotsItem(scrapy.Item):
    # define the fields for your item here like:
    url = scrapy.Field()
    title = scrapy.Field()
    published_at = scrapy.Field()
    content = scrapy.Field()


class ScrapyTest(Model):
    id = AutoField(primary_key=True)
    last_price = CharField(default='')
    change = CharField(default='')
    last_timedate = DateTimeField()
    created_at = DateTimeField()
    updated_at = DateTimeField()

    class Meta:
        database = db
        table_name = 'scrapy_test'
