from jesse.routes import router

# BTC/USDT 선물 거래
router.futures('Bybit', 'BTC-USDT', '1h', 'VolumnCVDStrategy')