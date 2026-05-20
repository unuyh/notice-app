import streamlit as st
import pandas as pd

# 1. 구글 시트 주소 설정
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/16Ygs3k4Dqolt6HaYNmdrNop1ptuV9_jZ2TEYaj8xzNA/edit?gid=0"

def load_data(url):
    export_url = url.replace("/edit?gid=", "/export?format=xlsx&gid=")
    return pd.read_excel(export_url, engine='openpyxl', header=0)

st.set_page_config(page_title="공지사항 자동 분배", layout="wide")
st.title("🏥 공지사항 자동 분배 시스템")

# 2. 데이터 저장소 초기화
if 'df' not in st.session_state:
    st.session_state['df'] = None

# 3. 실시간 불러오기 버튼
if st.button("🔄 실시간 데이터 불러오기"):
    with st.spinner("구글 시트에서 최신 데이터를 가져오는 중..."):
        st.session_state['df'] = load_data(GOOGLE_SHEET_URL)
        st.rerun()

# 4. 데이터 로드 후 필터링 및 분배 로직
if st.session_state['df'] is not None:
    df = st.session_state['df']
    
    # 키워드 검색을 통해 실제 컬럼명 매칭
    col_date = next((c for c in df.columns if '배포일자' in str(c)), None)
    col_notice = next((c for c in df.columns if '반영시 공지문' in str(c)), None)
    col_hospital = next((c for c in df.columns if '공지병원' in str(c)), None)
    
    if all([col_date, col_notice, col_hospital]):
        # A. 배포일자 필터링
        dates = sorted(df[col_date].dropna().unique())
        selected_date = st.selectbox("📅 1단계: 배포일자를 선택하세요", dates)
        
        # 날짜로 필터링된 데이터
        date_filtered_df = df[df[col_date] == selected_date]
        
        # B. 병원 선택 (드롭박스)
        hospitals = date_filtered_df[col_hospital].dropna().unique()
        selected_hospital = st.selectbox("📌 2단계: 확인할 병원을 고르세요:", hospitals)
        
        # C. 최종 분류된 데이터 표시
        final_df = date_filtered_df[date_filtered_df[col_hospital] == selected_hospital]
        
        st.subheader(f"✨ {selected_hospital} 공지사항 상세")
        
        # 기존 엑셀 방식처럼 텍스트를 분류하여 표시
        for idx, row in final_df.iterrows():
            st.info(f"{row[col_notice]}")
            st.divider()
    else:
        st.error("오류: 필요한 컬럼(배포일자, 반영시 공지문, 공지병원)을 찾을 수 없습니다.")
else:
    st.info("데이터가 없습니다. '실시간 데이터 불러오기' 버튼을 눌러주세요.")