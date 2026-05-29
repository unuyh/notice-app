import streamlit as st
import pandas as pd

# 1. 페이지 세팅
st.set_page_config(page_title="EDGE&NEXT 공지사항", layout="wide")

# 2. 레이아웃 강제 고정 CSS (절대 변경 금지)
st.markdown("""
    <style>
    .block-container { max-width: 1400px; padding-left: 2rem; padding-right: 2rem; margin: 0 auto; }
    
    /* 제목과 버튼을 위한 엄격한 그리드 컨테이너 */
    .fixed-header-grid {
        display: grid;
        grid-template-columns: 1fr 90px;
        align-items: center;
        width: 100%;
        margin-top: 20px;
        margin-bottom: 10px;
        gap: 10px;
    }
    
    /* 제목: 넘치면 무조건 줄임표 처리 */
    .title-text {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        font-size: 1.5rem;
        font-weight: bold;
        margin: 0;
    }
    
    /* 버튼: 사이즈 절대 고정 및 사라짐 방지 */
    .fixed-copy-btn {
        width: 80px !important;
        height: 40px !important;
        cursor: pointer;
        background-color: #ff4b4b !important;
        color: white !important;
        border: none !important;
        border-radius: 5px !important;
        font-weight: bold !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
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
        copy_text = group_mapping[selected_option].replace("\n", "\\n").replace("'", "\\'")
        
        # [HTML 렌더링] Streamlit 내부 레이아웃 엔진을 거치지 않는 고정 헤더
        st.markdown(f"""
        <div class="fixed-header-grid">
            <h3 class="title-text" title="{selected_option}">📌 {selected_option} 내용</h3>
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