# Daily Routine Bot

Daily Routine Bot은 Telegram을 통해 하루 루틴을 정해진 시간에 질문하고, 사용자의 선택형 또는 자유 입력형 답변을 날짜별로 저장하는 개인용 routine tracker입니다.

이 저장소는 public repository로 관리할 수 있도록 설계되었습니다. 실제 bot token, chat id, 서버 IP, SSH key 경로, 개인 서버 계정 정보는 저장소에 포함하지 않습니다.

## 주요 기능

- 요일 기반 루틴 질문 스케줄
- 정해진 시간에 Telegram으로 자동 질문 발송
- 선택형 답변과 자유 입력형 답변 저장
- 선택형 질문의 Telegram reply keyboard 지원
- 조회/상태 변경용 Telegram 메인 메뉴 버튼
- Telegram 앱 명령어 메뉴 설정
- 질문 대기 상태 관리
- 출근/퇴근/음주 상태에 따른 조건부 질문
- 퇴근 예정시간 입력값 기준 동적 퇴근 확인
- 아침 시작, 퇴근, 운동, 음주, 취침 루틴에 맞춘 짧은 코칭 메시지
- `/skip`으로 현재 질문 건너뛰기
- `/pause`, `/resume`으로 자동 질문 일시 중지/재개
- SQLite 기반 일별 루틴 기록 저장
- `/today`로 오늘 기록 조회
- `/week`로 최근 7일 기록 요약
- `/record`로 수동 기록 추가 또는 수정
- Linux VM 또는 Oracle Cloud 배포용 systemd 템플릿 제공

## 기본 루틴

루틴 스케줄은 `config/routine_schedule.json`에서 관리합니다.

| 시간 | 항목 | 방식 | 설명 |
| --- | --- | --- | --- |
| 07:00 | 기상시간 | 선택/입력 | 실제 기상시간 기록 |
| 07:30 | 출근 예정 유무 | 선택 | 출근, 재택, 휴무, 연차 |
| 08:00 | 출근시간 | 선택/입력 | 출근 예정 또는 실제 출근시간 |
| 12:00 | 점심식사 메뉴 | 선택/입력 | 점심 메뉴 기록 |
| 14:00 | 퇴근 예정시간 | 선택/입력 | 당일 퇴근 예정시간 |
| 18:00 | 퇴근 여부 확인 | 선택 | 예정대로 퇴근했는지 확인 |
| 18:30 | 연장근무 이유 | 선택/입력 | 늦어진 경우 사유 기록 |
| 19:30 | 저녁 식사 | 선택/입력 | 저녁 시간과 메뉴 |
| 21:00 | 저녁 운동 여부 | 선택 | 운동 여부 기록 |
| 21:30 | 음주 여부 | 선택 | 음주 여부 기록 |
| 21:35 | 음주량 | 선택/입력 | 마신 경우 양 기록 |
| 22:30 | 내일 기상 예정시간 | 선택/입력 | 다음날 목표 기상시간 |
| 23:00 | 취침시간 | 선택/입력 | 실제 또는 예정 취침시간 |

## Telegram 명령어

| 명령어 | 기능 |
| --- | --- |
| `/start` | 봇 시작 및 현재 대화방 등록 |
| `/help` | 사용 가능한 명령어 표시 |
| `/today` | 오늘 루틴 기록 조회 |
| `/week` | 최근 7일 루틴 요약 |
| `/fields` | 수동 기록 가능한 항목 표시 |
| `/record <항목> <내용>` | 특정 항목을 수동으로 기록 |
| `/skip` | 현재 대기 중인 질문 건너뛰기 |
| `/cancel` | 현재 대기 중인 질문 취소 |
| `/pause` | 정해진 시간의 자동 질문 일시 중지 |
| `/resume` | 자동 질문 재개 |
| `/status` | 봇 상태와 대기 질문 확인 |

예시:

```text
/record lunch_menu 김치찌개
/record bed_time 23:40
/today
/week
```

## 메시지 흐름

봇은 설정된 시간마다 아직 발송하지 않은 질문이 있는지 확인합니다. 질문이 발송되면 해당 질문은 pending 상태가 되고, 사용자의 다음 일반 메시지를 답변으로 저장합니다.

선택형 질문은 Telegram reply keyboard와 번호 입력을 모두 지원합니다. 조회와 상태 변경은 메인 메뉴 버튼으로 사용할 수 있습니다.

```text
출근 예정이신가요?
1. 출근
2. 재택
3. 휴무
4. 연차
```

사용자가 `1`을 입력하거나 Telegram 버튼에서 `출근`을 선택하면 `출근`으로 저장됩니다. 번호 대신 직접 텍스트를 입력해도 기록됩니다.

평소에는 다음 메인 메뉴가 표시됩니다.

```text
오늘 기록 | 최근 7일
상태 | 항목 보기
일시 중지 | 다시 시작
```

## 조건부 질문

현재 스케줄은 선행 답변에 따라 다음 질문을 자동으로 생략합니다.

