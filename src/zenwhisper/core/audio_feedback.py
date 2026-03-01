import os
import subprocess
import threading
from pathlib import Path

class SoundFeedback:
    def __init__(self):
        self.enabled = True
        # Locate assets: prefer local dev path, fallback to installed system path
        current_dir = Path(__file__).parent.absolute()
        asset_dir = current_dir.parent / "assets"
        
        # Fallback to system-installed path
        system_asset_dir = Path("/usr/share/zenwhisper/zenwhisper/assets")
        
        self.start_sound = self._find_sound("start.wav", asset_dir, system_asset_dir)
        self.stop_sound = self._find_sound("stop.wav", asset_dir, system_asset_dir)
        print(f"DEBUG: Sound paths: start={self.start_sound}, stop={self.stop_sound}")

    def _find_sound(self, filename, *dirs):
        """Find a sound file in multiple directories."""
        for d in dirs:
            path = d / filename
            if path.exists():
                return str(path)
        return None

    def play_start(self):
        self._play(self.start_sound)

    def play_stop(self):
        self._play(self.stop_sound)

    def _play(self, file_path):
        if not self.enabled or not file_path or not os.path.exists(file_path):
            print(f"DEBUG: Sound skipped (enabled={self.enabled}, path={file_path})")
            return
            
        def _target():
            try:
                # Use subprocess with proper argument list (no shell=True, handles spaces)
                subprocess.Popen(
                    ["paplay", file_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except FileNotFoundError:
                # paplay not available, try aplay as fallback
                try:
                    subprocess.Popen(
                        ["aplay", "-q", file_path],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                except Exception as e:
                    print(f"DEBUG: No audio player available: {e}")
            except Exception as e:
                print(f"DEBUG: Sound playback error: {e}")
            
        threading.Thread(target=_target, daemon=True).start()

# Global instance
sounds = SoundFeedback()
