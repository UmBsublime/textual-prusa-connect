from __future__ import annotations

import datetime
from typing import Optional

from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from requests import Session

from textual.app import App, ComposeResult
from textual.containers import Vertical, Container
from textual.widgets import Static, RichLog, TabPane, TabbedContent

from textual_prusa_connect.widgets import PrinterHeader, ToolStatus
from textual_prusa_connect.models import Printer


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    printer_uuid: str
    session_id: str


SETTINGS = Settings()



class PrusaConnectAPI:
    def __init__(self, headers: dict[str, str]):
        self.base_url = "https://connect.prusa3d.com/app/"
        self.session = Session()
        self.session.headers.update(headers)

    def get_printers(self) -> list[Printer]:
        response = self.session.get(self.base_url + "printers")
        if response.ok:
            return [Printer(**r) for r in response.json()['printers']]

    def get_printer(self, printer_id) -> Printer | None:
        response = self.session.get(f"{self.base_url}printers/{printer_id}")
        if response.ok:
            return Printer(**response.json())
        return None

    def get_storage(self):
        ...

    def get_cameras(self):
        ...

    def get_config(self):
        ...

    def get_files(self, printer: str | None = None, limit: int = 1):
        return self.session.get(f'{self.base_url}printers/{printer}/files?limit={limit}')

    def get_queue(self):
        ...

    def get_events(self, printer: str | None = None, limit: int = 3):
        return self.session.get(f'{self.base_url}printers/{printer}/events?limit={limit}')

    def get_supported_commands(self):
        ...

    def get_printer_types(self):
        ...

    def get_unseen(self):
        ...

    def get_login(self):
        return self.session.get(f'{self.base_url}login')

    def get_jobs(self, limit: int = 3, offset: int = 0):
        return self.session.get(f'{self.base_url}jobs?limit={limit}&offset={offset}')

    def get_groups(self):
        ...

    def get_invitations(self):
        ...

    def set_sync(self):
        # {command: "SET_PRINTER_READY"}
        # {command: "CANCEL_PRINTER_READY"}
        ...


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
    CSS_PATH = "css.tcss"

    refresh_rate = 5
    def __init__(self, headers: dict[str, str]):
        super().__init__()
        self.client = PrusaConnectAPI(headers)
        self.printer = self.client.get_printer(SETTINGS.printer_uuid)

    def compose(self) -> ComposeResult:
        with Vertical():
            yield PrinterHeader(printer=self.printer)
            with TabbedContent() as tc:
                with TabPane("Dashboard"):
                    with Container():
                        yield ToolStatus(printer=self.printer)
                    with Container(classes='--category'):
                        yield Static("Currently printing")
                    with Container(classes='--category'):
                        yield Static("Print history")
                    with Container(classes='--category'):
                        yield Static("Latest file uploads")
                    with Container(classes='--category'):
                        yield Static("Events log")
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
        self.set_interval(self.refresh_rate, self.update_printer)
        ...
    def update_printer(self, init: bool = False):
        self.printer = self.client.get_printer(self.printer.uuid.get_secret_value())
        if init:
            self.query_one(RichLog).write(self.printer)
        self.query_one(RichLog).write('updated')


if __name__ == '__main__':
    my_headers = {
        'cookie': f'SESSID="{SETTINGS.session_id}"'

    }
    app = PrusaConnectApp(my_headers)
    app.run()
    app.push_screen_wait()
