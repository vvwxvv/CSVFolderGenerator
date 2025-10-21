"""
CSV Reorder Utility – Production-ready implementation
Works identically in source and PyInstaller builds.
"""

import csv
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field


@dataclass
class SortColumn:
    """Column to sort by."""
    name: str
    is_date: bool = False

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Column name must be a non-empty string")
        self.name = self.name.strip()


@dataclass
class CSVReorderConfig:
    """Configuration for reordering."""
    sort_columns: List[SortColumn]
    reverse: bool = False
    use_language_sorting: bool = False
    language_column: str = "language"
    language_order: List[str] = field(default_factory=lambda: ["EN", "CN"])
    output_prefix: str = "sorted_"
    encoding: str = "utf-8"

    def __post_init__(self):
        if not self.sort_columns:
            raise ValueError("At least one sort column must be specified")
        if self.use_language_sorting and not self.language_column.strip():
            raise ValueError("Language column name cannot be empty when language sorting is enabled")
        if self.use_language_sorting and not self.language_order:
            raise ValueError("Language order cannot be empty when language sorting is enabled")


class CSVReorderError(Exception):
    """Raised for any reorder-related error."""
    pass


class CSVReorder:
    """
    Robust CSV re-ordering utility.
    Supports multi-column sorting, date parsing, language ordering,
    comprehensive logging, and works frozen with PyInstaller.
    """

    DATE_FORMATS = [
        "%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y", "%Y",
        "%Y-%m", "%m-%Y", "%m/%d/%Y", "%d.%m.%Y", "%Y.%m.%d",
    ]

    def __init__(self, config: CSVReorderConfig, logger: Optional[logging.Logger] = None):
        self.config = config
        self.logger = logger or self._setup_default_logger()
        self._validate_config()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _setup_default_logger(self) -> logging.Logger:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
            logger.addHandler(handler)
        return logger

    def _validate_config(self) -> None:
        try:
            for col in self.config.sort_columns:
                if not isinstance(col, SortColumn):
                    raise ValueError(f"Invalid sort column type: {type(col)}")
            "test".encode(self.config.encoding)
        except Exception as e:
            raise CSVReorderError(f"Configuration validation failed: {e}")

    def parse_date(self, date_string: str) -> Union[datetime, str]:
        if not isinstance(date_string, str) or not date_string.strip():
            return date_string
        date_string = date_string.strip()
        for fmt in self.DATE_FORMATS:
            try:
                return datetime.strptime(date_string, fmt)
            except ValueError:
                continue
        self.logger.warning(f"Could not parse date: '{date_string}'")
        return date_string

    def _validate_csv_columns(self, fieldnames: List[str]) -> None:
        if not fieldnames:
            raise CSVReorderError("CSV file has no columns")

        sort_names = {col.name for col in self.config.sort_columns}
        missing = sort_names - set(fieldnames)
        if missing:
            raise CSVReorderError(f"Sort columns missing: {', '.join(missing)}")

        if (self.config.use_language_sorting and
                self.config.language_column not in fieldnames):
            raise CSVReorderError(f"Language column '{self.config.language_column}' missing")

    def _create_sort_key(self, row: Dict[str, Any]) -> Tuple:
        try:
            key_parts = []
            if self.config.use_language_sorting:
                lang = row.get(self.config.language_column, "").strip()
                try:
                    idx = self.config.language_order.index(lang)
                except ValueError:
                    idx = len(self.config.language_order)
                key_parts.append(idx)

            for col in self.config.sort_columns:
                val = row.get(col.name, "")
                if col.is_date and val:
                    key_parts.append(self.parse_date(str(val)))
                else:
                    key_parts.append(str(val).lower() if val else "")
            return tuple(key_parts)
        except Exception as e:
            raise CSVReorderError(f"Error creating sort key: {e}")

    # ------------------------------------------------------------------
    # FIXED – delimiter sniffing now works in PyInstaller builds
    # ------------------------------------------------------------------
    def _read_csv_file(self, file_path: Path) -> Tuple[List[str], List[Dict[str, Any]]]:
        try:
            # 1. Sniff in binary -> encoding cannot corrupt the sample
            with open(file_path, "rb") as fb:
                sample = fb.read(2048)
                if not sample:
                    raise CSVReorderError("CSV file is empty")
                delimiter = csv.Sniffer().sniff(sample.decode("utf-8", "ignore")).delimiter

            # 2. Read with correct encoding
            with open(file_path, "r", newline="", encoding=self.config.encoding) as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                fieldnames = reader.fieldnames
                if not fieldnames:
                    raise CSVReorderError("CSV file has no header row")
                data = list(reader)

            self.logger.info(f"Successfully read {len(data)} rows from {file_path}")
            return fieldnames, data

        except UnicodeDecodeError as e:
            raise CSVReorderError(f"Encoding error reading CSV file: {e}")
        except csv.Error as e:
            raise CSVReorderError(f"CSV parsing error: {e}")
        except Exception as e:
            raise CSVReorderError(f"Error reading CSV file: {e}")

    # ------------------------------------------------------------------
    # Write file
    # ------------------------------------------------------------------
    def _write_csv_file(self, file_path: Path, fieldnames: List[str],
                        data: List[Dict[str, Any]]) -> None:
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", newline="", encoding=self.config.encoding) as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            self.logger.info(f"Successfully wrote {len(data)} rows to {file_path}")
        except Exception as e:
            raise CSVReorderError(f"Error writing CSV file: {e}")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def reorder_csv(self, input_file: Union[str, Path],
                    output_directory: Union[str, Path]) -> Optional[Path]:
        try:
            input_path = Path(input_file)
            output_dir = Path(output_directory)

            self.logger.info(f"Starting CSV reordering: {input_path}")

            if not input_path.exists() or not input_path.is_file():
                raise CSVReorderError(f"Input file not found: {input_path}")

            fieldnames, data = self._read_csv_file(input_path)
            if not data:
                raise CSVReorderError("The input CSV file contains no data rows")

            self._validate_csv_columns(fieldnames)

            self.logger.info("Sorting CSV data...")
            sorted_data = sorted(data, key=self._create_sort_key,
                                 reverse=self.config.reverse)

            output_path = output_dir / f"{self.config.output_prefix}{input_path.name}"
            self._write_csv_file(output_path, fieldnames, sorted_data)

            self.logger.info(f"CSV reordering completed successfully: {output_path}")
            return output_path

        except CSVReorderError:
            raise
        except Exception as e:
            error_msg = f"Unexpected error during CSV reordering: {e}"
            self.logger.error(error_msg)
            raise CSVReorderError(error_msg)

    def reorder_csv_safe(self, input_file: Union[str, Path],
                         output_directory: Union[str, Path]) -> Optional[Path]:
        try:
            return self.reorder_csv(input_file, output_directory)
        except CSVReorderError as e:
            self.logger.error(f"CSV reordering failed: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return None


# ------------------------------------------------------------------
# Convenience factory
# ------------------------------------------------------------------
def create_reorder_config(sort_columns: List[Tuple[str, bool]], **kwargs) -> CSVReorderConfig:
    cols = [SortColumn(name=n, is_date=d) for n, d in sort_columns]
    return CSVReorderConfig(sort_columns=cols, **kwargs)


# ------------------------------------------------------------------
# Quick CLI smoke-test
# ------------------------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    cfg = create_reorder_config([("year", True), ("title", False)])
    ro = CSVReorder(cfg)
    ro.reorder_csv_safe("sample.csv", "sorted_output")