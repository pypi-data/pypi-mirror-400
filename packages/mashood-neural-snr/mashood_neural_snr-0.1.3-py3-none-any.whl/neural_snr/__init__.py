from .inference import SNREstimator

_default_estimator = None

def snr(file_path: str) -> float:
    global _default_estimator
    if _default_estimator is None:
        _default_estimator = SNREstimator()
    
    return _default_estimator.estimate(file_path)