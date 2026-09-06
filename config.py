import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot 設定
TG_TOKEN = os.getenv('TG_TOKEN')
TG_CHAT_ID = os.getenv('TG_CHAT_ID')

# OpenAI API 設定
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# 日誌設定
LOGS_DIR = os.getenv('LOGS_DIR', 'logs')

# 台股上市櫃公司「簡稱->代號」對照表，由排程每日同步一次（見 main.py）
STOCK_CODE_FILE = os.getenv('STOCK_CODE_FILE', 'data/stock_codes.json')
