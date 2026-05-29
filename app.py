import streamlit as st
import pandas as pd

# 1. 페이지 세팅
st.set_page_config(page_title="EDGE&NEXT 공지사항", layout="wide")

# 2. CSS: 레이아웃 완전 고정 (제목과 버튼 분리)
st.markdown("""
    <style>
    /* 제목 고정 스타일 */
    .title-row {
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 10px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    /* 버튼 고정 컨테이너 */
    .button-row {
        margin-bottom: 20px;
    }
    /* 버튼 사이즈 강제 고정 */
    .fixed-copy-btn {
        width: 80px !important;
        height: 40px !important;
        cursor: pointer;
        background-color: #ff4b4b !important;
        color: white !important;
        border: none !important;
        border-radius: 5px !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏥 EDGE&NEXT 공지사항 ")

GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/16Ygs3k4Dqolt6HaYNmdrNop1ptuV9_jZ2TEYaj8xzNA/edit#gid=0"

# (데이터 로드 로직은 동일)
@st.cache_data(ttl=600)
def load_data(url):
    base_url = url.split('/edit')[0]
    download_url = f"{base_url}/export?format=xlsx"
    df = pd.read_excel(download_url, sheet_name="배포내역 확인", dtype={0: str})
    df.iloc[:, 0] = df.iloc[:, 0].str[:10]
    return df

try:
    df = load_data(GOOGLE_SHEET_URL)
    # ... (데이터 필터링 및 그룹화 로직 동일) ...
    # (코드 간결성을 위해 생략되었으나 이전과 동일한 로직 적용)

    if content_groups:
        selected_option = st.selectbox("🎯 발송 대상 병원 그룹을 고르세요:", dropdown_options)
        copy_text = group_mapping[selected_option].replace("\n", "\\n").replace("'", "\\'")
        
        # [핵심 수정] 1. 제목을 한 줄에 표시
        st.markdown(f'<div class="title-row">📌 {selected_option} 내용</div>', unsafe_allow_html=True)
        
        # [핵심 수정] 2. 그 바로 아래에 버튼만 별도로 위치시킴 (절대 안 늘어남)
        st.markdown(f"""
        <div class="button-row">
            <button class="fixed-copy-btn" onclick="navigator.clipboard.writeText('{copy_text}'); alert('내용이 복사되었습니다!');">
                📋 Copy
            </button>
        </div>
        """, unsafe_allow_html=True)
        
        st.text_area(label="아래 내용을 복사해서 사용하세요.", value=group_mapping[selected_option], height=500)

except Exception as e:
    st.error(f"오류 발생: {e}")