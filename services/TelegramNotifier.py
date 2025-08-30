import requests
import json
import urllib.parse

from config import TG_TOKEN, TG_CHAT_ID


class TelegramNotifier:
    def __init__(self, token=TG_TOKEN, chat_id=TG_CHAT_ID):
        self.domain = 'https://api.telegram.org'
        self.bot_token = 'bot' + token
        self.chat_id = chat_id

    def send_message(self, msg):
        if type(msg) == dict:
            msg = json.dumps(msg)
        msg = list(self.text_slicer(msg))
        for text in msg:
            #text = urllib.parse.quote_plus(str(text))
            res = {
                "chat_id": self.chat_id,
                "text": str(text),
                "parse_mode": "HTML"
            }
            endpoint = 'sendMessage'
            url = "{domain}/{bot_token}/{endpoint}".format(domain=self.domain,
                                                           bot_token=self.bot_token,
                                                           endpoint=endpoint)
            res = requests.get(url, params=res)
            print(res.text)

    def send_photo(self, img_path):
        data = {"chat_id": self.chat_id}
        file = {'photo': open(img_path, 'rb')}
        endpoint = 'sendPhoto'
        url = "{domain}/{bot_token}/{endpoint}".format(domain=self.domain,
                                                       bot_token=self.bot_token,
                                                       endpoint=endpoint)
        res = requests.post(url, data=data, files=file)
        print(res.text)

    def send_file(self, file_path):
        data = {"chat_id": self.chat_id}
        file = {'document': open(file_path, 'rb')}
        endpoint = 'sendDocument'
        url = "{domain}/{bot_token}/{endpoint}".format(domain=self.domain,
                                                       bot_token=self.bot_token,
                                                       endpoint=endpoint)
        res = requests.post(url, data=data, files=file)
        print(res.text)

    def get_update(self):
        endpoint = 'getUpdates'
        url = "{domain}/{bot_token}/{endpoint}".format(domain=self.domain,
                                                       bot_token=self.bot_token,
                                                       endpoint=endpoint)
        res = requests.get(url)
        print(res.text)

    def text_slicer(self, full_text, chucks=4096):
        """Yield successive n-sized chunks from lst.
        :type full_text: str, full_text for slicing
        :type chucks: int, how many chucks that have to be split
        :return generator object
        """
        for i in range(0, len(full_text), chucks):
            yield full_text[i:i + chucks]


if __name__ == '__main__':
    tgn = TelegramNotifier()
    tgn.get_update()