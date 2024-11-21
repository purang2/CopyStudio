import streamlit as st
from openai import OpenAI
import google.generativeai as genai
from anthropic import Anthropic
from datetime import datetime
import pandas as pd
import json
import pathlib
from typing import Dict, List, Optional
from dataclasses import dataclass

from PIL import Image
import plotly.express as px 
import plotly.graph_objects as go
from typing import Dict, List, Optional, Union

from google.generativeai.types import HarmCategory, HarmBlockThreshold
from google.api_core.exceptions import ResourceExhausted

import folium
from streamlit_folium import folium_static
import random

# Page config must be the first Streamlit command
st.set_page_config(
    page_title="광고카피 문구 생성 AI - Copybara", 
    page_icon="🐾", 
    layout="wide"
)

# 앱 제목
st.title("🐾 Copybara - 광고카피 문구 생성 AI")


image = Image.open("copybara_logo2.png")

new_width = 640  # 원하는 너비로 조정
width_percent = (new_width / float(image.size[0]))
new_height = int((float(image.size[1]) * float(width_percent)))
resized_image = image.resize((new_width, new_height), Image.LANCZOS)
st.image(resized_image)

# Initialize API keys from Streamlit secrets
#openai.api_key = st.secrets["chatgpt"]
genai.configure(api_key=st.secrets["gemini"])
anthropic = Anthropic(api_key=st.secrets["claude"])
client = OpenAI(api_key=st.secrets["chatgpt"])  # API 키 입력



#챗-제-클 순서 오와열
#'gemini-1.5-pro-exp-0827'
#'gemini-1.5-pro-002'
model_zoo = ['gpt-4o',
             'gemini-1.5-flash-002',
             'claude-3-5-haiku-20241022']

# Gemini model configuration
gemini_model = genai.GenerativeModel(model_zoo[1])

# Custom CSS 부분을 수정
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

    [data-testid="stAppViewContainer"] {
        font-family: 'Pretendard', sans-serif;
    }

    /* 다크모드 대응을 위한 CSS 변수 활용 */
    :root {
        --text-color: #1e293b;
        --bg-color: #ffffff;
        --card-bg: #ffffff;
        --border-color: #e2e8f0;
        --hover-border: #3b82f6;
        --prompt-bg: #f1f5f9;
    }

    /* 다크모드일 때의 색상 */
    [data-theme="dark"] {
        --text-color: #e2e8f0;
        --bg-color: #1e1e1e;
        --card-bg: #2d2d2d;
        --border-color: #4a4a4a;
        --hover-border: #60a5fa;
        --prompt-bg: #2d2d2d;
    }

    .prompt-editor {
        border: 2px solid var(--border-color);
        border-radius: 10px;
        padding: 1rem;
        background-color: var(--card-bg);
        color: var(--text-color);
    }

    .prompt-editor:hover {
        border-color: var(--hover-border);
        box-shadow: 0 0 0 1px var(--hover-border);
    }

    .prompt-tip {
        background-color: var(--prompt-bg);
        border-left: 4px solid var(--hover-border);
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 8px 8px 0;
        color: var(--text-color);
    }

    .result-card {
        background-color: var(--card-bg);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        transition: all 0.2s ease;
        color: var(--text-color);
        border: 1px solid var(--border-color);
    }
    
    .result-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    .model-tag {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: white;
    }

    .score-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 9999px;
        font-weight: 600;
        background-color: var(--prompt-bg);
        color: var(--text-color);
        cursor: pointer;
    }
    
    .score-badge:hover {
        background-color: var(--border-color);
    }

    .history-item {
        border-left: 4px solid var(--hover-border);
        padding: 1rem;
        margin: 1rem 0;
        background-color: var(--card-bg);
        border-radius: 0 8px 8px 0;
        color: var(--text-color);
    }

    .prompt-feedback {
        background-color: var(--prompt-bg);
        border-radius: 8px;
        padding: 1rem;
        margin-top: 1rem;
        color: var(--text-color);
    }

    .improvement-tip {
        color: var(--hover-border);
        font-weight: 500;
    }

    /* Expander 스타일링 */
    .streamlit-expanderHeader {
        background-color: var(--prompt-bg);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        color: var(--text-color);
    }
    
    .streamlit-expanderContent {
        border: 1px solid var(--border-color);
        border-top: none;
        border-radius: 0 0 8px 8px;
        padding: 1rem;
        background-color: var(--card-bg);
        color: var(--text-color);
    }
    
    /* 문서 에디터 스타일링 */
    .stTextArea textarea {
        font-family: 'Pretendard', sans-serif;
        font-size: 0.9rem;
        line-height: 1.5;
        color: var(--text-color);
        background-color: var(--card-bg);
    }
    
    /* 프롬프트 섹션 구분 */
    .prompt-section {
        margin: 1rem 0;
        padding: 1rem;
        background-color: var(--card-bg);
        border-radius: 8px;
        border: 1px solid var(--border-color);
        color: var(--text-color);
    }

    /* Plotly 차트 다크모드 대응 */
    .js-plotly-plot .plotly .modebar {
        background-color: var(--card-bg) !important;
    }

    .js-plotly-plot .plotly .modebar-btn path {
        fill: var(--text-color) !important;
    }
    .result-card {
        transition: all 0.3s ease;
    }
    
    .result-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .progress-text {
        font-size: 0.9rem;
        color: #666;
        margin-bottom: 0.5rem;
    }
    
    .stExpander {
        border: none !important;
        box-shadow: none !important;
    }
