from __future__ import annotations

from typing import Callable

from rich.text import TextType
from textual.app import App, ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.widget import Widget
from textual.widgets import Static, RichLog, TabPane, TabbedContent, Header, LoadingIndicator

from textual_prusa_connect.config import AppSettings
from textual_prusa_connect.connect_api import PrusaConnectAPI
from textual_prusa_connect.app_widgets import PrinterHeader
from textual_prusa_connect.widgets.dashboard import ToolStatus, CurrentlyPrinting, HistoryContainer, PrintJob, PrintFile

SETTINGS = AppSettings()
PRINTING_REFRESH = 5
OTHER_REFRESH = 60


class LazyTabPane(TabPane):
    loaded = False

    def __init__(self, title: TextType, init_callable: Callable, *children: Widget):
        super().__init__(title, *children)
        self.init_callable = init_callable

    def compose(self) -> ComposeResult:
        yield VerticalScroll()
        yield LoadingIndicator()

    def on_show(self):
        if self.loaded:
            return
        elements = self.init_callable()
        self.query_one(LoadingIndicator).remove()
        vs = self.query_one(VerticalScroll)
        for i, element in enumerate(elements):
            vs.mount(element)
            if i < len(elements) - 1:
                vs.mount(Static(" "))
        self.loaded = True


class PrusaConnectApp(App):
    DEFAULT_CSS = """
    PrusaConnectApp {
        TabbedContent {
             height: 1fr;
        }
        Container {
            height: auto;
        }
    }
    """

    BINDINGS = [('p', 'toggle_refresh', 'Pause'),
                ('s', 'screenshot', 'Take screenshot'),
                ('q', 'quit', 'Quit')]
    CSS_PATH = "css.tcss"
    do_refresh = True
    refresh_rate = PRINTING_REFRESH

    def __init__(self, headers: dict[str, str]):
        super().__init__()
        self.refresh_timer = None
        self.client = PrusaConnectAPI(headers)
        self.printer = self.client.get_printer(SETTINGS.printer_uuid)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical():
            yield PrinterHeader(printer=self.printer)
            with TabbedContent():
                with TabPane("Dashboard"):
                    with VerticalScroll():
                        yield ToolStatus(printer=self.printer)
                        if self.printer.job_info:
                            yield CurrentlyPrinting(printer=self.printer)
                        yield HistoryContainer(items=self.client.get_files(SETTINGS.printer_uuid, limit=3),
                                               item_type=PrintFile,
                                               title="Latest file uploads")
                        yield HistoryContainer(items=self.client.get_jobs(limit=3),
                                               item_type=PrintJob,
                                               title="Print history")
                        yield Static("Events log", classes='--dashboard-category')
                yield TabPane("Printer files")
                yield TabPane("Print Queue")
                
                def load_print_history():
                    jobs = self.client.get_jobs(limit=25)
                    return [PrintJob(job) for job in jobs]
                yield LazyTabPane("Print history", load_print_history)
                yield TabPane("Control")
                yield TabPane("Statistics")
                yield TabPane("Telemetry")
                yield TabPane("Settings")
                with TabPane("App logs", id='logs'):
                    yield RichLog()

    def on_mount(self):
        self.update_printer(True)
        self.refresh_timer = self.set_interval(self.refresh_rate, self.update_printer)
        self.set_interval(OTHER_REFRESH, self.background_loop)

    def background_loop(self):
        new_rate = OTHER_REFRESH
        if self.printer.printer_state == 'PRINTING':
            new_rate = PRINTING_REFRESH

        if new_rate != self.refresh_rate:
            self.refresh_rate = new_rate
            self.refresh_timer.stop()
            self.query_one(RichLog).write(f'new rate {self.refresh_rate}')
            self.refresh_timer = self.set_interval(self.refresh_rate, self.update_printer, pause=not self.do_refresh)

    def update_printer(self, init: bool = False):
        new_printer = self.client.get_printer(self.printer.uuid.get_secret_value())
        if self.printer.printer_state != new_printer.printer_state:
            self.notify(f"{self.printer.printer_state}->{new_printer.printer_state}",
                        title='Stage change',
                        timeout=10)
        self.printer = new_printer
        if init:
            self.query_one(RichLog).write(self.printer)
        self.query_one(RichLog).write(f'updated {self.refresh_rate}')

    def action_toggle_refresh(self):
        if self.do_refresh:
            self.refresh_timer.pause()
            self.query_one(TabbedContent).add_class('--app-paused')
            self.query_one(RichLog).write('paused')
        else:
            self.refresh_timer.resume()
            self.query_one(TabbedContent).remove_class('--app-paused')
            self.query_one(RichLog).write('unpaused')
        self.do_refresh = not self.do_refresh


if __name__ == '__main__':
    my_headers = {
        'cookie': f'SESSID="{SETTINGS.session_id}"'
    }
    app = PrusaConnectApp(my_headers)
    app.run()
