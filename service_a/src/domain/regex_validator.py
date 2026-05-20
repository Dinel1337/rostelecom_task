import re
from dataclasses import dataclass

@dataclass
class SerialRegex:
    value: str
    
    def __post_init__(self):
        if not re.fullmatch(r'[A-Za-z0-9]{6,}', self.value):
            raise ValueError(f'Неверное серийное что-то: {self.value}')