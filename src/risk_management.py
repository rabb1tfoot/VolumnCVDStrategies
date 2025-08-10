import os
import numpy as np
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv(os.path.join(os.path.dirname(__file__), '../config/.env'))

class RiskManager:
    def __init__(self, exchange, symbol=None):
        """
        위험 관리 클래스
        
        :param exchange: ccxt 거래소 객체
        :param symbol: 거래 심볼 (예: 'BTC/USDT')
        """
        self.exchange = exchange
        self.symbol = symbol or os.getenv('TRADE_SYMBOL', 'BTC/USDT')
        self.stop_loss_percent = float(os.getenv('STOP_LOSS_PERCENT', 2)) / 100
        self.take_profit_percent = float(os.getenv('TAKE_PROFIT_PERCENT', 5)) / 100
        self.risk_per_trade = float(os.getenv('RISK_PER_TRADE', 1)) / 100  # 거래당 위험 비율
        
    def calculate_position_size(self, entry_price, stop_loss_price=None):
        """
        포지션 크기 계산 (계정 잔고 대비 위험 비율 기반)
        
        :param entry_price: 진입 가격
        :param stop_loss_price: 손절 가격 (None일 경우 고정 비율 사용)
        :return: 포지션 크기 (계약 수)
        """
        try:
            # 계정 잔고 조회
            balance = self.exchange.fetch_balance()
            equity = balance['USDT']['free']  # USDT 기준
            
            # 손절 가격 계산
            if stop_loss_price is None:
                stop_loss_price = entry_price * (1 - self.stop_loss_percent)
                
            # 위험 금액 계산
            risk_amount = equity * self.risk_per_trade
            
            # 포지션 크기 계산
            risk_per_contract = abs(entry_price - stop_loss_price)
            position_size = risk_amount / risk_per_contract
            
            return round(position_size, 4)  # 소수점 4자리까지
        except Exception as e:
            print(f"Error calculating position size: {e}")
            return None
            
    def dynamic_stop_loss(self, current_price, atr_period=14, multiplier=2.0):
        """
        동적 손절 가격 계산 (ATR 기반)
        
        :param current_price: 현재 가격
        :param atr_period: ATR 기간
        :param multiplier: ATR 승수
        :return: 손절 가격
        """
        try:
            # 과거 데이터 가져오기
            ohlcv = self.exchange.fetch_ohlcv(self.symbol, '1h', limit=atr_period+1)
            closes = np.array([x[4] for x in ohlcv])
            highs = np.array([x[2] for x in ohlcv])
            lows = np.array([x[3] for x in ohlcv])
            
            # ATR 계산
            atr = self.calculate_atr(highs, lows, closes, atr_period)
            stop_loss_price = current_price - (atr[-1] * multiplier)
            
            return stop_loss_price
        except Exception as e:
            print(f"Error calculating dynamic stop loss: {e}")
            return current_price * (1 - self.stop_loss_percent)
            
    def calculate_atr(self, highs, lows, closes, period=14):
        """ATR(평균 실변동폭) 계산"""
        tr = []
        for i in range(1, len(closes)):
            high_low = highs[i] - lows[i]
            high_close = abs(highs[i] - closes[i-1])
            low_close = abs(lows[i] - closes[i-1])
            tr.append(max(high_low, high_close, low_close))
            
        atr = [sum(tr[:period]) / period]
        for i in range(period, len(tr)):
            atr.append((atr[-1] * (period - 1) + tr[i]) / period)
            
        return np.array(atr)
        
    def risk_reward_ratio(self, entry_price, take_profit_price, stop_loss_price):
        """
        위험-보상 비율 계산
        
        :param entry_price: 진입 가격
        :param take_profit_price: 익절 가격
        :param stop_loss_price: 손절 가격
        :return: 위험-보상 비율
        """
        reward = abs(take_profit_price - entry_price)
        risk = abs(entry_price - stop_loss_price)
        return reward / risk if risk > 0 else 0
        
    def calculate_take_profit(self, entry_price, direction, risk_reward_ratio=1.5):
        """
        익절 가격 계산 (위험-보상 비율 기반)
        
        :param entry_price: 진입 가격
        :param direction: 포지션 방향 ('long' 또는 'short')
        :param risk_reward_ratio: 원하는 위험-보상 비율
        :return: 익절 가격
        """
        if direction == 'long':
            return entry_price * (1 + self.stop_loss_percent * risk_reward_ratio)
        elif direction == 'short':
            return entry_price * (1 - self.stop_loss_percent * risk_reward_ratio)
        else:
            return entry_price * (1 + self.take_profit_percent)

if __name__ == "__main__":
    # 테스트 실행 (실제 거래소 연결 없이)
    from execution import OrderExecutor
    
    executor = OrderExecutor()
    risk_manager = RiskManager(executor.exchange)
    
    print("Testing risk management...")
    entry_price = 50000
    stop_loss = risk_manager.dynamic_stop_loss(entry_price)
    position_size = risk_manager.calculate_position_size(entry_price, stop_loss)
    
    print(f"Entry Price: {entry_price}")
    print(f"Dynamic Stop Loss: {stop_loss:.2f}")
    print(f"Position Size: {position_size}")
    
    take_profit = risk_manager.calculate_take_profit(entry_price, 'long')
    rr_ratio = risk_manager.risk_reward_ratio(entry_price, take_profit, stop_loss)
    print(f"Take Profit: {take_profit:.2f}")
    print(f"Risk-Reward Ratio: {rr_ratio:.2f}")