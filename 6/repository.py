import os
import json
from typing import List, Dict

class DataRepository:
    """파일 저장 및 초기화를 담당하는 클래스"""
    
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        
        # 파일 경로 설정 (JSONL 형식)
        self.tx_file = os.path.join(data_dir, "transactions.jsonl")
        self.cat_file = os.path.join(data_dir, "categories.jsonl")
        self.bg_file = os.path.join(data_dir, "budgets.jsonl")
        
        # 프로그램 실행 시 자동으로 초기화 진행
        self._initialize_storage()

    def _initialize_storage(self):
        """폴더와 파일이 없으면 자동 생성하고 초기 세팅을 진행합니다."""
        # 1. 저장 폴더가 없으면 생성
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            print(f"[안내] 데이터 저장 폴더가 생성되었습니다: {self.data_dir}")

        # 2. 거래 내역 파일이 없으면 생성
        if not os.path.exists(self.tx_file):
            with open(self.tx_file, "w", encoding="utf-8") as f:
                pass  # 빈 파일 만들기

        # 3. 예산 파일이 없으면 생성
        if not os.path.exists(self.bg_file):
            with open(self.bg_file, "w", encoding="utf-8") as f:
                pass  # 빈 파일 만들기

        # 4. 카테고리 파일 초기화 (안 A: 파일이 없거나 비어있으면 기본값 자동 생성)
        if not os.path.exists(self.cat_file) or os.path.getsize(self.cat_file) == 0:
            default_categories = ["food", "transport", "rent", "salary", "etc"]
            self.save_categories(default_categories)
            print(f"[안내] 초기 카테고리가 자동 생성되었습니다: {', '.join(default_categories)}")

    # ==========================================
    # 카테고리 읽고 쓰기 기능
    # ==========================================
    def load_categories(self) -> List[str]:
        """파일에서 카테고리 목록을 읽어옵니다."""
        categories = []
        if not os.path.exists(self.cat_file):
            return categories
            
        with open(self.cat_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    # json형태로 저장된 줄을 파이썬 딕셔너리로 변환
                    data = json.loads(line)
                    categories.append(data["name"])
        return categories

    def save_categories(self, categories: List[str]):
        """카테고리 목록을 파일에 덮어씁니다."""
        with open(self.cat_file, "w", encoding="utf-8") as f:
            for cat in categories:
                # 한 줄에 하나씩 dict -> json 문자열로 변환하여 저장
                f.write(json.dumps({"name": cat}, ensure_ascii=False) + "\n")

    # ==========================================
    # 거래 내역 추가 저장 기능
    # ==========================================
    def save_transaction(self, tx_dict: Dict):
        """새로운 거래 내역을 파일 끝에 추가(Append)합니다."""
        with open(self.tx_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(tx_dict, ensure_ascii=False) + "\n")
