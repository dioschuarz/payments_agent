"""Data loader for mock services with JSON schema validation."""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import jsonschema


class DataLoader:
    """Loads and validates JSON data files against JSON schemas."""

    def __init__(self, data_dir: Optional[str] = None, schema_dir: Optional[str] = None):
        """
        Initialize data loader.

        Args:
            data_dir: Directory containing JSON data files (defaults to src/infrastructure/mocks/data)
            schema_dir: Directory containing JSON schema files (defaults to src/infrastructure/mocks/schemas)
        """
        if data_dir is None:
            # Default to project's mock data directory
            base_path = Path(__file__).parent
            data_dir = str(base_path / "data")
        if schema_dir is None:
            base_path = Path(__file__).parent
            schema_dir = str(base_path / "schemas")

        self._data_dir = Path(data_dir)
        self._schema_dir = Path(schema_dir)

        if not self._data_dir.exists():
            raise ValueError(f"Data directory does not exist: {data_dir}")
        if not self._schema_dir.exists():
            raise ValueError(f"Schema directory does not exist: {schema_dir}")

    def load_data(self, filename: str, validate: bool = True) -> Any:
        """
        Load JSON data file and optionally validate against schema.

        Args:
            filename: Name of JSON file (e.g., "beneficiaries.json")
            validate: Whether to validate against schema (default: True)

        Returns:
            Parsed JSON data

        Raises:
            FileNotFoundError: If data file doesn't exist
            jsonschema.ValidationError: If validation fails
        """
        data_path = self._data_dir / filename
        if not data_path.exists():
            raise FileNotFoundError(f"Data file not found: {data_path}")

        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if validate:
            schema_filename = filename.replace(".json", "_schema.json")
            schema_path = self._schema_dir / schema_filename
            if schema_path.exists():
                with open(schema_path, "r", encoding="utf-8") as f:
                    schema = json.load(f)
                jsonschema.validate(instance=data, schema=schema)
            else:
                # Schema not found, skip validation
                pass

        return data

    def load_beneficiaries(self) -> List[Dict[str, Any]]:
        """Load beneficiaries data."""
        return self.load_data("beneficiaries.json")

    def load_countries(self) -> List[Dict[str, Any]]:
        """Load countries data."""
        return self.load_data("countries.json")

    def load_currencies(self) -> Dict[str, Any]:
        """Load currencies configuration."""
        return self.load_data("currencies.json")

    def load_delivery_methods(self) -> List[Dict[str, Any]]:
        """Load delivery methods data."""
        return self.load_data("delivery_methods.json")

