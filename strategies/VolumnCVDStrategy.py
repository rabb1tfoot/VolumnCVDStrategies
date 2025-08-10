from jesse.strategies import Strategy
import jesse.indicators as ta
from jesse import utils

class VolumnCVDStrategy(Strategy):
    @property
    def obv(self):
        return ta.obv(self.candles)
    
    @property
    def vwap(self):
        return ta.vwap(self.candles)
    
    def should_long(self) -> bool:
        # OBV 상승 추세 + 가격이 VWAP 아래인 경우
        return self.obv[-1] > self.obv[-2] and self.close < self.vwap
    
    def should_short(self) -> bool:
        # OBV 하락 추세 + 가격이 VWAP 위인 경우
        return self.obv[-1] < self.obv[-2] and self.close > self.vwap
    
    def should_cancel(self) -> bool:
        return True
    
    def go_long(self):
        entry = self.close
        qty = utils.risk_to_qty(self.capital, 1, entry, self.stop_loss)
        self.buy = qty, entry
    
    def go_short(self):
        entry = self.close
        qty = utils.risk_to_qty(self.capital, 1, entry, self.stop_loss)
        self.sell = qty, entry
    
    @property
    def stop_loss(self):
        return self.close * 0.98  # 2% stop loss
    
    @property
    def take_profit(self):
        return self.close * 1.05  # 5% take profit