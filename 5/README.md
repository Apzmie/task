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

2026-05-19 07:25:47,379 [INFO] [AgentWorker][Worker-Thread-1] Processing critical data in Memory A...
2026-05-19 07:25:47,379 [INFO] [AgentWorker][Worker-Thread-2] Establishing network connections in Pool B...
2026-05-19 07:25:49,382 [INFO] [AgentWorker][Worker-Thread-1] Need resource [Socket_Pool_B] to finish job.
2026-05-19 07:25:49,382 [INFO] [AgentWorker][Worker-Thread-1] WAITING for [Socket_Pool_B]... (Status: BLOCKED)
2026-05-19 07:25:49,382 [INFO] [AgentWorker][Worker-Thread-2] Need resource [Shared_Memory_A] to write logs.
2026-05-19 07:25:49,382 [INFO] [AgentWorker][Worker-Thread-2] WAITING for [Shared_Memory_A]... (Status: BLOCKED)
```
```bash
[Bug] CPU 사용률 초과로 인한 강제 종료 #2

1. Description (현상 설명)
애플리케이션 실행 후 CPU 부하가 임계치를 초과하면서 `CPU Threshold Violated` 및 `WATCHDOG: INITIATING EMERGENCY ABORT` 로그와 함께 프로세스가 강제 종료되었다.

2. Evidence & Logs (증거 자료)
2026-05-18 07:44:44,780 [INFO] [CpuWorker] Current Load: 46.14%
2026-05-18 07:44:47,885 [INFO] [CpuWorker] Current Load: 52.12%
2026-05-18 07:44:47,986 [CRITICAL] [CpuWorker] CPU Threshold Violated! (52.11999999999999%).

>>> [SYSTEM] WATCHDOG: INITIATING EMERGENCY ABORT (SIGTERM) <<<

07:44:21 | PID:6943 | 2172KB | 0.0% | 50.0%
07:44:21 | PID:6944 | 21676KB | 0.1% | 55.5%
07:44:22 | PID:6943 | 2172KB | 0.0% | 8.2%
07:44:22 | PID:6944 | 21676KB | 0.1% | 4.5%
07:44:23 | PID:6943 | 2172KB | 0.0% | 4.4%
07:44:23 | PID:6944 | 21724KB | 0.1% | 2.8%
07:44:24 | PID:6943 | 2172KB | 0.0% | 3.0%
07:44:24 | PID:6944 | 21724KB | 0.1% | 1.9%

3. Root Cause Analysis (원인 분석)
현상 분석: CPU 부하가 지속적으로 증가하며 내부 Watchdog 임계치를 초과하였다. 
시스템 동작: 애플리케이션의 Watchdog 보호 정책이 과도한 CPU 점유를 감지하고 프로세스를 종료하였다.

4. Workaround & Verification (조치 및 검증)
조치 내용: 환경변수 설정을 통해 CPU_MAX_OCCUPY 값을 기존 70MB에서 10MB로 조정하고 시스템에 적용했습니다.
검증 결과: CPU 임계치 초과(CpuWorker)는 해결되었으나 멀티스레드 환경에서 스레드끼리 서로 자원을 기다리며 멈추는 Deadlock 문제가 발생하였다.

2026-05-19 07:25:47,379 [INFO] [AgentWorker][Worker-Thread-1] Processing critical data in Memory A...
2026-05-19 07:25:47,379 [INFO] [AgentWorker][Worker-Thread-2] Establishing network connections in Pool B...
2026-05-19 07:25:49,382 [INFO] [AgentWorker][Worker-Thread-1] Need resource [Socket_Pool_B] to finish job.
2026-05-19 07:25:49,382 [INFO] [AgentWorker][Worker-Thread-1] WAITING for [Socket_Pool_B]... (Status: BLOCKED)
2026-05-19 07:25:49,382 [INFO] [AgentWorker][Worker-Thread-2] Need resource [Shared_Memory_A] to write logs.
2026-05-19 07:25:49,382 [INFO] [AgentWorker][Worker-Thread-2] WAITING for [Shared_Memory_A]... (Status: BLOCKED)

```
```bash
교착상태(Deadlock): 서로가 서로가 가진 걸 기다리면서 아무도 일을 못 하고 멈춰버린 상태
상호 배제: 하나의 자원은 동시에 여러 사람이 함께 사용할 수 없음
점유 대기: 하나 가지고 있으면서 다른 것도 기다림
비선점: 강제로 뺏을 수 없음
순환 대기: 서로가 원형으로 기다림

2026-05-19 07:25:47,379 [INFO] [AgentWorker][Worker-Thread-1] Processing critical data in Memory A...
2026-05-19 07:25:47,379 [INFO] [AgentWorker][Worker-Thread-2] Establishing network connections in Pool B...
2026-05-19 07:25:49,382 [INFO] [AgentWorker][Worker-Thread-1] Need resource [Socket_Pool_B] to finish job.
2026-05-19 07:25:49,382 [INFO] [AgentWorker][Worker-Thread-1] WAITING for [Socket_Pool_B]... (Status: BLOCKED)
2026-05-19 07:25:49,382 [INFO] [AgentWorker][Worker-Thread-2] Need resource [Shared_Memory_A] to write logs.
2026-05-19 07:25:49,382 [INFO] [AgentWorker][Worker-Thread-2] WAITING for [Shared_Memory_A]... (Status: BLOCKED)

