import streamlit as st
import pandas as pd
import json

# 1. 페이지 세팅
st.set_page_config(page_title="EDGE&NEXT 공지사항", layout="wide")

# CSS: 텍스트 박스 영역 우측 상단에 버튼 고정
st.markdown("""
    <style>
    .block-container { max-width: 1400px; padding: 2rem; margin: 0 auto; }
    /* 텍스트 박스 컨테이너를 상대 위치로 설정 */
    .stTextArea { position: relative; }
    /* Copy 버튼을 텍스트 박스 오른쪽 끝으로 위치 조정 */
    .copy-btn-container { 
        display: flex; 
        justify-content: flex-end; 
        margin-bottom: 5px; 
    }
    </style>
    """, unsafe_allow_html=True)

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
    df = pd.read_excel(download_url, sheet_name="배포내역 확인", dtype={0: str})
    df.iloc[:, 0] = df.iloc[:, 0].str[:10]
    return df

try:
    df = load_data(GOOGLE_SHEET_URL)
    available_dates = df.iloc[:, 0].dropna()
    available_dates = available_dates[available_dates.str.match(r'\d{4}-\d{2}-\d{2}')]
    date_list = sorted(list(set(available_dates)), reverse=True)
    
    if not date_list:
        st.error("❌ '배포내역 확인' 시트의 A열에서 데이터를 찾을 수 없습니다.")
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
        dropdown_options = []
        group_mapping = {}
        for i, (text, hospitals) in enumerate(content_groups.items(), 1):
            name = f"{i}. [{', '.join(hospitals)}] 공지사항"
            dropdown_options.append(name)
            group_mapping[name] = text
        
        selected_option = st.selectbox("🎯 발송 대상 병원 그룹을 고르세요:", dropdown_options)
        target_text = group_mapping[selected_option]
        
        # 1. 제목은 일반 마크다운으로 표시
        st.markdown(f"### 📌 {selected_option} 내용")
        
        # 2. 버튼 컨테이너를 사용하여 우측 정렬
        st.markdown('<div class="copy-btn-container">', unsafe_allow_html=True)
        json_text = json.dumps(target_text)
        if st.button("📋 Copy"):
            st.write(f'<script>navigator.clipboard.writeText({json_text});</script>', unsafe_allow_html=True)
            st.toast("복사되었습니다!", icon="✅")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 3. 텍스트 박스 출력
        st.text_area(label="아래 내용을 복사해서 사용하세요.", value=target_text, height=500, label_visibility="collapsed")
        
    else:
        st.info("💡 등록된 공지사항이 없습니다.")

except Exception as e:
    st.error(f"오류 발생: {e}")