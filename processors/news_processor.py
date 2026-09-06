import json
import os
import threading
from typing import Dict, Optional
from services.OpenAIService import OpenAIService
from services.StockCodeService import StockCodeService
from services.TelegramNotifier import TelegramNotifier
import config


class NewsProcessor:
    """新聞處理器 - 負責摘要、關鍵字提取、發送"""

    # APScheduler 預設用 ThreadPoolExecutor 並行執行不同爬蟲的排程 job，
    # 多個爬蟲可能同時讀寫 previous.log，需要鎖避免互相覆蓋彼此的紀錄
    _log_lock = threading.Lock()

    def __init__(self, stock_code_service: Optional[StockCodeService] = None):
        self.telegram = TelegramNotifier(config.TG_TOKEN, config.TG_CHAT_ID)
        self.openai_service = OpenAIService(config.OPENAI_API_KEY)
        self.stock_code_service = stock_code_service
    
    def process_news(self, news_item: Dict[str, str], crawler_name: str) -> bool:
        """
        處理新聞：檢查重複、摘要、關鍵字提取、發送
        返回 True 表示處理成功，False 表示跳過或失敗
        """
        if not news_item:
            print(f"{crawler_name}: 沒有抓到新聞")
            return False
        
        # 檢查是否已處理過
        if not self._check_previous_url(news_item, crawler_name):
            print(f"{crawler_name}: 新聞已處理過，跳過")
            return False
        
        # 過濾特定作者
        if '謝金河' in news_item.get("title", ""):
            print(f"{crawler_name}: 跳過謝金河文章")
            return False
        
        # OpenAI 處理
        title = news_item.get("title")
        content = news_item.get("content")
        
        try:
            stock_code_map = self.stock_code_service.get_map() if self.stock_code_service else None
            summary = self.openai_service.summarize_news(title, content)
            keywords = self.openai_service.extract_finance_keywords(title, content, stock_code_map)
            keywords_str = ' '.join(sorted(keywords)) if keywords else ""
            
            # 組合訊息
            message_parts = [f"<a href='{news_item.get('url')}'>{title}</a>"]
            if summary:
                message_parts.append(f"摘要：{summary}")
            if keywords_str:
                message_parts.append(f"相關股票：{keywords_str}")
            message_parts.append(news_item.get("published_at"))
            
            # 發送 Telegram 訊息
            self.telegram.send_message("\n\n".join(message_parts))
            print(f"{crawler_name}: 新聞處理完成")
            return True
            
        except Exception as e:
            print(f"{crawler_name}: 處理新聞時發生錯誤: {e}")
            return False
    
    def _check_previous_url(self, news_item: Dict[str, str], crawler_name: str) -> bool:
        """檢查是否為新的新聞（避免重複發送）

        紀錄格式為 {crawler_name: [url, ...]}，每個來源各自獨立維護最近
        maximum_items 筆歷史，避免來源一多，彼此的紀錄互相擠掉導致誤判成
        新文章而重複發送。讀寫過程用 lock 包起來，避免 APScheduler 並行
        執行多個爬蟲 job 時互相覆蓋彼此寫入的結果。
        """
        maximum_items = 20
        file_path = os.path.join(config.LOGS_DIR, 'previous.log')
        url = news_item.get('url')

        with self._log_lock:
            # 確保目錄存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # 讀取歷史記錄
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    previous_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                previous_data = {}

            # 相容舊版格式（單一扁平 list，所有來源共用）：偵測到就視為過期紀錄重新開始
            if not isinstance(previous_data, dict):
                previous_data = {}

            source_urls = previous_data.get(crawler_name, [])

            # 檢查 URL 是否存在
            if url in source_urls:
                return False

            # 新增到該來源的歷史記錄
            source_urls.append(url)
            if len(source_urls) > maximum_items:
                source_urls.pop(0)
            previous_data[crawler_name] = source_urls

            # 寫回檔案
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(previous_data, f, ensure_ascii=False, indent=2)

            return True