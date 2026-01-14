# Finance Profile: Backtesting, pandas-ta, quantlib
# This code is injected into the user's kernel

FINANCE_INSPECTION_CODE = '''
# ContextEngine Finance Profile
def _ce_inspect_finance(obj, info):
    """Finance-specific inspection."""
    
    # Backtrader Strategy
    try:
        import backtrader as bt
        if isinstance(obj, bt.Strategy):
            info.update({
                "is_bt_strategy": True,
                "strategy_name": type(obj).__name__,
                "analyzers": [type(a).__name__ for a in obj.analyzers] if hasattr(obj, 'analyzers') else []
            })
            return info
        if isinstance(obj, bt.Cerebro):
            info.update({
                "is_cerebro": True,
                "strategies": len(obj.strats),
                "datas": len(obj.datas)
            })
            return info
    except ImportError:
        pass
        
    # vectorbt
    try:
        import vectorbt as vbt
        if hasattr(vbt, 'Portfolio') and isinstance(obj, vbt.Portfolio):
            info.update({
                "is_vbt_portfolio": True,
                "total_return": float(obj.total_return()),
                "sharpe_ratio": float(obj.sharpe_ratio()),
                "max_drawdown": float(obj.max_drawdown())
            })
            return info
    except ImportError:
        pass
        
    # pandas-ta indicators on DataFrames
    try:
        import pandas as pd
        if isinstance(obj, pd.DataFrame):
            ta_cols = [c for c in obj.columns if any(
                ind in c.upper() for ind in ['SMA', 'EMA', 'RSI', 'MACD', 'BB', 'ATR']
            )]
            if ta_cols:
                info["detected_indicators"] = ta_cols
    except Exception:
        pass
        
    return info
'''
