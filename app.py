import streamlit as st
import pandas as pd
from fpdf import FPDF
import os
from datetime import datetime  # 에러 원인 완벽 복구

st.set_page_config(page_title="사업승인 체크 v7.5_Boss", layout="wide")
font_path = "fonts/NanumGothic.ttf"

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
    p_name = st.text_input("용역명", "신규 개발사업 프로젝트")
    address = st.text_input("주소", "대전광역시 서구 월드컵대로484번안길 10, 3층")
    const_cost = st.number_input("총공사비(억원)", value=50)
    col1, col2 = st.columns(2)
    land_area = col1.number_input("대지면적(㎡)", value=10000)
    total_area = col2.number_input("연면적(㎡)", value=50000)
    col3, col4 = st.columns(2)
    b_floors = col3.number_input("지하층수", value=2)
    g_floors = col4.number_input("지상층수", value=20)
    max_h = st.number_input("최고높이(m)", value=60)
    depth = st.number_input("굴착깊이(m)", value=12)
    households = st.number_input("세대수", value=500)
    parking = st.number_input("주차장 연면적(㎡)", value=10000)
    excl_area = total_area - parking
    st.text_input("제외 면적(㎡)", f"{excl_area:,}", disabled=True)
    
    edu = st.selectbox("교육시설", ["해당없음", "200m 이내 존재"])
    landsc = st.selectbox("경관지구", ["해당없음", "해당"])
    under_link = st.selectbox("지하연계 복합건축", ["해당없음", "해당"])
    urban = st.selectbox("지역구분", ["도시지역", "도시외지역"])
    rail = st.number_input("철도거리(m)", value=0)
    public_inst = st.selectbox("공공기관 여부", ["민간", "공공기관"])
    
    usage_options = ["공동주택(아파트)", "주상복합", "오피스텔", "다가구주택", "연립주택 및 다세대주택", "제1종 근린생활시설(일용품 소매점)", "제2종 근린생활시설(다중생활시설)", "문화 및 집회시설(동·식물원 제외)", "교육연구시설(연구소·도서관 제외)", "노유자시설", "수련시설", "업무시설", "신축 공공건축물/교통수단·여객시설"]
    usages = st.multiselect("용도", usage_options, default=["공동주택(아파트)"])

st.title("■ 사업승인 체크 리스트_Web v7.5")

