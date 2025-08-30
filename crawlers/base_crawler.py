from abc import ABC, abstractmethod
from typing import Dict, Optional
from contextlib import contextmanager
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random


class NewsCrawler(ABC):
    """新聞爬蟲抽象基礎類別"""
    
    # 10組不同的 User-Agent
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 OPR/108.0.0.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    
    def __init__(self, name: str):
        self.name = name
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': random.choice(self.USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    @abstractmethod
    def get_latest_news(self) -> Optional[Dict[str, str]]:
        """
        抓取最新一則新聞
        返回格式：{
            'url': str,
            'title': str, 
            'content': str,
            'published_at': str
        }
        """
        pass
    
    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """抓取網頁並解析為 BeautifulSoup 物件"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f"抓取 {url} 失敗: {e}")
            return None
    
    @contextmanager
    def browser_session(self):
        """瀏覽器 context manager"""
        driver = None
        try:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument("--ignore-certificate-errors")
            options.add_argument("--incognito")
            options.add_argument(f'--user-agent={random.choice(self.USER_AGENTS)}')
            
            driver = webdriver.Chrome(options=options)
            yield driver
            
        except Exception as e:
            print(f"啟動瀏覽器失敗: {e}")
            yield None
        finally:
            if driver:
                driver.quit()
    
    def fetch_page_with_browser(self, driver, url: str) -> Optional[BeautifulSoup]:
        """使用現有的瀏覽器實例抓取網頁"""
        try:
            driver.get(url)
            
            # 等待頁面載入
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            return BeautifulSoup(driver.page_source, 'html.parser')
            
        except Exception as e:
            print(f"使用瀏覽器抓取 {url} 失敗: {e}")
            return None