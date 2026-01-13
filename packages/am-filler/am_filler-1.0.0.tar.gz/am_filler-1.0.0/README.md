# AM_filler

> **Automatic Missing Value Filler** - Fill missing values in datasets intelligently with one line of code.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Overview

AM_filler is a Python library that **automatically detects column types** and fills missing values using the **best strategy** — without any user configuration. It saves time and prepares datasets for ML/DL tasks in one line of code.

![Distribution Logic](docs/images/distribution_logic.png)

### Why AM_filler?

| Feature | sklearn/PyCaret | AM_filler |
|---------|-----------------|-----------|
| Choose imputation strategy | Manual | **Automatic** |
| Handle text columns | Limited | **Built-in** |
| Configuration required | Yes | **None** |
| One-line usage | No | **Yes** |

---

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/AM_filler.git
cd AM_filler

# Install in development mode
pip install -e .
```

---

## ⚡ Quick Start

```python
from am_filler import AMFiller
import pandas as pd

# Your DataFrame with missing values
df = pd.read_csv("your_data.csv")

# One line to fill all missing values!
df_clean = AMFiller().fit_transform(df)
```

That's it! AM_filler automatically:
- Detects column types (numeric, categorical, text)
- Chooses the best imputation strategy
- Fills all missing values
- Logs what was done

---

## 🧠 How It Works - The Logic

AM_Filler uses intelligent algorithms to determine how to fill missing data:

### 1. Numeric Data (Intelligence)
It checks the **distribution** of data before deciding:
*   **Normal Distribution**: Uses **MEAN**.
*   **Skewed / Outliers**: Uses **MEDIAN**.

*(See the graph above for visual representation)*

### 2. Context-Aware Text Filling
Unlike other libraries that drop text or fill with "Missing", AM_Filler uses context-aware templates:
*   **Description**: "Information not available."
*   **Feedback**: "No review provided."
*   etc.

### 3. Categorical Data
*   Uses **MODE** (Most frequent value).

---

## 📁 Project Structure

```
AM_filler/
├── am_filler/
│   ├── __init__.py      # Public API exports
│   ├── core.py          # Main AMFiller class
│   ├── numeric.py       # Numeric imputation (smart mean/median)
│   ├── categorical.py   # Categorical imputation (mode)
│   ├── text.py          # Text imputation (sentences)
│   └── utils.py         # Helper functions
├── examples/
│   └── test_notebook.ipynb # Interactive Demo!
├── docs/
│   └── images/          # Documentation assets
├── README.md
├── pyproject.toml
└── setup.py
```

---

## 🧪 Running Tests

```bash
# Install test dependencies
pip install pytest

# Run all tests
pytest tests/ -v
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.