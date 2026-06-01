# task5
```bash
docker run -d --name linux-mission2 --privileged -p 20023:15034 ubuntu:24.04 sleep infinity
apt update && apt install -y python3 procps net-tools iproute2 curl adduser nano

adduser mission-user
mkdir -p /home/mission-user/mission/upload_files
mkdir -p /home/mission-user/mission/api_keys
mkdir -p /home/mission-user/mission/logs

chown -R mission-user:mission-user /home/mission-user/mission

#.bashrc에 환경변수 추가 (로그아웃 후 재접속해도 유지되도록)
cat <<EOF >> /home/mission-user/.bashrc
export AGENT_HOME=/home/mission-user/mission
export AGENT_PORT=15034
export AGENT_UPLOAD_DIR=\$AGENT_HOME/upload_files
export AGENT_KEY_PATH=\$AGENT_HOME/api_keys
export AGENT_LOG_DIR=\$AGENT_HOME/logs
export MEMORY_LIMIT=256
export CPU_MAX_OCCUPY=70
export MULTI_THREAD_ENABLE=true
EOF

#secret.key 생성
echo "agent_api_key_test" > /home/mission-user/mission/api_keys/secret.key

chmod +x /home/mission-user/mission/monitor.sh
chmod +x /home/mission-user/mission/agent-app-leak

su - mission-user
source ~/.bashrc

#스트림 에디터(Stream Editor): 파일 내용을 한 줄씩 흘려보내며 중간에서 가로채 편집
sed -i 's/export MEMORY_LIMIT=.*/export MEMORY_LIMIT=512/g' /home/mission-user/.bashrc
source ~/.bashrc
```
```bash
[Bug] 메모리 임계치 초과로 인한 강제 종료 #1

1. Description (현상 설명)
agent-leak-app을 실행하면 메모리를 계속 먹다가 임계치인 256MB를 초과하면 MemoryGuard에 의해 강제 종료됨.

2. Evidence & Logs (증거 자료)
/home/mission-user/mission/agent-leak-app
2026-05-21 05:21:08,633 [INFO] [MemoryWorker] Current Heap: 250MB
2026-05-21 05:21:11,673 [INFO] [MemoryWorker] Current Heap: 275MB
2026-05-21 05:21:11,673 [CRITICAL] [MemoryGuard] Memory limit exceeded (275MB >= 256MB) / (Recommend Over 256MB)
2026-05-21 05:21:11,673 [CRITICAL] [MemoryGuard] Self-terminating process 3372 to prevent system instability.
>>> [SYSTEM] SELF-TERMINATED (Memory Limit Exceeded) <<<

#프로그램 자체를 유지하는 데 필요한 최소한의 숨은 메모리(약 2~3MB)가 더해졌기 때문에 수치가 다르게 나옴
/home/mission-user/mission/monitor.sh
05:21:08 | PID:3371 | 2132KB | 0.0% | 0.3%
05:21:08 | PID:3372 | 251836KB | 1.5% | 1.2%
05:21:09 | PID:3371 | 2132KB | 0.0% | 0.3%
05:21:09 | PID:3372 | 277440KB | 1.6% | 1.3%

3. Root Cause Analysis (원인 분석)
현상 분석: 앱 내부에서 데이터가 해제되지 않고 계속 쌓여 설정된 메모리 임계치(256MB)를 초과하는 메모리 누수가 발생했습니다.
시스템 동작: 시스템 전체가 멈추는 대형 장애를 막기 위해 내부 보호 엔진(MemoryGuard)이 개입하여 해당 프로세스를 선제적으로 강제 종료했습니다.

4. Workaround & Verification (조치 및 검증)
조치 내용: 환경변수 설정을 통해 MEMORY_LIMIT 값을 기존 256MB에서 512MB로 상향 조정하고 시스템에 적용했습니다.
검증 결과: 메모리 부족 종료(MemoryGuard)는 해결되었으나 이번에는 CPU 임계치 초과(CpuWorker)로 종료되었습니다.
2026-05-21 05:31:15,441 [INFO] [CpuWorker] Current Load: 49.25%
2026-05-21 05:31:18,544 [INFO] [CpuWorker] Current Load: 56.65%
2026-05-21 05:31:18,646 [CRITICAL] [CpuWorker] CPU Threshold Violated! (56.65%).
>>> [SYSTEM] WATCHDOG: INITIATING EMERGENCY ABORT (SIGTERM) <<<

05:31:17 | PID:4187 | 2108KB | 0.0% | 0.4%
05:31:17 | PID:4188 | 21588KB | 0.1% | 1.0%
05:31:18 | PID:4187 | 2108KB | 0.0% | 0.4%
05:31:18 | PID:4188 | 21588KB | 0.1% | 0.9%
```
```bash
#`이는 `ps`가 프로세스 전체의 평균 CPU 사용률을 계산하는 반면, 애플리케이션 내부 Watchdog은 짧은 시간 동안의 순간 CPU 부하를 기준으로 판단하기 때문으로 보인다.