| 조건 | 동작 |
| --- | --- |
| 출근 예정 유무가 `출근`이 아님 | 출근시간, 퇴근 예정시간, 퇴근 확인, 연장근무 이유 질문 생략 |
| 퇴근 확인이 `예` | 연장근무 이유 질문 생략 |
| 음주 여부가 `아니오` | 음주량 질문 생략 |

퇴근 확인 질문은 고정 18:00이 아니라 사용자가 입력한 퇴근 예정시간을 기준으로 발송합니다. 예를 들어 `18:00`, `18시`, `오후 6시`, `6시` 입력을 지원합니다.

## 루틴 코칭

이 봇은 단순 기록뿐 아니라 루틴을 건강하게 유지하도록 짧은 피드백을 제공합니다.

| 상황 | 메시지 방향 |
| --- | --- |
| 아침 기상 | 하루 시작을 긍정적으로 열고 물/가벼운 움직임을 유도 |
| 출근 계획 | 오늘의 우선순위 하나를 정하도록 유도 |
| 퇴근 예정시간 | 일을 닫을 기준을 정하도록 유도 |
| 예정시간 퇴근 실패 | 연장근무 이유를 기록해 반복 패턴을 찾도록 유도 |
| 운동 미실시 | 부담 없는 3분 스트레칭 제안 |
| 음주 | 수분 섭취와 수면 시간 유지 유도 |
| 취침 | 화면을 내려놓고 수면으로 전환하도록 유도 |

## 저장 구조

```text
Daily_Routine_Bot/
├── config/
│   ├── development_plan.md
│   ├── feature_design.md
│   ├── oracle_deploy.md
│   └── routine_schedule.json
├── routine_bot/
│   ├── cli.py
│   ├── config.py
│   ├── messages.py
│   ├── schedule.py
│   ├── storage.py
│   └── telegram.py
├── var/
│   ├── routine.sqlite3
│   └── state.json
└── README.md
```

## 데이터 저장

SQLite DB는 runtime 디렉토리의 `routine.sqlite3`에 생성됩니다. 저장 단위는 날짜, 항목, 값입니다.

| date | field | value |
| --- | --- | --- |
| 2026-08-25 | wake_time | 07:10 |
| 2026-08-25 | work_plan | 출근 |
| 2026-08-25 | lunch_menu | 김치찌개 |

같은 날짜의 같은 항목을 다시 입력하면 최신 값으로 갱신됩니다.

## 로컬 실행

```bash
git clone <REPOSITORY_URL> Daily_Routine_Bot
cd Daily_Routine_Bot
printf '%s\n' '<TELEGRAM_BOT_TOKEN>' > .telegram.key
chmod 600 .telegram.key
python3 -m routine_bot.cli init-db
python3 -m routine_bot.cli setup-ui
python3 -m routine_bot.cli poll
```

`poll`은 Telegram long polling 방식으로 계속 실행됩니다. 개발 중 중지하려면 `Ctrl-C`를 사용합니다.

## Git에 올리지 않는 파일

아래 파일은 `.gitignore`로 제외합니다.

| 파일 | 설명 |
| --- | --- |
| `.telegram.key` | Telegram bot token |
| `.telegram.chat` | 등록된 Telegram 대화방 식별자 |
| `var/` | SQLite DB와 runtime state |
| `__pycache__/` | Python cache |
| `.pytest_cache/` | test cache |

## Public Repository 보안 기준

public repository에는 다음 정보를 남기지 않습니다.

- 실제 서버 IP 또는 hostname
- SSH private key 경로
- 실제 Linux 계정명
- Telegram bot token
- Telegram chat id
- SQLite DB 또는 runtime state
- 개인 로컬 절대경로

배포 문서에는 placeholder만 사용합니다.

## 배포

Linux VM 또는 Oracle Cloud 인스턴스에서는 systemd 서비스로 상시 실행하는 구성을 사용합니다. 배포 템플릿은 [config/oracle_deploy.md](config/oracle_deploy.md)를 참고합니다.

예상 서비스명:

```text
daily-routine-bot.service
```

운영 명령 예시:

```bash
sudo systemctl status daily-routine-bot.service
sudo systemctl restart daily-routine-bot.service
sudo journalctl -u daily-routine-bot.service -n 100 --no-pager
```

## 현재 MVP 범위

현재 버전은 다음 범위를 우선 지원합니다.

- Telegram bot token 검증
- `/start` 기반 대화방 등록
- 스케줄 기반 질문 발송
- 조건부 질문 발송
- 퇴근 예정시간 기준 동적 질문
- 선택형 질문 reply keyboard
- 메인 메뉴 버튼
- Telegram command menu 설정
- 답변별 루틴 코칭 메시지
- 답변 기록
- 오늘/최근 7일 조회
- 일시 중지/재개
- SQLite 저장
- Linux VM 배포 문서

## 다음 개선 후보

- 주간/월간 통계 리포트
- CSV 백업 또는 Google Sheets 연동
