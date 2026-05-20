import streamlit as st
import pandas as pd

# 1. 구글 시트 주소 설정
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/16Ygs3k4Dqolt6HaYNmdrNop1ptuV9_jZ2TEYaj8xzNA/edit?gid=0"

def load_data(url):
    export_url = url.replace("/edit?gid=", "/export?format=xlsx&gid=")
    return pd.read_excel(export_url, engine='openpyxl')

st.set_page_config(page_title="공지사항 자동 분배", layout="wide")
st.title("🏥 공지사항 자동 분배 시스템")

# 2. 데이터 저장소 초기화
if 'df' not in st.session_state:
    st.session_state['df'] = None

# 3. 실시간 불러오기 버튼
if st.button("🔄 실시간 데이터 불러오기"):
    with st.spinner("데이터를 가져오는 중..."):
        st.session_state['df'] = load_data(GOOGLE_SHEET_URL)
        st.rerun() # 데이터를 불러오면 즉시 화면을 갱신합니다.

# 4. 데이터가 있을 때만 기존 로직 실행
if st.session_state['df'] is not None:
    df = st.session_state['df']
    
    # --- 여기서부터는 기존에 잘 작동하던 질문자님의 로직을 그대로 유지합니다 ---
    # 혹시 기존 로직이 이 아래에 있는 것들이라면 그대로 두시면 됩니다.
    
    # 예시: '공지병원' 기준으로 필터링하는 로직 (기존 스타일대로)
    target_hospitals = df['공지병원'].unique()
    selected_hospital = st.selectbox("병원 선택", target_hospitals)
    
    filtered_df = df[df['공지병원'] == selected_hospital]
    st.dataframe(filtered_df)
    
    # 기존에 만드셨던 다른 복잡한 로직들도 이 아래에 그대로 두시면 됩니다.
    # ------------------------------------------------------------------

else:
    st.info("데이터가 없습니다. '실시간 데이터 불러오기' 버튼을 눌러주세요.")