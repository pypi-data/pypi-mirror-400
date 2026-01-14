# ML Profile: PyTorch, TensorFlow, Keras, sklearn
# This code is injected into the user's kernel

ML_INSPECTION_CODE = '''
# ContextEngine ML Profile
def _ce_inspect_ml(obj, info):
    """ML-specific inspection."""
    
    # PyTorch Model
    try:
        import torch
        if isinstance(obj, torch.nn.Module):
            info.update({
                "is_pytorch_model": True,
                "architecture": str(obj),
                "total_params": sum(p.numel() for p in obj.parameters()),
                "trainable_params": sum(p.numel() for p in obj.parameters() if p.requires_grad),
                "device": str(next(obj.parameters()).device) if len(list(obj.parameters())) > 0 else "N/A"
            })
            return info
            
        # PyTorch Tensor
        if isinstance(obj, torch.Tensor):
            info.update({
                "is_tensor": True,
                "shape": list(obj.shape),
                "dtype": str(obj.dtype),
                "device": str(obj.device),
                "requires_grad": obj.requires_grad,
                "min": float(obj.min().item()) if obj.numel() > 0 else None,
                "max": float(obj.max().item()) if obj.numel() > 0 else None,
                "mean": float(obj.float().mean().item()) if obj.numel() > 0 else None
            })
            return info
    except ImportError:
        pass
        
    # TensorFlow/Keras Model
    try:
        import tensorflow as tf
        if isinstance(obj, tf.keras.Model):
            info.update({
                "is_keras_model": True,
                "total_params": obj.count_params(),
                "layers": len(obj.layers),
                "input_shape": str(obj.input_shape) if hasattr(obj, 'input_shape') else "N/A",
                "output_shape": str(obj.output_shape) if hasattr(obj, 'output_shape') else "N/A"
            })
            return info
            
        # TensorFlow Tensor
        if isinstance(obj, tf.Tensor):
            info.update({
                "is_tf_tensor": True,
                "shape": list(obj.shape),
                "dtype": str(obj.dtype)
            })
            return info
    except ImportError:
        pass
        
    # sklearn Models
    try:
        from sklearn.base import BaseEstimator
        if isinstance(obj, BaseEstimator):
            info.update({
                "is_sklearn_model": True,
                "model_type": type(obj).__name__,
                "params": obj.get_params()
            })
            if hasattr(obj, 'feature_importances_'):
                info["feature_importances"] = obj.feature_importances_.tolist()[:10]
            if hasattr(obj, 'coef_'):
                info["coef_shape"] = list(obj.coef_.shape)
            return info
    except ImportError:
        pass
        
    return info
'''
