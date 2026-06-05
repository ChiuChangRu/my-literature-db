#!/usr/bin/env python3
"""
papers.json 標準化與更新工具
將 PubMed 數據轉換為你的 papers.json v2.0 格式
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
import os

class PapersJSONFormatter:
    """papers.json v2.0 格式轉換器"""
    
    # v2.0 Schema 定義
    SCHEMA_VERSION = "2.0"
    
    # 標準化的分類清單
    SUBSTRATES = [
        "Pellethane 2363 TPU",
        "Silicone",
        "Polyurethane",
        "PVC",
        "Other"
    ]
    
    CURE_METHODS = [
        "Air Plasma",
        "LED UV",
        "Thermal",
        "Combination",
        "Chemical"
    ]
    
    HYDROPHILIC_POLYMERS = [
        "PVP (Polyvinyl Pyrrolidone)",
        "PEG (Polyethylene Glycol)",
        "MPC (2-Methacryloyloxyethyl Phosphorylcholine)",
        "SBMA (Sulfobetaine Methacrylate)",
        "Chitosan",
        "Hyaluronic Acid",
        "Other"
    ]
    
    PHOTOINITIATORS = [
        "Benzophenone",
        "2-Hydroxy-2-methylpropiophenone",
        "Camphorquinone",
        "None (Thermal/Chemical)"
    ]
    
    PRIMER_STRATEGIES = [
        "PDA (Polydopamine)",
        "Benzophenone",
        "PUA (Polyurethane Acrylate)",
        "Silane Coupling",
        "Isocyanate",
        "None"
    ]
    
    APPLICATIONS = [
        "Ureteral Stent (Double J)",
        "Ureteral Stent (Pigtail)",
        "Urinary Catheter",
        "Guidewire",
        "Puncture Needle",
        "Other Medical Device"
    ]
    
    @classmethod
    def create_paper_entry(
        cls,
        pmid: str = "",
        doi: str = "",
        title: str = "",
        authors: List[str] = None,
        year: str = "",
        journal: str = "",
        abstract: str = "",
        url: str = "",
        oa_info: Dict = None,
        # 可選的元標籤
        substrate: str = "",
        cure_method: str = "",
        hydrophilic_polymer: str = "",
        photoinitiator: str = "",
        primer_strategy: str = "",
        application: str = "",
        key_findings: str = "",
        notes: str = ""
    ) -> Dict:
        """
        建立符合 papers.json v2.0 的條目
        
        Args:
            pmid: PubMed ID
            doi: Digital Object Identifier
            title: 論文標題
            authors: 作者清單
            year: 發表年份
            journal: 期刊名稱
            abstract: 摘要
            url: 論文 URL
            oa_info: 開放存取資訊
            substrate: 基材類型
            cure_method: 固化方法
            hydrophilic_polymer: 親水高分子
            photoinitiator: 光引發劑
            primer_strategy: 底漆策略
            application: 應用領域
            key_findings: 關鍵發現
            notes: 筆記
        
        Returns:
            符合 v2.0 schema 的論文條目
        """
        authors = authors or []
        oa_info = oa_info or {}
        
        # 驗證並標準化分類
        validated_tags = {
            "substrate": cls._validate_category(substrate, cls.SUBSTRATES),
            "cure_method": cls._validate_category(cure_method, cls.CURE_METHODS),
            "hydrophilic_polymer": cls._validate_category(hydrophilic_polymer, cls.HYDROPHILIC_POLYMERS),
            "photoinitiator": cls._validate_category(photoinitiator, cls.PHOTOINITIATORS),
            "primer_strategy": cls._validate_category(primer_strategy, cls.PRIMER_STRATEGIES),
            "application": cls._validate_category(application, cls.APPLICATIONS)
        }
        
        entry = {
            # 基本元數據
            "id": doi or f"pmid_{pmid}",  # 優先用 DOI 作為 ID
            "pmid": pmid,
            "doi": doi,
            "title": title,
            "authors": authors,
            "year": int(year) if year and year.isdigit() else None,
            "journal": journal,
            "abstract": abstract,
            "url": url,
            
            # 開放存取資訊
            "oa": {
                "is_oa": oa_info.get("is_oa", False),
                "free_urls": oa_info.get("free_urls", []),
                "sources": oa_info.get("sources", [])
            },
            
            # 過濾標籤（用於多維過濾）
            "tags": {
                "substrate": validated_tags["substrate"],
                "cure_method": validated_tags["cure_method"],
                "hydrophilic_polymer": validated_tags["hydrophilic_polymer"],
                "photoinitiator": validated_tags["photoinitiator"],
                "primer_strategy": validated_tags["primer_strategy"],
                "application": validated_tags["application"]
            },
            
            # 研究內容
            "content": {
                "key_findings": key_findings,
                "notes": notes
            },
            
            # 元數據
            "metadata": {
                "added_date": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "reviewed": False  # 需要人工審查
            }
        }
        
        return entry
    
    @staticmethod
    def _validate_category(value: str, valid_options: List[str]) -> str:
        """
        驗證分類是否在允許的清單中
        
        Args:
            value: 要驗證的值
            valid_options: 允許的選項清單
        
        Returns:
            驗證後的值，或空字符串
        """
        if not value:
            return ""
        
        if value in valid_options:
            return value
        
        # 嘗試模糊匹配
        lower_value = value.lower()
        for option in valid_options:
            if lower_value in option.lower() or option.lower() in lower_value:
                return option
        
        print(f"⚠️  警告：'{value}' 不在標準分類中")
        return ""
    
    @classmethod
    def convert_from_pubmed(cls, pubmed_data: Dict, **tags) -> Dict:
        """
        將 PubMed 數據轉換為 papers.json v2.0 格式
        
        Args:
            pubmed_data: PubMed API 返回的數據
            **tags: 額外的分類標籤
        
        Returns:
            papers.json v2.0 格式的條目
        """
        return cls.create_paper_entry(
            pmid=pubmed_data.get("pmid", ""),
            doi=pubmed_data.get("doi", ""),
            title=pubmed_data.get("title", ""),
            authors=pubmed_data.get("authors", []),
            year=str(pubmed_data.get("year", "")),
            journal=pubmed_data.get("journal", ""),
            abstract=pubmed_data.get("abstract", ""),
            url=pubmed_data.get("url", ""),
            oa_info=pubmed_data.get("oa_info", {}),
            **tags
        )


class PapersJSONManager:
    """papers.json 文件管理器"""
    
    def __init__(self, file_path: str = "papers.json"):
        """
        初始化管理器
        
        Args:
            file_path: papers.json 的路徑
        """
        self.file_path = file_path
        self.data = self._load()
    
    def _load(self) -> Dict:
        """載入現有的 papers.json"""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"⚠️  {self.file_path} 格式錯誤，建立新檔案")
                return self._init_new()
        else:
            return self._init_new()
    
    def _init_new(self) -> Dict:
        """初始化新的 papers.json"""
        return {
            "version": "2.0",
            "metadata": {
                "created_date": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "total_papers": 0
            },
            "papers": []
        }
    
    def add_paper(self, paper: Dict, allow_duplicate: bool = False) -> bool:
        """
        添加論文條目
        
        Args:
            paper: papers.json v2.0 格式的條目
            allow_duplicate: 是否允許重複（根據 DOI/PMID 檢查）
        
        Returns:
            是否成功添加
        """
        # 檢查重複
        paper_id = paper.get("id", "")
        pmid = paper.get("pmid", "")
        
        if not allow_duplicate:
            for existing in self.data["papers"]:
                if (existing.get("id") == paper_id and paper_id) or \
                   (existing.get("pmid") == pmid and pmid):
                    print(f"⏭️  論文已存在: {paper.get('title', paper_id)}")
                    return False
        
        self.data["papers"].append(paper)
        self.data["metadata"]["total_papers"] = len(self.data["papers"])
        self.data["metadata"]["last_updated"] = datetime.now().isoformat()
        
        print(f"✅ 添加論文: {paper.get('title', paper_id)}")
        return True
    
    def batch_add(self, papers: List[Dict], allow_duplicate: bool = False) -> int:
        """
        批量添加論文
        
        Args:
            papers: 論文列表
            allow_duplicate: 是否允許重複
        
        Returns:
            成功添加的數量
        """
        count = 0
        for paper in papers:
            if self.add_paper(paper, allow_duplicate):
                count += 1
        
        return count
    
    def save(self) -> bool:
        """保存 papers.json"""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            print(f"💾 已保存到 {self.file_path}")
            return True
        except IOError as e:
            print(f"❌ 保存失敗: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """獲取統計資訊"""
        papers = self.data.get("papers", [])
        
        stats = {
            "total": len(papers),
            "by_year": {},
            "by_substrate": {},
            "by_cure_method": {},
            "by_application": {},
            "oa_papers": sum(1 for p in papers if p.get("oa", {}).get("is_oa", False))
        }
        
        for paper in papers:
            year = paper.get("year")
            if year:
                stats["by_year"][str(year)] = stats["by_year"].get(str(year), 0) + 1
            
            tags = paper.get("tags", {})
            for key in ["substrate", "cure_method", "application"]:
                value = tags.get(key, "")
                if value:
                    stats[f"by_{key}"][value] = stats[f"by_{key}"].get(value, 0) + 1
        
        return stats
    
    def export_filtered(self, filters: Dict) -> List[Dict]:
        """
        導出符合過濾條件的論文
        
        Args:
            filters: 過濾條件 (AND 邏輯跨維度, OR 邏輯在同維度)
                     如: {"substrate": ["Pellethane 2363 TPU"], "year": [2020, 2021]}
        
        Returns:
            符合條件的論文列表
        """
        results = []
        
        for paper in self.data.get("papers", []):
            match = True
            
            for filter_key, filter_values in filters.items():
                if not filter_values:
                    continue
                
                if filter_key == "year":
                    paper_year = paper.get("year")
                    if paper_year not in filter_values:
                        match = False
                        break
                else:
                    paper_value = paper.get("tags", {}).get(filter_key, "")
                    if paper_value not in filter_values:
                        match = False
                        break
            
            if match:
                results.append(paper)
        
        return results


# ============ 使用示例 ============

if __name__ == "__main__":
    # 初始化管理器
    manager = PapersJSONManager("papers.json")
    
    # 範例 1：添加單篇論文
    sample_paper = PapersJSONFormatter.create_paper_entry(
        pmid="12345678",
        doi="10.1016/j.biomaterials.2021.120853",
        title="Hydrophilic Coating Development for Ureteral Stents",
        authors=["Smith J.", "Johnson K.", "Lee M."],
        year="2021",
        journal="Biomaterials",
        abstract="This study demonstrates...",
        url="https://pubmed.ncbi.nlm.nih.gov/12345678/",
        substrate="Pellethane 2363 TPU",
        cure_method="LED UV",
        hydrophilic_polymer="PVP (Polyvinyl Pyrrolidone)",
        photoinitiator="Benzophenone",
        primer_strategy="PDA (Polydopamine)",
        application="Ureteral Stent (Double J)",
        key_findings="PVP coating achieved 80% reduction in friction coefficient",
        notes="Excellent biocompatibility results"
    )
    
    manager.add_paper(sample_paper)
    
    # 範例 2：批量添加（模擬來自 PubMed）
    sample_papers = [
        {
            "pmid": f"1234567{i}",
            "doi": f"10.1016/j.biomaterials.2021.1208{i}3",
            "title": f"Study {i}: Coating Research",
            "authors": ["Author A.", "Author B."],
            "year": f"202{i}",
            "journal": "Biomaterials",
            "abstract": f"Abstract {i}...",
            "url": f"https://pubmed.ncbi.nlm.nih.gov/1234567{i}/",
            "oa_info": {"is_oa": i % 2 == 0, "free_urls": [], "sources": []}
        }
        for i in range(5)
    ]
    
    converted_papers = [
        PapersJSONFormatter.convert_from_pubmed(
            p,
            substrate="Pellethane 2363 TPU",
            cure_method="Air Plasma" if i % 2 == 0 else "LED UV"
        )
        for i, p in enumerate(sample_papers)
    ]
    
    added = manager.batch_add(converted_papers)
    print(f"\n✅ 批量添加了 {added} 篇論文")
    
    # 保存
    manager.save()
    
    # 顯示統計
    stats = manager.get_statistics()
    print(f"\n📊 統計資訊:")
    print(f"  總論文數: {stats['total']}")
    print(f"  開放存取: {stats['oa_papers']}")
    print(f"  按年份: {stats['by_year']}")
    print(f"  按基材: {stats['by_substrate']}")
    
    # 過濾示例
    print("\n🔍 過濾示例：Pellethane TPU + LED UV")
    filtered = manager.export_filtered({
        "substrate": ["Pellethane 2363 TPU"],
        "cure_method": ["LED UV"]
    })
    print(f"找到 {len(filtered)} 篇相關論文")
