import streamlit as st
#import openai
from openai import OpenAI
import google.generativeai as genai
from anthropic import Anthropic
from datetime import datetime
import pandas as pd
import json
import pathlib
from typing import Dict, List, Optional
from dataclasses import dataclass

import plotly.express as px 
import plotly.graph_objects as go


# Page config must be the first Streamlit command
st.set_page_config(
    page_title="CopyStudio Lab - 광고 카피 연구소", 
    page_icon="🔬", 
    layout="wide"
)

# Initialize API keys from Streamlit secrets
#openai.api_key = st.secrets["chatgpt"]
genai.configure(api_key=st.secrets["gemini"])
anthropic = Anthropic(api_key=st.secrets["claude"])
client = OpenAI(api_key=st.secrets["chatgpt"])  # API 키 입력



#챗-제-클 순서 오와열
model_zoo = ['gpt-4o',
             'gemini-1.5-pro-exp-0827',
             'claude-3-5-haiku-20241022']

# Gemini model configuration
gemini_model = genai.GenerativeModel(model_zoo[1])


# Custom CSS
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

    [data-testid="stAppViewContainer"] {
        font-family: 'Pretendard', sans-serif;
        background-color: #f8fafc;
    }

    .prompt-editor {
        border: 2px solid #e2e8f0;
        border-radius: 10px;
        padding: 1rem;
        background-color: white;
    }

    .prompt-editor:hover {
        border-color: #3b82f6;
        box-shadow: 0 0 0 1px #3b82f6;
    }

    .prompt-tip {
        background-color: #f1f5f9;
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 8px 8px 0;
    }

    .result-card {
        background-color: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        transition: all 0.2s ease;
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
        background-color: #f1f5f9;
        cursor: pointer;
    }
    
    .score-badge:hover {
        background-color: #e2e8f0;
    }

    .history-item {
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        margin: 1rem 0;
        background-color: white;
        border-radius: 0 8px 8px 0;
    }

    .prompt-feedback {
        background-color: #f8fafc;
        border-radius: 8px;
        padding: 1rem;
        margin-top: 1rem;
    }

    .improvement-tip {
        color: #3b82f6;
        font-weight: 500;
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


def create_adaptive_prompt(
    city_doc: str, 
    target_generation: str, 
    mbti: str = None,
    include_mbti: bool = False
) -> str:
    """문서 기반 유연한 프롬프트 생성"""
    base_prompt = f"""
당신은 숙련된 카피라이터입니다. 
아래 제공되는 도시 정보를 참고하여, 매력적인 광고 카피를 생성해주세요.
이 정보는 참고용이며, 카피는 자연스럽고 창의적이어야 합니다.

[도시 정보]
{city_doc}

[카피 작성 가이드라인]
1. 위 정보는 영감을 얻기 위한 참고 자료입니다.
2. 도시의 핵심 매력을 포착해 신선한 관점으로 표현해주세요.
3. 타겟층에 맞는 톤앤매너를 사용하되, 정보의 나열은 피해주세요.
4. 감성적 공감과 구체적 특징이 조화를 이루도록 해주세요.

[타겟 정보]
세대: {target_generation}"""

    if include_mbti and mbti:
        mbti_prompt = f"""
MBTI: {mbti}
특별 고려사항: 
- {mbti} 성향의 여행 선호도를 반영
- 해당 성향의 관심사와 가치관 고려"""
        base_prompt += mbti_prompt

    base_prompt += """

[제약사항]
- 한 문장으로 작성
- 이모지 1-2개 포함
- 도시만의 독특한 특징 하나 이상 포함
- 클리셰나 진부한 표현 지양
"""
    return base_prompt
# Load documents
def load_docs() -> Dict[str, Dict[str, str]]:
    docs_path = pathlib.Path("docs")
    docs = {
        "region": {},
        "generation": {},
        "mbti": {}
    }
    
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
    
    # Load MBTI doc
    mbti_file = docs_path / "mbti" / "mbti_all.txt"
    if mbti_file.exists():
        with open(mbti_file, "r", encoding="utf-8") as f:
            content = f.read()
            # MBTI 파일 내용을 그대로 저장
            docs["mbti"]["mbti_all"] = content
    
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
                    response = gemini_model.generate_content(prompt)
                    return response.text if hasattr(response, 'text') else "Gemini API 응답 오류"
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
            # 숫자만 추출하는 로직 개선
            score_text = ''.join(c for c in score_line.split('점수:')[1] if c.isdigit() and c != '*')
            score = int(score_text) if score_text else 0
            
            # 이유 추출
            reason_line = next(l for l in lines if '이유:' in l)
            reason = reason_line.split('이유:')[1].strip()
            
            # 상세점수 추출 개선
            try:
                detailed_line = next(l for l in lines if '상세점수:' in l)
                detailed_scores_text = detailed_line.split('상세점수:')[1].strip()
                detailed_scores = []
                
                for s in detailed_scores_text.split(','):
                    score_text = ''.join(c for c in s if c.isdigit() and c != '*')
                    detailed_scores.append(int(score_text) if score_text else 0)
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

def generate_copy(prompt: str, model_name: str) -> str:
    """광고 카피 생성"""
    try:
        if model_name == "gpt":
            #response = openai.ChatCompletion.create(
            response = client.chat.completions.create(
                model=model_zoo[0],
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000
            )
            return response.choices[0].message.content.strip()
        elif model_name == "gemini":
            try:
                response = gemini_model.generate_content(prompt)
                return response.text if hasattr(response, 'text') else "Gemini API 응답 오류"
            except Exception as e:
                return f"Gemini 평가 실패: {str(e)}"
        else:  # claude
            response = anthropic.messages.create(
                model=model_zoo[2],
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000
            )
            return response.content[0].text.strip()
    except Exception as e:
        return f"생성 실패: {str(e)}"
        
def visualize_evaluation_results(results: Dict):
    """결과 시각화 함수"""
    fig = go.Figure(data=go.Scatterpolar(
        r=results['detailed_scores'],
        theta=st.session_state.scoring_config.criteria,
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



def analyze_prompt_performance(history: List[dict]) -> dict:
    """프롬프트 성능 분석"""
    if not history:
        return None
    
    latest = history[-1]
    prev = history[-2] if len(history) > 1 else None
    
    current_avg = sum(e['score'] for e in latest['evaluations'].values()) / 3
    prev_avg = sum(e['score'] for e in prev['evaluations'].values()) / 3 if prev else None
    
    analysis = {
        "current_score": current_avg,
        "improvement": current_avg - prev_avg if prev_avg else 0,
        "top_model": max(latest['evaluations'].items(), key=lambda x: x[1]['score'])[0],
        "suggestions": []
    }
    
    if analysis["improvement"] <= 0:
        analysis["suggestions"].append("더 구체적인 지역 특징을 언급해보세요")
        analysis["suggestions"].append("타겟층의 관심사를 더 반영해보세요")
    
    return analysis

def create_performance_chart(history: List[dict]) -> go.Figure:
    """성능 트렌드 차트 생성"""
    if not history:
        return None
        
    data = []
    for entry in history:
        timestamp = entry['timestamp']
        for model, eval_data in entry['evaluations'].items():
            data.append({
                'timestamp': timestamp,
                'model': model,
                'score': eval_data['score']
            })
    
    df = pd.DataFrame(data)
    
    fig = go.Figure()
    for model in ["gpt", "gemini", "claude"]:
        model_data = df[df['model'] == model]
        fig.add_trace(go.Scatter(
            x=model_data['timestamp'],
            y=model_data['score'],
            name=model.upper(),
            line=dict(color=MODEL_COLORS[model])
        ))
    
    fig.update_layout(
        title='프롬프트 성능 트렌드',
        xaxis_title="시간",
        yaxis_title="점수",
        legend_title="모델"
    )
    
    return fig



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
    
    # 프롬프트 생성
    prompt = create_adaptive_prompt(
        city_doc=DOCS["region"].get(selected_region, "지역 정보가 없습니다."),
        target_generation=selected_generation,
        mbti=selected_mbti,
        include_mbti=include_mbti
    )
    
    # 프롬프트 표시 및 편집 가능하게
    edited_prompt = st.text_area(
        "생성 프롬프트",
        value=prompt,
        height=400
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
    st.subheader("실험 결과")
    
    if st.session_state.history:
        latest_experiment = st.session_state.history[-1]
        
        # 성능 분석
        analysis = analyze_prompt_performance(st.session_state.history)
        if analysis:
            try:
                st.markdown(f"""
                <div class="prompt-feedback">
                    <h4>📈 성능 분석</h4>
                    <p>현재 평균 점수: {analysis['current_score']:.1f}</p>
                    <p>이전 대비: {analysis['improvement']:+.1f}</p>
                    <p>최고 성능 모델: {analysis['top_model'].upper()}</p>
                    
                    <div class="improvement-tip">
                        💡 개선 포인트:
                        {'<br>'.join(f'- {s}' for s in analysis['suggestions'])}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"성능 분석 표시 중 오류 발생: {str(e)}")
        
        # 결과 카드 표시
        model_list = ["gpt", "gemini", "claude"]
        for idx, model_name in enumerate(model_list):
            try:
                with st.container():
                    result = latest_experiment['results'].get(model_name, "결과 없음")
                    eval_data = latest_experiment['evaluations'].get(model_name, {
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
