from textual_prusa_connect.config import AppSettings
from textual_prusa_connect.connect_api import PrusaConnectAPI

if __name__ == '__main__':
    from rich import print
    SETTINGS = AppSettings()
    my_headers = {
        'cookie': f'SESSID="{SETTINGS.session_id}"'
    }

    c = PrusaConnectAPI(my_headers)
    r = c.get_jobs(limit=10, offset=3)
    #r = c.get_job(r[0].id)

    print(r[-1])