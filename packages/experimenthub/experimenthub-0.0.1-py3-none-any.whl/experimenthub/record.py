from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

__author__ = "Jayaram Kancherla"
__copyright__ = "Jayaram Kancherla"
__license__ = "MIT"


@dataclass(frozen=True)
class ExperimentHubRecord:
    """Container for a single ExperimentHub entry."""

    ehub_id: str
    title: str
    species: Optional[str]
    taxonomy_id: Optional[str]
    genome: Optional[str]
    description: Optional[str]
    url: str
    release_date: Optional[date]
    preparer_dataclass: Optional[str]

    @classmethod
    def from_db_row(cls, row: tuple) -> "ExperimentHubRecord":
        """Build a record from a database query row.

        Expected row format:
        (id, title, species, taxonomyid, genome, description, full_url, date_added, rdataclass)
        """
        rid, title, species, tax_id, genome, desc, url, date_str, rdataclass = row
        ehub_id = f"EH{rid}"

        rel_date: Optional[date] = None
        if date_str:
            try:
                rel_date = datetime.strptime(str(date_str).split(" ")[0], "%Y-%m-%d").date()
            except ValueError:
                pass

        return cls(
            ehub_id=ehub_id,
            title=title or "",
            species=species,
            taxonomy_id=str(tax_id) if tax_id else None,
            genome=genome,
            description=desc,
            url=url,
            release_date=rel_date,
            preparer_dataclass=rdataclass,
        )
