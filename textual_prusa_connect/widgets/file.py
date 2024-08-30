from datetime import timedelta, datetime

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widget import Widget
from textual.widgets import Static

from textual_prusa_connect.models import Job, File, FirmwareFile, PrintFile
from textual_prusa_connect.utils import is_wsl
from textual_prusa_connect.widgets import Pretty


class BaseFileWidget(Widget):
    def __init__(self) -> None:
        super().__init__()
        self.file_path = None
        self.add_class('--file-widget')

    def on_click(self) -> None:
        url = f"https://connect.prusa3d.com{self.file_path}"
        if not is_wsl():
            self.app.open_url(url)
            self.notify("Browser opened")
        else:
            self.notify("Not available on WSL\n"+url, severity="warning")


class PrintJobWidget(BaseFileWidget):
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
                    yield Pretty(self.job.file.meta, 'printer_model', classes='--cell')
                    yield Pretty(self.job.file.meta, 'filament_type', classes='--cell')
                    if self.job.end != -1:
                        delta = timedelta(seconds=self.job.end - self.job.start)
                    else:
                        delta = "---"
                    yield Static(f'Real time: [blue]{delta}')
                with Horizontal():
                    yield Pretty(self.job.file.meta, 'layer_height', classes='--cell')
                    yield Pretty(self.job.file.meta, 'nozzle_diameter', classes='--cell')
                    if self.job.end == -1:
                        yield Static(f'Print end: [blue]---')
                    else:
                        yield Static(f'Print end: [blue]{datetime.fromtimestamp(self.job.end)}')


class PrintFileWidget(BaseFileWidget):
    def __init__(self, file: File) -> None:
        super().__init__()
        self.file = file
        self.tooltip = 'Click to open image preview in browser'
        self.file_path = self.file.preview_url

    def compose(self):
        with Horizontal():
            yield Static("  🗋   ", classes='--icon')
            with Vertical(classes='--lighter-background'):
                with Horizontal():
                    yield Static(f'[yellow]{self.file.name}')
                with Horizontal(classes='--dimgrey-background'):
                    yield Pretty(self.file.meta, "printer_model", classes='--cell')
                    yield Pretty(self.file.meta, "filament_type", classes='--cell')
                    yield Pretty(self.file.meta, 'estimated_print_time',  is_timedelta=True)
                with Horizontal():
                    yield Pretty(self.file.meta, "layer_height", classes='--cell')
                    yield Pretty(self.file.meta, "nozzle_diameter", classes='--cell')
                    yield Pretty(self.file, 'uploaded', is_timestamp=True)


class FirmwareFileWidget(Widget):
    def __init__(self, file: File) -> None:
        super().__init__()
        self.file = file

    def compose(self):
        with Horizontal():
            yield Static("  FW  ", classes='--icon')
            with Vertical(classes='--lighter-background'):
                with Horizontal():
                    yield Static(f"[red]{self.file.name}")
                with Horizontal(classes='--dimgrey-background'):
                    yield Pretty(self.file, "size", unit=' bytes')

                with Horizontal():
                    yield Pretty(self.file, "m_timestamp", is_timestamp=True)

    def on_mount(self):
        self.app.query_one('RichLog').write(self.file)


class FileHistory(Widget):
    def __init__(self, files: list[File], title='Latest file uploads') -> None:
        super().__init__()
        self.files = files
        self.border_title = title
        self.add_class('--dashboard-category')
        self.can_focus = True

    def compose(self) -> ComposeResult:
        for i, file in enumerate(self.files):
            if isinstance(file, FirmwareFile):
                yield FirmwareFileWidget(file)
            if isinstance(file, PrintFile):
                yield PrintFileWidget(file)
            if i < len(self.files) - 1:
                yield Static(' ')
