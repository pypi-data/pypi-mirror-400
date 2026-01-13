import numpy as np
import scipy.signal

def align_and_calculate_snr(noisy: np.ndarray, enhanced: np.ndarray) -> float:
    # 1. Normalize lengths
    min_len = min(len(noisy), len(enhanced))
    noisy = noisy[:min_len]
    enhanced = enhanced[:min_len]
    
    # 2. Cross-Correlation for Latency
    correlation = scipy.signal.correlate(noisy, enhanced, mode='full')
    lags = scipy.signal.correlation_lags(len(noisy), len(enhanced), mode='full')
    lag_idx = np.argmax(correlation)
    delay = lags[lag_idx]
    
    # 3. Apply Time Shift
    if delay > 0:
        enhanced_aligned = enhanced[delay:]
        noisy_aligned = noisy[:len(enhanced_aligned)]
    elif delay < 0:
        noisy_aligned = noisy[abs(delay):]
        enhanced_aligned = enhanced[:len(noisy_aligned)]
    else:
        enhanced_aligned = enhanced
        noisy_aligned = noisy

    # 4. Least Squares Scaling
    numerator = np.dot(noisy_aligned, enhanced_aligned)
    denominator = np.dot(enhanced_aligned, enhanced_aligned)
    alpha = 1.0 if denominator == 0 else (numerator / denominator)
    
    # 5. Extract Residuals
    speech_est = alpha * enhanced_aligned
    noise_est = noisy_aligned - speech_est
    
    # 6. Power Calculation
    p_signal = np.mean(speech_est**2)
    p_noise = np.mean(noise_est**2)
    
    if p_noise < 1e-12: p_noise = 1e-12

    snr_db = 10 * np.log10(p_signal / p_noise)
    return float(snr_db)