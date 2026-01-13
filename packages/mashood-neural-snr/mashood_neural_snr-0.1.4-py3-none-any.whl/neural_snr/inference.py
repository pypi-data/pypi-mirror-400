import os
import sys
import contextlib
import subprocess
import torch
import torchaudio
from tqdm import tqdm
from df.enhance import enhance, init_df
from torchaudio.transforms import Resample
from .core import align_and_calculate_snr

# --- THE SAFE SILENCER ---
@contextlib.contextmanager
def silence_all():
    """
    1. Redirects stdout/stderr to devnull (Hides Logs)
    2. Mocks subprocess to prevent 'fatal: not a git repo' (Hides Git Error)
    """
    # Prepare the Mock for subprocess
    original_check_output = subprocess.check_output
    original_run = subprocess.run

    def dummy_check_output(*args, **kwargs):
        # Return empty bytes for any command (fooling the git check)
        return b"" 

    def dummy_run(*args, **kwargs):
        return subprocess.CompletedProcess(args, 0, stdout=b"", stderr=b"")

    # Open null device
    with open(os.devnull, "w") as devnull:
        # Redirect Python streams safely (No os.dup2 crashes)
        with contextlib.redirect_stdout(devnull), contextlib.redirect_stderr(devnull):
            try:
                # Apply the subprocess patch
                subprocess.check_output = dummy_check_output
                subprocess.run = dummy_run
                yield
            finally:
                # Restore everything
                subprocess.check_output = original_check_output
                subprocess.run = original_run

class SNREstimator:
    def __init__(self):
        self.model = None
        self.df_state = None
        self.target_sr = None
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_path = os.path.join(self.current_dir, "DeepFilterNet3")

    def _load_model(self):
        """Helper to load model silently"""
        if self.model is not None:
            return 
            
        # Run init inside the silencer
        with silence_all():
            self.model, self.df_state, _ = init_df(model_base_dir=self.model_path, post_filter=True)
            
        self.target_sr = self.df_state.sr()

    def estimate(self, file_path: str, show_progress: bool = True) -> float:
        loading_needed = (self.model is None)
        steps_count = 5 if loading_needed else 4
        
        if show_progress:
            bar = tqdm(total=steps_count, desc="Initializing", unit="step", leave=False)

        # Step 1: Load Model
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

        # Step 4: Inference (Also silenced to catch any runtime warnings)
        if show_progress: bar.set_description("Separating Speech")
        with silence_all():
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