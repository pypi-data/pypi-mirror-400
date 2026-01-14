#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------- #
# Copyright (c) 2025, UChicago Argonne, LLC. All rights reserved.         #
#                                                                         #
# Copyright 2025. UChicago Argonne, LLC. This software was produced       #
# under U.S. Government contract DE-AC02-06CH11357 for Argonne National   #
# Laboratory (ANL), which is operated by UChicago Argonne, LLC for the    #
# U.S. Department of Energy. The U.S. Government has rights to use,       #
# reproduce, and distribute this software.  NEITHER THE GOVERNMENT NOR    #
# UChicago Argonne, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR        #
# ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If software is     #
# modified to produce derivative works, such modified software should     #
# be clearly marked, so as not to confuse it with the version available   #
# from ANL.                                                               #
#                                                                         #
# Additionally, redistribution and use in source and binary forms, with   #
# or without modification, are permitted provided that the following      #
# conditions are met:                                                     #
#                                                                         #
#     * Redistributions of source code must retain the above copyright    #
#       notice, this list of conditions and the following disclaimer.     #
#                                                                         #
#     * Redistributions in binary form must reproduce the above copyright #
#       notice, this list of conditions and the following disclaimer in   #
#       the documentation and/or other materials provided with the        #
#       distribution.                                                     #
#                                                                         #
#     * Neither the name of UChicago Argonne, LLC, Argonne National       #
#       Laboratory, ANL, the U.S. Government, nor the names of its        #
#       contributors may be used to endorse or promote products derived   #
#       from this software without specific prior written permission.     #
#                                                                         #
# THIS SOFTWARE IS PROVIDED BY UChicago Argonne, LLC AND CONTRIBUTORS     #
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT       #
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS       #
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL UChicago     #
# Argonne, LLC OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,        #
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,    #
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;        #
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER        #
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT      #
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN       #
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE         #
# POSSIBILITY OF SUCH DAMAGE.                                             #
# ----------------------------------------------------------------------- #
import sys
from AnyQt.QtCore import Qt
from AnyQt.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QFrame
)

from aps.common.plot.splitter import ToggleSplitter, ToggleDirection

class MainWindow(QMainWindow):
    def __init__(self, direction=ToggleDirection.RemoveLeft):
        super().__init__()
        self.setWindowTitle("Custom Splitter: Collapse Right Pane")
        self.resize(550, 550)

        splitter = ToggleSplitter(direction=direction, orientation=Qt.Horizontal)

        left  = self._pane("Left pane\n(I stay when the right collapses)")
        right = self._pane("Right pane\n(click the arrow to hide/show me)")


        if direction == ToggleDirection.RemoveLeft:
            right.setMinimumWidth(0)
            left.setMinimumWidth(150)
        elif direction == ToggleDirection.RemoveRight:
            right.setMinimumWidth(150)
            left.setMinimumWidth(0)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setHandleWidth(28)
        splitter.setSizes([500, 500])

        # Make sure panes are allowed to collapse
        splitter.setCollapsible(0, True)
        splitter.setCollapsible(1, True)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(splitter)
        layout.setContentsMargins(6, 6, 6, 6)
        self.setCentralWidget(container)

    def _pane(self, text):
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setObjectName("pane")
        v = QVBoxLayout(frame)
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignCenter)
        v.addWidget(lbl)
        frame.setStyleSheet("""
            QFrame#pane { background: #f6f8fa; border: 1px solid #d0d7de; border-radius: 8px; }
            QLabel { font-size: 14px; color: #24292f; }
        """)
        return frame


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow(direction=ToggleDirection.RemoveLeft)
    w.show()
    sys.exit(app.exec())