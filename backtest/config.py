# 백테스팅 설정
config = {
    # 데이터 설정
    'data': {
        'dataname': 'backtest/data/bybit_BTCUSDT_1h_20250810.csv',
        'timeframe': '1h',       # 캔들 시간 단위 (1m, 5m, 15m, 1h, 4h, 1d)
        'compression': 1,        # 데이터 압축률 (기본값 1)
    },
    
    # 전략 설정
    'strategy': {
        'type': 'swing',         # 전략 유형: 'swing'(스윙), 'scalping'(스캘핑)
        'volume_spike_threshold': 1.5,  # 거래량 급증 임계값 (예: 1.5 = 150%, 평균 거래량 대비 150% 증가 시 신호)
        'vwap_period': 20,       # VWAP(Volume Weighted Average Price) 계산 기간 (봉 개수)
        'sma_period': 50,        # 단순 이동평균(SMA) 기간 (스윙 전략용)
        'rsi_period': 14,        # RSI(상대강도지수) 계산 기간
    },
    
    # 위험 관리
    'risk_per_trade': 1,  # 거래당 위험 비율 (%): 각 거래에서 위험하는 계정 자산의 비율 (1% 권장)
    'stop_loss': 2,       # 손절 비율 (%): 진입 가격 대비 손절 수준 (2% = 진입가격의 2% 하락 시 손절)
    'take_profit': 5,     # 익절 비율 (%): 진입 가격 대비 익절 수준 (5% = 진입가격의 5% 상승 시 익절)
    
    # 백테스팅 기간
    'start_date': '2025-07-01',  # 백테스팅 시작 일자
    'end_date': '2025-08-10',    # 백테스팅 종료 일자
    
    # 초기 자본
    'initial_cash': 10000,  # 백테스팅 시작 시 초기 자본 (USD)
}