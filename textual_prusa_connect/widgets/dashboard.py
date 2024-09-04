from datetime import datetime, timedelta
from typing import Any

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import ProgressBar, Static, TabPane

from textual_prusa_connect.messages import PrinterUpdated
from textual_prusa_connect.models import File, Printer
from textual_prusa_connect.widgets import Pretty
from textual_prusa_connect.widgets.file import PrintJobWidget, FileHistory
from textual_prusa_connect.widgets.tool import ToolList


class CurrentlyPrinting(Widget):
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

    printer = reactive(..., recompose=True)

    def __init__(self, *children: Widget, printer: Printer, file: File) -> None:
        super().__init__(*children)
        self.add_class('--dashboard-category')
        self.add_class('--requires-printer')
        self.printer = printer
        self.file = file
        self.border_title = "Currently Printing"
        self.progress_bar = ProgressBar(total=100, show_eta=False)
        self.weight_progress = ProgressBar(total=self.printer.job_info.get('model_weight', 0), show_eta=False)
        self.height_progress = ProgressBar(total=self.printer.job_info.get('total_height', 0), show_eta=False)

    #def on_mount(self):
    #    self.app.query_one('RichLog').write(self.file)

    def on_printer_updated(self, msg: PrinterUpdated):
        if msg.printer != self.printer:
            self.printer = msg.printer


    def compose(self) -> ComposeResult:
        """
      'estimated_printing_time_normal_mode': '8h 50m 57s',
      'max_layer_z': 47.45,
      'filament_used_mm3': 167200.0,
      'filament_used_cm3': 167.2,
      'filament_used_mm': 69515.75,
        """
        try:
            with Horizontal(classes='--main') as main:
                main.styles.padding = (0, 0, 1, 0)
                yield Static("  ⚙  ", classes='--icon')
                with Vertical():
                    yield Static(f'[yellow]{self.printer.job_info["display_name"]}')
                    with Horizontal():
                        with Vertical():
                            start = datetime.fromtimestamp(self.printer.job_info['start'])
                            end = datetime.fromtimestamp(
                                self.printer.job_info['start'] +
                                self.printer.job_info['time_remaining'] +
                                self.printer.job_info['time_printing']
                            )
                            yield Static(f"Started: [blue]{start}")
                            estimated_end = self.printer.job_info['start'] + self.file.meta['estimated_print_time']
                            yield Static(f"Prusa end: [blue]{datetime.fromtimestamp(estimated_end)}")
                            yield Static(f"Real End: [blue]{end}")

                            yield Static(f'Prusa duration: [blue]{timedelta(seconds=self.file.meta["estimated_print_time"])}')
                            real_duration = self.printer.job_info['time_printing'] + self.printer.job_info['time_remaining']
                            yield Static(f'Real duration: [blue]{timedelta(seconds=real_duration)}')

                            elapsed = timedelta(seconds=self.printer.job_info['time_printing'])
                            remaining = '00:00:00'
                            if self.printer.job_info['time_remaining'] != -1:
                                remaining = timedelta(seconds=self.printer.job_info['time_remaining'])
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
                                    f' [green]{remaining:.2f}/{self.printer.job_info["model_weight"]:.2f}[/] grams (weight)')
                            with Horizontal():
                                self.height_progress.update(progress=self.printer.axis_z)
                                yield self.height_progress
                                yield Static(
                                    f' [green]{self.printer.axis_z:.2f}/{self.printer.job_info["total_height"]:.2f}[/] mm (height)')
                        with Vertical():
                            yield Pretty(self.file.meta, 'printer_model')
                            yield Pretty(self.file.meta, 'filament_type')
                            yield Static(f"Filament length: [blue]{self.file.meta['filament_used_m']:.2f} meters")
                            yield Static(f"Filament weight: [blue]{self.file.meta['filament_used_g']:.2f} grams")
                            yield Pretty(self.file.meta, 'filament_cost', unit="$")
                            yield Pretty(self.file.meta, 'nozzle_diameter')
                            yield Pretty(self.file.meta, 'bed_temperature')
                            yield Static(f"Layer height: [blue]{self.file.meta['layer_height']}")
                            yield Static(f"Fill density: [blue]{self.file.meta['fill_density']}")
                            yield Static(f"Brim width: [blue]{self.file.meta['brim_width']}")
                            yield Static(f"Support material: [blue]{bool(self.file.meta['support_material'])}")
                            yield Static(f"Ironing: [blue]{bool(self.file.meta['ironing'])}")
        except (TypeError, KeyError):
            self.notify("Couldn't load 'currently printing' section", severity='error')
            self.remove()


class EventContainer(Widget):
    DEFAULT_CSS = """
        EventContainer {
            height: auto;
        }
        """
    printer = reactive(..., recompose=True)

    def __init__(self) -> None:
        super().__init__()
        self.add_class('--dashboard-category')
        self.border_title = "Event log"

    def compose(self):
        yield Static("Hi")


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
        self.can_focus = True

    def compose(self) -> ComposeResult:
        for i, item in enumerate(self.items):
            yield self.item_type(item)
            if i < len(self.items) - 1:
                yield Static(' ')


class DashboardPane(TabPane):
    printer: Printer = reactive(..., recompose=True)

    def __init__(self, client, printer: Printer) -> None:
        super().__init__(title="Dashboard")
        self.client = client
        self.printer = printer

    def compose(self):
        with VerticalScroll():
            yield ToolList(printer=self.printer)

            with Container(id='currently-printing-placeholder'):
                yield CurrentlyPrinting(printer=self.printer, file=self.client.get_jobs(limit=1)[0].file)

            yield FileHistory(files=self.client.get_files(self.printer.uuid.get_secret_value(), limit=3))
            yield HistoryContainer(items=self.client.get_jobs(limit=3),
                                   item_type=PrintJobWidget,
                                   title="Print history")
            yield EventContainer()
