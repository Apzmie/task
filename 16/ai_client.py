# ai_client.py
import google.generativeai as genai

from config import (
    API_KEY,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_OUTPUT_TOKENS,
    validate_api_key,
)


def call_ai(
    prompt,
    model=DEFAULT_MODEL,
    temperature=DEFAULT_TEMPERATURE,
    max_output_tokens=DEFAULT_MAX_OUTPUT_TOKENS
):
    """
    Gemini API 호출 공통 함수
    """

    validate_api_key()

    try:
        # Gemini API Key 설정
        genai.configure(api_key=API_KEY)

        # 모델 생성
        gemini_model = genai.GenerativeModel(model)

        # 요청 생성
        response = gemini_model.generate_content(
            prompt,
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_output_tokens,
            }
        )

        return response.text.strip()

    except Exception as e:
        raise RuntimeError(
            f"[ERROR] Gemini API 호출 실패\n{e}"
        )


def generate_commit(
    prompt,
    model=DEFAULT_MODEL,
    temperature=DEFAULT_TEMPERATURE,
    max_output_tokens=DEFAULT_MAX_OUTPUT_TOKENS
):
    """
    커밋 메시지 생성
    """

    return call_ai(
        prompt,
        model,
        temperature,
        max_output_tokens
    )


def generate_pr(
    prompt,
    model=DEFAULT_MODEL,
    temperature=DEFAULT_TEMPERATURE,
    max_output_tokens=DEFAULT_MAX_OUTPUT_TOKENS
):
    """
    PR 제목/본문 생성
    """

    return call_ai(
        prompt,
        model,
        temperature,
        max_output_tokens
    )