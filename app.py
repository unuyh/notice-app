import streamlit as st
import pandas as pd

# 1. 웹 페이지 기본 세팅
st.set_page_config(page_title="공지사항 자동 분배기", layout="wide")
st.title("🏥 구글 시트 연동 공지사항 자동 정렬 및 필터 시스템")

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
    # '배포내역 확인' 시트를 읽어옴
    return pd.read_excel(download_url, sheet_name="배포내역 확인")

try:
    # 데이터 불러오기
    df = load_data(GOOGLE_SHEET_URL)
    
    # [수정 1] 날짜 전처리: 시간을 제거하고 'YYYY-MM-DD' 형식의 문자열로 강제 변환
    # pd.to_datetime으로 변환 후 다시 문자열로 포맷팅하여 00:00:00 발생을 원천 차단합니다.
    df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], errors='coerce').dt.strftime('%Y-%m-%d')
    
    # 3. 배포일자(A열) 목록 추출
    available_dates = df.iloc[:, 0].dropna()
    available_dates = available_dates[~available_dates.isin(["nan", "", "NaT", "None"])]
    date_list = sorted(list(set(available_dates)), reverse=True)
    
    if not date_list:
        st.error("❌ '배포내역 확인' 시트의 A열에서 올바른 날짜 데이터를 찾을 수 없습니다.")
        st.stop()
        
    selected_date = st.selectbox("📅 조회할 배포일자를 선택하세요:", date_list)
    
    # 4. 선택 날짜 필터링 및 공지사항 분류
    filtered_df = df[df.iloc[:, 0] == selected_date]
    
    # W열(공지내용: 인덱스 22), X열(대상병원: 인덱스 23) 사용
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
        # 중복 제거 및 정렬 후 병합
        combined = list(set(notice_dict[hospital] + all_hospital_notices))
        current_notices = sorted(combined)
        hospital_final_texts[hospital] = "\n\n".join(current_notices)
    
    content_groups = {}
    for h, t in hospital_final_texts.items():
        if not t: continue
        content_groups.setdefault(t, []).append(h)
        
    # 6. 결과 출력
    if content_groups:
        st.success(f"🎉 {selected_date} 자 데이터를 성공적으로 불러와 그룹화했습니다!")
        
        dropdown_options = []
        group_mapping = {}
        for i, (text, hospitals) in enumerate(content_groups.items(), 1):
            if "전체병원" in hospitals:
                name = f"{i}. [전체병원] 공지사항"
            else:
                name = f"{i}. [{', '.join(hospitals)}] 공지사항"
            dropdown_options.append(name)
            group_mapping[name] = text
        
        selected_option = st.selectbox("🎯 발송 대상 병원 그룹을 고르세요:", dropdown_options)
        
        st.write("---")
        
        # [수정 2] 복사 버튼 추가
        # st.copy_to_clipboard 기능을 사용하여 버튼 클릭 시 해당 그룹의 텍스트가 복사됩니다.
        col1, col2 = st.columns([8, 2])
        with col1:
            st.subheader(f"📌 {selected_option} 내용")
        with col2:
            # 텍스트 박스 바로 위나 옆에 배치하여 접근성을 높입니다.
            if st.button("📋 Copy", use_container_width=True):
                st.copy_to_clipboard(group_mapping[selected_option])
                st.toast("내용이 복사되었습니다!") # 우측 하단에 알림 메시지 표시

        st.text_area(label="아래 내용을 복사해서 사용하세요.", value=group_mapping[selected_option], height=500)
    else:
        st.info(f"💡 선택하신 {selected_date}에는 등록된 공지사항이 없습니다.")

except Exception as e:
    st.error(f"오류 발생: {e}")
    st.write("구글 시트의 링크나 '배포내역 확인' 시트 이름을 다시 확인해주세요.")