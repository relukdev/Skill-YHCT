#!/usr/bin/env python3
"""
yhct_consult.py — AI Thăm khám Y học Cổ truyền + TĐĐVCS
Sử dụng: python yhct_consult.py [--mode chat|analyze|report]
"""

import sys
import os
import json
from datetime import datetime

# ─────────────────────────────────────────────
# KNOWLEDGE BASE — Nhúng trực tiếp để offline
# ─────────────────────────────────────────────

BAT_CUONG_RULES = {
    "duong_hu": {
        "keywords": ["sợ lạnh", "tay chân lạnh", "thích ấm", "thích nước ấm",
                     "mặt trắng", "môi nhợt", "tiểu trong", "tiểu dài",
                     "phân lỏng", "lưỡi nhợt", "rêu trắng", "mạch trầm", "mạch trì"],
        "label": "Dương hư (Hàn chứng)",
        "treatment_principle": "Bổ Dương, ôn kinh tán hàn",
        "technique": "Rung + Bỉ nhẹ",
        "spa_therapy": "Xông hơi ấm 40–42°C, Moxa"
    },
    "am_hu": {
        "keywords": ["nóng buốt", "chiều tối", "mồ hôi trộm", "thích lạnh",
                     "thích nước lạnh", "khô miệng", "tiểu vàng", "tiểu ít",
                     "táo bón", "lưỡi đỏ", "ít rêu", "không rêu", "mạch tế", "mạch sác"],
        "label": "Âm hư (Nhiệt chứng)",
        "treatment_principle": "Bổ Âm, thanh hư nhiệt",
        "technique": "Xoay nhẹ + Bỉ",
        "spa_therapy": "Xông hơi mát 35–37°C, massage nhẹ"
    },
    "hu_chung": {
        "keywords": ["mệt mỏi", "giọng yếu", "chán ăn", "người gầy",
                     "bệnh lâu", "mãn tính", "mạch nhược", "hụt hơi"],
        "label": "Hư chứng",
        "treatment_principle": "Bổ hư, phù chính",
        "technique": "Rung + Bỉ",
        "spa_therapy": "Massage nhẹ nhàng, bổ huyệt"
    },
    "thuc_chung": {
        "keywords": ["đau tăng khi ấn", "bụng cứng", "người mập",
                     "bệnh mới", "cấp tính", "mạch hữu lực", "đau dữ dội"],
        "label": "Thực chứng",
        "treatment_principle": "Tả thực, khu tà",
        "technique": "Đẩy + Bật + Gua Sha",
        "spa_therapy": "Gua Sha, massage mạnh"
    }
}

ORGAN_MAP = {
    "CAN": {
        "element": "Mộc", "pair": "Đởm",
        "keywords": ["cáu kỉnh", "tức giận", "đau đầu bên", "mắt đỏ", "mắt khô",
                     "cơ cổ vai căng", "móng giòn", "kinh không đều", "stress"],
        "acupoints": "LR3 (Thái Xung), GB34 (Dương Lăng Tuyền)",
        "pattern": "Can khí uất kết / Can Dương vượng"
    },
    "TAM": {
        "element": "Hỏa", "pair": "Tiểu Trường",
        "keywords": ["mất ngủ", "hồi hộp", "lo âu", "hay quên",
                     "đánh trống ngực", "đầu lưỡi đỏ", "tim đập nhanh"],
        "acupoints": "HT7 (Thần Môn), PC6 (Nội Quan)",
        "pattern": "Tâm Thận bất giao / Tâm huyết hư"
    },
    "TY": {
        "element": "Thổ", "pair": "Vị",
        "keywords": ["chán ăn", "chướng bụng", "cơ thể nặng", "tiêu lỏng",
                     "hay lo lắng", "môi nhợt", "tay chân mỏi"],
        "acupoints": "SP6 (Tam Âm Giao), ST36 (Túc Tam Lý)",
        "pattern": "Tỳ khí hư / Tỳ Vị hư hàn"
    },
    "PHE": {
        "element": "Kim", "pair": "Đại Trường",
        "keywords": ["ho", "khó thở", "da khô", "hay buồn", "dễ cảm",
                     "mũi khô", "ngạt mũi", "giọng khàn"],
        "acupoints": "LU7 (Liệt Khuyết), LI11 (Khúc Trì)",
        "pattern": "Phế khí hư / Phế Âm hư"
    },
    "THAN": {
        "element": "Thủy", "pair": "Bàng Quang",
        "keywords": ["đau lưng", "tiểu đêm", "ù tai", "yếu sinh lý",
                     "đầu gối yếu", "tóc rụng", "hay sợ hãi", "lưng mỏi"],
        "acupoints": "KI3 (Thái Khê), BL23 (Thận Du), GV4 (Mệnh Môn)",
        "pattern": "Thận Âm hư / Thận Dương hư"
    }
}