sed -i 's/export CPU_MAX_OCCUPY=.*/export CPU_MAX_OCCUPY=10/g' /home/mission-user/.bashrc
source ~/.bashrc
```
```bash
[Bug] CPU 사용률 초과로 인한 강제 종료 #2

1. Description (현상 설명)
애플리케이션 실행 후 CPU 부하가 임계치를 초과하면서 `CPU Threshold Violated` 및 `WATCHDOG: INITIATING EMERGENCY ABORT` 로그와 함께 프로세스가 강제 종료되었다.

2. Evidence & Logs (증거 자료)
2026-05-21 05:31:15,441 [INFO] [CpuWorker] Current Load: 49.25%
2026-05-21 05:31:18,544 [INFO] [CpuWorker] Current Load: 56.65%
2026-05-21 05:31:18,646 [CRITICAL] [CpuWorker] CPU Threshold Violated! (56.65%).
>>> [SYSTEM] WATCHDOG: INITIATING EMERGENCY ABORT (SIGTERM) <<<

>>> [SYSTEM] WATCHDOG: INITIATING EMERGENCY ABORT (SIGTERM) <<<

05:31:17 | PID:4187 | 2108KB | 0.0% | 0.4%
05:31:17 | PID:4188 | 21588KB | 0.1% | 1.0%
05:31:18 | PID:4187 | 2108KB | 0.0% | 0.4%
05:31:18 | PID:4188 | 21588KB | 0.1% | 0.9%

3. Root Cause Analysis (원인 분석)
현상 분석: CPU 부하가 지속적으로 증가하며 내부 Watchdog 임계치를 초과하였다. 
시스템 동작: 애플리케이션의 Watchdog 보호 정책이 과도한 CPU 점유를 감지하고 프로세스를 종료하였다.

4. Workaround & Verification (조치 및 검증)
조치 내용: 환경변수 설정을 통해 CPU_MAX_OCCUPY 값을 기존 70MB에서 10MB로 조정하고 시스템에 적용했습니다.
검증 결과: CPU 임계치 초과(CpuWorker)는 해결되었으나 멀티스레드 환경에서 스레드끼리 서로 자원을 기다리며 멈추는 Deadlock 문제가 발생하였다.

2026-05-21 06:40:05,790 [INFO] [AgentWorker][Worker-Thread-1] LOCK ACQUIRED: [Shared_Memory_A]. (Holding...)
2026-05-21 06:40:05,791 [INFO] [AgentWorker][Worker-Thread-2] LOCK ACQUIRED: [Socket_Pool_B]. (Holding...)
2026-05-21 06:40:07,793 [INFO] [AgentWorker][Worker-Thread-1] WAITING for [Socket_Pool_B]... (Status: BLOCKED)
2026-05-21 06:40:07,793 [INFO] [AgentWorker][Worker-Thread-2] WAITING for [Shared_Memory_A]... (Status: BLOCKED)

06:40:13 | PID:4952 | 21680KB | 0.1% | 0.4%
[THREAD STATUS]
   4952    4952 SNl+  0.3  0.1
   4952    5121 SNl+  0.0  0.1
   4952    5122 SNl+  0.0  0.1
```
```bash
S : Sleeping → 대기 상태 (CPU 안 쓰고 기다림)
N : Nice (low priority) → 낮은 우선순위로 실행됨
l : multi-threaded → 멀티스레드 프로세스
+ : foreground process → 현재 터미널에서 실행 중인 포그라운드 프로세스

