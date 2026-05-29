import streamlit as st
import pandas as pd

# 1. 페이지 세팅
st.set_page_config(page_title="EDGE&NEXT 공지사항", layout="wide")

# 2. 레이아웃 강제 고정 CSS
st.markdown("""
    <style>
    .block-container { max-width: 1400px; padding: 2rem; margin: 0 auto; }
    .title-row { font-size: 1.5rem; font-weight: bold; margin-bottom: 5px; }
    .button-row { margin-bottom: 20px; }
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
    # 데이터 로드
    df = load_data(GOOGLE_SHEET_URL)
    available_dates = df.iloc[:, 0].dropna()
    available_dates = available_dates[available_dates.str.match(r'\d{4}-\d{2}-\d{2}')]
    date_list = sorted(list(set(available_dates)), reverse=True)
    
    if not date_list:
        st.error("❌ '배포내역 확인' 시트의 A열에서 데이터를 찾을 수 없습니다.")
        st.stop()
        
    selected_date = st.selectbox("📅 조회할 배포일자를 선택하세요:", date_list)
    
    # 데이터 처리
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
        st.success(f"🎉 {selected_date} 자 데이터를 성공적으로 불러와 그룹화했습니다!")
        
        dropdown_options = []
        group_mapping = {}
        for i, (text, hospitals) in enumerate(content_groups.items(), 1):
            name = f"{i}. [{', '.join(hospitals)}] 공지사항"
            dropdown_options.append(name)
            group_mapping[name] = text
        
        selected_option = st.selectbox("🎯 발송 대상 병원 그룹을 고르세요:", dropdown_options)
        copy_text = group_mapping[selected_option].replace("\n", "\\n").replace("'", "\\'")
        
        # [수정된 레이아웃] 제목 한 줄 + 아래에 버튼 한 줄
        st.markdown(f'<div class="title-row">📌 {selected_option} 내용</div>', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="button-row">
            <button class="fixed-copy-btn" onclick="navigator.clipboard.writeText('{copy_text}'); alert('내용이 복사되었습니다!');">
                📋 Copy
            </button>
        </div>
        """, unsafe_allow_html=True)
        
        st.text_area(label="아래 내용을 복사해서 사용하세요.", value=group_mapping[selected_option], height=500)
    else:
        st.info("💡 등록된 공지사항이 없습니다.")

except Exception as e:
    st.error(f"오류 발생: {e}")