VERTEBRA_MAP = {
    "đau đầu": ["C1", "C2", "C3"],
    "chóng mặt": ["C1", "C2", "D1"],
    "mất ngủ": ["C1", "D1", "D9"],
    "huyết áp": ["C5", "C6", "C7", "D1"],
    "cổ gáy": ["C4", "C5", "C6", "C7"],
    "cổ vai": ["C5", "C6", "D1", "D2"],
    "tê tay": ["C5", "C6", "D1", "D2"],
    "ho": ["C3", "C4", "D2", "D3"],
    "khó thở": ["D2", "D3", "D4", "D5"],
    "đau ngực": ["D2", "D3", "D4", "D5"],
    "dạ dày": ["D6", "D7", "D8", "D9"],
    "chướng bụng": ["D8", "D9", "D10"],
    "mệt mỏi": ["D1", "D9", "L1"],
    "sợ lạnh": ["D1", "L1", "L2"],
    "đau lưng": ["L1", "L2", "L3", "L4", "L5"],
    "thắt lưng": ["L1", "L2", "L3", "L4", "L5"],
    "thần kinh tọa": ["L3", "L4", "L5", "S1", "S2"],
    "tê chân": ["L3", "L4", "L5"],
    "kinh nguyệt": ["C7", "D10", "D12", "L3", "S1"],
    "tiểu đêm": ["D11", "D12", "L1", "L2"],
    "đau thận": ["D11", "D12", "L1", "L2"],
    "cáu kỉnh": ["C1", "C2", "D1", "D5"],
    "stress": ["C1", "D1", "D9"],
}

ABSOLUTE_CONTRAINDICATIONS = [
    "đang châm cứu", "vừa châm cứu", "gãy xương", "da lở loét",
    "vết thương hở", "sốt cao", "bệnh lây nhiễm", "ung thư cột sống",
    "di căn xương", "phẫu thuật cột sống", "thoát vị đĩa đệm cấp"
]

RED_FLAGS = [
    "đau cột sống kèm sốt không rõ", "sụt cân không rõ nguyên nhân",
    "yếu liệt tiến triển nhanh", "đau đầu dữ dội đột ngột",
    "đau ngực khó thở vã mồ hôi", "nói ngọng méo miệng",
    "tiểu đại tiện không kiểm soát"
]

CAUTIONS = [
    "mang thai", "huyết áp cao", "loãng xương", "thuốc chống đông"
]

# ─────────────────────────────────────────────
# CORE FUNCTIONS
# ─────────────────────────────────────────────

def check_safety(text: str) -> dict:
    """Kiểm tra an toàn — ưu tiên tuyệt đối."""
    t = text.lower()
    absolute = [c for c in ABSOLUTE_CONTRAINDICATIONS if c in t]
    red_flags = [r for r in RED_FLAGS if r in t]
    cautions = [c for c in CAUTIONS if c in t]

    if absolute:
        return {
            "level": "STOP",
            "message": f"🚫 CHỐNG CHỈ ĐỊNH TUYỆT ĐỐI: {', '.join(absolute)}. KHÔNG thực hiện TĐĐVCS.",
            "action": "Dừng ngay. Giải thích lý do. Hướng dẫn đến bác sĩ."
        }
    if red_flags:
        return {
            "level": "URGENT_REFER",
            "message": f"🔴 CỜ ĐỎ phát hiện: {', '.join(red_flags)}. Cần gặp bác sĩ NGAY.",
            "action": "Không tiếp tục thăm khám. Chuyển bác sĩ khẩn cấp."
        }
    if cautions:
        return {
            "level": "CAUTION",
            "message": f"⚠️ Thận trọng: {', '.join(cautions)}. Cần điều chỉnh kỹ thuật.",
            "action": "Tiếp tục nhưng giảm lực, theo dõi sát."
        }
    return {"level": "SAFE", "message": "✅ An toàn để tiến hành.", "action": "Tiếp tục thăm khám."}


