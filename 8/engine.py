import time
from data_structures import HashMap, DoublyLinkedList, MinHeap, Node

class MiniRedis:
    def __init__(self):
        # 1. 메인 저장소: 키를 넣으면 데이터(노드)를 O(1)로 바로 꺼내는 해시맵
        self.map = HashMap()  # key -> Node(key, value)

        # 2. LRU 순서 제어기: 최근에 쓰인 키는 맨 앞으로, 안 쓰인 키는 맨 뒤로 보내는 이중 연결 리스트
        self.lru_list = DoublyLinkedList()  # 최근 사용 순서

        # 3. 만료 시간 스케줄러: 가장 빨리 만료될 키를 맨 위로 정렬하는 최소 힙
        self.ttl_heap = MinHeap()  # (expire_at, key)

        # 4. 실시간 만료 시간 장부: 힙에서 꺼낸 만료 시간이 유효한지 검증하고, 현재 남은 시간을 조회하는 해시맵
        # 메인 저장소에 안전하게 잘 들어있는 새 데이터를 건드리는(지워버리는) 대참사를 막고 보호하기 위함
        self.ttl_map = HashMap()  # key -> expire_at (TTL 조회용)
        
        self.max_memory = 0
        self.used_memory = 0
        self.evicted_keys = 0
    
    # 키와 값의 글자 수를 더해서 메모리 크기(바이트)를 계산하는 함수
    def _get_size(self, key, value):
        return len(str(key)) + len(str(value))
    
    # 메모리 용량이 초과되었을 때, 허용 범위 안으로 들어올 때까지 가장 오래된 데이터(LRU)를 강제 삭제하는 함수
    def _evict_if_needed(self, new_key, new_value):
        item_size = self._get_size(new_key, new_value)

        # 들어올 데이터 자체가 최대 허용 용량보다 크면 저장 불가능(OOM 에러)
        if self.max_memory > 0 and item_size > self.max_memory:
            return False
       
        # (현재 용량 + 새 데이터 용량)이 최대 용량을 초과하는 동안 계속 반복    
        while self.max_memory > 0 and (self.used_memory + item_size > self.max_memory):
            # LRU 리스트의 맨 뒤(가장 오랫동안 사용되지 않은 노드)를 꺼냄
            target = self.lru_list.remove_back()
            if target:
                # 해당 키를 메인 해시맵, 만료 시간 해시맵에서 모두 지우고 용량 차감
                self.map.remove(target.key)
                self.ttl_map.remove(target.key)
                self.used_memory -= self._get_size(target.key, target.value)
                self.evicted_keys += 1  # 강제 삭제 카운트 증가
        return True

    # 시간이 지나 만료된 키들을 실시간으로 체크하여 삭제하는 청소 함수
    def _check_expired_keys(self):
        now = time.time()

        # 힙에 데이터가 있고, 가장 만료가 임박한 데이터의 만료 시간이 현재 시간보다 작거나 같으면 반복
        while self.ttl_heap.size() > 0 and self.ttl_heap.peek()[0] <= now:
            _, key = self.ttl_heap.pop()  # 힙에서 만료된 키를 꺼냄

            # 메인 해시맵에 실제로 존재하는지 확인 (덮어쓰기나 DEL로 사라지지 않았는지 검증)
            node = self.map.get(key)
            if node:
                # 진짜 만료된 것이 맞다면 모든 자료구조(LRU, 메인맵, TTL맵)에서 완전히 삭제하고 용량 차감
                self.lru_list.remove_node(node)
                self.map.remove(key)
                self.ttl_map.remove(key)
                self.used_memory -= self._get_size(key, node.value)

    # 데이터 저장 함수 (기존 키가 있으면 덮어쓰고, 용량 부족하면 LRU로 확보 후 저장)
    def set(self, key, value):
        self._check_expired_keys()  # 1. 만료된 키들 먼저 정리
        
        # 2. 이미 존재하는 키라면 덮어쓰기 위해 기존 데이터 완전 삭제 (기존 TTL도 함께 지워짐)
        if self.map.get(key):
            self.delete(key)
            
        # 3. 용량 체크 후 필요하다면 오래된 데이터를 지워 공간 확보 (실패 시 OOM 에러 리턴)
        if not self._evict_if_needed(key, value):
            return "(error) OOM command not allowed"

        # 4. 새로운 노드를 생성하여 메인 해시맵에 넣고, 최근에 사용되었으므로 LRU 리스트 맨 앞에 삽입
        node = Node(key, value)
        self.map.put(key, node)
        self.lru_list.insert_front(node)
        self.used_memory += self._get_size(key, value)  # 사용 중인 메모리 누적
        return "OK"

    # 데이터 조회 함수 (성공 시 해당 데이터를 LRU 리스트 맨 앞으로 이동시켜 최신화)
    def get(self, key):
        self._check_expired_keys()  # 조회 전 만료 여부 먼저 체크
        
        node = self.map.get(key)
        if not node:
            return "(nil)"  # 키가 없거나 이미 만료되어 삭제됐다면 (nil) 반환
        
        # 조회가 성공했으므로 최근 사용된 것으로 간주하여 LRU 리스트 맨 앞으로 이동
        self.lru_list.remove_node(node)
        self.lru_list.insert_front(node)
        return f'"{node.value}"'

    # 데이터 강제 삭제 함수
    def delete(self, key):
        node = self.map.get(key)
        if node:
            # 데이터가 존재하면 LRU 리스트, 메인 해시맵, 만료 해시맵에서 모두 지우고 용량 차감
            self.lru_list.remove_node(node)
            self.map.remove(key)
            self.ttl_map.remove(key)
            self.used_memory -= self._get_size(key, node.value)
            return 1  # 삭제 성공
        return 0  # 삭제할 데이터가 없음
    
    # 특정 키에 만료 시간(초)을 설정하는 함수
    def expire(self, key, seconds):
        self._check_expired_keys()
        if not self.map.get(key):
            return 0  # 존재하는 키가 아니면 설정 실패(0)
        
        # 현재 시간 + 요청한 초 = 만료될 절대 시간 계산
        expire_at = time.time() + int(seconds)
        self.ttl_heap.push(expire_at, key)  # 만료 스케줄러(최소 힙)에 등록
        self.ttl_map.put(key, expire_at)  # 실시간 만료 확인 장부에 최신 만료 시간 기록
        return 1  # 설정 성공

    # 특정 키의 남은 만료 시간을 초 단위로 계산해서 알려주는 함수
    def ttl(self, key):
        self._check_expired_keys()
        if not self.map.get(key):
            return -2  # 키 자체가 존재하지 않으면 -2 리턴
        expire_at = self.ttl_map.get(key)
        if not expire_at:
            return -1  # 키는 존재하나 만료 시간(타이머)이 설정되어 있지 않으면 -1 리턴
        return int(expire_at - time.time())  # (만료 예정 시간 - 현재 시간) 계산하여 남은 초 반환
    
    # 현재 메모리 현황 및 강제 통계를 문자열로 포맷팅하여 리턴하는 함수
    def info_memory(self):
        return f"used_memory:{self.used_memory} maxmemory:{self.max_memory} evicted_keys:{self.evicted_keys}"
