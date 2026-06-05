#!/usr/bin/env python3
"""
PDF 提取與動態網站爬蟲工具
提取論文全文、圖表、元數據；處理 JavaScript 渲染的頁面
"""

import os
import requests
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import tempfile

try:
    import pdfplumber
except ImportError:
    print("⚠️  pdfplumber 未安裝，PDF 提取功能可能受限")
    pdfplumber = None

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
except ImportError:
    print("⚠️  Selenium 未安裝，動態網站爬蟲功能受限")
    webdriver = None


class PDFExtractor:
    """PDF 文件提取工具"""
    
    @staticmethod
    def extract_text(pdf_path: str) -> Optional[str]:
        """
        從 PDF 提取全部文本
        
        Args:
            pdf_path: PDF 文件路徑
        
        Returns:
            提取的文本，或 None
        """
        if not pdfplumber:
            print("❌ pdfplumber 未安裝")
            return None
        
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
            
            return text
        
        except Exception as e:
            print(f"❌ PDF 提取失敗: {e}")
            return None
    
    @staticmethod
    def extract_tables(pdf_path: str) -> List[Dict]:
        """
        從 PDF 提取表格
        
        Args:
            pdf_path: PDF 文件路徑
        
        Returns:
            表格清單
        """
        if not pdfplumber:
            return []
        
        tables = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    page_tables = page.extract_tables()
                    for j, table in enumerate(page_tables or []):
                        tables.append({
                            "page": i + 1,
                            "table_index": j,
                            "data": table
                        })
        
        except Exception as e:
            print(f"⚠️  表格提取失敗: {e}")
        
        return tables
    
    @staticmethod
    def extract_metadata(pdf_path: str) -> Optional[Dict]:
        """
        從 PDF 提取元數據（標題、作者、建立日期等）
        
        Args:
            pdf_path: PDF 文件路徑
        
        Returns:
            元數據字典
        """
        if not pdfplumber:
            return None
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                metadata = pdf.metadata
                
                return {
                    "title": metadata.get("Title", ""),
                    "author": metadata.get("Author", ""),
                    "subject": metadata.get("Subject", ""),
                    "creator": metadata.get("Creator", ""),
                    "producer": metadata.get("Producer", ""),
                    "creation_date": metadata.get("CreationDate", ""),
                    "modification_date": metadata.get("ModDate", ""),
                    "pages": len(pdf.pages)
                }
        
        except Exception as e:
            print(f"⚠️  元數據提取失敗: {e}")
            return None
    
    @staticmethod
    def download_and_extract(url: str, output_dir: str = ".") -> Tuple[Optional[str], Optional[Dict]]:
        """
        下載 PDF 並提取內容
        
        Args:
            url: PDF URL
            output_dir: 保存目錄
        
        Returns:
            (提取的文本, 元數據)
        """
        try:
            # 下載 PDF
            response = requests.get(url, timeout=30, verify=False)
            response.raise_for_status()
            
            # 保存臨時文件
            pdf_filename = url.split("/")[-1] or "temp.pdf"
            pdf_path = os.path.join(output_dir, pdf_filename)
            
            with open(pdf_path, "wb") as f:
                f.write(response.content)
            
            print(f"✅ 下載成功: {pdf_filename}")
            
            # 提取內容
            text = PDFExtractor.extract_text(pdf_path)
            metadata = PDFExtractor.extract_metadata(pdf_path)
            
            return text, metadata
        
        except requests.exceptions.RequestException as e:
            print(f"❌ 下載失敗: {e}")
            return None, None


class DynamicWebScraper:
    """動態網站爬蟲工具（JavaScript 渲染）"""
    
    def __init__(self, headless: bool = True, timeout: int = 10):
        """
        初始化爬蟲
        
        Args:
            headless: 是否使用無頭模式
            timeout: 等待超時時間（秒）
        """
        self.headless = headless
        self.timeout = timeout
        self.driver = None
    
    def _init_driver(self):
        """初始化 Selenium WebDriver"""
        if not webdriver:
            raise ImportError("Selenium 未安裝")
        
        if self.driver:
            return
        
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        try:
            self.driver = webdriver.Chrome(options=options)
        except Exception as e:
            print(f"⚠️  無法啟動 Chrome，嘗試使用其他瀏覽器: {e}")
    
    def scrape_page(self, url: str, wait_selector: Optional[str] = None) -> Optional[str]:
        """
        爬蟲動態頁面
        
        Args:
            url: 頁面 URL
            wait_selector: 等待特定元素出現的 CSS 選擇器
        
        Returns:
            頁面 HTML 內容
        """
        try:
            self._init_driver()
            
            print(f"🌐 正在載入: {url}")
            self.driver.get(url)
            
            # 等待指定元素（可選）
            if wait_selector:
                WebDriverWait(self.driver, self.timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector))
                )
                print(f"✅ 元素已加載: {wait_selector}")
            
            # 返回渲染後的 HTML
            return self.driver.page_source
        
        except Exception as e:
            print(f"❌ 爬蟲失敗: {e}")
            return None
    
    def extract_elements(self, url: str, selector: str) -> List[str]:
        """
        提取特定 CSS 選擇器的元素
        
        Args:
            url: 頁面 URL
            selector: CSS 選擇器
        
        Returns:
            元素文本列表
        """
        try:
            self._init_driver()
            
            self.driver.get(url)
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            
            return [elem.text for elem in elements]
        
        except Exception as e:
            print(f"❌ 元素提取失敗: {e}")
            return []
    
    def close(self):
        """關閉瀏覽器"""
        if self.driver:
            self.driver.quit()
            self.driver = None


