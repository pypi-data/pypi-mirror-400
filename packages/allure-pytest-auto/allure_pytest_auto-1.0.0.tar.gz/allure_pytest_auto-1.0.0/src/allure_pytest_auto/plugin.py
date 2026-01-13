from datetime import datetime
import shutil
from pathlib import Path

import pytest

from allure_pytest_auto.reporting.allure_manager import generate_and_open_report
from allure_pytest_auto.reporting.properties_writer import write_environment_properties
from allure_pytest_auto.runner.env import is_ci
from allure_pytest_auto.runner.execution_manager import run_post_processing
from allure_pytest_auto.settings.config_loader import load_allure_pytest_auto_config

def pytest_addoption(parser):
    group = parser.getgroup("allure-pytest-auto")

    group.addoption(
        "--allure-pytest-auto-config",
        action="store",
        dest="allure_pytest_auto_config",
        default=None,
        help="Path to allure_pytest_auto.toml",
    )

def _clean_results_dir(results_dir: Path) -> None:
    if results_dir.exists():
        for item in results_dir.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()


def pytest_configure(config):

    allure_pytest_auto_config = config.getoption("--allure-pytest-auto-config")
    # Check if explicitly passed but empty/blank
    if allure_pytest_auto_config is not None and allure_pytest_auto_config.strip() == "":
        raise pytest.UsageError(
            "--allure-config cannot be empty or blank. Please provide a valid file path."
        )

    # LOAD CONFIG ──────────────────────────────
    runner_config = load_allure_pytest_auto_config(
        config_path=config.getoption("allure_pytest_auto_config")
    )

    # READ RESULTS DIR FROM CLI (MANDATORY) ────
    results_dir_opt = getattr(config.option, "allure_report_dir", None)
    if not results_dir_opt:
        raise pytest.UsageError(
            "\nMissing required --alluredir option.\n\n"
            "Usage:\n"
            "pytest --alluredir=allure-results --allure-pytest-auto-config=allure_pytest_auto.toml\n"
        )

    results_dir = Path(results_dir_opt)
    results_dir.mkdir(parents=True, exist_ok=True)
    _clean_results_dir(results_dir)

    # REPORT DIR (CONFIG + CI LOGIC) ───────────
    base_report_dir = runner_config.allure_report_dir

    if is_ci():
        report_dir = base_report_dir
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = base_report_dir / timestamp

    report_dir.mkdir(parents=True, exist_ok=True)

    # OPEN REPORT CONFIG
    open_report = (
        runner_config.open_report_by_default
    )

    if is_ci():
        open_report = False

    # STORE STATE
    config._allure_pytest_auto = {
        "results_dir": results_dir,
        "report_dir": report_dir,
        "open_report": open_report,
        "cfg": runner_config,
    }

    # ENVIRONMENT.PROPERTIES
    write_environment_properties(
        results_dir=results_dir,
        env_properties=runner_config.environment,
    )

def pytest_sessionfinish(session, exitstatus):
    state = getattr(session.config, "_allure_pytest_auto", None)
    if not state:
        return
    cfg = state["cfg"]

    generate_and_open_report(
        allure_cli_path=cfg.allure_cli_path,
        results_dir=state["results_dir"],
        report_dir=state["report_dir"],
        report_title=cfg.report_title,
        open_report=state["open_report"],
    )

    run_post_processing(
        exit_status=exitstatus,
    )