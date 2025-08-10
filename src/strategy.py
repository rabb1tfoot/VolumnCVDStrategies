from .strategy_loader import load_strategy

class TradingStrategy:
    def __init__(self, data, strategy_name=None, style=None):
        """
        거래량 기반 매매 전략 클래스
        
        :param data: DataFrame with columns ['open', 'high', 'low', 'close', 'volume']
        :param strategy_name: 사용할 전략 이름 (None일 경우 환경변수 사용)
        :param style: 거래 스타일 (SCALPING, SWING)
        """
        self.data = data.copy()
        self.strategy = load_strategy() if strategy_name is None else None
        self.strategy_name = strategy_name
        self.style = style
        
    def generate_signals(self):
        """매매 신호 생성"""
        if self.strategy:
            return self.strategy.generate_signals(self.data)
        else:
            # 기본 전략 (VWAP + 거래량 스파이크)
            return self._generate_basic_signals()
            
    def _generate_basic_signals(self):
        """기본 매매 신호 생성 (VWAP + 거래량 스파이크)"""
        # VWAP 계산
        typical_price = (self.data['high'] + self.data['low'] + self.data['close']) / 3
        cumulative_tp_volume = (typical_price * self.data['volume']).cumsum()
        cumulative_volume = self.data['volume'].cumsum()
        self.data['vwap'] = cumulative_tp_volume / cumulative_volume
        
        # 거래량 스파이크 감지 (20기간 이동평균 대비 2배 이상)
        self.data['volume_ma'] = self.data['volume'].rolling(window=20).mean()
        self.data['volume_spike'] = (self.data['volume'] > 2 * self.data['volume_ma']).astype(int)
        
        # 신호 초기화
        self.data['signal'] = 0
        
        # 매수 신호: 가격이 VWAP 아래이고 거래량 급증 발생
        self.data.loc[
            (self.data['close'] < self.data['vwap']) & 
            (self.data['volume_spike'] == 1), 
            'signal'
        ] = 1  # 매수
        
        # 매도 신호: 가격이 VWAP 위이고 거래량 급증 발생
        self.data.loc[
            (self.data['close'] > self.data['vwap']) & 
            (self.data['volume_spike'] == 1), 
            'signal'
        ] = -1  # 매도
        
        return self.data['signal']
        
if __name__ == "__main__":
    import pandas as pd
    # 테스트 데이터 (실제로는 DataCollector에서 받아옴)
    data = pd.DataFrame({
        'open': [50000, 51000, 51500, 52000],
        'high': [50500, 51500, 52000, 52500],
        'low': [49500, 50500, 51000, 51500],
        'close': [50200, 51200, 51700, 52200],
        'volume': [1000, 2500, 3000, 4000]
    })
    
    # 환경변수 기반 전략 로드 테스트
    strategy = TradingStrategy(data)
    signals = strategy.generate_signals()
    print("Generated signals (using strategy loader):")
    print(signals)
    
    # 기본 전략 테스트
    basic_strategy = TradingStrategy(data, strategy_name="BASIC")
    basic_signals = basic_strategy.generate_signals()
    print("\nBasic strategy signals:")
    print(basic_signals)