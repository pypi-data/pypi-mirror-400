import os
import sys
import contextlib
import torch
import torchaudio
from tqdm import tqdm
from df.enhance import enhance, init_df
from torchaudio.transforms import Resample
from .core import align_and_calculate_snr

# --- THE SAFE SILENCER ---
@contextlib.contextmanager
def suppress_output():
    """
    Redirects Python's stdout and stderr to null.
    Safe for Windows, keeps the progress bar alive.
    """
    with open(os.devnull, "w") as devnull:
        # We use contextlib to redirect Python's stream objects
        # This catches print() and logging output without crashing the OS
        with contextlib.redirect_stdout(devnull), contextlib.redirect_stderr(devnull):
            yield

class SNREstimator:
    def __init__(self):
        # Placeholders
        self.model = None
        self.df_state = None
        self.target_sr = None
        
        # Paths
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_path = os.path.join(self.current_dir, "DeepFilterNet3")

    def _load_model(self):
        """Helper to load model only when needed"""
        if self.model is not None:
            return 
            
        # MUTE THE NOISY FUNCTION
        with suppress_output():
            self.model, self.df_state, _ = init_df(model_base_dir=self.model_path, post_filter=True)
            
        self.target_sr = self.df_state.sr()

    def estimate(self, file_path: str, show_progress: bool = True) -> float:
        loading_needed = (self.model is None)
        steps_count = 5 if loading_needed else 4
        
        if show_progress:
            bar = tqdm(total=steps_count, desc="Initializing", unit="step", leave=False)

        # Step 1: Load Model (Silenced)
        if loading_needed:
            if show_progress: bar.set_description("Loading AI Model")
            self._load_model()
            if show_progress: bar.update(1)

        # Step 2: Load Audio
        if show_progress: bar.set_description("Loading Audio")
        waveform, orig_sr = torchaudio.load(file_path)
        if show_progress: bar.update(1)

        # Step 3: Resample
        if show_progress: bar.set_description("Resampling")
        if orig_sr != self.target_sr:
            resampler = Resample(orig_sr, self.target_sr)
            waveform = resampler(waveform)
        if show_progress: bar.update(1)

        # Step 4: Inference (Silenced)
        if show_progress: bar.set_description("Separating Speech")
        with suppress_output():
            enhanced_tensor = enhance(self.model, self.df_state, waveform)
        if show_progress: bar.update(1)

        # Step 5: Calculation
        if show_progress: bar.set_description("Calculating SNR")
        noisy_np = waveform.mean(dim=0).squeeze().numpy()
        enhanced_np = enhanced_tensor.mean(dim=0).squeeze().numpy()
        
        snr_val = align_and_calculate_snr(noisy_np, enhanced_np)
        if show_progress: bar.update(1)
        
        if show_progress: 
            bar.close()
            
        return snr_val