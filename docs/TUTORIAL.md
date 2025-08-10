# 통합 거래량 기반 전략 사용 가이드

## 1. 전략 개요
통합 거래량 기반 전략은 4가지 핵심 지표(OBV, Volume Profile, CVD, Market Profile)를 결합하여:
- 단기 스캘핑 기회 포착
- 중장기 스윙 기회 식별
- 거짓 신호 필터링 및 승률 향상

## 2. 전략 설정
`config.py`에서 전략 매개변수 조정:
```python
{
    'strategy': 'IntegratedVolumeStrategy',
    'parameters': {
        'scalping_enabled': True,  # 스캘핑 모드 활성화
        'swing_enabled': True,     # 스윙 모드 활성화
        'risk_reward_ratio': 2.0   # 위험-보상 비율
    }
}
```

## 3. 실행 방법
```bash
# 가상 환경 활성화 (Windows)
venv\Scripts\activate

# 메인 실행
python src/main.py
```

## 4. 백테스팅 (Backtrader 사용)
Jesse 대신 Backtrader를 사용한 백테스팅:

### 4.1 데이터 준비
1. Bybit API를 통해 데이터 수집:
```bash
python src/data_collection.py
```
2. 수집된 데이터는 `backtest/data/` 디렉토리에 CSV 형식으로 저장

### 4.2 백테스팅 실행
1. `backtest/backtrader_strategy.py` 파일에서 데이터 경로 설정:
```python
data = bt.feeds.GenericCSVData(
    dataname='backtest/data/bybit_btcusdt_1h.csv',  # 실제 데이터 경로로 수정
    fromdate=datetime(2024, 1, 1),
    todate=datetime(2024, 12, 31),
    dtformat=('%Y-%m-%d'),
    openinterest=-1
)
```
2. 백테스팅 실행:
```bash
python backtest/backtrader_strategy.py
```

### 4.3 결과 해석
1. **터미널 출력**:
   ```
   Starting Portfolio Value: 10000.00
   Final Portfolio Value: 12450.75
   ```
   - 초기/최종 포트폴리오 가치 비교로 수익률 계산

2. **시각화 결과**:
   - 자산 변동 곡선
   - 매수/매도 신호 표시
   - 기술적 지표(OBV, 이동평균) 표시

3. **성능 지표**:
   - 총 수익률
   - 최대 자본 인하(MDD)
   - 승률
   - 평균 손익비

### 4.4 백테스팅 최적화
```python
# backtrader_strategy.py에 추가
cerebro.optstrategy(
    IntegratedVolumeStrategy,
    risk_reward_ratio=[1.5, 2.0, 2.5],  # 최적의 위험-보상 비율 탐색
    scalping_enabled=[True, False]       # 스캘핑 모드 활성화 여부 테스트
)
```

## 5. 전략 세부 설명
### 5.1 스캘핑 모드
- **진입 조건**:
  1. 가격이 Volume Profile POC 근접
  2. CVD 20% 이상 급등
  3. OBV 단기 > 장기 이평
  4. Market Profile Poor High 돌파

### 5.2 스윙 모드
- **진입 조건**:
  1. 주간 Value Area 이탈
  2. OBV 강세 다이버전스
  3. CVD 강세 다이버전스
  4. Volume Profile 저거래량 구간 통과

## 6. 모니터링
- `logs/` 디렉토리에서 실시간 로그 확인

## 7. 문제 해결
- **데이터 부족**: `data_collection.py`로 데이터 수집
- **전략 수정**: `src/strategies/integrated_volume_strategy.py` 조정
- **백테스팅 오류**: `backtest/backtrader_strategy.py` 디버깅