from openai import OpenAI
from typing import List, Set


class OpenAIService:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def _make_request(self, messages: List[dict], max_tokens: int = 300) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.3,
                timeout=30
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"OpenAI API 請求失敗: {e}")
            return ""
    
    def summarize_news(self, title: str, content: str) -> str:
        messages = [
            {
                "role": "system", 
                "content": "你是一個新聞摘要助手。請用繁體中文將新聞內容摘要成 100 字左右，重點突出財經相關信息。"
            },
            {
                "role": "user", 
                "content": f"標題：{title}\n\n內容：{content}\n\n請摘要這則新聞："
            }
        ]
        return self._make_request(messages, max_tokens=150)
    
    def extract_finance_keywords(self, title: str, content: str) -> Set[str]:
        messages = [
            {
                "role": "system",
                "content": f"""你是一個財經關鍵字提取助手。從新聞中提取台灣或美國的上市櫃股票名稱或代號。
                ，每個名稱前加上 # 符號，用逗號分隔。如果沒有找到相關股票，請返回空字符串。"""
            },
            {
                "role": "user",
                "content": f"標題：{title}\n內容：{content}"
            }
        ]
        
        result = self._make_request(messages, max_tokens=100)
        
        keywords = set()
        if result:
            for keyword in result.split(','):
                keyword = keyword.strip()
                if keyword.startswith('#'):
                    keywords.add(keyword)
        
        return keywords