def analyze_bat_cuong(symptoms: list[str]) -> dict:
    """Phân tích Bát Cương từ danh sách triệu chứng."""
    text = " ".join(symptoms).lower()
    scores = {k: 0 for k in BAT_CUONG_RULES}

    for rule_key, rule in BAT_CUONG_RULES.items():
        for kw in rule["keywords"]:
            if kw in text:
                scores[rule_key] += 1

    # Xác định Âm/Dương (ngưỡng linh hoạt theo số triệu chứng)
    if scores["duong_hu"] >= 1 and scores["duong_hu"] > scores["am_hu"]:
        am_duong = "duong_hu"
    elif scores["am_hu"] >= 1 and scores["am_hu"] > scores["duong_hu"]:
        am_duong = "am_hu"
    elif scores["duong_hu"] == scores["am_hu"] and scores["duong_hu"] >= 1:
        am_duong = "duong_hu"  # Mặc định Hu khi bằng nhau
    else:
        am_duong = "binh_thuong"

    # Xác định Hư/Thực
    if scores["hu_chung"] >= 1 and scores["hu_chung"] > scores["thuc_chung"]:
        hu_thuc = "hu_chung"
    elif scores["thuc_chung"] >= 1 and scores["thuc_chung"] > scores["hu_chung"]:
        hu_thuc = "thuc_chung"
    else:
        hu_thuc = "binh_thuong"

    # Biểu/Lý dựa trên thời gian (heuristic)
    bieu_ly = "ly_chung" if any(w in text for w in ["lâu", "mãn", "tháng", "năm"]) else "bieu_chung"

    result = {
        "am_duong": am_duong,
        "hu_thuc": hu_thuc,
        "bieu_ly": bieu_ly,
        "scores": scores,
        "primary_pattern": BAT_CUONG_RULES.get(am_duong, {}).get("label", "Chưa xác định"),
        "treatment_principle": BAT_CUONG_RULES.get(am_duong, {}).get("treatment_principle", ""),
        "technique": BAT_CUONG_RULES.get(am_duong, {}).get("technique", "Xoay + Bỉ"),
        "spa_therapy": BAT_CUONG_RULES.get(am_duong, {}).get("spa_therapy", "Massage nhẹ")
    }
    return result


def identify_organs(symptoms: list[str]) -> list[dict]:
    """Xác định tạng phủ bị ảnh hưởng."""
    text = " ".join(symptoms).lower()
    organ_scores = []

    for organ, data in ORGAN_MAP.items():
        score = sum(1 for kw in data["keywords"] if kw in text)
        if score > 0:
            organ_scores.append({
                "organ": organ,
                "element": data["element"],
                "score": score,
                "acupoints": data["acupoints"],
                "pattern": data["pattern"]
            })

    return sorted(organ_scores, key=lambda x: x["score"], reverse=True)


def map_vertebrae(symptoms: list[str]) -> dict:
    """Ánh xạ triệu chứng → đốt sống TĐĐVCS."""
    text = " ".join(symptoms).lower()
    found = {}

    for kw, vertebrae in VERTEBRA_MAP.items():
        if kw in text:
            for v in vertebrae:
                found[v] = found.get(v, 0) + 1

    # Sắp xếp theo tần suất
    sorted_v = sorted(found.items(), key=lambda x: x[1], reverse=True)
    all_vertebrae = [v for v, _ in sorted_v]

    # Nhóm theo vùng
    zones = {
        "co": [v for v in all_vertebrae if v.startswith("C")],
        "lung": [v for v in all_vertebrae if v.startswith("D")],
        "that_lung": [v for v in all_vertebrae if v.startswith("L")],
        "cung_cut": [v for v in all_vertebrae if v.startswith("S")]
    }

    return {
        "all_vertebrae": all_vertebrae,
        "zones": zones,
        "primary_zone": _get_primary_zone(zones),
        "frequency_map": dict(sorted_v)
    }


