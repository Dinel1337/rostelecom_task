import re
from dataclasses import dataclass

@dataclass
class SerialRegex:
    #чисто для понта, можно было и в pydantic сунуть, но условно у нас сложная логика проверки...
    value:str
    
    def __post_init__(self):
        if not re.match(r'^[a-zA-Z0-9]{6,}$', self.value):
            raise ValueError(f'Неверное серийное что-то: {self.value}')