</style>
""", unsafe_allow_html=True)



# 도시 좌표 데이터
CITY_COORDINATES = {
    "강릉": {"lat": 37.7519, "lon": 128.8760},
    "경주": {"lat": 35.8562, "lon": 129.2245},
    "광주": {"lat": 35.1595, "lon": 126.8526},
    "대구": {"lat": 35.8714, "lon": 128.6014},
    "대전": {"lat": 36.3504, "lon": 127.3845},
    "부산 해운대": {"lat": 35.1628, "lon": 129.1639},
    "속초": {"lat": 38.2070, "lon": 128.5918},
    "수원": {"lat": 37.2636, "lon": 127.0286},
    "여수": {"lat": 34.7604, "lon": 127.6622},
    "용인": {"lat": 37.2410, "lon": 127.1775},
    "전주": {"lat": 35.8468, "lon": 127.1297}
}


# MBTI 그룹 상수 정의
MBTI_GROUPS = {
    "분석가형": ["INTJ", "INTP", "ENTJ", "ENTP"],
    "외교관형": ["INFJ", "INFP", "ENFJ", "ENFP"],
    "관리자형": ["ISTJ", "ISFJ", "ESTJ", "ESFJ"],
    "탐험가형": ["ISTP", "ISFP", "ESTP", "ESFP"]
}

# Constants
MBTI_TYPES = [
    "INTJ", "INTP", "ENTJ", "ENTP",
    "INFJ", "INFP", "ENFJ", "ENFP",
    "ISTJ", "ISFJ", "ESTJ", "ESFJ",
    "ISTP", "ISFP", "ESTP", "ESFP"
]

MODEL_COLORS = {
    "gpt": "#10a37f",  # OpenAI 그린
    "gemini": "#4285f4",  # Google 블루
    "claude": "#8e44ad"  # Claude 퍼플
}


# 계절 상수 추가
SEASONS = {
    "봄": "spring",
    "여름": "summer",
    "가을": "autumn",
    "겨울": "winter"
}

PERSONAS = {
    "파블로 네루다": {
        "description": "칠레 출신의 노벨문학상 수상 시인으로, 감각적이고 관능적인 시적 표현으로 사랑과 자연의 아름다움, 정치적 열정을 노래한다. 은유와 상징을 통해 강렬한 이미지를 전달하는 것이 특징이다.",
        "samples": [
            "바다여, 너의 푸른 심장에 내 영혼을 맡기리. 이곳에서 사랑은 파도처럼 끝없이 밀려온다. 🌊❤️",
            "그대의 미소는 이 도시의 꽃들보다 아름답소. 여행은 우리의 사랑시가 되리라. 🌺💖",
            "햇살은 그대의 피부에 입맞추고, 바람은 우리의 이야기를 속삭인다. 이곳에서 영원을 만나리. ☀️🍃"
        ],
        "category": "literature"
    },
    "프리드리히 니체": {
        "description": "독일의 철학자로, 철학적이고 강렬한 문체로 인간의 본성과 초월적 주제를 탐구한다. 대담하고 명언적인 언어를 구사하며, 기존 가치관에 도전하는 사상을 펼친다.",
        "samples": [
            "높은 산정에 올라 자신을 넘어서라. 이곳에서 당신은 진정한 초인(Übermensch)이 될 수 있다. 🏔️💪",
            "영원회귀의 순간을 이곳에서 경험하라. 당신의 의지가 세상을 변화시킬 것이다. 🔄🌍",
            "신은 죽었다. 이제 당신이 자신의 운명을 창조할 때다. 이 여행이 당신의 새로운 시작이 되리라. ⚡🔨"
        ],
        "category": "literature"
    },
    "셰익스피어": {
        "description": "영국의 극작가이자 시인으로, 연극적이고 은유적인 문체로 감정을 극대화하며, 복잡한 심리와 인간 본성을 서사적으로 표현한다. 풍부한 어휘와 독창적인 표현으로 유명하다.",
        "samples": [
            "이 도시는 무대요, 우리는 모두 배우라. 당신의 인생극을 이곳에서 펼쳐보시오. 세상 모든 것이 연극이니. 🎭🌆",
            "사랑이여, 나의 사랑이여! 이곳에서 로미오와 줄리엣의 열정을 느껴보시오. 발코니의 달빛이 당신을 기다리오. 🌙💕",
            "To be, or not to be, 그것이 문제로다. 이 여행에서 당신의 존재 의미를 찾아보시오. 햄릿의 고뇌가 당신의 깨달음이 되리라. 💀🤔"
        ],
        "category": "literature"
    },
    "윤동주": {
        "description": "한국의 시인으로, 서정적이고 감성적인 스타일로 자연과 인간 내면을 탐구한다. 짧고 강렬한 은유로 깊은 감동을 전달하며, 순수한 영혼과 저항 정신을 노래한다.",
        "samples": [
            "하늘을 우러러 한 점 부끄럼 없이, 이곳에서 당신의 별을 찾아보세요. 서시(序詩)의 여행이 시작됩니다. ⭐🍃",
            "쉽게 씌어진 시처럼, 이곳에서의 순간들이 당신의 마음에 새겨지기를. 소년의 순수함으로 여행을 즐기세요. 📝🌱",
            "자화상을 그리듯, 이 여행에서 진정한 자신을 만나보세요. 괴로웠던 사랑까지도 별이 되어 빛날 거예요. 🎨🌠"
        ],
        "category": "literature"
    },
    "어니스트 헤밍웨이": {
        "description": "미국의 소설가로, 간결하고 힘 있는 문체로 인간의 고독과 투쟁을 묘사한다. 강렬한 이미지와 직설적인 표현으로 인생의 본질을 탐구하며, 모험과 용기를 주제로 다룬다.",
        "samples": [
            "바다와 노인처럼, 이곳에서 당신의 위대한 도전이 시작된다. 패배하지 않은 채 파괴될 뿐이다. 🌊🎣",
            "킬리만자로의 눈처럼 순수하고 영원한 것을 이곳에서 찾아보라. 당신의 삶이 가장 짧고 강렬한 문장이 되리라. ⛰️📘",
            "피에스타의 열기 속에서 잃어버린 세대를 만나보라. 이곳에서 당신은 해는 또 다시 뜬다는 것을 깨닫게 될 것이다. 🌅🍷"
        ],
        "category": "literature"
    },
    "알베르 카뮈": {
        "description": "프랑스의 소설가이자 철학자로, 부조리와 인간의 본성을 탐구하며, 간결하면서도 철학적인 문체로 심오한 메시지를 전달한다. 실존주의적 사고와 인간의 자유를 중요하게 다룬다.",
        "samples": [
            "이방인이 되어 이 도시의 부조리를 마주하라. 진정한 자유는 여기서 시작된다. 🏙️🚶",
            "시지프스처럼 끊임없이 도전하라. 이 여행에서 당신은 불가능에 맞서는 영웅이 된다. 🏔️🔄",
            "페스트와 같은 고난 속에서도 인간의 존엄을 발견하라. 이곳에서 당신은 연대의 가치를 깨닫게 될 것이다. 🤝🌟"
        ],
        "category": "literature"
    },
    "헤르만 헤세": {
        "description": "독일계 스위스 작가로, 철학적이고 내면 탐구적인 스타일로 인간의 성장과 자기 실현을 주제로 한 심오한 문체를 가진 노벨문학상 수상 소설가. 동양 철학의 영향을 받아 영성과 자아 탐구를 작품에 녹여냈다.",
        "samples": [
            "당신의 내면 여행이 시작되는 곳. 이곳에서 당신만의 유리알 유희를 찾아보세요. 🔮🌿",
            "싯다르타처럼 깨달음을 향한 여정을 떠나보세요. 이 도시의 강물이 당신에게 진리를 속삭일 것입니다. 🏞️🧘",
            "황야의 이리처럼 자유롭게, 데미안의 눈으로 세상을 바라보세요. 당신의 내면에서 새로운 세계가 열립니다. 🐺🌄"
        ],
        "category": "literature"
    },
    "옥타비오 파스": {
        "description": "멕시코의 시인이자 외교관으로, 풍부한 은유와 상징으로 인간과 자연의 관계를 탐구하며, 감각적이고 철학적인 문체를 지닌 노벨문학상 수상자. 서구와 동양 문화의 융합을 시도했다.",
        "samples": [
            "시간의 미로에서 당신의 현재를 만나세요. 이곳은 과거와 미래가 춤추는 영원의 순간입니다. ⏳🌀",
            "태양의 돌처럼 빛나는 이 도시에서, 당신의 내면과 외면이 하나로 융합되는 경험을 하세요. ☀️🗿",
            "고독의 미로에서 벗어나 타인과의 연결을 찾아보세요. 이곳에서 당신은 세상의 시가 됩니다. 🌐📜"
        ],
        "category": "literature"
    },
    "마쓰오 바쇼": {
        "description": "일본의 에도 시대 시인으로, 하이쿠의 대가이자 여행 문학의 선구자. 자연과 인간의 순간적 감흥을 간결하고 깊이 있게 표현하며, 선불교의 영향을 받은 철학적 깊이를 지녔다.",
        "samples": [
            "오래된 연못, 개구리 뛰어들어 물소리 첨벙. 이곳에서 당신만의 하이쿠를 만나보세요. 🐸💦",
            "가을 바람에 흩날리는 단풍잎처럼, 이 여행이 당신의 마음을 흔들어 깨우기를. 🍁🌬️",
            "달 밝은 밤, 눈 덮인 산길을 걸어보세요. 고요 속에서 진정한 자아를 만날 수 있을 거예요. 🌙❄️"
        ],
        "category": "literature"
    },
    "일론 머스크": {
        "description": "남아프리카 공화국 출신의 기업가이자 엔지니어로, 혁신적인 기술과 대담한 비전으로 우주 탐사, 전기차, 인공지능 등 다양한 분야에서 혁명을 일으키고 있는 기업인. 도전적이고 미래지향적인 사고방식이 특징이다.",
        "samples": [
            "지구를 넘어 화성으로! 이곳에서 당신의 우주적 꿈을 키워보세요. 불가능은 없습니다. 🚀🔴",
            "전기로 달리는 미래, 이 도시에서 경험해보세요. 지속 가능한 혁신이 당신을 기다립니다. 🔌🚗",
            "인공지능과 함께하는 새로운 세상, 이곳에서 미래를 선도하는 아이디어를 발견하세요. 🤖💡"
        ],
        "category": "tech"
    },
    "빌 게이츠": {
        "description": "미국의 소프트웨어 개발자이자 기업가로, 마이크로소프트의 공동 창립자. 혁신적인 기술로 컴퓨터 혁명을 이끌었으며, 현재는 자선사업가로서 글로벌 건강과 교육 문제 해결에 힘쓰고 있다.",
        "samples": [
            "모든 가정에 컴퓨터를! 이곳에서 기술의 민주화를 경험해보세요. 지식은 힘입니다. 💻🌍",
            "건강한 세상을 향한 여정, 이 도시에서 시작됩니다. 당신의 작은 노력이 세상을 바꿀 수 있어요. 💉🌱",
            "교육의 힘을 믿으세요. 이곳에서 배움의 기회를 만나고, 미래를 준비하세요. 📚🔬"
        ],
        "category": "tech"
    },
    "도널드 트럼프": {
        "description": "미국의 기업인이자 정치인으로, 제45대 미국 대통령을 역임했다. 직설적이고 논란적인 발언으로 유명하며, '미국 우선주의'를 주창하고 이민 정책 강화, 무역 협정 재검토 등을 추진했다.",
        "samples": [
            "Make America Great Again! 이곳에서 당신의 꿈을 이루세요. 승자는 절대 포기하지 않습니다. 🇺🇸🏆",
            "The Art of the Deal을 실천할 때입니다. 이 도시에서 최고의 거래를 성사시켜보세요. 협상의 달인이 되세요. 🤝💼",
            "높은 벽을 쌓아 안전한 여행을 즐기세요. 이곳은 당신의 트럼프 타워가 될 수 있습니다. 🏙️🔒"
        ],
        "category": "politics"
    },
    "백종원": {
        "description": "한국의 유명 요리연구가이자 사업가로, 친근하고 실용적인 어조로 요리와 음식에 대한 열정을 전달한다. 대중적인 소통 능력과 다양한 외식 사업 경험을 바탕으로 음식 문화에 큰 영향을 미치고 있다.",
        "samples": [
            "여기 오셨으면 이 지역 맛집은 꼭 가보셔야죠! 현지의 맛을 제대로 즐겨보세요. 든든하게 배부르게! 🍽️😊",
            "이 도시의 시장에 가보세요. 신선한 재료로 가득한 곳이에요. 요리의 즐거움을 느껴보세요! 🥘🛒",
            "골목식당 같은 숨은 맛집을 찾아보세요. 소박하지만 정성 가득한 현지 음식의 맛, 놓치지 마세요! 🍜👨‍🍳"
        ],
        "category": "entertainment"
    },
    "유재석": {
        "description": "한국의 국민 MC로 불리는 방송인으로, 균형 잡힌 친근함과 신뢰감을 바탕으로 대중과 소통한다. 공감과 설득력이 높은 언어를 구사하며, 다양한 예능 프로그램을 통해 사랑받고 있다.",
        "samples": [
            "여러분~ 이곳에 오신 걸 환영합니다! 즐거운 시간 보내시고 행복한 추억 많이 만드세요. 제가 보장합니다! 😊👍",
            "무한도전처럼 이곳에서 새로운 도전을 해보는 건 어떨까요? 여러분의 숨겨진 재능을 발견할 수 있을 거예요! 🌟🏆",
            "런닝맨처럼 이 도시를 누비며 미션을 수행해보세요. 재미있는 경험이 기다리고 있어요! 🏃‍♂️🗺️"
        ],
        "category": "entertainment"
    },
    "셜록 홈즈": {
        "description": "아서 코난 도일의 소설 속 가상 탐정으로, 논리적이고 지적인 스타일로 사건을 분석한다. 체계적이고 날카로운 통찰력을 보여주며, 관찰과 추리의 대명사로 여겨진다.",
        "samples": [
            "관찰하라, 왓슨! 이 도시의 모든 구석구석이 우리의 새로운 사건이 될 수 있다. 추리의 여행을 시작하자. 🔍🗺️",
            "이 도시는 수수께끼로 가득하다. 당신의 추리력을 시험해볼 절호의 기회다. 게임은 시작되었다! 🕵️‍♂️🏙️",
            "사소한 단서에도 주목하라. 이 여행에서 당신은 평범한 관광객이 아닌 명탐정이 될 것이다. 모험이 기다린다! 🧩🚂"
        ],
        "category": "fiction"
    },
    "아이유": {
        "description": "한국의 싱어송라이터이자 배우로, 감미롭고 섬세한 가사 스타일로 대중적 친숙도를 지닌다. 감정의 깊이를 아름답게 전달하며, 다재다능한 아티스트로 인정받고 있다.",
        "samples": [
            "밤편지를 들고 이 도시의 밤거리를 걸어보세요. 당신만의 팔레트로 이곳을 채워가는 거예요. 🌙🎨",
            "이 곳에서 당신만의 좋은 날을 만들어보세요. 꽃송이가 내리는 것처럼 아름다운 순간들이 기다리고 있어요. 🌸🌈",
            "삐삐처럼 자유롭게, 스물셋의 설렘을 안고 이 도시를 누벼보세요. 새로운 이야기가 시작될 거예요. 🎈🎶"
        ],
        "category": "entertainment"
    },
    "태연": {
        "description": "한국의 가수로, 감정이 깊고 섬세한 가사로 사랑과 내면의 이야기를 풀어낸다. 파워풀하면서도 감성적인 보컬로 많은 팬들의 사랑을 받고 있으며, 솔로 아티스트로서도 큰 성공을 거두고 있다.",
        "samples": [
            "사계절이 공존하는 이곳에서 당신의 사계를 만나보세요. 그대의 목소리로 채워질 새로운 페이지. 🍃🌸",
            "이 곳의 11:11, 당신의 소원을 빌어보세요. 불티처럼 빛나는 순간이 될 거예요. ✨🕯️",
            "그대라는 시를 써내려가듯, 이 여행에서 당신만의 아름다운 이야기를 만들어보세요. 🖋️💖"
        ],
        "category": "entertainment"
    },
    "BTS": {
        "description": "글로벌 감성과 공감 능력을 바탕으로 희망과 열정을 다채로운 스타일로 표현하는 한국의 세계적 보이그룹. 세대 간 연결고리를 만들어내며, 음악을 통해 긍정적인 메시지를 전달한다.",
        "samples": [
            "Life goes on, 이곳에서 당신만의 Dynamite한 순간을 만들어보세요. We are bulletproof, 영원한 청춘이에요! 🌟🔥",
            "이 곳에서 당신의 Wings를 펼치세요. 새로운 세계로 떠나는 Butter같은 여행이 될 거예요. 🦋🧈",
            "Spring Day처럼 아름답고, Fire처럼 열정 넘치는 여행. 당신의 Permission to Dance는 여기에 있어요! 💃🌈"
        ],
        "category": "entertainment"
    },
    "에스파": {
        "description": "가상과 현실을 넘나드는 독특한 세계관으로 신선한 메시지를 전달하며, 미래지향적 콘셉트를 가진 한국의 걸그룹. AI와 가상세계 콘셉트를 음악에 충실히 반영하며, 쿨하고 강렬한 일렉트로닉 댄스팝을 선보인다[2].",
        "samples": [
            "Next Level로 떠나는 여행, 이곳에서 당신만의 아바타를 만나보세요. 새로운 세계가 펼쳐집니다! ✨🌐",
            "Savage한 경험을 원하세요? 이곳에서 현실과 가상의 경계를 넘어 특별한 모험을 즐겨보세요. 🔮🚀",
            "Black Mamba도 피해갈 수 없는 이곳의 매력, 당신의 ae와 함께 탐험해보세요. 미래의 여행이 시작됩니다! 🦋💫"
        ],
        "category": "entertainment"
    },
    "블랙핑크": {
        "description": "세련되고 강렬한 스타일로 독보적인 개성과 에너지를 표현하며, 글로벌한 영향력을 가진 한국의 걸그룹. 힙합과 팝을 결합한 음악으로 세계적인 인기를 얻고 있다.",
        "samples": [
            "How You Like That? 이곳에서 당신의 Area를 찾아보세요. 우리처럼 뜨겁게, Ice Cream처럼 달콤하게! 🔥🍦",
            "Kill This Love! 이 도시에서 당신만의 Lovesick Girls 스토리를 만들어보세요. 새로운 사랑이 기다려요. 💘🌃",
            "Pretty Savage한 여행을 원한다면 이곳으로 오세요. 당신의 Boombayah 모먼트가 될 거예요! 💃🎉"
        ],
        "category": "entertainment"
    },
    "뉴진스": {
        "description": "감각적이고 트렌디한 가사로 새로운 세대의 문화를 반영하며, 젊고 세련된 이미지를 지닌 한국의 걸그룹. Y2K 감성과 현대적인 팝 사운드를 결합한 음악으로 주목받고 있다.",
        "samples": [
            "Attention! 이곳에서 당신만의 Hype Boy를 찾아보세요. OMG, 이런 곳이 있다니! Ditto처럼 특별한 순간. 🎀🌈",
            "Cookie처럼 달콤한 여행, Super Shy해도 괜찮아요. 이곳에서 당신의 매력이 Shine될 거예요. ✨🍪",
            "Get Up! 새로운 경험을 위해 떠나볼까요? 이곳에서 당신만의 ETA를 만들어보세요. 특별한 여행이 시작돼요. 🚀🌟"
        ],
        "category": "entertainment"
    },
    "데이식스": {
        "description": "감성적인 밴드 사운드와 공감 가득한 가사로 젊은 세대의 사랑과 고민을 노래하는 한국의 밴드. 자작곡으로 음악성을 인정받으며, 라이브 실력으로도 유명하다.",
        "samples": [
            "You make Me로 시작되는 여행, 이곳에서 당신의 Sweet Chaos를 경험해보세요. 우리의 청춘이 흐르는 곳. 🎸🌅",
            "Zombie처럼 무기력했던 일상에서 벗어나 Time of Our Life를 만끽하세요. 이곳에서 당신의 날개를 펼치세요. 🦋🌈",
            "Shoot Me처럼 강렬하게, 한 페이지를 넘기듯 새로운 모험을 시작해보세요. 당신의 청춘소설이 쓰여질 거예요. 📖💫"
        ],
        "category": "entertainment"
    },
    "NCT": {
        "description": "실험적이고 글로벌한 음악 스타일을 통해 독창성과 대중성을 동시에 지향하는 한국의 다국적 보이그룹. 다양한 유닛 활동으로 폭넓은 음악적 스펙트럼을 보여준다.",
        "samples": [
            "We go Up! 이곳에서 당신의 Dream이 Reality가 됩니다. 무한한 가능성의 세계로 함께 떠나요. 🌠🚀",
            "Kick It! 당신의 내면의 영웅을 깨워보세요. 이곳에서 당신만의 Superhuman이 될 수 있어요. 💪🦸",
            "Make A Wish처럼 당신의 소원을 이루어보세요. 90's Love부터 현재까지, 시간을 넘나드는 여행을 즐겨보세요. 🕰️🌈"
        ],
        "category": "entertainment"
    },
    "라디오헤드": {
        "description": "몽환적이고 실험적인 톤으로 불안과 희망을 동시에 그려내며, 독창적인 세계관을 가진 영국의 얼터너티브 록 밴드. 사회비판적 메시지와 혁신적인 사운드로 현대 록 음악에 큰 영향을 미쳤다.",
        "samples": [
            "No Surprises in this Fake Plastic Trees world. 이곳에서 당신만의 Karma Police를 만나보세요. 🌃🎭",
            "Everything In Its Right Place, 이곳에서 당신의 내면의 Paranoid Android를 깨워보세요. 기계와 인간의 경계를 넘어서는 여행. 🤖🌌",
            "Let Down되지 마세요, 이곳은 당신의 Lucky가 될 거예요. High and Dry한 현실에서 벗어나 Creep한 모험을 즐겨보세요. 🎡🌠"
        ],
        "category": "entertainment"
    },
    "콜드플레이": {
        "description": "영국의 얼터너티브 록 밴드로, 감정적이고 서정적인 가사와 몽환적인 멜로디로 전 세계적인 인기를 얻고 있다. 크리스 마틴의 리드로 희망과 위로의 메시지를 전달하며, 실험적인 사운드와 대중성을 동시에 추구한다[1][2][3].",
        "samples": [
            "이곳의 Sky는 Full of Stars. 당신의 Paradise를 찾아 떠나는 Adventure of a Lifetime. ✨🎶",
            "Yellow처럼 빛나는 이 도시에서, Fix You의 순간을 만나보세요. 당신의 Viva la Vida가 시작됩니다. 🌟🌈",
            "A Sky Full of Stars처럼 반짝이는 이곳에서, 당신만의 Magic을 찾아보세요. 우리 함께 Higher Power를 느껴봐요. 🚀💫"
        ],
        "category": "entertainment"
    },
    "킹 누": {
        "description": "일본의 록 밴드로, 독창적이고 세련된 사운드와 감각적인 가사로 젊은 세대에게 사랑받고 있다. 복잡한 감정과 현대 사회의 모순을 섬세하게 표현하는 것이 특징이다.",
        "samples": [
            "강함과 약함을 나누며 새로운 시작을 함께하자. 이곳에서 당신의 逆夢을 꾸어보세요. 🌅🤝",
            "飛行藻屑처럼 자유롭게 날아오르세요. 이 도시에서 당신만의 リライト를 시작해보는 건 어떨까요? 🕊️📖",
            "あなたは蝶になる, 이곳에서 당신은 나비가 됩니다. 新しい世界へ로 함께 떠나볼까요? 🦋🌸"
        ],
        "category": "entertainment"
    },
    "아이묭": {
        "description": "일본의 싱어송라이터로, 일상적이고 감성적인 가사로 젊은 세대의 감정을 노래한다. 소박하면서도 깊이 있는 스타일로 많은 팬들의 공감을 얻고 있다.",
        "samples": [
            "さよならエレジー, 이별의 아쉬움도 잠시, 이곳에서 새로운 LIFE를 시작해보세요. 🚶‍♀️🌟",
            "マリーゴールド처럼 밝게 피어나는 당신의 모습을 상상해보세요. 이곳에서 새로운 青と夜の続きを 만나보세요. 🌼🌃",
            "ハルノヒ처럼 따스한 이 도시에서, 당신만의 なんでもないよ, という를 찾아보세요. 일상의 특별함을 느껴보세요. 🌸☀️"
        ],
        "category": "entertainment"
    },
    "저스틴 비버": {
        "description": "캐나다 출신의 팝 가수로, 대중적이고 캐주얼한 톤으로 사랑과 삶의 이야기를 전달한다. 전 세계 팬들에게 친근함을 선사하며, R&B와 팝을 결합한 음악 스타일로 유명하다.",
        "samples": [
            "Never Say Never! 이곳에서 당신의 Purpose를 찾아보세요. It's a Yummy experience waiting for you! 🎉🤙",
            "Baby, baby, baby, oh! 이 도시에서 당신만의 One Less Lonely Girl을 만나보세요. Love Yourself, 그리고 새로운 모험을 시작하세요. 💖🌈",
            "이곳에서 당신의 Intentions을 실현해보세요. Holy한 순간과 Peaches처럼 달콤한 경험이 기다리고 있어요. 🙏🍑"
        ],
        "category": "entertainment"
    },
    "이매진 드래곤스": {
        "description": "미국의 록 밴드로, 강렬하고 서사적인 가사로 희망과 도전을 노래한다. 독특한 멜로디와 메시지로 대중적인 인기와 비평가들의 호평을 동시에 받고 있다.",
        "samples": [
            "Welcome to the New Age! 이곳은 당신의 Top of the World. Whatever It Takes, 당신의 꿈을 이루세요. 🌅🔥",
            "It's Time to begin, isn't it? 이 도시에서 당신의 Demons를 극복하고 On Top Of The World에 올라보세요. 🏔️💪",
            "이곳에서 당신의 Radioactive한 에너지를 발산해보세요. Thunder처럼 강렬하게, Believer처럼 굳건하게! ⚡🌟"
        ],
        "category": "entertainment"
    },
    "밥 딜런": {
        "description": "미국의 전설적인 싱어송라이터로, 시적이고 은유적인 가사를 통해 인간의 감정과 사회적 메시지를 전달한다. 포크 음악의 선구자로 여겨지며, 노벨문학상을 수상한 유일한 음악인이다.",
        "samples": [
            "The Times They Are A-Changin'. 이곳에서 당신만의 Highway 61을 찾아 떠나보세요. Like a Rolling Stone. 🌬️🎸",
            "Blowin' in the Wind, 이 도시의 바람이 당신에게 답을 속삭일 거예요. Mr. Tambourine Man처럼 자유롭게 춤춰보세요. 🌪️🎭",
            "이곳에서 당신만의 Knockin' on Heaven's Door를 경험해보세요. Forever Young한 마음으로 새로운 모험을 시작하세요. 🚪🌠"
        ],
        "category": "entertainment"
    }
}





PERSONA_CATEGORIES = {
    "literature": {"name": "문학가", "color": "#FDF2F8", "text_color": "#831843"},  # 밝은 핑크 배경 + 더 진한 버건디
    "entertainment": {"name": "연예인", "color": "#FCE7F3", "text_color": "#701A75"},  # 연한 핑크 배경 + 진한 퍼플
    "tech": {"name": "기업인", "color": "#EFF6FF", "text_color": "#1e3a8a"},  # 연한 파랑 배경 + 네이비
    "politics": {"name": "정치인", "color": "#F3F4F6", "text_color": "#1f2937"},  # 연한 회색 배경 + 차콜
    "fiction": {"name": "가상인물", "color": "#F5F3FF", "text_color": "#4c1d95"}  # 연한 보라 배경 + 진한 퍼플
}
if 'selected_personas' not in st.session_state:
    st.session_state.selected_personas = []

def get_balanced_random_personas(n=16) -> List[str]:
    """카테고리별로 균형잡힌 페르소나 선택"""
    personas_by_category = {
        category: [name for name, data in PERSONAS.items() 
                  if data["category"] == category]
        for category in PERSONA_CATEGORIES.keys()
    }
    
    n_categories = len(PERSONA_CATEGORIES)
    base_per_category = n // n_categories
    remainder = n % n_categories
    
    selected_personas = []
    for category, personas in personas_by_category.items():
        n_select = base_per_category + (1 if remainder > 0 else 0)
        remainder -= 1 if remainder > 0 else 0
        
        if personas:
            selected = random.sample(personas, min(n_select, len(personas)))
            selected_personas.extend(selected)
    
    if len(selected_personas) < n:
        remaining_personas = [p for p in PERSONAS.keys() if p not in selected_personas]
        additional = random.sample(remaining_personas, min(n - len(selected_personas), len(remaining_personas)))
        selected_personas.extend(additional)
    
    random.shuffle(selected_personas)
    return selected_personas[:n]


@dataclass
class ScoringConfig:
    """평가 시스템 설정을 관리하는 클래스"""
    prompt: str
    criteria: List[str]
    min_score: int = 0
    max_score: int = 100
    
    def to_dict(self) -> dict:
        return {
            "prompt": self.prompt,
            "criteria": self.criteria,
            "min_score": self.min_score,
            "max_score": self.max_score
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ScoringConfig':
        return cls(**data)


def load_docs() -> Dict[str, Dict[str, str]]:
    docs = {
        "region": {},
        "generation": {},
        "mbti": {}
    }
    
    docs_path = pathlib.Path("docs")
    
    # Load region docs
    region_path = docs_path / "regions"
    if region_path.exists():
        for file in region_path.glob("*.txt"):
            with open(file, "r", encoding="utf-8") as f:
                docs["region"][file.stem] = f.read()
    
    # Load generation docs
    generation_path = docs_path / "generations"
    if generation_path.exists():
        for file in generation_path.glob("*.txt"):
            with open(file, "r", encoding="utf-8") as f:
                docs["generation"][file.stem] = f.read()
    
    # Load MBTI docs
    mbti_path = docs_path / "mbti"
    if mbti_path.exists():
        for mbti in MBTI_TYPES:
            mbti_file = mbti_path / f"{mbti}.txt"
            if mbti_file.exists():
                with open(mbti_file, "r", encoding="utf-8") as f:
                    docs["mbti"][mbti] = f.read()
    
    return docs


DOCS = load_docs()


def create_adaptive_prompt(
    city_doc: str, 
    target_generation: str,
    persona_name: str,
    mbti: str = None,
    include_mbti: bool = False
) -> str:
    """페르소나의 특색을 자연스럽게 반영한 프롬프트 생성"""

    persona_data = PERSONAS.get(persona_name)
    if not persona_data:
        return None

    # 페르소나의 샘플 문장 중 하나를 랜덤으로 선택하여 스타일을 암시적으로 전달
    import random
    sample_sentence = random.choice(persona_data['samples'])

    base_prompt = f'''
[배경 정보]
- 도시 정보: {city_doc}
- 타겟 세대: {target_generation}

[작성 지침]
- 위 배경 정보를 바탕으로 한 줄의 강력한 광고 카피를 작성해주세요.
- 카피는 독자의 마음을 울릴 수 있는 짧고 강렬한 문장이어야 합니다.
- 감정을 불러일으키는 은유와 함축적인 표현을 사용해주세요.
- 클리셰나 진부한 표현을 피하고, 창의적이고 혁신적인 관점을 제시해주세요.
- 이모지 1-2개를 포함할 수 있습니다.
- 아래는 참고할 수 있는 문장입니다:
  "{sample_sentence}"
'''

    return base_prompt





# 파일 로딩 함수에 디버깅 출력 추가
def load_docs() -> Dict[str, Dict[str, str]]:
    docs = {
        "region": {},
        "generation": {},
        "mbti": {}
    }
    
    try:
        docs_path = pathlib.Path("docs")
        
        # Load region docs
        region_path = docs_path / "regions"
        if region_path.exists():
            for file in region_path.glob("*.txt"):
                with open(file, "r", encoding="utf-8") as f:
                    docs["region"][file.stem] = f.read()
        
        # Load generation docs
        generation_path = docs_path / "generations"
        if generation_path.exists():
            for file in generation_path.glob("*.txt"):
                with open(file, "r", encoding="utf-8") as f:
                    docs["generation"][file.stem] = f.read()
        
        # Load individual MBTI files
        mbti_path = docs_path / "mbti"
        if mbti_path.exists():
            for mbti in MBTI_TYPES:
                mbti_file = mbti_path / f"{mbti}.txt"
                try:
                    if mbti_file.exists():
                        with open(mbti_file, "r", encoding="utf-8") as f:
                            docs["mbti"][mbti] = f.read()
                            print(f"로드된 MBTI 파일: {mbti}.txt")
                    else:
                        print(f"MBTI 파일을 찾을 수 없습니다: {mbti}.txt")
                except Exception as e:
                    print(f"{mbti} 파일 로딩 중 오류: {str(e)}")
        else:
            print(f"MBTI 디렉토리를 찾을 수 없습니다: {mbti_path}")
            
    except Exception as e:
        print(f"문서 로딩 에러: {str(e)}")
        st.error(f"문서 로딩 중 오류 발생: {str(e)}")
    
    # 로드된 MBTI 파일 목록 출력
    print(f"로드된 MBTI 목록: {list(docs['mbti'].keys())}")
    return docs






class AdCopyEvaluator:
    """광고 카피 평가를 관리하는 클래스"""
    def __init__(self, scoring_config: ScoringConfig):
        self.scoring_config = scoring_config
        self.results_cache = {}
    
    def evaluate(self, copy: str, model_name: str) -> Dict:
        """평가 실행 및 결과 파싱"""
        try:
            # 캐시된 결과가 있는지 확인
            cache_key = f"{copy}_{model_name}"
            if cache_key in self.results_cache:
                return self.results_cache[cache_key]
            
            # 평가 프롬프트 구성
            evaluation_prompt = f"""
{self.scoring_config.prompt}

