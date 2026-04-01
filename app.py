# ============================================================
#  Copyright (c) 2026 (주)아이팝엔지니어링 (EYEPOP Engineering)
#  김홍정 All rights reserved.
#  본 소프트웨어는 (주)아이팝엔지니어링의 지적 재산입니다.
#  무단 복제, 배포, 수정을 금지합니다.
#  Unauthorized copying, distribution, or modification
#  of this software is strictly prohibited.
# ============================================================

import streamlit as st
import pandas as pd
from fpdf import FPDF
import os
from datetime import datetime

st.set_page_config(page_title="사업승인 체크 v9.0 | EYEPOP", layout="wide", page_icon="🏗️")
font_path = "fonts/NanumGothic.ttf"

# ── 아이팝 CI 컬러 테마 CSS ──────────────────────────────────────────────
st.markdown("""
<style>
/* ── CI 컬러 변수 */
:root {
    --ci-blue:  #3D7CC5;
    --ci-green: #6B8A28;
    --ci-gray:  #888888;
    --ci-blue-light: #EBF3FC;
    --ci-green-light: #F2F6E8;
    --bg-target: #EBF3FC;
    --bg-hold:   #FFF8EC;
    --bg-non:    #F8F8F8;
    --red-mark:  #CC0000;
}
/* ── 브랜드 헤더 바 */
.brand-header {
    background: linear-gradient(135deg, #3D7CC5 0%, #2D6CB5 100%);
    color: white;
    padding: 14px 24px;
    border-radius: 8px;
    margin-bottom: 18px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 2px 8px rgba(61,124,197,0.25);
}
.brand-header .title { font-size: 20px; font-weight: bold; letter-spacing: -0.5px; }
.brand-header .subtitle { font-size: 12px; opacity: 0.85; margin-top: 3px; }
.brand-header .version-badge {
    background: rgba(255,255,255,0.2);
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: bold;
    border: 1px solid rgba(255,255,255,0.4);
}
/* ── 요약 바지 */
.summary-bar {
    display: flex; gap: 12px; margin: 12px 0;
}
.summary-chip {
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: bold;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}
.chip-target { background: #3D7CC5; color: white; }
.chip-non    { background: #888888; color: white; }
.chip-hold   { background: #E07B00; color: white; }
.chip-fix    { background: #CC0000; color: white; }
/* ── 체크리스트 테이블 */
.checklist-table {
    width: 100%; border-collapse: collapse;
    font-family: 'Malgun Gothic', '맑은 고딕', sans-serif;
    margin-top: 10px; border-radius: 8px; overflow: hidden;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}
.checklist-table th {
    background: #3D7CC5; color: white;
    padding: 10px 8px; text-align: center;
    font-size: 13px; font-weight: bold;
    border: 1px solid #2D6CB5;
}
.checklist-table td {
    padding: 8px 10px;
    border: 1px solid #D0D9E8;
    vertical-align: top; line-height: 1.55;
    font-size: 12.5px;
}
.checklist-table tr:hover td { filter: brightness(0.96); }
/* ── 결과 배지 */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: bold;
    white-space: nowrap;
}
.badge-target { background: #3D7CC5; color: white; }
.badge-hold   { background: #E07B00; color: white; }
.badge-non    { background: #888888; color: white; }
.badge-hold-changed { background: #E07B00; color: white; border: 2px solid #FFD600; }
/* ── 수정 항목 */
.corrected-name { color: #CC0000; font-weight: 500; }
.corrected-law  { color: #CC0000; font-weight: bold; }
/* ── 기본 정보 패널 */
.info-panel {
    background: linear-gradient(135deg, #EBF3FC 0%, #F2F6E8 100%);
    border-left: 4px solid #3D7CC5;
    padding: 16px 20px; border-radius: 8px;
    margin-bottom: 16px;
}
.info-panel .panel-title {
    color: #3D7CC5; font-size: 15px; font-weight: bold; margin-bottom: 10px;
}
.info-panel table { width: 100%; border-collapse: collapse; font-size: 13px; }
.info-panel td { padding: 4px 8px; }
.info-panel .label { color: #555; width: 22%; }
.info-panel .value { font-weight: bold; color: #222; }
/* 대전 섹션 */
.daejeon-header {
    background: #6B8A28; color: white;
    padding: 10px 16px; border-radius: 6px;
    font-size: 15px; font-weight: bold;
    margin: 20px 0 8px;
}
.checklist-table.daejeon th { background: #6B8A28; border-color: #5A7A20; }
</style>
""", unsafe_allow_html=True)

# ── Footer 워터마크 (JS 동적 생성) ─────────────────────────────────────
_footer_html = """
<style>
#copyright-footer {
    position: fixed;
    bottom: 0; left: 0; right: 0;
    background: rgba(255,255,255,0.92);
    border-top: 1px solid #ddd;
    text-align: center;
    padding: 6px 0;
    font-size: 12px;
    color: #888;
    z-index: 9999;
    pointer-events: none;
}
</style>
<script>
(function(){
    function injectFooter(){
        if(document.getElementById('copyright-footer')) return;
        var el = document.createElement('div');
        el.id = 'copyright-footer';
        el.innerHTML = 'Copyright &copy; ' + new Date().getFullYear()
            + ' (주)아이팝엔지니어링 (EYEPOP Engineering) &nbsp;|&nbsp; 김홍정 &nbsp;|&nbsp; 사업승인 체크리스트 Web v9.0 &nbsp;|&nbsp; All Rights Reserved.';
        document.body.appendChild(el);
    }
    if(document.readyState === 'loading'){
        document.addEventListener('DOMContentLoaded', injectFooter);
    } else {
        injectFooter();
    }
    var obs = new MutationObserver(injectFooter);
    obs.observe(document.body, {childList: true, subtree: false});
})();
</script>
"""

