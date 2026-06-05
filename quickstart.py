#!/usr/bin/env python3
"""
自動化文獻管理系統 - 快速啟動腳本
簡化版，適合快速開始和測試
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

def print_header(text):
    """列印美化的標題"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def print_section(text):
    """列印小標題"""
    print(f"\n→ {text}\n")

def menu_main():
    """主菜單"""
    print_header("自動化文獻管理系統")
    
    options = [
        "1. 快速開始教學",
        "2. 執行完整管道（PubMed → JSON）",
        "3. 僅查詢 PubMed",
        "4. 檢查開放存取狀態",
        "5. 管理 papers.json",
        "6. 設定 GitHub 自動化",
        "7. 顯示系統狀態",
        "0. 退出"
    ]
    
    for opt in options:
        print(f"  {opt}")
    
    return input("\n請選擇 (0-7): ").strip()

def tutorial_quick_start():
    """快速開始教學"""
    print_header("快速開始教學")
    
    print("""
這是一個 6 步系統，幫助你自動管理文獻：

【第 1 步】查詢 PubMed
  → 使用關鍵詞搜尋論文
  → 批量下載元數據（標題、作者、摘要等）
  
【第 2 步】檢查開放存取
  → 查詢論文是否有免費版本
  → Unpaywall + PubMed Central
  
【第 3 步】轉換格式
  → 標準化為 papers.json v2.0
  → 支援多維過濾（基材、固化方法等）
  
【第 4 步】提取全文（可選）
  → PDF 文本提取
  → 動態網站爬蟲
  
【第 5 步】自動化管道
  → 一鍵執行全部流程
  → 自動提交到 GitHub
  
【第 6 步】排程自動化
  → GitHub Actions
  → 每週自動更新

💡 快速開始：
  1. 打開 config.json，填入你的郵箱和 GitHub 路徑
  2. 執行「完整管道」選項
  3. papers.json 會自動更新並推送到 GitHub
    """)
    
    input("\n按 Enter 返回主菜單...")

def step_pubmed_fetch():
    """Step 1: PubMed 查詢"""
    print_header("第 1 步: 查詢 PubMed")
    
    # 載入設定
    config = load_config()
    email = config.get("email", "user@example.com")
    
    query = input("請輸入搜尋關鍵詞 (如 'ureteral stent coating'): ").strip()
    if not query:
        print("❌ 關鍵詞不能為空")
        return None
    
    min_date = input("最早發表日期 (YYYY/MM/DD，留空跳過): ").strip()
    max_results = input("最大結果數 (預設 50): ").strip()
    max_results = int(max_results) if max_results.isdigit() else 50
    
    print_section(f"正在查詢: {query}")
    
    try:
        from pubmed_fetcher import PubMedFetcher
        
        fetcher = PubMedFetcher(email=email)
        papers = fetcher.search_and_fetch(
            query=query,
            max_results=max_results,
            min_date=min_date if min_date else None
        )
        
        if papers:
            print(f"\n✅ 找到 {len(papers)} 篇論文")
            
            # 顯示前 3 篇
            print("\n前 3 篇論文:")
            for i, p in enumerate(papers[:3], 1):
                print(f"  {i}. {p.get('title', 'Unknown')}")
                print(f"     PMID: {p.get('pmid')} | 年份: {p.get('year')}")
            
            # 儲存結果
            output_file = f"pubmed_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(papers, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 結果已保存: {output_file}")
            return papers
        else:
            print("❌ 未找到相關論文")
            return None
    
    except ImportError:
        print("❌ 缺少依賴：pip install requests")
        return None
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
        return None

def step_check_oa():
    """Step 2: 檢查開放存取"""
    print_header("第 2 步: 檢查開放存取狀態")
    
    # 載入設定
    config = load_config()
    email = config.get("email", "user@example.com")
    
    # 載入上一步的結果
    results_file = input("輸入 PubMed 結果文件路徑 (如 'pubmed_results_*.json'): ").strip()
    
    if not os.path.exists(results_file):
        print(f"❌ 文件不存在: {results_file}")
        return None
    
    try:
        with open(results_file, "r", encoding="utf-8") as f:
            papers = json.load(f)
        
        print_section(f"正在檢查 {len(papers)} 篇論文的開放存取狀態...")
        
        from unpaywall_fetcher import OpenAccessAggregator
        
        aggregator = OpenAccessAggregator(email=email)
        
        oa_count = 0
        for i, paper in enumerate(papers, 1):
            enriched = aggregator.find_free_version(paper)
            if enriched["oa_info"]["is_oa"]:
                oa_count += 1
            
            if i % 10 == 0 or i == len(papers):
                print(f"  進度: {i}/{len(papers)} ({oa_count} 篇開放存取)")
        
        print(f"\n✅ 檢查完成")
        print(f"   開放存取: {oa_count}/{len(papers)} ({oa_count*100//len(papers)}%)")
        
        # 儲存增強版本
        output_file = f"papers_with_oa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(papers, f, ensure_ascii=False, indent=2)
        
        print(f"💾 增強版本已保存: {output_file}")
        return papers
    
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
        return None

