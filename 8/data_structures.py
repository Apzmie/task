# --- 1. 이중 연결 리스트 (Doubly Linked List) ---
class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class DoublyLinkedList:
    def __init__(self):
        # 머리와 꼬리에 더미 노드를 두어 삽입/삭제를 간편하게 함
        self.head = Node(None, None)
        self.tail = Node(None, None)
        self.head.next = self.tail
        self.tail.prev = self.head
        self.size = 0
    
    # 리스트의 맨 앞에 노드 추가
    def insert_front(self, node):
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node
        self.size += 1
        return node
    
    # 리스트의 맨 뒤에 노드 추가
    def insert_back(self, node):
        node.next = self.tail
        node.prev = self.tail.prev
        self.tail.prev.next = node
        self.tail.prev = node
        self.size += 1
        return node
    
    # 특정 노드를 리스트에서 제거
    def remove_node(self, node):
        if self.size == 0: return
        node.prev.next = node.next
        node.next.prev = node.prev
        self.size -= 1
    
    # 가장 앞의 노드 제거 후 반환
    def remove_front(self):
        if self.size == 0: return None
        target = self.head.next
        self.remove_node(target)
        return target
    
    # 가장 뒤의 노드 제거 후 반환
    def remove_back(self):
        if self.size == 0: return None
        target = self.tail.prev
        self.remove_node(target)
        return target
    
    # 특정 노드를 맨 앞으로 이동
    def move_to_front(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev
        self.size -= 1
        self.insert_front(node)

# --- 2. 해시맵 (HashMap) - 체이닝 방식 ---
class HashMap:
    def __init__(self, capacity=1024):
        self.capacity = capacity
        # 해시 충돌 시 같은 버킷에 리스트로 데이터를 담음
        self.table = [[] for _ in range(self.capacity)]
        self.count = 0
    
    # 입력된 키를 고유한 버킷 인덱스로 변환하는 해시 함수
    def _hash(self, key):
        h = 0
        for char in str(key):
            h = (h * 31 + ord(char)) % self.capacity
        return h
    
    # 키-값 데이터를 저장하거나 기존 값을 수정
    def put(self, key, value):
        idx = self._hash(key)
        bucket = self.table[idx]
        for item in bucket:
            if item[0] == key:
                item[1] = value
                return
        bucket.append([key, value])
        self.count += 1
        if self.count / self.capacity > 0.75:
            self._resize()
    
    # 키를 통해 저장된 값을 조회
    def get(self, key):
        idx = self._hash(key)
        for item in self.table[idx]:
            if item[0] == key:
                return item[1]
        return None
    
    # 키를 통해 데이터를 삭제
    def remove(self, key):
        idx = self._hash(key)
        bucket = self.table[idx]
        for i, item in enumerate(bucket):
            if item[0] == key:
                bucket.pop(i)
                self.count -= 1
                return True
        return False
    
    # 데이터가 너무 많아지면 버킷 개수를 2배로 늘리고 재배치
    def _resize(self):
        old_table = self.table
        self.capacity *= 2
        self.table = [[] for _ in range(self.capacity)]
        self.count = 0
        for bucket in old_table:
            for key, value in bucket:
                self.put(key, value)

    # 키가 해시맵에 있는지 확인
    def contains(self, key):
        idx = self._hash(key)
        for item in self.table[idx]:
            if item[0] == key:
                return True
        return False

    # 해시맵에 저장된 모든 키를 반환
    def keys(self):
        all_keys = []
        for bucket in self.table:
            for item in bucket:
                all_keys.append(item[0])
        return all_keys

    # 저장된 전체 데이터 개수 반환
    def size(self):
        return self.count

# --- 3. 최소 힙 (Min-Heap) - TTL 관리용 ---
class MinHeap:
    def __init__(self):
        self.heap = []
    
    # 힙에 담긴 데이터 개수 반환
    def size(self):
        return len(self.heap)

    # 새로운 만료 시간 데이터 추가 후 힙 정렬(Up)
    def push(self, expire_at, key):
        self.heap.append((expire_at, key))
        self._heapify_up(len(self.heap) - 1)

    # 가장 빨리 만료될 데이터를 제거하고 반환 후 힙 정렬(Down)
    def pop(self):
        if self.size() == 0: return None
        if self.size() == 1: return self.heap.pop()
        
        root = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._heapify_down(0)
        return root

    # 데이터를 꺼내지 않고 가장 빨리 만료될 데이터만 확인
    def peek(self):
        return self.heap[0] if self.heap else None

    #부모와 비교하며 위로 올라가며 제자리 찾기
    def _heapify_up(self, idx):
        while idx > 0:
            parent = (idx - 1) // 2
            if self.heap[idx][0] < self.heap[parent][0]:
                self.heap[idx], self.heap[parent] = self.heap[parent], self.heap[idx]
                idx = parent
            else:
                break

    # 자식과 비교하며 아래로 내려가며 제자리 찾기
    def _heapify_down(self, idx):
        while True:
            smallest = idx
            left = 2 * idx + 1
            right = 2 * idx + 2
            
            if left < self.size() and self.heap[left][0] < self.heap[smallest][0]:
                smallest = left
            if right < self.size() and self.heap[right][0] < self.heap[smallest][0]:
                smallest = right
            
            if smallest != idx:
                self.heap[idx], self.heap[smallest] = self.heap[smallest], self.heap[idx]
                idx = smallest
            else:
                break
