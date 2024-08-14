import datetime

from textual.containers import Vertical, Horizontal
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static, Button

from textual_prusa_connect.models import Printer


class PrinterHeader(Widget):
    DEFAULT_CSS = """
    PrinterHeader {
        height: auto;
        border: round lightgrey;
        background: $background-lighten-2;
        border-title-color: $primary-lighten-2;
        Static {
            width: 1fr;
        }
        Vertical {
            height: auto;
        }
        Horizontal {
            height: auto;
        }
    }
    """

    printer = reactive(..., recompose=True)

    def __init__(self, *children: Widget, printer: Printer) -> None:
        super().__init__(*children)
        self.printer = printer

    def compose(self):
        with Horizontal():
            yield Static("  🖨  ", id='icon')
            with Vertical(classes='--cell'):
                yield Static(f"name: [blue]{self.printer.name} - {self.printer.printer_model}")
                yield Static(f"state: [blue]{self.printer.printer_state}", classes='--lighter-background')
                yield Static(f"location: [blue]{self.printer.location}")
            with Vertical(classes='--cell'):
                yield Static(f"tool: [blue]{self.printer.slot['active']}/{self.printer.slots}")
                yield Static(f"nozzle diameter: [blue]{self.printer.nozzle_diameter}", classes='--lighter-background')
                yield Static(f"material: [blue]{self.printer.filament['material']}")
            with Vertical(classes='--cell'):
                yield Static(f"nozzle temp: [blue]{self.printer.temp['temp_nozzle']}/{self.printer.temp['target_nozzle']}")
                yield Static(f"bed temp: [blue]{self.printer.temp['temp_bed']}/{self.printer.temp['target_bed']}", classes='--lighter-background')
                yield Static(f"current z: [blue]{self.printer.axis_z}mm")
            with Vertical():
                yield Static(f"speed: [blue]{self.printer.speed}%")
                if self.printer.job_info:
                    yield Static(f"progress: [blue]{self.printer.job_info['progress']:.1f}%", classes='--lighter-background')
                else:
                    yield Static(' ', classes='--lighter-background')
                eta = ''
                if self.printer.job_info:
                    elapsed = datetime.timedelta(seconds=self.printer.job_info['time_printing'])
                    remaining = '00:00:00'
                    if self.printer.job_info['time_remaining'] != -1:
                        remaining = datetime.timedelta(seconds=self.printer.job_info['time_remaining'])
                    eta = f'[green]{elapsed} / {remaining}'
                yield Static(eta)
            yield Button("🚀 Set Ready", disabled=self.printer.printer_state == "PRINTING")

    def on_mount(self):
        self.update_printer()
        self.border_title = f'[darkviolet]{self.printer.name} - {self.printer.printer_model}'
        self.set_interval(self.app.refresh_rate, self.update_printer)

    def update_printer(self):
        self.printer = self.app.printer
