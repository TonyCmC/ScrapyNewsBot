import json
import os
from typing import Dict

import requests

# 證交所（上市）與櫃買中心（上櫃）的公開資料 API，回傳全部上市櫃公司基本資料
TWSE_URL = "https://openapi.twse.com.tw/v1/opendata/t187ap03_L"
TPEX_URL = "https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap03_O"


class StockCodeService:
    """維護「公司簡稱 -> 股票代號」對照表

    資料來源為證交所、櫃買中心的公開資料 API，由排程每日同步一次寫入
    本地檔案。OpenAI 在辨識新聞提及的股票時，偶爾會對代號沒把握而自行
    加註錯誤的狀態文字（例如把已上市公司誤標成「未上市」），這份本地
    對照表可用來校正，避免依賴模型記憶。
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        self._map: Dict[str, str] = {}
        self._load()

    def sync(self) -> bool:
        """向證交所、櫃買中心抓取最新上市櫃公司清單並寫入本地檔案"""
        try:
            mapping: Dict[str, str] = {}

            twse_resp = requests.get(TWSE_URL, timeout=30)
            twse_resp.raise_for_status()
            for item in twse_resp.json():
                name = (item.get("公司簡稱") or "").strip()
                code = (item.get("公司代號") or "").strip()
                if name and code:
                    mapping[name] = code

            tpex_resp = requests.get(TPEX_URL, timeout=30)
            tpex_resp.raise_for_status()
            for item in tpex_resp.json():
                name = (item.get("CompanyAbbreviation") or "").strip()
                code = (item.get("SecuritiesCompanyCode") or "").strip()
                if name and code:
                    mapping[name] = code

            if not mapping:
                print("StockCodeService: 同步結果為空，放棄寫入以保留舊資料")
                return False

            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(mapping, f, ensure_ascii=False, indent=2)

            self._map = mapping
            print(f"StockCodeService: 同步完成，共 {len(mapping)} 檔上市櫃公司")
            return True

        except Exception as e:
            print(f"StockCodeService: 同步失敗，沿用舊資料: {e}")
            return False

    def _load(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self._map = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._map = {}

    def get_map(self) -> Dict[str, str]:
        """回傳目前記憶體中的「簡稱 -> 代號」對照表（同步失敗時為上次成功結果）"""
        return self._map
