class MinHeap:
    def __init__(self):
        # 힙을 저장할 리스트 (데이터를 담을 바구니)
        self.heap = []

    def size(self):
        # 힙에 데이터가 몇 개 있는지 확인
        return len(self.heap)

    def peek(self):
        # 맨 앞에 있는 '가장 빨리 만료될 데이터'를 살짝 엿봅니다.
        return self.heap[0] if self.heap else None

    def push(self, expire_at, key):
        # 새로운 데이터(만료시간, 이름표)를 힙 맨 뒤에 추가합니다.
        self.heap.append((expire_at, key))
        # 새로 들어온 녀석이 자기 자리를 찾아 위로 올라가게 합니다.
        self._heapify_up(len(self.heap) - 1)

    def pop(self):
        # 데이터를 하나 빼내어 삭제합니다.
        if self.size() == 0: return None
        if self.size() == 1: return self.heap.pop()
        
        # 맨 앞 데이터를 챙겨두고, 맨 뒤에 있던 데이터를 맨 앞으로 옮깁니다.
        root = self.heap[0]
        self.heap[0] = self.heap.pop()
        # 맨 앞으로 온 녀석이 자기 자리를 찾아 아래로 내려가게 합니다.
        self._heapify_down(0)
        return root

    def _heapify_up(self, idx):
        # 새로 추가된 데이터가 부모보다 '만료시간이 더 빠르면' 자리를 바꿉니다.
        while idx > 0:
            parent = (idx - 1) // 2 # 부모 위치 계산
            if self.heap[idx][0] < self.heap[parent][0]:
                # 부모보다 작으니 위치 교체
                self.heap[idx], self.heap[parent] = self.heap[parent], self.heap[idx]
                idx = parent
            else:
                break # 더 이상 올라갈 필요 없으면 멈춤

    def _heapify_down(self, idx):
        # 맨 앞으로 온 데이터가 자식들보다 '만료시간이 더 늦으면' 자리를 바꿉니다.
        smallest = idx
        left = 2 * idx + 1 # 왼쪽 자식
        right = 2 * idx + 2 # 오른쪽 자식

        # 왼쪽 자식이랑 비교
        if left < self.size() and self.heap[left][0] < self.heap[smallest][0]:
            smallest = left
        # 오른쪽 자식이랑 비교
        if right < self.size() and self.heap[right][0] < self.heap[smallest][0]:
            smallest = right

        # 자식이 나보다 작으면(더 빨리 만료되면) 자리를 바꿉니다.
        if smallest != idx:
            self.heap[idx], self.heap[smallest] = self.heap[smallest], self.heap[idx]
            self._heapify_down(smallest) # 계속 아래로 내려가며 확인