try:
    import streamlit.components.v1 as _stc2
    _stc2.html(_footer_html, height=0)
except Exception:
    pass

# ── 상태 저장소 초기화 ──────────────────────────────────────────────────
if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False

def _comma_input(label, default_val, key, help_text=None, as_float=False):
    """천단위 쉼표가 표시되는 숫자 입력 (as_float=True 시 소수점 지원)"""
    display = f"{default_val:g}" if as_float else f"{int(default_val):,}"
    raw = st.text_input(label, value=display, key=key,
                        help=help_text, placeholder="숫자 입력")
    try:
        cleaned = raw.replace(",", "").replace("，", "").replace(" ", "")
        return float(cleaned) if as_float else int(cleaned)
    except Exception:
        return default_val

st.sidebar.markdown("### 🔄 시스템 제어")
col_btn1, col_btn2 = st.sidebar.columns(2)

if col_btn1.button("🔄 초기화", use_container_width=True):
    st.session_state.clear()
    st.rerun()

if col_btn2.button("🔍 분석 실행", type="primary", use_container_width=True):
    st.session_state.analyzed = True

st.sidebar.divider()

with st.sidebar:
    st.header("📝 기본 정보 입력")
    today_str = datetime.now().strftime("%Y년 %m월 %d일")
    st.markdown(f"<p style='color:#3D7CC5;font-size:13px;font-weight:bold;'>📅 작성일: {today_str}</p>", unsafe_allow_html=True)
    p_name = st.text_input("용역명", "신규 개발사업 프로젝트")
    address = st.text_input("주소", "대전광역시 서구 월드컵대로484번안길 10, 3층")

    # 총공사비 - 50억 미만 / 이상 선택 (기본값: 50억원 이상)
    cost_opt = st.selectbox("총공사비", ["50억원 미만", "50억원 이상"], index=1)

    st.divider()
    # 면적 입력
    col1, col2 = st.columns(2)
    with col1:
        land_area  = _comma_input("대지면적(㎡)", 10000, "land_area")
    with col2:
        total_area = _comma_input("연면적(㎡)", 50000, "total_area")
    under_area = _comma_input("지하층 연면적(㎡)", 10000, "under_area")
    above_area = total_area - under_area
    st.text_input("지상층 연면적(㎡)", f"{above_area:,}", disabled=True, key="above_area_disp")
    parking    = _comma_input("주차장(기계실) 면적(㎡)", 10000, "parking")
    excl_area  = total_area - parking
    st.text_input("비주거 산정 연면적(㎡)", f"{excl_area:,}", disabled=True, key="excl_area_disp")

    # 건폐율/용적률/건축면적
    col_a, col_b = st.columns(2)
    with col_a:
        build_coverage = _comma_input("건폐율(%)", 60, "build_coverage")
    with col_b:
        floor_area_ratio = _comma_input("용적률(%)", 250, "floor_area_ratio")
    arch_area = _comma_input("건축면적(㎡)", 3000, "arch_area")

    st.divider()
    # 층수/높이/굴착
    col3, col4 = st.columns(2)
    with col3:
        b_floors = _comma_input("지하층수", 2, "b_floors")
    with col4:
        g_floors = _comma_input("지상층수", 20, "g_floors")
    max_h    = _comma_input("최고높이(m)", 60, "max_h", as_float=True)
    depth    = _comma_input("굴착깊이(m)", 12, "depth", as_float=True)
    households = _comma_input("세대수", 500, "households")

    st.divider()
    edu        = st.selectbox("교육시설", ["해당없음", "200m 이내 존재"])
    heritage   = st.selectbox("문화재 시설", ["해당없음", "200m 이내"])
    landsc     = st.selectbox("경관지구", ["해당없음", "해당"])
    under_link = st.selectbox("지하연계 복합건축", ["해당없음", "해당"])
    urban      = st.selectbox("지역구분", ["도시지역", "도시외지역"])
    rail       = _comma_input("철도거리(m)", 0, "rail")
    public_inst = st.selectbox("공공기관 여부", ["민간", "공공기관"])

    usage_options = ["공동주택(아파트)", "주상복합", "오피스텔", "다가구주택", "연립주택 및 다세대주택", "제1종 근린생활시설(일용품 소매점)", "제2종 근린생활시설(다중생활시설)", "문화 및 집회시설(동·식물원 제외)", "교육연구시설(연구소·도서관 제외)", "노유자시설", "수련시설", "업무시설", "신축 공공건축물/교통수단·여객시설"]
    usages = st.multiselect("용도", usage_options, default=["공동주택(아파트)"])