교착상태(Deadlock): 서로가 서로가 가진 걸 기다리면서 아무도 일을 못 하고 멈춰버린 상태
상호 배제: 하나의 자원은 동시에 여러 사람이 함께 사용할 수 없음
점유 대기: 하나 가지고 있으면서 다른 것도 기다림
비선점: 강제로 뺏을 수 없음
순환 대기: 서로가 원형으로 기다림

sed -i 's/export MULTI_THREAD_ENABLE=.*/export MULTI_THREAD_ENABLE=false/g' /home/mission-user/.bashrc
source /home/mission-user/.bashrc

#CPU와 메모리가 점진적으로 증가하다가 CPU 임계치(10%)에 도달하자 시스템이 자동으로 부하를 낮추는 제어가 동작한 상태
```
```bash
[Bug] 교착상태로 인한 무한 대기 상태 #3
1. Description (현상 설명)
Worker-Thread들이 자원 대기 상태에 빠져 작업이 멈춘 교착상태(Deadlock) 현상이 발생함

2. Evidence & Logs (증거 자료)
2026-05-21 06:40:05,790 [INFO] [AgentWorker][Worker-Thread-1] LOCK ACQUIRED: [Shared_Memory_A]. (Holding...)
2026-05-21 06:40:05,791 [INFO] [AgentWorker][Worker-Thread-2] LOCK ACQUIRED: [Socket_Pool_B]. (Holding...)
2026-05-21 06:40:07,793 [INFO] [AgentWorker][Worker-Thread-1] WAITING for [Socket_Pool_B]... (Status: BLOCKED)
2026-05-21 06:40:07,793 [INFO] [AgentWorker][Worker-Thread-2] WAITING for [Shared_Memory_A]... (Status: BLOCKED)

06:40:13 | PID:4952 | 21680KB | 0.1% | 0.4%
[THREAD STATUS]
   4952    4952 SNl+  0.3  0.1
   4952    5121 SNl+  0.0  0.1
   4952    5122 SNl+  0.0  0.1

3. Root Cause Analysis (원인 분석)
현상 분석: 각 Worker-Thread가 서로 다른 자원을 점유한 상태에서 상대 자원을 WAITING/BLOCKED 상태로 대기하고 있음이 확인됨
시스템 동작: OS는 각 스레드가 이미 점유한 자원을 해제하지 않은 상태에서 추가 자원을 요청하는 점유 대기 구조를 허용하여, 상호 배제·점유 대기·비선점·순환 대기 조건이 동시에 충족되며 Deadlock 상태가 유지됨

4. Workaround & Verification (조치 및 검증)
조치 내용: 환경변수 설정을 통해 MULTI_THREAD_ENABLE을 기존 True에서 False로 조정하고 시스템에 적용했습니다. true는 여러 스레드가 동시에 실행되며 자원을 서로 나눠 쓰고 기다리는 구조라 충돌이 생기고, false는 한 번에 하나씩 순서대로 처리해서 기다림 자체가 발생하지 않음
검증 결과: CPU와 메모리가 점진적으로 증가하다가 CPU 임계치(10%)에 도달하자 시스템이 자동으로 부하를 낮추는 제어가 동작하는 상태가 되었습니다.
2026-05-21 06:57:37,766 [INFO] [CpuWorker] Current Load: 8.12%
2026-05-21 06:57:39,870 [INFO] [CpuWorker] Peak reached (10.00%). Starting cooldown...
2026-05-21 06:57:40,405 [INFO] [MemoryWorker] Current Heap: 200MB
2026-05-21 06:57:40,872 [INFO] [CpuWorker] Current Load: 10.00%
2026-05-21 06:57:42,974 [INFO] [CpuWorker] Cooldown complete (5.00%). Resuming load increase...
2026-05-21 06:57:43,444 [INFO] [MemoryWorker] Current Heap: 225MB
2026-05-21 06:57:43,976 [INFO] [CpuWorker] Current Load: 5.00%

06:57:43 | PID:5352 | 252148KB | 1.5% | 1.7%
[THREAD STATUS]
   5352    5352 SNl+  0.2  1.5
   5352    5425 SNl+  1.3  1.5
   5352    5426 SNl+  0.2  1.5
```
```bash
Q9. monitor.sh는 데이터를 어떻게 추출했나요?
pgrep으로 agent-app-leak 프로그램의 ID를 찾은 후, ps 명령어를 통해 1초마다 메모리와 CPU 정보를 추출하여 로그 파일에 저장했습니다.

