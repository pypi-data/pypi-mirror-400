# Context Engine Inspection Script
# Dynamically loads active profiles and inspects variables

from context_engine.profiles import get_active_profiles
from context_engine.profiles.base import BASE_INSPECTION_CODE
from context_engine.profiles.ml import ML_INSPECTION_CODE
from context_engine.profiles.finance import FINANCE_INSPECTION_CODE

def get_inspection_code(var_name: str) -> str:
    """Generates the full inspection code with active profiles."""
    profiles = get_active_profiles()
    
    # Start with core inspection
    code = '''
import json

def _context_engine_inspect(var_name):
    try:
        if var_name not in globals():
            return json.dumps({"error": f"Variable '{var_name}' not found"})
            
        obj = globals()[var_name]
        info = {
            "type": type(obj).__name__,
            "str_repr": str(obj)[:500]
        }
        
'''
    
    # Inject profile code blocks
    if "base" in profiles:
        code += '''
        # Base Profile (Pandas, Numpy, builtins)
        try:
            import pandas as pd
            import numpy as np
            
            if isinstance(obj, pd.DataFrame):
                info.update({
                    "is_dataframe": True,
                    "shape": list(obj.shape),
                    "columns": list(obj.columns),
                    "dtypes": {k: str(v) for k, v in obj.dtypes.items()},
                    "memory_mb": round(obj.memory_usage(deep=True).sum() / 1024 / 1024, 2),
                    "head": obj.head(5).to_dict(orient='records')
                })
            elif isinstance(obj, pd.Series):
                info.update({
                    "is_series": True,
                    "shape": list(obj.shape),
                    "dtype": str(obj.dtype),
                    "head": obj.head(5).tolist()
                })
            elif isinstance(obj, np.ndarray):
                info.update({
                    "is_array": True,
                    "shape": list(obj.shape),
                    "dtype": str(obj.dtype),
                    "stats": {"min": float(obj.min()), "max": float(obj.max()), "mean": float(obj.mean())} if obj.size > 0 else {}
                })
            elif isinstance(obj, (list, tuple)):
                info.update({"length": len(obj), "sample": list(obj)[:5]})
            elif isinstance(obj, dict):
                info.update({"length": len(obj), "keys": list(obj.keys())[:20]})
        except Exception:
            pass
'''
    
    if "ml" in profiles:
        code += '''
        # ML Profile (PyTorch, TensorFlow, sklearn)
        try:
            import torch
            if isinstance(obj, torch.nn.Module):
                info.update({
                    "is_pytorch_model": True,
                    "total_params": sum(p.numel() for p in obj.parameters()),
                    "trainable_params": sum(p.numel() for p in obj.parameters() if p.requires_grad)
                })
            elif isinstance(obj, torch.Tensor):
                info.update({
                    "is_tensor": True,
                    "shape": list(obj.shape),
                    "dtype": str(obj.dtype),
                    "device": str(obj.device)
                })
        except ImportError:
            pass
        try:
            import tensorflow as tf
            if isinstance(obj, tf.keras.Model):
                info.update({
                    "is_keras_model": True,
                    "total_params": obj.count_params(),
                    "layers": len(obj.layers)
                })
        except ImportError:
            pass
        try:
            from sklearn.base import BaseEstimator
            if isinstance(obj, BaseEstimator):
                info.update({
                    "is_sklearn_model": True,
                    "model_type": type(obj).__name__,
                    "params": obj.get_params()
                })
        except ImportError:
            pass
'''

    if "finance" in profiles:
        code += '''
        # Finance Profile (Backtrader, vectorbt)
        try:
            import backtrader as bt
            if isinstance(obj, bt.Cerebro):
                info.update({"is_cerebro": True, "strategies": len(obj.strats)})
        except ImportError:
            pass
        try:
            import vectorbt as vbt
            if hasattr(vbt, 'Portfolio') and isinstance(obj, vbt.Portfolio):
                info.update({
                    "is_vbt_portfolio": True,
                    "total_return": float(obj.total_return()),
                    "sharpe_ratio": float(obj.sharpe_ratio())
                })
        except ImportError:
            pass
'''
    
    # Close function
    code += '''
        return json.dumps(info, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})

print(_context_engine_inspect('{var_name}'))
'''
    
    return code.replace("{var_name}", var_name)

# Legacy compatibility
_context_engine_inspection_code = get_inspection_code("{var_name}")
