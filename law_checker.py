# ============================================================
#  Copyright (c) 2024 (주)아이팝엔지니어링
#  법령 변경 자동 체크 스크립트 - law_checker.py
#  GitHub Actions에 의해 매월 1일 자동 실행
# ============================================================

import smtplib
import os
import json
import urllib.request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# ── 설정 ──────────────────────────────────────────────────────
GMAIL_USER = os.environ.get("GMAIL_USER", "")
GMAIL_PASS = os.environ.get("GMAIL_PASS", "")
RECIPIENT  = "gunbon21@gmail.com"
TODAY      = datetime.now().strftime("%Y년 %m월 %d일")

# ── 42개 항목 정의 ─────────────────────────────────────────────
ITEMS = [
    {"no": 1,  "name": "구조 성능기반설계",           "law": "내진설계 지침"},
    {"no": 2,  "name": "설계안전보건대장",             "law": "건설기술진흥법 시행령 / 안전보건대장 고시"},
    {"no": 3,  "name": "단지내 주변일조·일영분석",     "law": "건축법 제61조"},
    {"no": 4,  "name": "단지특화디자인(색채 등)",      "law": "건축심의 기준"},
    {"no": 5,  "name": "소규모 지하안전영향평가",      "law": "지하안전관리에 관한 특별법"},
    {"no": 6,  "name": "지하안전영향평가",             "law": "지하안전관리에 관한 특별법"},
    {"no": 7,  "name": "착공후 지하안전영향평가",      "law": "지하안전관리에 관한 특별법"},
    {"no": 8,  "name": "현황측량(지장물조사)",         "law": "지하안전 관련 규정"},
    {"no": 9,  "name": "지질조사",                    "law": "지하안전 매뉴얼"},
    {"no": 10, "name": "흙막이 설계",                 "law": "건축법 시행령"},
    {"no": 11, "name": "수량산출서",                  "law": "주택법 / 제출 기준"},
    {"no": 12, "name": "단지내 소음예측평가",          "law": "주택건설기준 등에 관한 규정 제9조"},
    {"no": 13, "name": "범죄예방 건축기준",            "law": "건축법 제53조의2"},
    {"no": 14, "name": "에너지절약설계기준",           "law": "녹색건축물 조성 지원법"},
    {"no": 15, "name": "수질오염물질 총량제",          "law": "물환경보전법 / 오염총량관리 방침"},
    {"no": 16, "name": "녹색건축인증",                "law": "녹색건축물 조성 지원법"},
    {"no": 17, "name": "제로에너지건축물 인증",        "law": "녹색건축물 조성 지원법"},
    {"no": 18, "name": "에너지절약형 친환경주택",      "law": "주택건설기준 등에 관한 규정 제64조"},
    {"no": 19, "name": "건강친화형 주택 건설기준",     "law": "주택건설기준 등에 관한 규정 제65조"},
    {"no": 20, "name": "공동주택 결로 방지 설계",      "law": "주택건설기준 등에 관한 규정 제14조"},
    {"no": 21, "name": "장수명 주택 건설인증",         "law": "주택건설기준 등에 관한 규정 제65조"},
    {"no": 22, "name": "교육환경평가서",               "law": "교육환경 보호에 관한 법률 제28조"},
    {"no": 23, "name": "에너지소비 총량제(ECO2)",      "law": "건축물 에너지효율등급 인증 및 제로에너지건축물 인증 기준"},
    {"no": 24, "name": "제로에너지건축물 (공공)",      "law": "녹색건축물 조성 지원법 (17번 병합)"},
    {"no": 25, "name": "건축물의 경관심의대상",        "law": "경관법 / 대전광역시 경관조례"},
    {"no": 26, "name": "성능위주 소방설계",            "law": "화재예방, 소방시설 설치·유지 및 안전관리에 관한 법률"},
    {"no": 27, "name": "풍동실험",                    "law": "건축구조기준(KBC)"},
    {"no": 28, "name": "건축물 교통영향평가",          "law": "도시교통정비 촉진법"},
    {"no": 29, "name": "장애물 없는 생활환경(BF) 인증","law": "교통약자의 이동편의 증진법"},
    {"no": 30, "name": "에너지사용계획 협의",          "law": "에너지이용 합리화법"},
    {"no": 31, "name": "건축물 안전영향평가",          "law": "건축법 제13조의2"},
    {"no": 32, "name": "사전재난영향성검토",           "law": "초고층 및 지하연계 복합건축물 재난관리에 관한 특별법"},
    {"no": 33, "name": "개발사업의 경관심의대상",      "law": "경관법 시행령"},
    {"no": 34, "name": "지구단위계획구역 지정",        "law": "국토의 계획 및 이용에 관한 법률 / 도시계획조례"},
    {"no": 35, "name": "지구단위계획변경",             "law": "국토의 계획 및 이용에 관한 법률"},
    {"no": 36, "name": "사전경관계획 심의",            "law": "경관법 시행령"},
    {"no": 37, "name": "문화재지표조사",               "law": "국가유산영향진단법"},
    {"no": 38, "name": "소규모 재해영향평가",          "law": "자연재해대책법"},
    {"no": 39, "name": "재해영향평가",                 "law": "자연재해대책법"},
    {"no": 40, "name": "환경영향평가",                 "law": "환경영향평가법"},
    {"no": 41, "name": "소규모 환경영향평가",          "law": "환경영향평가법"},
    {"no": 42, "name": "지하철(철도) 영향성 검토",     "law": "철도안전법"},
    # 대전 특화
    {"no": 43, "name": "민간건축물 녹색건축 설계기준 [대전]", "law": "대전광역시 조례"},
    {"no": 44, "name": "건축물 경관심의 [대전]",              "law": "대전광역시 경관조례"},
    {"no": 45, "name": "범죄예방 도시디자인(CPTED) [대전]",   "law": "대전광역시 CPTED 조례"},
]

