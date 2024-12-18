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
import re 
from metadata import SEASONS, PERSONA_CATEGORIES, CITY_COORDINATES, MBTI_GROUPS, MBTI_TYPES, MODEL_COLORS, LOGO_BASE64, name_list
from persona import PERSONAS


# Page config must be the first Streamlit command
st.set_page_config(
    page_title="Copybara - 여행지 홍보 카피라이팅 문구 생성 AI", 
    page_icon="🐾", 
    layout="wide"
)

# 앱 제목
st.title("🐾 Copybara - 여행지 홍보 카피라이팅 문구 생성 AI")


#image = Image.open("copybara_logo2.png")
image = Image.open("copybara_santa_logo.png")

new_width = 640  # 원하는 너비로 조정
width_percent = (new_width / float(image.size[0]))
new_height = int((float(image.size[1]) * float(width_percent)))
resized_image = image.resize((new_width, new_height), Image.LANCZOS)
st.image(resized_image)



# Initialize API keys from Streamlit secrets
genai.configure(api_key=st.secrets["gemini"])
anthropic = Anthropic(api_key=st.secrets["claude"])
client = OpenAI(api_key=st.secrets["chatgpt"])  # API 키 입력



#챗-제-클 순서 오와열
model_zoo = ['gpt-4o',
             'gemini-1.5-pro-002',
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
        transition: all 0.3s ease;
    }
    
    .result-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
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
        background-color: #000; /* 카드 배경을 검정색으로 변경 */
        color: #fff; /* 텍스트를 흰색으로 변경 */
        border-radius: 20px; /* 모서리를 둥글게 */
        padding: 2rem; /* 패딩 조정 */
        text-align: center; /* 텍스트 가운데 정렬 */
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2); /* 그림자 효과 */
    }
    
    .result-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(0, 0, 0, 0.3); /* 호버 시 더 강한 그림자 */
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
    
    .copy-text {
        font-size: 1.8rem; /* 카피 텍스트 크기 */
        font-weight: 700; /* 카피 텍스트 굵기 */
        line-height: 1.6; /* 줄 간격 조정 */
        margin-bottom: 1rem; /* 아래 여백 */
    }
    
    .description-text {
        font-size: 1.2rem; /* 설명 텍스트 크기 */
        font-weight: 400; /* 설명 텍스트 굵기 */
        line-height: 1.8; /* 줄 간격 */
        color: #bbb; /* 설명 텍스트는 밝은 회색 */
        margin-top: 1rem; /* 위 여백 */
    }
    
    .score-badge {
        margin-top: 2rem; /* 점수 배지 위 여백 */
        font-size: 1.5rem; /* 점수 배지 폰트 크기 */
        font-weight: bold; /* 점수 강조 */
        background-color: #333; /* 점수 배지 배경색 */
        color: #fff; /* 점수 배지 텍스트 색 */
        padding: 0.5rem 1rem; /* 배지 패딩 */
        border-radius: 9999px; /* Pill 형태 */
        display: inline-block; /* 인라인 블록 배치 */
    }
    
    .feedback {
        margin-top: 2rem; /* 피드백 위 여백 */
        font-size: 1rem; /* 피드백 텍스트 크기 */
        line-height: 1.5; /* 피드백 줄 간격 */
        color: #bbb; /* 피드백 텍스트 색상 */
        font-style: italic; /* 기울임 효과 */
    }
</style>
""", unsafe_allow_html=True)


# CSS에 추가
st.markdown("""
<style>
    /* 기존 CSS */
    
    /* 페르소나 변형 카드 스타일 */
    .persona-variation-card {
        background-color: rgba(30, 30, 30, 0.6);
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        backdrop-filter: blur(5px);
        transition: all 0.3s ease;
    }
    
    .persona-variation-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
    }
    
    .persona-name {
        font-size: 1.1em;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 8px;
    }
    
    .persona-copy {
        font-size: 1.4em;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 15px;
        line-height: 1.5;
    }
    
    .persona-explanation {
        color: rgba(255, 255, 255, 0.8);
        font-size: 1.1em;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)


#오디오 파트 (1213~)

# TTS 생성 함수 수정
def generate_tts(copy_text, file_name):
    try:
        # 4개의 음성 엔트리 중 랜덤 선택
        voice_options = ["alloy", "echo", "fable", "onyx"]
        selected_voice = random.choice(voice_options)
        st.info(f"🎤 선택된 목소리: {selected_voice}")

        # OpenAI TTS 요청
        response = client.audio.speech.create(
            model="tts-1",
            voice=selected_voice,  # 랜덤으로 선택된 목소리
            input=copy_text
        )
        audio_file_path = f"{file_name}.mp3"
        with open(audio_file_path, "wb") as audio_file:
            for chunk in response.iter_bytes():
                audio_file.write(chunk)
        return audio_file_path
    except Exception as e:
        st.error(f"TTS 생성 중 오류 발생: {str(e)}")
        return None

# 오디오 파일 재생 함수
def play_audio(file_path):
    audio_file = open(file_path, "rb")
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format="audio/mp3", start_time=0)




