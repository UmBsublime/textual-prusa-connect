import datetime
from typing import Optional

from pydantic import BaseModel, SecretStr

class Printer(BaseModel):
    api_key: Optional[SecretStr] = None
    axis_x: Optional[float] = None
    axis_y: Optional[float] = None
    axis_z: Optional[float] = None
    filament: dict
    firmware: str
    flow: Optional[int] = None
    job_info: Optional[dict] = None
    location: str
    owner: Optional[dict] = None
    printer_model: str
    printer_state: str
    printer_type: str
    printer_type_name: str
    prusaconnect_api_key: Optional[SecretStr] = None
    name: str
    nozzle_diameter: float
    speed: Optional[int]
    slot: Optional[dict] = None
    slots: int
    sn: Optional[SecretStr] = None
    state_reason: Optional[str] = None
    # support: Optional[dict] = None
    supported_printer_models: list[str]
    temp: Optional[dict]
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