def _get_primary_zone(zones: dict) -> str:
    zone_names = {"co": "Cổ (C)", "lung": "Lưng (D)", "that_lung": "Thắt lưng (L)", "cung_cut": "Cùng cụt (S)"}
    max_zone = max(zones, key=lambda z: len(zones[z]))
    return zone_names.get(max_zone, "Chưa xác định") if zones[max_zone] else "Chưa xác định"


def calculate_confidence(symptom_count: int, questions_answered: int,
                          has_tongue: bool = False, has_pulse: bool = False) -> int:
    score = 40
    if symptom_count >= 5: score += 15
    elif symptom_count >= 3: score += 10
    if questions_answered >= 8: score += 20
    elif questions_answered >= 5: score += 10
    if has_tongue: score += 15
    if has_pulse: score += 10
    return min(score, 95)


def generate_report(patient_info: dict, bat_cuong: dict, organs: list,
                    vertebrae: dict, safety: dict, confidence: int) -> str:
    """Tạo báo cáo thăm khám dạng Markdown."""
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    top_organ = organs[0] if organs else {"organ": "Chưa xác định", "element": "—", "acupoints": "—", "pattern": "—"}

    # Kế hoạch điều trị
    v_list = ", ".join(vertebrae["all_vertebrae"][:8]) if vertebrae["all_vertebrae"] else "Chưa xác định"
    organ_list = "\n".join([f"  - **{o['organ']}** ({o['element']}): {o['pattern']} — Huyệt: {o['acupoints']}"
                             for o in organs[:3]]) if organs else "  - Chưa xác định"

    report = f"""# PHIẾU THĂM KHÁM YHCT + TĐĐVCS
**Ngày:** {now} | **Confidence:** {confidence}%

---

## THÔNG TIN
- **Họ tên:** {patient_info.get('name', 'Không cung cấp')}
- **Tuổi/Giới:** {patient_info.get('age', '—')} / {patient_info.get('gender', '—')}
- **Triệu chứng chính:** {patient_info.get('chief_complaint', '—')}
- **Thời gian bệnh:** {patient_info.get('duration', '—')}

---

## CHẨN ĐOÁN YHCT

### Bát Cương
| Cặp | Kết quả |
|-----|---------|
| Âm / Dương | **{bat_cuong.get('primary_pattern', '—')}** |
| Biểu / Lý | **{bat_cuong.get('bieu_ly', '—').replace('_', ' ').title()}** |
| Hư / Thực | **{bat_cuong.get('hu_thuc', '—').replace('_', ' ').title()}** |

**Nguyên tắc điều trị:** {bat_cuong.get('treatment_principle', '—')}

### Ngũ Hành — Tạng Phủ
{organ_list}

---

## KẾ HOẠCH TĐĐVCS

**Đốt sống trọng điểm:** {v_list}  
**Vùng chính:** {vertebrae.get('primary_zone', '—')}  
**Kỹ thuật:** {bat_cuong.get('technique', '—')}  
**Liệu pháp bổ trợ:** {bat_cuong.get('spa_therapy', '—')}

---

## HUYỆT VỊ
{top_organ.get('acupoints', '—')}

---

## LƯU Ý AN TOÀN
{safety.get('message', '✅ An toàn')}

---

> ⚠️ **Tuyên bố pháp lý:** Kết quả này chỉ mang tính hỗ trợ tham khảo, không thay thế chẩn đoán của bác sĩ YHCT có chứng chỉ hành nghề.
"""
    return report


# ─────────────────────────────────────────────
# INTERACTIVE CLI
# ─────────────────────────────────────────────

