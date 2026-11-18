import importlib.util
from PIL import Image, ImageDraw

_spec = importlib.util.spec_from_file_location("ve", "1_visual_engine.py")
_ve = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ve)
WIDTH, HEIGHT, F_H1, F_H2, F_BODY, F_SMALL, F_MONO, get_step = (
    _ve.WIDTH, _ve.HEIGHT, _ve.F_H1, _ve.F_H2, _ve.F_BODY, _ve.F_SMALL, _ve.F_MONO, _ve.get_step
)

def draw_cursor_and_click(draw, x, y, is_clicking=False):
    if is_clicking:
        draw.ellipse((x - 48, y - 48, x + 48, y + 48), outline=(255, 45, 85), width=3)
        draw.ellipse((x - 28, y - 28, x + 28, y + 28), outline=(255, 90, 120), width=4)
        draw.ellipse((x - 12, y - 12, x + 12, y + 12), fill=(255, 45, 85))
    else:
        draw.ellipse((x - 16, y - 16, x + 22, y + 22), outline=(57, 255, 20), width=2)
    pointer = [(x, y), (x, y + 38), (x + 11, y + 27), (x + 19, y + 44), (x + 25, y + 41), (x + 17, y + 24), (x + 30, y + 24)]
    draw.polygon(pointer, fill=(255, 255, 255), outline=(14, 165, 233))

