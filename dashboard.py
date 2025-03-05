#streamlit run dashboard.py 해당 코드를 git bash 터미널에 crtl c + crtl v 하면 웹이 실행 됩니다.

import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import subprocess
import json
import base64
from datetime import datetime

st.set_page_config(page_title="서울 관광지 혼잡도 예측", layout="wide")

# BMHANNAPro.ttf 폰트 적용 함수
def font_css(font_path):
    with open(font_path, "rb") as f:
        font_base64 = base64.b64encode(f.read()).decode()

    font_css = f"""
    <style>
    @font-face {{
        font-family: 'BMHANNAPro';
        src: url('data:font/ttf;base64,{font_base64}') format('truetype');
    }}

    /* 기본 텍스트 요소에는 BMHANNAPro 적용 (이모지, 기호 제외) */
    body, h1, h2, h3, h4, h5, h6, p, button, label {{
        font-family: 'BMHANNAPro', sans-serif !important;
    }}
    </style>
    """
    return font_css

#폰트 파일 경로 설정 및 적용
font_path = "assets/BMHANNAPro.ttf"  
st.markdown(font_css(font_path), unsafe_allow_html=True)

# 현재 날짜 및 요일 가져오기
today = datetime.today()
today_str = today.strftime("%Y년 %m월 %d일 %A")

# 현재 스크립트(dashboard.py)가 위치한 디렉토리
base_dir = os.path.dirname(os.path.abspath(__file__))

# 모델이 있는 폴더 (train_and_predict)
model_dir = os.path.join(base_dir, "train_and_predict")

model_files = [
    "changdeokgung.py", "changgyeonggung.py", "deoksugung.py",
    "gyeongbokgung.py", "jongmyo.py", "seoul_arts_center.py",
    "seoul_grand_park.py"
]

# 관광지 데이터
tourist_sites = {
    "창덕궁": 119765,
    "창경궁": 47126,
    "덕수궁": 20401,
    "경복궁": 94070,
    "종묘": 40652,
    "예술의전당": 50734,
    "서울대공원": 1984065
}

############################################################################
# 세션 상태 초기화 (최초 실행 시)
if "predicted_data" not in st.session_state:
    st.session_state["predicted_data"] = {}

# 7개의 모델 실행 후 예측 결과 수집
def collect_predictions():
    predicted_data = {}

    for model in model_files:
        result = subprocess.run(["python", os.path.join(model_dir, model)], capture_output=True, text=True)

        st.write(f"📌 {model} 실행 결과 (stdout):\n")
        st.text(result.stdout)  # 정상 실행된 출력
        #st.write(f"📌 {model} 실행 결과 (stderr):\n")
        #st.text(result.stderr)  # 에러 메시지 확인

        try:
            model_output = json.loads(result.stdout.strip())  # JSON 로드 시도
            predicted_data.update(model_output)  # 예측 결과 병합
        except json.JSONDecodeError:
            st.error(f"❌ {model} 실행 오류: JSON 형식이 아닙니다.\n원본 출력:\n{result.stdout}\n에러 메시지:\n{result.stderr}")

    st.write("✅ 최종 predicted_data:", predicted_data)
    st.session_state["predicted_data"] = predicted_data

collect_predictions()

############################################################################

st.markdown(
    f"""
    <div style="text-align: center; padding: 20px; background-color: #4CAF50; color: white; border-radius: 10px;">
        <h1>서울 관광지 혼잡도 예측 대시보드</h1>
        <h3>오늘은 <b>{today_str}</b> 입니다! 관광하고 싶은 방문지를 선택하세요.</h3>
    </div>
    """,
    unsafe_allow_html=True
)

# 방문지 선택 제목 중앙 정렬 + 크기 확대
st.markdown(
    """
    <style>
    /* 방문지 선택 제목 스타일 */
    .visit-title {
        text-align: center;
        font-size: 28px;
        font-weight: bold;
        color: #333;
        margin-bottom: 15px;
    }

    /* 전체 라디오 버튼을 감싸는 div를 중앙 정렬 */
    div[role="radiogroup"] {
        display: flex;
        justify-content: center;  /* 중앙 정렬 */
        gap: 20px;  /* 버튼 사이 간격 조정 */
        flex-wrap: wrap; /* 화면이 작아지면 줄바꿈 */
    }

    /* 개별 버튼 스타일 (크기 확대) */
    div[role="radiogroup"] label {
        font-size: 22px !important;  /* 폰트 크기 확대 */
        padding: 15px 30px !important;  /* 버튼 내부 여백 조정 */
        border: 3px solid #4CAF50 !important;  /* 버튼 테두리 추가 */
        border-radius: 12px !important;  /* 둥근 버튼 스타일 */
        margin: 8px !important;  /* 버튼 간격 조정 */
        text-align: center !important;  /* 텍스트 중앙 정렬 */
        cursor: pointer; /* 클릭 가능하도록 변경 */
        transition: all 0.3s ease-in-out; /* 부드러운 효과 */
    }

    /* 마우스를 올리면 색상 변경 */
    div[role="radiogroup"] label:hover {
        background-color: #DFFFD6 !important;
        transform: scale(1.05); /* 살짝 확대 */
    }
    </style>
    
    <h2 class="visit-title">🚀 방문지를 선택하세요</h2>
    """,
    unsafe_allow_html=True
)

