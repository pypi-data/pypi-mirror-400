```
# Disruptive Innovation Index Calculator

A simple, high-performance Python tool to calculate citation-based disruptive innovation index (**DI1**, **DI5**, **mCD**).

## 📦 Installation

```bash
pip install from disrupt_idx
```

## 🚀 Quick Start

### 1. Prepare Data

Place these 3 files in your working directory:

| **File**        | **Columns Required**                     | **Description**                  |
| --------------- | ---------------------------------------- | -------------------------------- |
| **`net.csv`**   | `id`, `cited`  *(or `netfrom`, `netto`)* | Citation network relationships.  |
| **`time.csv`**  | `id`, `publicationDate`                  | Publication dates (YYYY/MM/DD).  |
| **`focal.csv`** | `id`                                     | List of target IDs to calculate. |

### 2. Run Code

Create a python script (e.g., `run.py`) and run it:

Python

```
from disruptive_metrics import DisruptiveInnovator

# Initialize (Automatically loads net.csv, time.csv, focal.csv)
calculator = DisruptiveInnovator()

print("Calculating...")

# Standard Metrics
calculator.calculate("DI1")
calculator.calculate("DI5")
calculator.calculate("mCD")

# Metrics with Time Window (e.g., 5 years)
calculator.calculate("DI1", window_years=5)

# Metrics excluding Nk term (nk mode)
calculator.calculate("DI1", exclude_nk=True)
```

## 📂 Output

Results are automatically saved in the **`results/`** folder:

- `results/DI1.csv`
- `results/DI1Y5.csv`
- ...and so on.

## 📄 License

MIT License