def render_demo_frame(scene_type, progress, title, d_ratios=None):
    img = Image.new("RGB", (WIDTH, HEIGHT), color=(11, 17, 32))
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, WIDTH, 90), fill=(20, 30, 50))
    scan_x = int((WIDTH - 240) * ((progress * 2.5) % 1.0))
    draw.rectangle((scan_x, HEIGHT - 18, scan_x + 240, HEIGHT - 13), fill=(255, 45, 85))
    scan_x2 = int(WIDTH - 240 - (WIDTH - 240) * ((progress * 2.5) % 1.0))
    draw.rectangle((scan_x2, HEIGHT - 10, scan_x2 + 240, HEIGHT - 5), fill=(57, 255, 20))
    tag = "PART 2：GitHub 協作流程" if scene_type.startswith("git_") else "PART 3：網站建置與操作"
    draw.text((50, 22), f"{tag}  |  {title}", fill=(57, 255, 20), font=F_H2)

    if scene_type == "git_issue":
        draw.rectangle((140, 130, WIDTH - 140, 910), fill=(13, 17, 23), outline=(48, 54, 61), width=2)
        draw.text((180, 165), "GitHub / VOC_Sentry / Issues / New Issue (#43)", fill=(139, 148, 158), font=F_SMALL)
        draw.rectangle((180, 220, WIDTH - 180, 290), fill=(22, 27, 34), outline=(56, 189, 248), width=2)
        draw.text((200, 238), "feat(#43): 新增精確評分篩選與短效拋棄式權杖", fill=(240, 246, 252), font=F_BODY)
        draw.rectangle((180, 315, WIDTH - 180, 740), fill=(22, 27, 34), outline=(48, 54, 61), width=2)
        groups = [
            ["### 1. 規格追溯 (Spec Traceability)", "- 依據 docs/api_contract.md v1.1 第 10.2 & 10.3 節實作"],
            ["### 2. 開發邊界 (Scope & Non-Goals)", "- 僅修改 /api/v1/voc/ 評分篩選與 /restricted/ 核銷端點"],
            ["### 3. 安全紅線 (Security Invariants)", "- Token 存於 LocMemCache，TTL=300秒，單次核銷即原子銷毀", "- 禁止前端傳入 reason_code (傳入回 400)，後端依群組自動推導"],
            ["### 4. 完成定義 (Definition of Done)", "- 通過越界存取、重放攻擊、過期失效與 Fail-Closed 審計測試"]
        ]
        vis_g = get_step(progress, d_ratios, len(groups), 0.78)
        ly = 340
        for grp in groups[:vis_g]:
            for line in grp:
                col = (56, 189, 248) if line.startswith("###") else (201, 209, 217)
                draw.text((205, ly), line, fill=col, font=F_SMALL)
                ly += 42
        btn_col = (46, 160, 67) if progress > 0.78 else (35, 134, 54)
        draw.rectangle((WIDTH - 450, 765, WIDTH - 180, 830), fill=btn_col)
        draw.text((WIDTH - 415, 782), "Submit new issue", fill=(255, 255, 255), font=F_BODY)

    elif scene_type == "git_branch":
        draw.rectangle((120, 130, WIDTH - 120, 910), fill=(12, 16, 26), outline=(56, 189, 248), width=2)
        draw.rectangle((120, 130, WIDTH - 120, 185), fill=(30, 41, 59))
        draw.text((150, 145), "VS Code Terminal - Git Feature Branch Workflow", fill=(148, 163, 184), font=F_SMALL)
        groups = [
            ["PS C:\\VOC_Sentry> git checkout main && git pull origin main"],
            ["PS C:\\VOC_Sentry> git checkout -b feature/issue-43-score-filter-token", "Switched to a new branch 'feature/issue-43-score-filter-token'"],
            ["# 依循 Copilot 守則：僅實作 Issue #43 範圍，不擅改 Schema"],
            ["PS C:\\VOC_Sentry> python manage.py test --settings=config.test_settings", "Ran 114 tests in 4.82s - OK (Isolated Test DB Verified)"],
            ["PS C:\\VOC_Sentry> git add . && git commit -m \"feat(#43): add score filter & ephemeral token\"", "PS C:\\VOC_Sentry> git push -u origin feature/issue-43-score-filter-token"]
        ]
        vis_g = get_step(progress, d_ratios, len(groups), 0.85)
        ty = 220
        for grp in groups[:vis_g]:
            for line in grp:
                if "OK" in line:
                    col = (57, 255, 20)
                    draw.rectangle((145, ty - 8, WIDTH - 145, ty + 38), fill=(15, 55, 38), outline=(57, 255, 20), width=2)
                    draw.ellipse((160, ty + 3, 184, ty + 27), fill=(57, 255, 20), outline=(255, 255, 255), width=2)
                    draw.text((198, ty), line, fill=col, font=F_MONO)
                    ty += 56
                    continue
                elif line.startswith("#"):
                    draw.text((155, ty), line, fill=(148, 163, 184), font=F_SMALL)
                    ty += 50
                    continue
                elif "Switched" in line:
                    col = (74, 222, 128)
                else:
                    col = (226, 232, 240)
                draw.text((155, ty), line, fill=col, font=F_MONO)
                ty += 50
    elif scene_type == "git_pr":
        draw.rectangle((140, 130, WIDTH - 140, 910), fill=(13, 17, 23), outline=(48, 54, 61), width=2)
        draw.text((180, 165), "Pull Request #44: feature/issue-43 -> main", fill=(240, 246, 252), font=F_H2)
        draw.rectangle((180, 225, 330, 270), fill=(35, 134, 54) if progress < 0.78 else (137, 87, 229))
        draw.text((215, 234), "Open" if progress < 0.78 else "Merged", fill=(255, 255, 255), font=F_BODY)
        checks = [
            "[PASS] Preflight Check：敏感金鑰與 .env 隔離檢查通過",
            "[PASS] Migration Check：makemigrations --check --dry-run 零漂移",
            "[PASS] Automated Test Suite：114 項單元與整合測試全數通過",
            "[APPROVED] Code Review：成員 C 與成員 D 雙重審查通過"
        ]
        vis_c = get_step(progress, d_ratios, len(checks), 0.72)
        cy = 310
        for chk in checks[:vis_c]:
            draw.rectangle((180, cy, WIDTH - 180, cy + 75), fill=(22, 27, 34), outline=(46, 160, 67), width=2)
            draw.ellipse((202, cy + 25, 226, cy + 49), fill=(57, 255, 20), outline=(255, 255, 255), width=2)
            draw.text((240, cy + 22), chk, fill=(57, 255, 20), font=F_BODY)
            cy += 95
        if vis_c >= 4:
            draw.rectangle((180, 740, 540, 810), fill=(46, 160, 67))
            draw.text((235, 758), "Confirm merge", fill=(255, 255, 255), font=F_BODY)

    elif scene_type == "powershell":
        draw.rectangle((120, 130, WIDTH - 120, 910), fill=(1, 36, 86), outline=(56, 189, 248), width=3)
        draw.rectangle((120, 130, WIDTH - 120, 185), fill=(15, 23, 42))
        draw.text((150, 145), "Windows PowerShell - VOC_Sentry Local Server Setup", fill=(248, 250, 252), font=F_SMALL)
        groups = [
            ["PS C:\\VOC_Sentry> python -m venv .venv && .\\.venv\\Scripts\\Activate.ps1", "PS C:\\VOC_Sentry> pip install -r requirements.txt"],
            ["PS C:\\VOC_Sentry> python local_server.py setup", "[OK] 建立全新 MySQL 資料庫、套用 Migrations 與初始化 RBAC 群組 (防呆保護已啟用)"],
            ["PS C:\\VOC_Sentry> python local_server.py check", "System check identified no issues (0 silenced)."],
            ["PS C:\\VOC_Sentry> python local_server.py runserver --port 8000", "[RUNNING] Waitress WSGI 伺服器已於 http://127.0.0.1:8000 安全啟動 (DEBUG=False)"]
        ]
        vis_g = get_step(progress, d_ratios, len(groups), 0.85)
        ty = 220
        for grp in groups[:vis_g]:
            for line in grp:
                if "[OK]" in line or "[RUNNING]" in line or "0 silenced" in line:
                    col = (57, 255, 20)
                    draw.ellipse((145, ty + 4, 167, ty + 26), fill=(57, 255, 20))
                    line_font = F_SMALL if ("[OK]" in line or "[RUNNING]" in line) else F_MONO
                    draw.text((180, ty), line, fill=col, font=line_font)
                else:
                    draw.text((155, ty), line, fill=(255, 255, 255), font=F_MONO)
                ty += 52

    elif scene_type == "dashboard":
        draw.rectangle((100, 120, WIDTH - 100, 920), fill=(248, 250, 252), outline=(148, 163, 184), width=2)
        draw.rectangle((100, 120, WIDTH - 100, 185), fill=(30, 41, 59))
        draw.text((140, 138), "http://127.0.0.1:8000  -  VOC_Sentry 旅宿顧客評論分析儀表板 (訪客公開視圖)", fill=(248, 250, 252), font=F_SMALL)
        draw.rectangle((150, 225, 580, 410), fill=(255, 255, 255), outline=(203, 213, 225), width=2)
        draw.text((180, 250), "通過驗證評論總數 (Verified)", fill=(100, 116, 139), font=F_SMALL)
        draw.text((180, 305), "1,476 筆", fill=(14, 165, 233), font=F_H1)
        draw.rectangle((150, 440, 580, 625), fill=(255, 255, 255), outline=(203, 213, 225), width=2)
        draw.text((180, 465), "整體平均評分 (Mean Score)", fill=(100, 116, 139), font=F_SMALL)
        draw.text((180, 520), "8.6 分", fill=(16, 185, 129), font=F_H1)
        draw.rectangle((620, 225, WIDTH - 150, 860), fill=(255, 255, 255), outline=(203, 213, 225), width=2)
        draw.text((660, 255), "各分數區間分布圖 (點擊 8.0 分長條執行下鑽查詢)", fill=(30, 41, 59), font=F_BODY)
        scores = [("10.0", 290), ("9.0", 380), ("8.0", 420), ("7.0", 210), ("6.0", 120)]
        bx = 700
        for sc, h in scores:
            col = (245, 158, 11) if sc == "8.0" else (59, 130, 246)
            draw.rectangle((bx, 780 - h, bx + 95, 780), fill=col)
            draw.text((bx + 20, 795), sc, fill=(51, 65, 85), font=F_SMALL)
            bx += 140

    elif scene_type == "login":
        draw.rectangle((100, 120, WIDTH - 100, 920), fill=(241, 245, 249))
        draw.rectangle((620, 240, 1300, 780), fill=(255, 255, 255), outline=(203, 213, 225), width=2)
        draw.text((680, 290), "VOC_Sentry 系統安全登入 (無公開註冊)", fill=(15, 23, 42), font=F_H2)
        draw.text((680, 355), "重新導向目標：/voc/?score=8.0 (保留篩選參數)", fill=(14, 165, 233), font=F_SMALL)
        draw.rectangle((680, 425, 1240, 495), fill=(248, 250, 252), outline=(148, 163, 184), width=2)
        draw.text((705, 445), "analyst_tw_01 (RBAC 群組：VOC_Analyst)" if progress > 0.45 else "請輸入授權帳號...", fill=(30, 41, 59), font=F_BODY)
        draw.rectangle((680, 525, 1240, 595), fill=(248, 250, 252), outline=(148, 163, 184), width=2)
        draw.text((705, 545), "••••••••••••••••" if progress > 0.55 else "請輸入密碼...", fill=(30, 41, 59), font=F_BODY)
        draw.rectangle((680, 635, 1240, 710), fill=(14, 165, 233))
        draw.text((885, 655), "安全登入", fill=(255, 255, 255), font=F_BODY)

    elif scene_type == "voc":
        draw.rectangle((100, 120, WIDTH - 100, 920), fill=(248, 250, 252))
        draw.text((140, 155), "VOC 評論白名單查詢清單 (篩選條件：score = 8.0 | 隱藏內部主鍵與姓名)", fill=(15, 23, 42), font=F_BODY)
        draw.rectangle((140, 220, WIDTH - 140, 285), fill=(30, 41, 59))
        draw.text((175, 238), "評論日期 (UTC)          評分(有權限顯示連結底線)      旅客國家          入住房型              旅客類型", fill=(255, 255, 255), font=F_SMALL)
        rows = [
            ("2026-10-15T08:20:00Z", "8.0", "Taiwan", "混合宿舍床位", "獨行旅客"),
            ("2026-10-12T14:05:00Z", "8.0", "Japan", "女性專屬六人房", "獨行旅客"),
            ("2026-10-09T11:40:00Z", "8.0", "Korea", "雙人標準房", "情侶/雙人")
        ]
        vis_step = get_step(progress, d_ratios, 2, 0.6)
        ry = 310
        for idx, (dt_str, sc_str, country, room, guest_type) in enumerate(rows):
            draw.rectangle((140, ry, WIDTH - 140, ry + 75), fill=(255, 255, 255), outline=(226, 232, 240), width=1)
            draw.text((175, ry + 22), dt_str, fill=(51, 65, 85), font=F_SMALL)
            if vis_step >= 2:
                link_col = (220, 38, 38) if (idx == 0 and progress > 0.78) else (2, 132, 199)
                draw.text((485, ry + 22), sc_str, fill=link_col, font=F_BODY)
                draw.line((485, ry + 52, 525, ry + 52), fill=link_col, width=3)
            else:
                draw.text((485, ry + 22), sc_str, fill=(51, 65, 85), font=F_BODY)
            draw.text((740, ry + 22), country, fill=(51, 65, 85), font=F_SMALL)
            draw.text((925, ry + 22), room, fill=(51, 65, 85), font=F_SMALL)
            draw.text((1165, ry + 22), guest_type, fill=(51, 65, 85), font=F_SMALL)
            ry += 95

    elif scene_type == "token":
        draw.rectangle((100, 120, WIDTH - 100, 920), fill=(15, 23, 42), outline=(56, 189, 248), width=2)
        draw.text((140, 155), "受限內文核銷與強制審計紀錄 (POST + CSRF + 拋棄式 Token)", fill=(56, 189, 248), font=F_H2)
        draw.rectangle((150, 230, WIDTH - 150, 460), fill=(30, 41, 59), outline=(74, 222, 128), width=2)
        draw.text((185, 255), "一次性 Token 核銷成功 (已從 LocMemCache 原子銷毀，重放請求將回傳 403)", fill=(74, 222, 128), font=F_SMALL)
        draw.text((185, 305), "旅客姓名 (PII)：陳*明  |  入住資訊：2 晚 · 2023 年 10 月", fill=(248, 250, 252), font=F_BODY)
        draw.text((185, 365), "評論完整原文：地點離捷運東門站非常近，公共交誼廳很乾淨，下次來台北還會入住。", fill=(226, 232, 240), font=F_BODY)
        draw.rectangle((150, 500, WIDTH - 150, 860), fill=(25, 36, 56), outline=(245, 158, 11), width=2)
        draw.text((185, 525), "強制審計紀錄 (VOCRestrictedAuditLog - Fail-Closed 寫入確認)", fill=(251, 191, 36), font=F_BODY)
        audits = [
            "• 調閱人員 (Actor)：analyst_tw_01 (群組自動推導 reason_code = SUPPORT_CASE)",
            "• 目標評論 (Target)：VOCReview #1042 (單次檢視授權，禁止批次匯出)",
            "• 稽核狀態 (Outcome)：ALLOW (已寫入不可否認審計日誌，若寫入失敗則阻斷顯示)",
            "• 影像安全管理同步生效：原圖 UUID 私有隔離 / 公開展示圖已去 EXIF 並加浮水印"
        ]
        vis_a = get_step(progress, d_ratios, len(audits), 0.80)
        ay = 585
        for a in audits[:vis_a]:
            draw.text((185, ay), a, fill=(226, 232, 240), font=F_SMALL)
            ay += 55
    return img
