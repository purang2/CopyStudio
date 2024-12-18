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
            for file in sorted(region_path.glob("*.txt")):  # 가나다 순 정렬
                with open(file, "r", encoding="utf-8") as f:
                    docs["region"][file.stem] = f.read()
        
        # Load generation docs
        generation_path = docs_path / "generations"
        if generation_path.exists():
            for file in sorted(generation_path.glob("*.txt")):  # 가나다 순 정렬
                with open(file, "r", encoding="utf-8") as f:
                    docs["generation"][file.stem] = f.read()
        
        # Load individual MBTI files
        mbti_path = docs_path / "mbti"
        if mbti_path.exists():
            for mbti in sorted(MBTI_TYPES):  # MBTI도 가나다 순 정렬
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
        
        # 가나다 순 정렬된 딕셔너리 생성
        docs["region"] = dict(sorted(docs["region"].items()))
        docs["generation"] = dict(sorted(docs["generation"].items()))
        docs["mbti"] = dict(sorted(docs["mbti"].items()))
    
    except Exception as e:
        print(f"문서 로딩 중 오류: {str(e)}")
    
    return docs


def get_safe_persona_info(data: dict, field: str, default: any = '') -> any:
    """페르소나 데이터에서 안전하게 정보를 추출"""
    try:
        if not isinstance(data, dict):
            return default
        return data.get(field, default)
    except Exception:
        return default

