#!/bin/bash

# 로그 파일 경로 설정
LOG_FILE="/home/mission-user/mission/logs/monitor.log"

echo "시작 시간: $(date)" > $LOG_FILE
echo "시간 | 프로세스ID | 메모리사용량(KB) | 메모리(%) | CPU(%)" >> $LOG_FILE
echo "--------------------------------------------------------" >> $LOG_FILE

while true; do

    # PID 가져오기
    PIDS=$(pgrep -f agent-app-leak | tr '\n' ',' | sed 's/,$//')

    if [ -n "$PIDS" ]; then

        TIMESTAMP=$(date +%H:%M:%S)

        # 기존 프로세스 정보
        ps -p "$PIDS" -o pid,rss,pmem,pcpu --no-headers | while read -r pid rss pmem pcpu; do

            echo "$TIMESTAMP | PID:$pid | ${rss}KB | ${pmem}% | ${pcpu}%" \
            | tee -a $LOG_FILE

            # ===== 추가 부분 (Deadlock 분석용) =====
            echo "[THREAD STATUS]" | tee -a $LOG_FILE

            ps -L -p "$pid" \
            -o pid,tid,stat,pcpu,pmem --no-headers \
            | tee -a $LOG_FILE

            echo "-----------------------------------" \
            | tee -a $LOG_FILE
            # =====================================

        done

    else
        echo "$(date +%H:%M:%S) | [경고] agent-app-leak이 실행 중이 아닙니다." \
        | tee -a $LOG_FILE
    fi

    sleep 1

done
