from dataclasses import dataclass
from typing import Optional


@dataclass
class Category:
    name: str
    icon: Optional[str] = None
    color: Optional[str] = None
    id: Optional[int] = None

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "icon": self.icon,
            "color": self.color,
        }