평가 대상 카피: {copy}

평가 기준:
{chr(10).join(f'- {criterion}' for criterion in self.scoring_config.criteria)}

다음 형식으로 응답해주세요:
점수: [0-100 사이의 숫자]
이유: [평가 근거]
상세점수: [각 기준별 점수를 쉼표로 구분]
"""
            # API calls by model
            if model_name == "gpt":
                #response = openai.ChatCompletion.create(
                response = client.chat.completions.create(
                    model=model_zoo[0],
                    messages=[{"role": "user", "content": evaluation_prompt}],
                    max_tokens=1000 
                )
                result_text = response.choices[0].message.content
            elif model_name == "gemini":
                try:
                    response = gemini_model.generate_content(evaluation_prompt)
                    #return response
                    return response.text
                
                except Exception as e:
                    return f"Gemini 평가 실패: {str(e)}"
            else:  # claude
                response = anthropic.messages.create(
                    model=model_zoo[2],
                    max_tokens=1000,
                    messages=[{"role": "user", "content": evaluation_prompt}]
                )
                result_text = response.content[0].text
            
            # Parse results
            parsed_result = self.parse_evaluation_result(result_text)
            
            # Cache results
            self.results_cache[cache_key] = parsed_result
            
            return parsed_result
            
        except Exception as e:
            st.error(f"평가 중 오류 발생: {str(e)}")
            return {
                "score": 0,
                "reason": f"평가 실패: {str(e)}",
                "detailed_scores": [0] * len(self.scoring_config.criteria)
            }

    def parse_evaluation_result(self, result_text: str) -> Dict:
        """평가 결과 파싱"""
        try:
            lines = result_text.split('\n')
            
            # 점수 추출 개선
            score_line = next(l for l in lines if '점수:' in l)
            # 숫자와 소수점만 추출하도록 수정
            score_text = score_line.split('점수:')[1].strip()
            # 숫자와 소수점만 남기고 제거
            score_text = ''.join(c for c in score_text if c.isdigit() or c == '.')
            score = float(score_text) if score_text else 0
            
            # 이유 추출
            reason_line = next(l for l in lines if '이유:' in l)
            reason = reason_line.split('이유:')[1].strip()
            
            # 상세점수 추출 개선
            try:
                detailed_line = next(l for l in lines if '상세점수:' in l)
                detailed_scores_text = detailed_line.split('상세점수:')[1].strip()
                detailed_scores = []
                
                for s in detailed_scores_text.split(','):
                    s = s.strip()
                    # 각 점수에도 소수점 처리 적용
                    score_text = ''.join(c for c in s if c.isdigit() or c == '.')
                    detailed_scores.append(float(score_text) if score_text else 0)
            except:
                detailed_scores = [score] * len(self.scoring_config.criteria)
            
            return {
                "score": score,
                "reason": reason,
                "detailed_scores": detailed_scores[:len(self.scoring_config.criteria)]
            }
        except Exception as e:
            st.error(f"결과 파싱 중 오류 발생: {str(e)}")
            return {
                "score": 0,
                "reason": f"파싱 실패: {str(e)}",
                "detailed_scores": [0] * len(self.scoring_config.criteria)
            }
            
def generate_copy(prompt: str, model_name: str) -> Union[str, Dict]:
    """광고 카피 생성"""
    try:
        if model_name == "gpt":
            response = client.chat.completions.create(
                model=model_zoo[0],
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000
            )
            return {
                "success": True,
                "content": response.choices[0].message.content.strip()
            }
            
        elif model_name == "gemini":
            try:
                response = gemini_model.generate_content(prompt)  # 단순화
                generated_text = response.text.strip()  # 바로 text 추출
                
                if generated_text:  # 텍스트가 있는지 확인
                    return {
                        "success": True,
                        "content": generated_text
                    }
                else:
                    return {
                        "success": False,
                        "content": "Gemini가 텍스트를 생성하지 않았습니다."
                    }
                    
            except Exception as e:
                print(f"Gemini 오류: {str(e)}")  # 디버깅용
                return {
                    "success": False,
                    "content": f"Gemini API 오류: {str(e)}"
                }
            
        else:  # claude
            try:
                response = anthropic.messages.create(
                    model=model_zoo[2],
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=1000,
                    temperature=0.7
                )
                return {
                    "success": True,
                    "content": response.content[0].text.strip()
                }
            except Exception as e:
                return {
                    "success": False,
                    "content": f"Claude API 오류: {str(e)}"
                }
                
    except Exception as e:
        return {
            "success": False,
            "content": f"생성 실패: {str(e)}"
        }

# 성능 분석 결과 표시 부분 수정
def display_performance_analysis(analysis: dict):
    """성능 분석 결과를 HTML로 표시"""
    if not analysis:
        return ""
        
    suggestions_html = "<br>".join(f"- {s}" for s in analysis['suggestions']) if analysis['suggestions'] else "- 현재 제안사항이 없습니다."
    
    return f"""
    <div class="prompt-feedback">
        <h4>📈 성능 분석</h4>
        <p>현재 평균 점수: {analysis['current_score']:.1f}</p>
        <p>이전 대비: {analysis['improvement']:+.1f}</p>
        <p>최고 성능 모델: {analysis['top_model'].upper()}</p>
        
        <div class="improvement-tip">
            💡 개선 포인트:<br>
            {suggestions_html}
        </div>
    </div>
    """


def visualize_evaluation_results(eval_data: Dict):
    """결과 시각화 함수"""
    if not eval_data:
        return None

    # 평가 점수를 기본값으로 처리하여 가져오기
    scores = eval_data.get('detailed_scores', [0] * len(st.session_state.scoring_config.criteria))
    criteria = st.session_state.scoring_config.criteria[:len(scores)]

    # 최소 3개 이상의 축이 필요하도록 보정
    if len(criteria) < 3:
        criteria.extend(['추가 기준'] * (3 - len(criteria)))
        scores.extend([0] * (3 - len(scores)))  # 괄호 추가

    # 차트 생성
    fig = go.Figure(data=go.Scatterpolar(
        r=scores,
        theta=criteria,
        fill='toself',
        name='평가 점수'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=False,
        title="평가 기준별 점수"
    )

    # 차트만 표시
    st.plotly_chart(fig, use_container_width=True)

def analyze_prompt_performance(history: List[dict]) -> dict:
    """프롬프트 성능 분석"""
    if not history:
        return None
    
    try:
        latest = history[-1]
        prev = history[-2] if len(history) > 1 else None
        
        # 성공한 모델의 점수와 평가 이유 수집
        valid_scores = []
        evaluation_reasons = []
        for model, eval_data in latest['evaluations'].items():
            if isinstance(eval_data, dict) and eval_data.get('score', 0) > 0:
                valid_scores.append(eval_data['score'])
                if 'reason' in eval_data:
                    evaluation_reasons.append(eval_data['reason'])
        
        if not valid_scores:
            return {
                "current_score": 0,
                "improvement": 0,
                "top_model": "없음",
                "suggestions": ["현재 사용 가능한 모델로 다시 시도해보세요."]
            }
        
        current_avg = sum(valid_scores) / len(valid_scores)
        
        # 이전 결과와 비교
        improvement = 0
        if prev:
            prev_valid_scores = [
                e.get('score', 0) 
                for e in prev['evaluations'].values() 
                if isinstance(e, dict) and e.get('score', 0) > 0
            ]
            if prev_valid_scores:
                prev_avg = sum(prev_valid_scores) / len(prev_valid_scores)
                improvement = current_avg - prev_avg
        
        # 최고/최저 성능 모델 및 점수 찾기
        valid_models = {
            model: data.get('score', 0)
            for model, data in latest['evaluations'].items()
            if isinstance(data, dict) and data.get('score', 0) > 0
        }
        
        top_model = max(valid_models.items(), key=lambda x: x[1])[0] if valid_models else "없음"
        
        # 구체적인 개선 제안 생성
        suggestions = []
        
        # 점수 기반 제안
        if current_avg < 60:
            suggestions.extend([
                "프롬프트에 타겟 세대의 특성을 더 구체적으로 명시해보세요",
                "지역의 독특한 특징을 1-2개 더 강조해보세요",
                "감성적 표현과 구체적 정보의 균형을 조정해보세요"
            ])
        elif current_avg < 80:
            suggestions.extend([
                "카피의 톤앤매너를 타겟 세대에 맞게 더 조정해보세요",
                "지역 특성을 더 창의적으로 표현해보세요"
            ])
            
        # 평가 이유 기반 제안
        low_score_aspects = []
        for reason in evaluation_reasons:
            if "타겟" in reason.lower() and "부족" in reason:
                low_score_aspects.append("타겟 적합성")
            if "창의" in reason.lower() and "부족" in reason:
                low_score_aspects.append("창의성")
            if "지역" in reason.lower() and "부족" in reason:
                low_score_aspects.append("지역 특성")
            if "전달" in reason.lower() and "부족" in reason:
                low_score_aspects.append("메시지 전달력")
        
        if low_score_aspects:
            if "타겟 적합성" in low_score_aspects:
                suggestions.append(f"선택한 세대({latest['settings']['generation']})의 관심사와 언어 스타일을 더 반영해보세요")
            if "창의성" in low_score_aspects:
                suggestions.append("진부한 표현을 피하고 더 신선한 비유나 표현을 시도해보세요")
            if "지역 특성" in low_score_aspects:
                suggestions.append(f"{latest['settings']['region']}만의 독특한 매력을 더 부각해보세요")
            if "메시지 전달력" in low_score_aspects:
                suggestions.append("핵심 메시지를 더 간결하고 임팩트 있게 전달해보세요")
        
        # 개선도 기반 제안
        if improvement < 0:
            suggestions.append("이전 프롬프트에서 잘 작동했던 요소들을 다시 활용해보세요")
        
        # 중복 제거
        suggestions = list(set(suggestions))
        
        return {
            "current_score": current_avg,
            "improvement": improvement,
            "top_model": top_model,
            "suggestions": suggestions[:3]  # 가장 중요한 3개만 표시
        }
        
    except Exception as e:
        return {
            "current_score": 0,
            "improvement": 0,
            "top_model": "분석 실패",
            "suggestions": ["분석 중 오류가 발생했습니다."]
        }

def visualize_evaluation_results(results: Dict):
    """결과 시각화 함수"""
    if not results or 'detailed_scores' not in results:
        return None
        
    # 현재 설정된 평가 기준 개수만큼만 사용
    scores = results['detailed_scores'][:len(st.session_state.scoring_config.criteria)]
    criteria = st.session_state.scoring_config.criteria[:len(scores)]
    
    # 최소 3개 이상의 축이 필요하도록 보정
    if len(criteria) < 3:
        criteria.extend(['추가 기준'] * (3 - len(criteria)))
        scores.extend([0] * (3 - len(scores)))
    
    fig = go.Figure(data=go.Scatterpolar(
        r=scores,
        theta=criteria,
        fill='toself',
        name='평가 점수'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=False,
        title="평가 기준별 점수"
    )
    return fig


def create_map_with_ad_copies(copies: dict):
    """광고 카피가 포함된 지도 생성"""
    # 한국 중심 좌표
    center_lat, center_lon = 36.5, 128.0
    
    # 지도 생성 - 모던한 스타일 적용
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=7,
        tiles=None,  # 기본 타일 제거
        control_scale=True  # 스케일 컨트롤 추가
    )
    
    # 모던한 다크 스타일 타일 추가
    folium.TileLayer(
        tiles='https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        name='Dark Mode',
        control=False,
    ).add_to(m)

    # 밝은 스타일 타일도 추가하고 레이어 컨트롤로 전환 가능하게 설정
    folium.TileLayer(
        tiles='https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        name='Light Mode',
        control=True
    ).add_to(m)

    # 레이어 컨트롤 추가
    folium.LayerControl().add_to(m)
    
    for region, copy in copies.items():
        if region in CITY_COORDINATES:
            coords = CITY_COORDINATES[region]
            
            # 말풍선 HTML 스타일 업데이트
            popup_html = f"""
            <div style="
                position: relative;
                width: 300px;
                padding: 18px;
                font-family: 'Pretendard', sans-serif;
                line-height: 1.6;
                background-color: rgba(23, 23, 23, 0.95);
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                border-radius: 16px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
                border: 1px solid rgba(255,255,255,0.1);
            ">
                <div style="
                    display: inline-block;
                    background: linear-gradient(135deg, rgba(26,115,232,0.2), rgba(26,115,232,0.1));
                    color: #4a9eff;
                    padding: 6px 14px;
                    border-radius: 20px;
                    font-size: 14px;
                    font-weight: 600;
                    margin-bottom: 12px;
                    border: 1px solid rgba(74,158,255,0.2);
                ">
                    {region}
                </div>
                <p style="
                    margin: 0;
                    font-size: 15px;
                    color: rgba(255,255,255,0.95);
                    line-height: 1.7;
                    font-weight: 500;
                    letter-spacing: -0.2px;
                ">
                    {copy}
                </p>
            </div>
            """
            
            # 위치 마커 스타일 업데이트
            folium.CircleMarker(
                location=[coords["lat"], coords["lon"]],
                radius=7,
                color='#4a9eff',
                fill=True,
                fill_color='#4a9eff',
                fill_opacity=0.9,
                weight=2,
                popup=folium.Popup(popup_html, max_width=320, show=True),
                tooltip=region
            ).add_to(m)

            # 글로우 효과를 위한 큰 원 추가
            folium.CircleMarker(
                location=[coords["lat"], coords["lon"]],
                radius=15,
                color='#4a9eff',
                fill=True,
                fill_color='#4a9eff',
                fill_opacity=0.2,
                weight=0
            ).add_to(m)

    # 지도 영역 자동 조정
    locations = [[coords["lat"], coords["lon"]] for coords in CITY_COORDINATES.values()]
    if locations:
        m.fit_bounds(locations)

    # 지도 스타일 업데이트
    m.get_root().html.add_child(folium.Element("""
        <style>
            .leaflet-popup-content-wrapper {
                background: rgba(23, 23, 23, 0.95) !important;
                backdrop-filter: blur(10px) !important;
                -webkit-backdrop-filter: blur(10px) !important;
                border-radius: 16px !important;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2) !important;
                border: 1px solid rgba(255,255,255,0.1) !important;
                padding: 0 !important;
            }
            .leaflet-popup-content {
                margin: 0 !important;
                padding: 0 !important;
            }
            .leaflet-popup-tip {
                background: rgba(23, 23, 23, 0.95) !important;
                backdrop-filter: blur(10px) !important;
                -webkit-backdrop-filter: blur(10px) !important;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2) !important;
                border: 1px solid rgba(255,255,255,0.1) !important;
            }
            .leaflet-popup-close-button {
                color: #4a9eff !important;
                font-size: 20px !important;
                padding: 8px 8px 0 0 !important;
            }
            .leaflet-popup {
                margin-bottom: 20px !important;
            }
            .leaflet-control-layers {
                border-radius: 12px !important;
                border: 1px solid rgba(255,255,255,0.1) !important;
                background: rgba(23, 23, 23, 0.95) !important;
                backdrop-filter: blur(10px) !important;
                -webkit-backdrop-filter: blur(10px) !important;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2) !important;
            }
            .leaflet-control-layers-list {
                color: white !important;
            }
            .leaflet-bar {
                border-radius: 12px !important;
                overflow: hidden;
            }
            .leaflet-bar a {
                background: rgba(23, 23, 23, 0.95) !important;
                color: #4a9eff !important;
                border: 1px solid rgba(255,255,255,0.1) !important;
            }
            .leaflet-control-zoom {
                border: none !important;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2) !important;
            }
        </style>
    """))
    
    return m




# Load documents
DOCS = load_docs()

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []
if 'show_tutorial' not in st.session_state:
    st.session_state.show_tutorial = True

# Initialize scoring config
DEFAULT_SCORING_CONFIG = ScoringConfig(
    prompt="""
