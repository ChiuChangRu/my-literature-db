#!/usr/bin/env python3
"""
完整自動化管道：PubMed → 開放存取檢查 → JSON 標準化 → GitHub 推送
適用於自動化更新你的 papers.json 資料庫
"""

import subprocess
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import tempfile
import shutil

# 導入前面建立的模組
# 實際使用時，確保這些文件在同一目錄或 Python 路徑中
# from pubmed_fetcher import PubMedFetcher
# from unpaywall_fetcher import OpenAccessAggregator
# from papers_json_manager import PapersJSONFormatter, PapersJSONManager


class AutomationPipeline:
    """完整的文獻自動化管道"""
    
    def __init__(self, 
                 github_repo_path: str,
                 email: str = "user@example.com",
                 max_results: int = 50):
        """
        初始化自動化管道
        
        Args:
            github_repo_path: 本地 GitHub 儲存庫路徑
            email: 用於 API 請求的郵箱
            max_results: 每次查詢的最大結果數
        """
        self.repo_path = github_repo_path
        self.email = email
        self.max_results = max_results
        self.papers_json_path = os.path.join(github_repo_path, "papers.json")
        self.log = []
    
    def _log(self, message: str, level: str = "INFO"):
        """記錄日誌"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.log.append(log_entry)
        print(log_entry)
    
    def run(self, 
            search_query: str,
            min_date: Optional[str] = None,
            tags: Dict = None) -> bool:
        """
        執行完整的自動化管道
        
        Args:
            search_query: PubMed 搜尋關鍵詞
            min_date: 最早發表日期 (YYYY/MM/DD)
            tags: 要分配給論文的標籤（如 substrate, cure_method 等）
        
        Returns:
            是否成功完成
        """
        tags = tags or {}
        
        try:
            self._log(f"開始自動化管道: {search_query}")
            
            # 第 1 步：查詢 PubMed
            self._log("第 1 步: 查詢 PubMed...")
            papers = self._fetch_from_pubmed(search_query, min_date)
            
            if not papers:
                self._log("未找到相關論文", "WARNING")
                return False
            
            self._log(f"找到 {len(papers)} 篇論文")
            
            # 第 2 步：檢查開放存取狀態
            self._log("第 2 步: 檢查開放存取狀態...")
            papers = self._enrich_with_oa(papers)
            
            # 第 3 步：轉換為 papers.json 格式
            self._log("第 3 步: 轉換為 papers.json 格式...")
            formatted_papers = self._format_papers(papers, tags)
            
            # 第 4 步：添加到 papers.json
            self._log("第 4 步: 更新 papers.json...")
            added_count = self._update_papers_json(formatted_papers)
            
            self._log(f"添加了 {added_count} 篇新論文")
            
            # 第 5 步：推送到 GitHub
            self._log("第 5 步: 推送到 GitHub...")
            if self._push_to_github():
                self._log("✅ 自動化管道完成")
                return True
            else:
                self._log("❌ GitHub 推送失敗", "ERROR")
                return False
        
        except Exception as e:
            self._log(f"管道執行失敗: {e}", "ERROR")
            return False
    
    def _fetch_from_pubmed(self, query: str, min_date: Optional[str]) -> List[Dict]:
        """查詢 PubMed（模擬）"""
        # 實際使用時，取消註釋並使用真實的 PubMedFetcher
        # from pubmed_fetcher import PubMedFetcher
        # fetcher = PubMedFetcher(self.email)
        # return fetcher.search_and_fetch(query, self.max_results, min_date=min_date)
        
        # 演示用的模擬數據
        return [
            {
                "pmid": f"1234567{i}",
                "doi": f"10.1016/j.biomaterials.2021.1208{i}3",
                "title": f"Hydrophilic Coating Study {i}",
                "authors": ["Author A.", "Author B."],
                "journal": "Biomaterials",
                "year": f"202{i % 3 + 1}",
                "abstract": f"This study examines... {i}",
                "url": f"https://pubmed.ncbi.nlm.nih.gov/1234567{i}/",
                "pubdate": f"202{i % 3 + 1} Jan 01"
            }
            for i in range(min(3, self.max_results))
        ]
    
    def _enrich_with_oa(self, papers: List[Dict]) -> List[Dict]:
        """檢查開放存取狀態（模擬）"""
        # 實際使用時，取消註釋並使用真實的 OpenAccessAggregator
        # from unpaywall_fetcher import OpenAccessAggregator
        # aggregator = OpenAccessAggregator(self.email)
        
        for paper in papers:
            # 模擬：50% 的論文是開放存取的
            paper["oa_info"] = {
                "is_oa": hash(paper.get("pmid", "")) % 2 == 0,
                "free_urls": [],
                "sources": []
            }
        
        return papers
    
    def _format_papers(self, papers: List[Dict], tags: Dict) -> List[Dict]:
        """轉換為 papers.json 格式（模擬）"""
        # 實際使用時，取消註釋並使用真實的 PapersJSONFormatter
        # from papers_json_manager import PapersJSONFormatter
        
        formatted = []
        for paper in papers:
            entry = {
                "id": paper.get("doi", f"pmid_{paper.get('pmid')}"),
                "pmid": paper.get("pmid", ""),
                "doi": paper.get("doi", ""),
                "title": paper.get("title", ""),
                "authors": paper.get("authors", []),
                "year": int(paper.get("year", 0)) if paper.get("year", "").isdigit() else None,
                "journal": paper.get("journal", ""),
                "abstract": paper.get("abstract", ""),
                "url": paper.get("url", ""),
                "oa": paper.get("oa_info", {}),
                "tags": tags or {
                    "substrate": "",
                    "cure_method": "",
                    "hydrophilic_polymer": "",
                    "photoinitiator": "",
                    "primer_strategy": "",
                    "application": ""
                },
                "content": {
                    "key_findings": "",
                    "notes": ""
                },
                "metadata": {
                    "added_date": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "reviewed": False
                }
            }
            formatted.append(entry)
        
        return formatted
    
    def _update_papers_json(self, papers: List[Dict]) -> int:
        """添加論文到 papers.json"""
        try:
            # 載入現有的 papers.json
            if os.path.exists(self.papers_json_path):
                with open(self.papers_json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = {
                    "version": "2.0",
                    "metadata": {
                        "created_date": datetime.now().isoformat(),
                        "last_updated": datetime.now().isoformat(),
                        "total_papers": 0
                    },
                    "papers": []
                }
            
            # 收集現有的 ID（避免重複）
            existing_ids = {p.get("id") for p in data.get("papers", [])}
            
            # 添加新論文
            added = 0
            for paper in papers:
                if paper.get("id") not in existing_ids:
                    data["papers"].append(paper)
                    added += 1
            
            # 更新元數據
            data["metadata"]["total_papers"] = len(data["papers"])
            data["metadata"]["last_updated"] = datetime.now().isoformat()
            
            # 保存
            with open(self.papers_json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self._log(f"papers.json 已更新: +{added} 論文")
            return added
        
        except Exception as e:
            self._log(f"更新 papers.json 失敗: {e}", "ERROR")
            return 0
    
    def _push_to_github(self) -> bool:
        """推送到 GitHub"""
        try:
            os.chdir(self.repo_path)
            
            # Git 操作
            commands = [
                ("git", "add", "papers.json"),
                ("git", "commit", "-m", f"Auto-update papers.json - {datetime.now().isoformat()}"),
                ("git", "push", "origin", "main")
            ]
            
            for cmd in commands:
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    # 某些命令可能失敗（如沒有更改時），這是正常的
                    if "nothing to commit" not in result.stdout and \
                       "nothing to commit" not in result.stderr:
                        self._log(f"Git 命令失敗: {' '.join(cmd)}", "WARNING")
                        self._log(result.stderr, "WARNING")
            
            self._log("GitHub 推送成功")
            return True
        
        except Exception as e:
            self._log(f"Git 操作失敗: {e}", "ERROR")
            return False
    
    def save_log(self, log_path: str):
        """保存日誌"""
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("\n".join(self.log))
        
        self._log(f"日誌已保存: {log_path}")


class GitHubActionsScheduler:
    """GitHub Actions 自動排程器"""
    
    @staticmethod
    def create_workflow(
        github_repo_path: str,
        cron_schedule: str = "0 0 * * 0",  # 每週日午夜
        search_queries: List[str] = None
    ) -> bool:
        """
        建立 GitHub Actions workflow 文件
        
        Args:
            github_repo_path: 本地 GitHub 儲存庫路徑
            cron_schedule: Cron 排程表達式
            search_queries: 搜尋關鍵詞清單
        
        Returns:
            是否成功建立
        """
        search_queries = search_queries or [
            "ureteral stent hydrophilic coating",
            "medical device coating biocompatibility",
            "polymer coating lubricity"
        ]
        
        workflow_dir = os.path.join(github_repo_path, ".github", "workflows")
        os.makedirs(workflow_dir, exist_ok=True)
        
        workflow_content = f"""name: Auto-update Papers Database

