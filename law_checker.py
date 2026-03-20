# ============================================================
#  Copyright (c) 2024 (주)아이팝엔지니어링
#  법령 변경 알림 스크립트 - law_checker.py
#  GitHub Actions에 의해 매월 1일 자동 실행
# ============================================================

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# ── 설정 ──────────────────────────────────────────────────────
GMAIL_USER = os.environ.get("GMAIL_USER", "")
GMAIL_PASS = os.environ.get("GMAIL_PASS", "")
RECIPIENT  = "gunbon21@gmail.com"
TODAY      = datetime.now().strftime("%Y년 %m월 %d일")
YEAR       = datetime.now().year

# ── 45개 항목 정의 ─────────────────────────────────────────────
ITEMS = [
    {"no": 1,  "name": "구조 성능기반설계",                      "law": "내진설계 지침",                              "link": "https://www.law.go.kr"},
    {"no": 2,  "name": "설계안전보건대장",                        "law": "건설기술진흥법 시행령 / 안전보건대장 고시",     "link": "https://www.law.go.kr/lsSc.do?query=건설기술진흥법"},
    {"no": 3,  "name": "단지내 주변일조·일영분석",                "law": "건축법 제61조",                              "link": "https://www.law.go.kr/lsSc.do?query=건축법"},
    {"no": 4,  "name": "단지특화디자인(색채 등)",                 "law": "건축심의 기준",                              "link": "https://www.law.go.kr"},
    {"no": 5,  "name": "소규모 지하안전영향평가",                  "law": "지하안전관리에 관한 특별법",                   "link": "https://www.law.go.kr/lsSc.do?query=지하안전관리"},
    {"no": 6,  "name": "지하안전영향평가",                        "law": "지하안전관리에 관한 특별법",                   "link": "https://www.law.go.kr/lsSc.do?query=지하안전관리"},
    {"no": 7,  "name": "착공후 지하안전영향평가",                  "law": "지하안전관리에 관한 특별법",                   "link": "https://www.law.go.kr/lsSc.do?query=지하안전관리"},
    {"no": 8,  "name": "현황측량(지장물조사)",                    "law": "지하안전 관련 규정",                          "link": "https://www.law.go.kr"},
    {"no": 9,  "name": "지질조사",                               "law": "지하안전 매뉴얼",                             "link": "https://www.law.go.kr"},
    {"no": 10, "name": "흙막이 설계",                            "law": "건축법 시행령",                              "link": "https://www.law.go.kr/lsSc.do?query=건축법+시행령"},
    {"no": 11, "name": "수량산출서",                             "law": "주택법",                                    "link": "https://www.law.go.kr/lsSc.do?query=주택법"},
    {"no": 12, "name": "단지내 소음예측평가",                     "law": "주택건설기준 등에 관한 규정 제9조",             "link": "https://www.law.go.kr/lsSc.do?query=주택건설기준"},
    {"no": 13, "name": "범죄예방 건축기준",                       "law": "건축법 제53조의2",                           "link": "https://www.law.go.kr/lsSc.do?query=건축법"},
    {"no": 14, "name": "에너지절약설계기준",                      "law": "녹색건축물 조성 지원법",                       "link": "https://www.law.go.kr/lsSc.do?query=녹색건축물"},
    {"no": 15, "name": "수질오염물질 총량제",                     "law": "물환경보전법",                               "link": "https://www.law.go.kr/lsSc.do?query=물환경보전법"},
    {"no": 16, "name": "녹색건축인증",                           "law": "녹색건축물 조성 지원법",                       "link": "https://www.law.go.kr/lsSc.do?query=녹색건축물"},
    {"no": 17, "name": "제로에너지건축물 인증",                   "law": "녹색건축물 조성 지원법",                       "link": "https://www.law.go.kr/lsSc.do?query=녹색건축물"},
    {"no": 18, "name": "에너지절약형 친환경주택",                  "law": "주택건설기준 등에 관한 규정 제64조",            "link": "https://www.law.go.kr/lsSc.do?query=주택건설기준"},
    {"no": 19, "name": "건강친화형 주택 건설기준",                 "law": "주택건설기준 등에 관한 규정 제65조",            "link": "https://www.law.go.kr/lsSc.do?query=주택건설기준"},
    {"no": 20, "name": "공동주택 결로 방지 설계",                  "law": "주택건설기준 등에 관한 규정 제14조",            "link": "https://www.law.go.kr/lsSc.do?query=주택건설기준"},
    {"no": 21, "name": "장수명 주택 건설인증",                    "law": "주택건설기준 등에 관한 규정 제65조",            "link": "https://www.law.go.kr/lsSc.do?query=주택건설기준"},
    {"no": 22, "name": "교육환경평가서",                          "law": "교육환경 보호에 관한 법률 제28조",              "link": "https://www.law.go.kr/lsSc.do?query=교육환경+보호"},
    {"no": 23, "name": "에너지소비 총량제(ECO2)",                 "law": "건축물 에너지효율등급 인증 기준",               "link": "https://www.law.go.kr"},
    {"no": 24, "name": "제로에너지건축물 (공공) ※17번 병합",      "law": "녹색건축물 조성 지원법",                       "link": "https://www.law.go.kr/lsSc.do?query=녹색건축물"},
    {"no": 25, "name": "건축물의 경관심의대상",                    "law": "경관법 / 대전광역시 경관조례",                  "link": "https://www.law.go.kr/lsSc.do?query=경관법"},
    {"no": 26, "name": "성능위주 소방설계",                       "law": "소방시설 설치 및 관리에 관한 법률",             "link": "https://www.law.go.kr/lsSc.do?query=소방시설"},
    {"no": 27, "name": "풍동실험",                               "law": "건축구조기준(KBC)",                          "link": "https://www.law.go.kr"},
    {"no": 28, "name": "건축물 교통영향평가",                     "law": "도시교통정비 촉진법",                          "link": "https://www.law.go.kr/lsSc.do?query=도시교통정비"},
    {"no": 29, "name": "장애물 없는 생활환경(BF) 인증",           "law": "교통약자의 이동편의 증진법",                    "link": "https://www.law.go.kr/lsSc.do?query=교통약자"},
    {"no": 30, "name": "에너지사용계획 협의",                     "law": "에너지이용 합리화법",                          "link": "https://www.law.go.kr/lsSc.do?query=에너지이용+합리화"},
    {"no": 31, "name": "건축물 안전영향평가",                     "law": "건축법 제13조의2",                           "link": "https://www.law.go.kr/lsSc.do?query=건축법"},
    {"no": 32, "name": "사전재난영향성검토",                      "law": "초고층 및 지하연계 복합건축물 재난관리에 관한 특별법", "link": "https://www.law.go.kr/lsSc.do?query=초고층+재난"},
    {"no": 33, "name": "개발사업의 경관심의대상",                  "law": "경관법 시행령",                              "link": "https://www.law.go.kr/lsSc.do?query=경관법"},
    {"no": 34, "name": "지구단위계획구역 지정",                    "law": "국토의 계획 및 이용에 관한 법률",               "link": "https://www.law.go.kr/lsSc.do?query=국토계획법"},
    {"no": 35, "name": "지구단위계획변경",                        "law": "국토의 계획 및 이용에 관한 법률",               "link": "https://www.law.go.kr/lsSc.do?query=국토계획법"},
    {"no": 36, "name": "사전경관계획 심의",                       "law": "경관법 시행령",                              "link": "https://www.law.go.kr/lsSc.do?query=경관법"},
    {"no": 37, "name": "문화재지표조사",                          "law": "국가유산영향진단법",                           "link": "https://www.law.go.kr/lsSc.do?query=국가유산"},
    {"no": 38, "name": "소규모 재해영향평가",                     "law": "자연재해대책법",                              "link": "https://www.law.go.kr/lsSc.do?query=자연재해대책법"},
    {"no": 39, "name": "재해영향평가",                           "law": "자연재해대책법",                              "link": "https://www.law.go.kr/lsSc.do?query=자연재해대책법"},
    {"no": 40, "name": "환경영향평가",                           "law": "환경영향평가법",                              "link": "https://www.law.go.kr/lsSc.do?query=환경영향평가법"},
    {"no": 41, "name": "소규모 환경영향평가",                     "law": "환경영향평가법",                              "link": "https://www.law.go.kr/lsSc.do?query=환경영향평가법"},
    {"no": 42, "name": "지하철(철도) 영향성 검토",                "law": "철도안전법",                                  "link": "https://www.law.go.kr/lsSc.do?query=철도안전법"},
    {"no": 43, "name": "민간건축물 녹색건축 설계기준 [대전]",      "law": "대전광역시 조례",                             "link": "https://www.daejeon.go.kr/law/"},
    {"no": 44, "name": "건축물 경관심의 [대전]",                  "law": "대전광역시 경관조례",                          "link": "https://www.daejeon.go.kr/law/"},
    {"no": 45, "name": "범죄예방 도시디자인(CPTED) [대전]",       "law": "대전광역시 CPTED 조례",                       "link": "https://www.daejeon.go.kr/law/"},
]

