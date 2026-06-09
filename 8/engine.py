import time
from data_structures import HashMap, DoublyLinkedList, MinHeap, Node

class MiniRedis:
    def __init__(self):
        self.map = HashMap()  # key -> Node(key, value)
        self.lru_list = DoublyLinkedList()  # 최근 사용 순서
        self.ttl_heap = MinHeap()  # (expire_at, key)
        self.ttl_map = HashMap()  # key -> expire_at (TTL 조회용)
        
        self.max_memory = 0
        self.used_memory = 0
        self.evicted_keys = 0

    def _get_size(self, key, value):
        return len(str(key)) + len(str(value))

    def _evict_if_needed(self, new_key, new_value):
        item_size = self._get_size(new_key, new_value)
        if self.max_memory > 0 and item_size > self.max_memory:
            return False # OOM
            
        while self.max_memory > 0 and (self.used_memory + item_size > self.max_memory):
            # LRU 삭제: tail.prev (가장 오래된 노드)
            target = self.lru_list.remove_back()
            if target:
                self.map.remove(target.key)
                self.ttl_map.remove(target.key)
                self.used_memory -= self._get_size(target.key, target.value)
                self.evicted_keys += 1
        return True

    def _check_expired_keys(self):
        now = time.time()
        while self.ttl_heap.size() > 0 and self.ttl_heap.peek()[0] <= now:
            _, key = self.ttl_heap.pop()
            # 만료 처리
            node = self.map.get(key)
            if node:
                self.lru_list.remove_node(node)
                self.map.remove(key)
                self.ttl_map.remove(key)
                self.used_memory -= self._get_size(key, node.value)

    def set(self, key, value):
        self._check_expired_keys()
        
        # 기존 키 삭제 (덮어쓰기)
        if self.map.get(key):
            self.delete(key)
            
        if not self._evict_if_needed(key, value):
            return "(error) OOM command not allowed"

        node = Node(key, value)
        self.map.put(key, node)
        self.lru_list.insert_front(node)
        self.used_memory += self._get_size(key, value)
        return "OK"

    def get(self, key):
        self._check_expired_keys()
        node = self.map.get(key)
        if not node:
            return "(nil)"
        
        # LRU 갱신
        self.lru_list.remove_node(node)
        self.lru_list.insert_front(node)
        return f'"{node.value}"'

    def delete(self, key):
        node = self.map.get(key)
        if node:
            self.lru_list.remove_node(node)
            self.map.remove(key)
            self.ttl_map.remove(key)
            self.used_memory -= self._get_size(key, node.value)
            return 1
        return 0

    def expire(self, key, seconds):
        self._check_expired_keys()
        if not self.map.get(key):
            return 0
        expire_at = time.time() + int(seconds)
        self.ttl_heap.push(expire_at, key)
        self.ttl_map.put(key, expire_at)
        return 1

    def ttl(self, key):
        self._check_expired_keys()
        if not self.map.get(key):
            return -2
        expire_at = self.ttl_map.get(key)
        if not expire_at:
            return -1
        return int(expire_at - time.time())

    def info_memory(self):
        return f"used_memory:{self.used_memory} maxmemory:{self.max_memory} evicted_keys:{self.evicted_keys}"