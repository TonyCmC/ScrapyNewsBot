#Scrapy News Telegram bot (新聞關鍵字機器人)

### 專案說明:

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

先到telegram找Bot father申請一個機器人，記下Bot token，
記錄下使用的群組ID (chatId)

先到專案下執行
```pip install -r requirements.txt```
相依套件安裝後， 至`news_bots/settings.py` 將bot token及chat Id填入
```ini
# Telegram Bot Token
TG_TOKEN = ' '
TG_CHAT_ID = ' '
```

```
cd news_bots
python main.py
```
