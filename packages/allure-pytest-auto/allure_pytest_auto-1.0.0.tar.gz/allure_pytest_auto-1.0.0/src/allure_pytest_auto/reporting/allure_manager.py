import logging
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

# Set up logging configuration
log = logging.getLogger(__name__)

def _resolve_allure_cli(allure_cli_path: str) -> tuple[str, bool, bool] | tuple[None, bool, bool]:

    cli_path = Path(allure_cli_path)

    # Full path
    if cli_path.exists():
        shell = sys.platform.startswith("win") and cli_path.suffix.lower() in (".bat", ".cmd")
        return str(cli_path), shell, True

    # From PATH
    resolved = shutil.which(allure_cli_path)
    if resolved:
        return resolved, sys.platform.startswith("win"), True

    # Not found
    return None, False, False


def generate_and_open_report(allure_cli_path: str, results_dir: Path, report_dir: Path, open_report: bool, report_title: str) -> None:

    # Params:
        # allure_cli_path: str,
        # results_dir: Path,
        # report_dir: Path,
        # open_report: bool,
        # report_title: str)
    # Returns -> None

    # Log the results_dir and report_dir paths
    log.info(f"Allure results dir: {results_dir.resolve()}")
    log.info(f"Allure report dir:  {report_dir.resolve()}")

    cli, shell, found = _resolve_allure_cli(allure_cli_path)

    # Delete empty allure report dir if allure_cli not found
    if not found:
        if report_dir.exists() and not any(report_dir.iterdir()):
            report_dir.rmdir()

            log.info(f"Deleted empty Allure report dir: {report_dir}")
        else:
            log.info(f"Allure report dir '{report_dir}' is not empty or does not exist")

        raise pytest.UsageError(
            f"Allure CLI not found at {allure_cli_path}.\nPlease provide the full path to the Allure CLI or ensure that Allure CLI is included in your system's PATH environment variable."
        )

    # allure generate < results_dir > -o < report_dir > --clean --single-file --report-name "<report_title>"
    subprocess.run([cli, "generate", str(results_dir), "-o",
                    str(report_dir), "--clean", "--single-file",
                    "--report-name", report_title],
                   check=True, shell=shell)

    if open_report:
        # allure open <report_dir>
        subprocess.Popen([cli, "open", str(report_dir)], shell=shell)