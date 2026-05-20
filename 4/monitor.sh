#!/bin/bash

# 1. 환경 변수 및 경로 설정
# 크론탭 실행을 위해 기본 환경 변수를 불러옵니다.
source /etc/profile.d/agent_env.sh 2>/dev/null

DATE=$(date "+%Y-%m-%d %H:%M:%S")
AGENT_HOME="${AGENT_HOME:-/home/agent-admin/agent-app}"
AGENT_PORT="${AGENT_PORT:-15034}"
LOG_PATH="/var/log/agent-app/monitor.log"
APP_NAME="agent_app"

# 2. Health Check (프로세스 및 포트 검증)
# 프로세스 PID 확인
PID=$(pgrep -f "$APP_NAME" | tr '\n' ',' | sed 's/,$//')
if [ -z "$PID" ]; then
    echo "[$DATE] [ERROR] Process '$APP_NAME' not found" >> "$LOG_PATH"
    exit 1
fi

# [추가] ss 명령어를 이용한 TCP 15034 포트 리슨 상태 확인
# 0.0.0.0:15034 또는 *:15034 형태로 열려있는지 확인합니다.
PORT_LISTEN=$(ss -tulnp | grep -E "[: ]${AGENT_PORT} ")
if [ -z "$PORT_LISTEN" ]; then
    echo "[$DATE] [ERROR] Port ${AGENT_PORT} is not in LISTEN state" >> "$LOG_PATH"
    exit 1
fi

# 3. 방화벽 상태 점검 (비활성 시 경고만 출력, 스크립트는 계속 진행)
UFW_STATUS=$(sudo ufw status 2>&1)
if [[ "$UFW_STATUS" != *"Status: active"* ]]; then
    echo "[WARNING] Firewall is inactive"
fi

# 4. 자원 수집
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4}')
MEM_USAGE=$(free | grep Mem | awk '{print $3/$2 * 100.0}' | cut -d. -f1)
DISK_USED=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')

# 5. 임계값 경고 (awk 활용 안전 비교)
# CPU > 20%
[[ $(awk -v n1="$CPU_USAGE" -v n2="20" 'BEGIN{print (n1>n2)?1:0}') -eq 1 ]] && echo "[WARNING] CPU threshold exceeded ($CPU_USAGE%)"
# MEM > 10%
[[ $MEM_USAGE -gt 10 ]] && echo "[WARNING] MEM threshold exceeded ($MEM_USAGE%)"
# DISK > 80%
[[ $DISK_USED -gt 80 ]] && echo "[WARNING] DISK threshold exceeded ($DISK_USED%)"

# 6. 로그 기록
echo "[$DATE] PID:$PID CPU:$CPU_USAGE% MEM:$MEM_USAGE% DISK_USED:$DISK_USED%" >> "$LOG_PATH"

# 7. 로그 로테이션 (최대 10MB 기준, 최대 10개 파일 백업 순환 유지)
# 10485760 bytes = 10MB
if [ -f "$LOG_PATH" ] && [ $(stat -c%s "$LOG_PATH") -ge 10485760 ]; then
    
    # [보완] 가장 오래된 10번째 파일이 있다면 미리 삭제하여 10개 이하로 유지
    if [ -f "${LOG_PATH}.10" ]; then
        rm -f "${LOG_PATH}.10"
    fi

    # 9번부터 1번까지 기존 백업 파일들을 한 칸씩 뒤로 밀어냅니다.
    # 예: .9 -> .10,  .8 -> .9, ... .1 -> .2
    for i in 9 8 7 6 5 4 3 2 1; do
        if [ -f "${LOG_PATH}.${i}" ]; then
            mv "${LOG_PATH}.${i}" "${LOG_PATH}.$((i+1))"
        fi
    done

    # 현재 가득 찬 monitor.log 파일을 monitor.log.1 로 변경
    mv "$LOG_PATH" "${LOG_PATH}.1"

    # 다음 크론탭 실행 시 권한 문제가 생기지 않도록 새 파일 생성 및 권한 부여
    touch "$LOG_PATH"
    chmod 660 "$LOG_PATH"
fi
