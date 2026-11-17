import os
import textwrap
import asyncio
import numpy as np
import edge_tts
from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageClip, VideoClip, AudioFileClip, concatenate_videoclips

VOICE = "zh-TW-HsiaoChenNeural"
RATE = "+0%"
FONT_BOLD = r"C:\Windows\Fonts\msjhbd.ttc"
FONT_REG = r"C:\Windows\Fonts\msjh.ttc"
FONT_MONO = r"C:\Windows\Fonts\consola.ttf"
WIDTH, HEIGHT = 1920, 1080
FPS = 24

def load_fonts():
    try:
        return (
            ImageFont.truetype(FONT_BOLD, 48),
            ImageFont.truetype(FONT_BOLD, 38),
            ImageFont.truetype(FONT_REG, 32),
            ImageFont.truetype(FONT_REG, 24),
            ImageFont.truetype(FONT_MONO, 28),
        )
    except IOError:
        d = ImageFont.load_default()
        return d, d, d, d, d

F_H1, F_H2, F_BODY, F_SMALL, F_MONO = load_fonts()

def create_slide_image(part_num, total_parts, title, bullets, output_img_path):
    img = Image.new("RGB", (WIDTH, HEIGHT), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)
    draw.rectangle((60, 60, WIDTH - 60, HEIGHT - 60), outline=(56, 189, 248), width=3)
    draw.rectangle((60, 60, WIDTH - 60, 210), fill=(30, 41, 59))
    draw.rectangle((60, 60, 85, 210), fill=(56, 189, 248))
    draw.text((120, 82), f"SECTION 1：系統架構與技術規格  |  PART {part_num:02d} / {total_parts}", fill=(56, 189, 248), font=F_SMALL)
    draw.text((120, 125), title, fill=(248, 250, 252), font=F_H1)

    y_offset = 265
    for bullet in bullets:
        draw.rectangle((110, y_offset - 15, WIDTH - 110, y_offset + 125), fill=(30, 41, 59), outline=(51, 65, 85), width=2)
        draw.ellipse((140, y_offset + 15, 175, y_offset + 50), fill=(56, 189, 248))
        wrapped = textwrap.wrap(bullet, width=44)
        text_y = y_offset + (12 if len(wrapped) == 1 else -2)
        for line in wrapped:
            draw.text((205, text_y), line, fill=(226, 232, 240), font=F_BODY)
            text_y += 46
        y_offset += 165

    draw.line((60, HEIGHT - 130, WIDTH - 60, HEIGHT - 130), fill=(51, 65, 85), width=2)
    draw.text((110, HEIGHT - 102), "VOC_Sentry 旅宿顧客評論分析與安全查詢平台  |  20 分鐘完整技術與實戰發表", fill=(148, 163, 184), font=F_SMALL)
    draw.text((WIDTH - 250, HEIGHT - 102), f"Slide {part_num:02d} / {total_parts}", fill=(56, 189, 248), font=F_SMALL)
    img.save(output_img_path)
def draw_cursor_and_click(draw, x, y, is_clicking=False):
    if is_clicking:
        draw.ellipse((x - 32, y - 32, x + 32, y + 32), outline=(239, 68, 68), width=4)
        draw.ellipse((x - 16, y - 16, x + 16, y + 16), fill=(239, 68, 68))
    pointer = [(x, y), (x, y + 36), (x + 10, y + 26), (x + 18, y + 42), (x + 24, y + 39), (x + 16, y + 23), (x + 28, y + 23)]
    draw.polygon(pointer, fill=(255, 255, 255), outline=(15, 23, 42))

