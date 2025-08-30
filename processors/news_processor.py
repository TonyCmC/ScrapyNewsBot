import json
import os
from typing import Dict
from services.OpenAIService import OpenAIService
from services.TelegramNotifier import TelegramNotifier
import config


class NewsProcessor:
    """新聞處理器 - 負責摘要、關鍵字提取、發送"""
    
    def __init__(self):
        self.telegram = TelegramNotifier(config.TG_TOKEN, config.TG_CHAT_ID)
        self.openai_service = OpenAIService(config.OPENAI_API_KEY)
        
        # 讀取股票清單
        with open(config.STOCK_JSON_PATH, 'r', encoding='utf-8') as f:
            self.stock_list = json.load(f)
    
    def process_news(self, news_item: Dict[str, str], crawler_name: str) -> bool:
        """
        處理新聞：檢查重複、摘要、關鍵字提取、發送
        返回 True 表示處理成功，False 表示跳過或失敗
        """
        if not news_item:
            print(f"{crawler_name}: 沒有抓到新聞")
            return False
        
        # 檢查是否已處理過
        if not self._check_previous_url(news_item):
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
            summary = self.openai_service.summarize_news(title, content)
            keywords = self.openai_service.extract_finance_keywords(title, content, self.stock_list)
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
    
    def _check_previous_url(self, news_item: Dict[str, str]) -> bool:
        """檢查是否為新的新聞（避免重複發送）"""
        maximum_items = 20
        file_path = os.path.join(config.LOGS_DIR, 'previous.log')
        
        # 確保目錄存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # 讀取歷史記錄
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                previous_items = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            previous_items = []
        
        # 檢查 URL 是否存在
        url_list = [item.get('url') for item in previous_items]
        if news_item.get('url') in url_list:
            return False
        
        # 新增到歷史記錄
        if len(previous_items) > maximum_items:
            previous_items.pop(0)
        previous_items.append(news_item)
        
        # 寫回檔案
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(previous_items, f, ensure_ascii=False, indent=2)
        
        return True