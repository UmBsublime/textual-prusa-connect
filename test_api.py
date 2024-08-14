from textual_prusa_connect.config import AppSettings
from textual_prusa_connect.connect_api import PrusaConnectAPI

if __name__ == '__main__':
    from rich import print
    SETTINGS = AppSettings()
    my_headers = {
        'cookie': f'SESSID="{SETTINGS.session_id}"'
    }

    c = PrusaConnectAPI(my_headers)
    r = c.get_jobs(limit=1, offset=3)
    print(r.json())
