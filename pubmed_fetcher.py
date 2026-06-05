#!/usr/bin/env python3
"""
PubMed 文獻自動擷取工具
查詢指定關鍵詞，取得論文元數據，並準備 JSON 格式輸出
"""

import requests
import json
from datetime import datetime
from typing import List, Dict, Optional
import time

class PubMedFetcher:
    """PubMed API 查詢工具"""
    
    def __init__(self, email: str = "user@example.com"):
        """
        初始化 PubMed 查詢工具
        Args:
            email: 用於 PubMed API 請求的郵箱（NCBI 要求）
        """
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.email = email
        self.delay = 0.35  # NCBI 建議最少延遲
    
    def search(self, query: str, max_results: int = 100, 
               min_date: Optional[str] = None, 
               max_date: Optional[str] = None) -> List[str]:
        """
        在 PubMed 搜尋論文 PMID
        
        Args:
            query: 搜尋關鍵詞（如 "ureteral stent coating"）
            max_results: 最多返回結果數
            min_date: 最早發表日期 (YYYY/MM/DD)
            max_date: 最晚發表日期 (YYYY/MM/DD)
        
        Returns:
            PMID 列表
        """
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "rettype": "json",
            "tool": "literature_db",
            "email": self.email
        }
        
        if min_date:
            params["mindate"] = min_date
        if max_date:
            params["maxdate"] = max_date
        
        print(f"🔍 查詢 PubMed: {query}")
        
        try:
            response = requests.get(
                f"{self.base_url}/esearch.fcgi",
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            pmids = data.get("esearchresult", {}).get("idlist", [])
            print(f"✅ 找到 {len(pmids)} 篇論文")
            
            return pmids
        
        except requests.exceptions.RequestException as e:
            print(f"❌ 查詢失敗: {e}")
            return []
    
    def fetch_details(self, pmids: List[str]) -> List[Dict]:
        """
        批量獲取論文詳細資訊
        
        Args:
            pmids: PMID 列表
        
        Returns:
            論文元數據列表
        """
        if not pmids:
            return []
        
        # NCBI 建議分批請求（最多 200 個）
        papers = []
        batch_size = 100
        
        for i in range(0, len(pmids), batch_size):
            batch = pmids[i:i+batch_size]
            pmid_str = ",".join(batch)
            
            params = {
                "db": "pubmed",
                "id": pmid_str,
                "rettype": "json",
                "tool": "literature_db",
                "email": self.email
            }
            
            print(f"📥 擷取詳細資訊 ({i+1}-{min(i+batch_size, len(pmids))})")
            
            try:
                response = requests.get(
                    f"{self.base_url}/efetch.fcgi",
                    params=params
                )
                response.raise_for_status()
                
                data = response.json()
                articles = data.get("result", {}).get("uids", [])
                
                for pmid in articles:
                    if pmid == "uids":  # 跳過 uids 鍵
                        continue
                    
                    article_data = data.get("result", {}).get(pmid, {})
                    paper = self._parse_article(pmid, article_data)
                    if paper:
                        papers.append(paper)
                
                # NCBI 禮儀：請求之間延遲
                time.sleep(self.delay)
            
            except requests.exceptions.RequestException as e:
                print(f"⚠️  批次 {i//batch_size} 擷取失敗: {e}")
                continue
        
        print(f"✅ 成功解析 {len(papers)} 篇論文")
        return papers
    
    def _parse_article(self, pmid: str, article_data: Dict) -> Optional[Dict]:
        """
        解析單篇論文資訊
        
        Args:
            pmid: 論文 PMID
            article_data: NCBI API 返回的論文數據
        
        Returns:
            標準化的論文元數據字典
        """
        try:
            # 基本資訊
            title = article_data.get("title", "")
            abstract = article_data.get("abstract", "")
            
            # 日期
            pub_date = article_data.get("pubdate", "")
            year = pub_date.split()[0] if pub_date else ""
            
            # 作者
            authors = []
            for author in article_data.get("authors", []):
                name = author.get("name", "")
                if name:
                    authors.append(name)
            
            # DOI
            doi = ""
            for uid in article_data.get("uid", []):
                if uid.get("type") == "doi":
                    doi = uid.get("value", "")
                    break
            
            # 期刊
            journal = article_data.get("source", "")
            
            # 建構標準化數據
            paper = {
                "pmid": pmid,
                "doi": doi,
                "title": title,
                "authors": authors,
                "journal": journal,
                "year": year,
                "abstract": abstract,
                "pubdate": pub_date,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                "accessed_date": datetime.now().isoformat()
            }
            
            return paper
        
        except Exception as e:
            print(f"⚠️  無法解析 PMID {pmid}: {e}")
            return None
    
    def search_and_fetch(self, query: str, max_results: int = 50, **kwargs) -> List[Dict]:
        """
        一鍵查詢 + 擷取詳細資訊
        
        Args:
            query: 搜尋關鍵詞
            max_results: 最多結果數
            **kwargs: 傳遞給 search() 的其他參數
        
        Returns:
            論文元數據列表
        """
        pmids = self.search(query, max_results, **kwargs)
        papers = self.fetch_details(pmids)
        return papers


# ============ 使用示例 ============

if __name__ == "__main__":
    # 初始化工具
    fetcher = PubMedFetcher(email="your-email@example.com")
    
    # 查詢 ureteral stent coating 相關論文（近 5 年）
    papers = fetcher.search_and_fetch(
        query="ureteral stent hydrophilic coating",
        max_results=50,
        min_date="2020/01/01"
    )
    
    # 保存為 JSON
    with open("/home/claude/pubmed_results.json", "w", encoding="utf-8") as f:
        json.dump(papers, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 結果已保存到 pubmed_results.json")
    print(f"📊 統計: {len(papers)} 篇論文")
    
    # 顯示前 3 篇摘要
    print("\n📄 前 3 篇論文：")
    for i, paper in enumerate(papers[:3], 1):
        print(f"\n{i}. {paper['title']}")
        print(f"   作者: {', '.join(paper['authors'][:3])}")
        print(f"   年份: {paper['year']}")
        print(f"   DOI: {paper['doi']}")
