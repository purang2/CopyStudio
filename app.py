import streamlit as st
import openai
from google.generativeai import GenerativeModel
import anthropic
import json
from datetime import datetime
import pandas as pd

# Page config
st.set_page_config(
    page_title="CopyStudio",
    page_icon="✨",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif;
    }
    
    .stButton button {
        background-color: #4CACBC;
        color: white;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        border: none;
        font-weight: 500;
    }
    
    .prompt-container {
        border: 2px solid #4CACBC;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    
    .result-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    
    .model-tag {
        font-size: 0.8em;
        padding: 3px 8px;
        border-radius: 15px;
        color: white;
    }
    
    .gpt-tag { background-color: #10a37f; }
    .gemini-tag { background-color: #4285f4; }
    .claude-tag { background-color: #8e44ad; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []
if 'region_info' not in st.session_state:
    st.session_state.region_info = ""
if 'mz_info' not in st.session_state:
    st.session_state.mz_info = ""

# Header
st.title("🎯 관광지 광고 카피 생성기")
st.markdown("#### MZ세대를 위한 맞춤형 광고 카피 생성 및 평가 시스템")

# Sidebar for document uploads
with st.sidebar:
    st.header("📄 문서 업로드")
    
    region_file = st.file_uploader("지역 정보 문서 (TXT)", type=['txt'])
    if region_file:
        st.session_state.region_info = region_file.read().decode('utf-8')
        st.success("지역 정보가 업로드되었습니다!")
        
    mz_file = st.file_uploader("MZ세대 여행 성향 문서 (TXT)", type=['txt'])
    if mz_file:
        st.session_state.mz_info = mz_file.read().decode('utf-8')
        st.success("MZ세대 정보가 업로드되었습니다!")

# Main content
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("💡 프롬프트 설정")
    
    default_prompt = """
다음 정보를 바탕으로 MZ세대를 위한 관광지 광고 카피를 생성해주세요:
1. 카피는 젊고 트렌디한 톤앤매너로 작성해주세요
2. 카피는 한 문장으로 작성해주세요
3. 이모지를 적절히 활용해주세요
4. MZ세대의 관심사와 여행 성향을 반영해주세요
"""
    
    prompt = st.text_area(
        "프롬프트를 수정해보세요",
        value=default_prompt,
        height=200,
        help="프롬프트를 수정하여 더 나은 광고 카피를 생성해보세요!"
    )

    if st.button("🎨 광고 카피 생성하기", use_container_width=True):
        with st.spinner("AI 모델이 광고 카피를 생성중입니다..."):
            # Simulate API calls (replace with actual API calls)
            results = {
                'gpt': "✨ 인생샷 건지러 떠나는 힙한 여행, 우리 동네가 기다려요!",
                'gemini': "🌊 MZ들의 핫플레이스, 우리 동네에서 트렌디한 일상 탈출!",
                'claude': "🎡 놀면서 배우는 우리 동네 스토리, 당신의 인스타를 채워드립니다"
            }
            
            # Evaluate copies
            evaluation_prompt = f"""
다음 광고 카피들을 0-100점 사이로 평가하고 그 이유를 설명해주세요.
평가 기준:
1. MZ세대 타겟팅 적절성
2. 메시지 전달력
3. 창의성과 참신성
4. 트렌디함

형식:
점수: [숫자]
이유: [설명]
"""
            
            # Simulate evaluations (replace with actual API calls)
            evaluations = {
                'gpt': {'score': 85, 'reason': "인생샷이라는 키워드와 힙한이라는 표현이 MZ세대의 관심사를 정확히 타겟팅했습니다."},
                'gemini': {'score': 88, 'reason': "핫플레이스와 트렌디란 단어 선택이 적절하며, 일상 탈출이라는 컨셉이 매력적입니다."},
                'claude': {'score': 82, 'reason': "인스타그램 연계 마케팅 접근이 좋으나, 다소 긴 문장 구조가 아쉽습니다."}
            }
            
            # Save to history
            st.session_state.history.append({
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'prompt': prompt[:20] + "...",
                'results': results,
                'evaluations': evaluations
            })

with col2:
    st.subheader("📊 생성 결과 기록")
    
    for idx, entry in enumerate(reversed(st.session_state.history)):
        with st.expander(f"📝 {entry['prompt']} ({entry['timestamp']})"):
            for model, copy in entry['results'].items():
                eval_data = entry['evaluations'][model]
                
                st.markdown(f"""
                <div class="result-card">
                    <span class="model-tag {model}-tag">{model.upper()}</span>
                    <p>{copy}</p>
                    <details>
                        <summary>평가 점수: {eval_data['score']}</summary>
                        <p>{eval_data['reason']}</p>
                    </details>
                </div>
                """, unsafe_allow_html=True)

# Display prompt history with rankings
st.subheader("🏆 프롬프트 성능 순위")
if st.session_state.history:
    history_df = pd.DataFrame([
        {
            '프롬프트': h['prompt'],
            '평균 점수': sum(h['evaluations'][m]['score'] for m in ['gpt', 'gemini', 'claude']) / 3,
            '최고 점수': max(h['evaluations'][m]['score'] for m in ['gpt', 'gemini', 'claude']),
            '생성 시간': h['timestamp']
        }
        for h in st.session_state.history
    ])
    
    st.dataframe(
        history_df.sort_values('평균 점수', ascending=False),
        use_container_width=True,
        hide_index=True
    )
