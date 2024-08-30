from typing import Literal

from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widget import Widget

from textual_prusa_connect.messages import PrinterUpdated
from textual_prusa_connect.models import Printer, Tool
from textual_prusa_connect.widgets import Pretty


class ToolDetails(Widget):
    DEFAULT_CSS = """
    ToolDetails {
        width: 1fr;
        height: auto;
    }
    """

    def __init__(self, tool: Tool, color: Literal['blue', 'green', 'orange'] = 'blue'):
        super().__init__()
        self.tool = tool
        self.color = color

    def compose(self):
        """with Vertical():
            for i, item in enumerate(self.tool.model_dump().items()):
                k, v = item
                odd = i % 2 != 0
                field = Static(f"{nicer_string(k)}: [{self.color}]{v}")
                if odd:
                    field.add_class('--lighter-background')
                yield field"""

        with Vertical():
            for i, attr in enumerate(self.tool.model_dump().keys()):
                odd = i % 2 != 0
                field = Pretty(self.tool, attr, self.color)
                if odd:
                    field.add_class('--lighter-background')
                yield field


class ToolList(Widget):
    DEFAULT_CSS = """
        ToolList {
            height: auto;
        }
        """

    printer = reactive(..., recompose=True)

    def __init__(self, *children: Widget, printer: Printer) -> None:
        super().__init__(*children)
        self.printer = printer
        self.add_class('--dashboard-category')
        self.add_class('--requires-printer')
        self.border_title = 'Tool List'

    def compose(self):
        with Horizontal():
            for i, item in enumerate(self.printer.slot['slots'].items()):
                slot, value = item
                if int(slot) == self.printer.slot['active']:
                    tool = ToolDetails(Tool(id=slot, **value), color='green')
                else:
                    tool = ToolDetails(Tool(id=slot, **value))

                if i < len(self.printer.slot['slots']) - 1:
                    tool.add_class('--cell')
                yield tool

    def on_printer_updated(self, msg: PrinterUpdated):
        if msg.printer != self.printer:
            self.printer = msg.printer
