from __future__ import annotations

from typing import Callable

from rich.text import TextType
from textual import work
from textual.app import App, ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Static, RichLog, TabPane, TabbedContent, Header, LoadingIndicator

from textual_prusa_connect.config import AppSettings
from textual_prusa_connect.connect_api import PrusaConnectAPI
from textual_prusa_connect.app_widgets import PrinterHeader
from textual_prusa_connect.widgets.tool import ToolList
from textual_prusa_connect.widgets.dashboard import CurrentlyPrinting, HistoryContainer, PrintJob, PrintFile, \
    DashboardPane

SETTINGS = AppSettings()
PRINTING_REFRESH = 5
MAIN_REFRESH = 30
OTHER_REFRESH = 60


class DataLoaded(Message):
    """Data loaded message"""
    def __init__(self, content):
        self.content = content
        super().__init__()


class LazyTabPane(TabPane):
    # reference https://gist.github.com/paulrobello/0a2f807ddd195c42f87cec9ff5825ac8
    loaded = False

    def __init__(self, title: TextType, init_callable: Callable, *children: Widget):
        super().__init__(title, *children)
        self.init_callable = init_callable

    def compose(self) -> ComposeResult:
        yield VerticalScroll()
        yield LoadingIndicator()

    @work
    async def update_data(self):
        content = self.init_callable()
        self.post_message(DataLoaded(content=content))

    async def on_data_loaded(self, msg: DataLoaded) -> None:
        msg.stop()
        await self.query_one(LoadingIndicator).remove()
        vs = self.query_one(VerticalScroll)
        for i, element in enumerate(msg.content):
            await vs.mount(element)
            if i < len(msg.content) - 1:
                await vs.mount(Static(" "))

    def on_show(self):
        if self.loaded:
            return
        self.update_data()
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
                yield DashboardPane(self.client, self.printer)

                yield TabPane("Printer files", disabled=True)
                yield TabPane("Print Queue", disabled=True)

                def load_print_history():
                    jobs = self.client.get_jobs(limit=25)
                    return [PrintJob(job) for job in jobs]
                yield LazyTabPane("Print history", load_print_history)

                yield TabPane("Control", disabled=True)
                yield TabPane("Statistics", disabled=True)
                yield TabPane("Telemetry", disabled=True)
                yield TabPane("Settings", disabled=True)
                with TabPane("App logs", id='logs'):
                    yield RichLog()

    def on_mount(self):
        self.screen.set_focus(None)
        self.update_printer(True)
        self.refresh_timer = self.set_interval(self.refresh_rate, self.update_printer)
        self.set_interval(MAIN_REFRESH, self.background_loop)

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
            self.notify(f"{self.printer.printer_state} -> {new_printer.printer_state}",
                        title='State change',
                        timeout=10)
            # We are no longer printing, let's remove the currently printing block
            if self.printer.printer_state == 'PRINTING':
                self.query_one(CurrentlyPrinting).remove()
            # NOT WORKING Started a new print, let's recompose to add the block back
            if new_printer.printer_state == 'PRINTING':
                self.query_one(DashboardPane).recompose()
        self.printer = new_printer
        if init:
            self.query_one(RichLog).write(self.printer)
        # self.query_one(RichLog).write(f'updated {self.refresh_rate}')

    def action_toggle_refresh(self):
        if self.do_refresh:
            self.refresh_timer.pause()
            self.query_one(TabbedContent).add_class('--app-paused')
            self.query_one(RichLog).write('paused')
        else:
            self.refresh_timer.resume()
            self.query_one(TabbedContent).remove_class('--app-paused')
            self.query_one(RichLog).write('resumed')
        self.do_refresh = not self.do_refresh


if __name__ == '__main__':
    my_headers = {
        'cookie': f'SESSID="{SETTINGS.session_id}"'
    }
    app = PrusaConnectApp(my_headers)
    app.run()
