from pathlib import Path
from typing import Mapping

def write_environment_properties(
    results_dir: Path,
    env_properties: Mapping[str, str],
) -> None:

    # Write environment.properties into the Allure results directory.
    if not env_properties:
        return

    env_file = results_dir / "environment.properties"

    lines = [f"{key}={value}\n" for key, value in env_properties.items()]

    env_file.write_text("".join(lines), encoding="utf-8")