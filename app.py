import streamlit as st
import pandas as pd

# 1. 구글 시트 주소 고정 (링크를 입력할 필요가 없도록 코드 내부에 고정)
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/16Ygs3k4Dqolt6HaYNmdrNop1ptuV9_jZ2TEYaj8xzNA/edit?gid=0"

# 2. 웹 페이지 기본 세팅
st.set_page_config(page_title="공지사항 자동 분배기", layout="wide")
st.title("🏥 구글 시트 연동 공지사항 자동 정렬 및 필터 시스템")
st.write("구글 스프레드시트에서 실시간으로 데이터를 불러와 날짜별/병원별 공지사항을 정렬합니다.")

# 고정 병원 목록
fixed_hospitals = [
    "전체병원", "서울부민", "부산부민", "온종합", "해운대부민", "혜민", 
    "대림성모", "제천서울", "여수중앙", "구포부민", "두발로", "세계로", 
    "청맥", "힐링본", "서울88", "송도웰니스", "평택요양", "소래푸른숲", 
    "서일메디컬", "울산연세", "쉬즈메디", "마곡부민", "성남중앙", "부천예손", "더케이부산", "김해메가", "미소래"
]

# 3. 데이터 불러오기 함수 (캐싱 적용으로 속도 향상)
@st.cache_data(ttl=600) # 10분마다 캐시 갱신
def load_data(url):
    # 다운로드 주소로 변환
    download_url = url.replace("/edit", "/export?format=xlsx")
    return pd.read_excel(download_url, sheet_name="배포내역 확인")

try:
    # 데이터 불러오기
    df = load_data(GOOGLE_SHEET_URL)
    
    # 원본 파일 고정 위치 세팅 및 전처리 (A열=0: 배포일자, W열=22: 공지내용, X열=23: 대상병원)
    df.iloc[:, 0] = df.iloc[:, 0].astype(str).str.split(" ").str[0].str.strip()
    
    # 4. 배포일자(A열) 목록 추출 및 정렬
    available_dates = df.iloc[:, 0].dropna()
    available_dates = available_dates[~available_dates.isin(["nan", "", "NaT"])]
    date_list = sorted(list(set(available_dates)), reverse=True)
    
    if not date_list:
        st.error("❌ 시트의 A열에서 올바른 '배포일자' 데이터를 찾을 수 없습니다.")
        st.stop()
        
    # 5. 배포일자 선택
    selected_date = st.selectbox("📅 조회할 배포일자를 선택하세요:", date_list)
    
    # 선택된 날짜 필터링
    filtered_df = df[df.iloc[:, 0] == selected_date]
    
    # 필터링된 데이터에서 W열(공지내용) 추출
    source_data = filtered_df.iloc[:, 22].dropna()
    
    # 병원별 임시 보관함 준비
    notice_dict = {hospital: [] for hospital in fixed_hospitals}
    
    # 데이터 분배 로직
    for idx, notice in source_data.items():
        notice_str = str(notice).strip()
        if not notice_str or notice_str == "nan":
            continue
            
        hospital_cell = filtered_df.loc[idx, filtered_df.columns[23]]
        if pd.isna(hospital_cell):
            continue
            
        hospitals = [h.strip() for h in str(hospital_cell).split(",")]
        for h in hospitals:
            if h in notice_dict:
                notice_dict[h].append(notice_str)
    
    # 전체병원 공지 통합 및 각 병원별 최종 텍스트 생성
    all_hospital_notices = notice_dict.get("전체병원", [])
    hospital_final_texts = {}
    for hospital in fixed_hospitals:
        current_notices = notice_dict[hospital].copy()
        if hospital != "전체병원":
            current_notices.extend(all_hospital_notices)
        current_notices = sorted(list(set(current_notices)))
        hospital_final_texts[hospital] = "\n\n".join(current_notices)
    
    # 내용이 같은 병원끼리 그룹화
    content_groups = {}
    for hospital, text in hospital_final_texts.items():
        if not text:
            continue
        if text not in content_groups:
            content_groups[text] = []
        content_groups[text].append(hospital)
        
    if content_groups:
        st.success(f"🎉 {selected_date} 자 데이터를 성공적으로 불러와 그룹화했습니다!")
        
        dropdown_options = []
        group_mapping = {}
        for i, (text, hospitals) in enumerate(content_groups.items(), 1):
            if "전체병원" in hospitals:
                option_name = f"{i}. [전체병원] 공지사항"
            else:
                option_name = f"{i}. [{', '.join(hospitals)}] 공지사항"
            dropdown_options.append(option_name)
            group_mapping[option_name] = text
        
        # 6. 병원 그룹 선택 드롭박스 및 출력
        selected_option = st.selectbox("🎯 발송 대상 병원 그룹을 고르세요:", dropdown_options)
        st.subheader(f"📌 {selected_option} 내용")
        st.text_area(label="복사해서 사용하세요.", value=group_mapping[selected_option], height=450)
    else:
        st.info(f"💡 선택하신 {selected_date}에는 등록된 병원별 공지사항이 없습니다.")

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다. 에러내용: {e}")