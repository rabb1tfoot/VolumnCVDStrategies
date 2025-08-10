# Bybit 선물 거래량 기반 자동매매 시스템

Python 기반 Bybit 거래소 자동매매 시스템으로, 고급 거래량 분석을 통한 매매 신호 생성 및 실행

## 주요 기능
- 실시간 시장 데이터 수집 (REST API + WebSocket)
- **통합 거래량 기반 전략 (OBV + Volume Profile + CVD + Market Profile)**
- 스캘핑 & 스윙 거래 모드 지원
- 위험 관리 모듈 (동적 손절/익절)
- **Backtrader 기반 백테스팅 시스템**
- 거래 내역 로깅 및 모니터링

## 시작하기
1. 의존성 설치: `pip install -r requirements.txt`
2. 환경 설정:
   - `config/.env.template` 파일을 복사하여 `.env` 생성
   - Bybit API 키 입력
3. 실행: `python src/main.py`

## 백테스팅 실행
```bash
# 데이터 수집 (필요한 경우)
python src/data_collection.py

# Backtrader 백테스팅 실행
python backtest/backtrader_strategy.py
```

## 디렉토리 구조
```
crypto-trading-system/
├── src/          # 소스 코드
│   └── strategies/ # 거래 전략
│       └── integrated_volume_strategy.py # 통합 전략
├── backtest/     # 백테스팅 스크립트 및 설정
├── config/       # 설정 파일
├── docs/         # 문서
├── tests/        # 테스트 코드
├── .gitignore
├── README.md
└── requirements.txt
```

## 통합 전략 특징
1. **스캘핑 모드**:
   - 가격 돌파 + CVD 급등 + OBV 상승 + Market Profile 불완전 경회 복구
   - 빠른 진입/청산 (분 단위)

2. **스윙 모드**:
   - 가격 이탈 + OBV/CVD 강세 다이버전스 + Volume Profile 저거래량 구간 통과
   - 중장기 포지션 (일/주 단위)

## 개발 예정 기능
- 웹 기반 대시보드
- AI 기반 전략 최적화

## 문의
문제 발생 시 [GitHub 이슈 트래커](https://github.com/rabb1tfoot/VolumnCVDStrategies/issues)에 등록해주세요.