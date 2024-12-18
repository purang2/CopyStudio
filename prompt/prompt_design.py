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