def run_interactive_consultation():
    """Chạy thăm khám tương tác qua terminal."""
    print("\n" + "="*60)
    print("  AI THĂM KHÁM Y HỌC CỔ TRUYỀN + TĐĐVCS")
    print("  Phiên bản 1.0 | Manus AI")
    print("="*60)
    print("\n⚠️  Lưu ý: Chỉ hỗ trợ tham khảo, không thay thế bác sĩ.\n")

    # Thu thập thông tin
    name = input("1. Họ tên (hoặc Enter để bỏ qua): ").strip() or "Khách"
    age = input("2. Tuổi: ").strip() or "—"
    gender = input("3. Giới tính (Nam/Nữ): ").strip() or "—"
    chief_complaint = input("4. Triệu chứng chính bạn đang gặp: ").strip()
    duration = input("5. Triệu chứng này kéo dài bao lâu? ").strip() or "—"

    print("\n--- Hỏi thêm để chẩn đoán chính xác hơn ---")
    q6 = input("6. Bạn có sợ lạnh, tay chân lạnh không? (có/không): ").strip()
    q7 = input("7. Bạn có nóng buốt về chiều tối, ra mồ hôi trộm không? (có/không): ").strip()
    q8 = input("8. Bạn có mệt mỏi, chán ăn, cơ thể nặng nề không? (có/không): ").strip()
    q9 = input("9. Bạn có cáu kỉnh, stress, đau đầu bên không? (có/không): ").strip()
    q10 = input("10. Bạn có mất ngủ, hồi hộp, lo âu không? (có/không): ").strip()

    # Tổng hợp triệu chứng
    all_symptoms = [chief_complaint, duration]
    if "có" in q6.lower(): all_symptoms.extend(["sợ lạnh", "tay chân lạnh"])
    if "có" in q7.lower(): all_symptoms.extend(["nóng buốt", "chiều tối", "mồ hôi trộm"])
    if "có" in q8.lower(): all_symptoms.extend(["mệt mỏi", "chán ăn", "cơ thể nặng"])
    if "có" in q9.lower(): all_symptoms.extend(["cáu kỉnh", "stress", "đau đầu bên"])
    if "có" in q10.lower(): all_symptoms.extend(["mất ngủ", "hồi hộp", "lo âu"])

    questions_answered = sum(1 for q in [q6, q7, q8, q9, q10] if q.strip())

    print("\n⏳ Đang phân tích...\n")

    # Phân tích
    safety = check_safety(" ".join(all_symptoms))
    if safety["level"] == "STOP":
        print(safety["message"])
        print(f"\n→ Hành động: {safety['action']}")
        return

    bat_cuong = analyze_bat_cuong(all_symptoms)
    organs = identify_organs(all_symptoms)
    vertebrae = map_vertebrae(all_symptoms)
    confidence = calculate_confidence(len(all_symptoms), questions_answered + 5)

    patient_info = {"name": name, "age": age, "gender": gender,
                    "chief_complaint": chief_complaint, "duration": duration}

    report = generate_report(patient_info, bat_cuong, organs, vertebrae, safety, confidence)

    print(report)

    # Lưu báo cáo
    save = input("\nLưu báo cáo ra file? (có/không): ").strip()
    if "có" in save.lower():
        filename = f"yhct_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"✅ Đã lưu: {filename}")


def analyze_from_text(text: str) -> dict:
    """Phân tích từ văn bản mô tả triệu chứng — dùng cho tích hợp."""
    symptoms = text.split(",") if "," in text else [text]
    safety = check_safety(text)
    bat_cuong = analyze_bat_cuong(symptoms)
    organs = identify_organs(symptoms)
    vertebrae = map_vertebrae(symptoms)
    confidence = calculate_confidence(len(symptoms), len(symptoms))

    return {
        "safety": safety,
        "bat_cuong": bat_cuong,
        "organs": organs[:3],
        "vertebrae": vertebrae,
        "confidence": confidence,
        "summary": f"{bat_cuong['primary_pattern']} | {organs[0]['organ'] if organs else '—'} | Đốt: {', '.join(vertebrae['all_vertebrae'][:5])}"
    }


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "chat"

    if mode == "analyze" and len(sys.argv) > 2:
        # Phân tích nhanh từ command line
        text = " ".join(sys.argv[2:])
        result = analyze_from_text(text)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif mode == "demo":
        # Demo với ca bệnh mẫu
        demo_symptoms = ["đau lưng", "mất ngủ", "sợ lạnh", "mệt mỏi", "tiểu đêm"]
        print("=== DEMO: Phân tích ca bệnh mẫu ===")
        print(f"Triệu chứng: {', '.join(demo_symptoms)}\n")
        result = analyze_from_text(", ".join(demo_symptoms))
        patient_info = {"name": "Demo", "age": "45", "gender": "Nam",
                        "chief_complaint": "đau lưng + mất ngủ", "duration": "3 tháng"}
        report = generate_report(patient_info, result["bat_cuong"], result["organs"],
                                  result["vertebrae"], result["safety"], result["confidence"])
        print(report)
    else:
        # Chế độ thăm khám tương tác
        run_interactive_consultation()
