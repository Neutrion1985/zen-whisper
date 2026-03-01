import os
import subprocess
import time
from PyQt6.QtWidgets import QApplication

class TextInjector:
    def __init__(self):
        # We prefer clipboard injection + Ctrl+V for Wayland compatibility
        self.method = self._detect_method()

    def _detect_method(self):
        try:
            subprocess.run(["xdotool", "--version"], capture_output=True)
            return "xdotool"
        except FileNotFoundError:
            try:
                subprocess.run(["wtype", "--version"], capture_output=True)
                return "wtype"
            except FileNotFoundError:
                return "wayland-clipboard"

    def inject(self, text):
        """Types the text into the currently focused window."""
        if not text:
            return
            
        print(f"Injecting text via {self.method}...")
        
        # Always copy to clipboard first for reliability
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        
        # Give a small delay for focus/clipboard sync
        time.sleep(0.02)

        if self.method == "xdotool":
            # Simulate Ctrl+V for better multi-language support than 'type'
            subprocess.run(["xdotool", "key", "--clearmodifiers", "ctrl+v"])
        elif self.method == "wtype":
            # wtype is often unreliable for Ctrl+V, 
            # so we try to 'type' it if possible, but wtype is rare on Ubuntu GNOME
            subprocess.run(["wtype", text])
        else:
            # On pure Wayland (GNOME) without wtype, we've already copied it.
            # Most Linux dictation apps on Wayland require the user to paste or 
            # use a dedicated portal. For now, we inform or try to use pynput to paste.
            try:
                from pynput.keyboard import Controller, Key
                keyboard = Controller()
                with keyboard.pressed(Key.ctrl if os.name != 'nt' else Key.cmd):
                    keyboard.press('v')
                    keyboard.release('v')
            except Exception as e:
                print(f"Could not automate Paste: {e}")

# Global instance
injector = TextInjector()