주어진 광고 카피를 다음 기준으로 평가해주세요.
각 기준별로 0-100점 사이의 점수를 부여하고, 
최종 점수는 각 기준의 평균으로 계산합니다.
    """,
    criteria=[
        "타겟 세대 적합성",
        "메시지 전달력",
        "창의성",
        "지역 특성 반영도"
    ]
)



if 'scoring_config' not in st.session_state:
    st.session_state.scoring_config = DEFAULT_SCORING_CONFIG
if 'evaluator' not in st.session_state:
    st.session_state.evaluator = AdCopyEvaluator(st.session_state.scoring_config)



# Tutorial
if st.session_state.show_tutorial:
    with st.sidebar:
        st.info("""
        👋 처음 오셨나요?
        
        1️⃣ 지역과 세대를 선택하세요
        2️⃣ 계절과 MBTI를 선택할 수 있습니다 (선택사항)
        3️⃣ 생성된 프롬프트를 검토/수정하세요
        4️⃣ 광고 카피를 생성하고 결과를 분석하세요
        
        🎯 프롬프트를 개선하며 더 좋은 결과를 만들어보세요!
        """)
        if st.button("알겠습니다!", use_container_width=True):
            st.session_state.show_tutorial = False

# Sidebar
with st.sidebar:
    # 평가 시스템 설정 부분 추가
    st.header("⚙️ 평가 시스템 설정")
    
    with st.expander("평가 프롬프트 설정", expanded=False):
        new_prompt = st.text_area(
            "평가 프롬프트",
            value=st.session_state.scoring_config.prompt
        )
        new_criteria = st.text_area(
            "평가 기준 (줄바꿈으로 구분)",
            value="\n".join(st.session_state.scoring_config.criteria)
        )
        
        if st.button("평가 설정 업데이트"):
            new_config = ScoringConfig(
                prompt=new_prompt,
                criteria=[c.strip() for c in new_criteria.split('\n') if c.strip()]
            )
            st.session_state.scoring_config = new_config
            st.session_state.evaluator = AdCopyEvaluator(new_config)
            st.success("평가 설정이 업데이트되었습니다!")

    st.title("🎯 타겟 설정")
    
    selected_region = st.selectbox(
        "지역 선택",
        options=[""] + list(DOCS["region"].keys()),
        format_func=lambda x: "지역을 선택하세요" if x == "" else x
    )
    
    selected_generation = st.selectbox(
        "세대 선택",
        options=[""] + list(DOCS["generation"].keys()),
        format_func=lambda x: "세대를 선택하세요" if x == "" else x
    )

    # 계절 선택 추가
    selected_season = st.selectbox(
        "계절 선택 (선택사항)",
        options=[""] + list(SEASONS.keys()),
        format_func=lambda x: "계절을 선택하세요" if x == "" else x
    )
    
    include_mbti = st.checkbox("MBTI 특성 포함하기")
    selected_mbti = None
    if include_mbti:
        selected_mbti = st.selectbox(
            "MBTI 선택",
            options=MBTI_TYPES,
            help="선택한 MBTI 성향에 맞는 카피가 생성됩니다"
        )
# Main content
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("💡 프롬프트 작성")
    
    # 프롬프트 에디터 영역
    st.markdown("""
    <div class="prompt-tip">
        💡 프롬프트를 수정하여 더 나은 결과를 만들어보세요.
        문서 내용은 접어두고 필요할 때 펼쳐볼 수 있습니다!
    </div>
    """, unsafe_allow_html=True)
    
    # 기본 프롬프트 구조
    base_structure = """당신은 숙련된 카피라이터입니다. 