st.markdown("""
<div class='brand-header'>
  <div>
    <div class='title'>🏗️ 사업승인 체크리스트</div>
    <div class='subtitle'>(주)아이팝엔지니어링 (EYEPOP Engineering) &nbsp;|&nbsp; 최종수정 2026-04-02 &nbsp;|&nbsp; 법적 근거 전면 검토 반영</div>
  </div>
  <div class='version-badge'>Web v9.0</div>
</div>
""", unsafe_allow_html=True)

# 분석 실행 버튼을 눌렀을 때만 아래 내용이 화면에 출력됨
if st.session_state.analyzed:
    L, T, D, H, HH = land_area, total_area, depth, max_h, households
    BF, GF = b_floors, g_floors
    TF = BF + GF
    excl_A = excl_area
    rail_D = rail

    is_edu        = (edu == "200m 이내 존재")
    is_heritage   = (heritage == "200m 이내")
    is_landscape  = (landsc == "해당")
    is_under_link = (under_link == "해당")
    is_public     = (public_inst == "공공기관")

    has_gong   = any(u in ["공동주택(아파트)", "다가구주택", "연립주택 및 다세대주택"] for u in usages)
    has_ju     = "주상복합" in usages
    is_biz_app = (has_gong and HH >= 20) or (has_ju and HH >= 300)
    c10_targets = ["다가구주택", "공동주택(아파트)", "연립주택 및 다세대주택", "오피스텔",
                   "제1종 근린생활시설(일용품 소매점)", "제2종 근린생활시설(다중생활시설)",
                   "문화 및 집회시설(동·식물원 제외)", "교육연구시설(연구소·도서관 제외)", "노유자시설", "수련시설"]

    # ── 기본 정보 상단 출력 ────────────────────────────────────────
    st.markdown(f"""
    <div class='info-panel'>
    <div class='panel-title'>📋 기본 정보</div>
    <table>
    <tr><td class='label'>📅 작성일</td><td class='value'>{today_str}</td>
        <td class='label'>🏗️ 용역명</td><td class='value'>{p_name}</td></tr>
    <tr><td class='label'>📍 주소</td><td class='value' colspan='3'>{address}</td></tr>
    <tr><td class='label'>💰 총공사비</td><td class='value'>{cost_opt}</td>
        <td class='label'>👥 세대수</td><td class='value'>{HH:,}세대</td></tr>
    <tr><td class='label'>🏠 대지면적</td><td class='value'>{L:,}㎡</td>
        <td class='label'>🏢 연면적</td><td class='value'>{T:,}㎡</td></tr>
    <tr><td class='label'>⬇️ 지하층 연면적</td><td class='value'>{under_area:,}㎡</td>
        <td class='label'>⬆️ 지상층 연면적</td><td class='value'>{above_area:,}㎡</td></tr>
    <tr><td class='label'>📊 건폐율/용적률</td><td class='value'>{build_coverage}% / {floor_area_ratio}%</td>
        <td class='label'>📐 건축면적</td><td class='value'>{arch_area:,}㎡</td></tr>
    <tr><td class='label'>🏗️ 층수</td><td class='value'>지하{BF}층 / 지상{GF}층 (총{TF}층)</td>
        <td class='label'>📏 최고높이 / 굴착</td><td class='value'>{H}m / {D}m</td></tr>
    <tr><td class='label'>🏛️ 용도</td><td class='value' colspan='3'>{", ".join(usages)}</td></tr>
    </table>
    </div>
    """, unsafe_allow_html=True)

    # ── 42개 항목 (제출시기 추가) ──────────────────────────────────
    # (no, 항목명, 판정, 법적근거, 제출시기, 비고)
    _item34 = "가" if (has_gong and HH >= 300) else "부"
    items = [
        (1,  "구조 성능기반설계",          "판단 유보", "건축법 시행령 제91조의3 + KBC 2016", "구조 심의 시", f"성능기반 내진설계 적용 대상 여부 구조 전문가 확인 필요 — 50층↑ 또는 H200m↑ 특수구조 건축물 의무 (현재: {TF}층, {H}m)"),
        (2,  "설계안전보건대장",            "가" if cost_opt=="50억원 이상" else "부", "산업안전보건법 제67조 + 고용노동부 고시", "공사 계약 체결 시",     f"공사비 50억 이상, 기본-설계-공사 3단계 분리 명기 (현재: {cost_opt})"),
        (3,  "단지내 주변일조.일영분석",    "가" if has_gong else "부",          "건축법 제61조",         "도시계획심의시",         "공동주택이면 해당"),
        (4,  "단지특화디자인(색채 등)",     "가" if has_gong or has_ju or "오피스텔" in usages else "부", "건축법 제60조의2 + 주택건설기준", "건축심의시", "공동주택·주상복합·오피스텔 해당 — 외관색채·입면디자인·조경 등 단지 특화 항목 심의위원회 검토"),
        (5,  "소규모 지하안전영향평가",     "가" if 10 <= D < 20 else "부",      "지하안전관리특별법 제14조", "사업승인 완료 전",    f"굴착 10m↑~20m 미만, 지반침하 발생 시 관할 지자체 즉시 통보·응급조치 의무 (현재: {D}m)"),
        (6,  "지하안전영향평가",            "가" if D >= 20 else "부",           "지하안전관리특별법 제13조", "사업승인 완료 전",    f"굴착 20m↑, 지반침하 발생 시 관할 지자체 즉시 통보·응급조치 의무 (현재: {D}m)"),
        (7,  "착공후 지하안전영향평가",     "가" if D >= 20 else "부",           "지하안전관리특별법 제22조", "공사 착공 후",        f"굴착 20m↑ 공사 착공 이후 사후 평가 제출 의무 (현재: {D}m)"),
        (8,  "현황측량(지장물조사)",        "가" if D >= 10 else "부",           "지하안전관리특별법 제12조 + 시행령 제7조", "사업계획승인신청 전", f"지하안전영향평가(10m↑) 선행 제출 사항, 지하 지장물·매설관로 현황 확인 (현재: {D}m)"),
        (9,  "지질조사",                   "가",                                "지하안전관리특별법 제9조 + 건설기술진흥법 제62조", "착공시", "전 사업 의무 — 지하안전영향평가 대상은 3공(시추·CPT·공내재하) 이상 발주 권고"),
        (10, "흙막이 설계",                "가" if BF > 0 else "부",            "건축법 시행령 제91조의3 + 가설구조물 설계기준", "인허가시", f"지하층 굴토 깊이 2m↑ 또는 인접 건축물 기초보다 깊은 경우 가설구조물 구조안전확인 의무 (현재: 지하{BF}층, 굴착{D}m)"),
        (11, "수량산출서",                 "가" if (has_gong and HH >= 20) or ("단독주택" in usages and HH >= 20) else "부", "주택법 제15조 + 주택건설기준 등에 관한 규정 제5조", "착공시", f"공동주택 20세대↑ / 단독주택 20호↑ / 도시형생활주택 30세대↑ 사업승인 신청 필수 첨부 (현재: {HH}세대)"),
        (12, "단지내 소음예측평가",         "가" if is_biz_app else "부",        "주택건설기준 제9조",     "사업계획승인신청시",     "사업계획승인 대상 해당 (30세대↑ 기준 확인 — 주택법 제15조 적용 세대수 기준과 일치)"),
        (13, "범죄예방 건축기준",           "가" if any(u in c10_targets for u in usages) else "부", "건축법 53조의2", "허가신청", "500세대 미만 아파트·다가구·다세대·연립·오피스텔 등 전면 의무 적용 확대"),
        (14, "에너지절약설계기준",          "가" if excl_A >= 500 or has_gong else "부", "녹색건축물 조성 지원법 제14조 + 건축물에너지절약설계기준(고시)", "사업계획승인신청시", f"비주거 연면적 500㎡↑ 또는 공동주택 전체 — EPI 점수 기준 충족 여부 확인 (현재: {excl_A:,}㎡)"),
        (15, "수질오염물질 총량제",         "가" if (has_gong and HH>=30) or (has_ju and HH>=30) else "부", "물환경보전법 제53조 + 수질오염총량관리기본방침", "사업계획승인신청시", f"30세대↑ 공동주택·주상복합 — 유역환경청 협의 필요, 오염부하량 할당 초과 시 사업 불가 (현재: {HH}세대)"),
        (16, "녹색건축인증",               "가" if ((has_gong and HH>=30) or excl_A>=500) else "부", "녹색건축물 조성 지원법 제16조", "사업승인 완료 후", f"주거 30세대↑ / 비주거 500㎡↑ 의무 — 공공건축물은 최우수(그린1등급) 이상 (현재: {HH}세대, {excl_A:,}㎡)"),
        (17, "제로에너지건축물 인증",       "가" if (has_gong and HH>=30) or (is_public and T>=500) or (T>=1000 and ("업무시설" in usages or is_public)) else "부", "녹색건축물법 제17조", "예비:사업승인후 / 본:사용승인후", f"공공건축물 500㎡↑ / 민간·공공 공동주택 30세대↑ / 업무시설 1,000㎡↑ 공공 의무화(민간 시행 시점 지자체 확인 필요) (현재: {HH}세대, {T:,}㎡)"),
        (18, "에너지절약형 친환경주택",     "가" if has_gong and HH>=30 and is_biz_app else "부", "주택건설기준 64조", "사업계획승인신청시", f"30세대 이상 사업승인 공동주택 (현재: {HH}세대)"),
        (19, "건강친화형 주택 건설기준",    "가" if has_gong and HH>=500 else "부", "주택건설기준 65조", "사업계획승인신청시", f"500세대↑ 공동주택, 감리자 이행확인서 제출 (현재: {HH}세대)"),
        (20, "공동주택 결로 방지 설계",     "가" if has_gong and HH>=500 else "부", "주택건설기준 14조", "착공신고 시", f"500세대 이상 공동주택 (현재: {HH}세대)"),
        (21, "장수명 주택 건설인증",        "가" if has_gong and HH>=1000 else "부", "주택건설기준 제65조의2", "사업계획승인 신청 전", f"1,000세대↑ 공동주택, 설계기준강도 21MPa 상향 (현재: {HH}세대)"),
        (22, "교육환경평가서",             "가" if is_edu and (T>=100000 or HH>=100) else "부", "교육환경보호법 제6조·시행령 제23조", "사업계획 승인 전", f"학교 200m이내 + 연면적 10만㎡↑ 또는 100세대↑ 공동주택 (21층 초과 기준 삭제), 유치원·대안학교 포함 (현재: {T:,}㎡, {HH}세대)"),
        (23, "에너지소비 총량제(ECO2)",    "가" if (excl_A>=3000 and any(u in ["업무시설", "교육연구시설(연구소·도서관 제외)"] for u in usages)) or (is_public and T>=500) else "부", "건축물에너지절약설계기준(국토부 고시) 제22조", "사업계획승인신청시", f"업무·교육 3,000㎡↑ / 공공 500㎡↑ — 용도별 단위면적당 에너지소비량(kWh/㎡·년) 기준 이내 설계 (현재: {excl_A:,}㎡, {T:,}㎡)"),
        (24, "제로에너지건축물 (공공) ※17번 병합", "부", "녹색건축물법", "-", "※ v8.0: 17번 항목으로 병합됨 (별도 항목 비활성화)"),
        (25, "건축물의 경관심의대상",       "가" if is_landscape else "부",      "경관법 제28조 + 지자체 경관조례", "건축심의시", "경관지구·중점경관관리구역 내 건축물 — 외관색채·입면형태·옥외광고물 포함 심의"),
        (26, "성능위주 소방설계",           "가" if (has_gong and (TF>=50 or H>=200)) or (not (has_gong and len(usages)==1) and (TF>=30 or H>=120)) else "부", "소방시설법 제8조", "건축심의 신청전", f"아파트 50층/200m↑ / 일반 30층/120m↑ (현재: {H}m, {TF}층)"),
        (27, "풍동실험",                   "판단 유보",                         "건축구조기준(KBC) 0306.5 + 건축법 시행령 제32조", "구조 심의 시", f"높이 60m↑ 또는 불규칙 평면 건축물 구조 엔지니어 판단 — 풍동시험기관(KIAEBS 등) 의뢰 필요 (현재: {H}m, {TF}층)"),
        (28, "건축물 교통영향평가",         "판단 유보",                         "도시교통정비 촉진법 제15조 + 시행령 제13조의2", "건축심의 전", f"연면적 3만㎡↑ 또는 판매·문화시설 2만㎡↑ 등 — 특별시·광역시 상급관청 심의 격상 여부 관할 교통부서 사전 확인 필요 (현재: {T:,}㎡)"),
        (29, "장애물 없는 생활환경(BF) 인증", "가" if is_public or "신축 공공건축물/교통수단·여객시설" in usages or TF>=50 or H>=200 or is_under_link else "부", "장애인편의법 제10조의2 + 초고층재난법 제9조", "예비:본인증전 / 본:사용승인후", "신축 공공·여객시설 + 민간 초고층(50층/200m↑) 및 지하연계 복합건축물 의무화"),
        (30, "에너지사용계획 협의",         "가" if (is_public and T >= 300000) or (not is_public and T >= 600000) else "부", "에너지이용합리화법 제10조 + 산업부 고시", "사업승인 신청 전", f"공공 30만㎡↑ / 민간 60만㎡↑ (현재: {T:,}㎡, {'공공' if is_public else '민간'})"),
        (31, "건축물 안전영향평가",         "가" if TF>=50 or H>=200 or (GF>=16 and T>=100000) else "부", "건축법 제13조의2 + 시행령 제10조의3", "건축 허가 전", f"50층↑ OR 200m↑ OR (16층↑ AND 10만㎡↑) (현재: {TF}층, {H}m, {T:,}㎡)"),
        (32, "사전재난영향성검토",          "가" if TF>=50 or H>=200 or is_under_link else "부", "초고층재난법 제7조", "허가등을 하기 전", f"50층↑ OR 200m↑ OR 지하연계복합 — 소방·재난 통합방재계획 포함 (현재: {TF}층, {H}m)"),
        (33, "개발사업의 경관심의대상",     "가" if L >= 30000 else "부",        "경관법 시행령 [별표]",   "도시계획심의시",         f"사업유형별 면적 기준 상이 — 주거:3만㎡↑, 일반개발:5만㎡↑ 등 별표 세분화 기준 확인 필요 (현재: {L:,}㎡)"),
        (34, "지구단위계획구역 지정",       _item34,                             "국토계획법 제51조제1항제8호 + 도시계획조례", "도시계획심의시", f"공동주택 300세대↑ (현재: {HH}세대)"),
        (35, "지구단위계획변경",            "가" if _item34 == "가" else "부",   "국토계획법 제49조~제52조 + 시행령 제43조", "건축심의 전", "34번 지구단위계획구역 지정과 연계 발주 — 변경결정·지형도면 고시까지 사업 일정 고려 필요"),
        (36, "사전경관계획 심의",           "가" if L >= 300000 or T >= 200000 else "부", "경관법 시행령 제24조 + 경관법 제27조", "도시계획심의시", f"대지 30만㎡↑ OR 연면적 20만㎡↑ 개발사업 — 경관계획 수립 후 시·도 경관위원회 심의 (현재: {L:,}㎡, {T:,}㎡)"),
        (37, "문화재지표조사(현상변경)",    "가" if is_heritage or L>=30000 else "부", "매장유산보호법 제6조 + 국가유산기본법", "실시계획 작성 완료전", f"문화재 200m이내 또는 대지 3만㎡↑ (2024 국가유산기본법 전환 반영) (현재: {L:,}㎡)"),
        (38, "소규모 재해영향평가",         "가" if (urban=="도시지역" and 10000 <= L < 50000) or (urban!="도시지역" and 5000 <= L < 50000) else "부", "자연재해대책법 시행령 별표1", "사업계획승인전", f"도시지역 1만~5만㎡ / 관리·농림지역 5천~5만㎡ (현재: {L:,}㎡, {urban})"),
        (39, "재해영향평가",               "가" if L >= 50000 else "부",        "자연재해대책법 제4조의2 + 시행령 제5조", "사업계획승인전", f"대지면적 5만㎡↑ — 홍수·침수·토사 등 유형별 검토, 지자체 재난관리부서 협의 필요 (현재: {L:,}㎡)"),
        (40, "환경영향평가",               "가" if L >= 125000 else "부",       "환경영향평가법",         "사업계획승인전",         f"일반기준 25만㎡↑, 12만5천㎡는 특정 지역·유형에 한함 — 시행령 [별표 3] 사업유형별 기준 확인 (현재: {L:,}㎡)"),
        (41, "소규모 환경영향평가",         "가" if (urban == "도시지역" and 5000 <= L < 60000) or (urban == "도시외지역" and 5000 <= L < 10000) else "부", "환경영향평가법 시행령 [별표 4]", "사업계획승인전", f"도시지역 5천~6만㎡(상한은 사업유형별 상이) / 도시외지역 5천~1만㎡ — 시행령 별표4 사업유형별 세분화 기준 확인 (현재: {L:,}㎡, {urban})"),
        (42, "지하철(철도) 영향성 검토",   "가" if 0 < rail_D <= 30 else "부",  "철도안전법 제45조의2 + 시행령 제45조의2", "착공 전",  f"철도보호지구(철도경계선 30m이내) — 노반·궤도 진동·침하 검토 후 철도운영기관 협의 필요 (현재: {rail_D}m)")
    ]

    # ── 대전광역시 특화 조례 항목 (주소에 "대전" 포함 시 추가) ──────────────
    is_daejeon = "대전" in address
    daejeon_items = []
    if is_daejeon:
        dj_no_base = 43
        daejeon_items.append((dj_no_base, "민간건축물 녹색건축 설계기준 [대전]",
            "가" if has_gong or excl_A >= 500 else "부",
            "대전광역시 조례", "사업계획승인신청시",
            f"주거(세대수)/비주거(연면적) 4개 군 분류, 환경·에너지·신재생에너지 기준 엄격화 (현재: {HH}세대, {excl_A:,}㎡)"))
        daejeon_items.append((dj_no_base+1, "건축물 경관심의 [대전]",
            "가" if TF >= 21 or T >= 100000 else "부",
            "대전광역시 경관조례", "건축심의시",
            f"21층↑ 또는 10만㎡↑ 원칙, 서구 등 기초자치단체 조례에 따라 미만도 대상 가능 → 대지 위치 확인 필수 (현재: {TF}층, {T:,}㎡)"))
        daejeon_items.append((dj_no_base+2, "범죄예방 도시디자인(CPTED) [대전]",
            "가" if any(u in c10_targets for u in usages) else "부",
            "대전광역시 CPTED 조례", "허가신청",
            "5년 단위 기본계획, 출입구·울타리·조경 등 자연적 감시·접근통제 자체방어적 디자인 기준 적용"))

    ORIGINALLY_HOLD_NOS = {1, 27, 28, 30, 33, 34, 35, 36, 38, 39, 40, 41}
    # v9.0 수정 항목 (🔴 즉시 5개 + 🟡 권장 10개)
    CORRECTED_NOS = {2, 12, 17, 21, 22, 26, 29, 30, 31, 33, 34, 37, 38, 40, 41}
    display_data = []
    cnts = {"target": 0, "non": 0, "hold": 0}

    for i in items:
        was_hold = i[0] in ORIGINALLY_HOLD_NOS and i[2] != "판단 유보"
        was_corrected = i[0] in CORRECTED_NOS
        if i[2] == "가":
            res, color, tag = "◯ 대상", "#0052CC", "target"
            cnts["target"] += 1
        elif i[2] == "판단 유보":
            res, color, tag = "! 판단 유보", "#FF9800", "hold"
            cnts["hold"] += 1
        else:
            res, color, tag = "✕ 비대상", "#B0B0B0", "non"
            cnts["non"] += 1
        display_data.append({"No": i[0], "분석 항목": i[1], "결과": res,
                              "제출시기": i[4], "법적 근거": i[3], "비고": i[5],
                              "color": color, "tag": tag, "was_hold": was_hold,
                              "was_corrected": was_corrected})

    # 대전 특화 항목 추가
    ORIGINALLY_HOLD_DJ_NOS = {43, 44}
    daejeon_display = []
    for i in daejeon_items:
        was_hold = i[0] in ORIGINALLY_HOLD_DJ_NOS and i[2] != "판단 유보"
        if i[2] == "가":
            res, color, tag = "◯ 대상", "#007A4D", "target"
            cnts["target"] += 1
        elif i[2] == "판단 유보":
            res, color, tag = "! 판단 유보", "#FF9800", "hold"
            cnts["hold"] += 1
        else:
            res, color, tag = "✕ 비대상", "#B0B0B0", "non"
            cnts["non"] += 1
        daejeon_display.append({"No": i[0], "분석 항목": i[1], "결과": res,
                                 "제출시기": i[4], "법적 근거": i[3], "비고": i[5],
                                 "color": color, "tag": tag, "was_hold": was_hold})

    # ── 요약 배지 ──────────────────────────────────────────────────────────
    corrected_cnt = len(CORRECTED_NOS)
    st.markdown(f"""
    <div class='summary-bar'>
      <span class='summary-chip chip-target'>● 대상 {cnts['target']}건</span>
      <span class='summary-chip chip-non'>✕ 비대상 {cnts['non']}건</span>
      <span class='summary-chip chip-hold'>▲ 판단유보 {cnts['hold']}건</span>
      <span class='summary-chip chip-fix'>🔴 v9.0 수정 {corrected_cnt}항목</span>
    </div>
    """, unsafe_allow_html=True)

    # ── HTML 테이블 렌더링 헬퍼 ─────────────────────────────────────────────
    def make_badge(tag, was_hold):
        if tag == "target":
            cls = "badge-target"; label = "● 대상"
        elif tag == "hold":
            cls = "badge-hold-changed" if was_hold else "badge-hold"; label = "▲ 유보"
        else:
            cls = "badge-non"; label = "✕ 비대상"
        return f"<span class='badge {cls}'>{label}</span>"

    def make_rows(data_list):
        rows = ""
        for row in data_list:
            bg = {"target": "#EBF3FC", "hold": "#FFF8EC", "non": "#F8F8F8"}[row['tag']]
            left_border = "border-left:3px solid #CC0000;" if row.get('was_corrected') else ""
            name_cls = " class='corrected-name'" if row.get('was_corrected') else ""
            law_cls  = " class='corrected-law'"  if row.get('was_corrected') else ""
            rows += f"""<tr style='background:{bg};{left_border}'>
              <td style='text-align:center;font-weight:bold;font-size:13px;'>{row['No']}</td>
              <td{name_cls}>{row['분석 항목']}</td>
              <td style='text-align:center;'>{make_badge(row['tag'], row.get('was_hold'))}</td>
              <td style='color:#555;font-size:12px;'>{row['제출시기']}</td>
              <td{law_cls}>{row['법적 근거']}</td>
              <td style='color:#444;font-size:12px;'>{row['비고']}</td>
            </tr>"""
        return rows

    header_row = """<tr>
      <th style='width:42px;'>No</th>
      <th style='width:190px;'>분석 항목</th>
      <th style='width:88px;'>결과</th>
      <th style='width:125px;'>제출시기</th>
      <th style='width:180px;'>법적 근거</th>
      <th>비고</th>
    </tr>"""

    st.markdown(f"""
    <table class='checklist-table'>
      <thead>{header_row}</thead>
      <tbody>{make_rows(display_data)}</tbody>
    </table>
    """, unsafe_allow_html=True)

    # 대전 특화 항목 표시
    if is_daejeon and daejeon_display:
        st.markdown("<div class='daejeon-header'>🏙️ 대전광역시 특화 조례 항목</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <table class='checklist-table daejeon'>
          <thead>{header_row}</thead>
          <tbody>{make_rows(daejeon_display)}</tbody>
        </table>
        """, unsafe_allow_html=True)

    def make_pdf():
        pdf = FPDF(); pdf.add_page()
        if os.path.exists(font_path): pdf.add_font("K", "", font_path); pdf.set_font("K", size=10)

        # 제목
        pdf.set_font("K", size=13)
        pdf.cell(0, 10, "■ 사업승인 체크 리스트 결과보고서", ln=True, align='C')
        pdf.set_font("K", size=9)
        pdf.set_text_color(61, 124, 197)
        pdf.cell(0, 6, f"분석 요약 - 대상: {cnts['target']} / 비대상: {cnts['non']} / 유보: {cnts['hold']}", ln=True, align='R')

        # 기본 정보 박스
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("K", size=9)
        pdf.set_fill_color(235, 243, 252)
        pdf.cell(0, 7, "[ 기본 정보 ]", border=1, ln=True, fill=True, align='C')
        info_pairs = [
            ("작성일", today_str, "용역명", p_name),
            ("주소", address, "총공사비", cost_opt),
            ("대지면적", f"{L:,}㎡", "연면적", f"{T:,}㎡"),
            ("지하층 연면적", f"{under_area:,}㎡", "지상층 연면적", f"{above_area:,}㎡"),
            ("건폐율", f"{build_coverage}%", "용적률", f"{floor_area_ratio}%"),
            ("건축면적", f"{arch_area:,}㎡", "최고높이", f"{H}m"),
            ("층수", f"지하{BF}/지상{GF}(총{TF}층)", "굴착깊이", f"{D}m"),
            ("세대수", f"{HH:,}세대", "용도", ", ".join(usages)),
        ]
        for pair in info_pairs:
            pdf.set_fill_color(250, 250, 250)
            pdf.cell(25, 6, pair[0], border=1, fill=True)
            pdf.cell(65, 6, str(pair[1]), border=1)
            if len(pair) > 2:
                pdf.cell(25, 6, pair[2], border=1, fill=True)
                pdf.cell(75, 6, str(pair[3]), border=1)
            pdf.ln()
        pdf.ln(3)

        # 저작권
        pdf.set_font("K", size=7)
        pdf.set_text_color(150, 150, 150)
        pdf.cell(0, 5, f"Copyright © {datetime.now().year} (주)아이팝엔지니어링 (EYEPOP Engineering)  |  김홍정  |  사업승인 체크리스트 Web v9.0  |  All Rights Reserved.", ln=True, align='C')
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("K", size=9)
        pdf.ln(2)

        # 체크리스트 테이블
        pdf.set_fill_color(61, 124, 197)
        pdf.set_text_color(255, 255, 255)
        col_w = [8, 42, 22, 28, 30, 60]
        headers = ["No", "분석 항목", "결과", "제출시기", "법적 근거", "비고"]
        for h, w in zip(headers, col_w):
            pdf.cell(w, 7, h, border=1, fill=True, align='C')
        pdf.ln()
        pdf.set_text_color(0, 0, 0)

        def pdf_row(r):
            col_w_local = [8, 42, 22, 28, 30, 60]
            texts = [
                str(r['No']),
                r['분석 항목'],
                r['결과'],
                r.get('제출시기', '-'),
                r['법적 근거'],
                r['비고']
            ]
            font_size = 8
            line_h = 4.5

            def split_text(text, width):
                pdf.set_font("K", size=font_size)
                words = str(text).split(' ')
                lines, cur = [], ''
                for w in words:
                    test = (cur + ' ' + w).strip()
                    if pdf.get_string_width(test) > width - 2 and cur:
                        lines.append(cur)
                        cur = w
                    else:
                        cur = test
                if cur:
                    lines.append(cur)
                return lines or ['']

            all_lines = [split_text(t, w) for t, w in zip(texts, col_w_local)]
            max_lines = max(len(l) for l in all_lines)
            row_h = max(7, max_lines * line_h + 1)

            # 페이지 넘김 체크
            if pdf.get_y() + row_h > pdf.page_break_trigger:
                pdf.add_page()
                pdf.set_fill_color(61, 124, 197)
                pdf.set_text_color(255, 255, 255)
                pdf.set_font("K", size=9)
                for h, w in zip(headers, col_w):
                    pdf.cell(w, 7, h, border=1, fill=True, align='C')
                pdf.ln()
                pdf.set_text_color(0, 0, 0)

            y0 = pdf.get_y()
            x0 = pdf.l_margin

            for i, (lines_i, w) in enumerate(zip(all_lines, col_w_local)):
                pdf.set_font("K", size=font_size)
                if i == 2:
                    if r.get('was_hold'):
                        pdf.set_fill_color(255, 255, 0)
                        pdf.rect(x0, y0, w, row_h, 'F')
                    if r['tag'] == "target": pdf.set_text_color(61, 124, 197)
                    elif r['tag'] == "hold": pdf.set_text_color(255, 152, 0)
                    else: pdf.set_text_color(160, 160, 160)
                else:
                    pdf.set_text_color(0, 0, 0)
                pdf.rect(x0, y0, w, row_h)
                for j, line in enumerate(lines_i):
                    pdf.set_xy(x0 + 1, y0 + j * line_h + 1)
                    align = 'C' if i in [0, 2] else 'L'
                    pdf.cell(w - 2, line_h, line, border=0, align=align)
                x0 += w

            pdf.set_text_color(0, 0, 0)
            pdf.set_xy(pdf.l_margin, y0 + row_h)

        for r in display_data:
            pdf_row(r)

        # 대전 특화 항목 PDF
        if daejeon_display:
            pdf.ln(3)
            pdf.set_fill_color(107, 138, 40)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("K", size=10)
            pdf.cell(0, 8, "  ▶ 대전광역시 특화 조례 항목", ln=True, fill=True)
            pdf.set_text_color(255, 255, 255)
            pdf.set_fill_color(107, 138, 40)
            pdf.set_font("K", size=9)
            for h, w in zip(headers, col_w):
                pdf.cell(w, 7, h, border=1, fill=True, align='C')
            pdf.ln()
            pdf.set_text_color(0, 0, 0)
            for r in daejeon_display:
                pdf_row(r)

        return pdf.output()

    st.divider()
    pdf_bytes = make_pdf()
    st.download_button("📥 [클릭] 분석 결과 PDF 저장하기", data=bytes(pdf_bytes),
                       file_name=f"사업승인체크리스트_v9_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                       mime="application/pdf", type="primary", use_container_width=True)
else:
    st.info("👈 좌측 하단의 **[🔍 분석 실행]** 버튼을 누르시면 42개 항목 분석 결과가 여기에 출력됩니다.")
