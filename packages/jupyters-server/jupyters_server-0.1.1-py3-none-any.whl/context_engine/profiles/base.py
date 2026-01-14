# Base Profile: Pandas, Numpy, Python builtins
# This code is injected into the user's kernel

BASE_INSPECTION_CODE = '''
# ContextEngine Base Profile
import json

def _ce_inspect_base(obj, info):
    """Base inspection for common types."""
    import pandas as pd
    import numpy as np
    
    # Pandas DataFrame
    if isinstance(obj, pd.DataFrame):
        info.update({
            "is_dataframe": True,
            "shape": list(obj.shape),
            "columns": list(obj.columns),
            "dtypes": {k: str(v) for k, v in obj.dtypes.items()},
            "memory_mb": round(obj.memory_usage(deep=True).sum() / 1024 / 1024, 2),
            "null_counts": obj.isnull().sum().to_dict(),
            "summary": obj.describe(include='all').to_dict(),
            "head": obj.head(5).to_dict(orient='records')
        })
        
    # Pandas Series
    elif isinstance(obj, pd.Series):
        info.update({
            "is_series": True,
            "shape": list(obj.shape),
            "dtype": str(obj.dtype),
            "null_count": int(obj.isnull().sum()),
            "summary": obj.describe().to_dict(),
            "head": obj.head(5).tolist()
        })
        
    # Numpy Array
    elif isinstance(obj, np.ndarray):
        info.update({
            "is_array": True,
            "shape": list(obj.shape),
            "dtype": str(obj.dtype),
            "min": float(obj.min()) if obj.size > 0 else None,
            "max": float(obj.max()) if obj.size > 0 else None,
            "mean": float(obj.mean()) if obj.size > 0 else None,
            "std": float(obj.std()) if obj.size > 0 else None
        })
        
    # Collections
    elif isinstance(obj, (list, tuple)):
        info.update({
            "length": len(obj),
            "sample": list(obj)[:5]
        })
    elif isinstance(obj, dict):
        info.update({
            "length": len(obj),
            "keys": list(obj.keys())[:20],
            "sample": {k: str(v)[:100] for k, v in list(obj.items())[:5]}
        })
    elif isinstance(obj, set):
        info.update({
            "length": len(obj),
            "sample": list(obj)[:5]
        })
        
    return info
'''
