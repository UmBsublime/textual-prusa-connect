from textual.containers import Vertical, Horizontal
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

from textual_prusa_connect.models import Printer, Tool
from textual_prusa_connect.utils import nicer_string


class ToolDetails(Widget):
    DEFAULT_CSS = """
    ToolDetails {
        width: 1fr;
        height: auto;
    }
    """

    def __init__(self, tool: Tool, color = 'blue'):
        super().__init__()
        self.tool = tool
        self.color = color

    def compose(self):
        with Vertical():
            for i, item in enumerate(self.tool.model_dump().items()):
                k, v = item
                odd = i % 2 != 0
                field = Static(f"{nicer_string(k)}: [{self.color}]{v}")
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

    def on_mount(self):
        self.update_printer()
        self.set_interval(self.app.refresh_rate, self.update_printer)

    def update_printer(self):
        self.printer = self.app.printer