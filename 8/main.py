import sys
from engine import MiniRedis

def run():
    db = MiniRedis()
    print("Mini Redis initialized. Type 'exit' to quit.")

    while True:
        try:
            # 프롬프트 출력
            line = input("mini-redis> ").strip()
            if not line: continue
            
            # 종료 조건
            if line.lower() in ["exit", "quit"]:
                break

            # 명령어 파싱
            tokens = line.split()
            cmd = tokens[0].upper()
            args = tokens[1:]

            # 명령어 처리
            result = None

            if cmd == "SET":
                if len(args) < 2:
                    result = "(error) ERR wrong number of arguments for 'SET' command"
                else:
                    result = db.set(args[0], args[1])
            
            elif cmd == "GET":
                if len(args) != 1:
                    result = "(error) ERR wrong number of arguments for 'GET' command"
                else:
                    result = db.get(args[0])

            elif cmd == "DEL":
                if len(args) != 1:
                    result = "(error) ERR wrong number of arguments for 'DEL' command"
                else:
                    result = f"(integer) {db.delete(args[0])}"

            elif cmd == "EXISTS":
                if len(args) != 1:
                    result = "(error) ERR wrong number of arguments for 'EXISTS' command"
                else:
                    exists = 1 if db.map.get(args[0]) else 0
                    result = f"(integer) {exists}"

            elif cmd == "DBSIZE":
                result = f"(integer) {db.map.count}"

            elif cmd == "KEYS":
                # 전체 키 출력
                keys = []
                for bucket in db.map.table:
                    for item in bucket:
                        keys.append(f'"{item[0]}"')
                result = "\n".join(keys) if keys else "(empty array)"

            elif cmd == "CONFIG" and len(args) >= 2 and args[0].upper() == "SET" and args[1].upper() == "MAXMEMORY":
                try:
                    db.max_memory = int(args[2])
                    result = "OK"
                except:
                    result = "(error) ERR value is not an integer or out of range"

            elif cmd == "INFO" and len(args) >= 1 and args[0].upper() == "MEMORY":
                result = db.info_memory()

            elif cmd == "EXPIRE":
                if len(args) != 2:
                    result = "(error) ERR wrong number of arguments for 'EXPIRE' command"
                else:
                    try:
                        res = db.expire(args[0], int(args[1]))
                        result = f"(integer) {res}"
                    except:
                        result = "(error) ERR value is not an integer"

            elif cmd == "TTL":
                if len(args) != 1:
                    result = "(error) ERR wrong number of arguments for 'TTL' command"
                else:
                    result = f"(integer) {db.ttl(args[0])}"

            else:
                result = f"(error) ERR unknown command '{cmd}'"

            print(result)

        except EOFError:
            break
        except Exception as e:
            print(f"(error) Internal Server Error: {e}")

if __name__ == "__main__":
    run()