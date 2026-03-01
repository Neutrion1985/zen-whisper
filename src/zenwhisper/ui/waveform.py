import sys
import math
import random
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import (QPainter, QColor, QPen, QLinearGradient, QBrush, 
                          QPainterPath, QRadialGradient)

class WaveformWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        # Window Setup: Frameless, Transparent, Always on Top, No focus
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool |
            Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Smaller, more compact size
        self.setFixedSize(280, 48)
        self.active = False
        self.processing = False
        self.amplitude = 0.05 
        self.target_amplitude = 0.05
        self.phase = 0.0
        self.breath_phase = 0.0
        self.pulse_phase = 0.0
        self.opacity = 0.0      # For fade in/out
        self.color_factor = 0.0  # 0.0 = Normal (Cyan/Purple), 1.0 = Processing (Yellow Neon)
        
        # Multi-layer waves with neon colors
        self.waves = [
            {'speed': 0.12, 'opacity': 200, 'freq': 0.8, 'color': QColor(150, 0, 255), 'width': 3.0},   # Purple (primary)
            {'speed': 0.08, 'opacity': 140, 'freq': 1.1, 'color': QColor(0, 220, 255), 'width': 2.0},    # Cyan
            {'speed': 0.06, 'opacity': 100, 'freq': 0.5, 'color': QColor(255, 100, 255), 'width': 1.5},   # Pink
        ]
        
        # Animation Timer (60 FPS)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)

    def set_amplitude(self, level):
        """Sets the new target amplitude (0.0 to 1.0)."""
        if not self.active and not self.processing:
            return # Ignore updates during fade out
        boosted = math.sqrt(level) * 2.0
        self.target_amplitude = max(0.05, min(0.95, boosted))

    def update_animation(self):
        # State logic
        is_visible = self.active or self.processing
        
        # Opacity: Factor 0.04 results in ~1.2s fade @ 60fps (very premium)
        target_opacity = 1.0 if is_visible else 0.0
        self.opacity += (target_opacity - self.opacity) * 0.04
        
        # Color & Amplitude preservation during fade-out
        if is_visible:
            # Active path
            target_color = 1.0 if self.processing else 0.0
            self.color_factor += (target_color - self.color_factor) * 0.1
            self.amplitude += (self.target_amplitude - self.amplitude) * 0.12
        else:
            # Fading out path: "Living Fade"
            # Keep the amplitude alive (0.2) so it doesn't look like a flat line
            # but also shrink it slightly from its last state.
            self.amplitude += (0.2 - self.amplitude) * 0.04
            
            if self.opacity < 0.02 and not is_visible:
                self.hide()
                self.color_factor = 0.0 # Reset for next use
                self.amplitude = 0.05
                
        self.phase += 0.12
        self.breath_phase += 0.03
        self.pulse_phase += 0.08
        
        if self.opacity > 0.01:
            self.update()

    def paintEvent(self, event):
        if self.opacity < 0.01: return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setOpacity(self.opacity)
        
        w = float(self.width())
        h = float(self.height())
        mid_y = h / 2
        
        # Background Capsule
        rect = QRectF(4, 4, w - 8, h - 8)
        capsule_radius = (h - 8) / 2
        
        # Background pulsing
        if self.processing or (not self.active and self.color_factor > 0.5):
            bg_alpha = int(180 + 30 * math.sin(self.pulse_phase))
        else:
            bg_alpha = int(160 + 40 * math.sin(self.breath_phase))
        
        # Main background
        painter.setPen(Qt.PenStyle.NoPen)
        bg_color = QColor(15, 15, 20, bg_alpha)
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(rect, capsule_radius, capsule_radius)
        
        # Border
        border_pen = QPen(QColor(150, 100, 255, 60))
        border_pen.setWidthF(1.0)
        painter.setPen(border_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect, capsule_radius, capsule_radius)

        # Draw waves
        padding = 20
        draw_w = w - 2 * padding
        
        for wave_cfg in self.waves:
            # Interpolate between normal and yellow neon
            base_color = QColor(wave_cfg['color'])
            target_color = QColor("#CCFF00")
            
            r = int(base_color.red() + (target_color.red() - base_color.red()) * self.color_factor)
            g = int(base_color.green() + (target_color.green() - base_color.green()) * self.color_factor)
            b = int(base_color.blue() + (target_color.blue() - base_color.blue()) * self.color_factor)
            
            wave_color = QColor(r, g, b)
            wave_color.setAlpha(wave_cfg['opacity'])
            
            # Setup pencils
            main_pen = QPen(wave_color)
            main_pen.setWidthF(wave_cfg['width'])
            main_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            main_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            
            glow_pen = QPen(QColor(wave_color.red(), wave_color.green(), wave_color.blue(), int(wave_cfg['opacity'] * 0.3)))
            glow_pen.setWidthF(wave_cfg['width'] * 3)
            glow_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            
            segments = 40 
            points = []
            for i in range(segments + 1):
                t = i / segments
                x = padding + t * draw_w
                envelope = math.sin(t * math.pi)
                
                if self.processing or (not self.active and self.color_factor > 0.5):
                    # Pulsing active wave
                    y_offset = math.sin(t * 3.0 * math.pi + self.pulse_phase) * (h * 0.22) * envelope
                else:
                    # Reactive wave
                    y1 = math.sin(t * 4.0 * wave_cfg['freq'] + self.phase * wave_cfg['speed'] * 12)
                    y2 = math.cos(t * 7.0 * wave_cfg['freq'] + self.phase * wave_cfg['speed'] * 18) * 0.4
                    y_offset = (y1 + y2) * self.amplitude * (h * 0.45) * envelope
                
                points.append((x, mid_y + y_offset))
            
            # Path construction
            if len(points) > 2:
                path = QPainterPath()
                path.moveTo(points[0][0], points[0][1])
                for i in range(len(points) - 1):
                    p_curr = points[i]
                    p_next = points[i+1]
                    mid_x = (p_curr[0] + p_next[0]) / 2
                    mid_y_pt = (p_curr[1] + p_next[1]) / 2
                    path.quadTo(p_curr[0], p_curr[1], mid_x, mid_y_pt)
                path.lineTo(points[-1][0], points[-1][1])
                
                # Draw path twice (Glow then Main)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.setPen(glow_pen)
                painter.drawPath(path)
                painter.setPen(main_pen)
                painter.drawPath(path)

    def show_zen(self):
        self.active = True
        self.processing = False
        self.show()
        # Center near bottom of screen
        screen = QApplication.primaryScreen().geometry()
        self.move(
            int((screen.width() - self.width()) / 2),
            int(screen.height() - self.height() - 60)
        )
        self.update()

    def show_processing(self):
        self.active = False
        self.processing = True
        self.show()

    def hide_zen(self):
        self.active = False
        self.processing = False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = WaveformWidget()
    w.show_zen()
    t = QTimer()
    t.timeout.connect(lambda: w.set_amplitude(random.random()))
    t.start(500)
    sys.exit(app.exec())
