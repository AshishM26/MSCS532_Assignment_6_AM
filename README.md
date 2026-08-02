# MSCS 532 Assignment 6

**Student:** Ashish Mahajan  
**Course:** MSCS 532-B01 - Algorithms and Data Structures  
**Instructor:** Dr. Michael Solomon  
**Assignment:** Assignment 6 - Medians and Order Statistics & Elementary Data Structures  
**Repository:** [MSCS532_Assignment_6_AM](https://github.com/AshishM26/MSCS532_Assignment_6_AM)

## Overview

This project implements deterministic and randomized algorithms for selecting the kth smallest value without fully sorting the input. It also implements a dynamic array, matrix, array-based stack, circular array queue, and singly linked list from scratch. Tests, reproducible benchmarks, charts, and a cloud-operations demonstration connect the theoretical analysis to measured behavior.

Detailed findings and analysis are provided in [report.md](report.md).

## Repository Structure

```text
MSCS532_Assignment_6_AM/
├── benchmarks/   # Reproducible empirical experiments
├── examples/     # Deterministic cloud-operations demonstration
├── results/      # Generated CSV results and charts
├── src/          # Algorithms and data structures
├── tests/        # unittest test suite
├── README.md
├── report.md
└── requirements.txt
```

## Setup and Execution

Python 3.11 or newer is recommended.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m unittest discover -s tests -v
python3 benchmarks/benchmark_selection.py
python3 benchmarks/benchmark_data_structures.py
python3 examples/cloud_operations_demo.py
```

The remaining algorithm descriptions, complexity summary, benchmark findings, limitations, and references are completed after validation so that all reported results match the generated CSV files.
