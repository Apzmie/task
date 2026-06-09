"""
data_structures.py
- 내장 자료구조(dict, set)를 사용하지 않고 밑바닥부터 구현한 자료구조 모듈
"""

# --- 1. 이중 연결 리스트 (Doubly Linked List) ---
class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class DoublyLinkedList:
    def __init__(self):
        # 더미 노드 사용
        self.head = Node(None, None)
        self.tail = Node(None, None)
        self.head.next = self.tail
        self.tail.prev = self.head
        self.size = 0

    def insert_front(self, node):
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node
        self.size += 1
        return node

    def remove_node(self, node):
        if self.size == 0: return
        node.prev.next = node.next
        node.next.prev = node.prev
        self.size -= 1

    def remove_back(self):
        if self.size == 0: return None
        target = self.tail.prev
        self.remove_node(target)
        return target

# --- 2. 해시맵 (HashMap) - 체이닝 방식 ---
class HashMap:
    def __init__(self, capacity=1024):
        self.capacity = capacity
        # 고정 길이 리스트 초기화 (체이닝을 위해 각 버킷을 리스트로 할당)
        self.table = [[] for _ in range(self.capacity)]
        self.count = 0

    def _hash(self, key):
        # 간단한 문자열 해시 함수
        h = 0
        for char in str(key):
            h = (h * 31 + ord(char)) % self.capacity
        return h

    def put(self, key, value):
        idx = self._hash(key)
        bucket = self.table[idx]
        for item in bucket:
            if item[0] == key:
                item[1] = value
                return
        bucket.append([key, value])
        self.count += 1
        
        # 로드 팩터 0.75 초과 시 확장 (간략 구현)
        if self.count / self.capacity > 0.75:
            self._resize()

    def get(self, key):
        idx = self._hash(key)
        for item in self.table[idx]:
            if item[0] == key:
                return item[1]
        return None

    def remove(self, key):
        idx = self._hash(key)
        bucket = self.table[idx]
        for i, item in enumerate(bucket):
            if item[0] == key:
                bucket.pop(i)
                self.count -= 1
                return True
        return False

    def _resize(self):
        old_table = self.table
        self.capacity *= 2
        self.table = [[] for _ in range(self.capacity)]
        self.count = 0
        for bucket in old_table:
            for key, value in bucket:
                self.put(key, value)

# --- 3. 최소 힙 (Min-Heap) - TTL 관리용 ---
class MinHeap:
    def __init__(self):
        self.heap = []

    def size(self):
        return len(self.heap)

    def push(self, expire_at, key):
        self.heap.append((expire_at, key))
        self._heapify_up(len(self.heap) - 1)

    def pop(self):
        if self.size() == 0: return None
        if self.size() == 1: return self.heap.pop()
        
        root = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._heapify_down(0)
        return root

    def peek(self):
        return self.heap[0] if self.heap else None

    def _heapify_up(self, idx):
        while idx > 0:
            parent = (idx - 1) // 2
            if self.heap[idx][0] < self.heap[parent][0]:
                self.heap[idx], self.heap[parent] = self.heap[parent], self.heap[idx]
                idx = parent
            else:
                break

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