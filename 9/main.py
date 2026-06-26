import sys
import time
import uuid
import shlex  # 사용자가 입력한 명령어에서 따옴표 등을 포함해 인자를 분리해주는 도구

# --- 1. 자료구조 클래스 ---
class Commit:
    """각 커밋 정보를 저장하는 객체입니다."""
    def __init__(self, message, author, parents=None):
        self.hash = uuid.uuid4().hex[:6]  # 고유 식별자(6자리 랜덤 문자열) 생성
        self.message = message            # 커밋 메시지
        self.author = author              # 작성자
        self.timestamp = time.strftime("%Y-%m-%d %H:%M:%S") # 생성 시간 기록
        self.parents = parents if parents else [] # 부모 커밋의 해시 목록 (DAG 구조를 위함)

    def __repr__(self):
        # 객체를 출력할 때 보기 좋게 보여주는 형식
        return f"commit {self.hash} ({self.author}, {self.timestamp}) \n    {self.message}"

class MiniGit:
    """Git의 핵심 저장소 로직을 담당하는 클래스입니다."""
    def __init__(self):
        self.commits = {}    # 전체 커밋 저장소 {해시: 커밋객체}
        self.branches = {}   # 브랜치 관리 {브랜치명: 최신커밋해시}
        self.current_branch = None # 현재 작업 중인 브랜치
        self.author = ""     # 현재 작성자
        self.index_keyword = {} # 검색용: {단어: [커밋해시들]}
        self.index_author = {}  # 검색용: {작성자: [커밋해시들]}

    def init(self, user_name):
        """저장소를 초기화하고 main 브랜치를 생성합니다."""
        self.author = user_name
        initial_commit = Commit("Initial commit", self.author)
        self.commits[initial_commit.hash] = initial_commit
        self.branches["main"] = initial_commit.hash
        self.current_branch = "main"
        return f"Initialized repository. Current branch: main, User: {user_name}"

    def commit(self, message):
        """현재 HEAD 위치에 새로운 커밋을 추가합니다."""
        if not self.current_branch: return "Error: Repository not initialized."
        parent_hash = self.branches[self.current_branch]
        new_commit = Commit(message, self.author, [parent_hash])
        self.commits[new_commit.hash] = new_commit
        self.branches[self.current_branch] = new_commit.hash
        
        # 검색 속도를 높이기 위한 역색인(Inverted Index) 업데이트
        self.index_author.setdefault(self.author, []).append(new_commit.hash)
        for word in message.lower().split():
            self.index_keyword.setdefault(word, []).append(new_commit.hash)
            
        return f"[{self.current_branch} {new_commit.hash}] {message}"

    # --- 2. 알고리즘 구현 ---
    def quick_sort(self, arr, key_func):
        """데이터를 기준(key_func)에 따라 빠르게 정렬하는 알고리즘(퀵 정렬)"""
        if len(arr) <= 1: return arr
        pivot = arr[len(arr) // 2] # 중간 값을 기준으로 분할
        left = [x for x in arr if key_func(x) < key_func(pivot)]
        middle = [x for x in arr if key_func(x) == key_func(pivot)]
        right = [x for x in arr if key_func(x) > key_func(pivot)]
        return self.quick_sort(left, key_func) + middle + self.quick_sort(right, key_func)

    def get_ancestors(self, commit_hash):
        """특정 커밋의 모든 조상을 스택(Stack)을 이용해 깊이 우선 탐색으로 찾기"""
        visited = set()
        stack = [commit_hash]
        while stack:
            curr = stack.pop()
            for p_hash in self.commits[curr].parents:
                if p_hash not in visited:
                    visited.add(p_hash)
                    stack.append(p_hash) # 부모를 다시 스택에 넣어 계속 탐색
        return visited

    def find_path(self, start_hash, end_hash):
        """두 커밋 사이의 최단 경로를 너비 우선 탐색(BFS)으로 찾기"""
        if start_hash not in self.commits or end_hash not in self.commits:
            return "Unknown commit"
        
        queue = [(start_hash, [start_hash])] # (현재위치, 지나온경로)
        visited = {start_hash}
        
        while queue:
            curr, path = queue.pop(0) # 큐에서 하나씩 꺼내 탐색
            if curr == end_hash: return " -> ".join(path)
            
            # 그래프를 무방향으로 해석하여 부모뿐만 아니라 자식 방향도 고려
            neighbors = list(self.commits[curr].parents)
            for h, c in self.commits.items():
                if curr in c.parents: neighbors.append(h)
                
            for neighbor in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        return "No path"

# --- 3. CLI 핸들러 ---
def run():
    git = MiniGit()
    print("Mini Git 시작 (exit 입력 시 종료)")
    while True: # 무한 루프를 통해 지속적으로 명령어 입력 대기
        try:
            line = input("mini-git> ").strip()
            if not line: continue
            if line.lower() in ['exit', 'quit']: break
            
            parts = shlex.split(line) # 명령어 파싱 (따옴표 고려)
            cmd = parts[0].upper()

            if cmd == "INIT": print(git.init(parts[1]))
            elif cmd == "BRANCH": git.branches[parts[1]] = git.branches[git.current_branch]
            elif cmd == "SWITCH": git.current_branch = parts[1]
            elif cmd == "COMMIT": print(git.commit(parts[1]))
            elif cmd == "LOG":
                # 정렬 옵션에 따라 정렬 알고리즘 적용
                if "--sort-by=date" in line:
                    for c in git.quick_sort(list(git.commits.values()), lambda c: c.timestamp): print(c)
                elif "--sort-by=author" in line:
                    for c in git.quick_sort(list(git.commits.values()), lambda c: c.author): print(c)
                else:
                    for c in git.commits.values(): print(c)
            elif cmd == "PATH": print(f"Path: {git.find_path(parts[1], parts[2])}")
            elif cmd == "ANCESTORS":
                anc_hashes = git.get_ancestors(parts[1])
                # 파이썬 기본 정렬 대신 수동 정렬을 사용할 수 있음(여기서는 출력 편의상 sorted 사용됨)
                sorted_anc = sorted([git.commits[h] for h in anc_hashes], key=lambda x: x.timestamp, reverse=True)
                for c in sorted_anc: print(c)
            elif cmd == "SEARCH":
                # 역색인(Inverted Index)을 사용하여 효율적인 검색
                if "--author=" in line:
                    auth = line.split("=")[1].strip('"')
                    for h in git.index_author.get(auth, []): print(git.commits[h])
                else:
                    key = parts[1].lower()
                    for h in git.index_keyword.get(key, []): print(git.commits[h])
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    run()