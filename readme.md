# News Telegram Bot (新聞關鍵字機器人)

## Description
In order to receive the latest finance news, this project crawls the latest article from several Taiwanese news sites — UDN (經濟日報), ChinaTimes (中時電子報), ETtoday (ETtoday新聞雲), LTN (自由財經), Cnyes (鉅亨網), Yahoo Stock (Yahoo奇摩股市), TrendForce (集邦科技), and CTEE (工商時報, currently disabled) — via their RSS feeds, live news lists, or public JSON APIs. Each new article is summarized and has its related stock keywords extracted by OpenAI (`gpt-4o-mini`), then the result is sent to a Telegram group/channel via the Telegram Bot API. Crawling is scheduled with APScheduler, polling each source on its own interval.

> Note: this project previously used the Scrapy framework; it has since been refactored to a set of plain crawler classes (see `crawlers/`) scheduled by APScheduler. There is no Scrapy dependency anymore despite the repo name.

### Message Format
```
Title (as a link)

摘要：Summary

相關股票：#keyword1 #keyword2 ...

YYYY-mm-dd HH:MM:SS
```

### Example Message
```
台股攻勢暫停！早盤小跌近30點 台積電、鴻海平盤震盪

摘要：台股今日開高走低，早盤一度上漲後翻黑，台積電與鴻海股價維持平盤震盪...

相關股票：#台積電 #鴻海

2021-03-15 09:02:00
```
-----
## Installation

1. Create a Telegram group, apply for a Telegram bot via [@BotFather](https://t.me/BotFather) and note down the `bot_token`, then get the `chat_id` with the `getUpdates` API ([Telegram API Document](https://core.telegram.org/bots/api#getting-updates)).
2. Get an OpenAI API key (used for news summarization and stock keyword extraction).
3. Install required packages:
   ```
   pip install -r requirements.txt
   ```
4. Some crawlers (ChinaTimes, CTEE, LTN) render pages with JavaScript and use Selenium headless Chrome — make sure a local Chrome browser and a matching ChromeDriver are installed and available on `PATH`.
5. Copy `.env.example` to `.env` and fill in the values:
   ```
   TG_TOKEN=your_telegram_bot_token_here
   TG_CHAT_ID=your_chat_id_here
   OPENAI_API_KEY=your_openai_api_key_here
   LOGS_DIR=logs
   ```
6. Run the bot:
   ```
   python main.py
   ```
   This starts a blocking APScheduler loop that polls each news source on its own interval and pushes new articles to Telegram.

-----------

## 專案說明

為了方便接收最新的財經新聞，此專案會定期爬取聯合新聞網(UDN, 經濟日報)、中時電子報、ETtoday新聞雲、自由財經(LTN)、鉅亨網(Cnyes)、Yahoo奇摩股市、TrendForce(集邦科技)及工商時報(CTEE，目前停用)等新聞網站的最新一則財經新聞（來源包含 RSS、即時新聞列表頁，或網站前端使用的公開 JSON API），透過 OpenAI（`gpt-4o-mini`）產生摘要並萃取相關股票關鍵字，再以 Telegram Bot API 將整理好的訊息發送至指定的 Telegram 群組/頻道。排程由 APScheduler 負責，各新聞來源以各自的時間間隔輪詢。

> 註：本專案早期使用 Scrapy 框架，現已重構為一組獨立的爬蟲類別（見 `crawlers/`），改用 APScheduler 排程，目前已不再依賴 Scrapy。

### 以下為範例訊息
```
台股攻勢暫停！早盤小跌近30點 台積電、鴻海平盤震盪

摘要：台股今日開高走低，早盤一度上漲後翻黑，台積電與鴻海股價維持平盤震盪...

相關股票：#台積電 #鴻海

2021-03-15 09:02:00
```

------
## 安裝說明

1. 先到 Telegram 建立群組，透過 [@BotFather](https://t.me/BotFather) 申請一個機器人並記下 `bot_token`，再用 `getUpdates` API 取得 `chat_id`（可參考 [Telegram API Document](https://core.telegram.org/bots/api#getting-updates)）。
2. 準備一組 OpenAI API Key（用於新聞摘要與股票關鍵字萃取）。
3. 安裝相依套件：
   ```
   pip install -r requirements.txt
   ```
4. 部分爬蟲（中時電子報、工商時報、自由財經）需以 Selenium 無頭瀏覽器模式抓取頁面，請確認本機已安裝 Chrome 瀏覽器及對應版本的 ChromeDriver，並已加入 `PATH`。
5. 複製 `.env.example` 為 `.env` 並填入以下設定：
   ```
   TG_TOKEN=your_telegram_bot_token_here
   TG_CHAT_ID=your_chat_id_here
   OPENAI_API_KEY=your_openai_api_key_here
   LOGS_DIR=logs
   ```
6. 執行腳本：
   ```
   python main.py
   ```
   程式會啟動一個持續執行的 APScheduler 排程迴圈，依各新聞來源設定的間隔輪詢，並將新文章推送至 Telegram。
