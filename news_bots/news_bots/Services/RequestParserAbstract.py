import os

import jieba
import requests
import json

from news_bots.definition import ROOT_DIR

jieba.set_dictionary(os.path.join(ROOT_DIR, '/news_bot/Resources/dict.txt.big'))
jieba.load_userdict(os.path.join(ROOT_DIR, '/news_bot/Resources/userdict.txt'))


class RequestParserAbstract:
    def __init__(self):
        self.stock_list: dict
        with open('Resources/stock.json', 'r', encoding='utf-8') as f:
            self.stock_list = json.loads(f.read())

    def get_context_from_url(self, url):
        header_payload = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'
        }
        res = requests.get(url, headers=header_payload)
        # now = datetime.now().strftime('%Y-%m-%d-%H-%M-%S.log')
        # with open('logs/{0}'.format(now), 'w', encoding='utf-8') as f:
        #     f.write(res.text)
        return res.text

    def parse_html_data(self, html_doc):
        pass

    def text_split(self, values):
        seg_list = jieba.cut(values, cut_all=False)
        result = []
        for seg in seg_list:
            if seg in self.stock_list.values():
                result.append('#' + seg)
        return set(result)

    def check_previous_url(self, obj):
        maximum_items = 20
        with open('news_bots/logs/previous.log', 'r', encoding='utf-8') as f:
            res = f.read()
        res = json.loads(res)
        url_list = [i.get('url') for i in res]
        if len(res) != 0 and obj.get('url') not in url_list:
            if len(res) > maximum_items:
                res.pop(0)
            res.append(obj)
            with open('logs/previous.log', 'w', encoding='utf-8') as fw:
                fw.write(json.dumps(res))
            return True
        return False
