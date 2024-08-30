from datetime import datetime, timedelta
from typing import Any, Literal

from textual.widget import Widget


class Pretty(Widget):
    def __init__(self,
                 obj: Any,
                 key: str,
                 color: Literal['blue', 'green', 'orange'] = 'blue',
                 unit: str = '',
                 is_timedelta: bool = False,
                 is_timestamp: bool = False,
                 **kwargs,
                 ):
        super().__init__(**kwargs)
        self.obj = obj
        self.key = key
        self.color = color
        self.unit = unit
        self.is_timedelta = is_timedelta
        self.is_timestamp = is_timestamp
        name = self.key.capitalize()
        self.pretty_name = name.replace('_', ' ')

    def render(self):
        if isinstance(self.obj, list):
            value, other = self.obj
            if isinstance(value, dict):
                value = value.get(self.key, None)
            else:
                value = getattr(value, self.key, None)
            return f"{self.pretty_name}: [{self.color}]{value}/{other}{self.unit}"
        elif isinstance(self.obj, dict):
            value = self.obj.get(self.key, None)
        else:
            value = getattr(self.obj, self.key, None)

        if value is None:
            return f"{self.pretty_name}: [red]None"

        if self.is_timedelta:
            value = timedelta(seconds=int(value))
        if self.is_timestamp:
            value = datetime.fromtimestamp(int(value))

        if isinstance(value, float):
            value = f"{value:.2f}"

        return f"{self.pretty_name}: [{self.color}]{value}{self.unit}"



