import datetime

from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, Static

from textual_prusa_connect.messages import PrinterUpdated
from textual_prusa_connect.models import Printer
from textual_prusa_connect.widgets import Pretty


class PrinterHeader(Widget):
    DEFAULT_CSS = """
    PrinterHeader {
        height: auto;
        border: round lightblue;
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
        self.add_class('--requires-printer')

    def compose(self):
        with Horizontal():
            yield Static("  🖨   ", id='icon')
            with Vertical(classes='--cell'):
                yield Pretty(self.printer, 'printer_state', classes='--lighter-background')
                yield Pretty(self.printer, 'location')
                yield Pretty(self.printer, 'firmware')
            with Vertical(classes='--cell'):
                yield Pretty(self.printer.filament, 'material')
                yield Pretty(self.printer, 'nozzle_diameter', classes='--lighter-background')
                yield Pretty([self.printer.slot, self.printer.slots], 'active')
            with Vertical(classes='--cell'):
                yield Pretty([self.printer.temp, self.printer.temp.get('target_nozzle', None)], 'temp_nozzle')
                yield Pretty([self.printer.temp, self.printer.temp.get('target_bed', None)], 'temp_bed', classes='--lighter-background')
                yield Pretty(self.printer, 'axis_z', unit='mm')
            with Vertical():
                yield Pretty(self.printer, 'speed', unit='%')
                if self.printer.job_info:
                    yield Static(f"progress: [blue]{self.printer.job_info['progress']:.1f}%", classes='--lighter-background')
                else:
                    yield Static(' ', classes='--lighter-background')
                eta = ''
                if self.printer.job_info:
                    elapsed = datetime.timedelta(seconds=self.printer.job_info.get('time_printing', 0))
                    remaining = '00:00:00'
                    if self.printer.job_info.get('time_remaining', None) and self.printer.job_info['time_remaining'] != -1:
                        remaining = datetime.timedelta(seconds=self.printer.job_info['time_remaining'])
                    eta = f'[green]{elapsed} / {remaining}'
                yield Static(eta)
            yield Button("🚀 Set Ready", disabled=self.printer.printer_state == "PRINTING")

    def on_mount(self):
        self.border_title = f'[darkviolet]{self.printer.name} - {self.printer.printer_model}'

    def on_printer_updated(self, msg: PrinterUpdated):
        if msg.printer != self.printer:
            self.printer = msg.printer
