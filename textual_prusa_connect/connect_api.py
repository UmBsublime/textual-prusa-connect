from __future__ import annotations

from requests import Session

from textual_prusa_connect.models import Printer, Job


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

    def get_jobs(self, limit: int = 5, offset: int = 0) -> list[Job]:
        retval = []
        other = 'state=FIN_OK&state=FIN_ERROR&state=FIN_STOPPED&state=UNKNOWN'
        for result in self.session.get(f'{self.base_url}jobs?limit={limit}&offset={offset}&{other}').json()['jobs']:
            retval.append(Job(**result))
        return retval
        #return [Job(), Job(), Job()]

    def get_job(self, job_id) -> Job:
        return self.session.get(f'{self.base_url}jobs/{job_id}')

    def get_groups(self):
        ...

    def get_invitations(self):
        ...

    def set_sync(self):
        # {command: "SET_PRINTER_READY"}
        # {command: "CANCEL_PRINTER_READY"}
        ...