def name_to_persona(name):
    """
    Generate a persona prompt for a given name by analyzing the representative works and characteristics of the person.
    
    Args:
        name (str): The name of the famous person (e.g., "아이유").
        
    Returns:
        str: A persona prompt containing representative text and characteristics of the person.
    """
    prompt = f"""
    당신은 한국의 유명 인물의 스타일과 작품을 분석하고 광고 카피 변형에 적합한 정보를 생성하는 AI입니다.
    아래 단계를 수행하세요:

    1. 주어진 인물의 대표적인 작품을 1개에서 최대 4개까지 선택하세요.
       - 선택한 작품의 제목을 제시하고, 해당 작품이 왜 중요한지 간략히 설명하세요.
    2. 각 작품에서 대표적인 구절이나 발언을 제시하세요.
    3. 작품의 주제, 감정, 언어적 특징을 분석하세요.
    4. 분석을 바탕으로 해당 인물의 스타일을 정의하세요.
       - 언어적 특징, 자주 사용하는 표현, 대표적인 감정적 메시지를 포함하세요.

    ### 입력:
    - 인물: {name}

    ### 결과:
    1. 대표 작품 (1~4개):
       - 작품 1: (설명: )
       - 작품 2: (설명: )
       - 작품 3: (설명: )
       - 작품 4: (설명: )
    2. 대표 구절/가사:
       - 
    3. 작품 분석:
       - 주제: 
       - 감정: 
       - 언어적 특징: 
    4. 스타일 정의:
       - 
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 창의적이고 분석적인 글쓰기를 잘하는 AI입니다."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=700,
            temperature=0.65,
        )

        # Extract the generated persona prompt
        content = response.choices[0].message.content
        return content.strip()
    except Exception as e:
        return f"Error: {e}"

def transform_ad_copy(base_copy, persona_prompt, name):
    """
    Transform an ad copy to reflect the style of a given persona.

    Args:
        base_copy (str): The original ad copy to transform.
        persona_prompt (str): The persona prompt defining the style of the person.
        name (str): The name of the person whose style is applied.

    Returns:
        str: The transformed ad copy.
    """
    prompt = f'''
    ### 작업 맥락:
    아래는 {name}의 스타일과 철학을 설명하는 내용입니다.
    {persona_prompt}

    ### 작업 대상:
    - 원본 카피: "{base_copy}"

    ### 작성 지침:
    1. 변형된 카피(Transformed Copy)는 반드시 {name}의 대표작, 문체, 철학에서 영감을 받아 작성하세요.
    2. 변형된 카피는 짧고 강렬하며, 독자가 {name}을 연상할 수 있는 상징적 요소를 포함해야 합니다.
    3. 설명(Explanation)에는 변형된 카피가 어떻게 {name}의 특징을 반영했는지 구체적으로 작성하세요.
    4. 변형된 카피는 반드시 독자에게 감정적 울림을 주고, 기존 광고 카피의 맥락(계절, 지역)을 유지해야 합니다.
    5. 결과는 아래 형식을 반드시 따르세요:
       Explanation: <설명 텍스트>
       Transformed Copy: <킬러 대사>
   '''
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "당신은 창의적이고 감성적이며 독창적인 글쓰기를 잘하는 AI입니다."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,  # 설명 + 결과 포함
        temperature=0.8,
        top_p=0.9,
    )

    output = response.choices[0].message.content.strip()

    return output



# 모델별 헤더 디자인 (로고 포함)
def get_model_header_html(model_name):
    return f'''
    <div style="text-align: center; padding: 15px; 
         background-color: {MODEL_COLORS.get(model_name, '#6c757d')}; 
         border-radius: 12px; margin-bottom: 20px;
         box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
        <div style="display: flex; align-items: center; justify-content: center; gap: 12px;">
            <img src="{LOGO_BASE64[model_name]}" 
                 style="width: 24px; height: 24px; object-fit: contain; 
                        {'filter: brightness(0) invert(1);' if model_name != 'claude' else ''}">
            <h3 style="margin: 0; color: white; font-size: 1.5em; 
                letter-spacing: 0.05em; font-weight: 600;">
                {model_name.upper()}
            </h3>
        </div>
    </div>
    '''

# 결과 카드 디자인 (초안)
def get_result_card_html(model_name, copy_text, description_text, eval_result):
    return f"""
    <div style="padding: 20px; border-radius: 12px; 
         background-color: rgba(30, 30, 30, 0.6);
         border: 1px solid {MODEL_COLORS.get(model_name, '#6c757d')};
         margin: 15px 0; backdrop-filter: blur(5px);">
        <div style="font-size: 1.4em; font-weight: 600; 
             color: #ffffff; margin-bottom: 15px;
             line-height: 1.5; letter-spacing: -0.02em;">
            {copy_text}
        </div>
        <p style="color: rgba(255, 255, 255, 0.8); font-size: 1.1em; 
              margin-top: 12px; line-height: 1.6;">
            {description_text}
        </p>
        <div style="text-align: center; margin-top: 15px;">
            <span style="background: {MODEL_COLORS.get(model_name, '#6c757d')}; 
                  color: white; padding: 8px 20px; border-radius: 20px;
                  font-size: 1.1em; font-weight: 500;">
                점수: {eval_result['score']}점
            </span>
        </div>
    </div>
    """

# 퇴고 결과 카드 디자인
def get_revision_card_html(model_name, copy_text, description_text, current_eval, improvement):
    return f"""
    <div style="padding: 20px; border-radius: 12px; 
         background-color: rgba(30, 30, 30, 0.6);
         border: 1px solid {MODEL_COLORS.get(model_name, '#6c757d')};
         margin: 15px 0; backdrop-filter: blur(5px);">
        <div style="font-size: 1.4em; font-weight: 600; 
             color: #ffffff; margin-bottom: 15px;
             line-height: 1.5; letter-spacing: -0.02em;">
            {copy_text}
        </div>
        <p style="color: rgba(255, 255, 255, 0.8); font-size: 1.1em; 
              margin-top: 12px; line-height: 1.6;">
            {description_text}
        </p>
        <div style="text-align: center; margin-top: 15px;">
            <span style="background: {MODEL_COLORS.get(model_name, '#6c757d')}; 
                  color: white; padding: 8px 20px; border-radius: 20px;
                  font-size: 1.2em; font-weight: 500;">
                최종 점수: {current_eval['score']}점
                <span style="color: {'#A7F3D0' if improvement > 0 else '#FCA5A5'}">
                    ({improvement:+.1f})
                </span>
            </span>
        </div>
    </div>
    """

if 'selected_personas' not in st.session_state:
    st.session_state.selected_personas = []

def get_balanced_random_personas(n=16) -> List[str]:
    """카테고리별로 균형잡힌 페르소나 선택"""
    # 카테고리별 최소 선택 수 정의
    min_per_category = {
        "literature": 4,
        "entertainment": 4,
        "tech": 3,
        "politics": 3,
        "fiction": 2
    }
    
    personas_by_category = {
        category: [name for name, data in PERSONAS.items() 
                  if data["category"] == category]
        for category in PERSONA_CATEGORIES.keys()
    }
    
    selected_personas = []
    
    # 각 카테고리에서 최소 수만큼 선택
    for category, min_count in min_per_category.items():
        available = personas_by_category[category]
        if available:
            selected = random.sample(available, min(min_count, len(available)))
            selected_personas.extend(selected)
    
    # 남은 수만큼 랜덤 선택
    remaining = n - len(selected_personas)
    if remaining > 0:
        remaining_personas = [p for p in PERSONAS.keys() 
                            if p not in selected_personas]
        additional = random.sample(remaining_personas, 
                                 min(remaining, len(remaining_personas)))
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
    
    try:
        docs_path = pathlib.Path("docs")
        
        # Load region docs
        region_path = docs_path / "regions"
        if region_path.exists():
            for file in sorted(region_path.glob("*.txt")):  # 가나다 순 정렬
                with open(file, "r", encoding="utf-8") as f:
                    docs["region"][file.stem] = f.read()
        
        # Load generation docs
        generation_path = docs_path / "generations"
        if generation_path.exists():
            for file in sorted(generation_path.glob("*.txt")):  # 가나다 순 정렬
                with open(file, "r", encoding="utf-8") as f:
                    docs["generation"][file.stem] = f.read()
        
        # Load individual MBTI files
        mbti_path = docs_path / "mbti"
        if mbti_path.exists():
            for mbti in sorted(MBTI_TYPES):  # MBTI도 가나다 순 정렬
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
        
        # 가나다 순 정렬된 딕셔너리 생성
        docs["region"] = dict(sorted(docs["region"].items()))
        docs["generation"] = dict(sorted(docs["generation"].items()))
        docs["mbti"] = dict(sorted(docs["mbti"].items()))
    
    except Exception as e:
        print(f"문서 로딩 중 오류: {str(e)}")
    
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

def create_revision_prompt(original_copy: str, evaluation_result: dict) -> str:
    """평가 결과를 바탕으로 퇴고 프롬프트 생성"""
    revision_prompt = f"""
