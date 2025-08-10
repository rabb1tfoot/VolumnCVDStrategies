# 암호화폐 자동매매 시스템 튜토리얼

## 시스템 개요
이 시스템은 Bybit 거래소의 선물 시장에서 거래량 기반 전략을 사용하여 자동으로 매매를 실행합니다. 주요 구성 요소는 다음과 같습니다:
1. 데이터 수집 모듈: 실시간 시장 데이터 수집
2. 전략 엔진: 매매 신호 생성
3. 주문 실행: Bybit API를 통한 주문 처리
4. 위험 관리: 손절/익절 관리
5. 로깅: 모든 거래 활동 기록

## 설치 및 설정
1. 저장소 복제:
   ```bash
   git clone https://github.com/rabb1tfoot/VolumnCVDStrategies.git
   cd VolumnCVDStrategies
   ```

2. 가상 환경 생성 및 활성화:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. 의존성 설치:
   ```bash
   pip install -r requirements.txt
   ```

4. 환경 설정:
   - `config/.env.template` 파일을 `config/.env`로 복사
   - Bybit API 키 입력
   - 거래 설정 조정 (거래 심볼, 금액, 위험 관리 파라미터)

## 실행 방법
### 백테스팅
```bash
python backtest/backtrader_strategy.py
```
결과는 `backtest/results/` 디렉토리에 저장됩니다.

### 실시간 거래
```bash
python src/main.py
```

## 전략 커스터마이징
1. 새로운 전략 추가:
   - `src/strategies/` 디렉토리에 새 전략 파일 생성
   - `src/strategy_loader.py`에 전략 등록

2. 기존 전략 수정:
   - `src/strategies/` 디렉토리의 파일 편집
   - VWAP, 거래량 스파이크, OBV 등 다양한 지표 활용

## 문제 해결
- 로그 파일: `logs/` 디렉토리에서 확인
- 일반적인 오류:
  - API 키 미설정: `.env` 파일 확인
  - 의존성 문제: `pip install -r requirements.txt` 재실행
  - 데이터 수집 오류: 인터넷 연결 및 API 상태 확인

## 기여 가이드
1. 새 기능 개발은 feature branch에서 진행
2. 변경 사항은 PR로 제출
3. 코드 리뷰 후 master 브랜치로 병합

## 문의
문제 발생 시 GitHub 이슈 트래커에 등록해주세요:  
https://github.com/rabb1tfoot/VolumnCVDStrategies/issues