# 방문지 선택 (가로 정렬 + 중앙 배치)
selected_site = st.radio(
    "",  # 제목은 CSS에서 처리했으므로 빈 문자열
    list(tourist_sites.keys()), 
    horizontal=True  # 가로 정렬 유지
)

st.markdown("<hr>", unsafe_allow_html=True)

predicted_data = st.session_state["predicted_data"]

if selected_site in predicted_data:
    selected_result = predicted_data[selected_site]
    st.markdown(
        f"""
        <div style="padding: 20px; border-radius: 10px; background-color: #f3f4f6; text-align: center;">
            <h2>🎯 선택하신 <b style='color: #ff5733;'>{selected_site}</b> 의 예측 데이터</h2>
            <h3>👥 예상 방문자수: <b>{selected_result['predicted_visitors']}명</b></h3>
            <h3>📊 혼잡도: <b>{selected_result['congestion_level']:.2f}%</b></h3>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.warning("해당 관광지에 대한 예측 데이터가 없습니다.")

    
st.markdown("<h4 style='text-align: center;'>아래 그래프와 랭킹을 통해 다른 관광지와 비교해보세요!</h4>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# 혼잡도 랭킹 및 대안 추천지
if predicted_data:
    all_predictions = [
        {"site": site, "predicted_visitors": data["predicted_visitors"], "congestion_level": data["congestion_level"]}
        for site, data in predicted_data.items()
    ]

    # 그래프 시각화 (Plotly)
    sites = [x['site'] for x in all_predictions]
    visitors = [x['predicted_visitors'] for x in all_predictions]
    congestion_values = [x['congestion_level'] for x in all_predictions]

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("예상 방문자수", "혼잡도")
    )

    fig.add_trace(
        go.Bar(x=sites, y=visitors, name='방문자수', marker_color='blue'),
        row=1, col=1
    )

    fig.add_trace(
        go.Bar(x=sites, y=congestion_values, name='혼잡도', marker_color='red'),
        row=1, col=2
    )

    fig.update_layout(height=600, showlegend=False, template="plotly_white")
    st.plotly_chart(fig)

    # 🔴 간격 추가
    st.markdown("<br><hr><br>", unsafe_allow_html=True)

    # 혼잡도 상태 반환 함수
    def get_congestion_status(congestion_level):
        if congestion_level < 10:
            return "매우 여유", "green"
        elif congestion_level < 30:
            return "여유", "lightgreen"
        elif congestion_level < 50:
            return "약간 붐빔", "yellow"
        elif congestion_level < 70:
            return "혼잡", "orange"
        else:
            return "매우 혼잡", "red"

    st.markdown("<h3 style='text-align: center;'>혼잡도 랭킹 (낮은 순)</h3>", unsafe_allow_html=True)

    st.markdown(
    """
    <style>
    /* 랭킹 전체 컨테이너 중앙 정렬 */
    .ranking-container {
        display: flex;
        flex-direction: column;
        align-items: center;  /* 중앙 정렬 */
        justify-content: center;
        text-align: center;
        width: 100%;
        max-width: 600px;  /* 최대 너비 제한 */
        margin: 0 auto;  /* 중앙 배치 */
    }

    /* 개별 랭킹 항목 스타일 */
    .ranking-item {
        display: flex;
        align-items: center;
        justify-content: center; /* 내부 요소 중앙 정렬 */
        font-size: 1.2em;
        padding: 10px;
        border-radius: 8px;
        width: 80%;  /* 적절한 너비 설정 */
        max-width: 500px;
        min-width: 300px;
        margin: 5px auto;  /* 중앙 정렬 */
    }

    /* 색상 포인트 */
    .ranking-item span {
        margin-right: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

    # 랭킹 리스트 중앙 정렬
    st.markdown("<div class='ranking-container'>", unsafe_allow_html=True)

    congestion_rank = sorted(all_predictions, key=lambda x: x['congestion_level'])

    for idx, pred in enumerate(congestion_rank):
        status, color = get_congestion_status(pred['congestion_level'])
        st.markdown(
            f"""
            <div class='ranking-item'>
                <span style='color: {color}; font-size: 1.5em;'>●</span>  <!-- 📌 색깔 공(●) 추가 -->
                {idx+1}. <strong>{pred['site']}</strong> - 혼잡도: {pred['congestion_level']:.2f}% ({status})
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("</div>", unsafe_allow_html=True)

# 🎯 대안 추천지
alternative_site = congestion_rank[0]  # 가장 여유로운 장소 선택
st.markdown(
    f"""
    <div style="padding: 20px; border-radius: 10px; background-color: #e3fcef; text-align: center;">
        <h2>🔥 대안 추천 관광지</h2>
        <h3>🎉 <b>{alternative_site['site']}</b> 에 방문해보세요!</h3>
        <h4>👥 예상 방문자수: {alternative_site['predicted_visitors']}명</h4>
        <h4>📊 혼잡도: {alternative_site['congestion_level']:.2f}%</h4>
    </div>
    """,
    unsafe_allow_html=True
)
