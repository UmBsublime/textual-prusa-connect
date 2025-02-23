from __future__ import annotations

from requests import Session

from textual_prusa_connect.models import Event, File, Job, Printer, FirmwareFile, PrintFile


class ResourceNotFound(Exception):
    ...


class Unauthorized(Exception):
    ...


class Wtf(Exception):
    ...


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
        elif response.status_code == 404:
            raise ResourceNotFound(f"{response.status_code}: {response.text}")
        elif response.status_code in (401, 403):
            raise Unauthorized(f"{response.status_code}: {response.text}")
        return None

    def get_storage(self):
        ...

    def get_cameras(self):
        ...

    def get_config(self):
        ...

    def get_files(self, printer: str | None = None, limit: int = 1) -> list[File]:
        retval = []
        for file in self.session.get(f'{self.base_url}printers/{printer}/files?limit={limit}').json()['files']:
            if file['type'] == 'FIRMWARE':
                retval.append(FirmwareFile(**file))
            elif file['type'] == 'PRINT_FILE':
                retval.append(PrintFile(**file))
        return retval

    def get_queue(self):
        ...

    def get_events(self, printer: str | None = None, limit: int = 5) -> list[Event]:
        retval = []
        try:
            for event in self.session.get(f'{self.base_url}printers/{printer}/events?limit={limit}').json()['events']:
                retval.append(Event(**event))
        except KeyError:
            retval = []

        return retval

    def get_supported_commands(self):
        ...

    def get_printer_types(self):
        ...

    def get_unseen(self):
        ...

    def get_login(self):
        return self.session.get(f'{self.base_url}login')

    def get_jobs(self, limit: int = 5, offset: int = 0) -> list[Job]:
        retval = []
        # other = 'state=FIN_OK&state=FIN_ERROR&state=FIN_STOPPED&state=UNKNOWN'
        for result in self.session.get(f'{self.base_url}jobs?limit={limit}&offset={offset}').json()['jobs']:
            retval.append(Job(**result))
        return retval

    def get_groups(self):
        ...

    def get_invitations(self):
        ...

    def set_sync(self):
        # {command: "SET_PRINTER_READY"}
        # {command: "CANCEL_PRINTER_READY"}
        ...
