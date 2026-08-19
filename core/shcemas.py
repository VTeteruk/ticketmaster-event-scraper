from dataclasses import dataclass


@dataclass
class Tickets:
    url: str
    event_url: str
    email: str
    quantity: int