당신은 숙련된 광고 카피라이터입니다. 아래 광고 카피를 더 효과적으로 개선해주세요.

[원본 카피]
{original_copy}

[현재 평가 결과]
- 총점: {evaluation_result.get('score', 0)}점
- 평가 이유: {evaluation_result.get('reason', '평가 없음')}
- 세부 점수:
{chr(10).join([f'- {criterion}: {score}점' for criterion, score in zip(st.session_state.scoring_config.criteria, evaluation_result.get('detailed_scores', []))])}

[개선 요구사항]
1. 각 평가 기준의 점수를 분석하여, 가장 낮은 점수를 받은 항목을 중점적으로 개선하세요.
2. 원본 카피의 핵심 메시지와 톤앤매너는 유지하면서, 다음 사항들을 개선하세요:
   - 감정적 공감력: 타겟 독자의 감정을 더 강하게 자극하는 표현 사용
   - 경험의 생생함: 구체적이고 감각적인 표현으로 경험을 더 생생하게 전달
   - 독자와의 조화: 타겟 세대의 언어와 관심사를 더 적극적으로 반영
   - 문화적/지역적 특성: 지역의 특색있는 요소를 더 효과적으로 활용

[제약 사항]
- 반드시 기존 평가 점수보다 높은 품질의 카피를 작성하세요.
- 형식은 반드시 "**카피**: (내용)" 형태를 유지하세요.
- 설명도 반드시 "**설명**: (내용)" 형태를 유지하세요.

