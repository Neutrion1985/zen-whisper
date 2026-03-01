import os
import threading
import time
from faster_whisper import WhisperModel

from PyQt6.QtCore import QObject, pyqtSignal

class TranscriptionEngine(QObject):
    transcription_ready = pyqtSignal(str)
    model_loaded = pyqtSignal(bool)
    
    def __init__(self, model_size="base"):
        super().__init__()
        self.model_size = model_size
        self.model = None
        self.is_loading = False
        self._load_lock = threading.Lock()

    def set_model_size(self, size):
        """Updates the model size. Note: requires load_model() to apply."""
        if self.model_size != size:
            self.model_size = size
            self.model = None # Force reload
            return True
        return False

    def load_model(self):
        """Loads the model in a separate thread if not already loaded."""
        with self._load_lock:
            if self.model is not None or self.is_loading:
                return
            
            self.is_loading = True
            
        def _target():
            print(f"Loading Whisper model: {self.model_size}...")
            start_l = time.perf_counter()
            success = False
            try:
                # Use int8 for speed/memory efficiency on CPU
                self.model = WhisperModel(self.model_size, device="auto", compute_type="int8")
                dur = time.perf_counter() - start_l
                print(f"Model {self.model_size} loaded successfully in {dur:.2f}s.")
                success = True
            except Exception as e:
                print(f"Error loading model {self.model_size}: {e}")
            finally:
                self.is_loading = False
                self.model_loaded.emit(success)

        thread = threading.Thread(target=_target, daemon=True)
        thread.start()

    def transcribe(self, audio_path):
        """Transcribes the given audio file."""
        if self.model is None:
            print("Error: Model not loaded yet")
            return "Error: Model not loaded"
        
        try:
            start_time = time.perf_counter()
            # 1. Build initial_prompt from vocabulary
            from zenwhisper.core.config import config
            voc_words = config.get("vocabulary") or []
            initial_prompt = None
            if voc_words:
                unique_words = list(dict.fromkeys(voc_words))
                initial_prompt = "Context: " + ", ".join(unique_words) + "."

            # Get language from config for explicit passing
            target_lang = config.get("language") or "en"

            # 2. Transcribe with beam_size=2 and VAD filter
            # Support mixed languages (RU+EN) by letting Whisper auto-detect
            segments, info = self.model.transcribe(
                audio_path, 
                beam_size=2,
                initial_prompt=initial_prompt,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500)
            )
            
            full_text = ""
            for segment in segments:
                full_text += segment.text + " "
            
            end_time = time.perf_counter()
            print(f"DEBUG: Engine transcription took {end_time - start_time:.4f}s")
                
            return full_text.strip()
        except Exception as e:
            print(f"Transcription Error (Engine): {e}")
            import traceback
            traceback.print_exc()
            return f"Error during transcription: {str(e)}"

# Global instance
engine = TranscriptionEngine(model_size="base")
