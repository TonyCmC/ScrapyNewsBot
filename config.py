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
