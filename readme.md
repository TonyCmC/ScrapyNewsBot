# Scrapy News Telegram bot (新聞關鍵字機器人)

## Description:
In order to receive the latest news about the finance, I build up this project to crawl the latest news via the RSS or the news list provided by Udn, ChinaTimes, Ettoday. I use Scrapy framework, split the keywords by Jieba package then send the result to particular Telegram Group with Telegram Bot API.

### Message Format:
```
Title
{'keyword1', 'keyword2', 'keyword3'...}
https://exampleURL.com
YYYY-mm-dd HH:MM:SS
```

### Example Message:
```
台股攻勢暫停！早盤小跌近30點 台積電、鴻海平盤震盪
{'#大立光', '#台積電', '#鴻海'}
https://finance.ettoday.net/amp/amp_news.php7?news_id=1938210
2021-03-15 09:02:00
```
-----
## Installation
Create a telegram group, apply for a telegram bot and save the `bot_token`, then get the `chat_id` with `getUpdates` API ([Telegram API Document](https://core.telegram.org/bots/api#getting-updates))  

Execute the command below in the project root to install required packages:
```
pip install -r requirements.txt
```

Update setting file with `bot_token` and `chat_id` (news_bots/settings.py):
```
# Telegram Bot Token
TG_TOKEN = ' '
TG_CHAT_ID = ' '
```

Execute the script:
```
cd news_bots
python main.py
```

-----------

## 專案說明:

為了方便爬取最新的新聞，使用Scrapy框架與Telegram Bot API整合，此專案以Udn, 中時及經濟日報為例，到各新聞網的＂財經＂相關新聞列表或RSS爬取新聞，以Jieba套件拆出關鍵字後，將整理好的訊息以Telegram Bot API發出至特定群組


### 以下為範例訊息
```
台股攻勢暫停！早盤小跌近30點 台積電、鴻海平盤震盪
{'#大立光', '#台積電', '#鴻海'}
https://finance.ettoday.net/amp/amp_news.php7?news_id=1938210
2021-03-15 09:02:00
```

------
## 安裝說明

先到telegram建立Group，找Bot father申請一個機器人，記下`bot_token`，用`getUpdates` API取得 `chat_id`， 可參考([Telegram API Document](https://core.telegram.org/bots/api#getting-updates))

先到專案下執行:
```
pip install -r requirements.txt
```

相依套件安裝後， 至`news_bots/settings.py` 將`bot_token`及`chat_id`填入:
```
# Telegram Bot Token
TG_TOKEN = ' '
TG_CHAT_ID = ' '
```

執行腳本:
```
cd news_bots
python main.py
```
