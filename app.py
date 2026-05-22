import streamlit as st
import pandas as pd

st.set_page_config(page_title="EDGE&NEXT 공지사항", layout="wide")
st.title("🏥 EDGE&NEXT 공지사항 ")

GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/16Ygs3k4Dqolt6HaYNmdrNop1ptuV9_jZ2TEYaj8xzNA/edit#gid=0"

@st.cache_data(ttl=600)
def load_data(url):
    base_url = url.split('/edit')[0]
    download_url = f"{base_url}/export?format=xlsx"
    # 날짜 시간 자동 변환 방지
    df = pd.read_excel(download_url, sheet_name="배포내역 확인", dtype={0: str})
    df.iloc[:, 0] = df.iloc[:, 0].str[:10]
    return df

try:
    df = load_data(GOOGLE_SHEET_URL)
    st.success("데이터를 성공적으로 불러왔습니다!")
    st.write(df.head()) # 데이터가 잘 들어오는지 확인용
except Exception as e:
    st.error(f"오류 발생: {e}")