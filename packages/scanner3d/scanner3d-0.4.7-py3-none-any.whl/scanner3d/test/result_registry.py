import json
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import Iterator, Optional
from scanner3d.test.result_path import get_output_dir


INDEX_FILENAME = "results_index.jsonl"


@dataclass
class ResultRecord:
    path: str
    kind: str
    test_name: Optional[str] = None
    scanner_name: Optional[str] = None
    camera_name: Optional[str] = None
    settings_name: Optional[str] = None
    timestamp: str = field(
        default_factory=lambda: datetime.now().isoformat(timespec="seconds")
    )


def _index_path() -> Path:
    root = get_output_dir()
    return root / INDEX_FILENAME


def register_result(path: Path, kind: str, **meta) -> None:
    """
    Register a single result file in results_index.jsonl.

    `path` is stored relative to test_results root if inside it,
    otherwise absolute.
    """
    root = get_output_dir()
    path = path.resolve()

    try:
        rel = path.relative_to(root)
    except ValueError:
        rel = path

    record = ResultRecord(path=str(rel), kind=kind, **meta)
    idx = _index_path()
    idx.parent.mkdir(exist_ok=True)

    with idx.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")


def iter_results(
    *,
    kind: str | None = None,
    scanner_name: str | None = None,
    test_name: str | None = None,
    settings_name: str | None = None,
) -> Iterator[ResultRecord]:
    """
    Iterate over all index entries, optionally filtering by attributes.
    """
    idx = _index_path()
    if not idx.exists():
        return iter(())

    def _gen() -> Iterator[ResultRecord]:
        with idx.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                data = json.loads(line)
                rec = ResultRecord(**data)

                if kind is not None and rec.kind != kind:
                    continue
                if scanner_name is not None and rec.scanner_name != scanner_name:
                    continue
                if test_name is not None and rec.test_name != test_name:
                    continue
                if settings_name is not None and rec.settings_name != settings_name:
                    continue

                yield rec

    return _gen()
