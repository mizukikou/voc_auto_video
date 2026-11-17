import importlib.util
from PIL import Image, ImageDraw

_spec = importlib.util.spec_from_file_location("ve", "1_visual_engine.py")
_ve = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ve)
WIDTH, HEIGHT, F_H1, F_H2, F_BODY, F_SMALL, F_MONO = (
    _ve.WIDTH, _ve.HEIGHT, _ve.F_H1, _ve.F_H2, _ve.F_BODY, _ve.F_SMALL, _ve.F_MONO
)

def draw_cursor_and_click(draw, x, y, is_clicking=False):
    if is_clicking:
        draw.ellipse((x - 48, y - 48, x + 48, y + 48), outline=(244, 63, 94), width=3)
        draw.ellipse((x - 28, y - 28, x + 28, y + 28), outline=(251, 113, 133), width=4)
        draw.ellipse((x - 12, y - 12, x + 12, y + 12), fill=(244, 63, 94))
    else:
        draw.ellipse((x - 16, y - 16, x + 22, y + 22), outline=(56, 189, 248), width=2)

    pointer = [(x, y), (x, y + 38), (x + 11, y + 27), (x + 19, y + 44), (x + 25, y + 41), (x + 17, y + 24), (x + 30, y + 24)]
    draw.polygon(pointer, fill=(255, 255, 255), outline=(14, 165, 233))

