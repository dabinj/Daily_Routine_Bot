# Linux VM 배포 메모

이 문서는 public repository에 포함되는 배포 템플릿입니다. 실제 서버 IP, SSH key 경로, 서버 계정명, Telegram token, chat id는 문서에 기록하지 않습니다.

## 준비

```bash
cd <APP_PARENT_DIR>
git clone <REPOSITORY_URL> Daily_Routine_Bot
cd Daily_Routine_Bot
printf '%s\n' '<TELEGRAM_BOT_TOKEN>' > .telegram.key
chmod 600 .telegram.key
python3 -m routine_bot.cli init-db
```

Telegram에서 `/start`를 보내면 봇이 사용할 대화방 식별자가 로컬 runtime 파일로 저장됩니다. 해당 파일은 git에 커밋하지 않습니다.

## systemd service 템플릿

`<SERVICE_USER>`와 `<APP_DIR>`는 실제 서버 환경에 맞게 서버에서만 치환합니다.

```bash
sudo tee /etc/systemd/system/daily-routine-bot.service >/dev/null <<'EOF'
[Unit]
Description=Daily Routine Telegram bot
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
User=<SERVICE_USER>
WorkingDirectory=<APP_DIR>
ExecStart=/usr/bin/python3 -m routine_bot.cli poll
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now daily-routine-bot.service
```

## 확인

```bash
systemctl status daily-routine-bot.service --no-pager -l
journalctl -u daily-routine-bot.service -n 50 --no-pager
```

## 중지

```bash
sudo systemctl stop daily-routine-bot.service
sudo systemctl disable daily-routine-bot.service
```

## Public repo 주의사항

다음 값은 서버 내부 또는 로컬 비밀 파일에만 둡니다.

- Telegram bot token
- Telegram chat id
- 서버 IP 또는 hostname
- SSH private key 경로
- 실제 Linux 계정명
- runtime DB와 state 파일
