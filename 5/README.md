# task5
```bash
docker run -d --name linux-mission2 --privileged -p 20023:15034 ubuntu:24.04 sleep infinity
apt update && apt install -y python3 procps net-tools iproute2 curl adduser nano

adduser mission-user
mkdir -p /home/mission-user/mission/upload_files
mkdir -p /home/mission-user/mission/api_keys
mkdir -p /home/mission-user/mission/logs

chown -R mission-user:mission-user /home/mission-user/mission
su - mission-user

#.bashrc에 환경변수 추가 (로그아웃 후 재접속해도 유지되도록)
cat <<EOF >> ~/.bashrc
export AGENT_HOME=/home/mission-user/mission
export AGENT_PORT=15034
export AGENT_UPLOAD_DIR=\$AGENT_HOME/upload_files
export AGENT_KEY_PATH=\$AGENT_HOME/api_keys
export AGENT_LOG_DIR=\$AGENT_HOME/logs
export MEMORY_LIMIT=256
export CPU_MAX_OCCUPY=70
export MULTI_THREAD_ENABLE=true
EOF

#환경변수 즉시 적용
source ~/.bashrc

#secret.key 생성
echo "agent_api_key_test" > $AGENT_HOME/api_keys/secret.key

chmod +x /home/mission-user/mission/monitor.sh
chmod +x /home/mission-user/mission/agent-app-leak

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

#맨 처음 켜질 때 뿜었던 엄청난 폭주 수치가 시간이 흐르면서 누적 평균 계산에 의해 점점 희석되어 낮아짐
```