def render_demo_frame(scene_type, progress, title):
    img = Image.new("RGB", (WIDTH, HEIGHT), color=(11, 17, 32))
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, WIDTH, 90), fill=(20, 30, 50))
    scan_x = int((WIDTH - 240) * ((progress * 2.5) % 1.0))
    draw.rectangle((scan_x, 86, scan_x + 240, 90), fill=(74, 222, 128))

    tag = "PART 2：GitHub 協作流程" if scene_type.startswith("git_") else "PART 3：網站建置與操作"
    draw.text((50, 22), f"{tag}  |  {title}", fill=(74, 222, 128), font=F_H2)

    if scene_type in ["powershell", "git_branch"]:
        draw.rectangle((120, 140, WIDTH - 120, HEIGHT - 80), fill=(10, 14, 23), outline=(56, 189, 248), width=3)
        draw.rectangle((120, 140, WIDTH - 120, 195), fill=(25, 36, 56))
        win_title = "VS Code Terminal - Git Feature Branch Workflow" if scene_type == "git_branch" else "Windows PowerShell - C:\\VOC_Sentry"
        draw.text((150, 152), win_title, fill=(56, 189, 248), font=F_SMALL)

        if scene_type == "git_branch":
            commands = [
                "PS C:\\VOC_Sentry> git checkout main && git pull origin main",
                "PS C:\\VOC_Sentry> git checkout -b feature/issue-43-score-filter-token",
                "Switched to a new branch 'feature/issue-43-score-filter-token'",
                "# 依循 Copilot 守則：僅實作 Issue #43 範圍，不擅改 Schema",
                "PS C:\\VOC_Sentry> python manage.py test --settings=config.test_settings",
                "Ran 114 tests in 4.82s - OK (Isolated Test DB Verified)",
                "PS C:\\VOC_Sentry> git add . && git commit -m \"feat(#43): add score filter & ephemeral token\"",
                "PS C:\\VOC_Sentry> git push -u origin feature/issue-43-score-filter-token"
            ]
        else:
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
        for idx, line in enumerate(commands[:visible_lines]):
            color = (74, 222, 128) if any(k in line for k in ["[OK]", "[INFO]", "OK", "Switched"]) else ((148, 163, 184) if line.startswith("#") else (248, 250, 252))
            cursor_blink = " _" if (idx == visible_lines - 1 and int(progress * 20) % 2 == 0) else ""
            draw.text((160, y), line + cursor_blink, fill=color, font=F_MONO)
            y += 65
        return img
    draw.rectangle((100, 130, WIDTH - 100, HEIGHT - 70), fill=(248, 250, 252), outline=(56, 189, 248), width=3)
    draw.rectangle((100, 130, WIDTH - 100, 200), fill=(226, 232, 240))
    urls = {
        "git_issue": "https://github.com",
        "git_pr": "https://github.com",
        "dashboard": "http://127.0.0",
        "login": "http://127.0.0",
        "voc": "http://127.0.0",
        "token": "http://127.0.0  (POST Body + CSRF)"
    }
    draw.rectangle((280, 145, WIDTH - 200, 185), fill=(255, 255, 255), outline=(203, 213, 225), width=2)
    draw.text((300, 152), urls[scene_type], fill=(51, 65, 85), font=F_SMALL)

    if scene_type == "git_issue":
        draw.rectangle((100, 200, WIDTH - 100, 270), fill=(36, 41, 47))
        draw.text((140, 218), "GitHub  |  mizukikou / VOC_Sentry   <> Code   (!) Issues   (Y) Pull requests", fill=(248, 250, 252), font=F_BODY)
        draw.rectangle((160, 300, WIDTH - 160, 860), fill=(255, 255, 255), outline=(203, 213, 225), width=2)
        draw.text((200, 325), "建立新 Issue：Issue #43 — 新增精確評分篩選與短效拋棄式權杖", fill=(15, 23, 42), font=F_H2)
        spec_lines = [
            "- 規格追溯：對齊 docs/api_contract.md v1.1 第 10.2 & 10.3 節",
            "- 開發範圍：GET /api/v1/voc/ 允許一位小數 score；POST /voc/restricted/ 核銷權杖",
            "- 安全邊界：權杖存於 LocMemCache (5分鐘有效)、禁止前端傳入 reason_code",
            "- 驗收條件 (DoD)：通過權限越界、重放攻擊與 Fail-Closed 審計自動化測試"
        ]
        sy = 410
        for sl in spec_lines:
            draw.text((200, sy), sl, fill=(51, 65, 85), font=F_BODY)
            sy += 65
        btn_c = (22, 163, 74) if progress > 0.65 else (34, 197, 94)
        draw.rectangle((WIDTH - 480, 750, WIDTH - 200, 815), fill=btn_c)
        draw.text((WIDTH - 445, 765), "Submit new issue", fill=(255, 255, 255), font=F_BODY)
        return img

    elif scene_type == "git_pr":
        draw.rectangle((100, 200, WIDTH - 100, 270), fill=(36, 41, 47))
        draw.text((140, 218), "GitHub  |  Pull Request #44 : feature/issue-43  ->  main", fill=(248, 250, 252), font=F_BODY)
        draw.rectangle((160, 300, WIDTH - 160, 860), fill=(255, 255, 255), outline=(203, 213, 225), width=2)
        draw.text((200, 325), "PR #44 審查與品質閘門檢查 (Quality Gate & Code Review)", fill=(15, 23, 42), font=F_H2)
        checks = [
            "[PASS] Preflight 安全預檢：無 Hardcoded Secret 與 .env 外洩",
            "[PASS] Migration Check：makemigrations --check 無未預期結構變更",
            "[PASS] Automated Regression：114 項整合測試全數通過 (隔離測試庫)",
            "[APPROVED] Team C & Team D 人工審查通過，符合 Issue #43 規格範圍"
        ]
        cy = 410
        for ck in checks:
            draw.text((200, cy), ck, fill=(22, 163, 74), font=F_BODY)
            cy += 65
        m_color = (126, 34, 206) if progress > 0.7 else (34, 197, 94)
        m_text = "Merged into main" if progress > 0.75 else "Confirm merge"
        draw.rectangle((200, 740, 520, 810), fill=m_color)
        draw.text((245, 757), m_text, fill=(255, 255, 255), font=F_BODY)
        return img

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
            "- 權杖驗證：CSPRNG Token 核銷成功 (LocMemCache 單次原子消耗)",
            "- 隱式原因碼：後端依群組自動推導為 SUPPORT_CASE (禁止前端傳入)",
            "- 強制審計：已寫入 VOCRestrictedAuditLog [ALLOW] (保留90天)",
            "------------------------------------------------------------------",
            "- 評論者 (PII)：王*明 (已通過雙權限授權顯示)",
            "- 評論原文：地點離捷運東門站非常近，公共空間乾淨且服務人員親切！"
        ]
        iy = 430
        for line in info:
            draw.text((410, iy), line, fill=(30, 41, 59), font=F_BODY)
            iy += 65
    return img
