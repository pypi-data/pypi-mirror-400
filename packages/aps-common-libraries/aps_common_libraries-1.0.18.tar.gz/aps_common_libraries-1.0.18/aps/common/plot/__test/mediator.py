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
from AnyQt.QtCore import QObject, pyqtSignal
from AnyQt.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel


class SenderWindow(QWidget):
    """First window: emits a signal when its button is clicked."""
    message_sent = pyqtSignal(str)

    def __init__(self, title="Sender"):
        super().__init__()
        self.setWindowTitle(title)
        self._clicks = 0

        self.button = QPushButton("Send message")
        self.info = QLabel("Click the button to send a message")

        layout = QVBoxLayout(self)
        layout.addWidget(self.info)
        layout.addWidget(self.button)

        self.button.clicked.connect(self._on_click)

    def _on_click(self):
        self._clicks += 1
        msg = f"Hello from Sender! (click #{self._clicks})"
        # Emit the signal carrying the message
        self.message_sent.emit(msg)


class ReceiverWindow(QWidget):
    """Second window: updates a label when it receives a message."""
    def __init__(self, title="Receiver"):
        super().__init__()
        self.setWindowTitle(title)

        self.label = QLabel("No messages yet")
        self.label.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)

    def on_message(self, text: str):
        # Handle the dispatched signal by updating the label
        self.label.setText(f"Received: {text}")


class Mediator(QObject):
    """
    Mediator object that decouples Sender and Receiver.
    It listens to Sender.message_sent and forwards it to Receiver.on_message.
    """
    # Optional: re-expose a forwarding signal to keep Sender and Receiver unaware of each other
    forward_message = pyqtSignal(str)

    def __init__(self, sender: SenderWindow, receiver: ReceiverWindow):
        super().__init__()
        # Connect sender -> mediator
        sender.message_sent.connect(self._handle_sender_message)
        # Connect mediator -> receiver
        self.forward_message.connect(receiver.on_message)

    def _handle_sender_message(self, text: str):
        # Do any routing/transformation/logging here if needed
        self.forward_message.emit(text)


def main():
    app = QApplication(sys.argv)

    sender = SenderWindow("Window A — Sender")
    receiver = ReceiverWindow("Window B — Receiver")

    # Create mediator to wire them up
    mediator = Mediator(sender, receiver)
    _ = mediator  # keep a reference (optional, avoids accidental GC)

    # Show both windows side by side
    sender.move(200, 200)
    receiver.move(500, 200)
    sender.show()
    receiver.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()