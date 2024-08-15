from textual_prusa_connect.config import AppSettings
from textual_prusa_connect.connect_api import PrusaConnectAPI

if __name__ == '__main__':
    from rich import print
    from textual_prusa_connect.config import AppSettings
    SETTINGS = AppSettings()
    my_headers = {
        'cookie': f'SESSID="{SETTINGS.session_id}"'
    }

    c = PrusaConnectAPI(my_headers)
    r = c.get_files(printer=SETTINGS.printer_uuid, limit=1)
    r = c.get_jobs()
    #r = c.get_job(r[0].id)

    print(r)