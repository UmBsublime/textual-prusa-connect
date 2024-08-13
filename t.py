from __future__ import annotations

import datetime
from typing import Optional

from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from requests import Session

from textual.app import App, ComposeResult
from textual.widgets import Static, RichLog


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    printer_uuid: str
    session_id: str


SETTINGS = Settings()

class Printer(BaseModel):
    printer_state: str
    state_reason: Optional[str] = None
    job_info: Optional[dict] = None
    api_key: Optional[SecretStr] = None
    axis_x: Optional[float] = None
    axis_y: Optional[float] = None
    axis_z: Optional[float] = None
    temp: dict
    flow: Optional[int] = None
    speed: int
    nozzle_diameter: float
    slot: Optional[dict] = None
    slots: int
    printer_model: str
    supported_printer_models: list[str]
    filament: dict
    support: Optional[dict] = None
    printer_type: str
    printer_type_name: str
    name: str
    firmware: str
    sn: Optional[str] = None
    uuid: str
    prusaconnect_api_key: Optional[SecretStr] = None
    owner: Optional[dict] = None

    def basic_info(self) -> str:
        return_val = f"""\
name: [blue]{self.name}[/blue] \
printer_model: [blue]{self.printer_model}[/blue]
state: [blue]{self.printer_state}[/blue] \
filament: [blue]{self.filament['material']}[/blue]
nozzle: [green]{self.temp['temp_nozzle']}/{self.temp['target_nozzle']}[/green] \
bed: [green]{self.temp['temp_bed']}/{self.temp['target_bed']}[/green]"""
        if self.printer_state == 'PRINTING':
            elapsed = datetime.timedelta(seconds=self.job_info['time_printing'])
            remaining = datetime.timedelta(seconds=self.job_info['time_remaining'])
            return_val += f""" toolhead: [green]{self.slot['active']}[/]
[yellow]{self.job_info["display_name"]}[/]
progress: [yellow]{int(self.job_info['progress']):d}%[/] \
print time: [yellow]{elapsed}[/] \
time left: [yellow]{remaining}[/]"""

        return return_val


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
    def __init__(self, headers: dict[str, str]):
        self.client = PrusaConnectAPI(headers)
        super().__init__()

    def compose(self) -> ComposeResult:
        printers = self.client.get_printers()
        log = RichLog()
        for printer in printers:
            log.write(printer)
            s = Static()
            s.styles.border = ("round", "red")
            s.styles.width = '50%'
            yield s

        yield log

    def on_mount(self):
        self.update_printer(True)
        self.set_interval(30, self.update_printer)

    def update_printer(self, init: bool = False):
        # self.query_one(RichLog).write("Printer updated")
        printer = self.client.get_printer(SETTINGS.printer_uuid)
        if init:
            self.query_one(RichLog).write(printer)
        self.query_one(Static).update(printer.basic_info())


if __name__ == '__main__':
    my_headers = {
        'cookie': f'SESSID="{SETTINGS.session_id}"'

    }
    app = PrusaConnectApp(my_headers)
    app.run()
    app.push_screen_wait()
