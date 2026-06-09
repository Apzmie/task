import time
import sys
from doubly_linked_list import DoublyLinkedList, Node
from hash_map import HashMap
from heap import MinHeap


# [실행부] 이 클래스 아래에 실행 로직을 통합했습니다.
class MiniRedis:
    def __init__(self):
        self.kv_store = HashMap()
        self.lru_list = DoublyLinkedList()
        self.ttl_heap = MinHeap()
        
        self.maxmemory = 0
        self.used_memory = 0
        self.evicted_keys = 0

    # --- 기존 메서드들 유지 ---
    def _is_expired(self, node):
        if hasattr(node, 'expire_at') and node.expire_at is not None:
            if time.time() >= node.expire_at:
                return True
        return False

    def _delete_key(self, key):
        node = self.kv_store.get_node(key)
        if node:
            self.used_memory -= (len(node.key) + len(str(node.value)))
            self.kv_store.remove(key)
            self.lru_list.remove_node(node.lru_node)
            return True
        return False

    def SET(self, key, value):
        if self.kv_store.contains(key):
            self._delete_key(key)
        
        new_mem = len(key) + len(str(value))
        # OOM 체크: 단일 항목이 maxmemory를 초과하는 경우
        if self.maxmemory > 0 and new_mem > self.maxmemory:
            return "(error) OOM command not allowed when used_memory > 'maxmemory'"

        while self.maxmemory > 0 and (self.used_memory + new_mem) > self.maxmemory:
            lru_node = self.lru_list.remove_back()
            if not lru_node: break
            self.kv_store.remove(lru_node.key)
            self.used_memory -= (len(lru_node.key) + len(str(lru_node.value)))
            self.evicted_keys += 1
            
        node = Node(key, value)
        node.lru_node = Node(key, value)
        self.kv_store.put(key, value)
        self.lru_list.insert_front(node.lru_node)
        self.used_memory += new_mem
        return "OK"

    def GET(self, key):
        node = self.kv_store.get_node(key)
        if not node or self._is_expired(node):
            if node: self._delete_key(key)
            return "(nil)"
        self.lru_list.move_to_front(node.lru_node)
        return f'"{node.value}"'

    def DEL(self, key):
        return "(integer) 1" if self._delete_key(key) else "(integer) 0"

    def EXISTS(self, key):
        node = self.kv_store.get_node(key)
        if node and not self._is_expired(node):
            return "(integer) 1"
        return "(integer) 0"

    def DBSIZE(self):
        return f"(integer) {self.kv_store.size}"

    def KEYS(self):
        keys = self.kv_store.keys()
        if not keys: return "(empty array)"
        return "\n".join([f'{i+1}. "{k}"' for i, k in enumerate(keys)])

    def CONFIG_SET_MAXMEMORY(self, bytes_val):
        try:
            self.maxmemory = int(bytes_val)
            return "OK"
        except:
            return "(error) ERR value is not an integer or out of range"

    def INFO_MEMORY(self):
        return f"used_memory:{self.used_memory}\nmaxmemory:{self.maxmemory}\nevicted_keys:{self.evicted_keys}"

    # --- CLI 실행 루프 ---
    def run(self):
        print("Mini Redis CLI를 시작합니다. (exit 입력 시 종료)")
        while True:
            try:
                cmd_line = input("mini-redis> ").strip()
                if not cmd_line: continue
                
                tokens = cmd_line.split()
                cmd = tokens[0].upper()
                args = tokens[1:]

                if cmd in ["EXIT", "QUIT"]:
                    print("Bye!")
                    break
                
                # 명령어 파싱 및 실행
                if cmd == "SET" and len(args) == 2:
                    print(self.SET(args[0], args[1]))
                elif cmd == "GET" and len(args) == 1:
                    print(self.GET(args[0]))
                elif cmd == "DEL" and len(args) == 1:
                    print(self.DEL(args[0]))
                elif cmd == "EXISTS" and len(args) == 1:
                    print(self.EXISTS(args[0]))
                elif cmd == "DBSIZE":
                    print(self.DBSIZE())
                elif cmd == "KEYS":
                    print(self.KEYS())
                elif cmd == "CONFIG" and len(args) == 3 and args[0:2] == ["SET", "maxmemory"]:
                    print(self.CONFIG_SET_MAXMEMORY(args[2]))
                elif cmd == "INFO" and len(args) == 1 and args[0].lower() == "memory":
                    print(self.INFO_MEMORY())
                else:
                    print(f"(error) ERR unknown command or wrong arguments for '{cmd}'")
            except Exception as e:
                print(f"(error) ERR {e}")

if __name__ == "__main__":
    # 실행부
    app = MiniRedis()
    app.run()
