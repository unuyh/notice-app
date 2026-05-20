import streamlit as st
import pandas as pd

# 1. 웹 페이지 제목 및 레이아웃 세팅
st.set_page_config(page_title="공지사항 자동 분배기", layout="wide")
st.title("🏥 구글 시트 연동 공지사항 자동 정렬 및 필터 시스템")
st.write("구글 스프레드시트 링크를 넣으면 [배포내역 확인] 시트에서 날짜별로 선택하여 실시간 데이터를 조회할 수 있습니다.")

# 고정 병원 목록
fixed_hospitals = [
    "전체병원", "서울부민", "부산부민", "온종합", "해운대부민", "혜민", 
    "대림성모", "제천서울", "여수중앙", "구포부민", "두발로", "세계로", 
    "청맥", "힐링본", "서울88", "송도웰니스", "평택요양", "소래푸른숲", 
    "서일메디컬", "울산연세", "쉬즈메디", "마곡부민", "성남중앙", "부천예손", "더케이부산", "김해메가", "미소래"
]

# 2. 구글 시트 주소 입력창
sheet_url = st.text_input("구글 스프레드시트 링크(URL)를 입력해주세요:")

if sheet_url:
    try:
        # 구글 시트 주소를 다운로드 주소로 변환
        if "/edit" in sheet_url:
            base_url = sheet_url.split("/edit")[0]
            download_url = f"{base_url}/export?format=xlsx"
        else:
            download_url = sheet_url

        # [배포내역 확인] 시트 가져오기
        df = pd.read_excel(download_url, sheet_name="배포내역 확인")
        
        # 원본 파일 고정 위치 세팅 (A열=0: 배포일자, W열=22: 공지내용, X열=23: 대상병원)
        # 날짜 데이터 처리 (문자열로 깔끔하게 변환하고 공백 제거)
        df.iloc[:, 0] = df.iloc[:, 0].astype(str).str.split(" ").str[0].str.strip()
        
        # 3. ✨ [핵심 기능] 배포일자(A열) 목록 추출 및 정렬
        # 빈 값이나 누락된 값 제거 후 유일한 날짜들만 정렬하여 가져오기
        available_dates = df.iloc[:, 0].dropna()
        available_dates = available_dates[~available_dates.isin(["nan", "", "NaT"])]
        date_list = sorted(list(set(available_dates)), reverse=True) # 최신 날짜가 맨 위로 오도록 정렬
        
        if not date_list:
            st.error("❌ 시트의 A열에서 올바른 '배포일자' 데이터를 찾을 수 없습니다.")
            st.stop()
            
        # 4. 화면 맨 위에 날짜 선택 드롭박스 배치
        selected_date = st.selectbox("📅 조회할 배포일자를 선택하세요:", date_list)
        
        # 선택된 날짜에 해당하는 행만 필터링!
        filtered_df = df[df.iloc[:, 0] == selected_date]
        
        # 필터링된 데이터에서 W열(공지내용) 추출
        source_data = filtered_df.iloc[:, 22].dropna()
        
        # 병원별 임시 보관함 준비
        notice_dict = {hospital: [] for hospital in fixed_hospitals}
        
        # 데이터 분배 로직 실행 (필터링된 데이터 기준)
        for idx, notice in source_data.items():
            notice_str = str(notice).strip()
            if not notice_str or notice_str == "nan":
                continue
                
            # X열에서 대상병원 가져오기
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
            st.write("---")
            
            dropdown_options = []
            group_mapping = {}
            for i, (text, hospitals) in enumerate(content_groups.items(), 1):
                if "전체병원" in hospitals:
                    option_name = f"{i}. [전체병원] 공지사항"
                else:
                    option_name = f"{i}. [{', '.join(hospitals)}] 공지사항"
                dropdown_options.append(option_name)
                group_mapping[option_name] = text
            
            # 5. 병원 그룹 선택 드롭박스
            selected_option = st.selectbox("🎯 발송 대상 병원 그룹을 고르세요:", dropdown_options)
            
            # 6. 복사용 하단 텍스트 상자 출력
            st.subheader(f"📌 {selected_option} 내용")
            st.text_area(label="복사해서 사용하세요.", value=group_mapping[selected_option], height=450)
        else:
            st.info(f"💡 선택하신 {selected_date}에는 등록된 병원별 공지사항이 없습니다.")
            
    except Exception as e:
        st.error(f"구글 시트를 읽어오는 중 오류가 발생했습니다. 링크 공유 권한을 확인해주세요. 에러내용: {e}")