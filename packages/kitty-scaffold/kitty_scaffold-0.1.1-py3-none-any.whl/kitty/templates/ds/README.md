# Data Science Project

A standardized data science project structure following industry best practices.

## Project Structure

```
├── data/
│   ├── raw/          # Original, immutable data
│   ├── interim/      # Intermediate transformed data
│   └── processed/    # Final datasets for modeling
├── notebooks/
│   ├── 01_eda.ipynb         # Exploratory Data Analysis
│   ├── 02_features.ipynb    # Feature Engineering
│   └── 03_modeling.ipynb    # Model Training
├── src/
│   ├── data_loader.py       # Data loading utilities
│   ├── preprocessing.py     # Data preprocessing
│   ├── features.py          # Feature engineering
│   ├── train.py             # Model training
│   └── evaluate.py          # Model evaluation
├── reports/
│   └── figures/             # Generated graphics
├── requirements.txt
└── README.md
```

## Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Add your raw data to `data/raw/`

3. Start with exploratory analysis in `notebooks/01_eda.ipynb`

4. Build reusable code in `src/`

## Best Practices

- Never modify raw data
- Use notebooks for exploration, src/ for production code
- Document your findings in reports/
- Version control your code, not your data