def render_demo_frame(scene_type, progress, title):
    img = Image.new("RGB", (WIDTH, HEIGHT), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, WIDTH, 90), fill=(30, 41, 59))
    draw.text((50, 22), f"SECTION 2：網站建置與實戰操作演示  |  {title}", fill=(74, 222, 128), font=F_H2)

    if scene_type == "powershell":
        draw.rectangle((120, 140, WIDTH - 120, HEIGHT - 80), fill=(12, 12, 12), outline=(100, 116, 139), width=3)
        draw.rectangle((120, 140, WIDTH - 120, 195), fill=(30, 41, 59))
        draw.text((150, 152), "Administrator: Windows PowerShell - C:\\VOC_Sentry", fill=(226, 232, 240), font=F_SMALL)
        commands = [
            "PS C:\\VOC_Sentry> python -m venv .venv",
            "PS C:\\VOC_Sentry> .\\.venv\\Scripts\\python.exe -m pip install -r .\\requirements.txt",
            "PS C:\\VOC_Sentry> .\\.venv\\Scripts\\python.exe .\\backend\\local_server.py --setup",
            "[OK] Database 'voc_sentry_local' initialized safely (utf8mb4).",
            "PS C:\\VOC_Sentry> .\\.venv\\Scripts\\python.exe .\\backend\\local_server.py --check",
            "System check identified no issues (0 silenced). Migrations verified.",
            "PS C:\\VOC_Sentry> .\\.venv\\Scripts\\python.exe .\\backend\\local_server.py --port 8000",
            "[INFO] Serving VOC_Sentry on http://127.0.0.1:8000 (DEBUG=False)"
        ]
        visible_lines = max(1, int(progress * (len(commands) + 1)))
        y = 230
        for line in commands[:visible_lines]:
            color = (74, 222, 128) if line.startswith("[") or "no issues" in line else (248, 250, 252)
            draw.text((160, y), line, fill=color, font=F_MONO)
            y += 65
        return img

    draw.rectangle((100, 130, WIDTH - 100, HEIGHT - 70), fill=(248, 250, 252), outline=(148, 163, 184), width=3)
    draw.rectangle((100, 130, WIDTH - 100, 200), fill=(226, 232, 240))
    urls = {
        "dashboard": "http://127.0.0",
        "login": "http://127.0.0",
        "voc": "http://127.0.0",
        "token": "http://127.0.0  (POST Body + CSRF)",
        "image": "http://127.0.0"
    }
    draw.rectangle((280, 145, WIDTH - 200, 185), fill=(255, 255, 255), outline=(203, 213, 225), width=2)
    draw.text((300, 152), urls[scene_type], fill=(51, 65, 85), font=F_SMALL)
    draw.rectangle((100, 200, WIDTH - 100, 270), fill=(15, 23, 42))
    draw.text((140, 218), "VOC_Sentry  |   Dashboard    VOC清單    圖片安全    Admin", fill=(248, 250, 252), font=F_BODY)

    if scene_type == "dashboard":
        draw.rectangle((150, 310, 650, 480), fill=(255, 255, 255), outline=(203, 213, 225), width=2)
        draw.text((180, 335), "通過資料驗證筆數 (KPI)", fill=(100, 116, 139), font=F_SMALL)
        draw.text((180, 385), "1,476 筆", fill=(14, 165, 233), font=F_H1)
        draw.rectangle((700, 310, WIDTH - 150, 880), fill=(255, 255, 255), outline=(203, 213, 225), width=2)
        draw.text((740, 335), "評分分布長條圖 (點擊 8.0 分長條下鑽查詢)", fill=(30, 41, 59), font=F_BODY)
        scores = [("6.0", 120), ("7.0", 210), ("8.0", 380), ("9.0", 420), ("10.0", 340)]
        bx = 780
        for sc, h in scores:
            bar_color = (239, 68, 68) if (sc == "8.0" and progress > 0.5) else (56, 189, 248)
            draw.rectangle((bx, 800 - h, bx + 110, 800), fill=bar_color)
            draw.text((bx + 30, 815), sc, fill=(30, 41, 59), font=F_SMALL)
            bx += 180
    elif scene_type == "login":
        draw.rectangle((660, 330, 1260, 770), fill=(255, 255, 255), outline=(203, 213, 225), width=2)
        draw.text((710, 365), "系統帳號登入 (無公開註冊)", fill=(15, 23, 42), font=F_H2)
        draw.rectangle((710, 450, 1210, 510), outline=(148, 163, 184), width=2)
        draw.text((730, 465), "analyst_user (群組: VOC_Analyst)", fill=(51, 65, 85), font=F_BODY)
        draw.rectangle((710, 540, 1210, 600), outline=(148, 163, 184), width=2)
        draw.text((730, 555), "••••••••••••••••", fill=(51, 65, 85), font=F_BODY)
        btn_color = (2, 132, 199) if progress > 0.6 else (14, 165, 233)
        draw.rectangle((710, 645, 1210, 710), fill=btn_color)
        draw.text((905, 658), "安全登入", fill=(255, 255, 255), font=F_BODY)
    elif scene_type == "voc":
        draw.text((150, 300), "VOC 授權查詢清單 (篩選: score = 8.0 | 隱藏 PK 與 review_id)", fill=(15, 23, 42), font=F_BODY)
        draw.rectangle((150, 360, WIDTH - 150, 420), fill=(226, 232, 240))
        draw.text((180, 375), "評論日期 (UTC)          分數     國家       房型              操作", fill=(30, 41, 59), font=F_BODY)
        rows = [
            "2026-10-15T08:20:00Z     8.0      Taiwan     混合宿舍床位      [檢視受限內文]",
            "2026-10-12T14:05:00Z     8.0      Japan      女性專屬六人房    [檢視受限內文]",
            "2026-10-09T11:40:00Z     8.0      Korea      雙人標準房        [檢視受限內文]"
        ]
        ry = 445
        for r in rows:
            draw.rectangle((150, ry - 10, WIDTH - 150, ry + 55), fill=(255, 255, 255), outline=(226, 232, 240), width=2)
            draw.text((180, ry + 5), r, fill=(51, 65, 85), font=F_BODY)
            ry += 85
    elif scene_type == "token":
        draw.rectangle((360, 310, WIDTH - 360, 880), fill=(255, 255, 255), outline=(239, 68, 68), width=3)
        draw.text((410, 345), "受限欄位安全檢視 (一次性拋棄式權杖驗證通過)", fill=(185, 28, 28), font=F_H2)
        info = [
            "• 權杖驗證：CSPRNG Token 核銷成功 (LocMemCache 單次原子消耗)",
            "• 隱式原因碼：後端依群組自動推導為 SUPPORT_CASE (禁止前端傳入)",
            "• 強制審計：已寫入 VOCRestrictedAuditLog [ALLOW] (保留90天)",
            "------------------------------------------------------------------",
            "• 評論者 (PII)：王*明 (已通過雙權限授權顯示)",
            "• 評論原文：地點離捷運東門站非常近，公共空間乾淨且服務人員親切！"
        ]
        iy = 430
        for line in info:
            draw.text((410, iy), line, fill=(30, 41, 59), font=F_BODY)
            iy += 65
    elif scene_type == "image":
        draw.text((150, 300), "影像安全防護模組 (ImageProtectionService)", fill=(15, 23, 42), font=F_BODY)
        draw.rectangle((150, 370, 910, 850), fill=(255, 255, 255), outline=(203, 213, 225), width=2)
        draw.text((180, 400), "1. 上傳驗證與私有原圖隔離", fill=(15, 23, 42), font=F_BODY)
        draw.text((180, 460), "• 僅限 JPEG/PNG (<=5MB, <=2000萬像素)\n• 原圖以 UUID 命名存於 private_images/\n• 需明確 view_original_image 權限", fill=(71, 85, 105), font=F_SMALL)
        draw.rectangle((960, 370, WIDTH - 150, 850), fill=(255, 255, 255), outline=(14, 165, 233), width=3)
        draw.text((990, 400), "2. 公開展示圖 (去 EXIF + 浮水印)", fill=(2, 132, 199), font=F_BODY)
        draw.rectangle((1020, 470, WIDTH - 210, 790), fill=(226, 232, 240))
        draw.text((1160, 610), "[ 展示圖片已合成 VOC Sentry 浮水印 ]", fill=(100, 116, 139), font=F_BODY)
    return img
