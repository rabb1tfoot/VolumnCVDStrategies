import os
import time
import ccxt
from dotenv import load_dotenv
import pandas as pd
try:
    from .custom_logger import logger  # 패키지 내부에서 임포트
except ImportError:
    from custom_logger import logger  # 직접 실행 시 절대 경로 임포트

# 환경 변수 로드
load_dotenv(os.path.join(os.path.dirname(__file__), '../config/.env'))

class DataCollector:
    def __init__(self):
        self.api_key = os.getenv('BYBIT_API_KEY')
        self.api_secret = os.getenv('BYBIT_API_SECRET')
        self.symbol = os.getenv('TRADE_SYMBOL', 'BTC/USDT')
        
        # Bybit 연결 초기화
        self.exchange = ccxt.bybit({
            'apiKey': self.api_key,
            'secret': self.api_secret,
            'enableRateLimit': True,
            'options': {'defaultType': 'future'}
        })
        self.ws_connected = False
        
    def validate_candle(self, candle):
        """캔들 데이터 무결성 검증"""
        if not candle:
            return False
        o, h, l, c = candle[1], candle[2], candle[3], candle[4]
        return h >= c >= l and h >= o >= l
        
    def fetch_with_retry(self, func, max_retries=5, *args, **kwargs):
        """지수 백오프 재시도 로직"""
        retry = 0
        while retry < max_retries:
            try:
                return func(*args, **kwargs)
            except ccxt.RateLimitExceeded as e:
                wait = 2 ** retry
                logger.warning(f"Rate limit exceeded. Retrying in {wait} seconds...")
                time.sleep(wait)
                retry += 1
            except ccxt.NetworkError as e:
                logger.error(f"Network error: {e}. Reconnecting...")
                self.reconnect()
                retry += 1
            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)
                return None
        logger.error(f"Failed after {max_retries} retries")
        return None
        
    def reconnect(self):
        """거래소 연결 재설정"""
        try:
            self.exchange = ccxt.bybit({
                'apiKey': self.api_key,
                'secret': self.api_secret,
                'enableRateLimit': True,
                'options': {'defaultType': 'future'}
            })
            logger.info("Exchange connection reestablished")
            return True
        except Exception as e:
            logger.error(f"Reconnection failed: {e}")
            return False
        
    def fetch_historical_data(self, timeframe='1h', limit=100):
        """과거 캔들 데이터 조회"""
        def _fetch():
            ohlcv = self.exchange.fetch_ohlcv(self.symbol, timeframe, limit=limit)
            # 데이터 무결성 검사
            valid_ohlcv = [c for c in ohlcv if self.validate_candle(c)]
            if len(valid_ohlcv) != len(ohlcv):
                logger.warning(f"Filtered {len(ohlcv) - len(valid_ohlcv)} invalid candles")
            return valid_ohlcv
            
        ohlcv = self.fetch_with_retry(_fetch)
        if ohlcv:
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            return df
        return None
        
    def stream_realtime_data(self, on_message, max_retries=3):
        """실시간 거래 데이터 스트리밍 (WebSocket) - 기본 구현"""
        retry = 0
        while retry < max_retries:
            try:
                logger.info("Starting WebSocket connection...")
                # 실제 WebSocket 연결 코드는 여기에 구현
                # 연결 성공 시 루프 실행
                self.ws_connected = True
                while self.ws_connected:
                    # 메시지 수신 및 on_message 콜백 호출
                    # 예시: message = receive_websocket_message()
                    # on_message(message)
                    pass
            except Exception as e:
                logger.error(f"WebSocket error: {e}. Reconnecting...")
                retry += 1
                time.sleep(2 ** retry)
        logger.error("WebSocket connection failed after retries")
        
    def close_websocket(self):
        """WebSocket 연결 종료"""
        self.ws_connected = False
        logger.info("WebSocket connection closed")
        
if __name__ == "__main__":
    import os
    import datetime
    
    collector = DataCollector()
    print("Fetching historical data...")
    data = collector.fetch_historical_data(limit=500)  # 500개 데이터 가져오기
    
    if data is not None:
        print(data.head())
        
        # 데이터 저장 디렉토리 생성
        data_dir = os.path.join(os.path.dirname(__file__), '../backtest/data')
        os.makedirs(data_dir, exist_ok=True)
        
        # 파일 이름 생성 (예: bybit_btcusdt_1h_20250810.csv)
        timestamp = datetime.datetime.now().strftime("%Y%m%d")
        filename = f"bybit_{collector.symbol.replace('/', '')}_1h_{timestamp}.csv"
        filepath = os.path.join(data_dir, filename)
        
        # CSV로 저장
        data.to_csv(filepath)
        print(f"Data saved to {filepath}")