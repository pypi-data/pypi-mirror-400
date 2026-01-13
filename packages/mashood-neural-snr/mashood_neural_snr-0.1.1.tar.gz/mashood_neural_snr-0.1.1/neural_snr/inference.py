import os
import sys
import logging
import contextlib
import torch
import torchaudio
from tqdm import tqdm  # The progress bar library
from df.enhance import enhance, init_df
from torchaudio.transforms import Resample
from .core import align_and_calculate_snr

# --- 1. Tool to Silence Logs ---
@contextlib.contextmanager
def suppress_output():
    """
    Temporarily redirects stdout and stderr to devnull to silence 
    DeepFilterNet's noisy logs and git errors.
    """
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        try:
            sys.stdout = devnull
            sys.stderr = devnull
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

class SNREstimator:
    def __init__(self):
        # Silence the "DF" logger specifically
        logging.getLogger("DF").setLevel(logging.ERROR)
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, "DeepFilterNet3")
        
        # We use our silence tool here because init_df is very noisy
        try:
            with suppress_output():
                self.model, self.df_state, _ = init_df(model_base_dir=model_path, post_filter=True)
        except Exception:
            # Fallback: If silence fails, just load normally
            self.model, self.df_state, _ = init_df(model_base_dir=model_path, post_filter=True)
            
        self.target_sr = self.df_state.sr()

    def estimate(self, file_path: str, show_progress: bool = True) -> float:
        """
        Calculates SNR. 
        show_progress=True will display a progress bar.
        """
        # Define steps for the progress bar
        steps = ["Loading Audio", "Resampling", "Separating Speech", "Calculating SNR"]
        
        # Create an iterator (either with tqdm or without)
        iterator = tqdm(steps, desc="Processing Audio", unit="step", leave=False) if show_progress else steps

        # --- Step 1: Loading ---
        if show_progress: iterator.set_description("Loading Audio")
        waveform, orig_sr = torchaudio.load(file_path)
        if show_progress: iterator.update(1)

        # --- Step 2: Resampling ---
        if show_progress: iterator.set_description("Resampling")
        if orig_sr != self.target_sr:
            resampler = Resample(orig_sr, self.target_sr)
            waveform = resampler(waveform)
        if show_progress: iterator.update(1)

        # --- Step 3: Inference (The Heavy Part) ---
        if show_progress: iterator.set_description("Neural Separation")
        # We suppress output here too, just in case torch prints warnings
        with suppress_output():
            enhanced_tensor = enhance(self.model, self.df_state, waveform)
        if show_progress: iterator.update(1)

        # --- Step 4: Calculation ---
        if show_progress: iterator.set_description("Calculating SNR")
        noisy_np = waveform.mean(dim=0).squeeze().numpy()
        enhanced_np = enhanced_tensor.mean(dim=0).squeeze().numpy()
        
        snr_val = align_and_calculate_snr(noisy_np, enhanced_np)
        if show_progress: iterator.update(1)
        
        # Close the bar properly
        if show_progress: 
            iterator.close()
            
        return snr_val