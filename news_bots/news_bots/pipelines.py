# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json

import jieba

from news_bots import settings
from news_bots.Services.TelegramNotifier import TelegramNotifier

jieba.set_dictionary('news_bots/Resources/dict.txt.big')
jieba.load_userdict('news_bots/Resources/userdict.txt')


class NewsBotsPipeline:
    def __init__(self):
        self.stock_list: dict
        with open('news_bots/Resources/stock.json', 'r', encoding='utf-8') as f:
            self.stock_list = json.loads(f.read())

    def process_item(self, item, spider):
        if self.check_previous_url(item):
            tg = TelegramNotifier(settings.TG_TOKEN, settings.TG_CHAT_ID)
            if '謝金河' not in item.get("title"):
                keywords = self.text_split(item.get('content'))
                tg.send_message("{title}\n{keywords}\n{url}\n{published_at}".format(title=item.get("title"),
                                                                                    keywords=keywords,
                                                                                    url=item.get("url"),
                                                                                    published_at=item.get(
                                                                                        "published_at")))
        return item

    def check_previous_url(self, obj):
        obj = dict(obj)
        maximum_items = 20
        file_path = 'logs/previous.log'
        with open(file_path, 'r', encoding='utf-8') as f:
            res = f.read()
        res = json.loads(res)
        url_list = [i.get('url') for i in res]
        if len(res) != 0 and obj.get('url') not in url_list:
            if len(res) > maximum_items:
                res.pop(0)
            res.append(obj)
            with open(file_path, 'w', encoding='utf-8') as fw:
                fw.write(json.dumps(res))
            return True
        return False

    def text_split(self, values):
        seg_list = jieba.cut(values, cut_all=False)
        result = []
        for seg in seg_list:
            if seg in self.stock_list.values():
                result.append('#' + seg)
        return set(result)
