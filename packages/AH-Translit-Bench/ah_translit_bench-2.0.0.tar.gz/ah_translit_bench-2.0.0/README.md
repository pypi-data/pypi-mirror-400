# **AH-Translit_Benchmark**

**Arabic → Hindi Transliteration Benchmark Dataset**

[![PyPI version](https://badge.fury.io/py/AH-Translit_Bench.svg)](https://pypi.org/project/AH-Translit-Bench/)
[![GitHub license](https://img.shields.io/github/license/vilalali/AH-Translit-Bench.svg)](https://github.com/vilalali/AH-Translit-Bench/blob/main/LICENSE)

---

## Description

**AH-Translit_Bench** is a **6,000-sample Arabic-to-Hindi transliteration benchmark dataset**, curated for **systematic evaluation and comparison** of transliteration models across **three linguistically distinct domains**:

* **Quranic Arabic**
* **Modern Standard Arabic (Daily Use)**
* **Modern Standard Arabic (Bibliographic)**

Each domain contributes **2,000 carefully selected sentence pairs**, ensuring **balanced, fair, and domain-aware evaluation** of cross-script transliteration systems.

This benchmark is designed **strictly for testing and reporting results**, and is complementary to the full AH-Translit training dataset.

---

## Dataset Curators

**Vilal Ali**
MS by Research, Data Sciences and Analytics Centre
IIIT Hyderabad
📧 [vilal.ali@research.iiit.ac.in](mailto:vilal.ali@research.iiit.ac.in)

**Mohd Hozaifa Khan**
MS by Research, CVIT
IIIT Hyderabad
📧 [mohd.hozaifa@research.iiit.ac.in](mailto:mohd.hozaifa@research.iiit.ac.in)

---

## Dataset Usage

Designed for **benchmarking and evaluating Arabic-to-Hindi phonetic transliteration models** under domain shifts and varying sequence-length conditions.

---

## Content Type

Text — sentence-level **Arabic source text** paired with **Hindi (Devanagari) phonetic transliteration**.

---

## File Type

CSV (Comma-Separated Values)

---

## Dataset Structure

```
AH-Translit-Benchmark-Dataset
├── quranic_benchmark_2000.csv
├── msa_dailyuse_benchmark_2000.csv
├── msa_bibliographic_benchmark_2000.csv
├── all_domain_mix_benchmark_6000.csv
└── README.md
```

---

## File Descriptions

* **quranic_benchmark_2000.csv**
  2,000 sentence pairs from **Quranic Arabic**, characterized by long sequences and rich morphology.

* **msa_dailyuse_benchmark_2000.csv**
  2,000 sentence pairs from **daily-use Modern Standard Arabic**, representing short and conversational inputs.

* **msa_bibliographic_benchmark_2000.csv**
  2,000 sentence pairs from **formal and bibliographic MSA**, featuring higher lexical diversity.

* **all_domain_mix_benchmark_6000.csv**
  Combined benchmark file containing all **6,000 samples**, evenly distributed across domains.

Each CSV contains exactly **two columns**:

```
Arabic , Hindi
```

Hindi text is **phonetic transliteration**, not translation.

---

## Benchmark Scale Summary

| Domain            |   Samples |
| ----------------- | --------: |
| Quranic           |     2,000 |
| MSA Daily Use     |     2,000 |
| MSA Bibliographic |     2,000 |
| **Total**         | **6,000** |

This strict balance ensures **macro-averaged, unbiased evaluation** across domains.

---

## How to Use This Dataset

### Load a Benchmark CSV

```python
import pandas as pd

df = pd.read_csv("quranic_benchmark_2000.csv")
print(df.head())
print(df.shape)  # (2000, 2)
```

### Load the Full Benchmark Mix

```python
df_all = pd.read_csv("all_domain_mix_benchmark_6000.csv")
print(df_all.shape)  # (6000, 2)
```

---

## 🧾 Example Data Snippet

```csv
Arabic,Hindi
المطبعة الحيدرية،,"अल-मतबअह अल-हैदरियह,"
```

---

## Version Overview

### **Version 2.0 (Current)**

**Version Description:**
Expanded benchmark release with **2,000 samples per domain**, covering Quranic Arabic, MSA Daily Use, and MSA Bibliographic text, along with a **combined 6,000-sample mixed-domain benchmark file** for standardized evaluation.

---

## Important Notes

* This is a **benchmark-only dataset**
* Not intended for model training
* No overlap with AH-Translit training splits
* Focuses on **phonetic fidelity**, not semantic translation

---

## License

* **Code:** MIT License
* **Dataset:** Creative Commons Attribution–NonCommercial 4.0 (CC BY-NC 4.0)

Permitted for **research and educational use only** with proper attribution.

Full license:
[https://creativecommons.org/licenses/by-nc/4.0/](https://creativecommons.org/licenses/by-nc/4.0/)

---

## Acknowledgements

The AH-Translit team at IIIT Hyderabad thanks **India Data** for hosting and supporting this benchmark dataset.

---

## Authors
**Vilal Ali** [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-0077B5.svg?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/vilal-ali/)
---
**Mohd Hozaifa Khan** [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-0077B5.svg?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/mohd-hozaifa-khan-361b7814a/)
---
