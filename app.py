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
from datetime import datetime  # 에러 원인 완벽 복구

st.set_page_config(page_title="사업승인 체크 v8.0_Boss", layout="wide")
font_path = "fonts/NanumGothic.ttf"

# ── 도메인 잠금: salgi-bot.github.io 이외 접근 차단 ──────────────────
_ALLOWED_DOMAIN = "salgi-bot.github.io"
try:
    import streamlit.components.v1 as _stc
    _domain_check_html = f"""
    <script>
    (function(){{
        var host = window.location.hostname;
        if (host !== "" && host !== "localhost" && host !== "127.0.0.1" && !host.endsWith("{_ALLOWED_DOMAIN}")) {{
            document.body.innerHTML = "<div style='display:flex;align-items:center;justify-content:center;height:100vh;font-family:sans-serif;'>"
                + "<div style='text-align:center;color:#c00;'>"
                + "<h2>⛔ 접근 제한</h2>"
                + "<p>이 서비스는 허가된 도메인에서만 사용 가능합니다.</p>"
                + "<p>Copyright &copy; (주)아이팝엔지니어링</p>"
                + "</div></div>";
            document.head.innerHTML = "";
        }}
    }})();
    </script>
    """
    _stc.html(_domain_check_html, height=0)
except Exception:
    pass
# ──────────────────────────────────────────────────────────────────────

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
            + ' (주)아이팝엔지니어링 &nbsp;|&nbsp; 사업승인 체크리스트 Web v8.0 &nbsp;|&nbsp; All Rights Reserved.';
        document.body.appendChild(el);
    }
    if(document.readyState === 'loading'){
        document.addEventListener('DOMContentLoaded', injectFooter);
    } else {
        injectFooter();
    }
    // 리렌더링 후에도 유지
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
# ──────────────────────────────────────────────────────────────────────

# ── 텔레그램 봇 설정 ───────────────────────────────────────────
import urllib.request, urllib.parse, json, random, string

def _tg_send(token, chat_id, text):
    """텔레그램 메시지 발송"""
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = urllib.parse.urlencode({"chat_id": chat_id, "text": text, "parse_mode": "HTML"}).encode()
        urllib.request.urlopen(url, data=data, timeout=10)
    except Exception as e:
        st.warning(f"텔레그램 발송 오류: {e}")

