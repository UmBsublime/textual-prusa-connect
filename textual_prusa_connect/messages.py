from __future__ import annotations

from textual.message import Message

from textual_prusa_connect.models import Printer


class PrinterUpdated(Message):
    def __init__(self, printer: Printer):
        super().__init__()
        self.printer = printer
