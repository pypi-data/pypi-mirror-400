import os
import sys
import logging
import contextlib
import torch
import torchaudio
from tqdm import tqdm
from df.enhance import enhance, init_df
from torchaudio.transforms import Resample
from .core import align_and_calculate_snr

# --- THE NUCLEAR SILENCER (Fixes fatal git error) ---
@contextlib.contextmanager
def suppress_output():
    """
    Redirects low-level file descriptors to silence 
    C-libraries and subprocesses.
    """
    try:
        # Open null device
        with open(os.devnull, "w") as devnull:
            # Save original file descriptors
            old_stdout_fd = os.dup(sys.stdout.fileno())
            old_stderr_fd = os.dup(sys.stderr.fileno())

            try:
                # Redirect 1 (stdout) and 2 (stderr) to devnull
                os.dup2(devnull.fileno(), sys.stdout.fileno())
                os.dup2(devnull.fileno(), sys.stderr.fileno())
                yield
            finally:
                # Restore original file descriptors
                os.dup2(old_stdout_fd, sys.stdout.fileno())
                os.dup2(old_stderr_fd, sys.stderr.fileno())
                os.close(old_stdout_fd)
                os.close(old_stderr_fd)
    except Exception:
        # Fallback for environments where os.dup2 fails
        with open(os.devnull, "w") as devnull:
            old_out, old_err = sys.stdout, sys.stderr
            try:
                sys.stdout, sys.stderr = devnull, devnull
                yield
            finally:
                sys.stdout, sys.stderr = old_out, old_err

class SNREstimator:
    def __init__(self):
        # Don't load the model here! Just set placeholders.
        # This ensures the class inits instantly.
        self.model = None
        self.df_state = None
        self.target_sr = None
        
        # Prepare path
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_path = os.path.join(self.current_dir, "DeepFilterNet3")
        
        logging.getLogger("DF").setLevel(logging.ERROR)

    def _load_model(self):
        """Helper to load model only when needed"""
        if self.model is not None:
            return # Already loaded
            
        with suppress_output():
            self.model, self.df_state, _ = init_df(model_base_dir=self.model_path, post_filter=True)
        self.target_sr = self.df_state.sr()

    def estimate(self, file_path: str, show_progress: bool = True) -> float:
        # Define logic: If model needs loading, that's step 1.
        loading_needed = (self.model is None)
        
        # Total steps
        steps_count = 5 if loading_needed else 4
        
        # Start Bar IMMEDIATELY
        if show_progress:
            bar = tqdm(total=steps_count, desc="Initializing", unit="step", leave=False)

        # --- Step 1: Load Model (The heavy part) ---
        if loading_needed:
            if show_progress: bar.set_description("Loading AI Model")
            self._load_model()
            if show_progress: bar.update(1)

        # --- Step 2: Load Audio ---
        if show_progress: bar.set_description("Loading Audio")
        waveform, orig_sr = torchaudio.load(file_path)
        if show_progress: bar.update(1)

        # --- Step 3: Resample ---
        if show_progress: bar.set_description("Resampling")
        if orig_sr != self.target_sr:
            resampler = Resample(orig_sr, self.target_sr)
            waveform = resampler(waveform)
        if show_progress: bar.update(1)

        # --- Step 4: Inference ---
        if show_progress: bar.set_description("Separating Speech")
        with suppress_output():
            enhanced_tensor = enhance(self.model, self.df_state, waveform)
        if show_progress: bar.update(1)

        # --- Step 5: Calculation ---
        if show_progress: bar.set_description("Calculating SNR")
        noisy_np = waveform.mean(dim=0).squeeze().numpy()
        enhanced_np = enhanced_tensor.mean(dim=0).squeeze().numpy()
        
        snr_val = align_and_calculate_snr(noisy_np, enhanced_np)
        if show_progress: bar.update(1)
        
        if show_progress: 
            bar.close()
            
        return snr_val