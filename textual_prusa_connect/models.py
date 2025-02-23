import datetime
from typing import Optional

from pydantic import BaseModel, SecretStr


class Printer(BaseModel):
    api_key: Optional[SecretStr] = None
    axis_x: Optional[float] = None
    axis_y: Optional[float] = None
    axis_z: Optional[float] = None
    filament: dict = {}
    firmware: str
    flow: Optional[int] = None
    job_info: Optional[dict] = {}
    location: str
    owner: Optional[dict] = None
    printer_model: str
    printer_state: str
    printer_type: str
    printer_type_name: str
    prusaconnect_api_key: Optional[SecretStr] = None
    name: str
    nozzle_diameter: float
    speed: Optional[int] = 0
    slot: Optional[dict] = None
    slots: int
    sn: Optional[SecretStr] = None
    state_reason: Optional[str] = None
    # support: Optional[dict] = None
    supported_printer_models: list[str]
    temp: Optional[dict] = {}
    uuid: SecretStr




class BasicPrinter(BaseModel):
    printer_state: str
    temp: dict
    speed: int
    nozzle_diameter: float
    slots: int
    printer_model: str
    supported_printer_models: list[str]
    filament: dict
    printer_type: str
    printer_type_name: str
    name: str
    firmware: str
    uuid: str
    job_info: dict = None
    axis_z: float = None


class Job(BaseModel):
    id: int
    printer_uuid: str
    origin_id: int
    path: str
    state: str
    # hash: str
    # team_id: int
    start: int
    end: Optional[int] = -1
    source: str
    # source_info: dict
    # planned: dict
    file: 'File'


class File(BaseModel):
    type: Optional[str] = None
    name: str
    path: Optional[str] = None
    m_timestamp: Optional[int] = None
    size: int
    display_name: str
    upload_id: Optional[int] = None
    uploaded: Optional[int] = None
    meta: Optional[dict] = {}
    # 'read_only': False,
    # 'hash': 'yUbtnfNt9Ju2yVwvjIRp4gxZ5ik.',
    # 'display_path': '/usb/NTS1StandB_0.4n_0.2mm_PLA_XLIS_1h1m.bgcode',
    # 'team_id': 26502,
    sync: dict
    preview_url: Optional[str] = None
    preview_mimetype: Optional[str] = None


class PrintFile(File):
    ...


class FirmwareFile(File):
    ...


class Tool(BaseModel):
    id: int
    material: str
    temp: float
    fan_hotend: float
    fan_print: float


class Event(BaseModel):
    event: str
    created: datetime.datetime
    data: Optional[dict] = {}
    server_time: datetime.datetime
    source: str
