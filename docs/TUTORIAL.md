# 자동매매 시스템 튜토리얼

## 1. 시스템 설정
1. 저장소 복제:
   ```bash
   git clone https://github.com/rabb1tfoot/VolumnCVDStrategies.git
   cd VolumnCVDStrategies
   ```

2. 가상 환경 생성 및 활성화:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. 의존성 설치:
   ```bash
   pip install -r requirements.txt
   ```

4. 환경 설정 파일 생성:
   ```bash
   copy config\.env.template config\.env
   ```
   - `config\.env` 파일에 Bybit API 키 입력
   - 거래 전략 및 스타일 설정 (TRADING_STRATEGY, TRADING_STYLE)

## 2. 실시간 거래 실행
1. 메인 스크립트 실행:
   ```bash
   python src/main.py
   ```
   - 시스템이 자동으로 설정된 전략 기반 매매 실행
   - 거래 내역은 `logs/` 디렉토리에 저장

## 3. 백테스팅 실행
1. 백테스팅 디렉토리 이동:
   ```bash
   cd backtest
   ```

2. 백테스팅 설정 수정 (`config.py`):
   - 시작/종료 날짜 조정
   - 거래 심볼, 금액 설정
   - 위험 관리 파라미터 조정

3. 백테스팅 실행:
   ```bash
   jesse run
   ```
   - 결과는 터미널에 출력 및 `storage/` 디렉토리에 저장

## 4. 전략 커스터마이징
1. 새 전략 추가:
   - `src/strategies/` 디렉토리에 새 파이썬 파일 생성
   - `generate_signals` 메서드 구현
   - `.env` 파일에 새 전략 이름 추가

2. Jesse 전략 수정:
   - `backtest/strategies/` 디렉토리에서 전략 파일 수정
   - `should_long()`, `should_short()` 메서드 구현

## 5. 모니터링 및 문제 해결
1. 로그 확인:
   - `logs/trading_*.log` 파일에서 거래 내역 확인
   - `logs/` 디렉토리의 오류 로그 분석

2. 문제 발생 시:
   - GitHub 이슈 트래커에 오류 내용 보고
   - `config\.env`에서 `LOG_LEVEL`을 `DEBUG`로 변경 후 재실행

## 6. 성능 최적화
1. 파라미터 튜닝:
   - `config.py` 및 `.env` 파일의 위험 관리 파라미터 조정
   - 전략별 임계값 최적화

2. 멀티타임프레임 분석:
   - 장기/단기 차트 결합 분석
   - `data_collection.py`에서 다중 시간대 데이터 수집 구현