def _gen_code():
    """8자리 랜덤 코드 생성"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

try:
    TG_TOKEN   = st.secrets["TG_TOKEN"]
    TG_CHAT_ID = st.secrets["TG_CHAT_ID"]
    valid_codes_raw = st.secrets.get("ACCESS_CODES", "")
    valid_codes = [c.strip() for c in valid_codes_raw.split(",") if c.strip()]
except Exception:
    TG_TOKEN = TG_CHAT_ID = ""
    valid_codes = []

_MAX_ATTEMPTS = 5

# session_state 초기화
for _k, _v in [("auth_ok", False), ("auth_attempts", 0),
                ("show_request", False), ("req_sent", False),
                ("show_admin", False)]:
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ── 인증 화면 ──────────────────────────────────────────────────
if not st.session_state.auth_ok:

    st.markdown("""
    <div style='max-width:440px;margin:60px auto 0;padding:40px 36px 30px;border-radius:14px;
                box-shadow:0 4px 24px rgba(0,0,0,0.10);background:white;text-align:center;'>
        <h2 style='color:#0052CC;margin:0 0 4px;'>🔐 사업승인 체크리스트</h2>
        <p style='color:#777;font-size:13px;margin:0 0 28px;'>(주)아이팝엔지니어링 · 승인된 사용자만 이용 가능</p>
    </div>
    """, unsafe_allow_html=True)

    tab_login, tab_request = st.tabs(["🔑 코드 입력", "📋 사용 신청"])

    # ── 탭1: 코드 입력 ──
    with tab_login:
        remaining = _MAX_ATTEMPTS - st.session_state.auth_attempts
        if remaining <= 0:
            st.error("⛔ 입력 횟수 초과로 접근이 차단되었습니다. 관리자에게 문의하세요.")
            st.stop()

        code_input = st.text_input("승인 코드", type="password", max_chars=8,
                                   placeholder="발급받은 8자리 코드 입력",
                                   help=f"남은 시도: {remaining}회")
        if st.button("✅ 입장", use_container_width=True, type="primary"):
            if code_input.strip().upper() in [c.upper() for c in valid_codes]:
                st.session_state.auth_ok = True
                st.rerun()
            else:
                st.session_state.auth_attempts += 1
                left = _MAX_ATTEMPTS - st.session_state.auth_attempts
                if left <= 0:
                    st.error("⛔ 입력 횟수 초과로 접근이 차단되었습니다.")
                else:
                    st.error(f"❌ 코드가 올바르지 않습니다. (남은 시도: {left}회)")

    # ── 탭2: 사용 신청 ──
    with tab_request:
        if st.session_state.req_sent:
            st.success("✅ 신청이 완료됐습니다! 관리자 승인 후 코드를 전달드립니다.")
        else:
            req_name    = st.text_input("이름 *", placeholder="홍길동")
            req_contact = st.text_input("연락처 * (이메일 또는 전화번호)", placeholder="010-0000-0000")
            req_org     = st.text_input("소속 (선택)", placeholder="회사명 또는 기관명")

            if st.button("📨 사용 신청하기", use_container_width=True, type="primary"):
                if not req_name or not req_contact:
                    st.error("이름과 연락처는 필수입니다.")
                else:
                    msg = (f"📋 <b>사업승인 체크리스트 사용 신청</b>\n\n"
                           f"👤 이름: {req_name}\n"
                           f"📞 연락처: {req_contact}\n"
                           f"🏢 소속: {req_org if req_org else '미입력'}\n\n"
                           f"✅ 승인하시려면 아래 관리자 페이지에서 코드를 발급해주세요.")
                    _tg_send(TG_TOKEN, TG_CHAT_ID, msg)
                    st.session_state.req_sent = True
                    st.rerun()

    # ── 관리자 패널 (숨김) ──
    with st.expander("🔧 관리자", expanded=False):
        admin_pw = st.text_input("관리자 비밀번호", type="password", key="admin_pw")
        try:
            admin_secret = st.secrets.get("ADMIN_PW", "")
        except Exception:
            admin_secret = ""

        if admin_pw == admin_secret and admin_secret:
            st.success("✅ 관리자 모드")
            st.markdown("**신규 코드 발급**")
            new_user = st.text_input("수신자 이름", key="new_user")
            if st.button("🎲 코드 생성 및 텔레그램 발송", key="gen_code"):
                new_code = _gen_code()
                msg = (f"🔑 <b>승인 코드 발급</b>\n\n"
                       f"👤 수신자: {new_user}\n"
                       f"🔐 코드: <code>{new_code}</code>\n\n"
                       f"⚙️ Streamlit Secrets의 ACCESS_CODES에 추가해주세요:\n"
                       f"<code>{new_code}</code>")
                _tg_send(TG_TOKEN, TG_CHAT_ID, msg)
                st.info(f"📤 발급된 코드: **{new_code}**\n\nStreamlit Secrets > ACCESS_CODES 에 추가 후 사용자에게 전달하세요.")
        elif admin_pw:
            st.error("비밀번호가 틀렸습니다.")

    st.markdown("""
    <p style='text-align:center;color:#bbb;font-size:11px;margin-top:20px;'>
        Copyright © 2024 (주)아이팝엔지니어링 | All Rights Reserved.
    </p>
    """, unsafe_allow_html=True)
    st.stop()
# ──────────────────────────────────────────────────────────────────────

# 상태 저장소 초기화 (분석 버튼 클릭 여부 저장)
if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False

st.sidebar.markdown("### 🔄 시스템 제어")
col_btn1, col_btn2 = st.sidebar.columns(2)

# [수정 1] 리셋 버튼
if col_btn1.button("🔄 초기화", use_container_width=True):
    st.session_state.clear()
    st.rerun()

# [수정 2] 분석 실행 버튼 (누르면 상태가 True로 바뀜)
if col_btn2.button("🔍 분석 실행", type="primary", use_container_width=True):
    st.session_state.analyzed = True

st.sidebar.divider()

with st.sidebar:
    st.header("📝 기본 정보 입력")
    today_str = datetime.now().strftime("%Y년 %m월 %d일")
    st.markdown(f"<p style='color:#0052CC;font-size:13px;font-weight:bold;'>📅 작성일: {today_str}</p>", unsafe_allow_html=True)
    p_name = st.text_input("용역명", "신규 개발사업 프로젝트")
    address = st.text_input("주소", "대전광역시 서구 월드컵대로484번안길 10, 3층")

    # 총공사비 - 50억 미만 / 이상 선택
    cost_opt = st.selectbox("총공사비", ["50억원 미만", "50억원 이상"])
    const_cost = 30 if cost_opt == "50억원 미만" else 50  # 내부 계산용

    st.divider()
    # 면적 입력
    col1, col2 = st.columns(2)
    land_area  = col1.number_input("대지면적(㎡)", value=10000, step=1, format="%d")
    total_area = col2.number_input("연면적(㎡)", value=50000, step=1, format="%d")
    under_area = st.number_input("지하층 연면적(㎡)", value=10000, step=1, format="%d")
    above_area = total_area - under_area
    st.text_input("지상층 연면적(㎡)", f"{above_area:,}", disabled=True)
    parking    = st.number_input("주차장(기계실) 연면적(㎡)", value=10000, step=1, format="%d")
    excl_area  = total_area - parking
    st.text_input("제외 면적(㎡)", f"{excl_area:,}", disabled=True)

    st.divider()
    # 건폐율/용적률/건축면적
    col_a, col_b = st.columns(2)
    build_coverage = col_a.number_input("건폐율(%)", value=60, step=1, format="%d")
    floor_area_ratio = col_b.number_input("용적률(%)", value=250, step=1, format="%d")
    arch_area = st.number_input("건축면적(㎡)", value=3000, step=1, format="%d")

    st.divider()
    # 층수/높이/굴착
    col3, col4 = st.columns(2)
    b_floors = col3.number_input("지하층수", value=2)
    g_floors = col4.number_input("지상층수", value=20)
    max_h    = st.number_input("최고높이(m)", value=60)
    depth    = st.number_input("굴착깊이(m)", value=12)
    households = st.number_input("세대수", value=500)

    st.divider()
    edu        = st.selectbox("교육시설", ["해당없음", "200m 이내 존재"])
    heritage   = st.selectbox("문화재 시설", ["해당없음", "200m 이내"])
    landsc     = st.selectbox("경관지구", ["해당없음", "해당"])
    under_link = st.selectbox("지하연계 복합건축", ["해당없음", "해당"])
    urban      = st.selectbox("지역구분", ["도시지역", "도시외지역"])
    rail       = st.number_input("철도거리(m)", value=0)
    public_inst = st.selectbox("공공기관 여부", ["민간", "공공기관"])

    usage_options = ["공동주택(아파트)", "주상복합", "오피스텔", "다가구주택", "연립주택 및 다세대주택", "제1종 근린생활시설(일용품 소매점)", "제2종 근린생활시설(다중생활시설)", "문화 및 집회시설(동·식물원 제외)", "교육연구시설(연구소·도서관 제외)", "노유자시설", "수련시설", "업무시설", "신축 공공건축물/교통수단·여객시설"]
    usages = st.multiselect("용도", usage_options, default=["공동주택(아파트)"])

st.title("■ 사업승인 체크 리스트_Web v8.0")

# 분석 실행 버튼을 눌렀을 때만 아래 내용이 화면에 출력됨
if st.session_state.analyzed:
    L, T, D, H, HH = land_area, total_area, depth, max_h, households
    BF, GF = b_floors, g_floors
    TF = BF + GF
    cost = const_cost * 100000000
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
    <tr><td style='color:#555;'>🚗 주차장(기계실)</td><td><b>{parking:,}㎡</b></td>
        <td style='color:#555;'>📐 제외면적</td><td><b>{excl_A:,}㎡</b></td></tr>
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
        (30, "에너지사용계획 협의",         "판단 유보",                         "에너지이용합리화법",      "사업승인 신청 전",       "연면적 약 30만㎡↑ 해당 예상 (민간 60만㎡↑)"),
        (31, "건축물 안전영향평가",         "가" if TF>=50 or H>=200 or (GF>=16 and T>=100000) else "부", "건축법 13조의2", "건축 허가 전", f"50층/200m↑ 또는 16층+10만㎡ (현재: {TF}층, {H}m, {T:,}㎡)"),
        (32, "사전재난영향성검토",          "가" if TF>=50 or H>=200 or is_under_link else "부", "초고층재난법", "허가등을 하기 전", f"50층/200m↑ 또는 지하연계복합 (현재: {TF}층, {H}m)"),
        (33, "개발사업의 경관심의대상",     "판단 유보",                         "경관법 시행령",          "도시계획심의시",         f"대지면적 3만㎡↑ 개발사업 (현재: {L:,}㎡)"),
        (34, "지구단위계획구역 지정",       "판단 유보",                         "도시계획조례",           "도시계획심의시",         "300세대↑ 아파트 또는 상업지역 200세대↑ 등"),
        (35, "지구단위계획변경",            "판단 유보",                         "관련 규정",             "건축심의 전",            "34번 지정 시 연계 발주"),
        (36, "사전경관계획 심의",           "판단 유보",                         "경관법 시행령",          "도시계획심의시",         f"대지 30만㎡↑ 또는 연면적 20만㎡↑ (현재: {L:,}㎡, {T:,}㎡)"),
        (37, "문화재지표조사(현상변경)",    "가" if is_heritage or L>=30000 else "부", "국가유산영향진단법", "실시계획 작성 완료전", f"문화재 200m이내 또는 대지 3만㎡↑ (현재: {L:,}㎡)"),
        (38, "소규모 재해영향평가",         "판단 유보",                         "자연재해대책법",         "사업계획승인전",         f"대지면적 5천~5만㎡ (현재: {L:,}㎡)"),
        (39, "재해영향평가",               "판단 유보",                         "자연재해대책법",         "사업계획승인전",         f"대지면적 5만㎡↑ (현재: {L:,}㎡)"),
        (40, "환경영향평가",               "판단 유보",                         "환경영향평가법",         "사업계획승인전",         f"사업면적 12만5천㎡↑ (현재: {L:,}㎡)"),
        (41, "소규모 환경영향평가",         "판단 유보",                         "환경영향평가법",         "사업계획승인전",         "도시지역 6만㎡ 미만 / 녹지지역 1만㎡ 미만 (분할 합산 기준)"),
        (42, "지하철(철도) 영향성 검토",   "가" if 0 < rail_D <= 30 else "부",  "철도안전법",            "-",                     f"철도경계선 30m 이내 (현재: {rail_D}m)")
    ]

    # ── 대전광역시 특화 조례 항목 (주소에 "대전" 포함 시 추가) ──────────────
    is_daejeon = "대전" in address
    daejeon_items = []
    if is_daejeon:
        dj_no_base = 43  # 43번부터 시작
        # 대전 특화 1: 민간건축물 녹색건축 설계기준
        daejeon_items.append((dj_no_base, "민간건축물 녹색건축 설계기준 [대전]",
            "가" if has_gong or excl_A >= 500 else "판단 유보",
            "대전광역시 조례", "사업계획승인신청시",
            f"주거(세대수)/비주거(연면적) 4개 군 분류, 환경·에너지·신재생에너지 기준 엄격화 (현재: {HH}세대, {excl_A:,}㎡)"))
        # 대전 특화 2: 건축물 경관심의
        daejeon_items.append((dj_no_base+1, "건축물 경관심의 [대전]",
            "가" if TF >= 21 or T >= 100000 else "판단 유보",
            "대전광역시 경관조례", "건축심의시",
            f"21층↑ 또는 10만㎡↑ 원칙, 서구 등 기초자치단체 조례에 따라 미만도 대상 가능 → 대지 위치 확인 필수 (현재: {TF}층, {T:,}㎡)"))
        # 대전 특화 3: 범죄예방 도시디자인 (CPTED)
        daejeon_items.append((dj_no_base+2, "범죄예방 도시디자인(CPTED) [대전]",
            "가" if any(u in c10_targets for u in usages) else "부",
            "대전광역시 CPTED 조례", "허가신청",
            "5년 단위 기본계획, 출입구·울타리·조경 등 자연적 감시·접근통제 자체방어적 디자인 기준 적용"))
    # ──────────────────────────────────────────────────────────────────────

    display_data = []
    cnts = {"target": 0, "non": 0, "hold": 0}

    for i in items:
        if i[2] == "가":
            res, color, tag = ("◯ 소규모" if i[0] == 38 else "◯ 대상"), "#0052CC", "target"
            cnts["target"] += 1
        elif i[2] == "판단 유보":
            res, color, tag = "! 판단 유보", "#FF9800", "hold"
            cnts["hold"] += 1
        else:
            res, color, tag = "✕ 비대상", "#B0B0B0", "non"
            cnts["non"] += 1
        display_data.append({"No": i[0], "분석 항목": i[1], "결과": res,
                              "제출시기": i[4], "법적 근거": i[3], "비고": i[5],
                              "color": color, "tag": tag})

    # 대전 특화 항목 추가
    daejeon_display = []
    for i in daejeon_items:
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
                                 "color": color, "tag": tag})

    st.subheader(f"📊 [ ◯ 대상: {cnts['target']} ]  [ ✕ 비대상: {cnts['non']} ]  [ ! 유보: {cnts['hold']} ]")

    # 헤더
    hcols = st.columns([1, 4, 2, 3, 3, 5])
    for h, t in zip(hcols, ["No", "분석 항목", "결과", "제출시기", "법적 근거", "비고"]):
        h.markdown(f"**{t}**")

    for row in display_data:
        cols = st.columns([1, 4, 2, 3, 3, 5])
        cols[0].write(f"**{row['No']}**")
        cols[1].write(row['분석 항목'])
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
            ("주차장(기계실)", f"{parking:,}㎡", "제외면적", f"{excl_A:,}㎡"),
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
        pdf.cell(0, 5, f"Copyright © {datetime.now().year} (주)아이팝엔지니어링  |  사업승인 체크리스트 Web v8.0  |  All Rights Reserved.", ln=True, align='C')
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
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("K", size=9)
            pdf.cell(col_w[0], 7, str(r['No']), border=1, align='C')
            pdf.cell(col_w[1], 7, r['분석 항목'], border=1)
            if r['tag'] == "target": pdf.set_text_color(0, 82, 204)
            elif r['tag'] == "hold": pdf.set_text_color(255, 152, 0)
            else: pdf.set_text_color(160, 160, 160)
            pdf.cell(col_w[2], 7, r['결과'], border=1, align='C')
            pdf.set_text_color(0, 0, 0)
            pdf.cell(col_w[3], 7, r.get('제출시기', '-'), border=1)
            pdf.cell(col_w[4], 7, r['법적 근거'], border=1)
            remark_text = str(r['비고'])
            remark_fs = 9
            while pdf.get_string_width(remark_text) > col_w[5] - 2 and remark_fs > 5:
                remark_fs -= 0.5
                pdf.set_font("K", size=remark_fs)
            pdf.cell(col_w[5], 7, remark_text, border=1)
            pdf.set_font("K", size=9)
            pdf.ln()

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
