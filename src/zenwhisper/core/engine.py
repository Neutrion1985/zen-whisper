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

    def load_model(self, force_size=None):
        """Loads the model in a separate thread if not already loaded or different size."""
        target_size = force_size if force_size else self.model_size
        
        with self._load_lock:
            # If model already loaded with correct size, do nothing
            if self.model is not None and self.model_size == target_size and not self.is_loading:
                return
            
            # If already loading correct size, do nothing
            if self.is_loading and self.model_size == target_size:
                return
                
            self.model_size = target_size
            self.is_loading = True
            self.model = None # Clear old model to free memory
            
        def _target():
            print(f"Loading Whisper model: {self.model_size}...")
            start_l = time.perf_counter()
            success = False
            try:
                # Use int8 for speed/memory efficiency on CPU/GPU
                # device="auto" handles CUDA if available
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

    def transcribe(self, audio_path, return_segments=False):
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

            # 2. Transcribe with beam_size=2 and VAD filter
            segments, info = self.model.transcribe(
                audio_path, 
                beam_size=2,
                initial_prompt=initial_prompt,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500)
            )
            
            if return_segments:
                # Return list of dicts for easier processing
                res = []
                for s in segments:
                    res.append({
                        "start": s.start,
                        "end": s.end,
                        "text": s.text.strip()
                    })
                return res

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

    def format_timestamp(self, seconds):
        """Formats seconds into SRT timestamp: HH:MM:SS,mmm"""
        td_hours = int(seconds // 3600)
        td_mins = int((seconds % 3600) // 60)
        td_secs = int(seconds % 60)
        td_msecs = int((seconds - int(seconds)) * 1000)
        return f"{td_hours:02}:{td_mins:02}:{td_secs:02},{td_msecs:03}"

    def to_srt(self, segments):
        """Converts segments list (from transcribe(return_segments=True)) into SRT string."""
        srt_lines = []
        for i, seg in enumerate(segments, 1):
            start = self.format_timestamp(seg["start"])
            end = self.format_timestamp(seg["end"])
            text = seg["text"]
            srt_lines.append(f"{i}")
            srt_lines.append(f"{start} --> {end}")
            srt_lines.append(f"{text}\n")
        return "\n".join(srt_lines)

# Global instance
engine = TranscriptionEngine(model_size="base")
