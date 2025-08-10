# Bybit 선물 거래량 기반 자동매매 시스템

Python 기반 Bybit 거래소 자동매매 시스템으로, 거래량 분석을 통한 매매 신호 생성 및 실행

## 주요 기능
- 실시간 시장 데이터 수집 (REST API + WebSocket)
- 4가지 거래량 기반 매매 전략 (OBV, Volume Profile, CVD, Market Profile)
- 스캘핑/스윙 거래 스타일 지원
- 위험 관리 모듈 (손절/익절)
- 거래 내역 로깅 및 모니터링
- Jesse 백테스팅 통합

## 시작하기
1. 의존성 설치: `pip install -r requirements.txt`
2. 환경 설정:
   - `config/.env.template` 파일을 복사하여 `.env` 생성
   - Bybit API 키 입력
   - 거래 전략 및 스타일 설정 (OBV, VOLUME_PROFILE, CVD, MARKET_PROFILE / SCALPING, SWING)
3. 실행: `python src/main.py`

## 백테스팅 가이드
1. 백테스팅 디렉토리로 이동: `cd backtest`
2. Jesse 설정 파일 수정 (`config.py`):
   - 시작/종료 날짜
   - 거래 심볼
   - 위험 관리 파라미터
3. 전략 선택 (`strategies/` 디렉토리)
4. 백테스팅 실행: `jesse run`

## 디렉토리 구조
```
crypto-trading-system/
├── src/                  # 소스 코드
│   ├── strategies/       # 전략 모듈
│   ├── data_collection.py
│   ├── strategy.py
│   ├── execution.py
│   ├── risk_management.py
│   ├── logging.py
│   └── main.py
├── backtest/             # 백테스팅 설정
│   ├── strategies/       # Jesse 전략
│   ├── config.py
│   └── routes.py
├── config/               # 설정 파일
├── docs/                 # 문서
├── tests/                # 테스트 코드
├── .gitignore
├── README.md
└── requirements.txt
```

## 지원 전략
1. **OBV 다이버전스 전략**
   - 가격과 OBV의 다이버전스 패턴 분석
   - 스캘핑: 5분 차트, 스윙: 1시간 차트

2. **Volume Profile 지지/저항 돌파 전략**
   - 고거래량대(HVZ) 분석
   - 지지선/저항선 돌파 신호 포착

3. **누적 거래량 델타(CVD) 전략**
   - 매수/매도 압력 분석
   - CVD-가격 다이버전스 패턴 감지

4. **마켓 프로파일 구조 분석**
   - Poor Highs/Lows, Single Prints 패턴 분석
   - 가치 영역(Value Area) 기반 거래

## 문의
문제 발생 시 GitHub 이슈 트래커에 등록해주세요.