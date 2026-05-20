import streamlit as st
import pandas as pd

# 1. 구글 시트 주소 설정
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/16Ygs3k4Dqolt6HaYNmdrNop1ptuV9_jZ2TEYaj8xzNA/edit?gid=0"

def load_data(url):
    export_url = url.replace("/edit?gid=", "/export?format=xlsx&gid=")
    # 첫 번째 줄을 헤더로 읽어옵니다.
    return pd.read_excel(export_url, engine='openpyxl', header=0)

st.set_page_config(page_title="공지사항 자동 분배", layout="wide")
st.title("🏥 공지사항 자동 분배 시스템")

if 'df' not in st.session_state:
    st.session_state['df'] = None

# 2. 버튼 클릭 시 데이터 로드
if st.button("🔄 실시간 데이터 불러오기"):
    with st.spinner("구글 시트에서 데이터를 가져오는 중..."):
        st.session_state['df'] = load_data(GOOGLE_SHEET_URL)
        st.rerun()

# 3. 데이터가 있을 때 로직 실행
if st.session_state['df'] is not None:
    df = st.session_state['df']
    
    # 4. 키워드가 포함된 열 이름 찾기
    col_date = next((c for c in df.columns if '배포일자' in str(c)), None)
    col_notice = next((c for c in df.columns if '반영시 공지문' in str(c)), None)
    col_hospital = next((c for c in df.columns if '공지병원' in str(c)), None)
    
    if all([col_date, col_notice, col_hospital]):
        # 병원 선택 드롭박스
        hospitals = df[col_hospital].dropna().unique()
        selected_hospital = st.selectbox("📌 확인할 병원을 고르세요:", hospitals)
        
        # 선택한 병원의 데이터 필터링
        filtered_df = df[df[col_hospital] == selected_hospital]
        
        # 5. 결과 출력 (배포일자와 공지내용 위주로 표시)
        st.subheader(f"✨ {selected_hospital} 공지사항 상세")
        
        for idx, row in filtered_df.iterrows():
            st.markdown(f"**📅 배포일자:** {row[col_date]}")
            st.info(f"{row[col_notice]}") # 공지 내용을 눈에 띄게 표시
            st.divider() # 구분선
            
    else:
        st.error("오류: 필요한 열(배포일자, 반영시 공지문, 공지병원)을 찾을 수 없습니다.")
        st.write("인식된 열 목록:", df.columns.tolist())
else:
    st.info("데이터가 없습니다. '실시간 데이터 불러오기' 버튼을 눌러주세요.")