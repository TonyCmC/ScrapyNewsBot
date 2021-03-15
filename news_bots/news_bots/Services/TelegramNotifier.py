import requests
import json


class TelegramNotifier:
    def __init__(self, token, chat_id):
        self.domain = 'https://api.telegram.org'
        self.bot_token = 'bot' + token
        self.chat_id = chat_id

    def send_message(self, msg):
        if type(msg) == dict:
            msg = json.dumps(msg)
        msg = list(self.text_slicer(msg[:200]))
        for text in msg:
            res = {
                "chat_id": self.chat_id,
                "text": str(text)
            }
            endpoint = 'sendMessage'
            url = "{domain}/{bot_token}/{endpoint}".format(domain=self.domain,
                                                           bot_token=self.bot_token,
                                                           endpoint=endpoint)
            res = requests.post(url, data=res)
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

    def text_slicer(self, full_text, chucks=4096):
        """Yield successive n-sized chunks from lst.
        :type full_text: str, full_text for slicing
        :type chucks: int, how many chucks that have to be split
        :return generator object
        """
        for i in range(0, len(full_text), chucks):
            yield full_text[i:i + chucks]

