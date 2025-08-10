import pandas as pd
import talib
import numpy as np

class OBVStrategy:
    def __init__(self, style='SCALPING'):
        """
        OBV 다이버전스 매매 전략
        
        :param style: 거래 스타일 (SCALPING, SWING)
        """
        self.style = style.upper()
        self.obv_period = 14  # OBV 계산 기간
        
        # 스타일별 파라미터 설정
        if self.style == 'SCALPING':
            self.timeframe = '5m'  # 5분 차트
            self.divergence_threshold = 0.01  # 다이버전스 임계값
        else:
            self.timeframe = '1h'  # 1시간 차트
            self.divergence_threshold = 0.03  # 다이버전스 임계값

    def calculate_obv(self, data):
        """OBV(On-Balance Volume) 계산"""
        return talib.OBV(data['close'], data['volume'])
        
    def detect_divergence(self, prices, obv_values):
        """가격과 OBV 간의 다이버전스 감지"""
        # 가격과 OBV의 최근 고점/저점 분석
        price_peaks = np.where((prices[:-2] < prices[1:-1]) & (prices[1:-1] > prices[2:]))[0] + 1
        obv_peaks = np.where((obv_values[:-2] < obv_values[1:-1]) & (obv_values[1:-1] > obv_values[2:]))[0] + 1
        
        # 상승 다이버전스 (가격은 저점 갱신, OBV는 저점 상승)
        bull_divergence = False
        # 하락 다이버전스 (가격은 고점 갱신, OBV는 고점 하락)
        bear_divergence = False
        
        # 최근 2개 피크 비교
        if len(price_peaks) >= 2 and len(obv_peaks) >= 2:
            price_peak1 = prices[price_peaks[-1]]
            price_peak2 = prices[price_peaks[-2]]
            obv_peak1 = obv_values[obv_peaks[-1]]
            obv_peak2 = obv_values[obv_peaks[-2]]
            
            # 하락 다이버전스: 가격은 상승, OBV는 하락
            if price_peak2 < price_peak1 and obv_peak2 > obv_peak1:
                bear_divergence = True
            # 상승 다이버전스: 가격은 하락, OBV는 상승
            elif price_peak2 > price_peak1 and obv_peak2 < obv_peak1:
                bull_divergence = True
        
        return bull_divergence, bear_divergence
        
    def generate_signals(self, data):
        """매매 신호 생성"""
        # OBV 계산
        obv = self.calculate_obv(data)
        data['obv'] = obv
        
        # 다이버전스 감지
        bull_div, bear_div = self.detect_divergence(data['close'].values, obv.values)
        
        # 신호 초기화
        signals = pd.Series(0, index=data.index)
        
        # 스캘핑: 단기 신호에 민감하게 반응
        if self.style == 'SCALPING':
            # 상승 다이버전스 발생 시 매수
            if bull_div:
                signals.iloc[-1] = 1
            # 하락 다이버전스 발생 시 매도
            elif bear_div:
                signals.iloc[-1] = -1
                
        # 스윙: 추세 확인 후 신호 발생
        else:
            # 추가 추세 확인 지표 (예: 20기간 이동평균)
            ma20 = data['close'].rolling(20).mean()
            current_close = data['close'].iloc[-1]
            
            # 상승 다이버전스 + 가격이 이동평균 위에 있을 때 매수
            if bull_div and current_close > ma20.iloc[-1]:
                signals.iloc[-1] = 1
            # 하락 다이버전스 + 가격이 이동평균 아래에 있을 때 매도
            elif bear_div and current_close < ma20.iloc[-1]:
                signals.iloc[-1] = -1
        
        return signals

if __name__ == "__main__":
    # 테스트 데이터
    data = pd.DataFrame({
        'open': [50000, 51000, 51500, 52000, 52500, 53000],
        'high': [50500, 51500, 52000, 52500, 53000, 53500],
        'low': [49500, 50500, 51000, 51500, 52000, 52500],
        'close': [50200, 51200, 51700, 52200, 52700, 53200],
        'volume': [1000, 1500, 1200, 1800, 2000, 1700]
    })
    
    # 스캘핑 모드 테스트
    scalping_strategy = OBVStrategy(style='SCALPING')
    scalping_signals = scalping_strategy.generate_signals(data)
    print("Scalping Signals:")
    print(scalping_signals)
    
    # 스윙 모드 테스트
    swing_strategy = OBVStrategy(style='SWING')
    swing_signals = swing_strategy.generate_signals(data)
    print("\nSwing Signals:")
    print(swing_signals)