"""models.py - the Record dataclass used by fetch/ingest (Day 3, S2)."""
from dataclasses import dataclass, field, asdict


@dataclass
class Record:
    id: str
    variety_name: str
    release_year: int | None = None          # None when the source does not say
    recommended_seasons: list[str] = field(default_factory=list)
    cane_yield_t_ha: dict = field(default_factory=dict)
    key_traits: str = ""
    source_url: str = ""

    def to_dict(self) -> dict:
        """Plain dict, ready for json.dump."""
        return asdict(self)