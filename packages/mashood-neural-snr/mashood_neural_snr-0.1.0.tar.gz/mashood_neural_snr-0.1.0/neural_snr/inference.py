import os
import torch
import torchaudio
from df.enhance import enhance, init_df
from torchaudio.transforms import Resample
from .core import align_and_calculate_snr

class SNREstimator:
    def __init__(self):
        # FIND THE MODEL FOLDER AUTOMATICALLY
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, "DeepFilterNet3")
        
        print(f"Loading DeepFilterNet model from: {model_path}")
        
        # Initialize with the local path
        self.model, self.df_state, _ = init_df(model_base_dir=model_path, post_filter=True)
        self.target_sr = self.df_state.sr()

    def estimate(self, file_path: str) -> float:
        waveform, orig_sr = torchaudio.load(file_path)
        
        if orig_sr != self.target_sr:
            resampler = Resample(orig_sr, self.target_sr)
            waveform = resampler(waveform)

        enhanced_tensor = enhance(self.model, self.df_state, waveform)
        
        noisy_np = waveform.mean(dim=0).squeeze().numpy()
        enhanced_np = enhanced_tensor.mean(dim=0).squeeze().numpy()
        
        return align_and_calculate_snr(noisy_np, enhanced_np)