# Daily Routine Bot 개발계획서

작성일: 2026-08-25

## 목표

Telegram 챗봇이 요일/시간 기반으로 하루 루틴 질문을 보내고, 사용자의 선택 또는 자유 입력을 SQLite에 기록한다. 이후 일별/주별 조회와 통계, 개인 AI 비서 agent 기능으로 확장한다.

## Public repository 원칙

이 저장소에는 코드, 문서, 설정 템플릿만 저장한다. 실제 Telegram token, chat id, 서버 IP, SSH key 경로, 서버 계정명, runtime DB는 저장하지 않는다.

## MVP 범위

- Telegram long polling
- 정해진 시간 질문 발송
- 요일별 질문 설정
- 선택형/입력형 답변 저장
- `/today`, `/week` 조회
- `/pause`, `/resume`, `/skip`
- SQLite 저장

## 데이터 모델

`routine_entries`

- `entry_date`
- `field`
- `label`
- `value`
- `source`
- `asked_at`
- `answered_at`

## 운영 방식

Linux VM에서 `systemd` service로 `python3 -m routine_bot.cli poll`을 상시 실행한다. 실제 서버 접속 정보와 secret은 서버 내부에서만 관리한다.

## 확장 계획

- 월간 통계
- 수면시간 계산
- 음주/운동 빈도 추적
- 출근/퇴근 패턴 분석
- Google Calendar 연동
- 개인 AI agent 메모리와 연결
