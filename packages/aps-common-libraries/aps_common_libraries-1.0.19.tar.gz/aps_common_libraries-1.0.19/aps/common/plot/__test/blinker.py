import sys
from AnyQt import QtCore, QtWidgets

class BlinkingBorderButton(QtWidgets.QPushButton):
    def __init__(self, text="", parent=None, *,
                 period_ms=500,
                 on_color="#ff3b30",
                 off_color="#999999",
                 border_width=2,
                 radius=8):
        super().__init__(text, parent)
        self._on = False

        # Size instead of padding
        self.setMinimumSize(120, 36)

        # Set stylesheet ONCE; use a dynamic property to flip border color
        self.setStyleSheet(f"""
        QPushButton {{
            border: {border_width}px solid {off_color};
            border-radius: {radius}px;
            background: palette(button);
        }}
        QPushButton[blink_on="true"] {{
            border-color: {on_color};
        }}
        """)

        self._timer = QtCore.QTimer(self, interval=period_ms)
        self._timer.timeout.connect(self._tick)
        self._timer.start()

    def _tick(self):
        self._on = not self._on
        self.setProperty("blink_on", self._on)
        # repolish so the style sees the property change
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = QtWidgets.QWidget()
    w.setWindowTitle("Blinking Border Button")
    lay = QtWidgets.QVBoxLayout(w)

    btn = BlinkingBorderButton("Blinking Border", period_ms=400)
    lay.addWidget(btn)

    # Toggle checkbox
    chk = QtWidgets.QCheckBox("Blinking enabled")
    chk.setChecked(True)
    def on_toggled(ok):
        if ok: btn._timer.start()
        else:  btn._timer.stop(); btn.setProperty("blink_on", False); btn.style().unpolish(btn); btn.style().polish(btn)
    chk.toggled.connect(on_toggled)
    lay.addWidget(chk)

    w.resize(300, 120)
    w.show()
    sys.exit(app.exec())
