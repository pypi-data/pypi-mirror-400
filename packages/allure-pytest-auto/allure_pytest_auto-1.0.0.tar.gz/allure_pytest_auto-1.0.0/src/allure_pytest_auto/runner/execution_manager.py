# allure_pytest_auto/runner/execution_manager.py

import logging


log = logging.getLogger(__name__)

def run_post_processing(exit_status: int) -> None:

    log.info("Test session finished with exit status: %s", exit_status)

    if exit_status == 0:
        log.info("Test run SUCCESS")
    else:
        log.warning("Test run FAILED (exit code: %s)", exit_status)