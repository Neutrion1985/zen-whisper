import os
import wave
import threading
import sounddevice as sd
import numpy as np
from pathlib import Path

class AudioRecorder:
    def __init__(self, temp_dir=None):
        self.temp_dir = temp_dir or Path("/tmp/zenwhisper")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.output_file = self.temp_dir / "latest_recording.wav"
        
        self.sample_rate = 16000  # Whisper expects 16kHz
        self.channels = 1
        self.recording = False
        self.audio_data = []
        self._stream = None
        self.level_callback = None
        self.device_id = None # Default
        self.gain = 1.0  # Microphone gain multiplier (1.0 = no boost)

    def start_recording(self, level_callback=None):
        """Starts recording audio in a non-blocking way."""
        if self.recording:
            return
        
        self.recording = True
        self.audio_data = []
        self.level_callback = level_callback
        
        def callback(indata, frames, time, status):
            if status:
                print(f"Recording status: {status}")
            if self.recording:
                # Apply gain boost
                boosted = indata * self.gain
                # Clip to prevent distortion
                boosted = np.clip(boosted, -1.0, 1.0)
                self.audio_data.append(boosted.copy())
                if self.level_callback:
                    # Calculate RMS for volume level (use boosted data)
                    rms = np.sqrt(np.mean(boosted**2))
                    self.level_callback(rms)

        try:
            self._stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                device=self.device_id,
                callback=callback
            )
            self._stream.start()
        except Exception as e:
            print(f"ERROR: Failed to start recording on device {self.device_id}: {e}")
            if self.device_id is not None:
                print("Falling back to default device...")
                self.device_id = None
                self._stream = sd.InputStream(
                    samplerate=self.sample_rate,
                    channels=self.channels,
                    device=None,
                    callback=callback
                )
                self._stream.start()
            else:
                self.recording = False
                raise e
        print(f"Recording started... (gain={self.gain}x)")

    def stop_recording(self):
        """Stops recording and returns the path to the saved WAV file."""
        if not self.recording:
            return None
        
        self.recording = False
        if self._stream:
            self._stream.stop()
            self._stream.close()
        
        print("Recording stopped. Saving file...")
        
        # Stack all audio chunks
        if not self.audio_data:
            return None
            
        full_audio = np.concatenate(self.audio_data, axis=0)
        
        # Save as WAV
        with wave.open(str(self.output_file), 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.sample_rate)
            wf.writeframes((full_audio * 32767).astype(np.int16).tobytes())
            
        return str(self.output_file)

# Global instance
recorder = AudioRecorder()
