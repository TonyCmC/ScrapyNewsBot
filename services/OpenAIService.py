import json
from openai import OpenAI
from typing import List, Set


class OpenAIService:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def _make_request(self, messages: List[dict], max_tokens: int = 300, json_mode: bool = False) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.3,
                timeout=30,
                response_format={"type": "json_object"} if json_mode else None
            )

            choice = response.choices[0]
            if choice.finish_reason == "length":
                print(f"OpenAI API 警告: 回應被 max_tokens ({max_tokens}) 截斷")

            return choice.message.content.strip()

        except Exception as e:
            print(f"OpenAI API 請求失敗: {e}")
            return ""

    def summarize_news(self, title: str, content: str) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "你是一個新聞摘要助手。請用繁體中文將新聞內容摘要成完整的一段話，"
                    "字數嚴格控制在 100 字以內（含標點），絕對不能寫到一半被截斷或漏掉結尾，"
                    "重點聚焦財經相關資訊。只輸出摘要本身，不要加上「摘要：」等前綴。"
                )
            },
            {
                "role": "user",
                "content": f"標題：{title}\n\n內容：{content}\n\n請摘要這則新聞："
            }
        ]
        # 100 個中文字約需 150~200 tokens，保留緩衝空間避免被硬性截斷
        return self._make_request(messages, max_tokens=300)

    def extract_finance_keywords(self, title: str, content: str) -> Set[str]:
        messages = [
            {
                "role": "system",
                "content": (
                    "你是一個財經關鍵字提取助手。請從新聞中找出提及的台灣或美國上市櫃公司。\n"
                    "輸出規則：\n"
                    "1. 只回傳 JSON 物件，格式為 {\"stocks\": [\"名稱1\", \"名稱2\"]}，不要有其他文字。\n"
                    "2. 每個項目一律使用「公司簡稱(代號)」格式，例如台股用「台積電(2330)」，"
                    "美股用「Apple(AAPL)」。\n"
                    "3. 若確定該公司但找不到代號，只寫公司簡稱即可，不要自行編造代號。\n"
                    "4. 找不到任何相關股票時，回傳 {\"stocks\": []}。"
                )
            },
            {
                "role": "user",
                "content": f"標題：{title}\n內容：{content}"
            }
        ]

        result = self._make_request(messages, max_tokens=150, json_mode=True)

        keywords = set()
        if result:
            try:
                data = json.loads(result)
                for name in data.get("stocks", []):
                    name = name.strip()
                    if name:
                        keywords.add(f"#{name}")
            except json.JSONDecodeError:
                print(f"關鍵字提取失敗，OpenAI 回應非合法 JSON: {result}")

        return keywords