def step_convert_format():
    """Step 3: 轉換格式"""
    print_header("第 3 步: 轉換為 papers.json v2.0")
    
    # 載入論文
    results_file = input("輸入論文數據文件路徑: ").strip()
    
    if not os.path.exists(results_file):
        print(f"❌ 文件不存在: {results_file}")
        return False
    
    try:
        with open(results_file, "r", encoding="utf-8") as f:
            papers = json.load(f)
        
        print_section("請輸入論文的分類標籤 (可留空)")
        
        tags = {}
        tag_options = {
            "substrate": ["Pellethane 2363 TPU", "Silicone", "PVC", "Other"],
            "cure_method": ["Air Plasma", "LED UV", "Thermal", "Chemical"],
            "application": ["Ureteral Stent (Double J)", "Ureteral Stent (Pigtail)", "Catheter", "Other"]
        }
        
        for key, options in tag_options.items():
            print(f"\n{key}:")
            for i, opt in enumerate(options, 1):
                print(f"  {i}. {opt}")
            
            choice = input("選擇 (留空跳過): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(options):
                tags[key] = options[int(choice)-1]
        
        print_section(f"正在轉換 {len(papers)} 篇論文...")
        
        from papers_json_manager import PapersJSONFormatter, PapersJSONManager
        
        # 轉換
        formatted_papers = [
            PapersJSONFormatter.convert_from_pubmed(p, **tags)
            for p in papers
        ]
        
        # 添加到 papers.json
        manager = PapersJSONManager("papers.json")
        added = manager.batch_add(formatted_papers)
        manager.save()
        
        print(f"\n✅ 轉換完成")
        print(f"   添加了 {added} 篇新論文到 papers.json")
        
        stats = manager.get_statistics()
        print(f"   資料庫總數: {stats['total']}")
        
        return True
    
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
        return False

def full_pipeline():
    """完整管道"""
    print_header("完整管道: PubMed → OA 檢查 → JSON 轉換")
    
    # Step 1
    papers = step_pubmed_fetch()
    if not papers:
        return
    
    # Step 2
    print("\n" + "="*60)
    proceed = input("是否檢查開放存取狀態? (y/n): ").lower()
    if proceed == 'y':
        # 先保存結果
        temp_file = "temp_papers.json"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(papers, f, ensure_ascii=False)
        
        # 檢查 OA
        config = load_config()
        email = config.get("email", "user@example.com")
        
        from unpaywall_fetcher import OpenAccessAggregator
        aggregator = OpenAccessAggregator(email=email)
        
        for i, paper in enumerate(papers, 1):
            aggregator.find_free_version(paper)
            if i % 10 == 0:
                print(f"  進度: {i}/{len(papers)}")
    
    # Step 3
    print("\n" + "="*60)
    proceed = input("是否轉換為 papers.json? (y/n): ").lower()
    if proceed == 'y':
        step_convert_format()

def view_database_status():
    """查看資料庫狀態"""
    print_header("資料庫狀態")
    
    try:
        from papers_json_manager import PapersJSONManager
        
        manager = PapersJSONManager("papers.json")
        stats = manager.get_statistics()
        
        print(f"""
📊 統計資訊:
  
  總論文數: {stats['total']}
  開放存取: {stats['oa_papers']}
  
  按年份分布:
""")
        for year in sorted(stats['by_year'].keys()):
            print(f"    {year}: {stats['by_year'][year]} 篇")
        
        print(f"\n  按基材分布:")
        for substrate, count in stats['by_substrate'].items():
            print(f"    {substrate}: {count} 篇")
        
        print(f"\n  按固化方法分布:")
        for method, count in stats['by_cure_method'].items():
            print(f"    {method}: {count} 篇")
        
    except FileNotFoundError:
        print("❌ papers.json 不存在")
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
    
    input("\n按 Enter 返回主菜單...")

def load_config():
    """載入設定文件"""
    if os.path.exists("config.json"):
        with open("config.json", "r") as f:
            return json.load(f)
    else:
        return {
            "email": "your-email@example.com",
            "github_repo_path": "/path/to/repo",
            "max_results_per_query": 50
        }

def setup_config():
    """設定設定文件"""
    print_header("初始設定")
    
    email = input("請輸入你的郵箱地址: ").strip()
    repo_path = input("請輸入 GitHub 儲存庫路徑: ").strip()
    
    config = {
        "email": email,
        "github_repo_path": repo_path,
        "max_results_per_query": 50,
        "search_queries": [
            "ureteral stent hydrophilic coating",
            "medical device biocompatibility"
        ]
    }
    
    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("✅ 設定已保存到 config.json")

def main():
    """主函數"""
    # 檢查設定
    if not os.path.exists("config.json"):
        print_header("首次使用，請進行初始設定")
        setup_config()
    
    while True:
        choice = menu_main()
        
        if choice == "0":
            print("\n👋 再見！")
            break
        elif choice == "1":
            tutorial_quick_start()
        elif choice == "2":
            full_pipeline()
        elif choice == "3":
            step_pubmed_fetch()
        elif choice == "4":
            step_check_oa()
        elif choice == "5":
            step_convert_format()
        elif choice == "6":
            print_section("GitHub Actions 設定")
            print("請參考 TUTORIAL.md 中的 'GitHub 整合' 部分")
            input("按 Enter 返回主菜單...")
        elif choice == "7":
            view_database_status()
        else:
            print("❌ 無效選擇，請重試")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 程式已中止")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()
