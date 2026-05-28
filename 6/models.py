#models.py
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class Transaction:
    """거래 내역 데이터를 담는 그릇 (데이터 모델)"""
    id: str                  # 유일한 ID (예: TX-000001)
    type: str                # income 또는 expense
    date: str                # YYYY-MM-DD 형식
    amount: int              # 양수 정수
    category: str            # 카테고리 이름
    memo: str = ""           # 선택 사항 (기본값 빈 문자열)
    tags: str = ""           # 선택 사항 (기본값 빈 문자열, 쉼표 구분)


# ==========================================
# 초보자를 위한 안전한 입력 검증 함수들
# ==========================================

def validate_date(date_str: str) -> bool:
    """날짜가 YYYY-MM-DD 형식에 맞는지 검사합니다."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_type(type_str: str) -> bool:
    """타입이 income 또는 expense 중 하나인지 검사합니다."""
    return type_str in ["income", "expense"]

def validate_amount(amount_str: str) -> Optional[int]:
    """금액이 양수 정수(1 이상)인지 검사하고, 맞으면 int로 변환해 리턴합니다."""
    try:
        amount = int(amount_str)
        if amount > 0:
            return amount
        return None
    except ValueError:
        return None

def validate_category(category_str: str, allowed_categories: List[str]) -> bool:
    """입력한 카테고리가 허용된 등록 목록에 있는지 검사합니다."""
    return category_str in allowed_categories
