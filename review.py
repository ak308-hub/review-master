import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# ---------------------------------------------------------
# [1] 환경 변수 로드
# ---------------------------------------------------------
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    st.error("API 키가 없습니다. .env 파일을 확인해주세요.")
    st.stop()

genai.configure(api_key=API_KEY)

# ---------------------------------------------------------
# [2] 사이드바 (설정 영역)
# ---------------------------------------------------------
with st.sidebar:
    st.header("⚙️ 분석 설정")
    
    keyword_count = st.slider(
        "추출할 키워드 개수", 
        min_value=5, 
        max_value=10, 
        value=5
    )
    
    st.markdown("---")
    st.info("💡 **사진 확인 기능 추가됨**\n\n분석 결과 맨 아래에 생기는 **'📸 사진 보러가기'** 링크를 누르면 가게의 실제 음식/인테리어 사진을 바로 볼 수 있습니다.")

# ---------------------------------------------------------
# [3] AI 모델 설정
# ---------------------------------------------------------
def analyze_place(place_query, count):
    # 프롬프트 수정: 구글 맵 검색 링크를 생성하도록 지시
    system_prompt = f"""
    당신은 '구글 지도 전문 리뷰 분석가'입니다.
    사용자가 입력한 정보('{place_query}')를 바탕으로 구글 지도를 검색하여 정밀하게 분석하세요.

    [필수 지침]
    1. **장소 식별**: 이름, 주소, 전화번호 중 무엇을 입력하든 정확한 장소를 찾아내세요.
    2. **주소/언어**: 도로명 주소를 명시하고, 외국어 장소는 '현지어(한국어)'로 표기하세요.
    3. **키워드**: 핵심 특징을 **{count}개** 뽑아주세요.
    4. **사진 링크**: 분석한 장소의 이름을 바탕으로 **구글 지도 검색 URL**을 생성하여 마크다운 링크로 제공하세요.

    [출력 형식]
    다음 형식을 엄격히 따르세요 (구분선 포함):

    ## 📍 장소명: [현지어 이름] ([한국어 발음])
    **🏠 주소:** [정확한 주소]
    
    ---
    ### 📸 사진 및 위치 확인
    👉 **[구글 지도에서 실제 사진 보기](https://www.google.com/maps/search/?api=1&query=[식별된_정확한_장소명])**
    *(위 링크를 클릭하면 사진 탭으로 이동합니다)*
    ---

    **⭐ 종합 평점:** [별점] ([분위기 요약])
    
    ### 🔥 핵심 키워드 TOP {count}
    1. #[키워드1]
    2. #[키워드2]
    ...
    
    ### 📝 한줄 요약
    [한 문장 요약]
    
    ### ⚠️ 주의할 점
    [단점이나 주의사항 1가지]
    """

    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash", 
        system_instruction=system_prompt
    )
    
    return model.generate_content(f"'{place_query}'에 대한 정보를 분석해줘.")

# ---------------------------------------------------------
# [4] 메인 앱 화면
# ---------------------------------------------------------
st.set_page_config(page_title="구글 맵 리뷰 마스터", page_icon="🗺️")

st.title("🗺️ 구글 맵 리뷰 마스터")
st.markdown("주소, 전화번호, 이름 무엇이든 넣으면 **AI가 장소를 분석하고 사진 링크를 제공**합니다.")

query = st.text_input(
    "검색어 입력", 
    placeholder="예: 오사카 킨류라멘, 서울시 강서구 화곡로 123, 02-123-4567"
)

if st.button("분석 시작 🚀", use_container_width=True):
    if not query:
        st.warning("검색어를 입력해주세요!")
    else:
        try:
            with st.spinner(f"🔍 '{query}' 정보를 찾고 사진 링크를 생성 중입니다..."):
                response = analyze_place(query, keyword_count)
                
                st.success("분석 완료! 아래 링크를 눌러 사진을 확인하세요.")
                st.markdown("---")
                # AI가 생성한 마크다운(링크 포함)을 그대로 출력
                st.markdown(response.text)
                
        except Exception as e:
            st.error(f"오류가 발생했습니다. 잠시 후 다시 시도해주세요.\n({e})")