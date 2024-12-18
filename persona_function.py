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
    return selected_personas[:n
