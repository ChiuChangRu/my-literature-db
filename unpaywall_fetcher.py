#!/usr/bin/env python3
"""
Unpaywall 開放存取論文查詢工具
自動查詢論文是否有免費的開放存取版本
"""

import requests
import json
from typing import Dict, Optional, List
import time

class UnpaywallFetcher:
    """Unpaywall 開放存取查詢工具"""
    
    def __init__(self, email: str = "user@example.com"):
        """
        初始化 Unpaywall 查詢工具
        Args:
            email: 用於 API 的郵箱（Unpaywall 要求）
        """
        self.base_url = "https://api.unpaywall.org/v2"
        self.email = email
        self.delay = 1  # Unpaywall 建議延遲
    
    def check_oa_status(self, doi: str) -> Optional[Dict]:
        """
        查詢論文的開放存取狀態
        
        Args:
            doi: 論文 DOI（格式如 "10.1038/nature12373"）
        
        Returns:
            包含開放存取狀態和免費 URL 的字典
        """
        if not doi:
            return None
        
        # 清理 DOI 格式
        doi = doi.lstrip("https://doi.org/").lstrip("http://doi.org/")
        
        params = {"email": self.email}
        
        try:
            response = requests.get(
                f"{self.base_url}/{doi}",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            # 解析結果
            result = {
                "doi": doi,
                "is_oa": data.get("is_oa", False),
                "oa_status": data.get("oa_status", "closed"),  # gold, green, hybrid, bronze, closed
                "free_urls": [],
                "publisher_url": data.get("publisher_copy_url", ""),
                "repository_urls": []
            }
            
            # 收集免費 URL
            if data.get("gold_oa"):
                gold = data.get("gold_oa", {})
                if gold.get("updated"):
                    result["free_urls"].append({
                        "type": "gold_oa",
                        "url": data.get("journal_is_in_doaj") and data.get("url", ""),
                        "source": "Publisher Gold OA"
                    })
            
            # Green OA (機構儲存庫)
            if data.get("green_oa"):
                result["oa_status"] = "green"
                repo_copy = data.get("best_oa_location", {})
                if repo_copy and repo_copy.get("url"):
                    result["repository_urls"].append({
                        "url": repo_copy.get("url"),
                        "host": repo_copy.get("host_type", "unknown"),
                        "version": repo_copy.get("version", "")
                    })
            
            # 混合 OA (Hybrid - 需要訂閱但有免費副本)
            if data.get("oa_status") == "hybrid":
                result["free_urls"].append({
                    "type": "hybrid_oa",
                    "url": data.get("journal_is_in_doaj") and data.get("url", ""),
                    "source": "Hybrid Journal"
                })
            
            time.sleep(self.delay)
            return result
        
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Unpaywall 查詢失敗 ({doi}): {e}")
            return None
    
    def batch_check(self, dois: List[str]) -> List[Dict]:
        """
        批量查詢多篇論文的開放存取狀態
        
        Args:
            dois: DOI 列表
        
        Returns:
            包含開放存取狀態的字典列表
        """
        results = []
        
        for i, doi in enumerate(dois, 1):
            if doi:
                print(f"🔍 查詢 Unpaywall ({i}/{len(dois)}): {doi}")
                result = self.check_oa_status(doi)
                if result:
                    results.append(result)
            else:
                print(f"⏭️  跳過空 DOI")
        
        return results


class PubMedCentral:
    """PubMed Central 查詢工具 - 另一個重要的開放存取資源"""
    
    @staticmethod
    def get_pmc_url(pmid: str) -> Optional[str]:
        """
        查詢論文是否在 PMC 上有免費版本
        
        Args:
            pmid: PubMed ID
        
        Returns:
            PMC URL 或 None
        """
        try:
            # PubMed 會自動重導到 PMC（如果可用）
            url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmid}/"
            response = requests.head(url, allow_redirects=True, timeout=5)
            
            if response.status_code == 200 and "pmc" in response.url:
                return f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmid}/"
            
            return None
        
        except requests.exceptions.RequestException:
            return None


class OpenAccessAggregator:
    """開放存取聚合工具 - 綜合查詢所有來源"""
    
    def __init__(self, email: str = "user@example.com"):
        self.unpaywall = UnpaywallFetcher(email)
        self.pmc = PubMedCentral()
    
    def find_free_version(self, paper: Dict) -> Dict:
        """
        為論文尋找所有可用的免費版本
        
        Args:
            paper: 論文元數據（包含 pmid, doi 等）
        
        Returns:
            增強版的論文數據，包含開放存取資訊
        """
        paper["oa_info"] = {
            "is_oa": False,
            "free_urls": [],
            "sources": []
        }
        
        # 優先查詢 PubMed Central
        pmid = paper.get("pmid", "")
        if pmid:
            pmc_url = self.pmc.get_pmc_url(pmid)
            if pmc_url:
                paper["oa_info"]["is_oa"] = True
                paper["oa_info"]["free_urls"].append(pmc_url)
                paper["oa_info"]["sources"].append("PubMed Central")
        
        # 然後查詢 Unpaywall（涵蓋 gold, green, hybrid OA）
        doi = paper.get("doi", "")
        if doi:
            oa_result = self.unpaywall.check_oa_status(doi)
            if oa_result and oa_result.get("is_oa"):
                paper["oa_info"]["is_oa"] = True
                
                if oa_result.get("free_urls"):
                    paper["oa_info"]["free_urls"].extend([
                        url.get("url") for url in oa_result.get("free_urls", [])
                    ])
                
                if oa_result.get("repository_urls"):
                    paper["oa_info"]["free_urls"].extend([
                        url.get("url") for url in oa_result.get("repository_urls", [])
                    ])
                
                paper["oa_info"]["sources"].append(oa_result.get("oa_status", "unknown"))
        
        # 備選：構造 Sci-Hub URL（⚠️ 注意：在某些地區可能違反法律）
        # paper["oa_info"]["scihub_url"] = f"https://sci-hub.st/{doi}" if doi else None
        
        return paper


# ============ 使用示例 ============

if __name__ == "__main__":
    # 模擬論文數據
    sample_papers = [
        {
            "pmid": "12345678",
            "doi": "10.1038/nature12373",
            "title": "Sample Paper 1"
        },
        {
            "pmid": "87654321",
            "doi": "10.1016/j.biomaterials.2021.120853",
            "title": "Sample Paper 2"
        }
    ]
    
    # 初始化聚合工具
    aggregator = OpenAccessAggregator(email="your-email@example.com")
    
    # 為每篇論文尋找免費版本
    print("🔍 尋找開放存取版本...\n")
    enriched_papers = []
    
    for paper in sample_papers:
        enriched = aggregator.find_free_version(paper)
        enriched_papers.append(enriched)
        
        print(f"📄 {paper['title']}")
        print(f"   開放存取: {'✅ 是' if enriched['oa_info']['is_oa'] else '❌ 否'}")
        print(f"   來源: {', '.join(enriched['oa_info']['sources']) if enriched['oa_info']['sources'] else '無'}")
        print(f"   免費 URL: {enriched['oa_info']['free_urls']}\n")
    
    # 保存結果
    with open("/home/claude/papers_with_oa.json", "w", encoding="utf-8") as f:
        json.dump(enriched_papers, f, ensure_ascii=False, indent=2)
    
    print("💾 結果已保存到 papers_with_oa.json")