# ── 이메일 HTML 생성 ───────────────────────────────────────────
def build_email_html():
    rows = ""
    for item in ITEMS:
        is_dj = "[대전]" in item["name"]
        bg = "#F3FFF8" if is_dj else "#FFFFFF"
        rows += f"""
        <tr style='background:{bg};'>
            <td style='padding:7px 10px;border:1px solid #ddd;text-align:center;color:#555;'>{item['no']}</td>
            <td style='padding:7px 10px;border:1px solid #ddd;font-weight:{"bold" if is_dj else "normal"};'>{item['name']}</td>
            <td style='padding:7px 10px;border:1px solid #ddd;font-size:12px;color:#555;'>{item['law']}</td>
            <td style='padding:7px 10px;border:1px solid #ddd;text-align:center;'>
                <a href='{item["link"]}' style='color:#0052CC;font-size:12px;'>법령 확인 →</a>
            </td>
        </tr>"""

    html = f"""
    <html><body style='font-family:Malgun Gothic,sans-serif;max-width:860px;margin:auto;'>
    <div style='background:#0052CC;color:white;padding:20px 25px;border-radius:8px 8px 0 0;'>
        <h2 style='margin:0;font-size:20px;'>📋 사업승인 체크리스트 법령 변경 확인 알림</h2>
        <p style='margin:6px 0 0;opacity:0.85;font-size:14px;'>{TODAY} | (주)아이팝엔지니어링 자동 발송</p>
    </div>
    <div style='background:#FFF8E1;border-left:4px solid #FFA000;padding:15px 20px;margin:0;'>
        <b>⚠️ 이번 달 법령 변경 여부를 직접 확인해 주세요!</b><br>
        <span style='font-size:13px;color:#555;'>아래 45개 항목의 근거 법령 링크를 클릭하여 최근 개정 여부를 확인하시기 바랍니다.<br>
        변경 사항 발견 시 <b>app.py</b>를 업데이트해 주세요.</span>
    </div>
    <div style='padding:15px 20px;background:#E3F2FD;font-size:13px;'>
        📌 <b>국가법령정보센터:</b>
        <a href='https://www.law.go.kr' style='color:#0052CC;margin-left:8px;'>www.law.go.kr →</a>
        &nbsp;&nbsp;|&nbsp;&nbsp;
        📌 <b>대전광역시 자치법규:</b>
        <a href='https://www.daejeon.go.kr/law/' style='color:#0052CC;margin-left:8px;'>daejeon.go.kr/law →</a>
    </div>
    <table style='width:100%;border-collapse:collapse;font-size:13px;'>
        <thead>
            <tr style='background:#0052CC;color:white;'>
                <th style='padding:10px;border:1px solid #ddd;width:40px;'>No</th>
                <th style='padding:10px;border:1px solid #ddd;'>항목명</th>
                <th style='padding:10px;border:1px solid #ddd;'>근거 법령</th>
                <th style='padding:10px;border:1px solid #ddd;width:90px;'>법령 확인</th>
            </tr>
        </thead>
        <tbody>{rows}</tbody>
    </table>
    <div style='margin-top:15px;padding:10px 20px;background:#F5F5F5;border-radius:4px;font-size:11px;color:#999;text-align:center;'>
        Copyright © {YEAR} (주)아이팝엔지니어링 &nbsp;|&nbsp; 사업승인 체크리스트 Web v8.0 &nbsp;|&nbsp; 매월 1일 자동 발송
    </div>
    </body></html>
    """
    return html

# ── 이메일 발송 ────────────────────────────────────────────────
def send_email():
    subject = f"[사업승인 체크리스트] {TODAY} 법령 변경 확인 알림 (45개 항목)"
    html_body = build_email_html()
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = GMAIL_USER
    msg["To"]      = RECIPIENT
    msg.attach(MIMEText(html_body, "html", "utf-8"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_PASS)
        server.sendmail(GMAIL_USER, RECIPIENT, msg.as_string())
    print(f"✅ 이메일 발송 완료 → {RECIPIENT}")

# ── 메인 실행 ──────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"[{TODAY}] 법령 변경 알림 이메일 발송 시작...")
    send_email()
    print("완료!")
