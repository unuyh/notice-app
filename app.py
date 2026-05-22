import streamlit as st
import pandas as pd

# 1. 웹 페이지 기본 세팅
st.set_page_config(page_title="EDGE&NEXT 공지사항", layout="wide")
st.title("🏥 EDGE&NEXT 공지사항 ")

GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/16Ygs3k4Dqolt6HaYNmdrNop1ptuV9_jZ2TEYaj8xzNA/edit#gid=0"

fixed_hospitals = [
    "전체병원", "서울부민", "부산부민", "온종합", "해운대부민", "혜민", 
    "대림성모", "제천서울", "여수중앙", "구포부민", "두발로", "세계로", 
    "청맥", "힐링본", "서울88", "송도웰니스", "평택요양", "소래푸른숲", 
    "서일메디컬", "울산연세", "쉬즈메디", "마곡부민", "성남중앙", "부천예손", "더케이부산", "김해메가", "미소래"
]

@st.cache_data(ttl=600)
def load_data(url):
    base_url = url.split('/edit')[0]
    download_url = f"{base_url}/export?format=xlsx"
    # 날짜 시간 자동 변환 방지 (A열을 문자열로)
    df = pd.read_excel(download_url, sheet_name="배포내역 확인", dtype={0: str})
    # 앞의 10글자만 남김
    df.iloc[:, 0] = df.iloc[:, 0].str[:10]
    return df

try:
    df = load_data(GOOGLE_SHEET_URL)
    
    available_dates = df.iloc[:, 0].dropna()
    available_dates = available_dates[available_dates.str.match(r'\d{4}-\d{2}-\d{2}')]
    date_list = sorted(list(set(available_dates)), reverse=True)
    
    if not date_list:
        st.stop()
        
    selected_date = st.selectbox("📅 조회할 배포일자를 선택하세요:", date_list)
    
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
    
    all_hospital_notices = notice_dict.get("전체병원", [])
    hospital_final_texts = {}
    for hospital in fixed_hospitals:
        current_notices = sorted(list(set(notice_dict[hospital] + all_hospital_notices)))
        hospital_final_texts[hospital] = "\n\n".join(current_notices)
    
    content_groups = {}
    for h, t in hospital_final_texts.items():
        if not t: continue
        content_groups.setdefault(t, []).append(h)
        
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
        
        # 복사 버튼 없이 일단 텍스트 영역만 표시 (라이브러리 문제 해결 전)
        st.text_area(label="아래 내용을 복사해서 사용하세요.", value=group_mapping[selected_option], height=500)
    else:
        st.info("💡 등록된 공지사항이 없습니다.")

except Exception as e:
    st.error(f"오류 발생: {e}")