Q10. CPU 사용률을 확인한 도구와 옵션의 의미는?
CPU 사용률을 확인한 도구는 ps 명령어이며, -o pcpu 옵션을 사용하여 CPU 사용률(%) 항목만 선택해 추출했습니다.

Q11. 프로세스가 멈춘 상태(Deadlock)는 어떻게 진단했나요?
프로그램이 죽지 않고 살아있는데 CPU 사용률이 0%로 지속되는 것을 확인했습니다. 스레드 상태를 조회(stat)했을 때, 일해야 하는 스레드들이 전부 S (Sleeping, 대기 상태)로 멈춰서 아무것도 안 하고 깨어나지 않는 것을 보고 데드락으로 판단했습니다.

Q12. 메모리 보호 정책(OOM Killer)이 프로세스를 강제 종료하는 근본 이유는?
리눅스 서버의 메모리가 100% 가득 차면 시스템 전체가 멈추는 대형 장애(크래시)가 발생합니다

Q13. CPU가 과점유될 때 단일 프로세스를 종료해야 하는 이유는?
특정 프로그램이 CPU를 100% 독점해 버리면, OS가 키보드/마우스 입력이나 네트워크 신호 등 다른 필수적인 작업들을 전혀 처리하지 못해 서버가 먹통(Hang)이 됩니다

Q14. 교착 상태(Deadlock)의 원리를 쉽게 설명한다면?
두 개 이상의 스레드가 서로 상대방이 가진 자원을 내놓으라고 버티며 무한히 대기하는 상태

Q15. 스레드 간의 꼬인 관계(순환 의존)를 어떻게 추적했나요?
애플리케이션 로그를 대조하여 Thread-1이 자원A를 붙잡고 자원B를 기다리는 순간, 동시에 Thread-2가 자원B를 붙잡고 자원A를 기다리는 서로 꼬리를 물고 늘어지는 대기 로그를 확인하여 추적했습니다.

Q16. 운영 서버 환경이라면 monitor.sh를 어떻게 개선할 것인가요?
자원 사용량이 임계치를 넘으면 즉시 담당자에게 경고 알림(Alert)을 보내고, 프로세스가 강제 종료되기 직전에 그 순간의 메모리 상태를 저장하는 파일을 자동으로 추출하도록 코드를 추가

Q17. 3가지 장애(메모리 초과, CPU 초과, 데드락) 중 가장 치명적인 것은?
데드락(Deadlock)입니다. 메모리나 CPU 초과는 시스템이 강제로 종료시켜주기라도 하지만, 데드락은 프로세스가 죽지도 않은 채 자원만 먹고 영원히 멈춰 있어서 모니터링 시스템이 장애를 감지하기 가장 어렵기 때문입니다.
예방책: 처음부터 자원을 가져오는 순서를 똑같이 맞추거나, 자원을 기다릴 때 일정 시간(Timeout)이 지나면 포기하고 빠져나오도록 코딩해야 합니다.

Q18. OOM(메모리 부족)과 데드락이 동시에 터지면 뭐부터 고치나요?
우선순위: OOM(메모리 부족)부터 무조건 먼저 해결해야 합니다.
이유: 데드락은 해당 프로그램 하나만 안 돌면 끝이지만, OOM은 리눅스 서버 전체를 다운시켜 그 서버에 있는 다른 멀쩡한 서비스나 데이터베이스까지 통째로 망가뜨리기 때문입니다.

Q19. 장애를 막기 위한 코드 레벨의 개선 방안은?
메모리 누수: 데이터를 쓰고 나면 반드시 메모리에서 지워주는 clear()나 close()를 명시하기.
CPU 과점유: 무한 루프(while) 안에 아주 잠깐이라도 쉬어가는 sleep() 코드를 넣어 CPU가 숨 쉴 틈 주기.
데드락: 무한정 기다리는 락 대신, 5초만 기다려보고 안 되면 포기하는 tryLock(timeout) 사용하기.

Q20. 이번 미션을 다시 한다면 다르게 접근할 점은? (회고)
설정값을 조절하는 수동적인 수습에서 벗어나, 프로그램 내부 코드를 분석하여 자원 낭비의 근본 원인을 찾는다
```
