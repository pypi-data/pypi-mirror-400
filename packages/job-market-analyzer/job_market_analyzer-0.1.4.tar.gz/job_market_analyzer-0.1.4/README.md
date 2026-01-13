# Job Market Analyzer 📊

A Python package to analyze job market data for Data Analyst roles.

## Features
- Analyze job postings from CSV
- Identify top required skills
- Calculate salary statistics
- Visualize trends using charts

## Installation
```bash
pip install job-market-analyzer

from job_market_analyzer import load_data, filter_jobs, top_skills

df = load_data("jobs.csv")
filtered = filter_jobs(df, "Data Analyst")
print(top_skills(filtered))


This makes PyPI render it **cleanly**.

---

### 🔧 IMPROVEMENT 2: Do NOT ship `jobs.csv` in real PyPI package (OPTIONAL)

For learning → fine  
For real PyPI → better practice:

- Remove `data/jobs.csv` from package
- Let users provide their own CSV

Later we can:
- move sample data to `examples/`
- or download data via API

But this is **optional** for now.

---

### 🔧 IMPROVEMENT 3: Add version info in code (Optional but nice)

In `__init__.py`:

```python
__version__ = "0.1.0"
