# allure_pytest_auto/settings/config_loader.py

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict
import tomllib
import pytest
import logging

from allure_pytest_auto.runner.env import is_ci

log = logging.getLogger(__name__)


@dataclass
class AllurePytestAutoConfig:
    allure_cli_path: str = "allure"
    allure_results_dir: Path = Path("allure-results")
    allure_report_dir: Path = Path("allure-report")
    open_report_by_default: bool = False
    report_title: str = "allure report"
    environment: Dict[str, str] = field(default_factory=dict)

    # Validate AllureConfig fields, raise pytest.UsageError if invalid.

    def validate(self) -> None:
        # CLI path must not be empty
        if not self.allure_cli_path or not self.allure_cli_path.strip():
            raise pytest.UsageError("Invalid configuration in allure_pytest_auto.toml: 'allure_cli_path' must not be empty")

        # Report dir must not be empty
        if (
                self.allure_report_dir is None
                or str(self.allure_report_dir).strip() == ""
                or self.allure_report_dir == Path(".")
        ):
            raise pytest.UsageError("Invalid configuration in allure_pytest_auto.toml: 'allure_report_dir' must not be empty")

        # Ensure report title has a default
        if not self.report_title or not self.report_title.strip():
            self.report_title = "allure report"

        # Env is not ci
        if not is_ci():
        # open_report_by_default is boolean
            if not isinstance(self.open_report_by_default,bool):
                 raise pytest.UsageError("Invalid configuration in allure_pytest_auto.toml: 'open_report_by_default' must be boolean - true or false")


# Load Allure configuration from TOML or use defaults. Raise pytest.UsageError on invalid config.

def load_allure_pytest_auto_config(config_path: str = None) -> AllurePytestAutoConfig:
    # ---- No config file: use defaults -------------------
    if not config_path:
        log.debug("No allure config provided, using defaults")
        cfg = AllurePytestAutoConfig()
        cfg.validate()
        return cfg

    # ---- Config file exists? --------------------------------
    path = Path(config_path)
    if not path.exists():
        raise pytest.UsageError(f"Allure config file not found: {path}")

    # ---- Load TOML ----------------------------------------
    try:
        with path.open("rb") as f:
            toml_data = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        raise pytest.UsageError(f"Invalid TOML in '{path}':\n{str(e)}")

    # ---- Build AllureConfig object ------------------------
    cfg = AllurePytestAutoConfig()

    # Map TOML keys to dataclass fields if present
    if "allure_cli_path" in toml_data:
        cfg.allure_cli_path = toml_data["allure_cli_path"]
    if "allure_results_dir" in toml_data:
        cfg.allure_results_dir = Path(toml_data["allure_results_dir"])
    if "allure_report_dir" in toml_data:
        cfg.allure_report_dir = Path(toml_data["allure_report_dir"])
    if "open_report_by_default" in toml_data:
        cfg.open_report_by_default = toml_data["open_report_by_default"]
    if "report_title" in toml_data:
        cfg.report_title = toml_data["report_title"]
    if "environment" in toml_data:
        cfg.environment = dict(toml_data["environment"])

    # ---- Validate config -----------------------------------
    cfg.validate()

    return cfg