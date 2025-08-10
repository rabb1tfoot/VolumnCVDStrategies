import pandas as pd
import numpy as np

class VolumeProfileStrategy:
    def __init__(self, data, window=100):
        """
        Volume Profile을 이용한 지지/저항 돌파(Breakout) 전략
        
        :param data: DataFrame with columns ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        :param window: Volume Profile 계산 기간 (봉 개수)
        """
        self.data = data.copy()
        self.window = window
        self.calculate_volume_profile()
        
    def calculate_volume_profile(self):
        """Volume Profile 계산"""
        # 가격 레벨별 거래량 누적
        self.data['price_level'] = self.data['close'].round(2)
        volume_profile = self.data.groupby('price_level')['volume'].sum().reset_index()
        
        # POC (Point of Control) - 최대 거래량 가격대
        poc = volume_profile.loc[volume_profile['volume'].idxmax(), 'price_level']
        self.data['poc'] = poc
        
        # Value Area (상위 70% 거래량 구간)
        volume_profile = volume_profile.sort_values('volume', ascending=False)
        cumulative_volume = volume_profile['volume'].cumsum()
        total_volume = volume_profile['volume'].sum()
        value_area = volume_profile[cumulative_volume <= total_volume * 0.7]
        self.data['value_area_high'] = value_area['price_level'].max()
        self.data['value_area_low'] = value_area['price_level'].min()
        
    def detect_breakout(self):
        """돌파 신호 감지"""
        # 신호 초기화
        self.data['signal'] = 0
        
        # 상승 돌파: 가격이 Value Area 상단 돌파
        breakout_up = (self.data['close'] > self.data['value_area_high']) & \
                     (self.data['close'].shift(1) <= self.data['value_area_high'])
        self.data.loc[breakout_up, 'signal'] = 1
        
        # 하락 돌파: 가격이 Value Area 하단 돌파
        breakout_down = (self.data['close'] < self.data['value_area_low']) & \
                       (self.data['close'].shift(1) >= self.data['value_area_low'])
        self.data.loc[breakout_down, 'signal'] = -1
        
        return self.data['signal']
        
    def generate_signals(self):
        """매매 신호 생성"""
        # 돌파 신호 감지
        self.detect_breakout()
        
        # 추가 조건: 거래량이 평균의 1.5배 이상
        avg_volume = self.data['volume'].rolling(window=self.window).mean()
        volume_spike = self.data['volume'] > avg_volume * 1.5
        self.data.loc[(self.data['signal'] != 0) & ~volume_spike, 'signal'] = 0
        
        return self.data['signal']

if __name__ == "__main__":
    # 테스트 데이터
    data = pd.DataFrame({
        'timestamp': pd.date_range(start='2023-01-01', periods=100, freq='T'),
        'open': np.random.rand(100) * 100 + 100,
        'high': np.random.rand(100) * 5 + 105,
        'low': np.random.rand(100) * 5 + 95,
        'close': np.random.rand(100) * 10 + 100,
        'volume': np.random.randint(1000, 10000, 100)
    })
    
    strategy = VolumeProfileStrategy(data, window=20)
    signals = strategy.generate_signals()
    print("Volume Profile Strategy Signals:")
    print(signals.tail(20))