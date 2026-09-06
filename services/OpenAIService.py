import json
import re
from openai import OpenAI
from typing import Dict, List, Optional, Set

# 解析模型輸出的「名稱(附註)」格式，附註可能是正確代號，也可能是模型自行
# 加註的錯誤狀態文字（例如「未上市」）
_NAME_ANNOTATION_PATTERN = re.compile(r'^(.*?)\(([^()]*)\)$')


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

    def extract_finance_keywords(
        self, title: str, content: str, stock_code_map: Optional[Dict[str, str]] = None
    ) -> Set[str]:
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
                        name = self._correct_stock_name(name, stock_code_map)
                        keywords.add(f"#{name}")
            except json.JSONDecodeError:
                print(f"關鍵字提取失敗，OpenAI 回應非合法 JSON: {result}")

        return keywords

    @staticmethod
    def _correct_stock_name(name: str, stock_code_map: Optional[Dict[str, str]]) -> str:
        """用本地上市櫃對照表校正模型輸出的股票代號

        模型對代號沒把握時，偶爾會自行加註錯誤的狀態文字（例如把已上市
        公司誤標成「未上市」），而不是照規則只留公司簡稱。若本地對照表
        查得到正確代號就直接覆蓋；查不到、附註內容又含有中文字（判斷為
        模型自行加註的說明文字，不是真正的代號，例如美股代號一定是英文
        字母）時，則捨棄附註只留簡稱，避免顯示錯誤或無意義的狀態註記。
        """
        match = _NAME_ANNOTATION_PATTERN.match(name)
        if not match:
            return name

        base_name, annotation = match.group(1).strip(), match.group(2).strip()

        if stock_code_map and base_name in stock_code_map:
            return f"{base_name}({stock_code_map[base_name]})"

        if annotation and any('一' <= ch <= '鿿' for ch in annotation):
            return base_name

        return name
