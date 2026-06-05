#!/usr/bin/env python3
"""
GitHub Actions 自動化腳本
每週自動查詢 PubMed 並更新 papers.json
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

def load_config():
    """載入設定檔案"""
    config_path = Path('config.json')
    
    if not config_path.exists():
        print("❌ 錯誤：config.json 不存在")
        sys.exit(1)
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ config.json 格式錯誤: {e}")
        sys.exit(1)

def main():
    print("=" * 70)
    print("🚀 GitHub Actions 自動化：開始更新 papers.json")
    print("=" * 70)
    print(f"⏰ 執行時間: {datetime.now().isoformat()}")
    
    # 載入設定
    try:
        config = load_config()
    except SystemExit:
        return 1
    
    # 獲取郵箱
    email = os.environ.get('RESEARCHER_EMAIL', config.get('email'))
    if not email:
        print("❌ 錯誤：未設定郵箱地址")
        print("請在 GitHub Secrets 中新增 RESEARCHER_EMAIL")
        return 1
    
    print(f"📧 郵箱: {email}")
    
    # 獲取搜尋詞
    queries = config.get('search_queries', [])
    default_tags = config.get('default_tags', {})
    
    if not queries:
        print("⚠️  警告：config.json 中沒有搜尋詞")
        return 0
    
    print(f"🔍 搜尋詞數: {len(queries)}")
    
    # 動態導入模組
    try:
        print("\n📚 導入模組...")
        from pubmed_fetcher import PubMedFetcher
        from unpaywall_fetcher import OpenAccessAggregator
        from papers_json_manager import PapersJSONFormatter, PapersJSONManager
        print("✅ 模組導入成功")
    except ImportError as e:
        print(f"❌ 導入失敗: {e}")
        print("請確保以下文件在儲存庫根目錄:")
        print("  - pubmed_fetcher.py")
        print("  - unpaywall_fetcher.py")
        print("  - papers_json_manager.py")
        return 1
    
    try:
        # 初始化工具
        print("\n🔧 初始化工具...")
        fetcher = PubMedFetcher(email=email)
        aggregator = OpenAccessAggregator(email=email)
        manager = PapersJSONManager('papers.json')
        print("✅ 工具初始化完成")
        
        total_added = 0
        
        # 對每個搜尋詞進行查詢
        print(f"\n{'='*70}")
        print("開始查詢")
        print(f"{'='*70}")
        
        for i, query in enumerate(queries, 1):
            print(f"\n[{i}/{len(queries)}] 查詢: {query}")
            
            try:
                # 查詢 PubMed
                print("  [1/4] 查詢 PubMed...", end=" ", flush=True)
                papers = fetcher.search_and_fetch(query, max_results=30)
                print(f"✅ 找到 {len(papers)} 篇論文")
                
                if not papers:
                    print("  ⏭️  跳過此查詢")
                    continue
                
                # 檢查開放存取
                print(f"  [2/4] 檢查開放存取 ({len(papers)} 篇)...", end=" ", flush=True)
                oa_count = 0
                for j, paper in enumerate(papers):
                    enriched = aggregator.find_free_version(paper)
                    if enriched.get('oa_info', {}).get('is_oa'):
                        oa_count += 1
                print(f"✅ {oa_count} 篇開放存取")
                
                # 轉換格式
                print("  [3/4] 轉換為 papers.json 格式...", end=" ", flush=True)
                formatted = [
                    PapersJSONFormatter.convert_from_pubmed(p, **default_tags)
                    for p in papers
                ]
                print(f"✅ {len(formatted)} 篇")
                
                # 添加到資料庫
                print("  [4/4] 添加到資料庫...", end=" ", flush=True)
                added = manager.batch_add(formatted)
                total_added += added
                print(f"✅ 新增 {added} 篇")
            
            except Exception as e:
                print(f"\n  ❌ 此查詞出錯: {e}")
                continue
        
        # 保存更新
        print(f"\n{'='*70}")
        print("保存結果")
        print(f"{'='*70}")
        
        print("💾 保存 papers.json...", end=" ", flush=True)
        manager.save()
        print("✅ 完成")
        
        # 顯示統計
        stats = manager.get_statistics()
        print(f"\n📊 資料庫統計:")
        print(f"   └─ 總論文數: {stats['total']}")
        print(f"   └─ 本次新增: {total_added}")
        print(f"   └─ 開放存取: {stats['oa_papers']}")
        
        print(f"\n{'='*70}")
        print(f"✅ 自動化更新完成！")
        print(f"{'='*70}")
        
        return 0
    
    except Exception as e:
        print(f"\n{'='*70}")
        print(f"❌ 發生錯誤")
        print(f"{'='*70}")
        print(f"錯誤信息: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
