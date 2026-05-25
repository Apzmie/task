from dataclasses import dataclass, field
from typing import Optional, List

@dataclass
class Transaction:
    id: str                  # 유일한 식별자 (예: TX-00001)
    type: str                # 'income' 또는 'expense'
    date: str                # YYYY-MM-DD 형식
    amount: int              # 양수 정수
    category: str            # 카테고리 이름
    memo: Optional[str] = "" # 선택 입력 (기본값 빈 문자열)
    tags: List[str] = field(default_factory=list) # 선택 입력 (기본값 빈 리스트)

@dataclass
class Budget:
    month: str               # YYYY-MM 형식
    amount: int              # 예산 금액 (양수 정수)