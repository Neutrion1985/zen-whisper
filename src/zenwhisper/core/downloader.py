import os
from huggingface_hub import snapshot_download
from PyQt6.QtCore import QThread, pyqtSignal
from tqdm import tqdm

class ModelDownloader(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str) # success, message

    def __init__(self, model_size):
        super().__init__()
        self.model_size = model_size
        # Map simple names to HuggingFace repo IDs
        self.repo_id = f"Systran/faster-whisper-{model_size}"

    def run(self):
        # We need a proper class here, not a lambda, because tqdm/huggingface_hub
        # might access class-level attributes like get_lock()
        signal_caller = self.progress

        class CustomTQDM(tqdm):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._last_percent = 0

            def update(self, n=1):
                super().update(n)
                if self.total:
                    percent = int((self.n / self.total) * 100)
                    if percent > self._last_percent:
                        self._last_percent = percent
                        signal_caller.emit(percent)

        try:
            print(f"DEBUG: Starting download for {self.repo_id}...")
            snapshot_download(
                repo_id=self.repo_id,
                repo_type="model",
                tqdm_class=CustomTQDM
            )
            self.finished.emit(True, f"Model {self.model_size} ready.")
        except Exception as e:
            print(f"DEBUG: Download error: {e}")
            import traceback
            traceback.print_exc()
            self.finished.emit(False, str(e))

def is_model_cached(model_size):
    """Checks if the model is already downloaded in the HF cache."""
    from huggingface_hub import scan_cache_dir
    try:
        repo_id = f"Systran/faster-whisper-{model_size}"
        cache_info = scan_cache_dir()
        for repo in cache_info.repos:
            if repo.repo_id == repo_id and repo.repo_type == "model":
                return True
    except Exception as e:
        print(f"DEBUG: Cache scan error: {e}")
    return False