SLIDE_CHAPTERS = [
    {
        "id": 1,
        "title": "商業背景、市場痛點與專案願景",
        "bullets": [
            "台灣整體旅宿業約 65% 至 80% 高度依賴 OTA 平台導流",
            "以「東門3號青年旅館」Booking.com 1,476 筆真實評論為實證",
            "解決三大痛點：人工讀不完、跨月趨勢難察覺、內含旅客隱私個資",
            "設計主軸：資料正確 → 分析可驗證 → 系統可操作 → 安全可控 → 測試可追溯"
        ],
        "script": (
            "大家好，歡迎來到 VOC Sentry 旅宿顧客評論分析與安全查詢平台的完整開發與實戰操作發表。"
            "我們首先來看這個專案的商業背景與核心痛點。根據市場統計，台灣整體旅宿業有高達百分之六十五到八十的訂單高度依賴線上訂房平台 OTA 導流，"
            "而旅客留下的網路評論直接決定了潛在客群的訂房意願。然而，對於人手有限的中小型旅宿而言，每天面對大量散落的評論，往往面臨三個嚴峻挑戰："
            "第一是評論量大，人工根本讀不完；第二是分數、日期與房型分散在各篇文章中，很難看出服務品質是變好還是變差；"
            "第三則是評論內容往往夾帶旅客姓名與個人住宿經驗，若直接開放給所有員工查看，會產生嚴重的隱私外洩與個資合規風險。"
            "因此，我們以東門3號青年旅館在 Booking.com 上的 1,476 筆真實住客評論為例，打造了 VOC Sentry 最小可行性產品。"
            "我們的目標是將傳統的「事後補救」，轉型為「可重複匯入、可交叉驗證、且權限嚴格可控」的營運決策工具。"
            "整套系統嚴格遵循五項層層遞進的設計原則：資料正確、分析可驗證、系統可操作、安全可控，以及測試可追溯。"
        )
    },
    {
        "id": 2,
        "title": "六週開發治理、四人分工與人機協同守則",
        "bullets": [
            "六週 MVP 敏捷開發，成員由程式設計初學者組成，強調規格先行",
            "四人明確職責：A 資料ETL、B 前端UI、C 架構整合、D 測試QA",
            "單向追溯鏈：Requirements → Architecture → Data Dictionary → API → Test",
            "AI 協作鐵律：AI 是執行助手，人類團隊才是架構與規格的最終決策者"
        ],
        "script": (
            "在進入技術架構之前，我們先說明這個專案的開發治理模式。VOC Sentry 是一個為期六週的 MVP 專案，由四位初學者成員組成，並採用明確的職責分離分工："
            "角色 A 負責原始資料唯讀盤點、資料清洗與 ETL；角色 B 負責前端 Django Templates、Bootstrap 版面與 Chart.js 圖表互動；"
            "角色 C 擔任架構與整合負責人，維護資料字典與 API 契約並管理 Pull Request；角色 D 則負責需求追溯矩陣、合成測試資料與獨立回歸測試。"
            "為了避免開發過程失控，我們建立了一條嚴格的單向規格追溯鏈：從需求規格書 v1.2、系統架構書 v1.1、資料字典 v1.2、API 契約 v1.1，一路落實到 GitHub Issue 與測試案例。"
            "特別值得一提的是我們的人機協同規範。在開發過程中，我們運用 ChatGPT 起草架構、Gemini 進行資安風險二道查核、GitHub Copilot 協助產生程式碼初稿。"
            "但我們訂立了最高守則：AI 是助手，不是決策者。AI 嚴禁接觸正式密鑰或真實顧客姓名，也不能自行發明未經團隊核准的資料庫欄位或 API 端點，所有程式碼都必須經過自動化測試與人工審查才能合併。"
        )
    },
    {
        "id": 3,
        "title": "系統架構設計與混合視圖策略（Hybrid View）",
        "bullets": [
            "採用 Django 5.2 Modular Monolith（模組化單體）架構",
            "遵循 KISS 原則：MVP 不引入 React、Vue、Redis、Celery 或 Docker",
            "SSR 優先混合策略：一般頁面用 Django Templates，圖表用 DRF JSON API",
            "正式環境採用 Waitress WSGI 伺服器，綁定本機 127.0.0.1 運行"
        ],
        "script": (
            "接下來介紹系統整體架構。我們在 Architecture v1.1 中確立了 Django Modular Monolith，也就是模組化單體架構。"
            "後端以 Python 3.14 搭配 Django 5.2 與 Django REST Framework 3.16 為核心，資料庫採用 MySQL 8.0，並使用 Waitress 作為本機 WSGI 伺服器。"
            "在架構決策上，我們嚴格遵守 KISS 保持簡單的原則，刻意排除了微服務、React 或 Vue 等重型單頁應用框架，也不引入 Celery、Redis 或 Message Queue 等非必要基礎設施，"
            "確保團隊能在六週內高可靠度地完成交付。在前後端互動上，我們採用 Hybrid View 混合視圖策略，以伺服器端渲染 SSR 為優先。"
            "一般的網頁導覽、登入驗證與表單操作，全部由 Django Views 搭配 Django Templates 與 Bootstrap 5.3 直接渲染 HTML；"
            "只有在 Dashboard 需要動態繪製 Chart.js 圖表，或是進行動態分頁查詢時，才透過 DRF API 提供最小必要的 JSON 資料交換。"
            "同時，我們也明確劃分了離線分析與線上運行的邊界：Pandas、Matplotlib 與 Seaborn 僅用於 Jupyter Notebook 的離線探索式分析，絕不作為線上網站的圖表渲染依賴。"
        )
    },
    {
        "id": 4,
        "title": "資料字典 v1.2 與資料庫結構設計（ER Model）",
        "bullets": [
            "三大核心資料表：VOCReview、ImageAsset、VOCRestrictedAuditLog",
            "技術主鍵採 BigAutoField，業務去重採複合唯一鍵 (評論者, 日期, 標題)",
            "精準定序：資料庫預設 ai_ci，Business Key 文字欄位採欄位級 utf8mb4_0900_bin",
            "保守隱私分類：reviewer_name 列為 PII，title 與 content 列為 Confidential"
        ],
        "script": (
            "在資料層設計上，我們以實際原始資料盤點為基礎，制定了團隊正式核准的 Data Dictionary v1.2。"
            "MySQL 資料庫主要包含三張核心資料表：儲存評論的 VOCReview、管理上傳影像的 ImageAsset，以及記錄受限欄位存取的 VOCRestrictedAuditLog。"
            "為了兼顧系統效能與業務資料的精準去重，我們在 VOCReview 中採用 Django 的 BigAutoField 作為系統技術主鍵，不對應任何原始欄位；"
            "而在業務層面，則以「評論者姓名、評論日期，以及清理後的有效標題」這三個欄位組成複合唯一約束 Business Key。"
            "特別的是，為了避免資料庫預設的忽略大小寫定序造成不同評論誤判為重複，我們將資料庫預設維持在 utf8mb4_0900_ai_ci，"
            "但針對這三個 Business Key 文字欄位，單獨設定為欄位級的 utf8mb4_0900_bin 二進位精準比對。"
            "在資料隱私分類上，我們採取最保守的治理標準：將評論者姓名歸類為個人識別資訊 PII，將標題與評論內文歸類為機密資料 Confidential，在未通過明確授權前，後端一律預設拒絕回傳。"
        )
    },
    {
        "id": 5,
        "title": "等冪 ETL 資料管線與防呆清洗機制",
        "bullets": [
            "五階段流程：Extract → Validate → Transform → Deduplication → Load",
            "唯讀串流讀取 UTF-8 BOM CSV，執行前後 SHA-256 雜湊值完全不變",
            "欄位精準轉換：stay_info 拆分為住宿晚數與入住日期，score 採 Decimal(3,1)",
            "安全熔斷機制：單列錯誤跳過並記安全摘要，結構錯誤或錯誤達 10% 整批拒收"
        ],
        "script": (
            "系統的第一條核心主線是等冪 ETL 資料匯入管線。為了避免長時間資料處理阻塞網頁請求，ETL 獨立透過 Django Management Command 執行。"
            "整個流程分為擷取、驗證、轉換、去重與載入五個階段。系統以 utf-8-sig 編碼唯讀開啟原始 CSV 檔案，絕不回寫或異動原始檔案，匯入前後的 SHA-256 雜湊值完全一致。"
            "在資料轉換階段，系統會將原始的 Unix 時間戳記轉為 UTC DateTime；將原本的 stay_info 字串，精準拆解為正整數的住宿晚數 stay_nights 與入住日期 stay_date；"
            "針對評分 score，嚴格採用 Decimal(3,1) 儲存，驗證範圍介於 1.0 到 10.0 之間，拒絕浮點數轉換誤差與超過一位小數的異常值；若原始標題缺失或空白，則統一正規化為「未提供標題」。"
            "在去重與容錯設計上，同一份檔案重複執行匯入時，若 Business Key 與內容相同會自動跳過，若同鍵但內容不同則拒絕覆寫並記錄衝突，確保完全的等冪性。"
            "此外，當資料列數達二十列以上且必要欄位錯誤比例達到百分之十，或發生缺少標頭等嚴重結構錯誤時，系統會觸發安全熔斷，整批拒收且絕不寫入半套資料。"
        )
    },
    {
        "id": 6,
        "title": "Dashboard 聚合 API 與台北時區精準查詢",
        "bullets": [
            "三大核准聚合端點：/summary/、/trends/（上限12個月）、/distribution/",
            "時區換算：前端輸入台北日期（UTC+8），後端轉為 UTC 半開區間進行查詢",
            "資料血緣不變量：KPI 總數（1,476）= 月份趨勢加總（1,476）= 評分分布加總（1,476）",
            "完整狀態處理：前端頁面具備 Loading、Empty 無資料與 Error 重試機制"
        ],
        "script": (
            "第二部分是顧客聲量儀表板與聚合 API。依據 API Contract v1.1，儀表板提供三個可匿名瀏覽的彙總端點，分別是摘要統計 summary、每月趨勢 trends，以及評分分布 distribution。"
            "這三個端點共用同一份通過驗證、完成排重且符合日期範圍的評論母體。在時間處理上，為了解決資料庫儲存 UTC 時間與台灣營運日界線的落差，"
            "使用者在前端成對輸入台北日期後，後端會統一換算為台北時間起日零點包含、迄日次日零點不包含的 UTC 時間區間進行查詢。"
            "在實際測試東門3號青年旅館的 1,476 筆評論時，儀表板顯示的核心 KPI 通過驗證筆數、橫跨 37 個月份的趨勢折線圖加總，以及 9 個評分級距的長條圖加總，"
            "三者數字完全相等，皆為 1,476 筆；即使篩選特定月份例如 2023 年 10 月，三項數字依然精準維持 41 筆的完全一致，驗證了高度可靠的資料血緣。"
            "同時，前端畫面也完整實作了載入中 Loading、查無資料 Empty 與後端異常可重試 Error 三種互動狀態，並為圖表附上無障礙資料表格。"
        )
    },
    {
        "id": 7,
        "title": "VOC 查詢白名單控制與評分下鑽流程",
        "bullets": [
            "GET /api/v1/voc/ 嚴格限制查詢白名單：成對日期、精確一位小數 score、分頁",
            "分頁預設 20 筆、上限 100 筆；後端固定依評論日期降冪排序，拒絕外部注入",
            "清單回應採最小揭露：排除系統主鍵 PK、來源 review_id 與評論原文",
            "評分下鑽導流：匿名點擊 Dashboard 長條圖先導向登入，登入後自動返回篩選頁"
        ],
        "script": (
            "當管理者在儀表板上看到某個評分級距，例如 8.0 分有異常波動，想要進一步查看明細時，就會進入 VOC 查詢與評分下鑽流程。"
            "為了防止未授權存取與惡意參數探測，後端對 GET /api/v1/voc/ 實施了嚴格的白名單控制。"
            "查詢參數僅允許成對的起始與結束日期、精確一位小數的 score 篩選，以及預設 20 筆、最大上限 100 筆的 page 與 page_size 分頁參數。"
            "任何未知參數、重複參數或格式錯誤都會直接回傳 HTTP 400 錯誤；排序規則也在後端固定為評論日期降冪排序，徹底杜絕呼叫者傳入任意欄位進行動態 ORM 排序的資安風險。"
            "在資料回傳上，一般清單只會回傳評論日期、分數、國家、房型與旅客類型等核准欄位，完全隱藏資料庫主鍵、來源編號 review_id，以及評論標題與內文。"
            "當匿名使用者在 Dashboard 點擊評分長條時，系統會先將其導向登入頁面，待驗證身分且確認具備 view_approved_voc_fields 權限後，才會安全導回原本點擊的分數篩選清單。"
        )
    },
    {
        "id": 8,
        "title": "零信任權限控管與短效拋棄式權杖（Issue #43）",
        "bullets": [
            "採用 Django RBAC 群組控權：VOC_Analyst、Quality_Auditor、Compliance_Officer",
            "落實零信任原則：即使是 Superuser 超級管理員，未獲明確授權也不自動放行",
            "CSPRNG 產生高強度一次性權杖，僅將 SHA-256 摘要存於單程序 LocMemCache",
            "多重安全綁定：效期 5 分鐘、綁定簽發 Session、單次原子核銷、限 POST Body 傳遞"
        ],
        "script": (
            "在資安防護的核心設計上，我們貫徹零信任與職責分離原則。系統依業務需求配置了三個核准群組：負責客服與營運分析的 VOC_Analyst、"
            "負責資料品質審查的 Quality_Auditor，以及負責合規稽核的 Compliance_Officer。"
            "後端嚴格區分「已登入」與「有權限」，即使是系統超級管理員 Superuser，若未具備明確的欄位權限，依然無法讀取受限評論或原始圖片。"
            "針對極度敏感的評論標題與內文，我們在 Issue #43 中設計了一套「短效拋棄式權杖 Ephemeral Token」機制。"
            "只有當登入者同時具備核准欄位與受限欄位雙重權限時，後端才會透過密碼學安全偽隨機數產生器 CSPRNG 簽發權杖，並只將其 SHA-256 雜湊摘要存入本機記憶體快取 LocMemCache 中。"
            "這組權杖具備四道安全鎖：第一，有效期限僅有 5 分鐘；第二，嚴格綁定當下的登入 Session，跨帳號或跨瀏覽器無法使用；"
            "第三，採用原子操作確保只能被消耗一次，重放攻擊會立即被拒；第四，權杖必須透過受 CSRF 保護的 HTTP POST Body 傳送，絕不出現在網址 URL 中，防止被瀏覽器歷史紀錄或伺服器日誌側錄。"
        )
    },
    {
        "id": 9,
        "title": "隱式原因碼推導與強制審計日誌（Fail-Closed）",
        "bullets": [
            "前端完全移除原因碼選單，禁止用戶端傳入 reason_code（傳入即回傳 400）",
            "後端依操作者所屬群組自動推導合法原因碼（如 VOC_Analyst → SUPPORT_CASE）",
            "強制審計 Fail-Closed：先成功寫入 VOCRestrictedAuditLog，才允許讀取受限內文",
            "審計日誌保存 90 天，只記操作者、目標 ID 與安全關聯碼，絕不複製評論原文"
        ],
        "script": (
            "除了權杖驗證之外，每一次受限評論的調閱都必須經過嚴格的合規審計。在許多傳統系統中，常由前端讓使用者自行下拉選擇查詢原因，但這容易遭到竄改或濫用。"
            "因此，我們在最新契約中徹底移除了前端的原因碼選單，並規定用戶端不得傳入 reason_code 參數，若惡意夾帶該參數，後端會直接回傳 HTTP 400 拒絕請求。"
            "合法的存取原因碼完全由後端根據當前登入者的群組權限自動隱式推導，例如 VOC_Analyst 會自動對應為 SUPPORT_CASE 客服案件支援，Quality_Auditor 則對應為 DATA_QUALITY_REVIEW 資料品質審查。"
            "更重要的是，系統執行嚴格的 Fail-Closed 失效安全機制：在讀取受限評論內容之前，後端必須先將操作者帳號、角色、目標評論識別碼、推導出的原因碼、時間戳記與不具認證能力的請求關聯識別碼，成功寫入資料庫的 VOCRestrictedAuditLog 稽核表。"
            "萬一資料庫異常導致稽核日誌寫入失敗，系統會立刻中斷並拒絕顯示任何受限內容，確保每一筆機敏資料的讀取都百分之百有跡可循。此外，稽核紀錄本身也絕不保存被查看的評論原文，並設定 90 天的保存期限。"
        )
    },
    {
        "id": 10,
        "title": "影像安全防護與去識別化模組（ImageProtectionService）",
        "bullets": [
            "集中式 ImageProtectionService 統一處理，業務模組嚴禁各自實作",
            "嚴格上傳驗證：僅限 JPEG/PNG、上限 5MB 與 2,000 萬像素，校驗二進位檔頭",
            "隱私去識別化：Pillow 轉 RGB 徹底清除相機型號、拍攝時間與 GPS 座標 EXIF",
            "原圖與展示圖分離：原圖以 UUID 存於私有目錄，展示圖縮放 1600px 並加浮水印"
        ],
        "script": (
            "系統的第三條核心主線是影像安全防護模組。我們將所有圖片處理邏輯集中封裝在 ImageProtectionService 服務中，避免安全規則分散在各個視圖。"
            "當已登入使用者透過表單上傳圖片時，系統不相信副檔名，而是直接檢查二進位檔頭與 MIME 類型，僅允許靜態的 JPEG 與 PNG 格式，"
            "並限制檔案大小不超過 5 MB、總像素不超過兩千萬像素，有效防禦動態圖檔與記憶體耗盡的像素炸彈攻擊。"
            "通過驗證後，系統會執行原圖與展示圖的實體與權限分離：原始圖片會以系統產生的 UUID 隨機重新命名，直接杜絕路徑穿越攻擊，並存放在不對外公開的私有目錄中，Cache-Control 設為 private no-store，必須具備明確的 view_original_image 權限才能透過後端 API 讀取。"
            "同時，系統會使用 Pillow 套件將圖片轉換為 RGB 模式，徹底剝除可能洩漏旅客行蹤的 GPS 定位、拍攝時間與相機型號等全部 EXIF 資訊，將長邊等比例縮放至 1600 像素，並合成「VOC Sentry」浮水印，產出供前端公開瀏覽的展示圖，有效降低未授權盜用與個資外洩風險。"
        )
    },
    {
        "id": 11,
        "title": "Windows 本機部署啟動與維運操作實務",
        "bullets": [
            "依循操作手冊進行單機 loopback（127.0.0.1:8000）安全交付與操作",
            "透過 local_server.py 統一管理：--setup 初始化、--check 環境與遷移檢查",
            "強制開啟 DEBUG=False 與本機私有 .env 密鑰隔離，不將真實資料與秘密入版控",
            "嚴格區分正式庫 voc_sentry_local 與隔離測試庫，防範誤刪正式營運資料"
        ],
        "script": (
            "接著我們從操作手冊的角度，說明這套系統在 Windows 本機環境的部署與維運規範。"
            "為了確保系統在交付後能安全穩定地運行，我們撰寫了專屬的 local_server.py 啟動器。"
            "在全新環境首次建置時，維運人員只需在虛擬環境中執行 --setup 參數，系統便會安全初始化本機的 voc_sentry_local 資料庫；若資料庫已存在，啟動器會自動拒絕覆寫，防止誤刪現有資料。"
            "啟動網站服務前，會先執行 --check 進行系統與資料庫遷移狀態檢查，隨後透過 Waitress 伺服器在 127.0.0.1 的 8000 埠號提供服務，並強制設定 DEBUG 為 False，避免任何除錯堆疊追蹤資訊外洩。"
            "在日常安全維運上，所有資料庫密碼、Secret Key 與原始 CSV 檔案皆存放於本機私有環境中，絕不提交至 Git 儲存庫。"
            "建立管理員帳號也必須透過終端機互動式指令完成，並依最小權限原則將帳號分配至對應的核准群組，確保日常操作的高度安全性。"
        )
    },
    {
        "id": 12,
        "title": "自動化品質閘門驗證成果與未來演進藍圖",
        "bullets": [
            "合併前強制品質閘門：安全預檢、MySQL 全域鎖、遷移檢查與 114 項回歸測試",
            "測試隔離保證：固定於獨立資料庫執行，絕不碰觸正式庫 voc_sentry_local",
            "誠實盤點現階段限制：Linux HTTPS 正式部署、90 天稽核自動排程待上線",
            "未來演進藍圖：導入 Redis 共用快取、NLP 情緒主題分析與負評即時預警"
        ],
        "script": (
            "最後，我們來總結第一階段技術架構的自動化品質驗證成果與未來演進方向。"
            "為了確保每一次程式碼合併都不會破壞既有功能，我們建立了一套嚴謹的自動化品質閘門，包含安全預檢、取得 MySQL 全域具名鎖，並執行 makemigrations --check 防範資料庫結構漂移。"
            "所有測試皆固定在完全隔離的測試資料庫中運行，測試結束後自動清理，百分之百不碰觸正式的 voc_sentry_local 資料庫，最終共計 114 項自動化整合回歸測試全數通過。"
            "在未來的演進藍圖中，我們規劃將系統部署至具備 Nginx 反向代理與 HTTPS 憑證的 Linux 正式主機，將記憶體快取升級為 Redis 以支援多程序高併發，並導入自然語言處理 NLP 情緒與主題分類模型與負評即時預警。"
            "接下來，我們將直接進入第二階段的「網站建置與模擬鼠標操作實戰演示」，帶大家實際走一遍從建立網站到操作各項安全功能的完整流程！"
        )
    }
]
MANUAL_SCENES = [
    {
        "id": 13,
        "scene_type": "powershell",
        "title": "實戰演練 1：本機環境建置與網站啟動（local_server.py）",
        "mouse_path": [(400, 400), (750, 480), (900, 620), (1100, 700)],
        "click_times": [0.3, 0.7],
        "script": (
            "歡迎來到第二階段的網站操作手冊實戰影音演示。現在畫面中顯示的是 Windows PowerShell 操作終端機。"
            "依照操作手冊第一章與第二章規範，在全新本機環境建置時，我們首先進入 C 槽的 VOC_Sentry 專案目錄，建立 Python 虛擬環境並安裝 requirements.txt 依賴套件。"
            "接著，我們使用專屬的 local_server.py 啟動器，加上 --setup 參數初始化全新的 voc_sentry_local 資料庫；"
            "若資料庫已經存在，啟動器會自動拒絕覆寫，確保現有營運資料不會被誤刪。"
            "初始化完成後，請看鼠標移動的位置，我們執行 --check 參數檢查系統設定與資料庫遷移狀態，確認零錯誤後，再執行 --port 8000 啟動 Waitress 本機伺服器。"
            "此時系統會以 DEBUG 等於 False 的安全模式，僅綁定在 127.0.0.1 的本機迴路位址上運行。"
        )
    },
    {
        "id": 14,
        "scene_type": "dashboard",
        "title": "實戰演練 2：瀏覽 Dashboard 彙總與評分下鑽操作",
        "mouse_path": [(350, 380), (850, 500), (1180, 580), (1195, 620)],
        "click_times": [0.75],
        "script": (
            "網站啟動後，我們打開瀏覽器進入 http://127.0.0。"
            "依照操作手冊第 3.1 節，Dashboard 頁面允許匿名使用者直接瀏覽核准的彙總數據。"
            "畫面左側顯示通過資料驗證的總筆數為 1,476 筆，右側則呈現依台北時區統計的每月趨勢與評分分布長條圖。"
            "請注意看畫面上的白色鼠標，當我們想要進一步查看 8.0 分的詳細評論時，我們將鼠標移動到 8.0 分的長條上並點擊一下。"
            "由於匿名使用者不具備查看逐筆評論的權限，系統會立即啟動保護機制，將畫面自動導向登入頁面，並在網址列安全保留原本要查詢的 score 等於 8.0 參數。"
        )
    },
    {
        "id": 15,
        "scene_type": "login",
        "title": "實戰演練 3：帳號登入與最小權限群組驗證",
        "mouse_path": [(900, 480), (900, 570), (960, 675), (960, 675)],
        "click_times": [0.25, 0.5, 0.8],
        "script": (
            "現在畫面跳轉到了安全登入頁面。依照操作手冊第 3.2 節，本系統不開放公開自助註冊，所有帳號都必須由管理員在終端機透過 --create-admin 指令建立，"
            "並且加入核准的 Django 權限群組，例如 VOC_Analyst、Quality_Auditor 或 Compliance_Officer。"
            "在這裡要特別提醒，就算是系統的超級管理員 Superuser，如果沒有被加入對應的權限群組，依然無法繞過後端的明確權限檢查。"
            "請看鼠標依序點擊帳號與密碼欄位輸入資料，接著點擊藍色的「安全登入」按鈕。驗證通過並確認具備 view_approved_voc_fields 權限後，系統就會自動帶我們回到剛剛篩選的評論清單。"
        )
    },
    {
        "id": 16,
        "scene_type": "voc",
        "title": "實戰演練 4：VOC 白名單清單查詢與受限內文觸發",
        "mouse_path": [(450, 310), (1250, 470), (1320, 470), (1320, 470)],
        "click_times": [0.85],
        "script": (
            "登入成功後，我們現在位於 /voc/ 授權查詢清單頁面，畫面上已經自動篩選出評分為 8.0 分的評論。"
            "依照操作手冊第 3.3 節，一般登入者即使有查詢權限，API 回傳的欄位也受到嚴格的白名單限制：畫面中只會顯示評論日期、分數、國家、房型與旅客類型，"
            "資料庫主鍵 PK、來源編號 review_id 以及評論原文全部不會出現在清單中。"
            "因為我們目前登入的帳號同時具備核准欄位與受限欄位雙重權限，系統在每一列右側為我們產生了「檢視受限內文」的操作按鈕。"
            "現在我們將鼠標移動到第一筆評論右側的按鈕並點擊，觸發一次性短效權杖的驗證流程。"
        )
    },
    {
        "id": 17,
        "scene_type": "token",
        "title": "實戰演練 5：一次性權杖核銷與強制審計日誌",
        "mouse_path": [(600, 450), (800, 550), (850, 680), (700, 750)],
        "click_times": [0.4],
        "script": (
            "點擊按鈕後，前端透過受 CSRF 保護的 HTTP POST Body，將一次性拋棄式權杖傳送到後端的 /voc/restricted/ 端點。"
            "這組權杖由 CSPRNG 產生，有效期限只有 5 分鐘，嚴格綁定當下的登入 Session，而且只能消耗一次，絕對不會出現在網址列中。"
            "同時，前端完全不傳送 reason_code，而是由後端根據操作者所屬的 VOC_Analyst 群組，自動推導為 SUPPORT_CASE 原因碼。"
            "後端在讀取受限欄位前，會先將這次存取行為寫入 VOCRestrictedAuditLog 稽核資料表，確認審計寫入成功後，才會在畫面上解鎖顯示評論者姓名與完整評論原文。"
        )
    },
    {
        "id": 18,
        "scene_type": "image",
        "title": "實戰演練 6：圖片安全上傳、去識別化與浮水印展示",
        "mouse_path": [(450, 500), (800, 600), (1300, 620), (1400, 650)],
        "click_times": [0.35, 0.75],
        "script": (
            "最後我們來到操作手冊第 3.4 節的圖片安全功能，網址位於 /images/。"
            "當已登入使用者透過表單上傳 JPEG 或 PNG 圖片時，後端的 ImageProtectionService 會檢查二進位檔頭、檔案大小上限 5 MB 以及兩千萬像素上限，阻絕偽裝執行檔與像素炸彈。"
            "接著請看畫面左側與右側的對比：系統會將原始圖片以 UUID 隨機重新命名，隔離存放在私有的 backend/private_images 目錄中，只有具備 view_original_image 權限的人才能透過後端 API 讀取；"
            "而右側生成的公開展示圖，則會自動清除所有 GPS 與相機 EXIF 隱私資訊，縮放至長邊 1600 像素並合成「VOC Sentry」浮水印，確保圖片公開展示時的安全性。"
            "以上便是 VOC Sentry 完整的 20 分鐘系統架構開發說明與全功能實戰操作演示，感謝您的聆聽與觀看！"
        )
    }
]
def interpolate_mouse(path, progress):
    if len(path) < 2:
        return path
    total_segments = len(path) - 1
    scaled = progress * total_segments
    idx = min(int(scaled), total_segments - 1)
    local_t = scaled - idx
    smooth_t = local_t * local_t * (3 - 2 * local_t)
    x1, y1 = path[idx]
    x2, y2 = path[idx + 1]
    return int(x1 + (x2 - x1) * smooth_t), int(y1 + (y2 - y1) * smooth_t)

