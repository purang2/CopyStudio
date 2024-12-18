# 계절 상수 추가
SEASONS = {
    "봄": "spring",
    "여름": "summer",
    "가을": "autumn",
    "겨울": "winter"
}

PERSONA_CATEGORIES = {
    "literature": {"name": "문학가", "color": "#FDF2F8", "text_color": "#831843"},  # 밝은 핑크 배경 + 더 진한 버건디
    "entertainment": {"name": "연예인", "color": "#FCE7F3", "text_color": "#701A75"},  # 연한 핑크 배경 + 진한 퍼플
    "tech": {"name": "기업인", "color": "#EFF6FF", "text_color": "#1e3a8a"},  # 연한 파랑 배경 + 네이비
    "politics": {"name": "정치인", "color": "#F3F4F6", "text_color": "#1f2937"},  # 연한 회색 배경 + 차콜
    "fiction": {"name": "가상인물", "color": "#F5F3FF", "text_color": "#4c1d95"}  # 연한 보라 배경 + 진한 퍼플
}



# 도시 좌표 데이터
CITY_COORDINATES = {
    "강릉": {"lat": 37.7519, "lon": 128.8760},
    "경주": {"lat": 35.8562, "lon": 129.2245},
    "광주": {"lat": 35.1595, "lon": 126.8526},
    "대구": {"lat": 35.8714, "lon": 128.6014},
    "대전": {"lat": 36.3504, "lon": 127.3845},
    "부산 해운대": {"lat": 35.1628, "lon": 129.1639},
    "속초": {"lat": 38.2070, "lon": 128.5918},
    "수원": {"lat": 37.2636, "lon": 127.0286},
    "여수": {"lat": 34.7604, "lon": 127.6622},
    "용인": {"lat": 37.2410, "lon": 127.1775},
    "전주": {"lat": 35.8468, "lon": 127.1297}
}


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

# 모델 색상 및 로고 설정
MODEL_COLORS = {
    "gpt": "#10a37f",  # OpenAI 그린
    "gemini": "#4285f4",  # Google 블루
    "claude": "#b99778"  # Claude 베이지
}

# SVG 로고를 base64로 인코딩
LOGO_BASE64 = {
    "gpt": """data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MCIgaGVpZ2h0PSI0MCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwYXRoIGQ9Ik0xMiAyYTEwIDEwIDAgMSAwIDAgMjAgMTAgMTAgMCAxIDAgMC0yMHptMCA1YTUgNSAwIDAgMSA1IDUgNSA1IDAgMCAxLTUgNSA1IDUgMCAwIDEtNS01IDUgNSAwIDAgMSA1LTV6Ii8+PC9zdmc+""",  # 무한 매듭 SVG

    "gemini": """data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MCIgaGVpZ2h0PSI0MCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIj48cGF0aCBkPSJNMTIgMkw0IDZsOCA0IDgtNHoiLz48cGF0aCBkPSJNNCAxOGw4IDQgOC00Ii8+PHBhdGggZD0iTTQgNnY4bDggNCIvPjxwYXRoIGQ9Ik0yMCA2djhsLTggNCIvPjwvc3ZnPg==""",  # 별 모양 SVG

    "claude": """data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MCIgaGVpZ2h0PSI0MCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIj48cmVjdCB4PSI0IiB5PSI0IiB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHJ4PSIyIi8+PHBhdGggZD0iTTggOGg4Ii8+PHBhdGggZD0iTTggMTJoOCIvPjxwYXRoIGQ9Ik04IDE2aDgiLz48L3N2Zz4="""  # AI 텍스트 SVG
}


# 상단에 name_list 정의 추가
name_list = [
    # 시인 (국내/해외)
    "윤동주", "김소월", "정호승", "나태주", "백석", "정지용", 
    "헤르만 헤세", "마츠오 바쇼", "파블로 네루다", "셰익스피어",
    # 유명인 (국내)
    "김구라", "유재석", "김광석", "서태지", "이명박", "문재인", 
    "수지", "레드벨벳", "임영웅",
    # 유명인 (해외)
    "스티브 잡스", "일론 머스크", "마틴 루터 킹", "모차르트", "빈센트 반 고흐"
]
