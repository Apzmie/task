"""
models.py
---------
가계부 애플리케이션의 데이터 모델 정의 및 입력 검증 로직을 담당합니다.
데이터 모델의 구조(dataclass)와 필드별 제약 조건을 관리합니다.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class Transaction:
    """
    거래 내역(Transaction) 데이터 모델
    
    Attributes:
        id (str): 유일한 거래 식별자 (예: TX-000001)
        type (str): 거래 타입 ('income' 또는 'expense')
        date (str): 거래 날짜 (형식: YYYY-MM-DD)
        amount (int): 거래 금액 (1 이상의 양수 정수)
        category (str): 거래 카테고리
        memo (str): 거래에 대한 간단한 메모 (기본값: "")
        tags (str): 쉼표로 구분된 태그 문자열 (기본값: "")
    """
    id: str
    type: str
    date: str
    amount: int
    category: str
    memo: str = ""
    tags: str = ""


# =============================================================================
# 입력 검증 함수 (Input Validation)
# =============================================================================
# 각 함수는 사용자로부터 입력받은 문자열이 비즈니스 로직을 통과할 수 있는지 확인합니다.

def validate_date(date_str: str) -> bool:
    """
    주어진 문자열이 유효한 날짜 형식(YYYY-MM-DD)인지 검사합니다.
    
    Args:
        date_str (str): 사용자로부터 입력받은 날짜 문자열
        
    Returns:
        bool: 유효한 날짜이면 True, 아니면 False
    """
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_type(type_str: str) -> bool:
    """
    거래 타입이 'income' 또는 'expense' 중 하나인지 확인합니다.
    
    Args:
        type_str (str): 검사할 거래 타입
        
    Returns:
        bool: 올바른 타입이면 True, 아니면 False
    """
    return type_str in ["income", "expense"]

def validate_amount(amount_str: str) -> Optional[int]:
    """
    입력된 금액이 1 이상의 정수인지 확인하고, 정수로 변환하여 반환합니다.
    
    Args:
        amount_str (str): 입력된 금액 문자열
        
    Returns:
        Optional[int]: 유효한 양수이면 int 값, 잘못된 값이면 None
    """
    try:
        amount = int(amount_str)
        return amount if amount > 0 else None
    except ValueError:
        return None

def validate_category(category_str: str, allowed_categories: List[str]) -> bool:
    """
    입력된 카테고리가 사전에 정의된 카테고리 목록에 포함되어 있는지 확인합니다.
    
    Args:
        category_str (str): 검사할 카테고리 이름
        allowed_categories (List[str]): 허용되는 카테고리 리스트
        
    Returns:
        bool: 목록에 존재하면 True, 아니면 False
    """
    return category_str in allowed_categories