def format_srt_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def append_srt_entries(srt_entries, srt_idx, script, start_time, audio_duration):
    sentences = [s.strip() for s in script.replace("。", "。\n").split("\n") if s.strip()]
    total_chars = sum(len(s) for s in sentences)
    s_start = start_time
    for s in sentences:
        s_dur = audio_duration * (len(s) / total_chars)
        srt_entries.append(f"{srt_idx}\n{format_srt_time(s_start)} --> {format_srt_time(s_start + s_dur)}\n{s}\n")
        s_start += s_dur
        srt_idx += 1
    return srt_idx

async def build_20min_master_video():
    os.makedirs("output_20min/slides", exist_ok=True)
    os.makedirs("output_20min/audio", exist_ok=True)

    clips = []
    srt_entries = []
    current_timeline = 0.0
    srt_idx = 1

    print("🚀 開始全自動建置 VOC_Sentry 20 分鐘終極發表大作（共 18 幕）...")

    # 第一階段：生成 12 幕深度技術架構簡報片段
    for ch in SLIDE_CHAPTERS:
        cid = ch["id"]
        slide_path = f"output_20min/slides/slide_{cid:02d}.png"
        audio_path = f"output_20min/audio/part_{cid:02d}.mp3"

        print(f"🎨 [{cid:02d}/18] 生成技術簡報與語音：{ch['title']}")
        create_slide_image(cid, 12, ch["title"], ch["bullets"], slide_path)

        communicate = edge_tts.Communicate(ch["script"], VOICE, rate=RATE)
        await communicate.save(audio_path)

        audio_clip = AudioFileClip(audio_path)
        duration = audio_clip.duration + 0.8
        srt_idx = append_srt_entries(srt_entries, srt_idx, ch["script"], current_timeline, audio_clip.duration)

        video_clip = ImageClip(slide_path).with_duration(duration).with_audio(audio_clip)
        clips.append(video_clip)
        current_timeline += duration
        print(f"   ✅ 累計片長：{current_timeline/60:.2f} 分鐘")

    # 第二階段：無縫串接 6 幕模擬鼠標建站與全功能操作演示片段
    for sc in MANUAL_SCENES:
        sid = sc["id"]
        audio_path = f"output_20min/audio/part_{sid:02d}.mp3"

        print(f"🖱️ [{sid:02d}/18] 生成鼠標實戰操作與語音：{sc['title']}")
        communicate = edge_tts.Communicate(sc["script"], VOICE, rate=RATE)
        await communicate.save(audio_path)

        audio_clip = AudioFileClip(audio_path)
        duration = audio_clip.duration + 0.8
        srt_idx = append_srt_entries(srt_entries, srt_idx, sc["script"], current_timeline, audio_clip.duration)

        def make_frame(t, scene_data=sc, total_dur=duration):
            progress = min(1.0, max(0.0, t / total_dur))
            frame_img = render_demo_frame(scene_data["scene_type"], progress, scene_data["title"])
            draw = ImageDraw.Draw(frame_img)
            mx, my = interpolate_mouse(scene_data["mouse_path"], progress)
            clicking = any(abs(progress - ct) < 0.04 for ct in scene_data["click_times"])
            draw_cursor_and_click(draw, mx, my, is_clicking=clicking)
            return np.array(frame_img)

        video_clip = VideoClip(make_frame, duration=duration).with_audio(audio_clip)
        clips.append(video_clip)
        current_timeline += duration
        print(f"   ✅ 累計片長：{current_timeline/60:.2f} 分鐘")

    # 輸出統一時間軸的 20 分鐘完整繁體中文 SRT 字幕檔
    srt_output = "output_20min/VOC_Sentry_20min_Master.srt"
    with open(srt_output, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_entries))
    print(f"📝 完整 20 分鐘同步 SRT 字幕已生成：{srt_output}")

    # 自動串接並渲染最終 20 分鐘 MP4 終極發表大作（已啟用 ultrafast 加速）
    print("🎬 正在串接所有 18 幕片段並渲染最終 20 分鐘 MP4 影片，請稍候...")
    final_video = concatenate_videoclips(clips, method="compose")
    mp4_output = "output_20min/VOC_Sentry_20min_Master.mp4"
    final_video.write_videofile(
        mp4_output,
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        preset="ultrafast",
        threads=4
    )
    print(f"🎉 終極發表大作製作完成！最終總片長：{current_timeline/60:.2f} 分鐘")
    print(f"📁 最終影片檔案：{mp4_output}")

if __name__ == "__main__":
    asyncio.run(build_20min_master_video())
