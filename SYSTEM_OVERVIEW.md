# 自動化文獻管理系統 - 完整檔案清單

## 📁 檔案結構

```
my-literature-db/
├── README.md                          # 你的專案說明
├── papers.json                        # 核心：標準化文獻資料庫 (v2.0)
├── config.json                        # 設定檔案
│
├── 🔧 核心工具模組
│   ├── pubmed_fetcher.py             # PubMed API 查詢工具
│   ├── unpaywall_fetcher.py          # 開放存取檢查工具
│   ├── papers_json_manager.py        # JSON 格式管理工具
│   ├── scraper_tools.py              # PDF 和爬蟲工具
│   └── automation_pipeline.py        # 完整自動化管道
│
├── 🚀 快速入門
│   ├── quickstart.py                 # 互動式選單（推薦新手使用）
│   ├── TUTORIAL.md                   # 完整教學文件
│   └── README.md                     # 說明文件
│
├── 📊 GitHub 自動化
│   └── .github/workflows/
│       └── auto-update-papers.yml    # GitHub Actions 排程腳本
│
└── 📦 備份和日誌
    ├── automation.log                # 自動化執行日誌
    ├── pubmed_results_*.json         # 臨時查詢結果
    └── backups/                      # 論文資料庫備份
```

---

## 🎯 各工具的用途速查表

| 工具 | 檔案 | 主要功能 | 使用場景 |
|------|------|--------|--------|
| **PubMed 查詢** | `pubmed_fetcher.py` | 搜尋論文、批量下載元數據 | 補充新論文 |
| **開放存取檢查** | `unpaywall_fetcher.py` | 查詢免費版本 URL | 找免費文獻 |
| **格式轉換** | `papers_json_manager.py` | 標準化、過濾、統計 | 維護資料庫 |
| **全文提取** | `scraper_tools.py` | PDF 解析、網站爬蟲 | 高階應用 |
| **自動化管道** | `automation_pipeline.py` | 一鍵執行所有步驟 | 生產環境 |
| **快速菜單** | `quickstart.py` | 互動式 UI | 快速開始 |

---

## 🚀 開始使用（選擇你的路徑）

### 路徑 1️⃣：新手 - 互動式菜單（推薦）

```bash
python quickstart.py
```

**流程：**
1. 首次運行會提示設定郵箱和 GitHub 路徑
2. 在主菜單中選擇：
   - 「1. 快速開始教學」- 了解系統
   - 「2. 執行完整管道」- 一鍵從 PubMed 到 GitHub
   - 「3-5」- 逐步執行各功能

### 路徑 2️⃣：中級 - 腳本式使用

```python
# 方法 A: 分步執行
from pubmed_fetcher import PubMedFetcher
from unpaywall_fetcher import OpenAccessAggregator
from papers_json_manager import PapersJSONManager, PapersJSONFormatter

# 1. 查詢
fetcher = PubMedFetcher(email="your-email@example.com")
papers = fetcher.search_and_fetch("ureteral stent coating", max_results=50)

# 2. 檢查 OA
aggregator = OpenAccessAggregator(email="your-email@example.com")
for paper in papers:
    aggregator.find_free_version(paper)

# 3. 轉換格式
formatted = [
    PapersJSONFormatter.convert_from_pubmed(
        p,
        substrate="Pellethane 2363 TPU",
        cure_method="LED UV"
    )
    for p in papers
]

# 4. 儲存
manager = PapersJSONManager("papers.json")
manager.batch_add(formatted)
manager.save()
```

### 路徑 3️⃣：高級 - 完整自動化管道

```python
# 方法 B: 一鍵執行
from automation_pipeline import AutomationPipeline

pipeline = AutomationPipeline(
    github_repo_path="/path/to/Pigtail",
    email="your-email@example.com"
)

pipeline.run(
    search_query="ureteral stent coating",
    min_date="2020/01/01",
    tags={"substrate": "Pellethane 2363 TPU"}
)

# papers.json 自動更新並推送到 GitHub
```

### 路徑 4️⃣：專家 - GitHub Actions 自動排程

```bash
# 建立 GitHub Actions workflow（每週自動運行）
python -c "
from automation_pipeline import GitHubActionsScheduler
GitHubActionsScheduler.create_workflow(
    '/path/to/repo',
    cron_schedule='0 0 * * 0'  # 每週日午夜
)
"

# 推送到 GitHub
git add .github/workflows/
git commit -m 'Add automatic update workflow'
git push
```

---

## 💡 實務工作流

### 場景 1: 補充新論文（每月一次）

```bash
# 步驟 1: 運行快速菜單
python quickstart.py

# 步驟 2: 選擇「2. 執行完整管道」
# 步驟 3: 輸入新的搜尋關鍵詞
# → papers.json 自動更新
# → 自動推送到 GitHub
```

### 場景 2: 精細化管理（研究階段）

```python
# 只查詢特定期間的論文
papers = fetcher.search_and_fetch(
    "ureteral stent coating",
    min_date="2023/01/01",
    max_date="2024/12/31"
)

# 只提取開放存取論文
oa_papers = [p for p in papers if p.get("oa_info", {}).get("is_oa")]

# 按特定標籤分類
filtered = manager.export_filtered({
    "substrate": ["Pellethane 2363 TPU"],
    "cure_method": ["LED UV"],
    "year": [2023, 2024]
})
```

### 場景 3: 自動維護（生產環境）

```bash
# 只需設定一次 GitHub Actions
# 之後每週自動執行：
# 1. PubMed 查詢
# 2. OA 檢查
# 3. JSON 更新
# 4. GitHub 推送

# 監控日誌（可選）
git log papers.json  # 查看更新歷史
```

---

## 📊 關鍵概念

