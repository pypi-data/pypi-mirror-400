# allure-pytest-auto

Pytest plugin generating timestamped Allure reports with configurable settings, CI/CD-ready. No more report overwrites.

[GitHub Repository](https://github.com/sjvaidya/allure-pytest-auto)

---

## ✨ Features

- ✅ Creates timestamped Allure HTML reports
- ✅ Optional auto-open report after test execution
- ✅ Single config file for Allure + environment.properties
- ✅ Works with local runs & CI/CD pipelines
- ✅ Zero boilerplate — no scripts needed


---
## 📸 Screenshots

**Local Run**

![Local Run](https://raw.githubusercontent.com/sjvaidya/allure-pytest-auto/refs/heads/main/screenshots/local_run.png)

**CI/CD Run**

![CI/CD Run](https://raw.githubusercontent.com/sjvaidya/allure-pytest-auto/refs/heads/main/screenshots/ci_run.png)

---

## 📥 Installation
```
pip install allure-pytest-auto
```
---
## ⚙️ Requirements

### System Requirements
- **Python**: >= 3.8  
- **Allure CLI**: >= 2.24.0  

### Python Dependencies (pip)
- **pytest**: >= 7.0  
- **allure-pytest**: >= 2.13  
---
## 🚀 Quick Start

1. Create a configuration file **allure_pytest_auto.toml** (recommended at project root)  

2. Run the below command:

```
pytest --alluredir=allure-results --allure-pytest-auto-config=allure_pytest_auto.toml
```

---

## ⚙️ Configuration

Recommended at project root.

***allure_pytest_auto.toml***

```toml
#Full path of Allure CLI. If allure binary is in path env variable use "allure". Use "allure" for CICD
#If not defined, defaults to "allure"
allure_cli_path = "allure"

#base directory to save timestamped allure report. If not defined, defaults to "allure-report"
allure_report_dir = "allure-report"

#Report name for allure report. If not defined or kept as empty string "", defaults to "Allure report"
report_title = "allure-pytest-auto demo"

#open report after run - true or false
open_report_by_default = "false"

#environment.properties
[environment]
ENV = "dev"
BUILD = "223"
DESCRIPTION = "Unit tests"
```
| Config                 | Description                                                                                                                                                                    | Default       |
|------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------|
| allure_cli_path        | Full path to allure cli (e.g. /opt/allure/bin/allure OR C:/Allure/bin/allure.bat)<br/> If allure cli is in path environment variable use "allure".<br/> For CI/CD use "allure" | allure        |
| allure_report_dir      | Path to base report directory in which timestamped allure report folders will be created                                                                                       | allure-report |
| report_title           | Title in generated allure report                                                                                                                                               | Allure Report |
| open_report_by_default | Opens allure report post run if True (ignored for cicd runs)                                                                                                                   | True          |
| [environment]          | Content of environment.properties                                                                                                                                              | N/A           |

---
## 🧪 Behavior
### 🧑‍💻 Local Runs
- ✅ Single config file for Allure + environment.properties
- ✅ Timestamped report directories
- ✅ Optional auto-open in browser

### 🤖 CI/CD Runs
- ✅ Single config file for Allure + environment.properties
- ✅ Fixed report directory. No timestamped report directories
- ✅ No Auto-open.

---

## 🧩 CLI Options

--alluredir → Allure results directory (required)

--allure-pytest-auto-config → Path to allure_pytest_auto config file (required)

---

## ❓ FAQ

See the [FAQ](FAQ.md) for common questions.

---

## 📜 License

MIT

---
## ✉️ Contact

For questions, issues, or contributions:  
- GitHub: [@sjvaidya](https://github.com/sjvaidya)
- Open an issue: [here](https://github.com/sjvaidya/allure-pytest-auto/issues)
