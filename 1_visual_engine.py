import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT_BOLD = r"C:\Windows\Fonts\msjhbd.ttc"
FONT_REG = r"C:\Windows\Fonts\msjh.ttc"
FONT_MONO = r"C:\Windows\Fonts\consola.ttf"
WIDTH, HEIGHT = 1920, 1080

def load_fonts():
    try:
        return (
            ImageFont.truetype(FONT_BOLD, 46),
            ImageFont.truetype(FONT_BOLD, 34),
            ImageFont.truetype(FONT_REG, 26),
            ImageFont.truetype(FONT_REG, 22),
            ImageFont.truetype(FONT_MONO, 26),
        )
    except IOError:
        d = ImageFont.load_default()
        return d, d, d, d, d

F_H1, F_H2, F_BODY, F_SMALL, F_MONO = load_fonts()

def ease_out(t):
    t = min(1.0, max(0.0, t))
    return 1 - (1 - t) ** 3

def get_step(progress, ratios, total, fallback_end=0.92):
    if ratios and len(ratios) == total:
        return max(1, sum(1 for r in ratios if progress >= r))
    return max(1, min(total, int(min(0.999, progress / fallback_end) * total) + 1))

def draw_cyber_background(draw, progress):
    for gx in range(0, WIDTH, 80):
        draw.line((gx, 0, gx, HEIGHT), fill=(20, 32, 54), width=1)
    for gy in range(0, HEIGHT, 80):
        draw.line((0, gy, WIDTH, gy), fill=(20, 32, 54), width=1)
    cx, cy = WIDTH - 140, 120
    angle = progress * 360 * 3
    for r, col in [(48, (14, 165, 233)), (34, (139, 92, 246)), (18, (74, 222, 128))]:
        draw.arc((cx - r, cy - r, cx + r, cy + r), start=angle, end=angle + 220, fill=col, width=3)
        angle = -angle * 1.5
    draw.rectangle((45, 45, WIDTH - 45, HEIGHT - 45), outline=(30, 58, 138), width=3)
    draw.rectangle((45, 45, WIDTH - 45, 195), fill=(20, 30, 50))
    scan_x = int(45 + (WIDTH - 290) * ((progress * 2) % 1.0))
    draw.rectangle((scan_x, HEIGHT - 18, scan_x + 200, HEIGHT - 13), fill=(255, 45, 85))
    scan_x2 = int(WIDTH - 245 - (WIDTH - 290) * ((progress * 2) % 1.0))
    draw.rectangle((scan_x2, HEIGHT - 10, scan_x2 + 200, HEIGHT - 5), fill=(57, 255, 20))

def draw_flowing_arrow(draw, x1, y1, x2, y2, progress, col=(56, 189, 248)):
    draw.line((x1, y1, x2, y2), fill=(51, 65, 85), width=4)
    t = (progress * 4) % 1.0
    px, py = int(x1 + (x2 - x1) * t), int(y1 + (y2 - y1) * t)
    draw.ellipse((px - 7, py - 7, px + 7, py + 7), fill=col)