개선된 버전을 제시해주세요.
"""
    return revision_prompt

def handle_revision_results(original_result: dict, revision_result: dict) -> dict:
    """퇴고 결과 처리 - 점수가 더 높은 버전을 선택"""
    original_score = original_result.get('score', 0)
    revision_score = revision_result.get('score', 0)
    
    if revision_score > original_score:
        return revision_result, True  # 개선됨
    else:
        return original_result, False  # 원본 유지

def generate_revision(original_copy: str, evaluation_result: dict, model_name: str) -> Dict:
    """평가 결과를 바탕으로 퇴고된 버전 생성"""
    revision_prompt = create_revision_prompt(original_copy, evaluation_result)
    return generate_copy(revision_prompt, model_name)  # 기존 generate_copy 함수 활용



def get_safe_persona_info(data: dict, field: str, default: any = '') -> any:
    """페르소나 데이터에서 안전하게 정보를 추출"""
    try:
        if not isinstance(data, dict):
            return default
        return data.get(field, default)
    except Exception:
        return default



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
            st.error(f"아쉽게 이번엔 점수가 반영되지 못했어요.: {str(e)}")
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


def visualize_evaluation_results(eval_data: Dict, unique_key: str):
    """결과 시각화 함수 - 더 강건한 버전"""
    try:
        if not eval_data or 'detailed_scores' not in eval_data:
            return None
            
        # 현재 설정된 평가 기준과 점수 가져오기
        scores = eval_data.get('detailed_scores', [])
        criteria = st.session_state.scoring_config.criteria
        
        # 둘 중 더 짧은 것을 기준으로 맞추기
        min_length = min(len(scores), len(criteria))
        scores = scores[:min_length]
        criteria = criteria[:min_length]
        
        # 최소 3개 이상의 축이 필요하도록 보정
        while len(criteria) < 3:
            criteria.append(f'기준 {len(criteria)+1}')
            scores.append(0)
            
        try:
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
                title=dict(
                    text="평가 기준별 점수",
                    x=0.5,
                    y=0.95
                )
            )
            return fig
        except Exception as e:
            st.error(f"차트 생성 중 오류 발생: {str(e)}")
            return None
            
    except Exception as e:
        st.error(f"데이터 처리 중 오류 발생: {str(e)}")
        return None

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


def extract_copy_and_description(result_text):
    """카피와 설명을 추출하는 함수"""
    if isinstance(result_text, str):
        if "**카피**:" in result_text and "**설명**:" in result_text:
            match = re.search(r"\*\*카피\*\*:\s*(.*?)\s*\*\*설명\*\*:\s*(.*)", result_text, re.DOTALL)
            if match:
                copy_text = match.group(1).strip()
                description_text = match.group(2).strip()
                return copy_text, description_text
        elif "**카피**:" in result_text:
            match = re.search(r"\*\*카피\*\*:\s*(.*)", result_text, re.DOTALL)
            if match:
                copy_text = match.group(1).strip()
                return copy_text, "설명 없음"
        elif "**설명**:" in result_text:
            match = re.search(r"\*\*설명\*\*:\s*(.*)", result_text, re.DOTALL)
            if match:
                description_text = match.group(1).strip()
                return "카피 없음", description_text
    return "카피 없음", "설명 없음"

# visualize_evaluation_results 함수 수정
def visualize_evaluation_results(eval_data: Dict, unique_key: str):
    """결과 시각화 함수"""
    try:
        if not eval_data or 'detailed_scores' not in eval_data:
            return None
            
        # 점수와 기준 가져오기
        scores = eval_data.get('detailed_scores', [])
        criteria = st.session_state.scoring_config.criteria

        # 유효성 검사
        if not scores or not criteria:
            return None

        # 길이 맞추기
        min_length = min(len(scores), len(criteria))
        scores = scores[:min_length]
        criteria = criteria[:min_length]
        
        # 최소 3개 축 보장
        while len(criteria) < 3:
            criteria.append(f'기준 {len(criteria)+1}')
            scores.append(0)

        # 데이터 확인용 로그
        print(f"Model Criteria: {criteria}")
        print(f"Model Scores: {scores}")
            
        try:
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
                title=dict(
                    text="평가 기준별 점수",
                    x=0.5,
                    y=0.95
                ),
                height=400  # 높이 고정
            )
            return fig
        except Exception as e:
            print(f"Chart creation error: {str(e)}")  # 디버깅용
            return None
            
    except Exception as e:
        print(f"Data processing error: {str(e)}")  # 디버깅용
        return None

def display_model_result(model_name: str, result: dict, eval_data: dict, idx: int):
    """각 모델의 결과를 표시하는 함수"""
    try:
        copy_text, description_text = extract_copy_and_description(result)
        feedback_text = eval_data.get('reason', "평가 이유 없음")

        # 1차 결과 표시 부분
        st.markdown(f"""
        <div style="padding: 15px; border-radius: 10px; 
             border: 1px solid {MODEL_COLORS.get(model_name, '#6c757d')}22;
             margin: 10px 0;">
            <div style="font-size: 1.2em; font-weight: 600; 
                 color: #1a1a1a; margin-bottom: 12px; 
                 line-height: 1.4; letter-spacing: -0.02em;">
                {copy_text}
            </div>
            <p style="color: #666; font-size: 0.95em; 
                  margin-top: 8px; line-height: 1.5;">
                {description_text}
            </p>
            <div style="text-align: center; margin-top: 12px;">
                <span style="background: {MODEL_COLORS.get(model_name, '#6c757d')}22; 
                      padding: 5px 15px; border-radius: 15px;">
                    점수: {eval_result['score']}점
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if 'detailed_scores' in eval_data:
            fig = visualize_evaluation_results(eval_data, f"model-{model_name}-{idx}")
            if fig is not None:
                st.plotly_chart(fig, use_container_width=True, key=f"chart-{model_name}-{idx}")
                
    except Exception as e:
        st.error(f"{model_name.upper()} 모델 결과 표시 중 오류 발생: {str(e)}")




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

