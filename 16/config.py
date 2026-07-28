# config.py
import os

# ==========================
# Gemini API 설정
# ==========================

# 환경변수에서 API Key 읽기
API_KEY = os.getenv("AI_API_KEY")

# 기본 모델
DEFAULT_MODEL = "gemini-2.5-flash"

# 기본 생성 옵션
DEFAULT_TEMPERATURE = 0.3
DEFAULT_MAX_OUTPUT_TOKENS = 1024


def validate_api_key():
    """
    API Key가 설정되어 있는지 확인한다.
    """
    if not API_KEY:
        raise EnvironmentError(
            "[ERROR] AI_API_KEY 환경변수가 설정되지 않았습니다.\n"
            "예) Windows(CMD): set AI_API_KEY=YOUR_KEY\n"
            "예) PowerShell: $env:AI_API_KEY='YOUR_KEY'\n"
            "예) macOS/Linux: export AI_API_KEY='YOUR_KEY'"
        )