from rich import print

from textual_prusa_connect.config import AppSettings
from textual_prusa_connect.connect_api import PrusaConnectAPI

if __name__ == '__main__':
    SETTINGS = AppSettings()
    my_headers = {
        'cookie': f'SESSID="{SETTINGS.session_id}"'
    }
    c = PrusaConnectAPI(my_headers)
    #r = c.get_files(printer=SETTINGS.printer_uuid, limit=1)
    #r = c.get_jobs()
    #r = c.get_job(r[0].id)
    r = c.get_events(SETTINGS.printer_uuid)

    print(r)
