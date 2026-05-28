#repository.py
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

    # ==========================================
    # [추가] 거래 내역 최신순 스트리밍 조회 (제너레이터)
    # ==========================================
    def load_transactions_backward(self):
        """
        파일의 끝에서부터 위로 한 줄씩 읽어오는 제너레이터입니다.
        전체 파일을 메모리에 한 번에 올리지 않아 대용량 파일에 안전합니다.
        """
        if not os.path.exists(self.tx_file) or os.path.getsize(self.tx_file) == 0:
            return

        with open(self.tx_file, "rb") as f:
            # 파일의 맨 끝(EOF)으로 이동합니다.
            f.seek(0, os.SEEK_END)
            position = f.tell()
            buffer = bytearray()

            while position > 0:
                # 1바이트씩 앞으로 이동하며 읽습니다.
                position -= 1
                f.seek(position)
                chunk = f.read(1)

                if chunk == b'\n':
                    if buffer:
                        # 한 줄이 완성되면 파이썬 문자열로 디코딩 후 리턴(yield)
                        line = buffer[::-1].decode('utf-8').strip()
                        if line:
                            yield json.loads(line)
                        buffer = bytearray()
                else:
                    buffer.extend(chunk)

            # 파일의 맨 첫 번째 줄 처리
            if buffer:
                line = buffer[::-1].decode('utf-8').strip()
                if line:
                    yield json.loads(line)

    # ==========================================
    # [추가] 거래 내역 삭제 (원자적 파일 교체 방식)
    # ==========================================
    def delete_transaction(self, tx_id: str) -> bool:
        """
        지정한 ID의 거래를 삭제합니다.
        임시 파일에 삭제할 대상을 제외하고 쓴 뒤, 원본 파일과 교체합니다.
        삭제 성공 시 True, 해당 ID가 없으면 False를 반환합니다.
        """
        if not os.path.exists(self.tx_file):
            return False

        found = False
        tmp_file = self.tx_file + ".tmp"  # 임시 파일 경로 (transactions.jsonl.tmp)

        # 원본 파일을 읽어서 삭제할 것만 빼고 임시 파일에 적습니다.
        with open(self.tx_file, "r", encoding="utf-8") as f_in, \
             open(tmp_file, "w", encoding="utf-8") as f_out:
            
            for line in f_in:
                if line.strip():
                    tx = json.loads(line.strip())
                    if tx.get("id") == tx_id:
                        found = True  # 삭제할 ID를 찾았으므로 건너뜁니다!
                        continue
                    # 삭제할 ID가 아니면 임시 파일에 그대로 저장합니다.
                    f_out.write(json.dumps(tx, ensure_ascii=False) + "\n")

        if found:
            # 안전하게 임시 파일을 원본 파일 이름으로 덮어씁니다.
            os.replace(tmp_file, self.tx_file)
            return True
        else:
            # 지울 ID를 못 찾았다면 생성했던 임시 파일을 지우고 끝냅니다.
            if os.path.exists(tmp_file):
                os.remove(tmp_file)
            return False

    # ==========================================
    # [추가] 거래 내역 수정을 위한 데이터 단건 조회 및 전체 수정
    # ==========================================
    def find_transaction_by_id(self, tx_id: str) -> dict | None:
        """ID로 특정 거래 내역 하나를 찾아서 딕셔너리로 반환합니다."""
        if not os.path.exists(self.tx_file):
            return None
        
        with open(self.tx_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    tx = json.loads(line.strip())
                    if tx.get("id") == tx_id:
                        return tx
        return None

    def update_transaction(self, updated_tx: dict) -> bool:
        """
        수정된 거래 내역 데이터를 받아서 파일을 안전하게 갱신합니다.
        구조는 delete와 비슷하게 임시 파일을 만들어 원자적으로 교체합니다.
        """
        if not os.path.exists(self.tx_file):
            return False

        tmp_file = self.tx_file + ".tmp"
        found = False

        with open(self.tx_file, "r", encoding="utf-8") as f_in, \
             open(tmp_file, "w", encoding="utf-8") as f_out:
            
            for line in f_in:
                if line.strip():
                    tx = json.loads(line.strip())
                    if tx.get("id") == updated_tx["id"]:
                        # 옛날 데이터 대신 수정된 데이터를 집어넣습니다!
                        f_out.write(json.dumps(updated_tx, ensure_ascii=False) + "\n")
                        found = True
                    else:
                        f_out.write(json.dumps(tx, ensure_ascii=False) + "\n")

        if found:
            os.replace(tmp_file, self.tx_file)
            return True
        else:
            if os.path.exists(tmp_file):
                os.remove(tmp_file)
            return False
    def save_budget(self, month: str, amount: int):
        """
        특정 월의 예산을 저장합니다.
        임시 파일을 만들어 기존 데이터를 복사하다가, 동일한 달을 만나면 갱신합니다.
        동일한 달이 없다면 맨 마지막에 새로 추가한 뒤 원본 파일과 교체합니다.
        """
        tmp_file = self.bg_file + ".tmp"
        found = False
        new_budget = {"month": month, "amount": amount}

        # 1. 기존 예산 파일이 존재하면 내용을 한 줄씩 읽으며 임시 파일에 복사합니다.
        if os.path.exists(self.bg_file):
            with open(self.bg_file, "r", encoding="utf-8") as f_in, \
                 open(tmp_file, "w", encoding="utf-8") as f_out:
                for line in f_in:
                    if line.strip():
                        bg = json.loads(line.strip())
                        if bg.get("month") == month:
                            # 이미 똑같은 달의 예산이 있다면 사용자가 새로 입력한 금액으로 덮어씁니다.
                            f_out.write(json.dumps(new_budget, ensure_ascii=False) + "\n")
                            found = True
                        else:
                            # 다른 달의 예산 데이터는 그대로 유지합니다.
                            f_out.write(json.dumps(bg, ensure_ascii=False) + "\n")

        # 2. 파일이 아예 없었거나, 파일은 있지만 해당 월의 데이터가 없었다면 임시 파일 맨 뒤에 새로 적어줍니다.
        if not found:
            # 'a' 모드가 아니라 'w' 모드로 열어서, 아예 빈 파일에서 시작하거나 기존 임시 파일 뒤에 덧붙이도록 처리합니다.
            # (기존 임시 파일이 없었다면 새로 생성됨)
            mode = "a" if os.path.exists(tmp_file) else "w"
            with open(tmp_file, mode, encoding="utf-8") as f_out:
                f_out.write(json.dumps(new_budget, ensure_ascii=False) + "\n")

        # 3. 임시 파일 작성이 완벽히 끝났으므로 원본 파일과 바꿉니다.
        os.replace(tmp_file, self.bg_file)

    # ==========================================
    # [수정] 월별 예산 조회 기능 (안전성 강화)
    # ==========================================
    def get_budget_by_month(self, month: str) -> int | None:
        """지정한 월의 예산 설정 금액을 찾아서 숫자로 반환합니다. 없으면 None을 반환합니다."""
        if not os.path.exists(self.bg_file):
            return None

        with open(self.bg_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    bg = json.loads(line.strip())
                    # 앞뒤 혹시 모를 공백까지 완전히 제거하고 정확하게 비교합니다.
                    if bg.get("month").strip() == month.strip():
                        return int(bg.get("amount"))
        return None
    
    def is_category_used(self, category_name: str) -> bool:
        """
        가계부 내역 파일(transactions.jsonl)을 한 줄씩 읽으면서
        해당 카테고리를 사용 중인 거래가 단 하나라도 있는지 검사합니다.
        """
        if not os.path.exists(self.tx_file):
            return False

        with open(self.tx_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    tx = json.loads(line.strip())
                    if tx.get("category") == category_name:
                        return True  # 사용 중인 내역을 발견하면 즉시 True 반환!
        return False
    
    def append_to_csv(self, file_path: str, row: list, is_first: bool):
        """
        주어진 데이터 row를 CSV 파일에 한 줄 추가합니다.
        is_first가 True이면 파일의 맨 처음에 헤더(컬럼명)를 작성합니다.
        """
        # 첫 번째 줄을 쓸 때는 새 파일('w')을 만들고, 그 뒤로는 이어쓰기('a') 모드로 엽니다.
        mode = "w" if is_first else "a"
        with open(file_path, mode, encoding="utf-8", newline="") as f:
            import csv
            writer = csv.writer(f)
            writer.writerow(row)

    def save_transactions_bulk(self, tx_dict_list: list):
        """임포트된 가계부 내역 리스트를 원본 JSONL 파일 뒤에 한 번에 이어붙입니다."""
        with open(self.tx_file, "a", encoding="utf-8") as f:
            for tx_dict in tx_dict_list:
                f.write(json.dumps(tx_dict, ensure_ascii=False) + "\n")