# [수정 3] 분석 실행 버튼을 눌렀을 때만 아래 내용이 화면에 출력됨
if st.session_state.analyzed:
    L, T, D, H, HH = land_area, total_area, depth, max_h, households
    BF, GF = b_floors, g_floors
    TF = BF + GF
    cost = const_cost * 100000000
    excl_A = excl_area
    rail_D = rail
    
    is_edu = (edu == "200m 이내 존재")
    is_landscape = (landsc == "해당")
    is_under_link = (under_link == "해당")
    is_public = (public_inst == "공공기관")
    
    has_gong = any(u in ["공동주택(아파트)", "다가구주택", "연립주택 및 다세대주택"] for u in usages)
    has_ju = "주상복합" in usages
    is_biz_app = (has_gong and HH >= 20) or (has_ju and HH >= 300)
    c10_targets = ["다가구주택", "공동주택(아파트)", "연립주택 및 다세대주택", "제1종 근린생활시설(일용품 소매점)", "제2종 근린생활시설(다중생활시설)", "문화 및 집회시설(동·식물원 제외)", "교육연구시설(연구소·도서관 제외)", "노유자시설", "수련시설"]

    # [수정 4] 42개 항목 완벽 복구
    items = [
        (1, "구조 성능기반설계", "판단 유보", "내진설계 지침", "구조 심의 시"),
        (2, "설계안전보건대장", "가" if cost >= 5000000000 else "부", "안전보건대장 고시", f"공사비 50억 이상 (현재: {const_cost}억원)"),
        (3, "단지내 주변일조.일영분석", "가" if has_gong else "부", "건축법 제61조", "공동주택이면 해당"),
        (4, "단지특화디자인(색채 등)", "가" if has_gong or has_ju or "오피스텔" in usages else "부", "심의 기준", "공동/주상/오피스텔 해당"),
        (5, "소규모 지하안전영향평가", "가" if 10 <= D < 20 else "부", "지하안전법", f"굴착 10~20m 미만 (현재: {D}m)"),
        (6, "지하안전영향평가", "가" if D >= 20 else "부", "지하안전법", f"굴착 20m 이상 (현재: {D}m)"),
        (7, "착공후 지하안전영향평가", "가" if D >= 20 else "부", "지하안전법", f"굴착 20m 이상 (현재: {D}m)"),
        (8, "현황측량(지장물조사)", "가" if D >= 10 else "부", "관련 규정", f"지하안전평가 대상 시 해당 (현재: {D}m)"),
        (9, "지질조사", "가", "지하안전 매뉴얼", "무조건 해당 (지안평 대상시 3공 발주)"),
        (10, "흙막이 설계", "가" if BF > 0 else "부", "건축법 시행령", f"지하층 있으면 해당 (현재: 지하 {BF}층)"),
        (11, "수량산출서", "가" if has_gong and HH >= 20 else "부", "제출 기준", f"공동주택 20세대 이상 사업승인 (현재: {HH}세대)"),
        (12, "단지내 소음예측평가", "가" if is_biz_app else "부", "주택건설기준 9조", "사업계획승인 대상 해당"),
        (13, "범죄예방 건축기준", "가" if any(u in c10_targets for u in usages) else "부", "건축법 53조의2", "특정 9개 용도 해당"),
        (14, "에너지절약설계기준", "가" if excl_A >= 500 or has_gong else "부", "녹색건축물법", f"비주거 500㎡이상 또는 공동주택 (현재: {excl_A:,}㎡)"),
        (15, "수질오염물질 총량제", "가" if (has_gong and HH>=30) or (has_ju and HH>=30) else "부", "오염총량방침", f"30세대 이상 공동주택/주상복합 (현재: {HH}세대)"),
        (16, "녹색건축인증", "가" if ((has_gong and HH>=30) or excl_A>=500) else "부", "녹색건축물법", f"주거30세대/비주거500㎡ (현재: {HH}세대, {excl_A:,}㎡)"),
        (17, "제로에너지건축물 인증", "가" if (has_gong and HH>=30) or (T>=1000 and ("업무시설" in usages or is_public)) else "부", "녹색건축물법", f"주거 30세대 / 1000㎡이상 업무,공공 (현재: {HH}세대, {T:,}㎡)"),
        (18, "에너지절약형 친환경주택", "가" if has_gong and HH>=30 and is_biz_app else "부", "주택건설기준 64조", f"30세대 이상 사업승인 공동주택 (현재: {HH}세대)"),
        (19, "건강친화형 주택 건설기준", "가" if has_gong and HH>=500 else "부", "주택건설기준 65조", f"500세대 이상 공동주택 (현재: {HH}세대)"),
        (20, "공동주택 결로 방지 설계", "가" if has_gong and HH>=500 else "부", "주택건설기준 14조", f"500세대 이상 공동주택 (현재: {HH}세대)"),
        (21, "장수명 주택 건설인증", "가" if has_gong and HH>=1000 else "부", "주택건설기준 65조", f"1,000세대 이상 공동주택 (현재: {HH}세대)"),
        (22, "교육환경평가서", "가" if is_edu and (T>=100000 or TF>21) else "부", "도정법 28조", f"200m이내 학교 + 10만㎡ 또는 21층 초과 (현재: {T:,}㎡, {TF}층)"),
        (23, "에너지소비 총량제(ECO2)", "가" if (excl_A>=3000 and any(u in ["업무시설", "교육연구시설(연구소·도서관 제외)"] for u in usages)) or (is_public and T>=500) else "부", "에너지설계기준", f"3000㎡이상 업무/교육, 500㎡이상 공공 (현재: {excl_A:,}㎡, {T:,}㎡)"),
        (24, "제로에너지건축물 (공공)", "가" if is_public and ((has_gong and HH>=30) or excl_A>=500) else "부", "녹색건축물법", f"공공기관 공동주택 30세대/비주거 500㎡ (현재: {HH}세대, {excl_A:,}㎡)"),
        (25, "건축물의 경관심의대상", "가" if is_landscape else "부", "경관조례", "경관지구 및 중점경관관리구역"),
        (26, "소방성능위주설계", "부" if (has_gong and len(usages)==1) else ("가" if T>=200000 or H>=120 or TF>=30 else "부"), "소방시설법", f"20만㎡/120m/30층 이상(공동주택 제외) (현재: {T:,}㎡, {H}m, {TF}층)"),
        (27, "풍동실험", "판단 유보", "건축구조기준", "협력업체 확인필요"),
        (28, "건축물 교통영향평가", "판단 유보", "도시교통정비법", "협력업체 확인필요"),
        (29, "장애물 없는 생활환경(BF)", "가" if is_public or "신축 공공건축물/교통수단·여객시설" in usages else "부", "이동편의증진법", "신축 공공 / 여객시설"),
        (30, "에너지사용계획 협의", "판단 유보", "에너지이용합리화법", "협력업체 확인필요"),
        (31, "건축물 안전영향평가", "가" if TF>=50 or H>=200 or (GF>=16 and T>=100000) else "부", "건축법 13조의2", f"50층/200m 또는 16층+10만㎡ (현재: {TF}층, {H}m, {T:,}㎡)"),
        (32, "사전재난영향성검토", "가" if TF>=50 or H>=200 or is_under_link else "부", "초고층재난법", f"50층/200m 또는 지하연계복합 (현재: {TF}층, {H}m)"),
        (33, "개발사업의 경관심의대상", "판단 유보", "경관법 시행령", "협력업체 확인필요"),
        (34, "지구단위계획구역 지정", "판단 유보", "도시계획조례", "협력업체 확인필요"),
        (35, "지구단위계획변경", "판단 유보", "관련 규정", "협력업체 확인필요"),
        (36, "사전경관계획 심의", "판단 유보", "경관법 시행령", "협력업체 확인필요"),
        (37, "문화재지표조사", "가" if L>=30000 else "부", "국가유산영향진단법", f"대지면적 3만㎡ 이상 (현재: {L:,}㎡)"),
        (38, "소규모 재해영향평가", "판단 유보", "자연재해대책법", f"대지면적 5천~5만㎡ (현재: {L:,}㎡)"),
        (39, "재해영향평가", "판단 유보", "자연재해대책법", f"대지면적 5만㎡ 이상 (현재: {L:,}㎡)"),
        (40, "환경영향평가", "판단 유보", "환경영향평가법", f"면적 12만5천㎡ 이상 (현재: {L:,}㎡)"),
        (41, "소규모 환경영향평가", "판단 유보", "환경영향평가법", "협력업체 확인필요"),
        (42, "지하철(철도) 영향성 검토", "가" if 0 < rail_D <= 30 else "부", "철도안전법", f"철도경계선 30m 이내 (현재: {rail_D}m)")
    ]

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
        display_data.append({"No": i[0], "분석 항목": i[1], "결과": res, "법적 근거": i[3], "비고": i[4], "color": color, "tag": tag})

    st.subheader(f"📊 [ ◯ 대상: {cnts['target']} ]  [ ✕ 비대상: {cnts['non']} ]  [ ! 유보: {cnts['hold']} ]")

    for row in display_data:
        cols = st.columns([1, 4, 2, 3, 5])
        cols[0].write(f"**{row['No']}**")
        cols[1].write(row['분석 항목'])
        cols[2].markdown(f"<span style='color:{row['color']}; font-weight:bold;'>{row['결과']}</span>", unsafe_allow_html=True)
        cols[3].write(row['법적 근거'])
        cols[4].write(row['비고'])

    def make_pdf():
        pdf = FPDF(); pdf.add_page()
        if os.path.exists(font_path): pdf.add_font("K", "", font_path); pdf.set_font("K", size=11)
        
        pdf.cell(0, 10, "■ 사업승인 체크 리스트 결과보고서 (Boss)", ln=True, align='C')
        pdf.set_text_color(0, 82, 204)
        pdf.cell(0, 8, f"분석 요약 - 대상: {cnts['target']} / 비대상: {cnts['non']} / 유보: {cnts['hold']}", ln=True, align='R')
        
        pdf.set_text_color(0, 0, 0)
        pdf.cell(190, 8, f"용역명: {p_name} / 주소: {address}", border=1, ln=True)
        pdf.ln(5)
        
        pdf.set_fill_color(240, 240, 240)
        col_w = [10, 50, 30, 40, 60]
        headers = ["No", "분석 항목", "결과", "법적 근거", "비고"]
        for h, w in zip(headers, col_w):
            pdf.cell(w, 8, h, border=1, fill=True, align='C')
        pdf.ln()

        for r in display_data:
            pdf.set_text_color(0, 0, 0)
            pdf.cell(col_w[0], 8, str(r['No']), border=1)
            pdf.cell(col_w[1], 8, r['분석 항목'], border=1)
            
            if r['tag'] == "target": pdf.set_text_color(0, 82, 204)
            elif r['tag'] == "hold": pdf.set_text_color(255, 152, 0)
            else: pdf.set_text_color(160, 160, 160)
            pdf.cell(col_w[2], 8, r['결과'], border=1, align='C')
            
            pdf.set_text_color(0, 0, 0)
            pdf.cell(col_w[3], 8, r['법적 근거'], border=1)
            
            # 비고란 폰트 자동 조절
            remark_text = str(r['비고'])
            remark_fs = 11
            while pdf.get_string_width(remark_text) > col_w[4] - 2 and remark_fs > 5:
                remark_fs -= 0.5
                pdf.set_font("K", size=remark_fs)
            
            pdf.cell(col_w[4], 8, remark_text, border=1)
            pdf.set_font("K", size=11)
            pdf.ln()
        return pdf.output()

    st.divider()
    pdf_bytes = make_pdf()
    st.download_button("📥 [클릭] 분석 결과 PDF 저장하기", data=bytes(pdf_bytes), file_name=f"Checklist_Boss_{datetime.now().strftime('%H%M%S')}.pdf", mime="application/pdf", type="primary", use_container_width=True)
else:
    st.info("👈 좌측 하단의 **[🔍 분석 실행]** 버튼을 누르시면 42개 항목 분석 결과가 여기에 출력됩니다.")
