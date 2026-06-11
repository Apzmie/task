import sys
from engine import MiniRedis

def run():
    # MiniRedis 인스턴스 생성 (데이터를 저장하고 관리할 엔진)
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

            # 1. 명령어 파싱 (입력을 공백 기준으로 분리)
            # 예: 'SET name Alice' -> ['SET', 'name', 'Alice']
            tokens = line.split()
            # 명령어는 대문자로 통일 (SET, get -> SET, GET)
            cmd = tokens[0].upper()
            # 명령어 뒤에 붙은 인자들
            args = tokens[1:]

            # 명령어 처리 결과 변수 초기화
            result = None

            # 2. 명령어 분기 처리 (각 명령어별 로직 실행)
            # SET: 키와 값을 저장
            if cmd == "SET":
                if len(args) < 2:
                    result = "(error) ERR wrong number of arguments for 'SET' command"
                else:
                    result = db.set(args[0], args[1])
            
            # GET: 특정 키의 값 조회
            elif cmd == "GET":
                if len(args) != 1:
                    result = "(error) ERR wrong number of arguments for 'GET' command"
                else:
                    result = db.get(args[0])
            
            # DEL: 특정 키와 데이터 삭제
            elif cmd == "DEL":
                if len(args) != 1:
                    result = "(error) ERR wrong number of arguments for 'DEL' command"
                else:
                    result = f"(integer) {db.delete(args[0])}"
            
            # EXISTS: 특정 키가 존재하는지 확인 (1: 있음, 0: 없음)
            elif cmd == "EXISTS":
                if len(args) != 1:
                    result = "(error) ERR wrong number of arguments for 'EXISTS' command"
                else:
                    exists = 1 if db.map.get(args[0]) else 0
                    result = f"(integer) {exists}"
            
            # DBSIZE: 현재 저장된 전체 키의 개수 반환
            elif cmd == "DBSIZE":
                result = f"(integer) {db.map.count}"

            # KEYS: 전체 키 목록 나열
            elif cmd == "KEYS":
                keys = []
                for bucket in db.map.table:
                    for item in bucket:
                        keys.append(f'"{item[0]}"')
                result = "\n".join(keys) if keys else "(empty array)"
            
            # CONFIG SET: 최대 메모리 제한 설정
            elif cmd == "CONFIG" and len(args) >= 2 and args[0].upper() == "SET" and args[1].upper() == "MAXMEMORY":
                try:
                    db.max_memory = int(args[2])
                    result = "OK"
                except:
                    result = "(error) ERR value is not an integer or out of range"
            
            # INFO: 메모리 사용량 및 통계 정보 출력
            elif cmd == "INFO" and len(args) >= 1 and args[0].upper() == "MEMORY":
                result = db.info_memory()

            # EXPIRE: 특정 키에 만료 시간(초) 설정
            elif cmd == "EXPIRE":
                if len(args) != 2:
                    result = "(error) ERR wrong number of arguments for 'EXPIRE' command"
                else:
                    try:
                        res = db.expire(args[0], int(args[1]))
                        result = f"(integer) {res}"
                    except:
                        result = "(error) ERR value is not an integer"
            
            # TTL: 특정 키의 남은 만료 시간 조회
            elif cmd == "TTL":
                if len(args) != 1:
                    result = "(error) ERR wrong number of arguments for 'TTL' command"
                else:
                    result = f"(integer) {db.ttl(args[0])}"
            
            # 알 수 없는 명령어 처리
            else:
                result = f"(error) ERR unknown command '{cmd}'"

            print(result)

        except EOFError:
            break
        except Exception as e:
            # 예기치 못한 에러 발생 시 처리
            print(f"(error) Internal Server Error: {e}")

if __name__ == "__main__":
    run()
