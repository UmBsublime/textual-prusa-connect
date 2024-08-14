import datetime
from tkinter.ttk import Progressbar, Separator

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static, ProgressBar, Rule

from textual_prusa_connect.models import Printer


class DashboardWidget(Widget):
    printer = reactive(..., recompose=True)

    def __init__(self, *children: Widget, printer: Printer) -> None:
        super().__init__(*children)
        self.printer = printer
        self.add_class('--dashboard-category')

    def on_mount(self):
        self.update_printer()
        self.set_interval(self.app.refresh_rate, self.update_printer)

    def update_printer(self):
        self.printer = self.app.printer


class ToolStatus(DashboardWidget):
    DEFAULT_CSS = """
    ToolStatus {
        height: 8;
    }
    """

    def __init__(self, *children: Widget, printer: Printer) -> None:
        super().__init__(*children, printer=printer)
        self.border_title = "Tool Status"

    def compose(self):
        with Horizontal():
            if self.printer.slot:
                for tool_id, tool in self.printer.slot['slots'].items():
                    with Vertical():
                        yield Static(f"tool: [green]{tool_id}", classes='--cell')
                        yield Static(f"material: [green]{tool['material']}", classes='--lighter-background --cell')
                        yield Static(f"temp: [green]{tool['temp']}", classes='--cell')
                        yield Static(f"hotend fan: [green]{tool['fan_hotend']}", classes='--lighter-background --cell')
                        yield Static(f"print fan: [green]{tool['fan_print']}", classes='--cell')


class CurrentlyPrinting(DashboardWidget):
    DEFAULT_CSS = """
        CurrentlyPrinting {
            height: 15;
        }
        Rule {
            height: 1;
            margin: 0;
        }
        Horizontal, Vertical {
            height: auto;
        }
        """

    def __init__(self, *children: Widget, printer: Printer) -> None:
        super().__init__(*children, printer=printer)
        self.border_title = "Currently Printing"

    def compose(self) -> ComposeResult:

        """
        job_info={
          'origin_id': 690,
          'id': 677,
          'path': '/usb/NTS1ST~1.BGC',
          'progress': 0.0,
          'preview_url':
    '/app/teams/26502/files/yUbtnfNt9Ju2yVwvjIRp4gxZ5ik./preview',
          'print_height': 12,
          'total_height': 27.0,
      },
    """
        with Horizontal():
            yield Static("  📁  ", id='icon')
            with Vertical():
                with Horizontal():
                    with Vertical():
                        start = datetime.datetime.fromtimestamp(self.printer.job_info['start'])
                        end = datetime.datetime.fromtimestamp(
                            self.printer.job_info['start'] +
                            self.printer.job_info['time_remaining'] +
                            self.printer.job_info['time_printing']
                        )
                        yield Static(f'[yellow]{self.printer.job_info["display_name"]}', classes='--cell')
                        yield Static(f"Started: [blue]{start}", classes='--lighter-background --cell')
                        elapsed = datetime.timedelta(seconds=self.printer.job_info['time_printing'])
                        yield Static(f"Printing time: [blue]{elapsed}", classes='--cell')

                    with Vertical():
                        yield ProgressBar()
                        remaining = '00:00:00'
                        if self.printer.job_info['time_remaining'] != -1:
                            remaining = datetime.timedelta(seconds=self.printer.job_info['time_remaining'])
                        yield Static(f"End: [blue]{end}", classes='--lighter-background')
                        yield Static(f"Remaining time: [blue]{remaining}")
                yield Rule()

                yield Static(
                    f'Weight (g): [green]{self.printer.job_info["model_weight"]-self.printer.job_info["weight_remaining"]:.2f}/{self.printer.job_info["model_weight"]:.2f}')
                yield ProgressBar()
                yield ProgressBar()