# 카드 HTML 생성 함수 추가
def get_persona_variation_card_html(model_name, persona_name, transformed_copy, explanation, score, improvement):
    score_color = '#A7F3D0' if improvement > 0 else '#FCA5A5'
    return f"""
    <div class="persona-card" style="padding: 20px; border-radius: 12px; 
         background-color: rgba(30, 30, 30, 0.6);
         border: 1px solid {MODEL_COLORS.get(model_name, '#6c757d')};
         margin: 15px 0; backdrop-filter: blur(5px)">
        <div class="persona-name" style="font-size: 1.1em; font-weight: 600; margin-bottom: 8px">
            🎭 {persona_name}의 버전
        </div>
        <div class="copy" style="font-size: 1.4em; font-weight: 600; 
             color: #ffffff; margin-bottom: 15px;
             line-height: 1.5">
            {transformed_copy}
        </div>
        <div class="explanation" style="color: rgba(255, 255, 255, 0.8); 
             font-size: 1.1em; line-height: 1.6">
            {explanation}
        </div>
        <div class="score" style="text-align: center; margin-top: 15px">
            <div style="display: inline-block; background: {MODEL_COLORS.get(model_name, '#6c757d')}; 
                  color: white; padding: 8px 20px; border-radius: 20px;
                  font-size: 1.2em; font-weight: 500">
                점수: {score:.1f}점
                <span style="color: {score_color}">({improvement:+.1f})</span>
            </div>
        </div>
    </div>"""


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

💡 **평가 기준**
1. 감정적 공감력: 카피가 감정적으로 독자에게 와닿고, 직관적으로 반응을 이끌어낼 수 있는지 평가하세요.
2. 경험의 생생함: 단순한 정보가 아니라, 카피가 독자가 상상할 수 있는 경험을 얼마나 생생하게 전달하는지 평가하세요.
3. 독자와의 조화: 카피가 독자에게 개인적으로 필요한 이야기로 다가가며, 어떤 긍정적인 변화를 제안하는지 평가하세요.
4. 문화적/지역적 특성 반영: 카피가 해당 지역의 독특한 매력을 얼마나 효과적으로 반영하고 있는지 평가하세요.
    """,
    criteria=[
        "Emotional Resonance (감정적 공감력)",
        "Experiential Vividness (경험의 생생함)",
        "Audience Alignment (독자와의 조화)",
        "Cultural Authenticity (문화적/지역적 특성 반영)"
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
        options=[""] + sorted(DOCS["region"].keys()),  # 가나다 순 정렬
        format_func=lambda x: "지역을 선택하세요" if x == "" else x
    )
    
    selected_generation = st.selectbox(
        "세대 선택",
        options=[""] + sorted(DOCS["generation"].keys()),  # 가나다 순 정렬
        format_func=lambda x: "세대를 선택하세요" if x == "" else x
    )
    
    # 계절 선택 추가
    selected_season = st.selectbox(
        "계절 선택 (선택사항)",
        options=[""] + sorted(SEASONS.keys()),  # 가나다 순 정렬
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
with st.container():
    st.subheader("💡 감성 여행 카피 생성을 위한 프롬프트 엔지니어링")

    # 프롬프트 에디터 영역
    with st.expander("📌 프롬프트 작성 가이드 보기", expanded=False):
        st.markdown("""
        💡 사색적이고 감성적인 카피를 작성해 특정 여행지나 경험에 대한 관심을 이끌어내세요.
        문서 내용은 접어두고 필요할 때 펼쳐볼 수 있습니다!
        """, unsafe_allow_html=True)

    # 기본 프롬프트 구조 (접기 가능)
    with st.expander("📝 Prompt Blueprint: 감성 카피 생성 핵심 프롬프트", expanded=False):
        base_structure = """당신은 맞춤형 감성 카피를 창작하는 숙련된 카피라이터입니다. 
아래 제공된 정보를 바탕으로 특정 여행지의 매력과 경험을 감성적으로 표현하세요.

💡 **목표**
1. 독자의 세대와 MBTI 특성에 맞는 메시지를 작성하여 공감대를 형성하고 관심을 유도합니다.
2. 여행지가 제공하는 구체적인 경험과 독자가 느낄 수 있는 변화를 철학적이고 감성적으로 묘사합니다.
3. 한 문장의 카피와 짧은 설명을 함께 작성하세요. 반드시 아래 외에 아무것도 출력하지 마세요.
   - **카피**: 여행지나 경험의 정서를 함축한 한 줄 메시지.
   - **설명**: 카피의 맥락을 보완하는 짧고 감성적인 해설로 독자가 느낄 변화를 상상하게 만드세요."""
        st.markdown(base_structure)

    # 외부 데이터와 연결된 참고 문서 (접기 가능)
    with st.expander("📄 Context Data Hub: 여행지 메타데이터 라이브러리", expanded=False):
        edited_docs = f"""