def draw_right_visual_chart(draw, chart_type, progress=1.0, r_ratios=None):
    rx1, ry1, rx2, ry2 = 1120, 240, 1845, 915
    draw.rectangle((rx1 - 3, ry1 - 3, rx2 + 3, ry2 + 3), outline=(30, 58, 138), width=2)
    draw.rectangle((rx1, ry1, rx2, ry2), fill=(17, 25, 43), outline=(56, 189, 248), width=2)

    if chart_type == "pain_points":
        draw.text((rx1 + 35, ry1 + 25), "市場痛點與 1,476 筆實證轉型", fill=(56, 189, 248), font=F_H2)
        bars = [
            ("台灣整體旅宿 OTA 依賴", 0.75, (245, 158, 11), 65, 80, "int_range"),
            ("獨立旅宿全球平均", 0.634, (56, 189, 248), 0, 63.4, "float"),
            ("大型連鎖飯店", 0.20, (168, 85, 247), 0, 20, "int_below")
        ]
        has_r = bool(r_ratios and len(r_ratios) >= 3)
        t_bar = float(r_ratios.__getitem__(0)) if has_r else 0.05
        t_pain = float(r_ratios.__getitem__(1)) if has_r else 0.35
        t_ok = float(r_ratios.__getitem__(2)) if has_r else 0.68
        by = ry1 + 100
        bar_anim = ease_out((progress - t_bar) / 0.18) if progress >= t_bar else 0.0
        for label, pct, col, v_min, v_max, fmt_type in bars:
            if fmt_type == "int_range":
                val_str = f"{int(v_min * bar_anim)}% - {int(v_max * bar_anim)}%"
            elif fmt_type == "float":
                val_str = f"{v_max * bar_anim:.1f}%"
            else:
                val_str = f"{int(v_max * bar_anim)}% 以下"
            draw.text((rx1 + 35, by), f"{label} ({val_str})", fill=(226, 232, 240), font=F_SMALL)
            draw.rectangle((rx1 + 35, by + 35, rx2 - 45, by + 65), fill=(30, 41, 59))
            fill_w = int((rx2 - rx1 - 80) * pct * bar_anim)
            if fill_w > 0:
                draw.rectangle((rx1 + 35, by + 35, rx1 + 35 + fill_w, by + 65), fill=col)
                draw.rectangle((rx1 + 35 + max(0, fill_w - 8), by + 35, rx1 + 35 + fill_w, by + 65), fill=(255, 255, 255))
            by += 95
        if progress >= t_pain:
            draw.rectangle((rx1 + 35, by + 20, rx2 - 35, by + 110), fill=(45, 20, 28), outline=(239, 68, 68), width=2)
            draw.text((rx1 + 60, by + 48), "痛點：人工讀不完 / 趨勢難察 / 含旅客個資", fill=(252, 165, 165), font=F_SMALL)
        if progress >= t_ok:
            draw.rectangle((rx1 + 35, by + 150, rx2 - 35, by + 240), fill=(15, 55, 38), outline=(74, 222, 128), width=3)
            draw.text((rx1 + 60, by + 178), "成果：東門3號青旅 1,476 筆評論安全落地", fill=(187, 247, 208), font=F_SMALL)

    elif chart_type == "docs_deliverables":
        draw.text((rx1 + 35, ry1 + 25), "已完成正式規格與 52 份資產清單", fill=(74, 222, 128), font=F_H2)
        docs = [("[完成] Requirements.md (v1.2)", "唯一需求基準與驗收門檻"), ("[完成] architecture.md (v1.1)", "模組化單體與安全邊界"), ("[完成] data_dictionary.md (v1.2)", "ABCD 核准欄位與唯一鍵"), ("[完成] api_contract.md (v1.1+#43)", "聚合 API 與一次性權杖"), ("[完成] testing_plan.md (v1.2)", "29 案追溯與品質閘門"), ("[完成] 網站操作手冊與新手教學", "52 份專案資產與交接指南"), ("[部分] Issue #43 手動瀏覽器驗證", "程式已合併，待補手動清單"), ("[未完] Linux + HTTPS 正式部署", "誠實標記為未來上線規劃")]
        visible_count = get_step(progress, r_ratios, len(docs))
        dy = ry1 + 85
        for idx, (name, desc) in enumerate(docs[:visible_count]):
            is_latest = (idx == visible_count - 1 and progress < 0.92)
            bg = (25, 55, 95) if is_latest else ((25, 36, 56) if "[完成]" in name else (45, 35, 22))
            border = (56, 189, 248) if is_latest else (51, 65, 85)
            draw.rectangle((rx1 + 30, dy, rx2 - 30, dy + 62), fill=bg, outline=border, width=2 if is_latest else 1)
            draw.text((rx1 + 45, dy + 15), name, fill=(248, 250, 252), font=F_SMALL)
            draw.text((rx1 + 420, dy + 15), desc, fill=(148, 163, 184), font=F_SMALL)
            dy += 70
    elif chart_type == "arch_diagram":
        draw.text((rx1 + 30, ry1 + 18), "Hybrid View 動態能量流與邊界架構圖", fill=(56, 189, 248), font=F_H2)
        draw.rectangle((rx1 + 30, ry1 + 65, rx2 - 30, ry1 + 102), fill=(25, 38, 62), outline=(56, 189, 248), width=1)
        draw.text(((rx1 + rx2) // 2, ry1 + 83), "運行環境：Python 3.14  |  Django 5.2  |  DRF 3.16  |  MySQL 8.0", fill=(125, 211, 252), font=F_SMALL, anchor="mm")

        boxes = [
            (rx1 + 95, ry1 + 118, rx2 - 95, ry1 + 166, "瀏覽器 End User (Bootstrap 5 + Chart.js)", (30, 58, 138)),
            (rx1 + 55, ry1 + 200, rx2 - 55, ry1 + 250, "Waitress WSGI (127.0.0.1:8000 | DEBUG=False)", (3, 105, 161)),
            (rx1 + 30, ry1 + 286, rx1 + 355, ry1 + 340, "Django Views (SSR HTML)", (15, 118, 110)),
            (rx1 + 370, ry1 + 286, rx2 - 30, ry1 + 340, "DRF API (最小必要 JSON)", (15, 118, 110)),
            (rx1 + 30, ry1 + 376, rx2 - 30, ry1 + 434, "Python 3.14 + Django 5.2 Core (權限/審計/影像)", (88, 28, 135)),
            (rx1 + 85, ry1 + 470, rx2 - 85, ry1 + 522, "Django ORM  ->  MySQL 8.0 (utf8mb4)", (153, 27, 27)),
            (rx1 + 30, ry1 + 560, rx2 - 30, ry1 + 628, "[邊界隔離] 離線 EDA：Pandas / Matplotlib (不進線上)", (55, 30, 20))
        ]
        visible_boxes = get_step(progress, r_ratios, len(boxes), 0.90)
        if visible_boxes >= 2:
            draw_flowing_arrow(draw, rx1 + 362, ry1 + 166, rx1 + 362, ry1 + 200, progress)
        if visible_boxes >= 4:
            draw_flowing_arrow(draw, rx1 + 362, ry1 + 250, rx1 + 192, ry1 + 286, progress)
            draw_flowing_arrow(draw, rx1 + 362, ry1 + 250, rx1 + 532, ry1 + 286, progress, (57, 255, 20))
        if visible_boxes >= 5:
            draw_flowing_arrow(draw, rx1 + 192, ry1 + 340, rx1 + 362, ry1 + 376, progress)
            draw_flowing_arrow(draw, rx1 + 532, ry1 + 340, rx1 + 362, ry1 + 376, progress, (57, 255, 20))
        if visible_boxes >= 6:
            draw_flowing_arrow(draw, rx1 + 362, ry1 + 434, rx1 + 362, ry1 + 470, progress, (74, 222, 128))
        for idx, (bx1, by1, bx2, by2, label, col) in enumerate(boxes[:visible_boxes]):
            b_outline = (245, 158, 11) if idx == 6 else (226, 232, 240)
            t_col = (253, 224, 71) if idx == 6 else (255, 255, 255)
            draw.rectangle((bx1, by1, bx2, by2), fill=col, outline=b_outline, width=2)
            draw.text(((bx1 + bx2) // 2, (by1 + by2) // 2), label, fill=t_col, font=F_SMALL, anchor="mm")

    elif chart_type == "er_model":
        draw.text((rx1 + 35, ry1 + 25), "MySQL 核心實體關聯圖 (ER Diagram)", fill=(56, 189, 248), font=F_H2)
        step = get_step(progress, r_ratios, 4, 0.85)
        if step >= 4:
            draw_flowing_arrow(draw, rx1 + 190, ry1 + 315, rx1 + 190, ry1 + 425, progress, (248, 113, 113))
            draw.text((rx1 + 202, ry1 + 322), "1", fill=(56, 189, 248), font=F_SMALL)
            draw.text((rx1 + 202, ry1 + 392), "N (target_id)", fill=(248, 113, 113), font=F_SMALL)

            draw_flowing_arrow(draw, rx1 + 385, ry1 + 305, rx1 + 345, ry1 + 425, progress, (251, 191, 36))
            draw.text((rx1 + 362, ry1 + 322), "1", fill=(56, 189, 248), font=F_SMALL)
            draw.text((rx1 + 365, ry1 + 362), "N (actor_id)", fill=(251, 191, 36), font=F_SMALL)

            draw_flowing_arrow(draw, rx1 + 545, ry1 + 315, rx1 + 545, ry1 + 425, progress, (74, 222, 128))
            draw.text((rx1 + 558, ry1 + 322), "1", fill=(56, 189, 248), font=F_SMALL)
            draw.text((rx1 + 558, ry1 + 392), "N (uploaded_by)", fill=(74, 222, 128), font=F_SMALL)

            draw.rectangle((rx1 + 385, ry1 + 95, rx2 - 35, ry1 + 315), fill=(25, 36, 56), outline=(56, 189, 248), width=2)
            draw.rectangle((rx1 + 385, ry1 + 95, rx2 - 35, ry1 + 135), fill=(15, 118, 110))
            draw.text((rx1 + 400, ry1 + 103), "auth_user (RBAC 帳號)", fill=(255, 255, 255), font=F_SMALL)
            for i, txt in enumerate(["PK: id (User ID)", "groups: VOC_Analyst", "is_superuser (不自動放行)", "Session 綁定驗證"]):
                draw.text((rx1 + 400, ry1 + 148 + i * 38), txt, fill=(226, 232, 240), font=F_SMALL)

        draw.rectangle((rx1 + 35, ry1 + 95, rx1 + 365, ry1 + 315), fill=(25, 36, 56), outline=(56, 189, 248), width=2)
        draw.rectangle((rx1 + 35, ry1 + 95, rx1 + 365, ry1 + 135), fill=(30, 58, 138))
        draw.text((rx1 + 50, ry1 + 103), "VOCReview (評論主表)", fill=(255, 255, 255), font=F_SMALL)
        for i, txt in enumerate(["PK: id (BigAutoField)", "UK: reviewer+date+title", "score: Decimal(3,1)", "PII: name / content"]):
            draw.text((rx1 + 50, ry1 + 148 + i * 38), txt, fill=(226, 232, 240), font=F_SMALL)

        if step >= 2:
            draw.rectangle((rx1 + 385, ry1 + 425, rx2 - 35, ry1 + 625), fill=(25, 36, 56), outline=(74, 222, 128), width=2)
            draw.rectangle((rx1 + 385, ry1 + 425, rx2 - 35, ry1 + 465), fill=(20, 83, 45))
            draw.text((rx1 + 400, ry1 + 433), "ImageAsset (影像資產)", fill=(255, 255, 255), font=F_SMALL)
            for i, txt in enumerate(["PK: uuid (私有原圖隔離)", "FK: uploaded_by_id", "展示圖去 EXIF + 浮水印"]):
                draw.text((rx1 + 400, ry1 + 478 + i * 42), txt, fill=(226, 232, 240), font=F_SMALL)

        if step >= 3:
            draw.rectangle((rx1 + 35, ry1 + 425, rx1 + 365, ry1 + 625), fill=(25, 36, 56), outline=(239, 68, 68), width=2)
            draw.rectangle((rx1 + 35, ry1 + 425, rx1 + 365, ry1 + 465), fill=(127, 29, 29))
            draw.text((rx1 + 50, ry1 + 433), "VOCRestrictedAuditLog", fill=(255, 255, 255), font=F_SMALL)
            for i, txt in enumerate(["PK: id | FK: actor / target", "reason_code (群組推導)", "Fail-Closed 強制寫入"]):
                draw.text((rx1 + 50, ry1 + 478 + i * 42), txt, fill=(226, 232, 240), font=F_SMALL)
    elif chart_type == "etl_pipeline":
        draw.text((rx1 + 35, ry1 + 25), "等冪 ETL 五階段雷射掃描管線", fill=(74, 222, 128), font=F_H2)
        steps = [("1. Extract (唯讀擷取)", "utf-8-sig 解碼去 BOM，SHA-256 雜湊前後不變"), ("2. Validate (結構檢驗)", "缺欄或錯誤列達 10% 觸發熔斷，整批拒收不寫半套"), ("3. Transform (精準清洗)", "stay_info 拆晚數日期，score 轉 Decimal(3,1)"), ("4. Deduplicate (複合去重)", "同鍵同內容跳過；同鍵異內容拒覆寫確保等冪"), ("5. Load (安全寫入)", "1,476 筆全數寫入 MySQL，拒絕 0 筆")]
        active_idx = get_step(progress, r_ratios, len(steps)) - 1
        sy = ry1 + 95
        for idx, (st, sd) in enumerate(steps[:active_idx + 1]):
            is_act = (idx == active_idx and progress < 0.92)
            bg, bd = ((16, 65, 48), (74, 222, 128)) if is_act else ((25, 36, 56), (56, 189, 248))
            draw.rectangle((rx1 + 45, sy, rx2 - 45, sy + 85), fill=bg, outline=bd, width=3 if is_act else 1)
            draw.text((rx1 + 65, sy + 12), ("▶ " if is_act else "") + st, fill=bd, font=F_SMALL)
            draw.text((rx1 + 65, sy + 46), sd, fill=(226, 232, 240), font=F_SMALL)
            sy += 110

    elif chart_type == "kpi_match":
        draw.text((rx1 + 35, ry1 + 25), "跨圖表數據血緣交叉驗證一致", fill=(56, 189, 248), font=F_H2)
        metrics = [("核心 KPI 通過驗證總數", 1476, (14, 165, 233)), ("37 個月份趨勢折線圖加總", 1476, (16, 185, 129)), ("9 個評分分布長條圖加總", 1476, (57, 255, 20))]
        vis_m = get_step(progress, r_ratios[:3] if r_ratios else None, 3, 0.72)
        t_sub = float(r_ratios.__getitem__(3)) if (r_ratios and len(r_ratios) >= 4) else 0.72
        my = ry1 + 110
        for idx, (m_name, val, col) in enumerate(metrics[:vis_m]):
            t_start = float(r_ratios.__getitem__(idx)) if (r_ratios and idx < len(r_ratios)) else idx * 0.2
            anim = ease_out((progress - t_start) / 0.14)
            draw.text((rx1 + 45, my), f"{m_name}：{int(1476 * anim):,} 筆", fill=(248, 250, 252), font=F_BODY)
            draw.rectangle((rx1 + 45, my + 42, rx2 - 45, my + 82), fill=(30, 41, 59))
            fill_w = int((rx2 - rx1 - 90) * anim)
            if fill_w > 0:
                draw.rectangle((rx1 + 45, my + 42, rx1 + 45 + fill_w, my + 82), fill=col)
                draw.rectangle((rx1 + 45 + max(0, fill_w - 8), my + 42, rx1 + 45 + fill_w, my + 82), fill=(255, 255, 255))
            if anim > 0.9:
                draw.text((rx1 + 65, my + 48), "100% 吻合 (台北時區 UTC+8 半開區間換算驗證)", fill=(255, 255, 255), font=F_SMALL)
            my += 125
        if progress >= t_sub:
            draw.rectangle((rx1 + 45, my + 10, rx2 - 45, my + 110), fill=(15, 55, 38), outline=(74, 222, 128), width=2)
            draw.text((rx1 + 65, my + 42), "特定月份抽測 (2023-10)：41 = 41 = 41 完全一致", fill=(74, 222, 128), font=F_SMALL)

    elif chart_type == "security_shield":
        draw.text((rx1 + 35, ry1 + 25), "零信任權杖與強制審計四道防線", fill=(248, 113, 113), font=F_H2)
        layers = [("防線 1：RBAC 明確權限", "區分已登入與有權限，Superuser 未授權亦攔截"), ("防線 2：CSPRNG 拋棄式權杖", "存於 LocMemCache，5 分鐘效期、綁定 Session、單次核銷"), ("防線 3：隱式原因碼推導", "禁止前端傳 reason_code (傳入回 400)，後端依群組推導"), ("防線 4：Fail-Closed 審計", "先寫入 AuditLog ALLOW 才顯示原文，失敗立即阻斷")]
        vis_l = get_step(progress, r_ratios, len(layers))
        ly = ry1 + 100
        for idx, (l_title, l_desc) in enumerate(layers[:vis_l]):
            is_act = (idx == vis_l - 1 and progress < 0.92)
            draw.rectangle((rx1 + 45, ly, rx2 - 45, ly + 115), fill=(68, 26, 34) if is_act else (48, 22, 28), outline=(252, 165, 165) if is_act else (239, 68, 68), width=3 if is_act else 2)
            draw.text((rx1 + 65, ly + 18), l_title, fill=(252, 165, 165), font=F_BODY)
            draw.text((rx1 + 65, ly + 62), l_desc, fill=(226, 232, 240), font=F_SMALL)
            ly += 138

    elif chart_type == "qa_metrics":
        draw.text((rx1 + 35, ry1 + 25), "自動化品質閘門與多維度測試證據", fill=(74, 222, 128), font=F_H2)
        cards = [(103, "項", "本機交付回歸與 Migration 漂移檢查通過", (16, 185, 129)), (75, "項", "Issue #40 合成 CSV 到 Dashboard 整合通過", (57, 255, 20)), (114, "項", "Issue #43 權限與權杖自動化測試全數通過", (14, 165, 233)), (29, "案", "需求追溯矩陣完整追蹤 (隔離測試庫零污染)", (245, 158, 11))]
        vis_c = get_step(progress, r_ratios, len(cards))
        cy = ry1 + 100
        for idx, (target_num, unit, desc, col) in enumerate(cards[:vis_c]):
            t_start = float(r_ratios.__getitem__(idx)) if (r_ratios and idx < len(r_ratios)) else idx * 0.2
            anim = ease_out((progress - t_start) / 0.12)
            draw.rectangle((rx1 + 45, cy, rx1 + 195, cy + 105), fill=col)
            draw.text((rx1 + 58, cy + 32), f"{int(target_num * anim)} {unit}", fill=(255, 255, 255), font=F_H2)
            draw.rectangle((rx1 + 195, cy, rx2 - 45, cy + 105), fill=(25, 36, 56), outline=col, width=2)
            draw.text((rx1 + 212, cy + 38), desc, fill=(248, 250, 252), font=F_SMALL)
            cy += 132

def render_slide_frame_array(part_num, total_parts, title, bullets, chart_type, progress, trigger_ratios=None, right_ratios=None):
    img = Image.new("RGB", (WIDTH, HEIGHT), color=(11, 17, 32))
    draw = ImageDraw.Draw(img)
    draw_cyber_background(draw, progress)
    draw.rectangle((45, 45, 72, 195), fill=(56, 189, 248))
    draw.text((100, 72), f"PART 1：系統架構與完整交付成果  |  SLIDE {part_num:02d} / {total_parts}", fill=(56, 189, 248), font=F_SMALL)
    draw.text((100, 115), title, fill=(248, 250, 252), font=F_H1)

    visible_cards = get_step(progress, trigger_ratios, len(bullets))
    y_offset = 240
    for idx, bullet in enumerate(bullets[:visible_cards]):
        is_newest = (idx == visible_cards - 1 and progress < 0.92)
        draw.rectangle((80, y_offset, 1090, y_offset + 140), fill=(26, 42, 68) if is_newest else (22, 33, 54), outline=(56, 189, 248) if is_newest else (51, 65, 85), width=3 if is_newest else 2)
        draw.rectangle((80, y_offset, 92, y_offset + 140), fill=(74, 222, 128) if is_newest else (14, 165, 233))
        draw.text((125, y_offset + 52), bullet, fill=(255, 255, 255) if is_newest else (226, 232, 240), font=F_BODY)
        y_offset += 170

    draw_right_visual_chart(draw, chart_type, progress=progress, r_ratios=right_ratios)
    overall_prog = ((part_num - 1) + progress) / 16.0
    draw.rectangle((45, HEIGHT - 122, WIDTH - 45, HEIGHT - 116), fill=(30, 41, 59))
    draw.rectangle((45, HEIGHT - 122, int(45 + (WIDTH - 90) * overall_prog), HEIGHT - 116), fill=(56, 189, 248))
    draw.text((90, HEIGHT - 95), "VOC_Sentry 旅宿顧客評論分析與安全查詢平台  |  動態圖表化技術架構與實戰發表", fill=(148, 163, 184), font=F_SMALL)
    draw.text((WIDTH - 230, HEIGHT - 95), f"Slide {part_num:02d} / {total_parts}", fill=(56, 189, 248), font=F_SMALL)
    return np.array(img)

