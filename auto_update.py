#!/usr/bin/env python3
import json, os, sys
from datetime import datetime

print("🚀 Auto-update started")
print(f"⏰ Time: {datetime.now()}")

try:
    config = json.load(open('config.json'))
    email = os.environ.get('RESEARCHER_EMAIL', config.get('email'))
    
    print(f"✅ Config loaded: {email}")
    print(f"✅ Queries: {len(config.get('search_queries', []))}")
    
    from pubmed_fetcher import PubMedFetcher
    from unpaywall_fetcher import OpenAccessAggregator
    from papers_json_manager import PapersJSONManager
    
    fetcher = PubMedFetcher(email=email)
    manager = PapersJSONManager('papers.json')
    
    for query in config.get('search_queries', [])[:1]:
        papers = fetcher.search_and_fetch(query, max_results=5)
        print(f"✅ Found {len(papers)} papers")
        manager.save()
    
    print("✅ Update completed!")
    sys.exit(0)
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
