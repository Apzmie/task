# task4

- [x] SSH 포트 변경(20022) 및 Root 원격 접속 차단 설정 확인 내역
- [x] 방화벽(UFW 또는 firewalld) 활성화 및 20022/tcp, 15034/tcp만 허용 내역
- [x] 계정/그룹(agent-admin/dev/test, agent-common/core) 생성 확인 내역
- [x] 디렉토리 구조 및 권한(ACL 포함) 확인 내역
- [x] 앱 Boot Sequence 5단계 [OK] 및 “Agent READY” 확인 내역
- [x] monitor.sh 실행 결과(프로세스/포트/리소스/경고) 내역
- [x] /var/log/agent-app/monitor.log 누적 기록 확인(최근 라인) 내역
- [x] crontab 매분 실행 등록 및 자동 실행 확인(1분 후 로그 증가) 내역

## 1
```bash
docker run -d --name linux-mission --privileged -p 20022:20022 -p 15034:15034 ubuntu:24.04 sleep infinity
docker exec -it linux-mission /bin/bash
apt update && apt install -y nano ssh ufw systemctl iproute2 net-tools acl cron

nano /etc/ssh/sshd_config
Port 22 -> Port 20022, PermitRootLogin prohibit-password -> PermitRootLogin no #루트 로그인 불가능
service ssh start

#Socket Statistics의 약자로, 현재 서버의 네트워크 연결 상태
ss -tulnp | grep sshd
tcp   LISTEN 0      128          0.0.0.0:20022      0.0.0.0:*    users:(("sshd",pid=3948,fd=3))
tcp   LISTEN 0      128             [::]:20022         [::]:*    users:(("sshd",pid=3948,fd=4))

grep "PermitRootLogin" /etc/ssh/sshd_config
PermitRootLogin no
```

## 2
```bash
ufw allow 20022/tcp
ufw allow 15034/tcp
ufw enable
ufw status
Status: active

To                         Action      From
--                         ------      ----
20022/tcp                  ALLOW       Anywhere
15034/tcp                  ALLOW       Anywhere
20022/tcp (v6)             ALLOW       Anywhere (v6)
15034/tcp (v6)             ALLOW       Anywhere (v6)
#v6: 새 주소 체계
```

## 3
```bash
adduser agent-admin
adduser agent-dev
adduser agent-test

groupadd agent-common
groupadd agent-core

#user modify, appendGroup
usermod -aG agent-common agent-admin
usermod -aG agent-common agent-dev
usermod -aG agent-common agent-test

usermod -aG agent-core agent-admin
usermod -aG agent-core agent-dev

id agent-admin
uid=1000(agent-admin) gid=1000(agent-admin) groups=1000(agent-admin),1003(agent-common),1004(agent-core)

id agent-test
uid=1002(agent-test) gid=1002(agent-test) groups=1002(agent-test),1003(agent-common)
```

## 4
```bash
mkdir -p /home/agent-admin/agent-app/
mkdir -p /home/agent-admin/agent-app/api_keys
mkdir -p /home/agent-admin/agent-app/upload_files
mkdir -p /var/log/agent-app

chgrp agent-common /home/agent-admin/agent-app/upload_files
chgrp agent-core /home/agent-admin/agent-app/api_keys
chgrp agent-core /var/log/agent-app

chmod 770 /home/agent-admin/agent-app/upload_files
chmod 770 /home/agent-admin/agent-app/api_keys
chmod 770 /var/log/agent-app

#get file access control list
getfacl /home/agent-admin/agent-app/upload_files
getfacl: Removing leading '/' from absolute path names
# file: home/agent-admin/agent-app/upload_files
# owner: root
# group: agent-common
user::rwx
group::rwx
other::---

#list long directory
ls -ld /home/agent-admin/agent-app/api_keys
drwxrwx--- 1 root agent-core 0 May 11 06:39 /home/agent-admin/agent-app/api_keys

ls -ld /var/log/agent-app
drwxrwx--- 1 root agent-core 0 May 11 06:39 /var/log/agent-app
```

