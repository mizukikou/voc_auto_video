# VOC_Sentry 20 分鐘發表影片自動化生成專案 — 專案狀態與交接摘要

## 1. 專案目標與工作目錄
- **工作目錄**：`c:\voc_auto_video`
- **輸出目錄**：`c:\voc_auto_video\output_visual_20min\`
  - 分段短語音快取：`audio\part_XX_sYY.mp3`
  - 分段影片快取：`clips\clip_01.mp4` ~ `clip_16.mp4`
  - 主合成影片與字幕：`VOC_Sentry_20min_Visual_Master.mp4` / `.ass`
  - 最終硬燒字幕成品：`VOC_Sentry_20min_Final_HardSub.mp4`
- **影片總架構（共 16 幕，約 20 分鐘，1920x1080 @ 12fps）**：
  - **PART 1（Slide 01 ~ 08）**：系統架構與完整交付成果（左欄重點卡片 + 右欄動態圖表）。
  - **PART 2（Demo 09 ~ 11）**：GitHub 團隊協作流程（建立 Issue #43 → Feature 分支與 114 項隔離測試 → PR 品質閘門與合併）。
  - **PART 3（Demo 12 ~ 16）**：Windows 本機建置（Waitress）與網站實戰操作（Dashboard 下鑽 → RBAC 登入 → VOC 白名單與評分底線連結 → 拋棄式 Token 核銷與 Fail-Closed 審計）。

---

## 2. 核心程式檔案職責與設計規格
1. **`1_visual_engine.py`（PART 1 投影片視覺渲染引擎）**
   - 支援左右雙欄各自依語音關鍵句比例（`trigger_ratios`、`right_ratios`）動態浮現。
   - **Slide 01**：右側三條長條圖百分比數字（`65% - 80%`、`63.4%`、`20% 以下`）隨長條伸長動畫（`bar_anim`）同步跳動。
   - **Slide 03**：架構圖頂部常駐 `運行環境：Python 3.14 | Django 5.2 | DRF 3.16 | MySQL 8.0`，包含 `Waitress WSGI (127.0.0.1:8000 | DEBUG=False)` 與底部 `[邊界隔離] 離線 EDA：Pandas / Matplotlib`。
   - **Slide 04**：MySQL ER Diagram 依語音順序顯示 `VOCReview` → `ImageAsset` → `VOCRestrictedAuditLog` → `auth_user (RBAC 帳號)`，並畫出三條 `1 : N` 外鍵連線（`target_id`、`actor_id`、`uploaded_by`），說明 `VOCReview` 與 `auth_user` 透過審計表橋接。
   - 底部配置雙層「**螢光紅 `(255, 45, 85)`**」與「**螢光綠 `(57, 255, 20)`**」霓虹流光條（位於字幕區下緣，避免遮擋字幕）。
2. **`2_demo_renderer.py`（PART 2 & PART 3 操作演示渲染引擎）**
   - 支援 `d_ratios` 依語音句首逐組顯示終端機指令與審查項目，絕不提早劇透。
   - 中文註解與狀態列使用微軟正黑體 `F_SMALL`，純英文指令使用等寬字型 `F_MONO`（無方框亂碼）。
   - **Demo 10 (`git_branch`)**：`Ran 114 tests in 4.82s - OK` 具備發光螢光綠燈圓點與綠色高亮外框。
   - **Demo 15 (`voc`)**：無 `[檢視受限內文]` 按鈕，直接以**評分 `8.0` 出現藍色連結底線**代表具備受限資料核銷雙重權限。
3. **`3_presentation_data.py`（16 幕完整講稿、觸發關鍵句與鼠標路徑資料）**
   - **Slide 01**：五項主軸完整收錄（`資料正確 → 可驗證 → 可操作 → 安全可控 → 自動化驗證`）。
   - **Slide 04**：講稿已補充 `VOCReview` 與 `auth_user` 透過審計紀錄表橋接的三條 `1 : N` 外鍵說明。
   - **Demo 10**：講稿已切分為 5 個獨立句子，確保最後一組 `git add` & `git push` 在念到「確認沒有破壞任何現有功能後」才顯示。
   - **Demo 15**：鼠標精準移動並點擊第一筆資料帶有底線的 `8.0` 分連結 `(505, 345)`。
4. **`4_run_build.py`（逐句精準語音合成與 0 誤差音畫同步主程式）**
   - 使用 `zh-TW-HsiaoChenNeural`（語速 `-12%`），將每幕講稿按句號切分為短句獨立合成 `.mp3`，依真實音檔秒數累加時間軸，並於每幕結尾補上 `2.0` 秒真實靜音幀（`AudioArrayClip`），確保全片 20 分鐘音畫與字幕零誤差同步。
   - 支援斷點續傳快取機制（已存在的 `part_XX_sYY.mp3` 與 `clip_XX.mp4` 會自動跳過）。
5. **`5_burn_hard_subtitles.py`（FFmpeg ASS 亮黃色黑底硬字幕燒錄腳本）**

---

## 3. 常用局部重算與全片重建指令（PowerShell）

### 情境 A：僅修改某一幕的「畫面排版/動畫」（未改語音講稿）
```powershell
# 範例：僅重算第 10 幕畫面並重新燒錄字幕
Remove-Item -Path "c:\voc_auto_video\output_visual_20min\clips\clip_10.mp4" -Force -ErrorAction SilentlyContinue
python -u "c:\voc_auto_video\4_run_build.py"
python -u "c:\voc_auto_video\5_burn_hard_subtitles.py"
```

### 情境 B：修改某一幕的「語音講稿文字」（需同步重算該幕語音與畫面）
```powershell
# 範例：重算第 10 幕語音與畫面
Remove-Item -Path "c:\voc_auto_video\output_visual_20min\audio\part_10*.*","c:\voc_auto_video\output_visual_20min\clips\clip_10.mp4" -Force -ErrorAction SilentlyContinue
python -u "c:\voc_auto_video\4_run_build.py"
python -u "c:\voc_auto_video\5_burn_hard_subtitles.py"
```

---

## 4. 給 AI 助手的協作規範（開啟新對話時請遵守）
- 提供完整 Python 程式碼修改時，**務必拆分成 4 個短小區塊分段顯示**，避免網頁介面截斷。
- 避免直接使用 `list[0]` 方括號索引（防止 Markdown 過濾），統一使用 `list.__getitem__(0)` 寫法。
