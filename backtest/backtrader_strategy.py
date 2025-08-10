import backtrader as bt
import pandas as pd
from datetime import datetime

class IntegratedVolumeStrategy(bt.Strategy):
    params = (
        ('scalping_enabled', True),
        ('swing_enabled', True),
        ('risk_reward_ratio', 2.0),
    )

    def __init__(self):
        # 데이터 참조
        self.dataclose = self.datas[0].close
        self.dataopen = self.datas[0].open
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low
        self.volume = self.datas[0].volume
        
        # 지표 계산 (예시)
        self.obv = bt.indicators.OnBalanceVolume(self.datas[0])
        self.sma_obv_short = bt.indicators.SMA(self.obv, period=5)
        self.sma_obv_long = bt.indicators.SMA(self.obv, period=20)
        
    def next(self):
        # 포지션 보유 중이면 스킵
        if self.position:
            return
            
        # 통합 스캘핑 전략 조건
        if self.params.scalping_enabled and self._scalping_long_conditions():
            self.buy()
            
        # 통합 스윙 전략 조건
        if self.params.swing_enabled and self._swing_long_conditions():
            self.buy()

    def _scalping_long_conditions(self):
        # 간단한 조건 예시 (실제 구현은 전략에 맞게 확장 필요)
        return (self.dataclose[0] > self.dataclose[-1] and 
                self.volume[0] > self.volume[-1] * 1.2)

    def _swing_long_conditions(self):
        # 간단한 조건 예시
        return (self.dataclose[0] > bt.indicators.SMA(self.dataclose, period=50)[0] and
                self.obv[0] > self.sma_obv_short[0] > self.sma_obv_long[0])

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
            
        if order.status in [order.Completed]:
            if order.isbuy():
                # 위험-보상 비율 기반 손절/익절 설정
                stop_price = order.executed.price * 0.99
                take_profit = order.executed.price * (1 + self.params.risk_reward_ratio * 0.01)
                self.sell(exectype=bt.Order.Stop, price=stop_price)
                self.sell(exectype=bt.Order.Limit, price=take_profit)

if __name__ == '__main__':
    # Cerebro 엔진 생성
    cerebro = bt.Cerebro()
    
    # 데이터 로드 (예시, 실제 Bybit 데이터 사용)
    data = bt.feeds.GenericCSVData(
        dataname='path/to/your/data.csv',
        fromdate=datetime(2024, 1, 1),
        todate=datetime(2024, 12, 31),
        dtformat=('%Y-%m-%d'),
        openinterest=-1
    )
    
    # 데이터 추가
    cerebro.adddata(data)
    
    # 전략 추가
    cerebro.addstrategy(IntegratedVolumeStrategy)
    
    # 초기 자본 설정
    cerebro.broker.setcash(10000.0)
    
    # 수수료 설정
    cerebro.broker.setcommission(commission=0.001)
    
    # 백테스팅 실행
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    
    # 결과 시각화
    cerebro.plot()