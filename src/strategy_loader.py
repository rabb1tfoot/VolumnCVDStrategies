import os
from dotenv import load_dotenv
from .strategies.obv_strategy import OBVStrategy
from .strategies.volume_profile_strategy import VolumeProfileStrategy

# 환경 변수 로드
load_dotenv(os.path.join(os.path.dirname(__file__), '../config/.env'))

class StrategyLoader:
    @staticmethod
    def get_strategy(data):
        """환경 설정에 따라 전략 인스턴스 반환"""
        strategy_type = os.getenv('TRADING_STRATEGY', 'obv').lower()
        
        if strategy_type == 'obv':
            return OBVStrategy(data)
        elif strategy_type == 'volume_profile':
            return VolumeProfileStrategy(data)
        else:
            raise ValueError(f"Unknown strategy type: {strategy_type}")

    @staticmethod
    def get_strategy_name():
        """현재 선택된 전략 이름 반환"""
        strategy_type = os.getenv('TRADING_STRATEGY', 'obv').lower()
        
        if strategy_type == 'obv':
            return "OBV Divergence Strategy"
        elif strategy_type == 'volume_profile':
            return "Volume Profile Breakout Strategy"
        else:
            return "Unknown Strategy"

if __name__ == "__main__":
    # 테스트 데이터
    import pandas as pd
    import numpy as np
    
    data = pd.DataFrame({
        'timestamp': pd.date_range(start='2023-01-01', periods=100, freq='T'),
        'open': np.random.rand(100) * 100 + 100,
        'high': np.random.rand(100) * 5 + 105,
        'low': np.random.rand(100) * 5 + 95,
        'close': np.random.rand(100) * 10 + 100,
        'volume': np.random.randint(1000, 10000, 100)
    })
    
    # 전략 로드 테스트
    strategy = StrategyLoader.get_strategy(data)
    print(f"Loaded strategy: {StrategyLoader.get_strategy_name()}")
    signals = strategy.generate_signals()
    print("Sample signals:")
    print(signals.tail(10))