04:39:51 | PID:309 | 21784KB | 0.1% | 0.2% (mem, cpu)
[THREAD STATUS]
    309     309 SNl+  0.2  0.1
    309     478 SNl+  0.0  0.1
    309     479 SNl+  0.0  0.1
-----------------------------------
S : Sleeping → 대기 상태 (CPU 안 쓰고 기다림)
N : Nice (low priority) → 낮은 우선순위로 실행됨
l : multi-threaded → 멀티스레드 프로세스
+ : foreground process → 현재 터미널에서 실행 중인 포그라운드 프로세스

프로세스(PID 309)는 종료되지 않았으나, 전체 CPU 사용률이 0.2% 수준으로 정체되었다.
또한 ps -L 결과에서 다수의 스레드(TID 478, 479)가 존재했지만, 각 스레드의 CPU 사용률이 0.0% 수준으로 유지되었다.
이는 스레드들이 정상 작업을 수행하지 못하고 대기 상태에 머물러 있음을 시사한다.

sed -i 's/export MULTI_THREAD_ENABLE=.*/export MULTI_THREAD_ENABLE=false/g' /home/mission-user/.bashrc
source /home/mission-user/.bashrc

2026-05-20 06:47:03,253 [INFO] [CpuWorker] Current Load: 10.00%
2026-05-20 06:47:05,356 [INFO] [CpuWorker] Cooldown complete (5.00%). Resuming load increase...
2026-05-20 06:47:05,774 [INFO] [MemoryWorker] Current Heap: 250MB
2026-05-20 06:47:06,358 [INFO] [CpuWorker] Current Load: 5.00%
2026-05-20 06:47:08,459 [INFO] [CpuWorker] Peak reached (10.00%). Starting cooldown...
2026-05-20 06:47:08,815 [INFO] [MemoryWorker] Current Heap: 275MB

06:47:13 | PID:825 | 328972KB | 2.0% | 1.6%
[THREAD STATUS]
    825     825 SNl+  0.1  2.0
    825     898 SNl+  1.3  2.0
    825     899 SNl+  0.2  2.0
-----------------------------------

#CPU와 메모리가 점진적으로 증가하다가 CPU 임계치(10%)에 도달하자 시스템이 자동으로 부하를 낮추는 제어가 동작한 상태
```
```bash
[Bug] 교착상태로 인한 무한 대기 상태 #3
1. Description (현상 설명)
Worker-Thread들이 자원 대기 상태에 빠져 작업이 멈춘 교착상태(Deadlock) 현상이 발생함

2. Evidence & Logs (증거 자료)
2026-05-19 07:25:47,379 [INFO] [AgentWorker][Worker-Thread-1] Processing critical data in Memory A...
2026-05-19 07:25:47,379 [INFO] [AgentWorker][Worker-Thread-2] Establishing network connections in Pool B...
2026-05-19 07:25:49,382 [INFO] [AgentWorker][Worker-Thread-1] Need resource [Socket_Pool_B] to finish job.
2026-05-19 07:25:49,382 [INFO] [AgentWorker][Worker-Thread-1] WAITING for [Socket_Pool_B]... (Status: BLOCKED)
2026-05-19 07:25:49,382 [INFO] [AgentWorker][Worker-Thread-2] Need resource [Shared_Memory_A] to write logs.
2026-05-19 07:25:49,382 [INFO] [AgentWorker][Worker-Thread-2] WAITING for [Shared_Memory_A]... (Status: BLOCKED)

04:39:51 | PID:309 | 21784KB | 0.1% | 0.2% (mem, cpu)
[THREAD STATUS]
    309     309 SNl+  0.2  0.1
    309     478 SNl+  0.0  0.1
    309     479 SNl+  0.0  0.1
-----------------------------------

3. Root Cause Analysis (원인 분석)
현상 분석: 각 Worker-Thread가 서로 다른 자원을 점유한 상태에서 상대 자원을 WAITING/BLOCKED 상태로 대기하고 있음이 확인됨
시스템 동작: OS는 각 스레드가 이미 점유한 자원을 해제하지 않은 상태에서 추가 자원을 요청하는 점유 대기 구조를 허용하여, 상호 배제·점유 대기·비선점·순환 대기 조건이 동시에 충족되며 Deadlock 상태가 유지됨

4. Workaround & Verification (조치 및 검증)
조치 내용: 환경변수 설정을 통해 MULTI_THREAD_ENABLE을 기존 True에서 False로 조정하고 시스템에 적용했습니다. true는 여러 스레드가 동시에 실행되며 자원을 서로 나눠 쓰고 기다리는 구조라 충돌이 생기고, false는 한 번에 하나씩 순서대로 처리해서 기다림 자체가 발생하지 않음
검증 결과: CPU와 메모리가 점진적으로 증가하다가 CPU 임계치(10%)에 도달하자 시스템이 자동으로 부하를 낮추는 제어가 동작하는 상태가 되었습니다.
2026-05-20 06:47:03,253 [INFO] [CpuWorker] Current Load: 10.00%
2026-05-20 06:47:05,356 [INFO] [CpuWorker] Cooldown complete (5.00%). Resuming load increase...
2026-05-20 06:47:05,774 [INFO] [MemoryWorker] Current Heap: 250MB
2026-05-20 06:47:06,358 [INFO] [CpuWorker] Current Load: 5.00%
2026-05-20 06:47:08,459 [INFO] [CpuWorker] Peak reached (10.00%). Starting cooldown...
2026-05-20 06:47:08,815 [INFO] [MemoryWorker] Current Heap: 275MB
```
