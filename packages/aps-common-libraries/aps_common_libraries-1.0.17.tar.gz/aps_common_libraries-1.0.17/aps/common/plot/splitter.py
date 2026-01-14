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

from AnyQt.QtCore import Qt, QSize
from AnyQt.QtWidgets import (
    QApplication, QSplitter, QSplitterHandle, QToolButton, QStyle, QMainWindow
)

class ToggleDirection:
    RemoveLeft   = 0
    RemoveRight  = 1
    RemoveTop    = 2
    RemoveBottom = 3

class Action:
    Remove = 0
    Add    = 1

class ToggleSplitterHandle(QSplitterHandle):
    def __init__(self, direction, orientation, parent):
        super().__init__(orientation, parent)
        assert orientation in [Qt.Horizontal, Qt.Vertical]
        if orientation == Qt.Horizontal: assert direction in [ToggleDirection.RemoveLeft, ToggleDirection.RemoveRight]
        if orientation == Qt.Vertical:   assert direction in [ToggleDirection.RemoveBottom, ToggleDirection.RemoveTop]

        self._direction = direction

        self.button = QToolButton(self)
        self.button.setAutoRaise(True)
        self.button.setCursor(Qt.PointingHandCursor)
        self.button.setFocusPolicy(Qt.NoFocus)
        self.button.setFixedSize(24, 24)
        self.button.clicked.connect(self.toggle_pane)
        self.update_icon()

    def sizeHint(self):
        base = super().sizeHint()
        if   self.orientation() == Qt.Horizontal: return QSize(max(base.width(), 28), base.height())
        elif self.orientation() == Qt.Vertical:   return QSize(base.width(), max(base.height(), 28))

    def resizeEvent(self, event):
        super().resizeEvent(event)

        w, h = self.size().width(), self.size().height()
        bw, bh = self.button.size().width(), self.button.size().height()
        self.button.move((w - bw) // 2, (h - bh) // 2)

    def _resize_parents(self, size: int, action):
        current = self
        while current is not None:
            parent = current.parent()
            if not parent is None:
                if self.orientation() == Qt.Horizontal:
                    current_size = parent.size().width()
                    if action == Action.Remove: new_size = max(28, current_size - size)
                    elif action == Action.Add:  new_size = max(28, current_size + size)
                    parent.setFixedWidth(new_size)
                elif self.orientation() == Qt.Vertical:
                    current_size = parent.size().height()
                    if action == Action.Remove: new_size = max(28, current_size - size)
                    elif action == Action.Add:  new_size = max(28, current_size + size)
                    parent.setFixedHeight(size)
            else: # reached the container
                if hasattr(current, "get_main_window"): current_position = current.get_main_window().pos()
                else:                                   current_position = current.pos()

                if self.orientation() == Qt.Horizontal:
                    if self._direction == ToggleDirection.RemoveLeft:
                        if action == Action.Remove: current.move(current_position.x() + size, current_position.y())
                        elif action == Action.Add:  current.move(current_position.x() - size, current_position.y())
                    else:
                        pass # stay where it is
                elif self.orientation() == Qt.Vertical:
                    if self._direction == ToggleDirection.RemoveTop:
                        if action == Action.Remove: current.move(current_position.x(), current_position.y() - size)
                        elif action == Action.Add:  current.move(current_position.x(), current_position.y() + size)
                    else:
                        pass

            current = parent

    def toggle_pane(self):
        splitter = self.splitter()

        if self._direction in [ToggleDirection.RemoveLeft, ToggleDirection.RemoveBottom]:
            if not getattr(splitter, "_collapsed_left", False):
                splitter._saved_sizes = splitter.sizes()
                sizes = [0, splitter._saved_sizes[1]]  # collapse left to 0
                self._resize_parents(splitter._saved_sizes[0], Action.Remove)
                splitter.setSizes(sizes)
                splitter._collapsed_left = True
            else:
                if hasattr(splitter, "_saved_sizes") and any(splitter._saved_sizes):
                    splitter.setSizes(splitter._saved_sizes)
                    self._resize_parents(splitter._saved_sizes[0], Action.Add)
                else:
                    splitter.setSizes([1, 1])
                splitter._collapsed_left = False
        elif self._direction in [ToggleDirection.RemoveRight, ToggleDirection.RemoveBottom]:
            if not getattr(splitter, "_collapsed_right", False):
                splitter._saved_sizes = splitter.sizes()
                sizes = [splitter._saved_sizes[0], 0]  # right to 0
                self._resize_parents(splitter._saved_sizes[1], Action.Remove)
                splitter.setSizes(sizes)
                splitter._collapsed_right = True
            else:
                if hasattr(splitter, "_saved_sizes") and any(splitter._saved_sizes):
                    splitter.setSizes(splitter._saved_sizes)
                    self._resize_parents(splitter._saved_sizes[1], Action.Add)
                else:
                    splitter.setSizes([1, 1])
                splitter._collapsed_right = False

        self.update_icon()

    def update_icon(self):
        style = QApplication.style()

        if self._direction == ToggleDirection.RemoveLeft:
            left_collapsed = getattr(self.splitter(), "_collapsed_left", False)

            if self.orientation() == Qt.Horizontal:
                icon = style.standardIcon(QStyle.SP_ArrowLeft if left_collapsed else QStyle.SP_ArrowRight)
            else:
                icon = style.standardIcon(QStyle.SP_ArrowUp if left_collapsed else QStyle.SP_ArrowDown)
        elif self._direction == ToggleDirection.RemoveRight:
            right_collapsed = getattr(self.splitter(), "_collapsed_right", False)

            if self.orientation() == Qt.Horizontal:
                icon = style.standardIcon(QStyle.SP_ArrowRight if right_collapsed else QStyle.SP_ArrowLeft)
            else:
                icon = style.standardIcon(QStyle.SP_ArrowDown if right_collapsed else QStyle.SP_ArrowUp)

        self.button.setIcon(icon)
        self.button.setIconSize(QSize(18, 18))

class ToggleSplitter(QSplitter):
    def __init__(self,
                 direction=ToggleDirection.RemoveLeft,
                 orientation=Qt.Horizontal,
                 saved_sizes=[300, 600],
                 parent=None):
        super().__init__(orientation, parent)
        assert direction in [ToggleDirection.RemoveLeft, ToggleDirection.RemoveRight]

        self._direction = direction

        if self._direction == ToggleDirection.RemoveLeft:    self._collapsed_left = False
        elif self._direction == ToggleDirection.RemoveRight: self._collapsed_right = False

        self._saved_sizes = saved_sizes

    def createHandle(self):
        return ToggleSplitterHandle(self._direction, self.orientation(), self)