### papers.json v2.0 Schema

```json
{
  "version": "2.0",
  "metadata": {
    "created_date": "2024-01-01T00:00:00",
    "last_updated": "2024-12-15T12:34:56",
    "total_papers": 50
  },
  "papers": [
    {
      "id": "10.1016/j.biomaterials.2021.1208533",
      "pmid": "12345678",
      "doi": "10.1016/j.biomaterials.2021.1208533",
      "title": "Hydrophilic Coating Development...",
      "authors": ["Smith J.", "Johnson K."],
      "year": 2021,
      "journal": "Biomaterials",
      "abstract": "...",
      "url": "https://pubmed.ncbi.nlm.nih.gov/12345678/",
      
      "oa": {
        "is_oa": true,
        "free_urls": ["https://..."],
        "sources": ["PubMed Central"]
      },
      
      "tags": {
        "substrate": "Pellethane 2363 TPU",
        "cure_method": "LED UV",
        "hydrophilic_polymer": "PVP",
        "photoinitiator": "Benzophenone",
        "primer_strategy": "PDA",
        "application": "Ureteral Stent (Double J)"
      },
      
      "content": {
        "key_findings": "PVP coating achieved 80% friction reduction",
        "notes": "Excellent biocompatibility"
      },
      
      "metadata": {
        "added_date": "2024-01-15T10:30:00",
        "last_updated": "2024-01-15T10:30:00",
        "reviewed": false
      }
    }
  ]
}
```

### 多維過濾示例

```python
# 搜尋：Pellethane + LED UV + 2020-2023
results = manager.export_filtered({
    "substrate": ["Pellethane 2363 TPU"],
    "cure_method": ["LED UV"],
    "year": [2020, 2021, 2022, 2023]
})

# 搜尋：所有 PVP 相關的論文
results = manager.export_filtered({
    "hydrophilic_polymer": ["PVP (Polyvinyl Pyrrolidone)"]
})

# 搜尋：雙 J 導管 OR Pigtail 導管 的論文
results = manager.export_filtered({
    "application": ["Ureteral Stent (Double J)", "Ureteral Stent (Pigtail)"]
})
```

---

## 🔧 安裝依賴

```bash
# 基礎（推薦）
pip install requests

# 完整功能
pip install requests pdfplumber selenium

# 可視化（可選）
pip install matplotlib pandas
```

---

## ⚡ 快速命令參考

```bash
# 查詢 PubMed
python -c "from pubmed_fetcher import PubMedFetcher; \
           f = PubMedFetcher('email@example.com'); \
           papers = f.search_and_fetch('query', max_results=100); \
           print(f'找到 {len(papers)} 篇論文')"

# 檢查 papers.json 統計
python -c "from papers_json_manager import PapersJSONManager; \
           m = PapersJSONManager('papers.json'); \
           stats = m.get_statistics(); \
           print(f\"總數: {stats['total']}, OA: {stats['oa_papers']}\")"

# 備份 papers.json
cp papers.json "backups/papers_$(date +%Y%m%d_%H%M%S).json"

# 檢查 Git 變更
git diff papers.json | head -50

# 推送到 GitHub
git add papers.json && git commit -m "Update papers" && git push
```

---

## 📚 進階主題

### 自訂分類標籤

編輯 `papers_json_manager.py` 中的 `PapersJSONFormatter` 類：

```python
CUSTOM_MATERIALS = [
    "Pellethane 2363 TPU",
    "Your New Material"  # 添加
]

CUSTOM_METHODS = [
    "Air Plasma",
    "Your Method"  # 添加
]
```

### 連接到你的 GitHub Pages

在 `index.html` 中加載並渲染 `papers.json`：

```javascript
// 動態過濾界面
fetch('papers.json')
  .then(r => r.json())
  .then(data => {
    // 建立多維過濾 UI
    // 呈現論文清單
  })
```

### 與其他工具整合

```python
# 導出為 BibTeX
def export_bibtex(papers):
    for p in papers:
        print(f"""@article{{{p['doi']},
    title={{{p['title']}}},
    author={{{'; '.join(p['authors'])}}},
    journal={{{p['journal']}}},
    year={{{p['year']}}}
}}""")

# 導出為 CSV
import csv
with open('papers.csv', 'w') as f:
    writer = csv.DictWriter(f, fieldnames=['title', 'authors', 'year', 'journal'])
    writer.writerows(papers)
```

---

## 🐛 故障排查

| 問題 | 解決方案 |
|------|--------|
| PubMed 查詢無結果 | ✓ 檢查拼寫 ✓ 嘗試更寬泛的關鍵詞 ✓ 檢查網路 |
| Unpaywall 很慢 | ✓ 正常現象（API 限速）✓ 大批量分批進行 |
| GitHub 推送失敗 | ✓ 檢查 SSH key ✓ 設定 git user.email/name |
| PDF 提取失敗 | ✓ 安裝 pdfplumber ✓ 某些 PDF 可能不可讀 |
| papers.json 衝突 | ✓ `git pull` 先 ✓ 手動合併 ✓ 使用 `git merge` 工具 |

---

## 📈 下一步

- [ ] 完成首次 PubMed 查詢
- [ ] 檢查開放存取狀態
- [ ] 轉換為 papers.json
- [ ] 設定 GitHub 自動化
- [ ] 檢查 GitHub Pages 展示效果
- [ ] 定期備份
- [ ] 分享你的資料庫！

---

## 💬 反饋和改進

有問題或建議？

1. 檢查 `TUTORIAL.md` 的常見問題部分
2. 查看各模組的代碼註釋
3. 用 `--help` 或 `-h` 查看命令說明
4. 在 GitHub 上提 Issue

---

**祝你的文獻研究順利！** 🎓
