from dataclasses import dataclass


@dataclass
class PathRequest:
    origin: str
    destination: str
    amount: int
