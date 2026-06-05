# 自動化文獻管理系統 - 完整教學指南

## 📖 目錄
1. [系統概覽](#系統概覽)
2. [安裝和設定](#安裝和設定)
3. [逐步使用教學](#逐步使用教學)
4. [進階功能](#進階功能)
5. [GitHub 整合](#github-整合)
6. [常見問題](#常見問題)

---

## 系統概覽

### 架構圖

```
┌─────────────────┐
│  PubMed API     │ ← 查詢論文元數據
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│ 1. pubmed_fetcher.py        │ ← 批量下載論文基本資訊
│    (查詢 + 詳細資訊提取)     │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ 2. unpaywall_fetcher.py     │ ← 檢查開放存取版本
│    (OA 狀態 + 免費 URL)      │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ 3. papers_json_manager.py   │ ← 格式標準化
│    (轉換為 papers.json v2.0) │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ 4. scraper_tools.py         │ ← 可選：提取全文
│    (PDF 提取 + 動態爬蟲)    │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ 5. automation_pipeline.py   │ ← 全自動流程控制
│    (一鍵執行 + GitHub 推送)  │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────┐
│ papers.json     │
│ (GitHub 儲存)   │
└─────────────────┘
```

### 核心特性

| 功能 | 說明 | 自動化程度 |
|------|------|----------|
| **PubMed 查詢** | 關鍵詞搜尋 + 批量元數據提取 | ⭐⭐⭐⭐⭐ |
| **開放存取檢查** | Unpaywall + PMC 整合 | ⭐⭐⭐⭐⭐ |
| **JSON 標準化** | v2.0 schema + 分類過濾 | ⭐⭐⭐⭐⭐ |
| **全文提取** | PDF + 動態網站爬蟲 | ⭐⭐⭐ |
| **GitHub 同步** | 自動提交 + 推送 | ⭐⭐⭐⭐⭐ |
| **排程自動化** | GitHub Actions | ⭐⭐⭐⭐⭐ |

---

## 安裝和設定

### 先決條件

- Python 3.8+
- Git
- GitHub 帳號（用於儲存庫）

### 步驟 1：克隆或初始化你的 GitHub 儲存庫

```bash
# 如果已有儲存庫
git clone https://github.com/ChiuChangru/Pigtail.git
cd Pigtail

# 如果要新建儲存庫
mkdir my-literature-db
cd my-literature-db
git init
git remote add origin https://github.com/YOUR_USERNAME/my-literature-db.git
```

### 步驟 2：安裝 Python 依賴

```bash
# 基礎依賴（推薦）
pip install requests

# 完整功能（包含 PDF 提取和爬蟲）
pip install requests pdfplumber selenium

# 如果使用動態爬蟲，還需下載 ChromeDriver
# https://chromedriver.chromium.org/
```

### 步驟 3：複製工具文件

將以下文件複製到儲存庫根目錄：
- `pubmed_fetcher.py`
- `unpaywall_fetcher.py`
- `papers_json_manager.py`
- `scraper_tools.py`
- `automation_pipeline.py`

### 步驟 4：建立設定文件

建立 `config.json`：

```json
{
  "email": "your-email@example.com",
  "github_repo_path": "/path/to/your/repo",
  "max_results_per_query": 50,
  "default_tags": {
    "substrate": "Pellethane 2363 TPU",
    "cure_method": "LED UV",
    "application": "Ureteral Stent (Double J)"
  },
  "search_queries": [
    "ureteral stent hydrophilic coating",
    "medical device lubricity",
    "TPU biocompatible coating"
  ]
}
```

---

## 逐步使用教學

### 用途 1：查詢 PubMed（一次性）

```python
from pubmed_fetcher import PubMedFetcher

# 初始化
fetcher = PubMedFetcher(email="your-email@example.com")

# 查詢單個關鍵詞
papers = fetcher.search_and_fetch(
    query="ureteral stent hydrophilic coating",
    max_results=100,
    min_date="2020/01/01"
)

# 保存為 JSON
import json
with open("pubmed_results.json", "w") as f:
    json.dump(papers, f, ensure_ascii=False, indent=2)

print(f"✅ 找到 {len(papers)} 篇論文")
```

### 用途 2：檢查開放存取狀態

```python
from unpaywall_fetcher import OpenAccessAggregator

# 初始化
aggregator = OpenAccessAggregator(email="your-email@example.com")

# 為每篇論文尋找免費版本
for paper in papers:
    enriched = aggregator.find_free_version(paper)
    if enriched["oa_info"]["is_oa"]:
        print(f"✅ {paper['title']}")
        print(f"   免費 URL: {enriched['oa_info']['free_urls']}")
    else:
        print(f"❌ {paper['title']} - 需要訂閱")
```

### 用途 3：轉換為 papers.json v2.0

```python
from papers_json_manager import PapersJSONFormatter, PapersJSONManager

# 初始化管理器
manager = PapersJSONManager("papers.json")

# 轉換 PubMed 數據
formatted_papers = [
    PapersJSONFormatter.convert_from_pubmed(
        paper,
        substrate="Pellethane 2363 TPU",
        cure_method="LED UV",
        application="Ureteral Stent (Double J)"
    )
    for paper in papers
]

# 添加到 papers.json
added = manager.batch_add(formatted_papers)
manager.save()

print(f"✅ 添加了 {added} 篇論文到 papers.json")
```

### 用途 4：提取 PDF 全文

```python
from scraper_tools import PDFExtractor

# 下載並提取 PDF
url = "https://example.com/paper.pdf"
text, metadata = PDFExtractor.download_and_extract(url)

if text:
    print(f"✅ 提取了 {len(text)} 字符")
    print(f"元數據: {metadata}")
    
    # 提取表格
    tables = PDFExtractor.extract_tables(url)
    print(f"找到 {len(tables)} 個表格")
```

### 用途 5：一鍵自動化管道

```python
from automation_pipeline import AutomationPipeline

# 初始化管道
pipeline = AutomationPipeline(
    github_repo_path="/path/to/Pigtail",
    email="your-email@example.com",
    max_results=50
)

# 執行一次完整流程
success = pipeline.run(
    search_query="ureteral stent coating 2024",
    min_date="2024/01/01",
    tags={
        "substrate": "Pellethane 2363 TPU",
        "cure_method": "LED UV"
    }
)

if success:
    print("✅ 成功更新 papers.json 並推送到 GitHub")
```

---

## 進階功能

### 進階 1：多條件過濾搜尋

```python
from papers_json_manager import PapersJSONManager

manager = PapersJSONManager("papers.json")

# 搜尋：Pellethane TPU + LED UV 固化 + 2020-2023 年
results = manager.export_filtered({
    "substrate": ["Pellethane 2363 TPU"],
    "cure_method": ["LED UV"],
    "year": [2020, 2021, 2022, 2023]
})

print(f"找到 {len(results)} 篇相關論文")
for paper in results:
    print(f"  - {paper['title']} ({paper['year']})")
```

### 進階 2：動態網站爬蟲

```python
from scraper_tools import DynamicWebScraper

# 用 Selenium 爬蟲 JavaScript 渲染的頁面
scraper = DynamicWebScraper(headless=True)

html = scraper.scrape_page(
    "https://example.com/journal-toc",
    wait_selector=".article-list"  # 等待該元素加載
)

if html:
    print(f"✅ 爬蟲成功，獲得 {len(html)} 字符的 HTML")

scraper.close()
```

### 進階 3：自訂 GitHub Actions 排程

```python
from automation_pipeline import GitHubActionsScheduler

# 建立 GitHub Actions workflow
GitHubActionsScheduler.create_workflow(
    github_repo_path="/path/to/repo",
    cron_schedule="0 0 * * 0",  # 每週日午夜
    search_queries=[
        "ureteral stent coating",
        "medical device biocompatibility",
        "polymer friction reduction"
    ]
)

# workflow 文件會建立在 .github/workflows/auto-update-papers.yml
```

---

## GitHub 整合

### 步驟 1：推送初始 papers.json

```bash
# 確保在儲存庫目錄下
cd /path/to/Pigtail

# 建立初始 papers.json（如果沒有）
python -c "from papers_json_manager import PapersJSONManager; \
           m = PapersJSONManager('papers.json'); \
           m.save()"

# 提交並推送
git add papers.json
git commit -m "Initial papers.json database"
git push origin main
```

### 步驟 2：設定 GitHub Actions 自動化

```bash
# 執行自動建立 workflow 文件
python -c "from automation_pipeline import GitHubActionsScheduler; \
           GitHubActionsScheduler.create_workflow('/path/to/Pigtail')"

# 提交 workflow
git add .github/workflows/
git commit -m "Add GitHub Actions auto-update workflow"
git push origin main
```

### 步驟 3：設定 GitHub Secrets（用於 API 認證）

在 GitHub 儲存庫設定：
1. 進入 Settings → Secrets and variables → Actions
2. 新增 Secret：
   - **Name**: `RESEARCHER_EMAIL`
   - **Value**: `your-email@example.com`

3. （可選）新增 Secret：
   - **Name**: `GITHUB_TOKEN`
   - **Value**: GitHub 會自動提供

### 步驟 4：手動測試自動化（可選）

```bash
# 手動執行一次完整流程
python automation_pipeline.py

# 檢查結果
git status  # 應該顯示 papers.json 有更新
```

---

## 常見問題

### Q1: PubMed API 返回空結果？

**A:** 
- 檢查搜尋關鍵詞拼寫
- 嘗試更廣泛的查詢（如只用 "stent coating"）
- 確認網路連接正常
- NCBI 有 API 使用政策，過於頻繁請求可能被暫時限制

```python
# 診斷
fetcher = PubMedFetcher(email="your-email@example.com")
pmids = fetcher.search("ureteral stent", max_results=10)
print(f"找到 {len(pmids)} 篇論文")
```

### Q2: Unpaywall 查詢很慢？

**A:**
- Unpaywall API 建議 1 秒延遲，請耐心等待
- 可使用 `time.sleep()` 自訂延遲
- 大批量查詢可分批進行

```python
# 優化：批量查詢時添加進度條
from tqdm import tqdm

for doi in tqdm(dois):
    result = aggregator.check_oa_status(doi)
```

### Q3: GitHub 推送失敗？

**A:**
- 檢查 Git 設定：
  ```bash
  git config user.email "your-email@example.com"
  git config user.name "Your Name"
  ```
- 確認有推送權限（SSH key 或 Personal Access Token）
- 檢查分支名稱（main vs master）

```bash
# 診斷
git remote -v  # 檢查遠程 URL
git status     # 檢查狀態
```

### Q4: PDF 提取失敗？

**A:**
- 確認安裝了 `pdfplumber`：`pip install pdfplumber`
- 某些 PDF 可能受密碼保護或無法複製文本
- 嘗試在線工具驗證 PDF 可讀性

```python
# 檢查 PDF 可讀性
import pdfplumber
try:
    with pdfplumber.open(pdf_path) as pdf:
        print(f"PDF 有 {len(pdf.pages)} 頁")
except Exception as e:
    print(f"PDF 讀取失敗: {e}")
```

### Q5: 如何自訂 papers.json 的分類標籤？

**A:** 編輯 `papers_json_manager.py` 中的分類清單：

```python
# 在 PapersJSONFormatter 類中修改
SUBSTRATES = [
    "Pellethane 2363 TPU",
    "Silicone",
    "Custom Material"  # 添加你的自訂材料
]

CURE_METHODS = [
    "Air Plasma",
    "LED UV",
    "Your Custom Method"  # 添加你的固化方法
]
```

---

## 實務建議

### 💡 最佳實踐

1. **定期備份**
   ```bash
   # 每週備份 papers.json
   cp papers.json "backups/papers_$(date +%Y%m%d).json"
   ```

2. **版本控制**
   ```bash
   # 定期檢查 papers.json 的更新歷史
   git log --oneline papers.json
   git diff HEAD~1 papers.json  # 查看最後一次更新的改動
   ```

3. **數據驗證**
   ```python
   # 添加論文前驗證
   import json
   with open("papers.json", "r") as f:
       data = json.load(f)
   
   # 檢查版本
   assert data.get("version") == "2.0"
   
   # 檢查必要欄位
   for paper in data.get("papers", []):
       assert paper.get("id")
       assert paper.get("title")
   ```

4. **漸進式擴展**
   - 先用小規模查詢測試（如 10-20 篇論文）
   - 確認流程正常後再擴大範圍
   - 逐步調整 cron 排程頻率

### 📊 監控和維護

```python
# 建立定期審查腳本
from papers_json_manager import PapersJSONManager

manager = PapersJSONManager("papers.json")
stats = manager.get_statistics()

print(f"""
📊 資料庫狀態:
  總論文數: {stats['total']}
  開放存取: {stats['oa_papers']}
  近年論文: {sum(v for k, v in stats['by_year'].items() if int(k) >= 2023)}
  主要基材: {max(stats['by_substrate'].items(), key=lambda x: x[1])[0]}
  主要固化方法: {max(stats['by_cure_method'].items(), key=lambda x: x[1])[0]}
""")
```

---

## 總結

這個系統讓你：
✅ **自動化** 文獻搜尋和管理
✅ **標準化** 論文元數據（papers.json v2.0）
✅ **免費獲得** 大量開放存取論文
✅ **與 GitHub 同步** 使用 GitHub Pages 展示
✅ **智能過濾** 支援多維度搜尋
✅ **可持續維護** 通過 GitHub Actions 定時更新

祝你的文獻研究順利！如有問題，歡迎提 GitHub Issue 或親自測試。
