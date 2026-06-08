class Node:
    def __init__(self, key, value):
        self.key = key      # 이 데이터가 뭔지 알려주는 이름표
        self.value = value  # 진짜 저장하고 싶은 값
        self.prev = None    # 내 앞에 있는 친구가 누구인지 기억할 자리
        self.next = None    # 내 뒤에 있는 친구가 누구인지 기억할 자리

class DoublyLinkedList:
    def __init__(self):
        # 리스트의 시작과 끝에 가짜 노드를 두어, 
        # 처음이나 끝에 데이터를 넣고 뺄 때 코드를 복잡하지 않게 만듦
        self.head = Node(None, None) 
        self.tail = Node(None, None)
        self.head.next = self.tail
        self.tail.prev = self.head
        self.size = 0       # 지금 리스트에 데이터가 몇 개 들어있는지 센 것

    def insert_front(self, node):
        # 맨 앞에 새로운 데이터를 끼워 넣기
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node
        self.size += 1

    def insert_back(self, node):
        # 맨 뒤에 새로운 데이터를 끼워 넣기
        node.prev = self.tail.prev
        node.next = self.tail
        self.tail.prev.next = node
        self.tail.prev = node
        self.size += 1

    def remove_node(self, node):
        # 리스트에서 특정 데이터를 쏙 빼내고, 
        # 끊어진 앞뒤 데이터끼리 서로 손잡게 하기
        node.prev.next = node.next
        node.next.prev = node.prev
        self.size -= 1
        return node

    def remove_front(self):
        # 맨 앞에 있는 데이터를 지우기
        if self.size == 0: return None
        return self.remove_node(self.head.next)

    def remove_back(self):
        # 맨 뒤에 있는 데이터를 지우기
        if self.size == 0: return None
        return self.remove_node(self.tail.prev)

    def move_to_front(self, node):
        # 중간에 있는 어떤 데이터를 끄집어내서 맨 앞으로 옮기기
        self.remove_node(node)
        self.insert_front(node)