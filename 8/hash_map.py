from doubly_linked_list import DoublyLinkedList, Node

class HashMap:
    def __init__(self, capacity=8):
        self.capacity = capacity # 창고의 전체 바구니 개수
        self.size = 0            # 현재 창고에 들어있는 물건 총 개수
        # 각 번호의 바구니마다 물건들을 관리할 '연결 리스트'를 하나씩 배치합니다.
        self.buckets = [DoublyLinkedList() for _ in range(self.capacity)]

    def _hash(self, key):
        # 이름표(key)를 받아서 몇 번 바구니에 넣을지 계산하는 '규칙'입니다.
        h = 5381
        for char in str(key):
            h = ((h << 5) + h) + ord(char)
        return h % self.capacity # 바구니 개수 안에서 번호를 정합니다.

    def put(self, key, value):
        # 1. 물건이 너무 많아지면(로드 팩터 0.75 초과), 바구니를 2배로 넓히고 이사 갑니다.
        if self.size / self.capacity > 0.75:
            self._resize()

        # 2. 내 이름표가 갈 바구니 번호를 찾습니다.
        idx = self._hash(key)
        bucket = self.buckets[idx]
        
        # 3. 같은 이름표를 가진 물건이 이미 바구니에 있는지 확인합니다.
        curr = bucket.head.next
        while curr != bucket.tail:
            if curr.key == key:
                curr.value = value # 이미 있다면 내용물만 새것으로 교체!
                return
            curr = curr.next
        
        # 4. 처음 들어오는 물건이면 바구니 뒤에 새로 매답니다.
        bucket.insert_back(Node(key, value))
        self.size += 1

    def get(self, key):
        # 1. 이름표를 보고 어느 바구니로 갈지 정합니다.
        idx = self._hash(key)
        bucket = self.buckets[idx]
        
        # 2. 바구니 안의 줄(연결 리스트)을 처음부터 끝까지 훑으며 찾습니다.
        curr = bucket.head.next
        while curr != bucket.tail:
            if curr.key == key:
                return curr.value # 찾았다면 물건을 반환!
            curr = curr.next
        return None # 끝까지 봐도 없다면 None을 반환합니다.

    def remove(self, key):
        idx = self._hash(key)
        bucket = self.buckets[idx]
        
        # 바구니 안에서 똑같은 이름표를 가진 물건을 찾습니다.
        curr = bucket.head.next
        while curr != bucket.tail:
            if curr.key == key:
                bucket.remove_node(curr) # 찾았으면 리스트에서 제거!
                self.size -= 1
                return True
            curr = curr.next
        return False # 못 찾았으면 지우기 실패

    def contains(self, key):
        # 물건이 있는지 확인합니다 (get이 None이 아니면 있는 것!)
        return self.get(key) is not None

    def keys(self):
        # 전체 바구니를 돌아다니며 모든 이름표를 리스트에 모읍니다.
        all_keys = []
        for bucket in self.buckets:
            curr = bucket.head.next
            while curr != bucket.tail:
                all_keys.append(curr.key)
                curr = curr.next
        return all_keys

    def _resize(self):
        # 1. 기존 창고의 모든 바구니를 비워둡니다.
        old_buckets = self.buckets
        
        # 2. 바구니 개수를 2배로 늘리고 새로운 창고를 짭니다.
        self.capacity *= 2
        self.size = 0
        self.buckets = [DoublyLinkedList() for _ in range(self.capacity)]
        
        # 3. 옛날 창고에 있던 물건들을 꺼내서, 새 바구니 규칙에 맞춰 다시 넣습니다.
        # (바구니 개수가 바뀌면, 해시 규칙에 따라 갈 곳도 바뀌기 때문입니다.)
        for bucket in old_buckets:
            curr = bucket.head.next
            while curr != bucket.tail:
                self.put(curr.key, curr.value)
                curr = curr.next

    def get_node(self, key):
        # 1. 어느 바구니에 있는지 계산
        idx = self._hash(key)
        bucket = self.buckets[idx]
        
        # 2. 바구니 안의 연결 리스트를 순회하며 키를 찾음
        curr = bucket.head.next
        while curr != bucket.tail:
            if curr.key == key:
                return curr  # 찾으면 노드 객체 자체를 반환
            curr = curr.next
        return None  # 없으면 None 반환