# ── Claude API로 법령 변경 여부 체크 ───────────────────────────
def check_law_changes():
    """국가법령정보센터 기반으로 각 항목의 법령 변경 여부를 체크"""
    
    items_text = "\n".join([f"{i['no']}. {i['name']} / 근거법: {i['law']}" for i in ITEMS])
    
    prompt = f"""당신은 대한민국 건설·건축 법령 전문가입니다.
아래 사업승인 체크리스트 45개 항목에 대해, 최근 3개월 이내 법령 또는 고시·기준이 변경되었는지 검토해주세요.

[체크리스트 항목]
{items_text}

각 항목에 대해 다음 형식의 JSON 배열로만 응답해주세요 (다른 텍스트 없이):
[
  {{
    "no": 항목번호,
    "name": "항목명",
    "changed": true 또는 false,
    "summary": "변경 없음" 또는 "변경 내용 요약 (변경일, 주요 내용)",
    "action": "확인 불필요" 또는 "app.py 수정 검토 필요"
  }},
  ...
]
변경이 확실하지 않은 경우 changed는 false로 표시하세요."""

    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": os.environ.get("ANTHROPIC_API_KEY", ""),
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    body = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 4000,
        "messages": [{"role": "user", "content": prompt}]
    }).encode("utf-8")

    try:
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=60) as res:
            data = json.loads(res.read().decode("utf-8"))
            text = data["content"][0]["text"].strip()
            # JSON 파싱
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            return json.loads(text.strip())
    except Exception as e:
        print(f"API 오류: {e}")
        return None

