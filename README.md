# Bybit 선물 거래량 기반 자동매매 시스템

Python 기반 Bybit 거래소 자동매매 시스템으로, 거래량 분석을 통한 매매 신호 생성 및 실행

## 주요 기능
- 실시간 시장 데이터 수집 (REST API + WebSocket)
- 거래량 기반 매매 전략 구현 (VWAP, 거래량 스파이크)
- 위험 관리 모듈 (동적 손절/익절, 포지션 크기 계산)
- 백테스팅 시스템 (Backtrader 통합)
- 거래 내역 로깅 및 모니터링

## 시작하기
1. 의존성 설치: `pip install -r requirements.txt`
2. 환경 설정:
   - `config/.env.template` 파일을 복사하여 `.env` 생성
   - Bybit API 키 입력
3. 실행: `python src/main.py`

## 디렉토리 구조
```
crypto-trading-system/
├── src/          # 소스 코드
│   ├── data_collection.py   # 데이터 수집
│   ├── strategy.py          # 거래 전략
│   ├── execution.py         # 주문 실행
│   ├── risk_management.py   # 위험 관리
│   ├── logging.py           # 로깅 시스템
│   └── main.py              # 메인 실행
├── config/       # 설정 파일
├── docs/         # 문서
├── backtest/     # 백테스팅
├── tests/        # 테스트 코드
├── .gitignore
└── README.md
```

## 백테스팅 실행
```
python backtest/backtrader_strategy.py
```

## 개발 예정 기능
- 다중 거래소 지원
- 웹 기반 대시보드
- AI 기반 전략 최적화

## 문의
문제 발생 시 GitHub 이슈 트래커에 등록해주세요:  
https://github.com/rabb1tfoot/VolumnCVDStrategies/issues