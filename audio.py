import random

# TTS 생성 함수 수정
def generate_tts(copy_text, file_name):
    try:
        # 4개의 음성 엔트리 중 랜덤 선택
        voice_options = ["alloy", "echo", "fable", "onyx"]
        selected_voice = random.choice(voice_options)
        st.info(f"🎤 선택된 목소리: {selected_voice}")

        # OpenAI TTS 요청
        response = client.audio.speech.create(
            model="tts-1",
            voice=selected_voice,  # 랜덤으로 선택된 목소리
            input=copy_text
        )
        audio_file_path = f"{file_name}.mp3"
        with open(audio_file_path, "wb") as audio_file:
            for chunk in response.iter_bytes():
                audio_file.write(chunk)
        return audio_file_path
    except Exception as e:
        st.error(f"TTS 생성 중 오류 발생: {str(e)}")
        return None

# 오디오 파일 재생 함수
def play_audio(file_path):
    audio_file = open(file_path, "rb")
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format="audio/mp3", start_time=0)