아래 제공되는 정보를 참고하여, 매력적인 광고 카피를 생성해주세요.
타겟 고객을 매혹하는 마케팅을 하기 위해 고객이 속한 세대와 MBTI의 특성을 제공하니 잘 참고해주세요.  
이 정보는 참고용이며, 카피는 자연스럽고 창의적이어야 합니다."""

    st.markdown("#### 기본 설정")
    st.markdown(base_structure)

    # 문서 내용을 expander로 표시
    with st.expander("📄 참고 문서 내용 보기/수정", expanded=False):
        docs_content = f"""
### 지역 정보
{DOCS["region"].get(selected_region, "지역 정보가 없습니다.")}

### 세대 특성
{DOCS["generation"].get(selected_generation, "세대 정보가 없습니다.")}
"""
        if include_mbti and selected_mbti:
            docs_content += f"""
### MBTI 특성
{DOCS["mbti"].get(selected_mbti, f"{selected_mbti} 정보를 찾을 수 없습니다.")}
"""
        if selected_season:
            docs_content += f"""
### 계절 특성
{selected_season}의 특징을 반영합니다."""

        edited_docs = st.text_area(
            "문서 내용 수정",
            value=docs_content,
            height=300,
            key="docs_editor"
        )
    
    st.markdown("#### 요구사항")
    requirements = """