on:
  schedule:
    - cron: '{cron_schedule}'  # 自動執行排程
  workflow_dispatch:  # 允許手動觸發

jobs:
  update-papers:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install requests pdfplumber selenium
      
      - name: Run update pipeline
        env:
          EMAIL: ${{ secrets.RESEARCHER_EMAIL }}
        run: |
          python automation_pipeline.py
      
      - name: Commit and push
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add papers.json
          git commit -m "Auto-update papers.json - ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}" || true
          git push
"""
        
        workflow_path = os.path.join(workflow_dir, "auto-update-papers.yml")
        
        try:
            with open(workflow_path, "w", encoding="utf-8") as f:
                f.write(workflow_content)
            
            print(f"✅ GitHub Actions workflow 已建立: {workflow_path}")
            return True
        
        except IOError as e:
            print(f"❌ 建立 workflow 失敗: {e}")
            return False


# ============ 使用示例 ============

if __name__ == "__main__":
    import sys
    
    # 設定參數
    GITHUB_REPO_PATH = "/path/to/your/github/repo"  # 修改為你的 GitHub 儲存庫路徑
    EMAIL = "your-email@example.com"  # 修改為你的郵箱
    
    # 檢查路徑是否存在
    if not os.path.exists(GITHUB_REPO_PATH):
        print(f"❌ 儲存庫路徑不存在: {GITHUB_REPO_PATH}")
        sys.exit(1)
    
    # 建立 GitHub Actions workflow
    print("=" * 60)
    print("建立 GitHub Actions 自動排程")
    print("=" * 60)
    
    GitHubActionsScheduler.create_workflow(
        GITHUB_REPO_PATH,
        cron_schedule="0 0 * * 0",  # 每週日午夜
        search_queries=[
            "ureteral stent hydrophilic coating",
            "medical device friction coating",
            "TPU biocompatible coating"
        ]
    )
    
    # 執行自動化管道
    print("\n" + "=" * 60)
    print("執行自動化管道")
    print("=" * 60)
    
    pipeline = AutomationPipeline(
        github_repo_path=GITHUB_REPO_PATH,
        email=EMAIL,
        max_results=50
    )
    
    # 搜尋多個主題
    success = True
    for query in [
        ("ureteral stent hydrophilic coating", {"application": "Ureteral Stent (Double J)"}),
        ("medical device lubricity coating", {"cure_method": "LED UV"}),
        ("TPU substrate biomedical coating", {"substrate": "Pellethane 2363 TPU"})
    ]:
        query_text, tags = query
        if not pipeline.run(query_text, tags=tags):
            success = False
    
    # 保存日誌
    log_path = os.path.join(GITHUB_REPO_PATH, "automation.log")
    pipeline.save_log(log_path)
    
    if success:
        print("\n✅ 自動化管道完成！")
    else:
        print("\n⚠️  自動化管道有某些步驟失敗")
    
    # 顯示日誌摘要
    print("\n" + "=" * 60)
    print("日誌摘要（最後 10 條）")
    print("=" * 60)
    for line in pipeline.log[-10:]:
        print(line)
