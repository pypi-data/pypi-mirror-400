# runner/env.py
import os

CI_ENV_VARS = (
    "CI",
    "GITHUB_ACTIONS",
    "GITLAB_CI",
    "JENKINS_URL",
    "BUILDKITE",
    "TF_BUILD",
    "CIRCLECI",
)

def is_ci() -> bool:
    return any(env_var in os.environ for env_var in CI_ENV_VARS)