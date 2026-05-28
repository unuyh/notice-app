import streamlit as st
import pandas as pd

# 1. 페이지 설정 및 여백을 위한 CSS 추가
st.set_page_config(page_title="EDGE&NEXT 공지사항", layout="wide")

st.markdown("""
    <style>
    /* 메인 콘텐츠 영역을 중앙으로 정렬하고 가로 폭을 1000px로 제한 */
    .block-container {
        max-width: 1000px;
        padding-left: 2rem;
        padding-right: 2rem;
        margin: 0 auto;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏥 EDGE&NEXT 공지사항")

# 고정 구글 시트 URL
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/16Ygs3k4Dqolt6HaYNmdrNop1ptuV9_jZ2TEYaj8xzNA/edit#gid=0"

# 고정 병원 목록
fixed_hospitals = [
    "전체병원", "서울부민", "부산부민", "온종합", "해운대부민", "혜민", 
    "대림성모", "제천서울", "여수중앙", "구포부민", "두발로", "세계로", 
    "청맥", "힐링본", "서울88", "송도웰니스", "평택요양", "소래푸른숲", 
    "서일메디컬", "울산연세", "쉬즈메디", "마곡부민", "성남중앙", "부천예손", "더케이부산", "김해메가", "미소래"
]

# 2. 데이터 불러오기 함수
@st.cache_data(ttl=600)
def load_data(url):
    base_url = url.split('/edit')[0]
    download_url = f"{base_url}/export?format=xlsx"
    return pd.read_excel(download_url, sheet_name="배포내역 확인")

try:
    df = load_data(GOOGLE_SHEET_URL)
    
    # 전처리: A열(배포일자) 날짜 형식 처리
    df.iloc[:, 0] = df.iloc[:, 0].astype(str).str.split(" ").str[0].str.strip()
    
    # 3. 배포일자(A열) 목록 추출
    available_dates = df.iloc[:, 0].dropna()
    available_dates = available_dates[~available_dates.isin(["nan", "", "NaT"])]
    date_list = sorted(list(set(available_dates)), reverse=True)
    
    if not date_list:
        st.error("❌ '배포내역 확인' 시트의 A열에서 데이터를 찾을 수 없습니다.")
        st.stop()
        
    selected_date = st.selectbox("📅 조회할 배포일자를 선택하세요:", date_list)
    
    # 4. 선택 날짜 필터링 및 공지사항 분류
    filtered_df = df[df.iloc[:, 0] == selected_date]
    source_data = filtered_df.iloc[:, 22].dropna()
    notice_dict = {hospital: [] for hospital in fixed_hospitals}
    
    for idx, notice in source_data.items():
        notice_str = str(notice).strip()
        if not notice_str or notice_str == "nan": continue
            
        hospital_cell = filtered_df.loc[idx, filtered_df.columns[23]]
        if pd.isna(hospital_cell): continue
            
        hospitals = [h.strip() for h in str(hospital_cell).split(",")]
        for h in hospitals:
            if h in notice_dict: notice_dict[h].append(notice_str)
    
    # 5. 병원별 텍스트 병합 및 그룹화
    all_hospital_notices = notice_dict.get("전체병원", [])
    hospital_final_texts = {}
    for hospital in fixed_hospitals:
        current_notices = sorted(list(set(notice_dict[hospital] + all_hospital_notices)))
        hospital_final_texts[hospital] = "\n\n".join(current_notices)
    
    content_groups = {}
    for h, t in hospital_final_texts.items():
        if not t: continue
        content_groups.setdefault(t, []).append(h)
        
    # 6. 결과 출력
    if content_groups:
        st.success(f"🎉 {selected_date} 자 데이터를 성공적으로 불러왔습니다!")
        
        dropdown_options = []
        group_mapping = {}
        for i, (text, hospitals) in enumerate(content_groups.items(), 1):
            name = f"{i}. [전체병원] 공지사항" if "전체병원" in hospitals else f"{i}. [{', '.join(hospitals)}] 공지사항"
            dropdown_options.append(name)
            group_mapping[name] = text
        
        selected_option = st.selectbox("🎯 발송 대상 병원 그룹을 고르세요:", dropdown_options)
        st.subheader(f"📌 {selected_option} 내용")
        st.text_area(label="공지 내용", value=group_mapping[selected_option], height=450)
    else:
        st.info("💡 등록된 공지사항이 없습니다.")

except Exception as e:
    st.error(f"오류 발생: {e}")