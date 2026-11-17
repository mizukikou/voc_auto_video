我正在進行「VOC_Sentry 旅宿顧客評論分析與安全查詢平台」的專題發表準備與自動化簡報影片製作，以下是目前累積的所有核心背景、系統架構與自動化影片腳本進度，請接續協助我：

### 一、 專案背景與核心規格（VOC_Sentry）
1. **商業背景與實證資料**：台灣旅宿業約 65%–80% 高度依賴 OTA 平台導流。本專案以「東門3號青年旅館」Booking.com 的 **1,476 筆**真實評論為實證，解決人工讀不完、跨月趨勢難察覺、以及評論夾帶旅客姓名（PII）與隱私個資的痛點。
2. **團隊治理與 52 份交付資產**：六週 MVP，採四人職責分離（A 資料ETL、B 前端UI、C 架構整合、D 測試QA）與單向規格追溯鏈。已完成 `Requirements.md (v1.2)`、`architecture.md (v1.1)`、`data_dictionary.md (v1.2)`、`api_contract.md (v1.1 + Issue #43)`、`testing_plan.md (v1.2)`、網站操作手冊與新手教學等 52 份資產，並如實區分完成（✅）、部分完成（🟡 Issue #43 手動瀏覽器清單待補）與未完成（⬜ Linux HTTPS 正式部署）。
3. **技術架構（Hybrid View）**：Python 3.14 + Django 5.2 + DRF 3.16 + MySQL 8.0 + Waitress（本機 127.0.0.1:8000，DEBUG=False）。遵循 KISS 原則（不引入 React/Vue/Redis/Celery/Docker）；一般頁面採 Django Templates SSR，儀表板動態圖表（Chart.js）與分頁採 DRF JSON API；Pandas/Matplotlib 僅限離線 EDA。
4. **資料層與等冪 ETL**：
   - 三大核心表：`VOCReview`、`ImageAsset`、`VOCRestrictedAuditLog`。
   - 技術主鍵 `BigAutoField`；業務去重採複合唯一鍵 `(reviewer_name, review_date, title)` 並設為欄位級 `utf8mb4_0900_bin` 精準比對；評分採 `Decimal(3,1)`；缺失標題正規化為「未提供標題」。
   - `import_voc` 唯讀串流讀取 UTF-8 BOM CSV（SHA-256 前後不變），同鍵同內容跳過、同鍵異內容拒覆寫確保等冪，結構錯誤或錯誤列達 10% 觸發熔斷整批拒收。
5. **儀表板與資安防護（零信任與 Fail-Closed）**：
   - 台北日期（UTC+8）轉 UTC 半開區間查詢；KPI 總數（1,476）= 37 個月趨勢加總 = 9 個評分分布加總（2023-10 單月皆為 41 筆）。
   - RBAC 群組控權（`VOC_Analyst`、`Quality_Auditor`、`Compliance_Officer`），即使是 Superuser 未獲明確授權亦不放行。
   - Issue #43 短效拋棄式權杖：CSPRNG 產生，SHA-256 摘要存於單程序 `LocMemCache`，效期 5 分鐘、綁定 Session、單次原子核銷、限 CSRF 保護之 POST Body 傳遞；禁止前端傳 `reason_code`（後端依群組自動推導）；必須先成功寫入 `VOCRestrictedAuditLog` 才顯示受限內文（Fail-Closed，保留 90 天，不存原文）。
   - 影像防護（`ImageProtectionService`）：限 JPEG/PNG、<=5MB、<=2000萬像素，校驗二進位檔頭；原圖 UUID 存私有目錄（需 `view_original_image`）；展示圖去 EXIF、縮放 1600px 並加浮水印。
6. **測試與驗證架構（隔離測試庫，零污染正式庫 `voc_sentry_local`）**：
   - 獨立量化測試紀錄（彼此獨立不相加）：**103 項**（本機交付回歸與 Migration 漂移檢查）、**75 項**（Issue #40 合成 CSV 端到端整合）、**114 項**（Issue #43 權限與權杖自動化測試）、**29 案**需求追溯矩陣。
   - `scripts/` 離線驗證腳本：`step2_inventory.py`（唯讀盤點）、`step2_independent_validation.py`（獨立重算原始 CSV 防盲點）、`issue38_dashboard_validation.py`（針對真實 1,476 筆唯讀對帳）。

---

### 二、 自動化 20 分鐘發表影片製作進度（位於 `C:\voc_auto_video\`）
目前已完成模組化 Python 影片生成引擎（使用 `edge-tts` 台灣繁體女聲 `zh-TW-HsiaoChenNeural`、`Pillow` 動態繪圖、`MoviePy` 剪輯與 `imageio_ffmpeg` 硬燒字幕）：
1. `1_visual_engine.py`：賽博科技感雙欄簡報引擎（含動態科技網格、旋轉光環、流光掃描線、能量流動線、標準 `1 : N` ER 實體關聯圖、動態伸長長條圖與 103/75/114 數據卡片）。
2. `2_demo_renderer.py`：模擬鼠標與雙層霓虹點擊特效引擎，演示 GitHub 開立 Issue #43 → Feature 分支開發與隔離測試 → PR #44 審查合併，以及 PowerShell 執行 `local_server.py`（`--setup`、`--check`、`--port 8000`）與網站完整操作流程。
3. `3_presentation_data.py`：16 幕完整全白話自然口語講稿（總長約 20 分鐘）。
4. `4_run_build.py`：主渲染引擎（語速 `RATE = "-5%"`），產出 `output_visual_20min/VOC_Sentry_20min_Visual_Master.mp4` 與亮黃色單行自然語意字幕 `.ass`。
5. `5_burn_hard_subtitles.py`：呼叫 FFmpeg 將 `.ass` 字幕永久硬燒進 `.mp4`，產出單檔可直接跨電腦播放的 `VOC_Sentry_20min_Final_HardSub.mp4`。

請確認收到以上彙整資料，並隨時準備協助我進行簡報演練 Q&A、文件調整或影片微調！
