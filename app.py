from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict

from textual.app import App, ComposeResult
from textual.containers import Vertical, Container
from textual.widgets import Static, RichLog, TabPane, TabbedContent, Rule, Header

from textual_prusa_connect.connect_api import PrusaConnectAPI
from textual_prusa_connect.app_widgets import PrinterHeader
from textual_prusa_connect.widgets.dashboard import ToolStatus, CurrentlyPrinting


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    printer_uuid: str
    session_id: str


SETTINGS = Settings()

PRINTING_REFRESH = 5
OTHER_REFRESH = 60

class PrusaConnectApp(App):
    DEFAULT_CSS = """
    PrusaConnectApp {
        .--category {
            border: round green;
        }
        TabbedContent {
             height: 1fr;
        }
        Container {
            height: auto;
        }
    }
    """
    BINDINGS = [('p', 'toggle_refresh', 'Pause'),
                ('s', 'screenshot', ''),
                ('q', 'quit', '')]
    CSS_PATH = "css.tcss"
    do_refresh = True
    refresh_rate = PRINTING_REFRESH
    def __init__(self, headers: dict[str, str]):
        super().__init__()
        self.client = PrusaConnectAPI(headers)
        self.printer = self.client.get_printer(SETTINGS.printer_uuid)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical():
            yield PrinterHeader(printer=self.printer)
            with TabbedContent() as tc:
                with TabPane("Dashboard"):
                    yield ToolStatus(printer=self.printer)
                    if self.printer.job_info:
                        yield CurrentlyPrinting(printer=self.printer)
                    yield Static("Print history", classes='--dashboard-category')
                    yield Static("Latest file uploads", classes='--dashboard-category')
                    yield Static("Events log", classes='--dashboard-category')
                yield TabPane("Files")
                yield TabPane("Queue")
                yield TabPane("History")
                yield TabPane("Control")
                yield TabPane("Stats")
                yield TabPane("Metrics")
                yield TabPane("Settings")
                with TabPane("Log", id='logs'):
                    yield RichLog()

    def on_mount(self):
        # self.query_one(TabbedContent).active = 'logs'
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
            self.refresh_timer = self.set_interval(self.refresh_rate, self.update_printer)

    def update_printer(self, init: bool = False):
        self.printer = self.client.get_printer(self.printer.uuid.get_secret_value())
        if init:
            self.query_one(RichLog).write(self.printer)
        self.query_one(RichLog).write(f'updated {self.refresh_rate}')

    def action_toggle_refresh(self):
        if self.do_refresh:
            self.refresh_timer.pause()
            self.query_one(TabbedContent).add_class('--app-paused')
        else:
            self.refresh_timer.resume()
            self.query_one(TabbedContent).remove_class('--app-paused')
        self.do_refresh = not self.do_refresh



if __name__ == '__main__':
    my_headers = {
        'cookie': f'SESSID="{SETTINGS.session_id}"'

    }
    app = PrusaConnectApp(my_headers)
    app.run()
    app.push_screen_wait()
