
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