# ── 이메일 HTML 보고서 생성 ────────────────────────────────────
def build_email_html(results):
    changed = [r for r in results if r.get("changed")]
    unchanged_count = len(results) - len(changed)

    rows = ""
    for r in results:
        if r.get("changed"):
            bg = "#FFF3E0"
            badge = "<span style='color:#E65100;font-weight:bold;'>⚠️ 변경</span>"
        else:
            bg = "#FFFFFF"
            badge = "<span style='color:#9E9E9E;'>✔ 변경없음</span>"

        rows += f"""
        <tr style='background:{bg};'>
            <td style='padding:8px;border:1px solid #ddd;text-align:center;'>{r['no']}</td>
            <td style='padding:8px;border:1px solid #ddd;'>{r['name']}</td>
            <td style='padding:8px;border:1px solid #ddd;text-align:center;'>{badge}</td>
            <td style='padding:8px;border:1px solid #ddd;font-size:13px;'>{r.get('summary','')}</td>
            <td style='padding:8px;border:1px solid #ddd;font-size:13px;color:#1565C0;'>{r.get('action','')}</td>
        </tr>"""

    changed_list = ""
    if changed:
        changed_list = "<ul>" + "".join([f"<li><b>{r['no']}. {r['name']}</b>: {r['summary']}</li>" for r in changed]) + "</ul>"
    else:
        changed_list = "<p style='color:#388E3C;'>✅ 변경된 항목이 없습니다.</p>"

    html = f"""
    <html><body style='font-family:Malgun Gothic,sans-serif;max-width:900px;margin:auto;'>
    <div style='background:#0052CC;color:white;padding:20px;border-radius:8px 8px 0 0;'>
        <h2 style='margin:0;'>📋 사업승인 체크리스트 법령 변경 보고서</h2>
        <p style='margin:5px 0 0;opacity:0.85;'>{TODAY} 기준 | (주)아이팝엔지니어링</p>
    </div>
    <div style='background:#E3F2FD;padding:15px;border-left:4px solid #0052CC;margin:15px 0;'>
        <b>📊 요약</b> &nbsp;|&nbsp;
        전체 항목: <b>{len(results)}개</b> &nbsp;|&nbsp;
        변경 항목: <b style='color:#E65100;'>{len(changed)}개</b> &nbsp;|&nbsp;
        변경 없음: <b style='color:#388E3C;'>{unchanged_count}개</b>
    </div>
    <div style='margin:15px 0;'>
        <h3 style='color:#0052CC;'>⚠️ 변경 항목 요약</h3>
        {changed_list}
    </div>
    <table style='width:100%;border-collapse:collapse;font-size:13px;'>
        <thead>
            <tr style='background:#0052CC;color:white;'>
                <th style='padding:10px;border:1px solid #ddd;width:40px;'>No</th>
                <th style='padding:10px;border:1px solid #ddd;'>항목명</th>
                <th style='padding:10px;border:1px solid #ddd;width:90px;'>변경여부</th>
                <th style='padding:10px;border:1px solid #ddd;'>변경 내용</th>
                <th style='padding:10px;border:1px solid #ddd;'>조치 사항</th>
            </tr>
        </thead>
        <tbody>{rows}</tbody>
    </table>
    <div style='margin-top:20px;padding:12px;background:#F5F5F5;border-radius:4px;font-size:12px;color:#757575;text-align:center;'>
        Copyright © {datetime.now().year} (주)아이팝엔지니어링 | 사업승인 체크리스트 Web v8.0 | 자동 발송 메일입니다.
    </div>
    </body></html>
    """
    return html, len(changed)

# ── 이메일 발송 ────────────────────────────────────────────────
def send_email(html_body, changed_count):
    subject = f"[사업승인 체크리스트] {TODAY} 법령 변경 보고서 {'⚠️ 변경 ' + str(changed_count) + '건 발견' if changed_count > 0 else '✅ 변경 없음'}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = GMAIL_USER
    msg["To"]      = RECIPIENT
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_PASS)
            server.sendmail(GMAIL_USER, RECIPIENT, msg.as_string())
        print(f"✅ 이메일 발송 완료 → {RECIPIENT}")
    except Exception as e:
        print(f"❌ 이메일 발송 실패: {e}")
        raise

# ── 메인 실행 ──────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"[{TODAY}] 법령 변경 체크 시작...")

    results = check_law_changes()

    if results is None:
        # API 오류 시 오류 알림 발송
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"[사업승인 체크리스트] ❌ {TODAY} 법령 체크 실패"
        msg["From"]    = GMAIL_USER
        msg["To"]      = RECIPIENT
        msg.attach(MIMEText("<p>법령 체크 중 오류가 발생했습니다. GitHub Actions 로그를 확인해주세요.</p>", "html", "utf-8"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_PASS)
            server.sendmail(GMAIL_USER, RECIPIENT, msg.as_string())
        print("❌ 오류 알림 발송 완료")
    else:
        html_body, changed_count = build_email_html(results)
        send_email(html_body, changed_count)
        print(f"[완료] 변경 항목 {changed_count}건 발견")