## 5
```bash
cat <<EOF > /etc/profile.d/agent_env.sh
export AGENT_HOME=/home/agent-admin/agent-app
export AGENT_PORT=15034
export AGENT_UPLOAD_DIR=\$AGENT_HOME/upload_files
export AGENT_KEY_PATH=\$AGENT_HOME/api_keys/t_secret.key
export AGENT_LOG_DIR=/var/log/agent-app
EOF

source /etc/profile.d/agent_env.sh

echo $AGENT_PORT
15034

echo "agent_api_key_test" > $AGENT_KEY_PATH

#동시부여, 하위 폴더/파일, 소유자 우선순위
chown -R agent-admin:agent-core /home/agent-admin/agent-app
chgrp agent-common /home/agent-admin/agent-app/upload_files
chmod 750 /home/agent-admin/agent-app/agent_app

su - agent-admin

~/agent-app/agent_app
>>> Starting Agent Boot Sequence...
[1/5] Checking User Account               [OK]
 ... Running as service user 'agent-admin' (uid=1001)
[2/5] Verifying Environment Variables     [OK]
 ... All required Envs correct
[3/5] Checking Required Files             [OK]
 ... Verified 'secret.key' with correct key string.
[4/5] Checking Port Availability          [OK]
 ... Port 15034 is available.
[5/5] Verifying Log Permission            [OK]
 ... Log directory is writable: /var/log/agent-app
------------------------------------------------------------
All Boot Checks Passed!
Agent READY
```

## 6
```bash
mkdir -p /home/agent-admin/agent-app/bin

chown agent-dev:agent-core /home/agent-admin/agent-app/bin/monitor.sh
chmod 750 /home/agent-admin/agent-app/bin/monitor.sh

su - agent-admin
~/agent-app/agent_app

#프로세스 id
pgrep -f "agent_app"
214
215

ss -tulnp | grep 15034
tcp   LISTEN 0      1            0.0.0.0:15034      0.0.0.0:*    users:(("agent_app",pid=222,fd=4))

ufw disable
/home/agent-admin/agent-app/bin/monitor.sh
[WARNING] Firewall is inactive

#1보다 높으면
CPU_INT=${CPU_USAGE%.*}
MEM_INT=${MEM_USAGE%.*}
DISK_INT=${DISK_USED%.*}
[ "$CPU_INT" -gt 1 ] && echo "[WARNING] CPU threshold exceeded ($CPU_USAGE%)"
[ "$MEM_INT" -gt 1 ] && echo "[WARNING] MEM threshold exceeded ($MEM_USAGE%)"
[ "$DISK_INT" -gt 1 ] && echo "[WARNING] DISK threshold exceeded ($DISK_USED%)"
[WARNING] CPU threshold exceeded (3.3%)
[WARNING] MEM threshold exceeded (5%)
```

## 7
```bash
#실시간
tail -f /var/log/agent-app/monitor.log
[2026-05-14 05:46:55] PID:454,455 CPU:0% MEM:4% DISK_USED:1%
[2026-05-14 06:05:27] PID: CPU:3.3% MEM:5% DISK_USED:1%
[2026-05-14 06:05:29] PID: CPU:3.3% MEM:5% DISK_USED:1%

# monitor.log 파일 내용 지우고 11MB 빈 파일로 덮어쓰기
dd if=/dev/zero of=/var/log/agent-app/monitor.log bs=1M count=11
/home/agent-admin/agent-app/bin/monitor.sh

# 별 5개면 "매월 매일 매시 매분마다 항상" 실행하라는 뜻
crontab -e
* * * * * /home/agent-admin/agent-app/bin/monitor.sh

service cron start

tail -f /var/log/agent-app/monitor.log
[2026-05-14 06:30:01] PID:12738,12739 CPU:0% MEM:4% DISK_USED:1%
[2026-05-14 06:31:01] PID:12738,12739 CPU:1.6% MEM:4% DISK_USED:1%
```

## 8
```bash
SSH 포트 변경 및 Root 접속 차단: 무작위 대입 공격(Brute Force)의 자동화 스캐너 표적에서 벗어나 공격 표면(Attack Surface)을 획기적으로 줄이고, 단 한 번의 해킹으로 시스템 최고 권한이 탈취되는 최악의 시나리오를 방지
agent-core 제한과 최소 권한 원칙: 특정 업무에 무관한 사용자의 접근을 원천 차단함으로써, 핵심 API 키 유출 및 로그 위변조 피해를 최소화
운영상의 경고/종료 분리 이유: 방화벽이나 임계치 초과는 서비스 연속성을 유지하면서 관리자가 인지하고 조치할 수 있는 여유(운영 가용성)를 확보하기 위함
>와 >> 차이: >는 기존 내용을 모두 지우고 새로 쓰지만, >>는 기존 데이터 뒤에 이어 쓰기

Nginx 전환 시 핵심 포인트: 감시 대상을 nginx 프로세스와 80/443 포트로 바꾸고, 로그는 Nginx 웹 로그로, 임계값은 트래픽 기준에 맞게 수정
프로세스 생존 중 포트 미개방: 설정 오류나 포트 중복이 원인이며, [에러 로그 확인] ➡️ [설정 파일 검증(nginx -t)] ➡️ [포트 점검(ss -lnpt)] 순으로 확인
디스크 풀 위험 시 대응: 즉시 오래된 로그를 압축하거나 삭제(단기)하고, logrotate를 적용해 주기적으로 자동 정리되도록 설정(중기)
```
