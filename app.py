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

# Gemini model configuration
gemini_model = genai.GenerativeModel('gemini-1.5-pro-exp-0827')


# Load documents from docs folder
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
    
    # Load MBTI docs
    mbti_path = docs_path / "mbti"
    if mbti_path.exists():
        for file in mbti_path.glob("*.txt"):
            with open(file, "r", encoding="utf-8") as f:
                docs["mbti"][file.stem] = f.read()
    
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
            # 모델별 API 호출
            if model_name == "gpt":
                response = openai.ChatCompletion.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": evaluation_prompt}]
                )
                result_text = response.choices[0].message.content
            elif model_name == "gemini":
                response = gemini_model.generate_content(evaluation_prompt)
                result_text = response.text
            else:  # claude
                response = anthropic.messages.create(
                    model="claude-3-5-haiku-20241022",
                    messages=[{"role": "user", "content": evaluation_prompt}]
                )
                result_text = response.content[0].text
            
            # 결과 파싱
            parsed_result = self.parse_evaluation_result(result_text)
            
            # 캐시에 저장
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
        """평가 결과 파싱 로직"""
        try:
            lines = result_text.split('\n')
            
            # 점수 추출
            score_line = next(l for l in lines if '점수:' in l)
            score = int(''.join(filter(str.isdigit, score_line)))
            
            # 이유 추출
            reason_line = next(l for l in lines if '이유:' in l)
            reason = reason_line.split('이유:')[1].strip()
            
            # 상세 점수 추출
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
    """광고 카피 생성 함수"""
    try:
        if model_name == "gpt":
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        elif model_name == "gemini":
            response = gemini_model.generate_content(prompt)
            return response.text.strip()
        else:  # claude
            response = anthropic.messages.create(
                model="claude-3-5-haiku-20241022",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
    except Exception as e:
        return f"생성 실패: {str(e)}"

def visualize_evaluation_results(results: Dict):
    """결과 시각화 함수"""
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

# Streamlit 앱 설정
st.set_page_config(page_title="CopyStudio Lab", page_icon="🔬", layout="wide")

# 문서 로드
DOCS = load_docs()

# 초기 평가 설정
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

# 세션 상태 초기화
if 'scoring_config' not in st.session_state:
    st.session_state.scoring_config = DEFAULT_SCORING_CONFIG
if 'evaluator' not in st.session_state:
    st.session_state.evaluator = AdCopyEvaluator(st.session_state.scoring_config)
if 'history' not in st.session_state:
    st.session_state.history = []
if 'selected_docs' not in st.session_state:
    st.session_state.selected_docs = {
        'region': '',
        'generation': '',
        'mbti': []
    }

# 메인 UI
st.title("🔬 광고 카피 생성 연구 플랫폼")

# 사이드바: 평가 설정
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

    # 타겟 설정
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
    
    selected_mbti_groups = st.multiselect(
        "MBTI 선택",
        options=list(DOCS["mbti"].keys())
    )

# 메인 컨텐츠
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("💡 프롬프트 작성")
    
    # 프롬프트 생성
    base_prompt = f"""
다음 정보를 바탕으로 광고 카피를 생성해주세요:

[지역 정보]
{DOCS["region"].get(selected_region, "지역 정보가 없습니다.")}

[세대 특성]
{DOCS["generation"].get(selected_generation, "세대 정보가 없습니다.")}
"""
    
    if selected_mbti_groups:
        mbti_info = "\n".join([
            f"[{mbti.upper()} 특성]\n{DOCS['mbti'].get(mbti, '정보 없음')}"
            for mbti in selected_mbti_groups
        ])
        base_prompt += f"\n[MBTI 특성]\n{mbti_info}"
    
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
                # 각 모델에서 카피 생성
                results = {
                    model: generate_copy(prompt, model)
                    for model in ["gpt", "gemini", "claude"]
                }
                
                # 평가 수행
                evaluations = {
                    model: st.session_state.evaluator.evaluate(copy, model)
                    for model, copy in results.items()
                }
                
                # 결과 저장
                experiment_data = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "prompt": prompt,
                    "results": results,
                    "evaluations": evaluations,
                    "settings": {
                        "region": selected_region,
                        "generation": selected_generation,
                        "mbti": selected_mbti_groups
                    }
                }
                st.session_state.history.append(experiment_data)

with col2:
    st.subheader("📊 실험 결과")
    
    for idx, experiment in enumerate(reversed(st.session_state.history)):
        with st.expander(f"실험 {len(st.session_state.history)-idx}", expanded=idx==0):
            st.text(f"시간: {experiment['timestamp']}")
            
            for model in ["gpt", "gemini", "claude"]:
                result = experiment['results'][model]
                evaluation = experiment['evaluations'][model]
                
                st.markdown(f"""
                **{model.upper()}**
                ```
                {result}
                ```
                점수: {evaluation['score']}
                이유: {evaluation['reason']}
                """)
                
                fig = visualize_evaluation_results(evaluation)
                st.plotly_chart(fig, use_container_width=True)

# 실험 데이터 다운로드 버튼
if st.session_state.history:
    st.download_button(
        "📥 실험 데이터 다운로드",
        data=json.dumps(st.session_state.history, indent=2, ensure_ascii=False),
        file_name="experiment_results.json",
        mime="application/json"
    )
        
