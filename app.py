import streamlit as st
import pandas as pd
import json

# 1. 페이지 세팅
st.set_page_config(page_title="EDGE&NEXT 공지사항", layout="wide")

# CSS: Streamlit 엔진의 자동 조정을 막는 CSS Grid 설정
st.markdown("""
    <style>
    /* 전체 컨테이너를 Grid로 설정하여 레이아웃 고정 */
    .title-btn-grid {
        display: grid;
        grid-template-columns: 1fr auto; /* 왼쪽은 남은 공간, 오른쪽은 버튼 고정 */
        align-items: center;
        gap: 10px;
        margin-bottom: 10px;
    }
    /* 버튼 크기 강제 고정 */
    .btn-fixed {
        width: 80px;
        height: 40px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏥 EDGE&NEXT 공지사항 ")

# 데이터 로드 로직 (이전과 동일)
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/16Ygs3k4Dqolt6HaYNmdrNop1ptuV9_jZ2TEYaj8xzNA/edit#gid=0"

@st.cache_data(ttl=600)
def load_data(url):
    base_url = url.split('/edit')[0]
    download_url = f"{base_url}/export?format=xlsx"
    df = pd.read_excel(download_url, sheet_name="배포내역 확인", dtype={0: str})
    return df

try:
    df = load_data(GOOGLE_SHEET_URL)
    # ... 데이터 처리 로직 ...
    
    if content_groups:
        selected_option = st.selectbox("🎯 발송 대상 병원 그룹을 고르세요:", dropdown_options)
        target_text = group_mapping[selected_option]
        
        # [핵심] 1. 제목과 버튼을 하나의 Grid 컨테이너로 묶습니다.
        st.markdown(f'<div class="title-btn-grid">', unsafe_allow_html=True)
        st.markdown(f"### 📌 {selected_option} 내용")
        
        # 2. 버튼 배치 (Streamlit 버튼을 사용하되 CSS로 제어)
        if st.button("📋 Copy"):
            st.toast("복사되었습니다!", icon="✅")
            # 실제 복사 동작을 위한 로직
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 3. 텍스트 박스 출력
        st.text_area(label="아래 내용을 복사해서 사용하세요.", value=target_text, height=500, label_visibility="collapsed")

except Exception as e:
    st.error(f"오류 발생: {e}")