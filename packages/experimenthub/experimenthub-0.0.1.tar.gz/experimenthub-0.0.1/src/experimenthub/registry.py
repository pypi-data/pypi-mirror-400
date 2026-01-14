import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pybiocfilecache import BiocFileCache

from ._ehub import EHUB_METADATA_URL
from .record import ExperimentHubRecord

__author__ = "Jayaram Kancherla"
__copyright__ = "Jayaram Kancherla"
__license__ = "MIT"


class ExperimentHubRegistry:
    """Registry for ExperimentHub resources."""

    # R classes that have corresponding BiocPy representations
    SUPPORTED_R_CLASSES = {
        "vector",
        "list",
        "character",
        "matrix",
        "numeric",
        "int",
        "matrix",
        "dataframe",
        "data.frame",
        "data frame",
        "dframe",
        "iranges",
        "genomicranges",
        "granges",
        "summarizedexperiment",
        "rangedSummarizedexperiment",
        "singlecellexperiment",
        "multiassayexperiment",
    }

    SUPPORTED_EXTENSIONS = ".rds"  # , ".rda", ".rdata"

    def __init__(
        self,
        cache_dir: Optional[Union[str, Path]] = None,
        force: bool = False,
    ) -> None:
        """Initialize the ExperimentHub registry.

        Args:
            cache_dir:
                Directory for the BiocFileCache database and cached files.
                If None, defaults to "~/.cache/experimenthub_bfc".

            force:
                If True, force re-download of the ExperimentHub metadata database.
        """
        if cache_dir is None:
            cache_dir = Path.home() / ".cache" / "experimenthub_bfc"

        self._cache_dir = Path(cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._bfc = BiocFileCache(self._cache_dir)

        self._registry_map: Dict[str, ExperimentHubRecord] = {}

        self._initialize_registry(force=force)

    def _initialize_registry(self, force: bool = False):
        """Fetch the ExperimentHub metadata and populate the registry."""
        rname = "experimenthub_metadata"

        existing = None
        try:
            existing = self._bfc.get(rname)
        except Exception:
            pass

        if force and existing:
            try:
                self._bfc.remove(rname)
            except Exception:
                pass
            existing = None

        if existing:
            md_resource = existing
        else:
            md_resource = self._bfc.add(rname, EHUB_METADATA_URL, rtype="web")

        md_path = self._get_filepath(md_resource)

        if not md_path or not os.path.exists(md_path):
            if existing and not force:
                return self._initialize_registry(force=True)
            raise RuntimeError("Failed to retrieve ExperimentHub metadata database.")

        conn = sqlite3.connect(md_path)
        try:
            query = """
            SELECT
                r.id,
                r.title,
                r.species,
                r.taxonomyid,
                r.genome,
                r.description,
                lp.location_prefix || rp.rdatapath AS full_url,
                r.rdatadateadded,
                rp.rdataclass
            FROM resources r
            LEFT JOIN location_prefixes lp
                ON r.location_prefix_id = lp.id
            LEFT JOIN rdatapaths rp
                ON rp.resource_id = r.id
            WHERE r.title IS NOT NULL
            ORDER BY r.id ASC;
            """
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
        finally:
            conn.close()

        for row in rows:
            rdataclass = row[-1]
            url = row[6]

            if rdataclass.lower() not in self.SUPPORTED_R_CLASSES:
                continue

            if not url or not url.lower().endswith(self.SUPPORTED_EXTENSIONS):
                continue

            record = ExperimentHubRecord.from_db_row(row)
            self._registry_map[record.ehub_id] = record

    def list_ids(self) -> List[str]:
        """List all available ExperimentHub IDs (e.g., 'EH1', 'EH123')."""
        return sorted(list(self._registry_map.keys()), key=lambda x: int(x[2:]))

    def get_record(self, ehub_id: str) -> ExperimentHubRecord:
        """Get the metadata record for a given ExperimentHub ID."""
        if ehub_id not in self._registry_map:
            raise KeyError(f"ID '{ehub_id}' not found in registry (or is not a supported format).")

        return self._registry_map[ehub_id]

    def search(self, query: str) -> List[ExperimentHubRecord]:
        """Search for resources matching the query string."""
        q = query.lower()
        results = []
        for rec in self._registry_map.values():
            if q in rec.title.lower():
                results.append(rec)
                continue
            if rec.species and q in rec.species.lower():
                results.append(rec)
                continue
            if rec.description and q in rec.description.lower():
                results.append(rec)
                continue

        return results

    def download(self, ehub_id: str, force: bool = False) -> str:
        """Download and cache the resource file."""
        record = self.get_record(ehub_id)
        url = record.url
        key = ehub_id

        if force:
            try:
                self._bfc.remove(key)
            except Exception:
                pass

        if not force:
            try:
                existing = self._bfc.get(key)
                if existing:
                    path = self._get_filepath(existing)
                    if path and os.path.exists(path) and os.path.getsize(path) > 0:
                        return path
            except Exception:
                pass

        resource = self._bfc.add(
            key,
            url,
            rtype="web",
            download=True,
        )

        path = self._get_filepath(resource)

        if not path or not os.path.exists(path) or os.path.getsize(path) == 0:
            try:
                self._bfc.remove(key)
            except Exception:
                pass
            raise RuntimeError(f"Download failed for {ehub_id}. File is empty or missing.")

        return path

    def load(self, ehub_id: str, force: bool = False) -> Any:
        """Load the resource using rds2py."""
        path = self.download(ehub_id, force=force)

        try:
            import rds2py
        except ImportError:
            raise ImportError(f"The resource {ehub_id} requires 'rds2py' to be loaded. " "Please install it via pip.")

        try:
            return rds2py.read_rds(path)
        except Exception as e:
            raise RuntimeError(f"Failed to load R data from {path}: {e}")

    def _get_filepath(self, resource: Any) -> Optional[str]:
        """Helper to extract absolute path from a BiocFileCache resource."""
        if hasattr(resource, "rpath"):
            rel_path = str(resource.rpath)
        elif hasattr(resource, "get"):
            rel_path = str(resource.get("rpath"))
        else:
            return None

        return str(self._cache_dir / rel_path)