1. 위 정보는 영감을 얻기 위한 참고 자료입니다.
2. 도시의 핵심 매력을 포착해 신선한 관점으로 표현해주세요.
3. 타겟층에 맞는 톤앤매너를 사용하되, 정보의 나열은 피해주세요.
4. 감성적 공감과 구체적 특징이 조화를 이루도록 해주세요.
5. 한 문장으로 작성하고, 이모지 1-2개를 포함해주세요.
"""
    st.markdown(requirements)

    # 최종 프롬프트 미리보기 및 수정
    st.markdown("#### 📝 최종 프롬프트")
    edited_prompt = st.text_area(
        "프롬프트 직접 수정",
        value=base_structure + "\n\n" + edited_docs + "\n\n요구사항:\n" + requirements,
        height=200,
        key="final_prompt"
    )

    # 생성 버튼을 눌렀을 때의 로직 수정
    if st.button("🎨 광고 카피 생성", use_container_width=True):
        if not selected_region or not selected_generation:
            st.error("지역과 세대를 선택해주세요!")
        else:
            with st.spinner("AI 모델이 광고 카피를 생성중입니다..."):
                results = {}
                evaluations = {}
                
                for model in ["gpt", "gemini", "claude"]:
                    result = generate_copy(edited_prompt, model)
                    
                    # result가 문자열인지 먼저 확인하고 문자열일 경우 오류 메시지로 처리
                    if isinstance(result, dict) and result.get("success"):
                        # result가 dict일 경우 정상 처리
                        results[model] = result["content"]
                        eval_result = st.session_state.evaluator.evaluate(result["content"], "gpt")  # 평가 시 gpt로 고정
                        evaluations[model] = eval_result
                    elif isinstance(result, str):
                        # gemini/claude가 문자열로 생성한 결과를 gpt로 평가
                        results[model] = result
                        eval_result = st.session_state.evaluator.evaluate(result, "gpt")  # 평가 시 gpt로 고정
                        evaluations[model] = eval_result
                    else:
                        # 알 수 없는 오류 발생 시 기본 값 설정
                        results[model] = "결과 없음"
                        evaluations[model] = {
                            "score": 0,
                            "reason": "평가 실패",
                            "detailed_scores": [0] * len(st.session_state.scoring_config.criteria)
                        }
                
                experiment_data = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "prompt": edited_prompt,
                    "results": results,
                    "evaluations": evaluations,
                    "settings": {
                        "region": selected_region,
                        "generation": selected_generation,
                        "season": selected_season if selected_season else None,
                        "mbti": selected_mbti if include_mbti else None
                    }
                }
                st.session_state.history.append(experiment_data)


                
# with col2 부분의 성능 분석 표시 코드를 아래와 같이 수정
with col2:
    st.subheader("실험 결과")
    
    if st.session_state.history:
        latest_experiment = st.session_state.history[-1]
        
        # 성능 분석
        analysis = analyze_prompt_performance(st.session_state.history)
        if analysis:
            try:
                # HTML 태그가 노출되지 않도록 컨테이너와 마크다운 사용
                with st.container():
                    st.markdown("### 📈 성능 분석")
                    st.write(f"현재 평균 점수: {analysis['current_score']:.1f}")
                    st.write(f"이전 대비: {analysis['improvement']:+.1f}")
                    st.write(f"최고 성능 모델: {analysis['top_model'].upper()}")
                    
                    # 개선 포인트를 마크다운으로 표시
                    if analysis['suggestions']:
                        st.markdown("#### 💡 개선 포인트:")
                        for suggestion in analysis['suggestions']:
                            st.markdown(f"- {suggestion}")
                    
            except Exception as e:
                st.error(f"성능 분석 표시 중 오류 발생: {str(e)}")
        
        # 결과 카드 표시
        model_list = ["gpt", "gemini", "claude"]
        for idx, model_name in enumerate(model_list):
            try:
                with st.container():
                    # 'latest_experiment['results']'가 딕셔너리인지 확인 후 처리
                    if isinstance(latest_experiment.get('results'), dict):
                        result = latest_experiment['results'].get(model_name, "결과 없음")
                    else:
                        result = "결과 없음"
                    
                    # 'latest_experiment['evaluations']'가 딕셔너리인지 확인 후 처리
                    eval_data = (latest_experiment.get('evaluations', {}).get(model_name) 
                                 if isinstance(latest_experiment.get('evaluations'), dict) 
                                 else {
                                     "score": 0,
                                     "reason": "평가 실패",
                                     "detailed_scores": [0] * len(st.session_state.scoring_config.criteria)
                                 })
        
                    st.markdown(f"""
                    <div class="result-card">
                        <span class="model-tag" style="background-color: {MODEL_COLORS[model_name]}">
                            {model_name.upper()}
                        </span>
                        <div style="margin: 1rem 0;">
                            {result}
                        </div>
                        <div class="score-badge">
                            점수: {eval_data.get('score', 0)}점
                        </div>
                        <div class="prompt-feedback">
                            {eval_data.get('reason', '평가 이유 없음')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if 'detailed_scores' in eval_data:
                        try:
                            fig = visualize_evaluation_results(eval_data)
                            st.plotly_chart(fig, use_container_width=True)
                        except Exception as e:
                            st.error(f"차트 생성 중 오류 발생: {str(e)}")
            except Exception as e:
                st.error(f"결과 표시 중 오류 발생 ({model_name}): {str(e)}")

    else:
        st.info("광고 카피를 생성하면 여기에 결과가 표시됩니다.")

# 지도 섹션 추가
st.markdown("---")  # 구분선

# 컨테이너를 사용하여 여백 제거
with st.container():
    st.markdown("""
        <h3 style="
            color: #1a73e8;
            font-weight: 600;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        ">
            🗺️ 지역별 광고 카피 대시보드
            <span style="
                font-size: 0.8em;
                color: rgba(255,255,255,0.6);
                font-weight: 400;
            ">
                Regional Ad-Copy Dashboard
            </span>
        </h3>
    """, unsafe_allow_html=True)
    # 컨트롤 패널을 좁은 컬럼에 배치
    col_control, col_map = st.columns([0.25, 0.75])
    
    with col_control:
        selected_regions = st.multiselect(
            "지역 선택",
            options=list(CITY_COORDINATES.keys()),
            default=["부산 해운대"],
            help="여러 지역을 선택하여 한 번에 광고 카피를 생성할 수 있습니다."
        )
        
        selected_generation = st.selectbox(
            "타겟 세대 선택",
            list(DOCS["generation"].keys()),
            key="map_generation"
        )

        include_mbti = st.checkbox("MBTI 특성 포함", key="map_mbti_check")
        if include_mbti:
            selected_mbti = st.selectbox(
                "MBTI 선택",
                options=MBTI_TYPES,
                key="map_mbti"
            )
        else:
            selected_mbti = None

        selected_season = st.selectbox(
            "계절 선택 (선택사항)",
            options=[""] + list(SEASONS.keys()),
            format_func=lambda x: "계절을 선택하세요" if x == "" else x,
            key="map_season"
        )

        # 생성 버튼을 눌렀을 때
        if st.button("🎨 16명의 멀티 페르소나 여행지 홍보 카피라이팅 생성", use_container_width=True):
            if not selected_regions or not selected_generation:
                st.error("지역과 세대를 선택해주세요!")
            else:
                with st.spinner("AI 모델이 다양한 관점의 여행지 홍보 카피라이팅을 생성중입니다..."):
                    try:
                        # 랜덤하게 10명의 페르소나 선택
                        selected_region = selected_regions[0]
                        selected_personas = get_balanced_random_personas(16)  # 여기를 변경
                        # 진행 상황 표시
                        progress_text = st.empty()
                        progress_bar = st.progress(0)
                        
                        persona_results = {}
                        for idx, persona_name in enumerate(selected_personas):
                            progress_text.text(f"✍️ {persona_name}의 시선으로 카피 생성 중...")
                            
                            # city_doc 확인
                            city_doc = DOCS["region"].get(selected_region)
                            if not city_doc:
                                st.error(f"선택한 지역({selected_region})의 정보를 찾을 수 없습니다.")
                                continue
                            
                            prompt = create_adaptive_prompt(
                                city_doc=city_doc,
                                target_generation=selected_generation,
                                persona_name=persona_name,
                                mbti=selected_mbti if include_mbti else None,
                                include_mbti=include_mbti
                            )
                            
                            if prompt:
                                result = generate_copy(prompt, "gpt")
                                persona_results[persona_name] = {
                                    "copy": result["content"] if isinstance(result, dict) else result,
                                    "persona_info": PERSONAS[persona_name],
                                    "category": PERSONAS[persona_name]["category"]
                                }
                            
                            progress_bar.progress((idx + 1) / len(selected_personas))
                        
                        # 진행 표시 제거
                        progress_text.empty()
                        progress_bar.empty()
        
                        if persona_results:  # 결과가 있는 경우에만 지도와 결과 표시
                
                            # 지도와 결과를 함께 표시할 컨테이너
                            st.markdown(f"### 🗺️ 다양한 시선으로 바라본 {selected_region}")
                            
                            # 2개의 컬럼으로 나누기
                            map_col, results_col = st.columns([0.6, 0.4])
                            
                            with map_col:
                                # 지도 생성 및 표시
                                copies_for_map = {selected_region: {
                                    "copies": persona_results,
                                    "coordinates": CITY_COORDINATES[selected_region]
                                }}
                                
                                m = folium.Map(
                                    location=[CITY_COORDINATES[selected_region]["lat"], 
                                             CITY_COORDINATES[selected_region]["lon"]],
                                    zoom_start=13,
                                    tiles='CartoDB dark_matter'
                                )
                                
                                # 위치 마커와 팝업 추가
                                for persona_name, result in persona_results.items():
                                    category_color = PERSONA_CATEGORIES[result["category"]]["color"]
                                    
                                    popup_html = f"""
                                    <div style="
                                        width: 300px;
                                        padding: 15px;
                                        font-family: 'Pretendard', sans-serif;
                                        background-color: rgba(255, 255, 255, 0.95);
                                        border-radius: 8px;
                                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                                    ">
                                        <div style="
                                            display: inline-block;
                                            padding: 4px 12px;
                                            background-color: {category_color};
                                            border-radius: 15px;
                                            font-size: 12px;
                                            font-weight: 600;
                                            margin-bottom: 8px;
                                            color: {PERSONA_CATEGORIES[result["category"]]["text_color"]};  /* 페르소나 이름 색상만 변경 */
                                        ">
                                            {persona_name}
                                        </div>
                                        <p style="
                                            margin: 8px 0;
                                            font-size: 14px;
                                            line-height: 1.6;
                                            color: #333;  /* 카피 내용은 원래 색상 유지 */
                                        ">
                                            {result['copy']}
                                        </p>
                                    </div>
                                    """
                                    
                                    # 각 페르소나별로 약간 다른 위치에 마커 생성
                                    offset = 0.0005 * (list(persona_results.keys()).index(persona_name) + 1)
                                    
                                    folium.CircleMarker(
                                        location=[
                                            CITY_COORDINATES[selected_region]["lat"] + offset,
                                            CITY_COORDINATES[selected_region]["lon"] + offset
                                        ],
                                        radius=8,
                                        color=category_color,
                                        fill=True,
                                        popup=folium.Popup(popup_html, max_width=320),
                                        tooltip=persona_name
                                    ).add_to(m)
                                
                                folium_static(m)
                            
                            with results_col:
                                # 결과를 4x4 매트릭스로 나누기
                                rows = [persona_results.items()]
                                chunks = list(persona_results.items())
                                
                                # 4x4 그리드로 나누기
                                for i in range(0, len(chunks), 4):
                                    row = st.columns(4)  # 4개의 컬럼 생성
                                    for j in range(4):
                                        if i + j < len(chunks):
                                            persona_name, result = chunks[i + j]
                                            category_color = PERSONA_CATEGORIES[result["category"]]["color"]
                                            
                                            with row[j]:
                                                st.markdown(f"""
                                                <div style="
                                                    background: linear-gradient(135deg, {category_color}40, {category_color}20);
                                                    padding: 15px;
                                                    border-radius: 12px;
                                                    border: 1px solid {category_color};
                                                    height: fit-content;
                                                    transition: transform 0.2s;
                                                    cursor: pointer;
                                                    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
                                                    margin-bottom: 15px;
                                                ">
                                                    <div style="
                                                        display: inline-block;
                                                        padding: 6px 14px;
                                                        background-color: {category_color};
                                                        border-radius: 20px;
                                                        font-size: 14px;
                                                        font-weight: 600;
                                                        margin-bottom: 10px;
                                                        color: {PERSONA_CATEGORIES[result["category"]]["text_color"]};
                                                        white-space: nowrap;
                                                        overflow: hidden;
                                                        text-overflow: ellipsis;
                                                    ">
                                                        {persona_name}
                                                    </div>
                                                    <p style="
                                                        font-size: 15px;
                                                        line-height: 1.6;
                                                        color: rgba(255, 255, 255, 0.95);
                                                        margin: 0;
                                                        overflow-wrap: break-word;
                                                        min-height: 100px;
                                                    ">
                                                        {result['copy']}
                                                    </p>
                                                </div>
                                                """, unsafe_allow_html=True)
                            
                            # 결과 저장 버튼
                            if st.button("💾 결과 저장"):
                                df = pd.DataFrame([
                                    {
                                        "페르소나": name,
                                        "카테고리": data["category"],
                                        "광고카피": data["copy"]
                                    }
                                    for name, data in persona_results.items()
                                ])
                                
                                csv = df.to_csv(index=False).encode('utf-8-sig')
                                st.download_button(
                                    label="📥 CSV 파일 다운로드",
                                    data=csv,
                                    file_name=f'{selected_region}_광고카피_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                                    mime='text/csv'
                                )
        
                    except Exception as e:
                        st.error(f"광고 카피 생성 중 오류가 발생했습니다: {str(e)}")
