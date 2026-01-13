# Matrix Regression

Multi-label text classification algorithm for online learning.

[![CodeFactor](https://www.codefactor.io/repository/github/nicoloverardo/matrix_regression/badge/main)](https://www.codefactor.io/repository/github/nicoloverardo/matrix_regression/overview/main)
[![codecov](https://codecov.io/gh/nicoloverardo/matrix_regression/branch/main/graph/badge.svg)](https://codecov.io/gh/nicoloverardo/matrix_regression)
![PyPI](https://img.shields.io/pypi/v/matrixreg?label=version)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/matrixreg)
![PyPI - Downloads](https://img.shields.io/pypi/dm/matrixreg)
![GitHub](https://img.shields.io/github/license/nicoloverardo/matrix_regression?color=green)
[![CI Pipeline](https://github.com/nicoloverardo/matrix_regression/actions/workflows/ci.yaml/badge.svg)](https://github.com/nicoloverardo/matrix_regression/actions/workflows/ci.yaml)
[![Build](https://github.com/nicoloverardo/matrix_regression/actions/workflows/publish.yml/badge.svg)](https://github.com/nicoloverardo/matrix_regression/actions/workflows/publish.yml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Description

Implementation of the MatrixRegression (MR) algorithm for multi-label text classification that can be used in an online learning context. It is presented in the following paper:

[Popa, I. & Zeitouni, Karine & Gardarin, Georges & Nakache, Didier & Métais, Elisabeth. (2007). Text Categorization for Multi-label Documents and Many Categories. 421 - 426. 10.1109/CBMS.2007.108.](https://www.researchgate.net/publication/4257876_Text_Categorization_for_Multi-label_Documents_and_Many_Categories)

Abstract:
> In this paper, we propose a new classification method that addresses classification in multiple categories of textual documents. We call it Matrix Regression (MR) due to its resemblance to regression in a high dimensional space. Experiences on a medical corpus of hospital records to be classified by ICD (International Classification of Diseases) code demonstrate the validity of the MR approach. We compared MR with three frequently used algorithms in text categorization that are k-Nearest Neighbors, Centroide and Support Vector Machine. The experimental results show that our method outperforms them in both precision and time of classification.


## Installation
Via PyPi using pip, as easy as:

```bash
pip install matrixreg
```

## Usage

```python
from matrixreg import MatrixRegression

mr = MatrixRegression()

# Fit
mr.fit(X_train, y_train)

# Predict
mr.predict(X_test)

# Partial fit
mr.partial_fit(new_X, new_y)
```

### Parameters optimization

This implementation is [scikit](https://scikit-learn.org/stable/index.html)-friendly; thus, it supports [GridSearchCV](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html).

```python
# Parameter to optimize
param_grid = [{"threshold": [0.3, 0.6, 0.9]}]

# Initialization
mr = MatrixRegression()
clf = GridSearchCV(mr, param_grid, cv=5, verbose=10, n_jobs=-1, scoring='f1_micro')

# Fit
clf.fit(X_train, y_train)

# Results
clf.best_params_, clf.best_score_
```

### Author

Nicolò Verardo

<a href="https://www.buymeacoffee.com/nicoloverardo" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height="30" width="120"></a>