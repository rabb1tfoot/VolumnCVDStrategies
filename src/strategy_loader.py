import os
from dotenv import load_dotenv
from .strategies.obv_strategy import OBVStrategy
from .strategies.volume_profile_strategy import VolumeProfileStrategy
from .strategies.cvd_strategy import CVDStrategy
from .strategies.market_profile_strategy import MarketProfileStrategy

# 환경 변수 로드
load_dotenv(os.path.join(os.path.dirname(__file__), '../config/.env'))

def load_strategy():
    """환경 변수 기반으로 적절한 전략 인스턴스 반환"""
    strategy_name = os.getenv('TRADING_STRATEGY', 'OBV').upper()
    style = os.getenv('TRADING_STYLE', 'SCALPING').upper()
    
    strategy_map = {
        'OBV': OBVStrategy,
        'VOLUME_PROFILE': VolumeProfileStrategy,
        'CVD': CVDStrategy,
        'MARKET_PROFILE': MarketProfileStrategy
    }
    
    if strategy_name not in strategy_map:
        raise ValueError(f"지원되지 않는 전략: {strategy_name}")
    
    return strategy_map[strategy_name](style)

# 테스트
if __name__ == "__main__":
    try:
        strategy = load_strategy()
        print(f"로드된 전략: {strategy.__class__.__name__}, 모드: {strategy.style}")
    except ValueError as e:
        print(e)