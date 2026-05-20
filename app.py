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

if st.button("🔄 실시간 데이터 불러오기"):
    with st.spinner("데이터를 가져오는 중..."):
        st.session_state['df'] = load_data(GOOGLE_SHEET_URL)
        st.rerun()

if st.session_state['df'] is not None:
    df = st.session_state['df']
    
    # [핵심 수정] '공지병원'이라는 단어가 포함된 열 이름을 찾습니다.
    target_col = next((col for col in df.columns if '공지병원' in str(col)), None)
    
    if target_col:
        # 해당 열을 사용하여 필터링 로직 수행
        target_hospitals = df[target_col].dropna().unique()
        selected_hospital = st.selectbox("병원 선택", target_hospitals)
        
        filtered_df = df[df[target_col] == selected_hospital]
        st.dataframe(filtered_df)
    else:
        st.error("오류: '공지병원'이라는 단어가 포함된 열을 찾을 수 없습니다.")
        st.write("현재 시트의 열 제목들:", df.columns.tolist())
else:
    st.info("데이터가 없습니다. '실시간 데이터 불러오기' 버튼을 눌러주세요.")