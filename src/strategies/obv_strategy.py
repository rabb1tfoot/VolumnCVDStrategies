import backtrader as bt

class OnBalanceVolume(bt.Indicator):
    lines = ('obv',)
    
    def __init__(self):
        self.addminperiod(1)
        
    def next(self):
        if len(self.data) > 1:
            if self.data.close[0] > self.data.close[-1]:
                self.lines.obv[0] = self.lines.obv[-1] + self.data.volume[0]
            elif self.data.close[0] < self.data.close[-1]:
                self.lines.obv[0] = self.lines.obv[-1] - self.data.volume[0]
            else:
                self.lines.obv[0] = self.lines.obv[-1]
        else:
            self.lines.obv[0] = self.data.volume[0]

class OBVStrategy(bt.Strategy):
    params = (
        ('ma_period', 21),
    )
    
    def __init__(self):
        self.obv = OnBalanceVolume(self.data)
        self.obv_ma = bt.indicators.SMA(self.obv, period=self.params.ma_period)
        
    def next(self):
        if not self.position:
            if self.obv[0] > self.obv_ma[0]:
                self.buy()
        else:
            if self.obv[0] < self.obv_ma[0]:
                self.sell()