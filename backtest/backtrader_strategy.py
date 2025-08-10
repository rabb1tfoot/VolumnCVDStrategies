import backtrader as bt
from datetime import datetime, timedelta
import random
import pandas as pd
import numpy as np
import sys
import os  # os 모듈 추가

# src 디렉토리 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from strategies.obv_strategy import OBVStrategy  # 전략 임포트
import json

# 간단한 랜덤 워크 데이터 생성 클래스 (날짜 정보 추가)
class RandomWalk(bt.feeds.DataBase):
    params = (
        ('start', datetime(2023, 1, 1)),
        ('open', 50000.0),
        ('high', 52000.0),
        ('low', 48000.0),
        ('close', 51000.0),
        ('volume', 10000.0),
        ('timeframe', bt.TimeFrame.Minutes),
        ('compression', 5),
    )
    
    def __init__(self):
        super().__init__()
        self.last_price = self.p.close
        self.vol = self.p.volume
        self.current_date = self.p.start
        
    def start(self):
        super().start()
        self._index = 0
        
    def _load(self):
        if self._index >= 100:  # 100개의 봉 생성
            return False
            
        # 랜덤 가격 생성
        change = random.uniform(-0.02, 0.02)
        self.lines.open[0] = self.last_price
        self.lines.high[0] = self.last_price * (1 + abs(change))
        self.lines.low[0] = self.last_price * (1 - abs(change))
        self.lines.close[0] = self.last_price * (1 + change)
        self.lines.volume[0] = self.vol * random.uniform(0.8, 1.2)
        self.lines.datetime[0] = bt.date2num(self.current_date)
        
        # 다음 봉을 위해 날짜 업데이트 (5분 간격)
        self.current_date += timedelta(minutes=5)
        self.last_price = self.lines.close[0]
        self._index += 1
        
        return True

# 백테스팅 설정
cerebro = bt.Cerebro()

# 데이터 로드
data = RandomWalk(
    dataname='RandomWalk',
    timeframe=bt.TimeFrame.Minutes,
    compression=5,
    start=datetime(2023, 1, 1),
    open=50000.0,
    high=52000.0,
    low=48000.0,
    close=51000.0,
    volume=10000.0
)
cerebro.adddata(data)

# 전략 추가
cerebro.addstrategy(OBVStrategy)

# 분석기 추가
cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
cerebro.addanalyzer(bt.analyzers.PeriodStats, _name='stats')

# 초기 자본 설정
cerebro.broker.setcash(10000.0)

# 백테스팅 실행
print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
results = cerebro.run()
print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

# 결과 저장
os.makedirs('backtest/results', exist_ok=True)

# 거래 내역 저장 (간소화)
try:
    trades_analysis = results[0].analyzers.trades.get_analysis()
    if trades_analysis and hasattr(trades_analysis, 'total'):
        trades_df = pd.DataFrame([{
            'total_trades': trades_analysis.total.total,
            'won': trades_analysis.won.total,
            'lost': trades_analysis.lost.total,
            'pnl_net': trades_analysis.pnl.net.total,
        }])
        trades_df.to_csv('backtest/results/trades.csv')
        print(f"Saved trades summary")
    else:
        print("No trades executed during backtest")
except Exception as e:
    print(f"Error saving trades: {e}")

# 성과 지표 저장
try:
    perf = {
        'sharpe_ratio': results[0].analyzers.sharpe.get_analysis()['sharperatio'],
        'drawdown': results[0].analyzers.drawdown.get_analysis()['max']['drawdown'],
        'return_percent': results[0].analyzers.returns.get_analysis()['rtot'],
    }
    with open('backtest/results/performance.json', 'w') as f:
        json.dump(perf, f)
    print("Saved performance metrics")
except Exception as e:
    print(f"Performance analysis failed: {e}")

# 결과 플롯 (옵션)
# cerebro.plot(style='candlestick')

print("Backtest results saved to backtest/results/")