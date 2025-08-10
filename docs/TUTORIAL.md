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

## 4. 전략 세부 설명

### 4.1 스캘핑 모드
- **진입 조건**:
  1. 가격이 Volume Profile POC 근접
  2. CVD 20% 이상 급등
  3. OBV 단기 > 장기 이평
  4. Market Profile Poor High 돌파
- **포지션 관리**:
  - 손절: 돌파 지지선 아래 0.5%
  - 익절: 위험-보상 비율 2:1

### 4.2 스윙 모드
- **진입 조건**:
  1. 주간 Value Area 이탈
  2. OBV 강세 다이버전스
  3. CVD 강세 다이버전스
  4. Volume Profile 저거래량 구간 통과
- **포지션 관리**:
  - 손절: 주요 지지선 아래 1%
  - 익절: Poor High 복구 지점 또는 위험-보상 2:1

## 5. 모니터링
- `logs/` 디렉토리에서 실시간 로그 확인:
  ```log
  2025-08-10 21:30:15 - LONG 진입: 0.05@50200, SL: 49949, TP: 50502
  2025-08-10 21:45:30 - Take Profit 실행: 0.05@50502 (+302)
  ```

## 6. 백테스팅
```bash
jesse run backtest --start 2024-01-01 --end 2024-12-31
```

## 7. 문제 해결
- **데이터 부족**: `jesse import-candles` 명령으로 데이터 수집
- **전략 수정**: `src/strategies/integrated_volume_strategy.py` 조정
- **디버깅**: `jesse run --debug` 모드 활성화