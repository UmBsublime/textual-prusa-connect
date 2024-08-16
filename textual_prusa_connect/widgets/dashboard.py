import datetime
import time
from typing import Any

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive, Reactive
from textual.widget import Widget
from textual.widgets import Static, ProgressBar, Rule

from textual_prusa_connect.models import Printer, Job, File
from textual_prusa_connect.utils import is_wsl


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
            height: auto;
        }
        Rule {
            height: 1;
            margin: 0;
        }
        Horizontal, Vertical {
            height: auto;
        }
        Static {
            width: 1fr;
        }
        """

    def __init__(self, *children: Widget, printer: Printer, file: File) -> None:
        super().__init__(*children, printer=printer)
        self.file = file
        self.border_title = "Currently Printing"
        self.progress_bar = ProgressBar(total=100, show_eta=False)
        self.weight_progress = ProgressBar(total=self.printer.job_info['model_weight'], show_eta=False)
        self.height_progress = ProgressBar(total=self.printer.job_info['total_height'], show_eta=False)

    def on_mount(self):
        self.app.query_one('RichLog').write(self.file)

    def compose(self) -> ComposeResult:

        """
          'estimated_print_time': 31857,                                                                                                                              ▆▆
          'estimated_printing_time_normal_mode': '8h 50m 57s',
          'printer_model': 'XL5IS',
          'layer_height': 0.25,
          'fill_density': '15%',
          'brim_width': 0,
          'support_material': 1,
          'ironing': 0,
          'total_height': 47.45,
          'max_layer_z': 47.45,
          'filament_used_mm3': 167200.0,
          'filament_used_cm3': 167.2,
          'filament_used_m': 69.51575,
          'filament_used_mm': 69515.75,
          'filament_used_g': 207.33,
          'filament_cost': 5.27,

    """
        with Horizontal():
            yield Static("  ⚙  ", classes='--icon')
            with Vertical():
                yield Static(f'[yellow]{self.printer.job_info["display_name"]}')
                with Horizontal():
                    with Vertical():
                        start = datetime.datetime.fromtimestamp(self.printer.job_info['start'])
                        end = datetime.datetime.fromtimestamp(
                            self.printer.job_info['start'] +
                            self.printer.job_info['time_remaining'] +
                            self.printer.job_info['time_printing']
                        )
                        yield Static(f"Started: [blue]{start}")
                        yield Static(f"Estimate end: [blue]")
                        yield Static(f"Real End: [blue]{end}")
                        elapsed = datetime.timedelta(seconds=self.printer.job_info['time_printing'])
                        remaining = '00:00:00'
                        if self.printer.job_info['time_remaining'] != -1:
                            remaining = datetime.timedelta(seconds=self.printer.job_info['time_remaining'])
                        yield Static(f"Printing time: [blue]{elapsed}")

                        yield Static(f"Remaining time: [blue]{remaining}")
                        with Horizontal():
                            self.progress_bar.update(progress=self.printer.job_info['progress'])
                            yield self.progress_bar
                            yield Static(f" [green]{elapsed}/{elapsed+remaining}")
                        with Horizontal():
                            remaining = self.printer.job_info['model_weight'] - self.printer.job_info[
                                'weight_remaining']
                            self.weight_progress.update(progress=remaining)
                            yield self.weight_progress
                            yield Static(
                                f' [green]{remaining:.2f}/{self.printer.job_info["model_weight"]:.2f}[/] grams')
                        with Horizontal():
                            self.height_progress.update(progress=self.printer.axis_z)
                            yield self.height_progress
                            yield Static(
                                f' [green]{self.printer.axis_z:.2f}/{self.printer.job_info["total_height"]:.2f}[/] mm')
                    with Vertical():
                        yield Static(f"Material: [blue]{self.file.meta['filament_type']}")
                        yield Static(f"Nozzle: [blue]{self.file.meta['nozzle_diameter']}")
                        yield Static(f"Bed temp: [blue]{self.file.meta['bed_temperature']}")
                        yield Static(f"Layer height: [blue]{self.file.meta['layer_height']}")
                        yield Static(f"Fill density: [blue]{self.file.meta['fill_density']}")
                        yield Static(f"Brim width: [blue]{self.file.meta['brim_width']}")
                        yield Static(f"Support material: [blue]{bool(self.file.meta['support_material'])}")
                        yield Static(f"Ironing: [blue]{bool(self.file.meta['ironing'])}")
                        yield Static(f"Cost: [blue]{self.file.meta['filament_cost']}$")
class BaseFileWidget(Widget):
    DEFAULT_CSS = """
        Vertical, Horizontal {
            width: 1fr;
        }
        Static {
            width: 1fr;
        }
        """

    def __init__(self) -> None:
        super().__init__()
        self.file_path = None
        self.add_class('--file-widget')

    def on_click(self, event: 'Event') -> None:
        url = f"https://connect.prusa3d.com{self.file_path}"
        if not is_wsl():
            self.app.open_url(url)
            self.notify("Browser opened")
        else:
            self.notify("Not available on WSL\n"+url, severity="warning")


class PrintJob(BaseFileWidget):
    def __init__(self, job: Job) -> None:
        super().__init__()
        self.job = job
        self.tooltip = 'Click to open image preview in browser'
        self.file_path = self.job.file.preview_url

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
                    if self.job.end != -1:
                        delta = datetime.timedelta(seconds=self.job.end - self.job.start)
                    else:
                        delta = "---"
                    yield Static(f'Real time: [blue]{delta}')
                with Horizontal():
                    yield Static(f'Layer height: [blue]{self.job.file.meta["layer_height"]}', classes='--cell')
                    yield Static(f'Nozzle size: [blue]{self.job.file.meta["nozzle_diameter"]}', classes='--cell')
                    if self.job.end == -1:
                        yield Static(f'Print end: [blue]---')
                    else:
                        yield Static(f'Print end: [blue]{datetime.datetime.fromtimestamp(self.job.end)}')


class PrintFile(BaseFileWidget):
    def __init__(self, file: File) -> None:
        super().__init__()
        self.file = file
        self.tooltip = 'Click to open image preview in browser'
        self.file_path = self.file.preview_url

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
