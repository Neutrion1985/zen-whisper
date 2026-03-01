from pynput import keyboard
import threading
from zenwhisper.core.config import config

class HotkeyListener:
    def __init__(self, callback):
        self.callback = callback
        self.hotkey_str = config.get("hotkey") or '<alt>+z'
        self.listener = None
        self._thread = None

    def _on_activate(self):
        print(f"Hotkey {self.hotkey_str} activated!")
        if self.callback:
            self.callback()

    def start(self):
        """Starts the global hotkey listener in a background thread.
        Note: on Wayland, pynput might fail. We recommend using system-level shortcuts 
        calling 'zenwhisper --toggle'.
        """
        try:
            def run_listener():
                with keyboard.GlobalHotKeys({
                    self.hotkey_str: self._on_activate
                }) as h:
                    self.listener = h
                    h.join()

            self._thread = threading.Thread(target=run_listener, daemon=True)
            self._thread.start()
            print(f"Global hotkey listener started (pynput): {self.hotkey_str}")
        except Exception as e:
            print(f"Pynput listener failed (expected on some Wayland setups): {e}")

    def restart(self, new_hotkey=None):
        """Restart the listener with a new hotkey combo."""
        if new_hotkey:
            self.hotkey_str = new_hotkey
        
        # Stop existing listener
        if self.listener:
            try:
                self.listener.stop()
            except Exception:
                pass
        
        # Re-start
        self.start()
        print(f"Hotkey listener restarted with: {self.hotkey_str}")