### 지역 정보
{DOCS["region"].get(selected_region, "지역 정보가 없습니다.")}

### 세대 특성
{DOCS["generation"].get(selected_generation, "세대 정보가 없습니다.")}

### MBTI 특성
{DOCS["mbti"].get(selected_mbti, f"{selected_mbti} 정보를 찾을 수 없습니다.")}

### 계절 특성
{selected_season}의 특징을 반영합니다.
"""
        edited_docs = st.text_area(
            "문서 내용 수정",
            value=edited_docs,
            height=300,
            key="docs_editor"
        )

    # 요구사항 (접기 가능)
    with st.expander("⚙️ Task Constraints: 감성 카피 최적화 요구사항", expanded=False):
        requirements = """
1. 세대와 MBTI 특성을 반영해 독자의 성향에 맞는 메시지를 작성하세요.
2. 여행지가 독자에게 가져올 긍정적 변화와 감정적 연결을 강조하세요.
3. 카피와 설명은 서로를 보완하며, 독립적으로도 매력적이어야 합니다.
4. 짧고 강렬한 메시지와 감성적인 해설을 작성하세요.
5. 기존 예시의 톤과 스타일을 유지하며, 추가 데이터에 따라 맞춤형 메시지를 제안하세요.
"""
        st.markdown(requirements)

    # 참고 예시 (접기 가능)
    with st.expander("✨ Few-Shot Prompting: 감성 카피 예시 전략", expanded=False):
        example_copies = [
            "**카피**: 어른은 그렇게 강하지 않다.\n**설명**: 서로의 약함을 품을 때 비로소 강해지는 곳, 이 도시는 그런 당신을 위한 쉼터입니다.",
            "**카피**: 인생을 세 단어로 말하면, Boy Meets Girl.\n**설명**: 사랑이 시작된 이곳, 이 작은 거리가 당신의 이야기를 기다리고 있습니다.",
            "**카피**: 인류는 달에 가서도 영어를 말한다.\n**설명**: 어떤 곳에서도 소통이 중요한 순간이 찾아옵니다.",
            "**카피**: 누군가로 끝나지 마라.\n**설명**: 이 도시는 당신만의 이야기를 만들 기회를 제공합니다.",
            "**카피**: 마흔살은 두번째 스무살.\n**설명**: 새로운 시작을 축하하는 여행지, 여기서 인생의 다음 장을 열어보세요.",
            "**카피**: 기적은 우연을 가장해 나타난다.\n**설명**: 일상의 순간들이 특별해지는 이곳을 만나보세요.",
            "**카피**: 뛰어난 팀에는 뛰어난 2인자가 있다.\n**설명**: 이 도시의 숨은 매력들이 당신을 돕는 동반자가 됩니다.",
            "**카피**: 인생의 등장인물이 달라진다.\n**설명**: 이 여행지는 당신의 새로운 이야기를 위한 무대입니다."
        ]

        edited_copies = st.text_area(
            "예시 수정/추가",
            value="\n\n".join(example_copies),
            height=400,
            key="copy_examples"
        )

    # 최종 프롬프트 미리보기 및 수정 (접기 가능)
    with st.expander("📝 Final Prompt Output: 최종 카피 프롬프트 미리보기", expanded=False):
        final_prompt = f"{base_structure}\n\n{edited_docs}\n\n요구사항:\n{requirements}\n\n참고 예시:\n{edited_copies}"
        edited_prompt = st.text_area(
            "프롬프트 직접 수정",
            value=final_prompt,
            height=400,
            key="final_prompt"
        )

    st.subheader("🎨 여행지 광고 카피라이팅 생성하기")
    if st.button("🎨 광고 카피 생성", use_container_width=True):
        if not selected_region or not selected_generation:
            st.error("지역과 세대를 선택해주세요!")
        else:
            with st.spinner("AI 모델이 광고 카피를 생성중입니다..."):
                results = {}
                evaluations = {}
                revisions = {}  # 퇴고 결과 저장
                revision_evaluations = {}  # 퇴고 결과 평가 저장
    
                model_cols = st.columns(3)
    
                # 1&2차 생성 (모델별로 1,2차를 연속해서)
                for idx, (model_name, col) in enumerate(zip(["gpt", "gemini", "claude"], model_cols)):
                    with col:
                        st.markdown(get_model_header_html(model_name), unsafe_allow_html=True)
    
                        # 1️⃣ 카피 (초안) 생성
                        st.markdown("##### 1️⃣ 카피 (초안)")
                        result = generate_copy(edited_prompt, model_name)
                        if isinstance(result, dict) and result.get("success"):
                            results[model_name] = result["content"]
                            eval_result = st.session_state.evaluator.evaluate(result["content"], "gpt")
                            evaluations[model_name] = eval_result
    
                            copy_text, description_text = extract_copy_and_description(results[model_name])
                            st.markdown(get_result_card_html(
                                model_name, copy_text, description_text, evaluations[model_name]
                            ), unsafe_allow_html=True)
    
                            # 초안 음성 생성 및 수동 재생 버튼 추가
                            audio_file_path = generate_tts(copy_text, f"{model_name}_copy_audio")
                            if audio_file_path:
                                if st.button(f"🎧 {model_name.upper()} 초안 음성 듣기"):
                                    st.audio(audio_file_path, format="audio/mp3")
    
                        # 2️⃣ 퇴고 카피
                        st.markdown("##### 2️⃣ AI 에이전트 퇴고 카피")
                        revision = generate_revision(results[model_name], evaluations[model_name], model_name)
                        if isinstance(revision, dict) and revision.get("success"):
                            revision_eval = st.session_state.evaluator.evaluate(revision["content"], "gpt")
                            revisions[model_name] = revision["content"]
                            revision_evaluations[model_name] = revision_eval
    
                            copy_text, description_text = extract_copy_and_description(revisions[model_name])
                            improvement = revision_evaluations[model_name]['score'] - evaluations[model_name]['score']
                            st.markdown(get_revision_card_html(
                                model_name, copy_text, description_text,
                                revision_evaluations[model_name], improvement
                            ), unsafe_allow_html=True)
    
                            # 퇴고 음성 생성 및 수동 재생 버튼 추가
                            audio_file_path = generate_tts(copy_text, f"{model_name}_revision_audio")
                            if audio_file_path:
                                if st.button(f"🎧 {model_name.upper()} 퇴고 음성 듣기"):
                                    st.audio(audio_file_path, format="audio/mp3")
    
                # 3차 페르소나 변형 생성
                persona_variations = {}
                for model_name, col in zip(["gpt", "gemini", "claude"], model_cols):
                    if model_name in revisions:
                        selected_personas = random.sample(name_list, 2)
                        persona_variations[model_name] = {}
    
                        with col:
                            with st.spinner(f"{model_name.upper()} 페르소나 변형 생성 중..."):
                                st.markdown("##### 3️⃣ 페르소나 변형")
    
                                base_copy_text, base_description_text = extract_copy_and_description(revisions[model_name])
                                base_copy = f"{base_copy_text} {base_description_text}"
    
                                for persona_name in selected_personas:
                                    try:
                                        persona_prompt = name_to_persona(persona_name)
                                        if "Error:" in persona_prompt:
                                            st.error(f"페르소나 생성 실패: {persona_prompt}")
                                            continue
    
                                        result = transform_ad_copy(base_copy, persona_prompt, persona_name)
                                        eval_result = st.session_state.evaluator.evaluate(result, "gpt")
                                        improvement = eval_result['score'] - revision_evaluations[model_name]['score']
    
                                        persona_variations[model_name][persona_name] = {
                                            "result": result,
                                            "evaluation": eval_result,
                                            "improvement": improvement
                                        }
    
                                        if "Explanation:" in result and "Transformed Copy:" in result:
                                            explanation = result.split("Explanation:")[1].split("Transformed Copy:")[0].strip()
                                            transformed_copy = result.split("Transformed Copy:")[1].strip()
    
                                            st.markdown(get_persona_variation_card_html(
                                                model_name,
                                                persona_name,
                                                transformed_copy,
                                                explanation,
                                                eval_result['score'],
                                                improvement
                                            ), unsafe_allow_html=True)
    
                                            # 페르소나 음성 생성 및 수동 재생 버튼 추가
                                            audio_file_path = generate_tts(transformed_copy, f"{model_name}_{persona_name}_audio")
                                            if audio_file_path:
                                                if st.button(f"🎧 {persona_name} 페르소나 음성 듣기"):
                                                    st.audio(audio_file_path, format="audio/mp3")
    
                                    except Exception as e:
                                        st.error(f"{persona_name} 처리 중 오류 발생: {str(e)}")
    
                experiment_data = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "prompt": edited_prompt,
                    "first_results": results,
                    "first_evaluations": evaluations,
                    "revisions": revisions,
                    "revision_evaluations": revision_evaluations,
                    "persona_variations": persona_variations,
                    "settings": {
                        "region": selected_region,
                        "generation": selected_generation,
                        "season": selected_season if selected_season else None,
                        "mbti": selected_mbti if include_mbti else None
                    }
                }
                st.session_state.history.append(experiment_data)
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
                            try:
                                progress_text.text(f"✍️ {persona_name}의 시선으로 카피 생성 중...")
                                
                                city_doc = DOCS["region"].get(selected_region, "")
                                if not city_doc:
                                    continue
                                
                                persona_data = PERSONAS.get(persona_name, {})
                                if not persona_data:
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
                                    if result.get('success', False):
                                        persona_results[persona_name] = {
                                            "copy": result.get('content', ''),
                                            "persona_info": persona_data,
                                            "category": get_safe_persona_info(persona_data, 'category', 'unknown')
                                        }
                                    
                                progress_bar.progress((idx + 1) / len(selected_personas))
                                
                            except Exception as e:
                                print(f"{persona_name} 처리 중 오류: {str(e)}")
                                continue
                        
                        # 진행 표시 제거
                        progress_text.empty()
                        progress_bar.empty()
        
                        if persona_results:  # 결과가 있는 경우에만 지도와 결과 표시
                
                            # 지도와 결과를 함께 표시할 컨테이너
                            st.markdown(f"### 🗺️ 다양한 시선으로 바라본 {selected_region}")
                            
                            # 지도 생성
                            m = folium.Map(
                                location=[CITY_COORDINATES[selected_region]["lat"], 
                                        CITY_COORDINATES[selected_region]["lon"]],
                                zoom_start=14,
                                tiles='CartoDB dark_matter'
                            )
        
                            # 4x4 그리드 위치 계산을 위한 기준점과 오프셋 설정
                            base_lat = CITY_COORDINATES[selected_region]["lat"]
                            base_lon = CITY_COORDINATES[selected_region]["lon"]
                            lat_offset = 0.004  # 위도 간격
                            lon_offset = 0.005  # 경도 간격
                            grid_size = 4

                            # Divicon을 사용하여 항상 보이는 라벨 추가
                                

                            
                            # 마커 추가
                            for idx, (persona_name, result) in enumerate(persona_results.items()):
                                try:
                                    category_color = get_safe_persona_info(
                                        PERSONA_CATEGORIES.get(
                                            get_safe_persona_info(result.get('persona_info', {}), 'category', 'unknown'),
                                            {}
                                        ),
                                        'color',
                                        '#333'
                                    )
                                    
                                    # 4x4 그리드 위치 계산
                                    row = idx // grid_size
                                    col = idx % grid_size
                                    
                                    marker_lat = base_lat + (lat_offset * (row - (grid_size-1)/2))
                                    marker_lon = base_lon + (lon_offset * (col - (grid_size-1)/2))


                                    html = f"""
                                        <div style="
                                            position: relative;
                                            left: 10px;
                                            top: -10px;
                                            background-color: rgba(255, 255, 255, 0.95);
                                            padding: 8px;
                                            border-radius: 8px;
                                            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                                            border: 2px solid {get_safe_persona_info(PERSONA_CATEGORIES.get(result.get('category', 'unknown'), {}), 'color', '#333')};
                                            min-width: 150px;
                                            max-width: 200px;
                                        ">
                                            <b style="
                                                color: {get_safe_persona_info(PERSONA_CATEGORIES.get(result.get('category', 'unknown'), {}), 'text_color', '#333')};
                                                font-size: 12px;
                                            ">{persona_name}{' ' + get_safe_persona_info(result.get('persona_info', {}), 'nationality', '') if get_safe_persona_info(result.get('persona_info', {}), 'nationality') else ''}</b>
                                            <p style="
                                                margin: 4px 0 0 0;
                                                color: #333;
                                                font-size: 11px;
                                                line-height: 1.4;
                                            ">{get_safe_persona_info(result, 'copy', '내용이 없습니다.')}</p>
                                        </div>
                                    """

                                    
                                    # DivIcon 생성 및 추가
                                    icon = folium.DivIcon(
                                        html=html,
                                        icon_size=(150, 100),
                                        icon_anchor=(0, 0)
                                    )
                                    
                                    folium.Marker(
                                        [marker_lat, marker_lon],
                                        icon=icon
                                    ).add_to(m)
                                    
                                except Exception as e:
                                    print(f"마커 생성 중 오류: {str(e)}")
                                    continue
                            
                            # 지도 경계 설정
                            bounds = [
                                [base_lat - (lat_offset * 3), base_lon - (lon_offset * 3)],
                                [base_lat + (lat_offset * 3), base_lon + (lon_offset * 3)]
                            ]
                            m.fit_bounds(bounds, padding=(150, 150))
        
                            # 지도 표시
                            folium_static(m)
                            
                            
                            # 결과 저장 부분을 try-except로 감싸고 상태 표시 추가
                            try:
                                if persona_results:  # 결과가 있는 경우에만 저장 버튼 표시
                                    col1, col2 = st.columns([1, 2])
                                    with col1:
                                        if st.button("💾 결과 저장하기", use_container_width=True):
                                            try:
                                                # DataFrame 생성
                                                df = pd.DataFrame([
                                                    {
                                                        "페르소나": name,
                                                        "카테고리": data["category"],
                                                        "광고카피": data.get("copy", ""),  # get으로 안전하게 접근
                                                        "생성시간": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                                    }
                                                    for name, data in persona_results.items()
                                                    if isinstance(data, dict)  # 데이터가 딕셔너리인 경우만 처리
                                                ])
                                                
                                                if not df.empty:
                                                    # CSV 파일 생성
                                                    csv = df.to_csv(index=False).encode('utf-8-sig')
                                                    
                                                    # 다운로드 버튼 표시
                                                    with col2:
                                                        st.download_button(
                                                            label=f"📥 {selected_region} 광고카피 다운로드",
                                                            data=csv,
                                                            file_name=f'{selected_region}_광고카피_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                                                            mime='text/csv',
                                                            help="생성된 모든 페르소나의 광고카피가 CSV 파일로 저장됩니다."
                                                        )
                                                        st.success("✅ CSV 파일이 준비되었습니다. 다운로드 버튼을 눌러주세요!")
                                                else:
                                                    st.warning("저장할 데이터가 없습니다.")
                                                    
                                            except Exception as e:
                                                st.error(f"파일 생성 중 오류가 발생했습니다: {str(e)}")
                                    
                            except Exception as e:
                                st.error(f"저장 기능 실행 중 오류가 발생했습니다: {str(e)}")
        
                    except Exception as e:
                        st.error(f"광고 카피 생성 중 오류가 발생했습니다: {str(e)}")
