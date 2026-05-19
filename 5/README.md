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
/home/mission-user/mission/agent-app-leak
2026-05-15 07:04:46,131 [INFO] [MemoryWorker] Current Heap: 250MB
2026-05-15 07:04:49,171 [INFO] [MemoryWorker] Current Heap: 275MB
2026-05-15 07:04:49,172 [CRITICAL] [MemoryGuard] Memory limit exceeded (275MB >= 256MB) / (Recommend Over 256MB)
2026-05-15 07:04:49,172 [CRITICAL] [MemoryGuard] Self-terminating process 4135 to prevent system instability.

/home/mission-user/mission/monitor.sh
07:04:45 | PID:4135 | 251956KB | 1.5% | 1.3%
07:04:46 | PID:4134 | 2176KB | 0.0% | 0.2%
07:04:46 | PID:4135 | 277560KB | 1.6% | 1.4%
07:04:47 | PID:4134 | 2176KB | 0.0% | 0.2%

#스트림 에디터(Stream Editor): 파일 내용을 한 줄씩 흘려보내며 중간에서 가로채 편집
sed -i 's/export MEMORY_LIMIT=.*/export MEMORY_LIMIT=512/g' /home/mission-user/.bashrc
source ~/.bashrc

2026-05-15 07:32:00,912 [INFO] [CpuWorker] Current Load: 50.93%
2026-05-15 07:32:01,013 [CRITICAL] [CpuWorker] CPU Threshold Violated! (50.93%).
```
```bash
1. Description (현상 설명)
agent-leak-app을 실행하면 메모리를 계속 먹다가 임계치인 256MB를 초과하면 MemoryGuard에 의해 강제 종료됨.

2. Evidence & Logs (증거 자료)
/home/mission-user/mission/agent-leak-app
2026-05-15 07:04:46,131 [INFO] [MemoryWorker] Current Heap: 250MB
2026-05-15 07:04:49,171 [INFO] [MemoryWorker] Current Heap: 275MB
2026-05-15 07:04:49,172 [CRITICAL] [MemoryGuard] Memory limit exceeded (275MB >= 256MB) / (Recommend Over 256MB)
2026-05-15 07:04:49,172 [CRITICAL] [MemoryGuard] Self-terminating process 4135 to prevent system instability.

#프로그램 자체를 유지하는 데 필요한 최소한의 숨은 메모리(약 2~3MB)가 더해졌기 때문에 수치가 다르게 나옴
/home/mission-user/mission/monitor.sh
07:04:45 | PID:4135 | 251956KB | 1.5% | 1.3%
07:04:46 | PID:4134 | 2176KB | 0.0% | 0.2%
07:04:46 | PID:4135 | 277560KB | 1.6% | 1.4%
07:04:47 | PID:4134 | 2176KB | 0.0% | 0.2%

3. Root Cause Analysis (원인 분석)
현상 분석: 앱 내부에서 데이터가 해제되지 않고 계속 쌓여 설정된 메모리 임계치(256MB)를 초과하는 메모리 누수가 발생했습니다.
시스템 동작: 시스템 전체가 멈추는 대형 장애를 막기 위해 내부 보호 엔진(MemoryGuard)이 개입하여 해당 프로세스를 선제적으로 강제 종료했습니다.

4. Workaround & Verification (조치 및 검증)
조치 내용: 환경변수 설정을 통해 MEMORY_LIMIT 값을 기존 256MB에서 512MB로 상향 조정하고 시스템에 적용했습니다.
검증 결과: 메모리 부족 종료(MemoryGuard)는 해결되었으나 이번에는 CPU 임계치 초과(CpuWorker)로 종료되었습니다.
2026-05-15 07:32:00,912 [INFO] [CpuWorker] Current Load: 50.93%
2026-05-15 07:32:01,013 [CRITICAL] [CpuWorker] CPU Threshold Violated! (50.93%).
```
```bash
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

