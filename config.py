config = {
    # 백테스팅 기간
    'start_date': '2024-01-01',
    'end_date': '2024-12-31',
    
    # 거래 통화 및 심볼
    'exchange': 'bybit',
    'symbol': 'BTC-USDT',
    
    # 거래 금액
    'fee': 0.001,  # 0.1%
    'type': 'futures',  # 선물 거래
    'settlement_currency': 'USDT',
    'base_currency': 'BTC',
    'quote_currency': 'USDT',
    
    # 백테스팅 설정
    'timeframe': '1h',  # 기본 시간 프레임
    'warmup_candles': 50,  # 지표 계산을 위한 초기 캔들 수
    
    # 위험 관리
    'risk_per_trade': 1,  # 거래당 위험 비율 (%)
    'stop_loss': 2,  # 손절 비율 (%)
    'take_profit': 5,  # 익절 비율 (%)
    
    # 전략 설정
    'strategy': 'VolumnCVDStrategy',
    
    # 로깅
    'logging': True,
    'log_level': 'INFO'
}