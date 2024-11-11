import streamlit as st
import openai
import google.generativeai as genai
from anthropic import Anthropic
from datetime import datetime
import pandas as pd
import json
import pathlib
import plotly.express as px
from typing import Dict, List, Optional
from dataclasses import dataclass

# Initialize API keys from Streamlit secrets
openai.api_key = st.secrets["chatgpt"]
genai.configure(api_key=st.secrets["gemini"])
anthropic = Anthropic(api_key=st.secrets["claude"])


#챗-제-클 순서 오와열
model_zoo = ['gpt-4o',
             'gemini-1.5-pro-exp-0827',
             'claude-3-5-haiku-20241022']

# Gemini model configuration
gemini_model = genai.GenerativeModel(model_zoo[1])


# CSS 


# Custom CSS for modern design
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

    /* 전체 폰트 및 색상 스타일 */
    [data-testid="stAppViewContainer"] {
        font-family: 'Pretendard', sans-serif;
        background-color: #f8fafc;
    }

    /* 헤더 스타일링 */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Pretendard', sans-serif;
        font-weight: 700;
        color: #1e293b;
    }

    /* 카드 스타일 */
    .stCard {
        border-radius: 15px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
        padding: 1rem;
        background-color: white;
    }

    /* 버튼 스타일링 */
    .stButton > button {
        background-color: #3b82f6;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background-color: #2563eb;
        transform: translateY(-1px);
    }

    /* 사이드바 스타일링 */
    [data-testid="stSidebar"] {
        background-color: white;
        border-right: 1px solid #e2e8f0;
        padding: 2rem 1rem;
    }
    [data-testid="stSidebar"] .stMarkdown {
        padding: 0.5rem 0;
    }

    /* 셀렉트박스 스타일링 */
    .stSelectbox > div > div {
        background-color: white;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        padding: 0.5rem;
    }

    /* 결과 카드 스타일링 */
    .result-card {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    /* 모델 태그 스타일링 */
    .model-tag {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .gpt-tag { background-color: #10b981; color: white; }
    .gemini-tag { background-color: #6366f1; color: white; }
    .claude-tag { background-color: #8b5cf6; color: white; }

    /* 평가 결과 스타일링 */
    .evaluation-score {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1e293b;
    }
    .evaluation-reason {
        color: #64748b;
        font-size: 0.875rem;
        line-height: 1.5;
        margin-top: 0.5rem;
    }

    /* 텍스트 영역 스타일링 */
    .stTextArea > div > textarea {
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        padding: 1rem;
        font-family: 'Pretendard', sans-serif;
    }

    /* 로딩 스피너 스타일링 */
    .stSpinner > div {
        border-color: #3b82f6;
    }

    /* 탭 스타일링 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: white;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        color: #1e293b;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3b82f6;
        color: white;
        border: none;
    }

    /* 경고/성공 메시지 스타일링 */
    .stAlert {
        border-radius: 8px;
        padding: 1rem;
    }
    .stSuccess {
        background-color: #ecfdf5;
        color: #065f46;
    }
    .stError {
        background-color: #fef2f2;
        color: #991b1b;
    }
</style>
""", unsafe_allow_html=True)








# MBTI 그룹 상수 정의
MBTI_GROUPS = {
    "분석가형": ["INTJ", "INTP", "ENTJ", "ENTP"],
    "외교관형": ["INFJ", "INFP", "ENFJ", "ENFP"],
    "관리자형": ["ISTJ", "ISFJ", "ESTJ", "ESFJ"],
    "탐험가형": ["ISTP", "ISFP", "ESTP", "ESFP"]
}

# 문서 로드 함수 수정
def load_docs() -> Dict[str, Dict[str, str]]:
    docs_path = pathlib.Path("docs")
    docs = {
        "region": {},
        "generation": {},
        "mbti": {}
    }
    
    # 지역 문서 로드
    region_path = docs_path / "regions"
    if region_path.exists():
        for file in region_path.glob("*.txt"):
            with open(file, "r", encoding="utf-8") as f:
                docs["region"][file.stem] = f.read()
    
    # 세대 문서 로드
    generation_path = docs_path / "generations"
    if generation_path.exists():
        for file in generation_path.glob("*.txt"):
            with open(file, "r", encoding="utf-8") as f:
                docs["generation"][file.stem] = f.read()
    
    # MBTI 문서 로드 (단일 파일)
    mbti_file = docs_path / "mbti" / "mbti_all.txt"
    if mbti_file.exists():
        with open(mbti_file, "r", encoding="utf-8") as f:
            content = f.read()
            # 각 MBTI 섹션 파싱
            for group in MBTI_GROUPS.keys():
                group_start = content.find(f"[{group}]")
                next_group_start = len(content)
                for other_group in MBTI_GROUPS.keys():
                    if other_group != group:
                        pos = content.find(f"[{other_group}]")
                        if pos > group_start and pos < next_group_start:
                            next_group_start = pos
                
                group_content = content[group_start:next_group_start].strip()
                for mbti in MBTI_GROUPS[group]:
                    mbti_start = group_content.find(mbti)
                    next_mbti_start = len(group_content)
                    for other_mbti in MBTI_GROUPS[group]:
                        if other_mbti != mbti:
                            pos = group_content.find(other_mbti)
                            if pos > mbti_start and pos < next_mbti_start:
                                next_mbti_start = pos
                    
                    mbti_content = group_content[mbti_start:next_mbti_start].strip()
                    docs["mbti"][mbti.lower()] = mbti_content
    
    return docs


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

class AdCopyEvaluator:
    """광고 카피 평가를 관리하는 클래스"""
    def __init__(self, scoring_config: ScoringConfig):
        self.scoring_config = scoring_config
        self.results_cache = {}
    
    def evaluate(self, copy: str, model_name: str) -> Dict:
        """평가 실행 및 결과 파싱"""
        try:
            # Check cache
            cache_key = f"{copy}_{model_name}"
            if cache_key in self.results_cache:
                return self.results_cache[cache_key]
            
            # Construct evaluation prompt
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
                response = openai.ChatCompletion.create(
                    model=model_zoo[0],
                    messages=[{"role": "user", "content": evaluation_prompt}]
                )
                result_text = response.choices[0].message.content
            elif model_name == "gemini":
                response = gemini_model.generate_content(evaluation_prompt)
                result_text = response.text
            else:  # claude
                response = anthropic.messages.create(
                    model=model_zoo[2],
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
            
            score_line = next(l for l in lines if '점수:' in l)
            score = int(''.join(filter(str.isdigit, score_line)))
            
            reason_line = next(l for l in lines if '이유:' in l)
            reason = reason_line.split('이유:')[1].strip()
            
            detailed_line = next(l for l in lines if '상세점수:' in l)
            detailed_scores = [
                int(s.strip()) for s in 
                detailed_line.split('상세점수:')[1].strip().split(',')
            ]
            
            return {
                "score": score,
                "reason": reason,
                "detailed_scores": detailed_scores
            }
        except Exception as e:
            st.error(f"결과 파싱 중 오류 발생: {str(e)}")
            return {
                "score": 0,
                "reason": f"파싱 실패: {str(e)}",
                "detailed_scores": [0] * len(self.scoring_config.criteria)
            }

def generate_copy(prompt: str, model_name: str) -> str:
    """광고 카피 생성"""
    try:
        if model_name == "gpt":
            response = openai.ChatCompletion.create(
                model=model_zoo[0],
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        elif model_name == "gemini":
            response = gemini_model.generate_content(prompt)
            return response.text.strip()
        else:  # claude
            response = anthropic.messages.create(
                model=model_zoo[2],
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
    except Exception as e:
        return f"생성 실패: {str(e)}"

def visualize_evaluation_results(results: Dict):
    """결과 시각화"""
    fig = px.radar(
        pd.DataFrame({
            '기준': st.session_state.scoring_config.criteria,
            '점수': results['detailed_scores']
        }),
        r='점수',
        theta='기준',
        title="평가 기준별 점수"
    )
    return fig

# Streamlit app configuration
st.set_page_config(page_title="CopyStudio Lab", page_icon="🔬", layout="wide")

# Load documents
DOCS = load_docs()

# Initial scoring configuration
DEFAULT_SCORING_CONFIG = ScoringConfig(
    prompt="""
주어진 광고 카피를 다음 기준으로 평가해주세요.
각 기준별로 0-100점 사이의 점수를 부여하고, 
최종 점수는 각 기준의 평균으로 계산합니다.
    """,
    criteria=[
        "타겟 적합성",
        "메시지 전달력",
        "창의성",
        "브랜드 적합성"
    ]
)

# Initialize session state
if 'scoring_config' not in st.session_state:
    st.session_state.scoring_config = DEFAULT_SCORING_CONFIG
if 'evaluator' not in st.session_state:
    st.session_state.evaluator = AdCopyEvaluator(st.session_state.scoring_config)
if 'history' not in st.session_state:
    st.session_state.history = []


# Sidebar configuration
with st.sidebar:
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

    # Target selection
    st.header("🎯 타겟 설정")
    
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
    
    st.subheader("MBTI 설정")
    selected_mbti_groups = st.multiselect(
        "MBTI 그룹 선택",
        options=MBTI_GROUPS.keys()
    )
    
    selected_mbti = []
    for group in selected_mbti_groups:
        selected_mbti.extend(MBTI_GROUPS[group])

# Main content
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("💡 프롬프트 작성")
    
    # Generate base prompt
    base_prompt = f"""
다음 정보를 바탕으로 광고 카피를 생성해주세요:

[지역 정보]
{DOCS["region"].get(selected_region, "지역 정보가 없습니다.")}

[세대 특성]
{DOCS["generation"].get(selected_generation, "세대 정보가 없습니다.")}
"""
    
    if selected_mbti:
        mbti_info = "\n".join([
            f"[{mbti.upper()} 특성]\n{DOCS['mbti'].get(mbti.lower(), '정보 없음')}"
            for mbti in selected_mbti
        ])
        base_prompt += f"\n[MBTI 특성]\n{mbti_info}"
    
    base_prompt += """
요구사항:
1. 선택된 타겟층의 특성을 반영한 톤앤매너로 작성
2. 카피는 한 문장으로 작성
3. 이모지를 적절히 활용
4. 선택된 지역의 특징을 효과적으로 표현
"""
    
    prompt = st.text_area(
        "생성 프롬프트",
        value=base_prompt,
        height=300
    )
    
    if st.button("🎨 광고 카피 생성", use_container_width=True):
        if not selected_region or not selected_generation:
            st.error("지역과 세대를 선택해주세요!")
        else:
            with st.spinner("AI 모델이 광고 카피를 생성중입니다..."):
                # Generate copies
                results = {
                    model: generate_copy(prompt, model)
                    for model in ["gpt", "gemini", "claude"]
                }
                
                # Evaluate copies
                evaluations = {
                    model: st.session_state.evaluator.evaluate(copy, model)
                    for model, copy in results.items()
                }
                
                # Save results
                experiment_data = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "prompt": prompt,
                    "results": results,
                    "evaluations": evaluations,
                    "settings": {
                        "region": selected_region,
                        "generation": selected_generation,
                        "mbti": selected_mbti
                    }
                }
                st.session_state.history.append(experiment_data)
with col2:
    st.subheader("📊 실험 결과")
    
    for idx, experiment in enumerate(reversed(st.session_state.history)):
        with st.container():
            st.markdown(f"""
            <div class="result-card">
                <p style='color: #64748b; font-size: 0.875rem;'>{experiment['timestamp']}</p>
                <div style='margin: 1rem 0;'>
            """, unsafe_allow_html=True)
            
            for model in ["gpt", "gemini", "claude"]:
                result = experiment['results'][model]
                evaluation = experiment['evaluations'][model]
                
                st.markdown(f"""
                <div style='margin-bottom: 1.5rem;'>
                    <span class="model-tag {model}-tag">{model.upper()}</span>
                    <div style='background-color: #f8fafc; padding: 1rem; border-radius: 8px; margin: 0.5rem 0;'>
                        {result}
                    </div>
                    <div class="evaluation-score">
                        점수: {evaluation['score']}점
                    </div>
                    <div class="evaluation-reason">
                        {evaluation['reason']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                fig = visualize_evaluation_results(evaluation)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("</div></div>", unsafe_allow_html=True)