class JournalScraper:
    """期刊網站專用爬蟲"""
    
    @staticmethod
    def scrape_journal_toc(journal_url: str, year: Optional[int] = None) -> List[Dict]:
        """
        爬蟲期刊目錄（Table of Contents）
        
        Args:
            journal_url: 期刊主頁 URL
            year: 指定年份（可選）
        
        Returns:
            文章清單
        """
        # 這是一個框架，實際實現取決於期刊網站結構
        print(f"🔄 正在爬蟲期刊: {journal_url}")
        
        scraper = DynamicWebScraper()
        html = scraper.scrape_page(journal_url)
        scraper.close()
        
        # TODO: 根據具體期刊實現 HTML 解析
        return []
    
    @staticmethod
    def scrape_research_gate(author_url: str) -> List[Dict]:
        """
        從 ResearchGate 爬蟲作者論文清單
        
        Args:
            author_url: 作者 ResearchGate 主頁
        
        Returns:
            論文清單
        """
        print(f"🔄 正在爬蟲 ResearchGate: {author_url}")
        
        scraper = DynamicWebScraper()
        html = scraper.scrape_page(author_url)
        scraper.close()
        
        # TODO: 實現 ResearchGate HTML 解析
        return []


class FullTextAcquisition:
    """全文獲取聯合工具"""
    
    def __init__(self, email: str = "user@example.com"):
        self.email = email
        self.pdf_extractor = PDFExtractor()
    
    def acquire_fulltext(self, paper_doi: str, free_urls: List[str] = None) -> Optional[Dict]:
        """
        嘗試多個途徑獲取全文
        
        Args:
            paper_doi: 論文 DOI
            free_urls: 已知的免費 URL
        
        Returns:
            包含全文和元數據的字典
        """
        full_text = None
        source = None
        
        free_urls = free_urls or []
        
        # 優先嘗試已知的免費 URL
        for url in free_urls:
            print(f"📥 嘗試從 {url} 下載...")
            text, metadata = PDFExtractor.download_and_extract(url)
            
            if text:
                full_text = text
                source = url
                break
        
        # 如果還沒找到，嘗試其他來源
        if not full_text:
            # TODO: 嘗試其他來源（需要更多 API 整合）
            pass
        
        return {
            "doi": paper_doi,
            "full_text": full_text,
            "text_length": len(full_text) if full_text else 0,
            "source": source,
            "extracted_date": datetime.now().isoformat() if full_text else None
        } if full_text else None


# ============ 使用示例 ============

if __name__ == "__main__":
    from datetime import datetime
    
    # 範例 1：提取 PDF 文本
    print("=" * 60)
    print("範例 1: PDF 提取")
    print("=" * 60)
    
    # 下載示例 PDF（需要替換為真實 URL）
    sample_pdf_url = "https://example.com/sample.pdf"
    # text, metadata = PDFExtractor.download_and_extract(sample_pdf_url)
    # if text:
    #     print(f"✅ 提取了 {len(text)} 字符的文本")
    #     print(f"元數據: {metadata}")
    
    print("⏭️  跳過下載示例（需要真實 URL）")
    
    # 範例 2：動態網站爬蟲
    print("\n" + "=" * 60)
    print("範例 2: 動態網站爬蟲")
    print("=" * 60)
    
    # scraper = DynamicWebScraper()
    # html = scraper.scrape_page("https://www.example.com")
    # scraper.close()
    # if html:
    #     print(f"✅ 爬蟲成功，獲取 {len(html)} 字符的 HTML")
    
    print("⏭️  Selenium 爬蟲（需要 Chrome 和 Selenium 安裝）")
    
    print("\n✅ PDF 和爬蟲工具已準備好")
    print("💡 提示：")
    print("  1. 安裝依賴: pip install pdfplumber selenium")
    print("  2. 下載 ChromeDriver 用於 Selenium")
    print("  3. 使用 download_and_extract() 下載並提取 PDF")
    print("  4. 使用 DynamicWebScraper 爬蟲 JavaScript 渲染的頁面")
