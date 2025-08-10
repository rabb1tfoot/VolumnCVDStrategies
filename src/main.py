import time
from data_collection import DataCollector
from execution import OrderExecutor
from risk_management import RiskManager
from strategy_loader import StrategyLoader
from logging import TradingLogger
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv(os.path.join(os.path.dirname(__file__), '../config/.env'))

def main():
    # 로거 초기화
    logger = TradingLogger().get_logger()
    logger.info("Starting cryptocurrency trading system")
    
    # 모듈 초기화
    data_collector = DataCollector()
    order_executor = OrderExecutor()
    risk_manager = RiskManager(order_executor.exchange)
    logger.info("Modules initialized")
    
    # 전략 로드
    strategy_name = StrategyLoader.get_strategy_name()
    logger.info(f"Loaded strategy: {strategy_name}")
    
    while True:
        try:
            # 실시간 데이터 수집
            logger.debug("Fetching real-time data...")
            data = data_collector.fetch_historical_data(timeframe='5m', limit=100)
            
            if data is not None:
                # 전략 실행
                strategy = StrategyLoader.get_strategy(data)
                signals = strategy.generate_signals()
                latest_signal = signals.iloc[-1]
                
                # 매매 신호 처리
                if latest_signal == 1:  # 매수 신호
                    logger.info("BUY signal detected")
                    # 포지션 크기 계산
                    position_size = risk_manager.calculate_position_size(
                        entry_price=data['close'].iloc[-1]
                    )
                    # 주문 실행
                    order_executor.place_market_order('buy', position_size)
                    
                elif latest_signal == -1:  # 매도 신호
                    logger.info("SELL signal detected")
                    # 포지션 청산
                    order_executor.close_all_positions()
                    
            # 1분 대기
            time.sleep(60)
            
        except Exception as e:
            logger.error(f"System error: {e}")
            time.sleep(10)  # 오류 후 잠시 대기

if __name__ == "__main__":
    main()