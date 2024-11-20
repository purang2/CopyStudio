
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
from typing import Dict, List, Optional, Union

from google.generativeai.types import HarmCategory, HarmBlockThreshold
from google.api_core.exceptions import ResourceExhausted

import folium
from streamlit_folium import folium_static



# Page config must be the first Streamlit command
st.set_page_config(
    page_title="광고카피 문구 생성 AI", 
    page_icon="📒", 
    layout="wide"
)

# 앱 제목
st.title("🐻 광고카피 문구 생성 AI")



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

    if include_mbti and mbti and mbti in MBTI_TYPES:
        try:
            mbti_content = DOCS["mbti"].get(mbti)
            if mbti_content:
                mbti_prompt = f"""

[MBTI 특성 - {mbti}]
{mbti_content}

특별 고려사항:
- 위 {mbti} 성향의 여행 선호도를 반영해 카피를 작성해주세요
- 해당 MBTI의 핵심 가치관과 선호 스타일을 고려해주세요"""
                base_prompt += mbti_prompt
            else:
                print(f"{mbti}.txt 파일의 내용을 찾을 수 없습니다.")
        except Exception as e:
            print(f"MBTI 프롬프트 생성 에러: {str(e)}")

    base_prompt += """

[제약사항]
- 한 문장으로 작성
- 이모지 1-2개 포함
- 도시만의 독특한 특징 하나 이상 포함
- 클리셰나 진부한 표현 지양
"""
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
