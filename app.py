# ============================================================
#  Copyright (c) 2024 (주)아이팝엔지니어링
#  All rights reserved.
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

st.set_page_config(page_title="사업승인 체크 v8.1_Boss", layout="wide")
font_path = "fonts/NanumGothic.ttf"

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
            + ' (주)아이팝엔지니어링 &nbsp;|&nbsp; 사업승인 체크리스트 Web v8.1 &nbsp;|&nbsp; All Rights Reserved.';
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
    st.markdown(f"<p style='color:#0052CC;font-size:13px;font-weight:bold;'>📅 작성일: {today_str}</p>", unsafe_allow_html=True)
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

st.title("■ 사업승인 체크 리스트_Web v8.1")
st.caption("🗓️ 최종 수정: 2026-04-01  |  인증 없는 완전 공개 버전")

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
    <div style='background:#F0F4FF;border-left:4px solid #0052CC;padding:14px 18px;border-radius:6px;margin-bottom:16px;font-size:13px;'>
    <b style='color:#0052CC;font-size:15px;'>📋 기본 정보</b><br><br>
    <table style='width:100%;border-collapse:collapse;'>
    <tr><td style='width:25%;color:#555;'>📅 작성일</td><td><b>{today_str}</b></td>
        <td style='width:25%;color:#555;'>🏗️ 용역명</td><td><b>{p_name}</b></td></tr>
    <tr><td style='color:#555;'>📍 주소</td><td colspan='3'><b>{address}</b></td></tr>
    <tr><td style='color:#555;'>💰 총공사비</td><td><b>{cost_opt}</b></td>
        <td style='color:#555;'>👥 세대수</td><td><b>{HH:,}세대</b></td></tr>
    <tr><td style='color:#555;'>🏠 대지면적</td><td><b>{L:,}㎡</b></td>
        <td style='color:#555;'>🏢 연면적</td><td><b>{T:,}㎡</b></td></tr>
    <tr><td style='color:#555;'>⬇️ 지하층 연면적</td><td><b>{under_area:,}㎡</b></td>
        <td style='color:#555;'>⬆️ 지상층 연면적</td><td><b>{above_area:,}㎡</b></td></tr>
    <tr><td style='color:#555;'>📊 건폐율</td><td><b>{build_coverage}%</b></td>
        <td style='color:#555;'>📊 용적률</td><td><b>{floor_area_ratio}%</b></td></tr>
    <tr><td style='color:#555;'>📐 건축면적</td><td><b>{arch_area:,}㎡</b></td>
        <td style='color:#555;'>📏 최고높이</td><td><b>{H}m</b></td></tr>
    <tr><td style='color:#555;'>🏗️ 층수</td><td><b>지하{BF}층 / 지상{GF}층 (총{TF}층)</b></td>
        <td style='color:#555;'>⛏️ 굴착깊이</td><td><b>{D}m</b></td></tr>
    <tr><td style='color:#555;'>🏛️ 용도</td><td colspan='3'><b>{", ".join(usages)}</b></td></tr>
    </table>
    </div>
    """, unsafe_allow_html=True)

    # ── 42개 항목 (제출시기 추가) ──────────────────────────────────
    # (no, 항목명, 판정, 법적근거, 제출시기, 비고)
    _item34 = "가" if (has_gong and HH >= 300) else "부"
    items = [
        (1,  "구조 성능기반설계",          "판단 유보", "내진설계 지침",         "구조 심의 시",          "구조 심의 시"),
        (2,  "설계안전보건대장",            "가" if cost_opt=="50억원 이상" else "부", "안전보건대장 고시", "공사 계약 체결 시",     f"공사비 50억 이상, 기본-설계-공사 3단계 분리 명기 (현재: {cost_opt})"),
        (3,  "단지내 주변일조.일영분석",    "가" if has_gong else "부",          "건축법 제61조",         "도시계획심의시",         "공동주택이면 해당"),
        (4,  "단지특화디자인(색채 등)",     "가" if has_gong or has_ju or "오피스텔" in usages else "부", "심의 기준", "건축심의시", "공동/주상/오피스텔 해당"),
        (5,  "소규모 지하안전영향평가",     "가" if 10 <= D < 20 else "부",      "지하안전법",            "사업승인 완료 전",       f"굴착 10~20m 미만, 침하 시 지자체 즉시 통보·응급조치 의무 (현재: {D}m)"),
        (6,  "지하안전영향평가",            "가" if D >= 20 else "부",           "지하안전법",            "사업승인 완료 전",       f"굴착 20m 이상, 침하 시 지자체 즉시 통보·응급조치 의무 (현재: {D}m)"),
        (7,  "착공후 지하안전영향평가",     "가" if D >= 20 else "부",           "지하안전법",            "공사 착공 후",           f"굴착 20m 이상 (현재: {D}m)"),
        (8,  "현황측량(지장물조사)",        "가" if D >= 10 else "부",           "관련 규정",             "사업계획승인신청 전",    f"지하안전평가 대상 시 해당 (현재: {D}m)"),
        (9,  "지질조사",                   "가",                                "지하안전 매뉴얼",        "착공시",                "무조건 해당 (지안평 대상시 3공 발주)"),
        (10, "흙막이 설계",                "가" if BF > 0 else "부",            "건축법 시행령",          "인허가시",              f"지하층 있으면 해당 (현재: 지하 {BF}층)"),
        (11, "수량산출서",                 "가" if (has_gong and HH >= 20) or ("단독주택" in usages and HH >= 20) else "부", "제출 기준", "착공시", f"공동주택 20세대/단독주택 20호/도시형생활주택 30세대 이상 (현재: {HH}세대)"),
        (12, "단지내 소음예측평가",         "가" if is_biz_app else "부",        "주택건설기준 9조",       "사업계획승인신청시",     "사업계획승인 대상 해당"),
        (13, "범죄예방 건축기준",           "가" if any(u in c10_targets for u in usages) else "부", "건축법 53조의2", "허가신청", "500세대 미만 아파트·다가구·다세대·연립·오피스텔 등 전면 의무 적용 확대"),
        (14, "에너지절약설계기준",          "가" if excl_A >= 500 or has_gong else "부", "녹색건축물법", "사업계획승인신청시", f"비주거 500㎡이상 또는 공동주택 (현재: {excl_A:,}㎡)"),
        (15, "수질오염물질 총량제",         "가" if (has_gong and HH>=30) or (has_ju and HH>=30) else "부", "오염총량방침", "사업계획승인신청시", f"30세대 이상 공동주택 또는 주상복합 (현재: {HH}세대)"),
        (16, "녹색건축인증",               "가" if ((has_gong and HH>=30) or excl_A>=500) else "부", "녹색건축물법", "사업승인 완료 후", f"주거30세대/비주거500㎡ (현재: {HH}세대, {excl_A:,}㎡)"),
        (17, "제로에너지건축물 인증",       "가" if (has_gong and HH>=30) or (is_public and T>=500) or (T>=1000 and ("업무시설" in usages or is_public)) else "부", "녹색건축물법", "예비:사업승인후 / 본:사용승인후", f"공공건축물 500㎡↑ / 민간·공공 공동주택 30세대↑ (현재: {HH}세대, {T:,}㎡)"),
        (18, "에너지절약형 친환경주택",     "가" if has_gong and HH>=30 and is_biz_app else "부", "주택건설기준 64조", "사업계획승인신청시", f"30세대 이상 사업승인 공동주택 (현재: {HH}세대)"),
        (19, "건강친화형 주택 건설기준",    "가" if has_gong and HH>=500 else "부", "주택건설기준 65조", "사업계획승인신청시", f"500세대↑ 공동주택, 감리자 이행확인서 제출 (현재: {HH}세대)"),
        (20, "공동주택 결로 방지 설계",     "가" if has_gong and HH>=500 else "부", "주택건설기준 14조", "착공신고 시", f"500세대 이상 공동주택 (현재: {HH}세대)"),
        (21, "장수명 주택 건설인증",        "가" if has_gong and HH>=1000 else "부", "주택건설기준 65조", "사업계획승인 신청 전", f"1,000세대↑ 공동주택, 설계기준강도 21MPa 상향 (현재: {HH}세대)"),
        (22, "교육환경평가서",             "가" if is_edu and (T>=100000 or TF>21) else "부", "도정법 28조", "사업계획 승인 전", f"학교 200m이내 + 10만㎡ 또는 21층 초과, 유치원·대안학교 포함 (현재: {T:,}㎡, {TF}층)"),
        (23, "에너지소비 총량제(ECO2)",    "가" if (excl_A>=3000 and any(u in ["업무시설", "교육연구시설(연구소·도서관 제외)"] for u in usages)) or (is_public and T>=500) else "부", "에너지설계기준", "사업계획승인신청시", f"3000㎡↑ 업무/교육, 500㎡↑ 공공 (현재: {excl_A:,}㎡, {T:,}㎡)"),
        (24, "제로에너지건축물 (공공) ※17번 병합", "부", "녹색건축물법", "-", "※ v8.0: 17번 항목으로 병합됨 (별도 항목 비활성화)"),
        (25, "건축물의 경관심의대상",       "가" if is_landscape else "부",      "경관조례",              "건축심의시",            "경관지구 및 중점경관관리구역"),
        (26, "성능위주 소방설계",           "가" if (has_gong and (TF>=50 or H>=200)) or (not (has_gong and len(usages)==1) and (TF>=30 or H>=120)) else "부", "소방시설법", "건축심의 신청전", f"아파트 50층/200m↑ / 일반 30층/120m↑ (현재: {H}m, {TF}층)"),
        (27, "풍동실험",                   "판단 유보",                         "건축구조기준",           "구조 심의 시",          "협력업체 확인필요"),
        (28, "건축물 교통영향평가",         "판단 유보",                         "도시교통정비법",         "-",                     "50층↑ 대단지 아파트 등 상급관청 단독 심의 격상 대상 여부 확인"),
        (29, "장애물 없는 생활환경(BF) 인증", "가" if is_public or "신축 공공건축물/교통수단·여객시설" in usages or TF>=50 or H>=200 or is_under_link else "부", "이동편의증진법", "예비:본인증전 / 본:사용승인후", "신축 공공·여객시설 + 민간 초고층(50층/200m↑) 및 지하연계 복합건축물 의무화"),
        (30, "에너지사용계획 협의",         "가" if (is_public and T >= 300000) or (not is_public and T >= 600000) else "부", "에너지이용합리화법", "사업승인 신청 전", f"공공 30만㎡↑ / 민간 60만㎡↑ (현재: {T:,}㎡, {'공공' if is_public else '민간'})"),
        (31, "건축물 안전영향평가",         "가" if TF>=50 or H>=200 or (GF>=16 and T>=100000) else "부", "건축법 13조의2", "건축 허가 전", f"50층/200m↑ 또는 16층+10만㎡ (현재: {TF}층, {H}m, {T:,}㎡)"),
        (32, "사전재난영향성검토",          "가" if TF>=50 or H>=200 or is_under_link else "부", "초고층재난법", "허가등을 하기 전", f"50층/200m↑ 또는 지하연계복합 (현재: {TF}층, {H}m)"),
        (33, "개발사업의 경관심의대상",     "가" if L >= 30000 else "부",        "경관법 시행령",          "도시계획심의시",         f"대지면적 3만㎡↑ 개발사업 (현재: {L:,}㎡)"),
        (34, "지구단위계획구역 지정",       _item34,                             "도시계획조례",           "도시계획심의시",         f"공동주택 300세대↑ (현재: {HH}세대)"),
        (35, "지구단위계획변경",            "가" if _item34 == "가" else "부",   "관련 규정",             "건축심의 전",            "34번 지정 시 연계 발주"),
        (36, "사전경관계획 심의",           "가" if L >= 300000 or T >= 200000 else "부", "경관법 시행령", "도시계획심의시", f"대지 30만㎡↑ 또는 연면적 20만㎡↑ (현재: {L:,}㎡, {T:,}㎡)"),
        (37, "문화재지표조사(현상변경)",    "가" if is_heritage or L>=30000 else "부", "국가유산영향진단법", "실시계획 작성 완료전", f"문화재 200m이내 또는 대지 3만㎡↑ (현재: {L:,}㎡)"),
        (38, "소규모 재해영향평가",         "가" if 5000 <= L < 50000 else "부", "자연재해대책법",         "사업계획승인전",         f"대지면적 5천~5만㎡ (현재: {L:,}㎡)"),
        (39, "재해영향평가",               "가" if L >= 50000 else "부",        "자연재해대책법",         "사업계획승인전",         f"대지면적 5만㎡↑ (현재: {L:,}㎡)"),
        (40, "환경영향평가",               "가" if L >= 125000 else "부",       "환경영향평가법",         "사업계획승인전",         f"사업면적 12만5천㎡↑ (현재: {L:,}㎡)"),
        (41, "소규모 환경영향평가",         "가" if (urban == "도시지역" and 5000 <= L < 60000) or (urban == "도시외지역" and 5000 <= L < 10000) else "부", "환경영향평가법", "사업계획승인전", f"도시지역 5천~6만㎡ / 도시외지역 5천~1만㎡ (현재: {L:,}㎡, {urban})"),
        (42, "지하철(철도) 영향성 검토",   "가" if 0 < rail_D <= 30 else "부",  "철도안전법",            "-",                     f"철도경계선 30m 이내 (현재: {rail_D}m)")
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
    display_data = []
    cnts = {"target": 0, "non": 0, "hold": 0}

    for i in items:
        was_hold = i[0] in ORIGINALLY_HOLD_NOS and i[2] != "판단 유보"
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
                              "color": color, "tag": tag, "was_hold": was_hold})

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

    st.subheader(f"📊 [ ◯ 대상: {cnts['target']} ]  [ ✕ 비대상: {cnts['non']} ]  [ ! 유보: {cnts['hold']} ]")

    # 헤더
    hcols = st.columns([1, 4, 2, 3, 3, 5])
    for h, t in zip(hcols, ["No", "분석 항목", "결과", "제출시기", "법적 근거", "비고"]):
        h.markdown(f"**{t}**")

    for row in display_data:
        cols = st.columns([1, 4, 2, 3, 3, 5])
        cols[0].write(f"**{row['No']}**")
        cols[1].write(row['분석 항목'])
        if row.get('was_hold'):
            cols[2].markdown(f"<span style='background:#FFFF00;color:{row['color']};font-weight:bold;padding:2px 6px;border-radius:3px;'>{row['결과']}</span>", unsafe_allow_html=True)
        else:
            cols[2].markdown(f"<span style='color:{row['color']}; font-weight:bold;'>{row['결과']}</span>", unsafe_allow_html=True)
        cols[3].write(row['제출시기'])
        cols[4].write(row['법적 근거'])
        cols[5].write(row['비고'])

    # 대전 특화 항목 표시
    if is_daejeon and daejeon_display:
        st.divider()
        st.markdown("### 🏙️ 대전광역시 특화 조례 항목")
        hcols2 = st.columns([1, 4, 2, 3, 3, 5])
        for h, t in zip(hcols2, ["No", "분석 항목", "결과", "제출시기", "법적 근거", "비고"]):
            h.markdown(f"**{t}**")
        for row in daejeon_display:
            cols = st.columns([1, 4, 2, 3, 3, 5])
            cols[0].write(f"**{row['No']}**")
            cols[1].write(row['분석 항목'])
            if row.get('was_hold'):
                cols[2].markdown(f"<span style='background:#FFFF00;color:{row['color']};font-weight:bold;padding:2px 6px;border-radius:3px;'>{row['결과']}</span>", unsafe_allow_html=True)
            else:
                cols[2].markdown(f"<span style='color:{row['color']}; font-weight:bold;'>{row['결과']}</span>", unsafe_allow_html=True)
            cols[3].write(row.get('제출시기', '-'))
            cols[4].write(row['법적 근거'])
            cols[5].write(row['비고'])

    def make_pdf():
        pdf = FPDF(); pdf.add_page()
        if os.path.exists(font_path): pdf.add_font("K", "", font_path); pdf.set_font("K", size=10)

        # 제목
        pdf.set_font("K", size=13)
        pdf.cell(0, 10, "■ 사업승인 체크 리스트 결과보고서", ln=True, align='C')
        pdf.set_font("K", size=9)
        pdf.set_text_color(0, 82, 204)
        pdf.cell(0, 6, f"분석 요약 - 대상: {cnts['target']} / 비대상: {cnts['non']} / 유보: {cnts['hold']}", ln=True, align='R')

        # 기본 정보 박스
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("K", size=9)
        pdf.set_fill_color(240, 245, 255)
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
        pdf.cell(0, 5, f"Copyright © {datetime.now().year} (주)아이팝엔지니어링  |  사업승인 체크리스트 Web v8.1  |  All Rights Reserved.", ln=True, align='C')
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("K", size=9)
        pdf.ln(2)

        # 체크리스트 테이블
        pdf.set_fill_color(0, 82, 204)
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
                pdf.set_fill_color(0, 82, 204)
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
                    if r['tag'] == "target": pdf.set_text_color(0, 82, 204)
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
            pdf.set_fill_color(0, 100, 60)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("K", size=10)
            pdf.cell(0, 8, "  ▶ 대전광역시 특화 조례 항목", ln=True, fill=True)
            pdf.set_text_color(255, 255, 255)
            pdf.set_fill_color(0, 100, 60)
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
                       file_name=f"사업승인체크리스트_v8_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                       mime="application/pdf", type="primary", use_container_width=True)
else:
    st.info("👈 좌측 하단의 **[🔍 분석 실행]** 버튼을 누르시면 42개 항목 분석 결과가 여기에 출력됩니다.")
