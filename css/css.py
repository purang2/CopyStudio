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
