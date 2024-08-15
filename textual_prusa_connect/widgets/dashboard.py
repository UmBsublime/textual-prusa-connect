import datetime
from typing import Any

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static, ProgressBar, Rule

from textual_prusa_connect.models import Printer, Job, File


class BaseDashboardWidget(Widget):
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


class ToolStatus(BaseDashboardWidget):
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


class CurrentlyPrinting(BaseDashboardWidget):
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
            yield Static("  📁  ", classes='--icon')
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


class PrintJob(Widget):
    DEFAULT_CSS = """
    PrintJob {
        height: 3;
    }
    Vertical, Horizontal {
        width: 1fr;
    }
    Static {
        width: 1fr;
    }

    """

    def __init__(self, job: Job) -> None:
        super().__init__()
        self.job = job
        self.tooltip = 'Click to open image preview in browser'

    def compose(self):
        with Horizontal():
            yield Static("  🗋  ", classes='--icon')
            with Vertical(classes='--lighter-background'):
                with Horizontal():
                    yield Static(f'[yellow]{self.job.file.name}')
                    yield Static(f'[green]{self.job.state}')
                with Horizontal(classes='--dimgrey-background'):
                    yield Static(f'Printer: [blue]{self.job.file.meta["printer_model"]}', classes='--cell')
                    yield Static(f'Material: [blue]{self.job.file.meta["filament_type"]}', classes='--cell')
                    delta = datetime.timedelta(seconds=self.job.end - self.job.start)
                    yield Static(f'Real time: [blue] {delta}')
                with Horizontal():
                    yield Static(f'Layer height: [blue]{self.job.file.meta["layer_height"]}', classes='--cell')
                    yield Static(f'Nozzle size: [blue]{self.job.file.meta["nozzle_diameter"]}', classes='--cell')
                    yield Static(f'Print end: [blue]{datetime.datetime.fromtimestamp(self.job.end)}')


    def on_click(self, event: 'Event') -> None:
        self.app.open_url(f"https://connect.prusa3d.com{self.job.file.preview_url}")


class PrintFile(Widget):
    DEFAULT_CSS = """
    PrintFile {
        height: 3;
    }
    Vertical, Horizontal {
        width: 1fr;
    }
    Static {
        width: 1fr;
    }

    """

    def __init__(self, file: File) -> None:
        super().__init__()
        self.file = file
        self.tooltip = 'Click to open image preview in browser'

    def compose(self):
        with Horizontal():
            yield Static("  🗋  ", classes='--icon')
            with Vertical(classes='--lighter-background'):
                with Horizontal():
                    yield Static(f'[yellow]{self.file.name}')
                    yield Static(f'[green]')
                with Horizontal(classes='--dimgrey-background'):
                    yield Static(f'Printer: [blue]{self.file.meta["printer_model"]}', classes='--cell')
                    yield Static(f'Material: [blue]{self.file.meta["filament_type"]}', classes='--cell')
                    delta = datetime.timedelta(seconds=self.file.meta['estimated_print_time'])
                    yield Static(f'Estimate time: [blue] {delta}')
                with Horizontal():
                    yield Static(f'Layer height: [blue]{self.file.meta["layer_height"]}', classes='--cell')
                    yield Static(f'Nozzle size: [blue]{self.file.meta["nozzle_diameter"]}', classes='--cell')
                    yield Static(f'Date added: [blue]{datetime.datetime.fromtimestamp(self.file.uploaded)}')


    def on_click(self, event: 'Event') -> None:
        self.app.open_url(f"https://connect.prusa3d.com{self.file.preview_url}")


class HistoryContainer(Widget):
    DEFAULT_CSS = """
    HistoryContainer {
        height: auto;
    }

    """

    def __init__(self, items: list[Any], title='PLACEHOLDER', item_type=None) -> None:
        super().__init__()
        self.items = items
        self.border_title = title
        self.add_class('--dashboard-category')
        self.item_type = item_type

    def compose(self) -> ComposeResult:
        for i, item in enumerate(self.items):
            yield self.item_type(item)
            if i < len(self.items) - 1:
                yield Static(' ')
